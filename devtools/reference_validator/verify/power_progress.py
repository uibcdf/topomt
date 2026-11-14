"""Check local power-cell progress without a producer or a global-count claim."""

import hashlib
import sys
from pathlib import Path
from typing import Any, Optional

from ..model import Model, _record, record_digest
from ..power_contracts import PowerLimits
from .power_cells import checked_cells


def kernel_identity() -> dict[str, Any]:
    """Bind the executable exact-power workflow and Python runtime by bytes."""
    root = Path(__file__).parents[1]
    names = [
        'model.py',
        'power_contracts.py',
        'power_cells.py',
        'power_runs.py',
        'storage.py',
        'hull_model.py',
        'contracts.py',
        'verify/__init__.py',
        'verify/power_cells.py',
        'verify/power_progress.py',
        'verify/polytope.py',
        'verify/geometry.py',
        'verify/center_hull.py',
    ]
    return {
        'algorithm': 'power-cell-progress/1',
        'python_version': sys.version,
        'files': {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in names
        },
    }


def check_progress(model: Model, progress: object) -> dict[str, Any]:
    """Validate a canonical source-cell prefix; global topology stays unknown.

    Parameters
    ----------
    model : Model
        Frozen exact model.
    progress : object
        Untrusted canonical progress record.

    Returns
    -------
    dict
        Checked local inventory without a global-count claim.

    Raises
    ------
    ValueError
        Invalid model, proof, work envelope or saved state.
    """
    state = _record(
        progress,
        {
            'schema',
            'model_sha256',
            'kernel',
            'limits',
            'cells',
            'remaining_atom_ids',
            'stop_reason',
            'request_sha256',
        },
    )
    if (
        state['schema'] != 'topomt.reference-validator.power-progress/1'
        or state['model_sha256'] != model.digest
        or state['kernel'] != kernel_identity()
        or state['request_sha256']
        != record_digest({k: state[k] for k in ['model_sha256', 'kernel', 'limits']})
    ):
        raise ValueError('Power progress model, schema or kernel changed')
    try:
        limits = PowerLimits(**state['limits'])
    except (TypeError, ValueError) as exc:
        raise ValueError('Invalid power progress work policy') from exc
    cells = checked_cells(model, state['cells'], limits=limits, complete=False)
    owners: list[Optional[int]] = []
    owners.extend(sorted(a.source_id for a in model.atoms))
    if not owners:
        owners = [None]
    remaining = owners[len(cells) :]
    if (
        not isinstance(state['remaining_atom_ids'], list)
        or any(
            v is not None and type(v) is not int for v in state['remaining_atom_ids']
        )
        or state['remaining_atom_ids'] != remaining
        or state['stop_reason'] not in {'cell_budget', 'cancelled', 'cells_complete'}
        or (state['stop_reason'] == 'cells_complete') != (not remaining)
    ):
        raise ValueError('Power progress inventory or stopping state differs')
    return {
        'model_sha256': model.digest,
        'topology_complete': False,
        'n_components': None,
        'completed_cells': len(cells),
        'remaining_atom_ids': remaining,
        'cells_complete': not remaining,
    }
