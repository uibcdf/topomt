"""Check arbitrary completed source tasks without trusting worker receipts."""

import hashlib
from pathlib import Path
from typing import Any, Optional

from ..model import Model, _record, record_digest
from ..power_contracts import PowerLimits
from .power_cells import checked_cells
from .power_progress import kernel_identity as power_kernel_identity


def kernel_identity() -> dict[str, Any]:
    """Bind the exact construction/checker and additional process workflow."""
    root = Path(__file__).parents[1]
    return {
        'algorithm': 'parallel-power-progress/1',
        'power_kernel': power_kernel_identity(),
        'files': {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in (
                'parallel.py',
                'parallel_runs.py',
                'verify/parallel_progress.py',
            )
        },
    }


def task_identity(model: Model, kernel: dict, index: int) -> str:
    """Bind a canonical source index to all constraints, limits and kernel."""
    owners: list[Optional[int]] = []
    owners.extend(sorted(a.source_id for a in model.atoms))
    if not owners:
        owners = [None]
    return record_digest(
        {
            'model_sha256': model.digest,
            'kernel': kernel,
            'limits': PowerLimits().to_record(),
            'operation': 'source_cell',
            'source_index': index,
            'source_id': owners[index],
        }
    )


def check_progress(model: Model, progress: object) -> dict[str, Any]:
    """Reconstruct every saved cell, including non-prefix completed work.

    Parameters
    ----------
    model : Model
        Exact complete all-atom numerical model.
    progress : object
        Untrusted source-bound partial inventory, never a global result.

    Returns
    -------
    dict
        Checked completed indices and completeness, without a component count.

    Raises
    ------
    ValueError
        Wrong binding, altered/duplicate/missing-owner task or invalid geometry.
    """
    state = _record(
        progress, {'schema', 'model_sha256', 'kernel', 'cells', 'stop_reason'}
    )
    if (
        state['schema'] != 'topomt.reference-validator.parallel-power-progress/1'
        or state['model_sha256'] != model.digest
        or state['kernel'] != kernel_identity()
        or len(model.atoms) > PowerLimits().max_atoms
        or not isinstance(state['cells'], list)
        or len(state['cells']) > max(1, len(model.atoms))
    ):
        raise ValueError('Parallel work model, kernel or inventory differs')
    indices = []
    for item in state['cells']:
        row = _record(item, {'source_index', 'task_sha256', 'cell'})
        i = row['source_index']
        if (
            type(i) is not int
            or not 0 <= i < max(1, len(model.atoms))
            or i in indices
            or row['task_sha256'] != task_identity(model, state['kernel'], i)
        ):
            raise ValueError('Invalid or repeated source-task identity')
        checked_cells(
            model, [row['cell']], limits=PowerLimits(), complete=False, offset=i
        )
        indices.append(i)
    complete = len(indices) == max(1, len(model.atoms))
    if (
        indices != sorted(indices)
        or state['stop_reason']
        not in {'cell_budget', 'cancelled', 'worker_failure', 'cells_complete'}
        or (state['stop_reason'] == 'cells_complete') != complete
    ):
        raise ValueError('Parallel work ordering or stopping state differs')
    return {
        'model_sha256': model.digest,
        'completed_source_indices': indices,
        'cells_complete': complete,
        'topology_complete': False,
        'n_components': None,
    }
