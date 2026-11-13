"""Bounded rational subdivision pilot, not a general topology constructor.

Search may share trusted primitive arithmetic with the verifier. The verifier
reconstructs coverage and recomputes every claimed predicate from the original
model; it does not import or trust this frontier/search implementation.
"""

from typing import Any

from .model import Box, Model, Tetrahedron
from .verify.geometry import cell_is_covered, cell_is_free, split


def _classify(model: Model, cell: Box | Tetrahedron, path: str) -> dict[str, Any]:
    covering_atom = next(
        (a.source_id for a in model.atoms if cell_is_covered(model, cell, a.source_id)),
        None,
    )
    if covering_atom is not None:
        return {'path': path, 'state': 'blocked', 'atom_id': covering_atom}
    return {'path': path, 'state': 'free' if cell_is_free(model, cell) else 'unknown'}


def partition(
    model: Model, *, max_depth: int = 4, max_leaves: int = 4096
) -> dict[str, Any]:
    """Produce a complete bounded partition with exact sufficient predicates.

    Parameters
    ----------
    model : Model
        Fixed nm ball/probe model with an admitted convex domain.
    max_depth, max_leaves : int
        Finite subdivision ceilings. Unfinished work stays in unknown leaves.

    Returns
    -------
    dict
        Unverified certificate; call the separately executable verifier before
        interpreting it as checked evidence. No requested volume precision or
        general component enumeration is implied by this pilot.

    Raises
    ------
    ValueError
        Work limits exceed this pilot's admitted envelope or are invalid.
    """
    if (
        type(max_depth) is not int
        or not 0 <= max_depth <= 24
        or type(max_leaves) is not int
        or not 1 <= max_leaves <= 4096
        or len(model.atoms) > 512
    ):
        raise ValueError('Pilot requires depth 0..24, 1..4096 leaves, <=512 atoms')
    stack = [('', model.domain)]
    leaf_count = 1
    leaves = []
    while stack:
        path, cell = stack.pop()
        leaf = _classify(model, cell, path)
        if leaf['state'] != 'unknown':
            leaves.append(leaf)
        elif len(path) < max_depth:
            children = split(cell)
            if leaf_count + len(children) - 1 <= max_leaves:
                leaf_count += len(children) - 1
                stack.extend((path + str(i), child) for i, child in enumerate(children))
            else:
                leaves.append({'path': path, 'state': 'unknown'})
        else:
            leaves.append({'path': path, 'state': 'unknown'})
    return {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'partition',
        'model_sha256': model.digest,
        'arithmetic': 'rational-exact/1',
        'refinement': {'max_depth': max_depth, 'max_leaves': max_leaves},
        'leaves': sorted(leaves, key=lambda leaf: leaf['path']),
    }
