"""Check exact contained-ball coverage and rigorously bounded analytic volumes.

The trusted formula is the integral of spherical caps, with rational Machin
pi enclosures and integer-derived square-root intervals. This route measures
total free volume; it supplies no exhaustive connected-region inventory.
"""

from fractions import Fraction
from itertools import combinations
from typing import Any

from ..model import Atom, Box, Model, _record, decode_scalar, encode_scalar
from ..volume_request import VolumeRequest
from ._interval import _exact, _Interval, _pi, _sqrt
from .geometry import _squared, volume


def _contains(outer: Atom, inner: Atom, probe: Fraction) -> bool:
    # A common probe cancels from the difference, but both operands are the
    # expanded radii used throughout this physical model.
    difference = (outer.radius + probe) - (inner.radius + probe)
    return difference >= 0 and _squared(outer.center, inner.center) <= difference**2


def _admit(model: Model) -> None:
    if not isinstance(model.domain, Box):
        raise ValueError('Analytic volume requires an axis-aligned box')
    for atom in model.atoms:
        radius = atom.radius + model.probe
        if any(
            not lo < c - radius or not c + radius < hi
            for lo, c, hi in zip(model.domain.lower, atom.center, model.domain.upper)
        ):
            raise ValueError(
                'Every expanded ball must be strictly contained in the box'
            )


def _budgets(terms: int, bits: int) -> None:
    if (
        type(terms) is not int
        or not 0 <= terms <= 512
        or type(bits) is not int
        or not 0 <= bits <= 4096
    ):
        raise ValueError(
            'Analytic budgets require 0..512 terms and 0..4096 distance bits'
        )


def _enclose(
    model: Model, clusters: list[list[int]], terms: int, bits: int
) -> _Interval:
    """Apply the declared cap formula after geometric admission is checked."""
    atoms = {a.source_id: a for a in model.atoms}
    coefficient = _exact(0)
    for cluster in clusters:
        radii = [atoms[i].radius + model.probe for i in cluster]
        sphere_sum = sum((Fraction(4, 3) * r**3 for r in radii), Fraction())
        current = _exact(sphere_sum)
        if len(cluster) == 2:
            a, b = (atoms[i] for i in cluster)
            squared = _squared(a.center, b.center)
            distance = _sqrt(squared, bits)
            cap_max = min(Fraction(4, 3) * r**3 for r in radii)
            if distance.lower == 0:
                lens = _Interval(Fraction(), cap_max)
            else:
                total, difference = sum(radii), radii[0] - radii[1]
                lens = (
                    (_exact(total) - distance).square()
                    * (
                        _exact(squared - 3 * difference**2)
                        + _exact(2 * total) * distance
                    )
                    / (_exact(12) * distance)
                ).clip(Fraction(), cap_max)
            current = current - lens
        coefficient = coefficient + current
    excluded = coefficient * _pi(terms)
    full = volume(model.domain)
    return (_exact(full) - excluded).clip(Fraction(), full)


def check(model: Model, cert: dict[str, Any]) -> dict[str, Any]:
    """Validate full source coverage, cluster disjointness, bounds and request."""
    _admit(model)
    request = VolumeRequest.from_record(cert['request'])
    refinement = _record(
        cert['refinement'],
        {'atan_terms', 'distance_bits', 'max_atan_terms', 'max_distance_bits'},
    )
    terms, bits = refinement['atan_terms'], refinement['distance_bits']
    max_terms, max_bits = refinement['max_atan_terms'], refinement['max_distance_bits']
    _budgets(terms, bits)
    _budgets(max_terms, max_bits)
    if terms > max_terms or bits > max_bits:
        raise ValueError('Actual refinement exceeds its recorded budget')
    atoms = {a.source_id: a for a in model.atoms}
    clusters = cert['clusters']
    if not isinstance(clusters, list) or any(
        not isinstance(g, list)
        or not 1 <= len(g) <= 2
        or any(type(i) is not int or i not in atoms for i in g)
        or g != sorted(set(g))
        for g in clusters
    ):
        raise ValueError('Invalid singleton/pair cluster records')
    if clusters != sorted(clusters):
        raise ValueError('Cluster order is not canonical')
    retained = [i for g in clusters for i in g]
    if len(retained) != len(set(retained)):
        raise ValueError('An atom occurs in multiple retained clusters')
    dominated = cert['dominated']
    if not isinstance(dominated, list):
        raise ValueError('Dominated atom coverage must be a list')
    removed = []
    for row in dominated:
        _record(row, {'source_id', 'covering_id'})
        i, j = row['source_id'], row['covering_id']
        if (
            type(i) is not int
            or type(j) is not int
            or i not in atoms
            or j not in retained
            or i in retained
            or not _contains(atoms[j], atoms[i], model.probe)
        ):
            raise ValueError('Claimed atom containment is unproved')
        removed.append(i)
    if removed != sorted(set(removed)) or set(retained) | set(removed) != set(atoms):
        raise ValueError('Source atom coverage is incomplete or duplicated')
    for i in retained:
        for j in atoms:
            if i != j and _contains(atoms[j], atoms[i], model.probe):
                if not _contains(atoms[i], atoms[j], model.probe) or j < i:
                    raise ValueError('Retained atom is not a canonical maximal ball')
    for first, second in combinations(clusters, 2):
        for i in first:
            for j in second:
                if (
                    _squared(atoms[i].center, atoms[j].center)
                    < (atoms[i].radius + atoms[j].radius + 2 * model.probe) ** 2
                ):
                    raise ValueError('Distinct clusters overlap in positive volume')
    for group in clusters:
        if len(group) == 2:
            a, b = (atoms[i] for i in group)
            distance = _squared(a.center, b.center)
            if (
                not (a.radius - b.radius) ** 2
                < distance
                < (a.radius + b.radius + 2 * model.probe) ** 2
            ):
                raise ValueError('Pair cluster is not a partial overlap')
    bounds = _enclose(model, clusters, terms, bits)
    if (
        decode_scalar(cert['volume_lower']) != bounds.lower
        or decode_scalar(cert['volume_upper']) != bounds.upper
    ):
        raise ValueError('Reported volume bounds differ from checked analytic bounds')
    passed = request.satisfied(bounds.lower, bounds.upper)
    if not passed and (terms != max_terms or bits != max_bits):
        raise ValueError('Unresolved volume stopped before its recorded budget')
    return {
        'volume_lower': encode_scalar(bounds.lower),
        'volume_upper': encode_scalar(bounds.upper),
        'volume_unit': 'nm**3',
        'volume_target': 'total_probe_center_free_set',
        'volume_enclosure_status': 'resolved',
        'precision_status': 'resolved' if passed else 'unresolved',
        'precision_request': request.to_record(),
        'stop_reason': 'requested_precision' if passed else 'refinement_limit',
        'boundary_incidence_status': 'not_computed',
        'analytic_scope': 'strictly-contained-singleton-pair-clusters/1',
    }
