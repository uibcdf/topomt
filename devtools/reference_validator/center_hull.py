"""Exact incremental hull proposal, independently checked through halfspaces."""

import copy
from fractions import Fraction
from itertools import combinations
from typing import Any

from .hull_model import CenterSource, HullLimits
from .model import Box, _determinant, encode_point, encode_scalar, point
from .verify.center_hull import _clip_planes, verify_hull
from .verify.polytope import (
    _canonical,
    _det,
    _encode_plane,
    _evaluate,
    _result,
    _vertices,
)


def _normal(
    a: tuple[Fraction, ...], b: tuple[Fraction, ...], c: tuple[Fraction, ...]
) -> tuple[Fraction, Fraction, Fraction]:
    u, v = (
        point([b[i] - a[i] for i in range(3)]),
        point([c[i] - a[i] for i in range(3)]),
    )
    return point(
        (
            u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0],
        )
    )


def _seed(points: dict[int, tuple[Fraction, Fraction, Fraction]]) -> list[int]:
    ids = sorted(points)
    if not ids:
        raise ValueError('A full-dimensional center hull is required')
    first = ids[0]
    a = points[first]
    second = next((i for i in ids if points[i] != a), None)
    if second is None:
        raise ValueError('A full-dimensional center hull is required')
    third = next((i for i in ids if any(_normal(a, points[second], points[i]))), None)
    if third is None:
        raise ValueError('A full-dimensional center hull is required')
    u, v = (
        point([points[second][j] - a[j] for j in range(3)]),
        point([points[third][j] - a[j] for j in range(3)]),
    )
    fourth = next(
        (
            i
            for i in ids
            if _determinant(u, v, point([points[i][j] - a[j] for j in range(3)])) != 0
        ),
        None,
    )
    if fourth is None:
        raise ValueError('A full-dimensional center hull is required')
    return [first, second, third, fourth]


def hull_certificate(
    source: CenterSource, *, limits: HullLimits = HullLimits()
) -> dict[str, Any]:
    """Propose an exact source hull with recoverable boundedness/equality proof.

    Parameters
    ----------
    source : CenterSource
        Exact centers, source row IDs, unit/frame and original input identity.
    limits : HullLimits
        Bounded source/halfspace/triple limits for this developer prototype.

    Returns
    -------
    dict
        A hull certificate. Its equality to the source convex hull is checked
        by exhaustive feasible plane triples, not by trusting this mesh.

    Raises
    ------
    ValueError
        Input is lower-dimensional, over budget or a proposed proof is invalid.
    """
    if len(source.centers) > limits.max_centers:
        raise ValueError('Hull center work limit exceeded')
    points = dict(zip(source.source_ids, source.centers))
    seed = _seed(points)
    interior = point(
        [sum((points[j][i] for j in seed), Fraction()) / 4 for i in range(3)]
    )

    def face(
        ids: tuple[int, int, int],
    ) -> tuple[tuple[int, int, int], tuple[Fraction, Fraction, Fraction], Fraction]:
        a, b, c = (points[i] for i in ids)
        normal = _normal(a, b, c)
        offset = sum((x * y for x, y in zip(normal, a)), Fraction())
        if sum((x * y for x, y in zip(normal, interior)), Fraction()) > offset:
            ids = (ids[1], ids[0], ids[2])
            normal = point([-v for v in normal])
            offset = -offset
        return ids, normal, offset

    faces = [face((ids[0], ids[1], ids[2])) for ids in combinations(seed, 3)]
    for i in sorted(points):
        if i in seed:
            continue
        visible = [
            f
            for f in faces
            if sum((a * b for a, b in zip(f[1], points[i])), Fraction()) > f[2]
        ]
        if not visible:
            continue
        boundary: dict[tuple[int, int], tuple[int, int]] = {}
        for ids, _, _ in visible:
            for a, b in zip(ids, (*ids[1:], ids[0])):
                key = (min(a, b), max(a, b))
                if key in boundary:
                    del boundary[key]
                else:
                    boundary[key] = (a, b)
        faces = [f for f in faces if f not in visible]
        faces.extend(face((a, b, i)) for a, b in boundary.values())
        if len(faces) > 4 * limits.max_centers:
            raise ValueError('Hull proposal face work limit exceeded')
    records: dict[tuple[int, int, int, int], list[int]] = {}
    weights: dict[tuple[int, int, int, int], Fraction] = {}
    for ids, normal, offset in faces:
        plane = _canonical((*normal, offset))
        index = next(i for i in range(3) if plane[i])
        weight = normal[index] / plane[index]
        if weight <= 0:
            raise ValueError('Invalid oriented face weight')
        records[plane] = min(records.get(plane, sorted(ids)), sorted(ids))
        weights[plane] = weights.get(plane, Fraction()) + weight
    planes = tuple(sorted(records))
    owners = {
        p: min(i for i, q in points.items() if q == p) for p in set(points.values())
    }
    # The proposal lists source centers with full-rank active planes. The
    # checker independently enumerates ALL feasible plane triples, including
    # potential vertices outside the source, to prove hull equality.
    vertex_ids = []
    for p, owner in owners.items():
        active = [plane for plane in planes if _evaluate(plane, p) == 0]
        if any(_det(*triple) != 0 for triple in combinations(active, 3)):
            vertex_ids.append(owner)
    total = sum(weights.values())
    rank = next(
        (
            list(ids)
            for ids in combinations(range(len(planes)), 3)
            if _det(*(planes[i][:3] for i in ids)) != 0
        ),
        None,
    )
    cert = {
        'schema': 'topomt.reference-validator.hull-certificate/1',
        'kind': 'center_hull',
        'source_sha256': source.digest,
        'facets': [
            {'coefficients': _encode_plane(p), 'source_ids': records[p]} for p in planes
        ],
        'positive_weights': [encode_scalar(weights[p] / total) for p in planes],
        'normal_rank_witness': rank,
        'affine_witness': seed,
        'vertex_source_ids': sorted(vertex_ids),
    }
    verify_hull(source, cert, limits=limits)
    return cert


def clip_certificate(
    source: CenterSource,
    hull: dict[str, Any],
    box: Box,
    *,
    limits: HullLimits = HullLimits(),
) -> dict[str, Any]:
    """Certify the exact closed hull/box intersection, retaining zero-volume seams.

    Parameters
    ----------
    source : CenterSource
        Original centers bound by the hull proof.
    hull : dict
        Original complete hull certificate, checked before use.
    box : Box
        Closed exact nm clipping box; it does not replace the physical hull.
    limits : HullLimits
        Explicit finite source/plane/triple ceilings.

    Returns
    -------
    dict
        Geometric clipping proof, with empty/lower-dimensional states distinct.

    Raises
    ------
    ValueError
        Original proof, clipping request or resource envelope is invalid.
    """
    checked = verify_hull(source, hull, limits=limits)
    from .verify.polytope import _decode_plane

    planes = tuple(_decode_plane(f['coefficients']) for f in checked['facets'])
    clipped = _clip_planes(planes, box)
    result = _result(_vertices(clipped, limits), clipped)
    cert = {
        'schema': 'topomt.reference-validator.hull-certificate/1',
        'kind': 'center_hull_clip',
        'source_sha256': source.digest,
        'hull': copy.deepcopy(hull),
        'clip_box': {
            'length_unit': 'nm',
            'lower': encode_point(box.lower),
            'upper': encode_point(box.upper),
        },
        'claimed_vertices': result['vertices'],
        'claimed_dimension': result['geometric_dimension'],
        'claimed_volume': result['geometric_volume'],
    }
    verify_hull(source, cert, limits=limits)
    return cert
