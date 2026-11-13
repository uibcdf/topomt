"""Independently check exact source-hull equality and bounded box clipping."""

import hashlib
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..hull_model import CenterSource, HullLimits
from ..model import (
    Box,
    _determinant,
    _record,
    decode_point,
    decode_scalar,
    point,
    record_digest,
)
from .polytope import _decode_plane, _det, _evaluate, _result, _vertices


def _hull(
    source: CenterSource, cert: dict[str, Any], limits: HullLimits
) -> tuple[dict[str, Any], tuple[tuple[int, int, int, int], ...]]:
    _record(
        cert,
        {
            'schema',
            'kind',
            'source_sha256',
            'facets',
            'positive_weights',
            'normal_rank_witness',
            'affine_witness',
            'vertex_source_ids',
        },
    )
    if (
        cert['schema'] != 'topomt.reference-validator.hull-certificate/1'
        or cert['kind'] != 'center_hull'
        or cert['source_sha256'] != source.digest
    ):
        raise ValueError('Hull schema or center source binding differs')
    centers = dict(zip(source.source_ids, source.centers))
    witness = cert['affine_witness']
    if (
        not isinstance(witness, list)
        or len(witness) != 4
        or any(type(i) is not int or i not in centers for i in witness)
        or len(set(witness)) != 4
    ):
        raise ValueError('Invalid full-dimensional affine witness')
    base = centers[witness[0]]
    edges = [point([centers[j][i] - base[i] for i in range(3)]) for j in witness[1:]]
    if _determinant(*edges) == 0:
        raise ValueError('Source witness is not full-dimensional')
    rows = cert['facets']
    if not isinstance(rows, list) or not 4 <= len(rows) <= limits.max_facets:
        raise ValueError('Hull facet work limit or schema invalid')
    planes = []
    for row in rows:
        _record(row, {'coefficients', 'source_ids'})
        plane = _decode_plane(row['coefficients'])
        ids = row['source_ids']
        if (
            not isinstance(ids, list)
            or len(ids) != 3
            or any(type(i) is not int or i not in centers for i in ids)
            or ids != sorted(set(ids))
        ):
            raise ValueError('Invalid supporting-plane source witness')
        a, b, c = (centers[i] for i in ids)
        u, v = (
            point([b[i] - a[i] for i in range(3)]),
            point([c[i] - a[i] for i in range(3)]),
        )
        if not any(u[i] * v[j] - u[j] * v[i] for i, j in [(0, 1), (0, 2), (1, 2)]):
            raise ValueError('Supporting source points are collinear')
        if any(_evaluate(plane, centers[i]) != 0 for i in ids) or any(
            _evaluate(plane, p) > 0 for p in source.centers
        ):
            raise ValueError('Plane does not support the complete source hull')
        planes.append(plane)
    if planes != sorted(set(planes)):
        raise ValueError('Hull planes are duplicated or not canonical')
    raw = cert['positive_weights']
    if not isinstance(raw, list) or len(raw) != len(planes):
        raise ValueError('Boundedness weight coverage differs')
    weights = [decode_scalar(w) for w in raw]
    if (
        any(w <= 0 for w in weights)
        or sum(weights) != 1
        or any(
            sum((w * p[i] for w, p in zip(weights, planes)), Fraction()) != 0
            for i in range(3)
        )
    ):
        raise ValueError('Positive normal equilibrium is unproved')
    rank = cert['normal_rank_witness']
    if (
        not isinstance(rank, list)
        or len(rank) != 3
        or any(type(i) is not int or not 0 <= i < len(planes) for i in rank)
        or len(set(rank)) != 3
        or _det(*(planes[i][:3] for i in rank)) == 0
    ):
        raise ValueError('Normals do not supply a full-rank boundedness witness')
    # H is inside P by supporting halfspaces. P is nonempty/full-dimensional
    # by the source witness, and bounded by positive equilibrium + rank.
    # Enumerating ALL feasible independent triples lists every P vertex.
    # If each is a source center, P=conv(vertices(P)) is inside H as well.
    fixed = tuple(planes)
    vertices = _vertices(fixed, limits)
    owners = {
        p: min(i for i, q in centers.items() if q == p) for p in set(source.centers)
    }
    if not vertices or any(p not in owners for p in vertices):
        raise ValueError('Halfspaces describe a larger or invalid source hull')
    expected = sorted(owners[p] for p in vertices)
    vertex_ids = cert['vertex_source_ids']
    if (
        not isinstance(vertex_ids, list)
        or any(type(i) is not int for i in vertex_ids)
        or vertex_ids != expected
    ):
        raise ValueError('Complete hull vertex/source inventory differs')
    result = _result(vertices, fixed)
    if (
        result['geometric_dimension'] != 3
        or decode_scalar(result['geometric_volume']) <= 0
    ):
        raise ValueError('Full-dimensional hull has inconsistent geometric support')
    result['hull_equality_status'] = 'resolved'
    return result, fixed


def _clip_box(data: object) -> Box:
    row = _record(data, {'length_unit', 'lower', 'upper'})
    if row['length_unit'] != 'nm':
        raise ValueError('Clip box unit differs')
    return Box(decode_point(row['lower']), decode_point(row['upper']))


def _clip_planes(
    planes: tuple[tuple[int, int, int, int], ...], box: Box
) -> tuple[tuple[int, int, int, int], ...]:
    from .polytope import _canonical

    extra = []
    for axis in range(3):
        for sign, bound in [(-1, -box.lower[axis]), (1, box.upper[axis])]:
            normal = [Fraction()] * 3
            normal[axis] = Fraction(sign)
            extra.append(_canonical(tuple([*normal, bound])))
    return tuple(sorted(set(planes) | set(extra)))


def verify_hull(
    source: CenterSource, certificate: object, *, limits: HullLimits = HullLimits()
) -> dict[str, Any]:
    """Check source-hull equality or its exact intersection with a closed box.

    Parameters
    ----------
    source : CenterSource
        All exact nm centers and their original row/frame/input identity.
    certificate : object
        Portable hull or hull/box clip proof record.
    limits : HullLimits
        Finite source/plane/triple work ceilings. They do not alter the hull.

    Returns
    -------
    dict
        Accepted geometric domain, dimensions, recoverable supports and exact
        geometric volume. No obstacle-free volume or topology is computed.

    Raises
    ------
    ValueError
        A proof, source, unit, geometric obligation or work ceiling is invalid.
    """
    if len(source.centers) > limits.max_centers:
        raise ValueError('Hull center work limit exceeded')
    if not isinstance(certificate, dict):
        raise ValueError('Hull certificate must be a record')
    kind = certificate.get('kind')
    if kind == 'center_hull':
        result, _ = _hull(source, certificate, limits)
    elif kind == 'center_hull_clip':
        cert = _record(
            certificate,
            {
                'schema',
                'kind',
                'source_sha256',
                'hull',
                'clip_box',
                'claimed_vertices',
                'claimed_dimension',
                'claimed_volume',
            },
        )
        if (
            cert['schema'] != 'topomt.reference-validator.hull-certificate/1'
            or cert['source_sha256'] != source.digest
        ):
            raise ValueError('Clipped hull source binding differs')
        _, planes = _hull(source, cert['hull'], limits)
        box = _clip_box(cert['clip_box'])
        clipped = _clip_planes(planes, box)
        result = _result(_vertices(clipped, limits), clipped)
        if (
            cert['claimed_vertices'] != result['vertices']
            or type(cert['claimed_dimension']) is not int
            or cert['claimed_dimension'] != result['geometric_dimension']
            or decode_scalar(cert['claimed_volume'])
            != decode_scalar(result['geometric_volume'])
        ):
            raise ValueError('Clipped supports, dimension or volume differ')
        result['hull_equality_status'] = 'resolved'
        result['clipping_status'] = 'resolved'
    else:
        raise ValueError('Unsupported hull certificate kind')
    result.update(
        {
            'schema': 'topomt.reference-validator.hull-verification/1',
            'verification_status': 'accepted',
            'kind': kind,
            'source_sha256': source.digest,
            'certificate_sha256': record_digest(certificate),
            'trusted_geometry': 'rational-halfspace-vertices/1',
            'checker_limits': limits.to_record(),
            'python_version': sys.version,
            'verifier_files_sha256': {
                name: hashlib.sha256(
                    (Path(__file__).parents[1] / name).read_bytes()
                ).hexdigest()
                for name in [
                    'model.py',
                    'hull_model.py',
                    'contracts.py',
                    'verify/polytope.py',
                    'verify/center_hull.py',
                ]
            },
        }
    )
    return result
