"""Bounded resumable partition work; independent checking precedes all reuse."""

import copy
from typing import Any

from .contracts import Configuration, _split_budget, kernel_identity, run_identity
from .model import Model, record_digest
from .producer import _classify
from .verify.geometry import split
from .verify.records import (
    make_run_record,
    verify_checkpoint,
    verify_transition,
)


def _advance(model: Model, checkpoint: dict[str, Any], budget: int) -> dict[str, Any]:
    _split_budget(budget)
    cp = copy.deepcopy(checkpoint)
    configuration = Configuration.from_record(cp['configuration'])
    certificate = cp['certificate']
    leaves = {leaf['path']: leaf for leaf in certificate['leaves']}
    performed = 0
    while performed < budget:
        candidates = sorted(
            path
            for path, leaf in leaves.items()
            if leaf['state'] == 'unknown' and len(path) < configuration.max_depth
        )
        if not candidates:
            break
        path = candidates[0]
        cell = model.domain
        for digit in path:
            cell = split(cell)[int(digit)]
        children = split(cell)
        if len(leaves) + len(children) - 1 > configuration.max_leaves:
            break
        del leaves[path]
        for i, child in enumerate(children):
            child_path = path + str(i)
            leaves[child_path] = _classify(model, child, child_path)
        performed += 1
    certificate['leaves'] = [leaves[path] for path in sorted(leaves)]
    cp['frontier'] = [
        path for path in sorted(leaves) if leaves[path]['state'] == 'unknown'
    ]
    cp['total_splits'] += performed
    cp['split_budget'] = budget
    cp['performed_splits'] = performed
    return cp


def start_run(
    model: Model,
    *,
    configuration: Configuration = Configuration(),
    split_budget: int = 32,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Start a checked run with a fixed model/request and bounded work.

    A budget counts splits, each involving at most eight child classifications;
    initial root classification and independent verification are additional
    bounded work. The returned pair is (checkpoint, derived run summary).
    """
    _split_budget(split_budget)
    if len(model.atoms) > 512:
        raise ValueError('Pilot atom ceiling exceeded')
    kernel = kernel_identity()
    seed = {
        'schema': 'topomt.reference-validator.checkpoint/1',
        'model_sha256': model.digest,
        'configuration': configuration.to_record(),
        'kernel': kernel,
        'run_sha256': run_identity(model, configuration, kernel),
        'certificate': {
            'schema': 'topomt.reference-validator.certificate/1',
            'kind': 'partition',
            'model_sha256': model.digest,
            'arithmetic': 'rational-exact/1',
            'refinement': configuration.to_record(),
            'leaves': [_classify(model, model.domain, '')],
        },
        'frontier': [],
        'total_splits': 0,
        'step_index': 0,
        'parent_sha256': None,
        'split_budget': 0,
        'performed_splits': 0,
    }
    checkpoint = _advance(model, seed, split_budget)
    return checkpoint, make_run_record(model, checkpoint)


def resume_run(
    model: Model, checkpoint: object, *, split_budget: int = 32
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Continue unresolved cells only after checking the entire prior state.

    Scientific inputs, fixed depth/leaf ceilings and code/runtime identity stay
    unchanged. Only the work budget of this step can differ. Earlier proofs
    and the original checkpoint are never mutated.
    """
    verify_checkpoint(model, checkpoint)
    assert isinstance(checkpoint, dict)
    child = _advance(model, checkpoint, split_budget)
    child['parent_sha256'] = record_digest(checkpoint)
    child['step_index'] = checkpoint['step_index'] + 1
    run = make_run_record(model, child)
    verify_transition(model, checkpoint, child, run)
    return child, run
