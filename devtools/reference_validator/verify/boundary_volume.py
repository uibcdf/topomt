"""Outward bounded face flux, with reconstructed complete power-cell coverage.

For an owner centered at c with expanded radius R use
F(x)=(x-c)*(1-R**3/|x-c|**3)/3 outside its ball, zero inside.
Its divergence is the free-space indicator and its sphere-normal flux is zero.
The proof argument and signed region accounting live in the developer guide.
"""

from fractions import Fraction
from typing import Any

from ..model import Model, _record, decode_point, encode_scalar, point
from ..volume_request import VolumeRequest
from ._interval import _exact, _Interval, _outward, _sqrt
from .geometry import _squared, volume
from .polytope import _result
from .power_cells import _locate, _planes


def roots(model: Model, topology: dict[str, Any]) -> list[tuple]:
    """Rebuild every oriented nonzero-flux face triangle from checked cells."""
    atoms = {a.source_id: a for a in model.atoms}
    result = []
    seen: dict[tuple, tuple] = {}
    for cell in topology['cells']:
        if 'coincident_dominator' in cell:
            continue
        vertices = tuple(decode_point(p) for p in cell['vertices'])
        atom = atoms.get(cell['atom_id'])
        planes = _planes(model, atom)
        poly = _result(vertices, tuple(planes[i] for i in cell['support']))
        if poly['geometric_dimension'] != 3:
            continue
        center = point((0, 0, 0)) if atom is None else atom.center
        radius = Fraction() if atom is None else atom.radius + model.probe
        if vertices in seen:
            if seen[vertices] != (center, radius):
                raise ValueError('Coincident full cells have different owner balls')
            continue
        seen[vertices] = (center, radius)
        for facet in poly['facets']:
            indices = facet['vertex_indices']
            for j in range(1, len(indices) - 1):
                triangle = tuple(
                    vertices[i] for i in [indices[0], indices[j], indices[j + 1]]
                )
                if coefficient(center, triangle) != 0:
                    result.append((center, radius, triangle))
        if len(result) > 4096:
            raise ValueError('Boundary root-triangle envelope exceeded')
    return result


def coefficient(center: tuple, triangle: tuple) -> Fraction:
    """Signed h*area/3 as a rational determinant; no normal normalization."""
    from ..model import _determinant

    return (
        _determinant(*(point([p[i] - center[i] for i in range(3)]) for p in triangle))
        / 6
    )


def children(triangle: tuple) -> tuple:
    """Four exact triangles with disjoint interiors and the same orientation."""
    a, b, c = triangle
    ab, bc, ca = (
        point([(x + y) / 2 for x, y in zip(p, q)]) for p, q in [(a, b), (b, c), (c, a)]
    )
    return ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))


def leaf_bound(
    model: Model,
    topology: dict[str, Any],
    checked: dict[str, Any],
    center: tuple,
    radius: Fraction,
    triangle: tuple,
    bits: int,
) -> tuple:
    """Bound one face integral and prove assignment when the whole piece is free."""
    low = sum(
        (
            max(
                min(p[i] for p in triangle) - center[i],
                center[i] - max(p[i] for p in triangle),
                Fraction(),
            )
            ** 2
            for i in range(3)
        ),
        Fraction(),
    )
    high = max(_squared(p, center) for p in triangle)

    def weight(squared: Fraction) -> _Interval:
        if radius == 0:
            return _exact(1)
        if squared <= radius**2:
            return _exact(0)
        distance = _sqrt(squared, bits)
        if distance.lower == 0:
            return _Interval(Fraction(), Fraction(1))
        return (_exact(1) - _exact(radius**3) / (distance * distance * distance)).clip(
            Fraction(), Fraction(1)
        )

    bound = _exact(coefficient(center, triangle)) * _Interval(
        weight(low).lower, weight(high).upper
    )
    ids = [r['region_id'] for r in checked['regions']]
    region = ids[0] if len(ids) == 1 else None
    if region is None and low > radius**2:
        centroid = point(
            [sum((p[i] for p in triangle), Fraction()) / 3 for i in range(3)]
        )
        location = _locate(model, topology, checked, centroid)
        if location['point_state'] != 'free':
            raise ValueError('Whole-free source face has no strict free centroid')
        region = location['region_id']
    # Every rounding contribution is retained in the enclosure. Common dyadic
    # denominators avoid explosive least-common-multiple growth in reductions.
    return (bound if bound.lower == bound.upper else _outward(bound, bits)), region


def aggregate(
    model: Model, checked: dict[str, Any], request: VolumeRequest, bounds: list[tuple]
) -> dict[str, Any]:
    """Signed flux accounting; uncertain assignments cannot supply positive lower mass."""
    ids = [r['region_id'] for r in checked['regions']]
    total = _exact(0)
    regions = {key: _exact(0) for key in ids}
    for bound, region in bounds:
        total = total + bound
        if region is not None:
            regions[region] = regions[region] + bound
        else:
            for key in ids:
                regions[key] = regions[key] + _Interval(
                    min(Fraction(), bound.lower), max(Fraction(), bound.upper)
                )
    if not ids:
        total = _exact(0)
    total = total.clip(Fraction(), volume(model.domain))
    regions = {
        key: value.clip(Fraction(), total.upper) for key, value in regions.items()
    }
    rows = [
        {
            'region_id': key,
            'lower': encode_scalar(value.lower),
            'upper': encode_scalar(value.upper),
            'precision_status': 'resolved'
            if request.satisfied(value.lower, value.upper)
            else 'unresolved',
        }
        for key, value in regions.items()
    ]
    passed = request.satisfied(total.lower, total.upper) and all(
        r['precision_status'] == 'resolved' for r in rows
    )
    return {
        'volume_lower': encode_scalar(total.lower),
        'volume_upper': encode_scalar(total.upper),
        'volume_unit': 'nm**3',
        'regions': rows,
        'precision_status': 'resolved' if passed else 'unresolved',
        'total_precision_status': 'resolved'
        if request.satisfied(total.lower, total.upper)
        else 'unresolved',
        'volume_enclosure_status': 'resolved',
        'topology_complete': True,
        'n_components': len(ids),
        'topology_status': 'resolved',
        'n_boundary_patches': checked['n_boundary_patches'],
        'boundary_status': 'resolved',
        'per_region_volume_status': 'resolved',
        'method': 'power-face-flux/1',
    }


def check(model: Model, certificate: object) -> dict[str, Any]:
    """Reconstruct oriented faces, complete subdivisions and signed flux bounds.

    Parameters
    ----------
    model : Model
        Original numerical model in nm.
    certificate : object
        Untrusted topology and canonical triangle paths; no numerical totals.

    Returns
    -------
    dict
        Checked total and per-region enclosures with separate precision states.

    Raises
    ------
    ValueError
        Invalid geometry, subdivision coverage or finite work limit.
    """
    from . import verify

    cert = _record(
        certificate,
        {
            'schema',
            'kind',
            'model_sha256',
            'arithmetic',
            'topology_certificate',
            'request',
            'bits',
            'leaves',
        },
    )
    if type(cert['bits']) is not int or cert['bits'] not in (64, 128, 256, 512):
        raise ValueError('Boundary arithmetic precision exceeds its envelope')
    checked = verify(model, cert['topology_certificate'])
    if checked['kind'] != 'power_cell_topology':
        raise ValueError('Boundary integration requires complete source-cell topology')
    triangles = roots(model, cert['topology_certificate'])
    paths = cert['leaves']
    if not isinstance(paths, list) or len(paths) > 4096:
        raise ValueError('Boundary leaf envelope exceeded')
    by_root: dict[int, set[str]] = {i: set() for i in range(len(triangles))}
    for row in paths:
        row = _record(row, {'root', 'path'})
        index, path = row['root'], row['path']
        if (
            type(index) is not int
            or index not in by_root
            or not isinstance(path, str)
            or len(path) > 12
            or any(c not in '0123' for c in path)
            or path in by_root[index]
        ):
            raise ValueError('Invalid boundary root/path or duplicate leaf')
        by_root[index].add(path)
    if paths != sorted(paths, key=lambda p: (p['root'], p['path'])):
        raise ValueError('Boundary paths must be canonical')
    bounds = []
    for index, (center, radius, triangle) in enumerate(triangles):
        leaves = by_root[index]
        prefixes = {p[:i] for p in leaves for i in range(len(p))}
        if leaves & prefixes:
            raise ValueError('Boundary partition has overlapping ancestors')
        stack = [('', triangle)]
        while stack:
            path, tri = stack.pop()
            if path in leaves:
                bounds.append(
                    leaf_bound(
                        model,
                        cert['topology_certificate'],
                        checked,
                        center,
                        radius,
                        tri,
                        cert['bits'],
                    )
                )
            elif path in prefixes:
                stack.extend(
                    (path + str(i), child) for i, child in enumerate(children(tri))
                )
            else:
                raise ValueError('Boundary partition omits a face or child')
    return aggregate(model, checked, VolumeRequest.from_record(cert['request']), bounds)
