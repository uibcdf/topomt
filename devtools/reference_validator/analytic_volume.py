"""Bounded P1 precision producer for analytically admitted ball clusters."""

from itertools import combinations
from typing import Any

from .model import Model, encode_scalar
from .verify import verify
from .verify.analytic_volume import _admit, _budgets, _contains, _enclose
from .verify.geometry import _squared
from .volume_request import VolumeRequest


def volume_certificate(
    model: Model,
    request: VolumeRequest,
    *,
    max_atan_terms: int = 64,
    max_distance_bits: int = 256,
) -> dict[str, Any]:
    """Produce a checked-primitive analytic total-volume certificate.

    Parameters
    ----------
    model : Model
        Exact nm balls, all strictly inside an axis-aligned box. After removing
        contained balls, each positive-overlap cluster must have size one/two.
    request : VolumeRequest
        All enabled absolute nm**3 and dimensionless relative tolerances.
    max_atan_terms, max_distance_bits : int
        Finite constant/distance refinement ceilings; zero retains coarse bounds.

    Returns
    -------
    dict
        Portable certificate for independent checking. A valid volume enclosure
        can still have unresolved requested precision. No topology is inferred.

    Raises
    ------
    ValueError
        Geometry, request or resource limits are outside the admitted scope.
    """
    _budgets(max_atan_terms, max_distance_bits)
    _admit(model)
    if len(model.atoms) > 512:
        raise ValueError('Analytic producer atom budget exceeded')
    atoms = sorted(model.atoms, key=lambda a: a.source_id)
    maximal = [
        a
        for a in atoms
        if not any(
            a.source_id != b.source_id
            and _contains(b, a, model.probe)
            and (not _contains(a, b, model.probe) or b.source_id < a.source_id)
            for b in atoms
        )
    ]
    removed = [
        {
            'source_id': a.source_id,
            'covering_id': next(
                b.source_id for b in maximal if _contains(b, a, model.probe)
            ),
        }
        for a in atoms
        if a not in maximal
    ]
    neighbors: dict[int, set[int]] = {a.source_id: set() for a in maximal}
    for a, b in combinations(maximal, 2):
        if _squared(a.center, b.center) < (a.radius + b.radius + 2 * model.probe) ** 2:
            neighbors[a.source_id].add(b.source_id)
            neighbors[b.source_id].add(a.source_id)
    remaining = set(neighbors)
    clusters = []
    while remaining:
        group = set()
        stack = [min(remaining)]
        while stack:
            current = stack.pop()
            if current not in group:
                group.add(current)
                stack.extend(neighbors[current] - group)
        if len(group) > 2:
            raise ValueError(
                'Analytic precision requires singleton/pair overlap clusters'
            )
        clusters.append(sorted(group))
        remaining -= group
    cert = {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'analytic_ball_union_volume',
        'arithmetic': 'rational-exact/1',
        'model_sha256': model.digest,
        'request': request.to_record(),
        'clusters': clusters,
        'dominated': removed,
    }
    terms, bits = 0, 0
    while True:
        bounds = _enclose(model, clusters, terms, bits)
        cert['volume_lower'], cert['volume_upper'] = (
            encode_scalar(bounds.lower),
            encode_scalar(bounds.upper),
        )
        cert['refinement'] = {
            'atan_terms': terms,
            'distance_bits': bits,
            'max_atan_terms': max_atan_terms,
            'max_distance_bits': max_distance_bits,
        }
        if request.satisfied(bounds.lower, bounds.upper) or (
            terms == max_atan_terms and bits == max_distance_bits
        ):
            verify(model, cert)
            return cert
        terms = min(max_atan_terms, max(1, 2 * terms))
        bits = min(max_distance_bits, max(1, 2 * bits))
