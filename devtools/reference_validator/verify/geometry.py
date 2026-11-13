"""Trusted exact primitive predicates for the developer certificate checker.

These are sufficient whole-cell predicates, not a complete free-piece or
topology construction. Fraction arithmetic, convexity and polynomial signs
form the declared trusted base. No floating geometry or native labels are used.
"""

from fractions import Fraction
from itertools import combinations

from ..model import Box, HullDomain, Model, Tetrahedron, _determinant, point


def _squared(a: tuple[Fraction, ...], b: tuple[Fraction, ...]) -> Fraction:
    return sum(((x - y) ** 2 for x, y in zip(a, b)), Fraction())


def contains(
    domain: Box | Tetrahedron | HullDomain, x: tuple[Fraction, Fraction, Fraction]
) -> bool:
    """Check closed convex-domain membership exactly, including its boundary."""
    if isinstance(domain, Box):
        return all(a <= v <= b for a, v, b in zip(domain.lower, x, domain.upper))
    if isinstance(domain, HullDomain):
        return all(
            sum(n * v for n, v in zip(plane[:3], x)) <= plane[3]
            for plane in domain.planes
        )
    v = domain.vertices
    edges = [tuple(q[i] - v[0][i] for i in range(3)) for q in v[1:]]
    rhs = tuple(x[i] - v[0][i] for i in range(3))
    determinant = _determinant(*edges)
    weights = [
        _determinant(*(edges[:i] + [rhs] + edges[i + 1 :])) / determinant
        for i in range(3)
    ]
    return all(w >= 0 for w in weights) and sum(weights) <= 1


def volume(domain: Box | Tetrahedron | HullDomain) -> Fraction:
    """Compute the exact rational volume of the full declared cell in nm**3."""
    if isinstance(domain, HullDomain):
        return domain.geometric_volume
    if isinstance(domain, Box):
        result = Fraction(1)
        for a, b in zip(domain.lower, domain.upper):
            result *= b - a
        return result
    base = domain.vertices[0]
    edges = [tuple(v[i] - base[i] for i in range(3)) for v in domain.vertices[1:]]
    return abs(_determinant(*edges)) / 6


def point_is_free(model: Model, x: tuple[Fraction, Fraction, Fraction]) -> bool:
    """Check a position against the domain and every expanded source ball."""
    return contains(model.domain, x) and all(
        _squared(x, a.center) > (a.radius + model.probe) ** 2 for a in model.atoms
    )


def segment_is_free(
    model: Model,
    start: tuple[Fraction, Fraction, Fraction],
    end: tuple[Fraction, Fraction, Fraction],
) -> bool:
    """Certify a complete straight segment with strict all-atom clearance."""
    if not contains(model.domain, start) or not contains(model.domain, end):
        return False
    direction = tuple(b - a for a, b in zip(start, end))
    length_squared = _squared(start, end)
    for atom in model.atoms:
        projection = sum(
            ((c - a) * d for c, a, d in zip(atom.center, start, direction)), Fraction()
        )
        parameter = (
            max(Fraction(), min(Fraction(1), projection / length_squared))
            if length_squared
            else Fraction()
        )
        closest = tuple(a + parameter * d for a, d in zip(start, direction))
        if _squared(closest, atom.center) <= (atom.radius + model.probe) ** 2:
            return False
    return True


def cell_is_free(model: Model, cell: Box | Tetrahedron | HullDomain) -> bool:
    """Sufficient whole-cell clearance using an exact bounding-box lower bound.

    The caller must establish cell containment/partition provenance separately.
    A failed sufficient test means unresolved, never proof of occupation.
    """
    lower = tuple(min(v[i] for v in cell.vertices) for i in range(3))
    upper = tuple(max(v[i] for v in cell.vertices) for i in range(3))
    for atom in model.atoms:
        minimum = sum(
            (
                max(lo - c, Fraction(), c - hi) ** 2
                for lo, c, hi in zip(lower, atom.center, upper)
            ),
            Fraction(),
        )
        if minimum <= (atom.radius + model.probe) ** 2:
            return False
    return True


def cell_is_covered(
    model: Model, cell: Box | Tetrahedron | HullDomain, atom_id: int
) -> bool:
    """Prove complete convex-cell coverage by one specified expanded ball."""
    atom = next((a for a in model.atoms if a.source_id == atom_id), None)
    return atom is not None and all(
        _squared(v, atom.center) <= (atom.radius + model.probe) ** 2
        for v in cell.vertices
    )


def split(cell: Box | Tetrahedron | HullDomain) -> tuple[Box | Tetrahedron, ...]:
    """Partition boxes into eight children, tetrahedra by exact edge bisection.

    Longest-edge ties use vertex index order. Child IDs are stable only within
    this exact model and subdivision convention, not across rigid transforms.
    """
    if not isinstance(cell, (Box, Tetrahedron)):
        raise ValueError(
            'Subdivision requires a box or tetrahedron; hull partition is not admitted'
        )
    if isinstance(cell, Box):
        mid = tuple((a + b) / 2 for a, b in zip(cell.lower, cell.upper))
        return tuple(
            Box(
                point([mid[i] if code & (1 << i) else cell.lower[i] for i in range(3)]),
                point([cell.upper[i] if code & (1 << i) else mid[i] for i in range(3)]),
            )
            for code in range(8)
        )
    a, b = max(
        combinations(range(4), 2),
        key=lambda pair: _squared(cell.vertices[pair[0]], cell.vertices[pair[1]]),
    )
    mid = point([(cell.vertices[a][i] + cell.vertices[b][i]) / 2 for i in range(3)])
    first, second = list(cell.vertices), list(cell.vertices)
    first[a], second[b] = mid, mid
    return Tetrahedron(tuple(first)), Tetrahedron(tuple(second))
