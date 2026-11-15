"""Checked radial Green reduction of power-cell face flux to analytic edges.

Exact rational cuts select the branches. Square roots and arctangents use
outward intervals. No spatial sampling or uncertain region allocation enters
this route; complete region labels come from certified free-vertex roots.
"""

from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
from typing import Any, Optional

from ..model import Model, _record, decode_point, point
from ..volume_request import VolumeRequest
from ._interval import _exact, _Interval, _outward, _sqrt
from .boundary_volume import aggregate, coefficient
from .edge_math import BITS, atan_dyadic
from .geometry import _squared, cell_is_free, volume
from .polytope import _cross, _dot, _result
from .power_cells import _planes

SCHEME = 'power-face-edge-antiderivative/1'


@lru_cache(maxsize=512)
def _atan_endpoint(value: Fraction, bits: int) -> _Interval:
    return atan_dyadic(value, bits)


def _angle(value: _Interval, bits: int) -> _Interval:
    return _Interval(
        _atan_endpoint(value.lower, bits).lower, _atan_endpoint(value.upper, bits).upper
    )


def _positive_sqrt(value: Fraction, bits: int) -> _Interval:
    result = _sqrt(value, bits)
    if result.lower <= 0:
        raise ArithmeticError(
            'Edge primitive needs more dyadic bits for its denominator'
        )
    return result


def _edge(
    center: tuple,
    radius: Fraction,
    normal: tuple,
    alpha: Fraction,
    left: tuple,
    right: tuple,
    bits: int,
) -> _Interval:
    y = point([a - b for a, b in zip(left, center)])
    e = point([b - a for a, b in zip(left, right)])
    n2 = _dot(normal, normal)
    factor = alpha * _dot(y, _cross(e, normal)) / (3 * n2)
    if factor == 0:
        return _exact(0)
    a = _dot(e, e)
    b = _dot(y, e)
    h2 = alpha * alpha / n2
    d = _dot(y, y) - h2 - b * b / a
    if d <= 0:
        raise ValueError(
            'A nonzero oriented edge requires positive radial line distance'
        )
    h = _positive_sqrt(h2, bits)
    ad = _positive_sqrt(a * d, bits)
    v0, v1 = b, b + a
    cut2 = a * (radius * radius - h2 - d)
    intervals = []
    if cut2 <= 0:
        intervals.append((_exact(v0), _exact(v1)))
    else:
        cut = _sqrt(cut2, bits)
        # Rational sign/square comparisons choose exact algebraic cut endpoints.
        # Interval endpoints never decide whether a geometric piece exists.
        if v0 < 0 and v0 * v0 > cut2:
            end = _exact(v1) if v1 < 0 and v1 * v1 >= cut2 else _exact(0) - cut
            intervals.append((_exact(v0), end))
        if v1 > 0 and v1 * v1 > cut2:
            start = _exact(v0) if v0 > 0 and v0 * v0 >= cut2 else cut
            intervals.append((start, _exact(v1)))
    total = _exact(0)
    constant = (
        _exact((h2 - 3 * radius * radius) / 2)
        if h2 <= radius * radius
        else _exact(-(radius**3)) / h
    )

    def primitives(v: _Interval) -> tuple[_Interval, _Interval]:
        radial2 = _exact(h2 + d) + v.square() / _exact(a)
        radial = _Interval(
            _sqrt(radial2.lower, bits).lower, _sqrt(radial2.upper, bits).upper
        )
        j1 = _angle(v / ad, bits) / ad
        j2 = _angle(h * v / (ad * radial), bits) / (h * ad)
        return j1, j2

    for low, high in intervals:
        l1, l2 = primitives(low)
        u1, u2 = primitives(high)
        value = (
            (high - low) / _exact(2 * a)
            + constant * (u1 - l1)
            + _exact(radius**3) * (u2 - l2)
        )
        total = _outward(total + _exact(factor) * value, bits)
    return total


def triangle_flux(
    center: tuple, radius: Fraction, triangle: tuple, bits: int
) -> _Interval:
    """Enclose the signed analytic face integral, including exact sphere cuts.

    Parameters
    ----------
    center : tuple
        Exact owner-ball center in nm.
    radius : Fraction
        Nonnegative expanded radius in nm.
    triangle : tuple
        Three outward-oriented rational points in nm.
    bits : int
        Admitted outward precision, 64 through 2048 in powers of two.

    Returns
    -------
    _Interval
        Signed rational flux enclosure in nm**3.

    Raises
    ------
    ValueError, ArithmeticError
        Invalid geometry/precision or insufficient positive denominator bounds.
    """
    if type(bits) is not int or bits not in BITS or radius < 0:
        raise ValueError('Invalid analytic edge radius or dyadic precision')
    if radius == 0:
        return _exact(coefficient(center, triangle))
    if all(_squared(p, center) <= radius * radius for p in triangle):
        return _exact(0)
    a, b, c = triangle
    normal = _cross(
        point([b[i] - a[i] for i in range(3)]), point([c[i] - a[i] for i in range(3)])
    )
    alpha = _dot(point([a[i] - center[i] for i in range(3)]), normal)
    if alpha == 0:
        return _exact(0)
    total = _exact(0)
    for left, right in [(a, b), (b, c), (c, a)]:
        total = total + _edge(center, radius, normal, alpha, left, right, bits)
    return _outward(total, bits)


def _closest(center: tuple, a: tuple, b: tuple) -> tuple:
    edge = point([v - u for u, v in zip(a, b)])
    length2 = _dot(edge, edge)
    t = max(
        Fraction(),
        min(
            Fraction(1), _dot(point([v - u for u, v in zip(a, center)]), edge) / length2
        ),
    )
    return point([u + t * v for u, v in zip(a, edge)])


def _face_minimum(center: tuple, vertices: tuple) -> tuple:
    a, b, c = vertices[:3]
    n = _cross(
        point([b[i] - a[i] for i in range(3)]), point([c[i] - a[i] for i in range(3)])
    )
    alpha = _dot(point([a[i] - center[i] for i in range(3)]), n)
    projection = point([center[i] + alpha * n[i] / _dot(n, n) for i in range(3)])
    edges = list(zip(vertices, vertices[1:] + vertices[:1]))
    if all(
        _dot(
            _cross(
                point([b[i] - a[i] for i in range(3)]),
                point([projection[i] - a[i] for i in range(3)]),
            ),
            n,
        )
        >= 0
        for a, b in edges
    ):
        return projection
    return min(
        (_closest(center, a, b) for a, b in edges), key=lambda p: _squared(p, center)
    )


def assigned_faces(
    model: Model, proof: dict[str, Any], checked: dict[str, Any]
) -> list[tuple]:
    """Reconstruct complete oriented face pieces with proved global region labels."""
    labels = {
        decode_point(checked['nodes'][i]): r['region_id']
        for r in checked['regions']
        for i in r['node_ids']
    }
    atoms = {a.source_id: a for a in model.atoms}
    seen: dict[tuple, tuple] = {}
    pieces: list[tuple] = []
    for cell in proof['cells']:
        if 'coincident_dominator' in cell:
            continue
        vertices = tuple(decode_point(p) for p in cell['vertices'])
        atom = atoms.get(cell['atom_id'])
        center = point((0, 0, 0)) if atom is None else atom.center
        radius = Fraction() if atom is None else atom.radius + model.probe
        planes = _planes(model, atom)
        poly = _result(vertices, tuple(planes[i] for i in cell['support']))
        if poly['geometric_dimension'] != 3:
            continue
        if vertices in seen:
            if seen[vertices] != (center, radius):
                raise ValueError('Coincident source cells have different owner balls')
            continue
        seen[vertices] = (center, radius)
        for facet in poly['facets']:
            face = tuple(vertices[i] for i in facet['vertex_indices'])
            free = [p for p in face if _squared(p, center) > radius * radius]
            if not free:
                continue
            ids = {labels[p] for p in free}
            if len(ids) == 1:
                triangles = [
                    (tuple([face[0], face[j], face[j + 1]]), next(iter(ids)))
                    for j in range(1, len(face) - 1)
                ]
            else:
                p = _face_minimum(center, face)
                if _squared(p, center) > radius * radius:
                    raise ValueError(
                        'A wholly free face cannot have distinct region roots'
                    )
                triangles = []
                for a, b in zip(face, face[1:] + face[:1]):
                    free_edge = [
                        v for v in (a, b) if _squared(v, center) > radius * radius
                    ]
                    edge_ids = {labels[v] for v in free_edge}
                    if not edge_ids:
                        continue
                    if len(edge_ids) == 1:
                        triangles.append(((p, a, b), next(iter(edge_ids))))
                    else:
                        q = _closest(center, a, b)
                        if _squared(q, center) > radius * radius:
                            raise ValueError(
                                'Free source edge cannot join different regions'
                            )
                        triangles.extend(
                            [((p, a, q), labels[a]), ((p, q, b), labels[b])]
                        )
            for tri, region in triangles:
                if coefficient(center, tri) != 0:
                    pieces.append((center, radius, tri, region))
            if len(pieces) > 4096:
                raise ValueError('Exact face-piece envelope exceeded')
    return pieces


def exact_result(
    model: Model,
    checked: dict[str, Any],
    request: VolumeRequest,
    bits: int,
) -> Optional[dict[str, Any]]:
    """Return only independently justified empty/whole-free shortcuts."""
    if not checked['regions']:
        result = aggregate(model, checked, request, [])
        result.update(
            method=SCHEME,
            face_piece_count=0,
            bits=bits,
            exact_shortcut='complete_empty_topology',
        )
        return result
    if len(checked['regions']) == 1 and cell_is_free(model, model.domain):
        result = aggregate(
            model,
            checked,
            request,
            [(_exact(volume(model.domain)), checked['regions'][0]['region_id'])],
        )
        result.update(
            method=SCHEME,
            face_piece_count=0,
            bits=bits,
            exact_shortcut='whole_domain_free',
        )
        return result
    return None


def reduce_bounds(
    model: Model,
    checked: dict[str, Any],
    request: VolumeRequest,
    bits: int,
    bounds: list[tuple],
) -> dict[str, Any]:
    """Reduce the complete canonical signed frontier with all error retained."""
    result = aggregate(model, checked, request, bounds)
    result['method'] = SCHEME
    result['face_piece_count'] = len(bounds)
    result['bits'] = bits
    return result


def evaluate(
    model: Model,
    proof: dict[str, Any],
    checked: dict[str, Any],
    request: VolumeRequest,
    bits: int,
) -> dict[str, Any]:
    """Integrate every reconstructed regional face piece and keep all errors."""
    shortcut = exact_result(model, checked, request, bits)
    if shortcut is not None:
        return shortcut
    pieces = assigned_faces(model, proof, checked)
    bounds = [
        (triangle_flux(center, radius, tri, bits), region)
        for center, radius, tri, region in pieces
    ]
    return reduce_bounds(model, checked, request, bits, bounds)


def prepare(model: Model, certificate: object) -> tuple[dict, dict, VolumeRequest]:
    """Admit symbolic headers and complete topology without evaluating volume.

    Parameters
    ----------
    model : Model
        Exact all-atom numerical model.
    certificate : object
        Untrusted complete topology, request, scheme and dyadic precision.

    Returns
    -------
    tuple
        Detached admitted certificate, independently checked topology and request.

    Raises
    ------
    ValueError, ArithmeticError
        Bad proof/scheme/units or the admitted numerical envelope is insufficient.
    """
    from . import verify

    cert = _record(
        deepcopy(certificate),
        {
            'schema',
            'kind',
            'model_sha256',
            'arithmetic',
            'topology_certificate',
            'request',
            'scheme',
            'bits',
        },
    )
    if (
        cert['schema'] != 'topomt.reference-validator.certificate/1'
        or cert['kind'] != 'power_edge_volume'
        or cert['model_sha256'] != model.digest
        or cert['arithmetic'] != 'rational-exact/1'
        or cert['scheme'] != SCHEME
        or type(cert['bits']) is not int
        or cert['bits'] not in BITS
    ):
        raise ValueError('Unsupported analytic edge scheme or precision')
    request = VolumeRequest.from_record(cert['request'])
    topology = verify(model, cert['topology_certificate'])
    if topology['kind'] != 'power_cell_topology':
        raise ValueError('Complete power-cell topology is required')
    return cert, topology, request


def check(model: Model, certificate: object) -> dict[str, Any]:
    """Check the complete analytic integral independently of its producer.

    Parameters
    ----------
    model : Model
        Exact all-atom numerical model.
    certificate : object
        Untrusted symbolic topology, unchanged request, scheme and precision.

    Returns
    -------
    dict
        Certified total/per-region bounds and their independently checked errors.

    Raises
    ------
    ValueError, ArithmeticError
        Invalid input/proof or insufficient admitted numerical envelope.
    """
    cert, topology, request = prepare(model, certificate)
    return evaluate(
        model, cert['topology_certificate'], topology, request, cert['bits']
    )
