"""Trusted exact halfspace intersections, geometric dimensions and volumes.

The checker enumerates every independent plane triple using integer Cramer
arithmetic. No hull producer, floating geometry, mesh topology or sample labels
enter these geometric conclusions. Full mathematical assumptions are documented
in the hull checkpoint.
"""

from fractions import Fraction
from functools import cmp_to_key
from itertools import combinations
from math import comb, gcd, lcm

from ..hull_model import HullLimits
from ..model import (
    _determinant,
    _integer_text,
    _parse_integer,
    encode_point,
    encode_scalar,
    point,
)


def _cross(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, int, int]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return sum(x * y for x, y in zip(a[:3], b[:3]))


def _det(a: tuple[int, ...], b: tuple[int, ...], c: tuple[int, ...]) -> int:
    return _dot(a, _cross(b, c))


def _canonical(values: tuple[Fraction, ...]) -> tuple[int, int, int, int]:
    multiplier = lcm(*(v.denominator for v in values))
    integers = [int(v * multiplier) for v in values]
    divisor = gcd(*integers)
    if not divisor or not any(integers[:3]):
        raise ValueError('Degenerate supporting plane')
    return (
        integers[0] // divisor,
        integers[1] // divisor,
        integers[2] // divisor,
        integers[3] // divisor,
    )


def _encode_plane(plane: tuple[int, ...]) -> list[str]:
    return [_integer_text(v) for v in plane]


def _decode_plane(raw: object) -> tuple[int, int, int, int]:
    if (
        not isinstance(raw, list)
        or len(raw) != 4
        or not all(isinstance(v, str) for v in raw)
    ):
        raise ValueError('Invalid integer halfspace')
    plane = tuple(_parse_integer(v) for v in raw)
    if _encode_plane(plane) != raw or not any(plane[:3]) or gcd(*plane) != 1:
        raise ValueError('Halfspace must have canonical primitive coefficients')
    return plane[0], plane[1], plane[2], plane[3]


def _evaluate(plane: tuple[int, ...], p: tuple[Fraction, ...]) -> Fraction:
    return sum((a * x for a, x in zip(plane[:3], p)), Fraction()) - plane[3]


def _vertices(
    planes: tuple[tuple[int, int, int, int], ...], limits: HullLimits
) -> tuple[tuple[Fraction, Fraction, Fraction], ...]:
    count = len(planes)
    if count > limits.max_facets or comb(count, 3) > limits.max_plane_triples:
        raise ValueError('Hull plane/triple work limit exceeded')
    crosses = {
        (i, j): _cross(planes[i], planes[j]) for i, j in combinations(range(count), 2)
    }
    result = set()
    for i, j, k in combinations(range(count), 3):
        determinant = _dot(planes[i], crosses[j, k])
        if determinant == 0:
            continue
        numerator = tuple(
            planes[i][3] * crosses[j, k][axis]
            - planes[j][3] * crosses[i, k][axis]
            + planes[k][3] * crosses[i, j][axis]
            for axis in range(3)
        )
        if determinant < 0:
            determinant = -determinant
            numerator = tuple(-v for v in numerator)
        if all(_dot(plane, numerator) <= plane[3] * determinant for plane in planes):
            result.add(point([Fraction(v, determinant) for v in numerator]))
    return tuple(sorted(result))


def _dimension(vertices: tuple[tuple[Fraction, Fraction, Fraction], ...]) -> int:
    if not vertices:
        return -1
    base = vertices[0]
    directions = [point([v[i] - base[i] for i in range(3)]) for v in vertices[1:]]
    first = next((v for v in directions if any(v)), None)
    if first is None:
        return 0
    second = next(
        (
            v
            for v in directions
            if any(
                first[i] * v[j] - first[j] * v[i] for i, j in combinations(range(3), 2)
            )
        ),
        None,
    )
    if second is None:
        return 1
    return 3 if any(_determinant(first, second, v) != 0 for v in directions) else 2


def _face_order(
    vertices: tuple[tuple[Fraction, Fraction, Fraction], ...],
    indices: list[int],
    plane: tuple[int, ...],
) -> list[int]:
    drop = max(range(3), key=lambda i: abs(plane[i]))
    axes = [i for i in range(3) if i != drop]
    center = [
        sum((vertices[j][a] for j in indices), Fraction()) / len(indices) for a in axes
    ]
    rays = {
        j: (vertices[j][axes[0]] - center[0], vertices[j][axes[1]] - center[1])
        for j in indices
    }

    def compare(i: int, j: int) -> int:
        a, b = rays[i], rays[j]
        half_a = 0 if a[1] > 0 or (a[1] == 0 and a[0] >= 0) else 1
        half_b = 0 if b[1] > 0 or (b[1] == 0 and b[0] >= 0) else 1
        if half_a != half_b:
            return half_a - half_b
        cross = a[0] * b[1] - a[1] * b[0]
        return -1 if cross > 0 else 1 if cross < 0 else (i > j) - (i < j)

    return sorted(indices, key=cmp_to_key(compare))


def _result(
    vertices: tuple[tuple[Fraction, Fraction, Fraction], ...],
    planes: tuple[tuple[int, int, int, int], ...],
) -> dict:
    dimension = _dimension(vertices)
    total = Fraction()
    facets = []
    if dimension == 3:
        interior = point(
            [
                sum((p[i] for p in vertices), Fraction()) / len(vertices)
                for i in range(3)
            ]
        )
        for plane in planes:
            indices = [i for i, p in enumerate(vertices) if _evaluate(plane, p) == 0]
            if len(indices) < 3:
                continue
            cycle = _face_order(vertices, indices, plane)
            a, b, c = (vertices[i] for i in cycle[:3])
            first = point([b[i] - a[i] for i in range(3)])
            second = point([c[i] - a[i] for i in range(3)])
            if _determinant(first, second, point(plane[:3])) < 0:
                cycle.reverse()
            anchor = vertices[cycle[0]]
            face_volume = Fraction()
            for left, right in zip(cycle[1:-1], cycle[2:]):
                vectors = [
                    point([p[i] - interior[i] for i in range(3)])
                    for p in (anchor, vertices[left], vertices[right])
                ]
                face_volume += abs(_determinant(*vectors)) / 6
            if face_volume:
                total += face_volume
                facets.append(
                    {'coefficients': _encode_plane(plane), 'vertex_indices': cycle}
                )
    return {
        'geometric_dimension': dimension,
        'geometric_state': 'empty'
        if dimension < 0
        else 'lower_dimensional'
        if dimension < 3
        else 'full_dimensional',
        'vertices': [encode_point(p) for p in vertices],
        'facets': facets,
        'geometric_volume': encode_scalar(total),
        'volume_unit': 'nm**3',
        'length_unit': 'nm',
        'free_volume_status': 'not_computed',
        'free_topology_status': 'not_computed',
    }
