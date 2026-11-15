"""Propose exact-coverage face-flux certificates with outward local bounds."""

from copy import deepcopy
from heapq import heappop, heappush
from typing import Any

from .model import Model
from .verify import verify
from .verify.boundary_volume import aggregate, children, leaf_bound, roots
from .volume_request import VolumeRequest


def boundary_volume_certificate(
    model: Model,
    topology_certificate: object,
    request: VolumeRequest,
    *,
    max_leaves: int = 4096,
    bits: int = 64,
) -> dict[str, Any]:
    """Propose a complete boundary partition; precision may remain unresolved.

    Parameters
    ----------
    model : Model
        Original exact numerical model.
    topology_certificate : object
        Untrusted complete power-cell topology, checked before use.
    request : VolumeRequest
        Total and every-region error requirements, without relaxation.
    max_leaves : int
        Finite maximum number of face triangles, at most 4096.
    bits : int
        Outward dyadic square-root precision: 64, 128, 256 or 512.

    Returns
    -------
    dict
        Proposed topology-bound certificate with reconstructible face paths.

    Raises
    ------
    ValueError
        Invalid proof, arithmetic or finite work envelope.
    """
    if type(max_leaves) is not int or not 1 <= max_leaves <= 4096:
        raise ValueError('Boundary leaf budget must be in 1..4096')
    if type(bits) is not int or bits not in (64, 128, 256, 512):
        raise ValueError('Invalid boundary arithmetic precision')
    proof = deepcopy(topology_certificate)
    checked = verify(model, proof)
    if checked['kind'] != 'power_cell_topology':
        raise ValueError('Complete power-cell topology required')
    if not isinstance(proof, dict):
        raise ValueError('Topology must be a record')
    return _construct(model, proof, checked, request, max_leaves, bits)


def _construct(
    model: Model,
    proof: dict[str, Any],
    checked: dict[str, Any],
    request: VolumeRequest,
    max_leaves: int,
    bits: int,
    evaluate=None,
) -> dict[str, Any]:
    if type(max_leaves) is not int or not 1 <= max_leaves <= 4096:
        raise ValueError('Boundary leaf budget must be in 1..4096')
    triangles = roots(model, proof)
    if len(triangles) > max_leaves:
        raise ValueError('Root boundary already exceeds the leaf budget')
    leaves = {}
    queue: list[tuple] = []

    def add_batch(index, paths, batch):
        center, radius, _ = triangles[index]
        bounds = (
            [
                leaf_bound(model, proof, checked, center, radius, triangle, bits)
                for triangle in batch
            ]
            if evaluate is None
            else evaluate(center, radius, batch, bits)
        )
        if len(bounds) != len(batch):
            raise ValueError('Missing boundary tasks')
        for path, triangle, bound in zip(paths, batch, bounds):
            leaves[index, path] = (triangle, bound)
            if len(path) < 12:
                heappush(queue, (-(bound[0].upper - bound[0].lower), index, path))

    for index, (_, _, triangle) in enumerate(triangles):
        add_batch(index, [''], [triangle])
    next_check = len(leaves)
    while queue and len(leaves) + 3 <= max_leaves:
        if len(leaves) >= next_check:
            if (
                aggregate(model, checked, request, [b for _, b in leaves.values()])[
                    'precision_status'
                ]
                == 'resolved'
            ):
                break
            next_check = max(next_check + 1, next_check * 2)
        _, index, path = heappop(queue)
        triangle, _ = leaves.pop((index, path))
        add_batch(index, [path + str(i) for i in range(4)], children(triangle))
    return {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'power_boundary_volume',
        'arithmetic': 'rational-exact/1',
        'model_sha256': model.digest,
        'topology_certificate': proof,
        'request': request.to_record(),
        'bits': bits,
        'leaves': [{'root': i, 'path': p} for i, p in sorted(leaves)],
    }
