"""Bounded exact contracts and declared convex domains for power-cell proofs."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Optional

from .model import Atom, Box, HullDomain, Model, point
from .verify.polytope import _canonical


@dataclass(frozen=True)
class PowerLimits:
    """Finite work ceilings, never geometric tolerances or size cutoffs."""

    max_atoms: int = 128
    max_support_planes: int = 48
    max_vertices_per_cell: int = 128
    max_total_vertices: int = 8192
    max_edges: int = 32768
    max_clip_steps: int = 50000

    def __post_init__(self) -> None:
        maxima = (128, 48, 128, 8192, 32768, 50000)
        for value, maximum in zip(vars(self).values(), maxima):
            if type(value) is not int or not 1 <= value <= maximum:
                raise ValueError('Power-cell work limit exceeds its bounded envelope')
        if self.max_support_planes < 6:
            raise ValueError('Power-cell support must admit the bounding box')

    def to_record(self) -> dict[str, int]:
        """Return detached work limits, without changing the physical model."""
        return dict(vars(self))


def _box_planes(domain: Box) -> tuple[tuple[int, int, int, int], ...]:
    planes = []
    for axis in range(3):
        for sign, bound in [(-1, -domain.lower[axis]), (1, domain.upper[axis])]:
            normal = [Fraction()] * 3
            normal[axis] = Fraction(sign)
            planes.append(_canonical(tuple([*normal, bound])))
    return tuple(sorted(planes))


def domain_planes(model: Model) -> tuple[tuple[int, int, int, int], ...]:
    domain = model.domain
    if isinstance(domain, HullDomain):
        return domain.planes
    if isinstance(domain, Box):
        return _box_planes(domain)
    planes = []
    for opposite in range(4):
        a, b, c = [v for i, v in enumerate(domain.vertices) if i != opposite]
        u, v = (
            point([b[k] - a[k] for k in range(3)]),
            point([c[k] - a[k] for k in range(3)]),
        )
        n = point(
            (
                u[1] * v[2] - u[2] * v[1],
                u[2] * v[0] - u[0] * v[2],
                u[0] * v[1] - u[1] * v[0],
            )
        )
        rhs = sum((x * y for x, y in zip(n, a)), Fraction())
        if sum(x * y for x, y in zip(n, domain.vertices[opposite])) > rhs:
            n, rhs = point([-x for x in n]), -rhs
        planes.append(_canonical(tuple([*n, rhs])))
    return tuple(sorted(planes))


def bounding_box(model: Model) -> Box:
    return Box(
        point([min(v[k] for v in model.domain.vertices) for k in range(3)]),
        point([max(v[k] for v in model.domain.vertices) for k in range(3)]),
    )


def bounding_planes(model: Model) -> tuple[tuple[int, int, int, int], ...]:
    return _box_planes(bounding_box(model))


def coincident_dominators(model: Model, atom: Atom) -> list[int]:
    return sorted(
        a.source_id
        for a in model.atoms
        if a.center == atom.center and a.radius > atom.radius
    )


def proposed_planes(
    model: Model, atom: Optional[Atom]
) -> tuple[tuple[int, int, int, int], ...]:
    """Linearize the producer's fixed-probe power comparisons exactly."""
    planes = set(domain_planes(model)) | set(bounding_planes(model))
    if atom is not None:
        own = (
            sum((x * x for x in atom.center), Fraction())
            - (atom.radius + model.probe) ** 2
        )
        for other in model.atoms:
            if other.center == atom.center:
                continue
            rhs = (
                sum((x * x for x in other.center), Fraction())
                - (other.radius + model.probe) ** 2
                - own
            )
            normal = tuple(2 * (b - a) for a, b in zip(atom.center, other.center))
            planes.add(_canonical(tuple([*normal, rhs])))
    return tuple(sorted(planes))


def certificate_header(model: Model) -> dict[str, Any]:
    return {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'power_cell_topology',
        'model_sha256': model.digest,
        'arithmetic': 'rational-exact/1',
        'construction': 'power-skeleton-caps/1',
    }
