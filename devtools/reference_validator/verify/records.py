"""Independent checkpoint, run-summary and refinement-lineage verification."""

from typing import Any

from ..contracts import (
    Configuration,
    _digest_is,
    _split_budget,
    _stop_reason,
    kernel_identity,
    run_identity,
)
from ..model import Box, Model, _record, decode_scalar, record_digest
from . import verify


def verify_checkpoint(model: Model, checkpoint: object) -> dict[str, Any]:
    """Check a complete saved state before permitting same-kernel resumption.

    The frontier must contain every unknown leaf exactly once, including cells
    at operational ceilings. Limits can stop work but never erase uncertainty.
    No producer or run-orchestration module is imported here.
    """
    cp = _record(
        checkpoint,
        {
            'schema',
            'model_sha256',
            'run_sha256',
            'kernel',
            'configuration',
            'certificate',
            'frontier',
            'total_splits',
            'step_index',
            'parent_sha256',
            'split_budget',
            'performed_splits',
        },
    )
    if (
        cp['schema'] != 'topomt.reference-validator.checkpoint/1'
        or cp['model_sha256'] != model.digest
    ):
        raise ValueError('Checkpoint schema or model differs')
    configuration = Configuration.from_record(cp['configuration'])
    if cp['kernel'] != kernel_identity():
        raise ValueError('Checkpoint kernel/runtime changed; start a new run')
    if cp['run_sha256'] != run_identity(model, configuration, cp['kernel']):
        raise ValueError('Checkpoint request identity differs')
    certificate = cp['certificate']
    result = verify(model, certificate)
    if (
        certificate['kind'] != 'partition'
        or certificate['refinement'] != configuration.to_record()
    ):
        raise ValueError('Checkpoint must retain its fixed partition request')
    frontier = sorted(
        leaf['path'] for leaf in certificate['leaves'] if leaf['state'] == 'unknown'
    )
    if cp['frontier'] != frontier:
        raise ValueError('Checkpoint frontier omits, duplicates or invents work')
    arity = 8 if isinstance(model.domain, Box) else 2
    actual_splits = (len(certificate['leaves']) - 1) // (arity - 1)
    if type(cp['total_splits']) is not int or cp['total_splits'] != actual_splits:
        raise ValueError('Checkpoint split count differs from its complete tree')
    _split_budget(cp['split_budget'])
    if (
        type(cp['performed_splits']) is not int
        or not 0 <= cp['performed_splits'] <= min(actual_splits, cp['split_budget'])
        or type(cp['step_index']) is not int
        or cp['step_index'] < 0
    ):
        raise ValueError('Invalid checkpoint work counters')
    if cp['step_index'] == 0:
        if cp['parent_sha256'] is not None or cp['performed_splits'] != actual_splits:
            raise ValueError('An initial checkpoint has no parent or prior work')
    elif not _digest_is(cp['parent_sha256']):
        raise ValueError('A resumed checkpoint needs a valid parent identity')
    return {
        **result,
        'checkpoint_sha256': record_digest(cp),
        'run_sha256': cp['run_sha256'],
        'frontier_count': len(frontier),
        'total_splits': actual_splits,
        'stop_reason': _stop_reason(model, certificate, configuration),
    }


def make_run_record(model: Model, checkpoint: object) -> dict[str, Any]:
    """Derive a checked summary; no supplied count or error claim is trusted."""
    checked = verify_checkpoint(model, checkpoint)
    return {
        'schema': 'topomt.reference-validator.run/1',
        'run_sha256': checked['run_sha256'],
        'checkpoint_sha256': checked['checkpoint_sha256'],
        'verification': checked,
    }


def verify_run(model: Model, run: object, checkpoint: object) -> dict[str, Any]:
    """Recompute the complete saved summary from its mathematical certificate.

    Standalone checking does not authenticate an unavailable parent history;
    use verify_transition with that parent to check the refinement relationship.
    """
    expected = make_run_record(model, checkpoint)
    if run != expected:
        raise ValueError('Run record differs from its checked checkpoint')
    return {
        **expected['verification'],
        'run_record_sha256': record_digest(expected),
        'lineage_status': 'not_checked',
    }


def verify_transition(
    model: Model, parent: object, child: object, run: object
) -> dict[str, Any]:
    """Prove source identity, retained facts and nested bounds across a step."""
    before = verify_checkpoint(model, parent)
    after = verify_run(model, run, child)
    # Both mappings are already schema checked above.
    assert isinstance(parent, dict) and isinstance(child, dict)
    if (
        before['run_sha256'] != after['run_sha256']
        or child['parent_sha256'] != record_digest(parent)
        or child['step_index'] != parent['step_index'] + 1
        or child['total_splits'] - parent['total_splits'] != child['performed_splits']
    ):
        raise ValueError('Checkpoint lineage or work delta differs')
    old = {leaf['path']: leaf for leaf in parent['certificate']['leaves']}
    new = {leaf['path']: leaf for leaf in child['certificate']['leaves']}
    for path, leaf in old.items():
        if leaf['state'] != 'unknown' and new.get(path) != leaf:
            raise ValueError('Refinement discarded a previously proved cell')
    for path in new:
        if not any(path[:i] in old for i in range(len(path) + 1)):
            raise ValueError('Checkpoint merged cells instead of refining them')
    if decode_scalar(after['volume_lower']) < decode_scalar(
        before['volume_lower']
    ) or decode_scalar(after['volume_upper']) > decode_scalar(before['volume_upper']):
        raise ValueError('Refinement worsened the certified volume enclosure')
    return {**after, 'lineage_status': 'resolved', 'volume_bounds_nested': True}
