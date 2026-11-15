"""Bounded resumable exact source-cell construction with independent checking."""

import hashlib
import json
import os
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional, SupportsIndex

from .model import Atom, Model, _record, record_digest
from .power_cells import _assemble, propose_cell
from .power_contracts import PowerLimits
from .storage import read_record_with_digest
from .verify import verify
from .verify.power_cells import checked_cells
from .verify.power_progress import check_progress, kernel_identity


def _advance(
    model: Model,
    state: dict[str, Any],
    cell_budget: int,
    stop: Optional[Callable[[], bool]],
) -> dict[str, Any]:
    if type(cell_budget) is not int or not 1 <= cell_budget <= 128:
        raise ValueError('Power step requires a cell budget in 1..128')
    result = deepcopy(state)
    limits = PowerLimits(**result['limits'])
    sorted_atoms = sorted(model.atoms, key=lambda a: a.source_id)
    owners: list[Optional[Atom]] = list(sorted_atoms)
    if not owners:
        owners = [None]
    result['stop_reason'] = 'cell_budget'

    def stop_check() -> None:
        if stop is not None and stop():
            raise InterruptedError('Cooperative power-cell stop')

    for atom in owners[len(result['cells']) : len(result['cells']) + cell_budget]:
        try:
            stop_check()
            row = propose_cell(model, atom, limits=limits, stop_check=stop_check)
            # Verify every retained local proof. No saved accepted flag or
            # partial global graph replaces independent source reconstruction.
            checked_cells(
                model,
                [row],
                limits=limits,
                complete=False,
                offset=len(result['cells']),
                stop_check=stop_check,
            )
        except InterruptedError:
            result['stop_reason'] = 'cancelled'
            break
        result['cells'].append(row)
    result['remaining_atom_ids'] = [
        None if a is None else a.source_id for a in owners[len(result['cells']) :]
    ]
    if not result['remaining_atom_ids']:
        result['stop_reason'] = 'cells_complete'
    return result


def start_power_run(
    model: Model,
    *,
    cell_budget: int = 1,
    limits: PowerLimits = PowerLimits(),
    stop: Optional[Callable[[], bool]] = None,
) -> dict[str, Any]:
    """Start exact construction; an unfinished prefix has no global count.

    Parameters
    ----------
    model : Model
        Frozen exact model.
    cell_budget : int
        Maximum new source cells in this step.
    limits : PowerLimits
        Fixed finite mathematical work envelope.
    stop : callable or None
        Cooperative cancellation predicate.

    Returns
    -------
    dict
        Checked local progress with unresolved global topology.

    Raises
    ------
    ValueError
        Invalid model, proof, work envelope or saved state.
    """
    return _advance(model, _initial_state(model, limits), cell_budget, stop)


def _initial_state(model: Model, limits: PowerLimits) -> dict[str, Any]:
    owners: list[Optional[int]] = []
    owners.extend(sorted(a.source_id for a in model.atoms))
    if not owners:
        owners = [None]
    state: dict[str, Any] = {
        'schema': 'topomt.reference-validator.power-progress/1',
        'model_sha256': model.digest,
        'kernel': kernel_identity(),
        'limits': limits.to_record(),
        'cells': [],
        'remaining_atom_ids': owners,
        'stop_reason': 'cell_budget',
    }
    state['request_sha256'] = record_digest(
        {k: state[k] for k in ['model_sha256', 'kernel', 'limits']}
    )
    check_progress(model, state)
    return state


def resume_power_run(
    model: Model,
    progress: object,
    *,
    cell_budget: int = 1,
    stop: Optional[Callable[[], bool]] = None,
) -> dict[str, Any]:
    """Recheck all retained cells and continue only the same executable model.

    Parameters
    ----------
    model : Model
        Original frozen model.
    progress : object
        Source-bound checked prefix record.
    cell_budget : int
        Maximum new source cells.
    stop : callable or None
        Cooperative cancellation predicate.

    Returns
    -------
    dict
        Detached progress preserving earlier cell evidence.

    Raises
    ------
    ValueError
        Invalid model, proof, work envelope or saved state.
    """
    check_progress(model, progress)
    if not isinstance(progress, dict):
        raise ValueError('Power progress must be a record')
    return _advance(model, progress, cell_budget, stop)


def finish_power_run(model: Model, progress: object) -> dict[str, Any]:
    """Assemble and independently verify complete topology, or reject a prefix.

    Parameters
    ----------
    model : Model
        Original exact model.
    progress : object
        Complete source-cell progress.

    Returns
    -------
    dict
        Independently checked complete topology certificate.

    Raises
    ------
    ValueError
        Invalid model, proof, work envelope or saved state.
    """
    checked = check_progress(model, progress)
    if not checked['cells_complete']:
        raise ValueError('Power construction is incomplete')
    if not isinstance(progress, dict):
        raise ValueError('Power progress must be a record')
    proof = _assemble(model, deepcopy(progress['cells']))
    verify(model, proof)
    return proof


def save_power_bundle(directory: Path, model: Model, progress: object) -> None:
    """Save verified progress exclusively; publish its commit manifest last.

    Parameters
    ----------
    directory : Path
        Exclusive new output directory.
    model : Model
        Original exact model.
    progress : object
        Progress to independently check before writing.

    Returns
    -------
    None
        Publish verified progress and then its checksum manifest.

    Raises
    ------
    ValueError
        Invalid model, proof, work envelope or saved state.
    """
    check_progress(model, progress)
    _write_power_bundle(directory, progress)


def _write_power_bundle(directory: Path, progress: object) -> None:
    """Private manifest-last writer; its caller owns actual validation."""
    directory.mkdir(parents=True, exist_ok=False)
    payload = (
        json.dumps(progress, sort_keys=True, indent=2, allow_nan=False) + '\n'
    ).encode()
    if len(payload) > 16 * 1024**2:
        raise ValueError('Power progress exceeds the 16 MiB record envelope')
    with (directory / 'progress.json').open('xb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    manifest = {
        'schema': 'topomt.reference-validator.power-bundle/1',
        'progress_sha256': hashlib.sha256(payload).hexdigest(),
    }
    with (directory / 'MANIFEST.json').open('x') as stream:
        json.dump(manifest, stream)
        stream.flush()
        os.fsync(stream.fileno())


def load_power_bundle(directory: Path, model: Model) -> dict[str, Any]:
    """Reject torn/altered bundles and recheck the precise saved payload.

    Parameters
    ----------
    directory : Path
        Existing complete saved bundle.
    model : Model
        Original exact model.

    Returns
    -------
    dict
        Independently rechecked progress from precisely the hashed bytes.

    Raises
    ------
    ValueError
        Invalid model, proof, work envelope or saved state.
    """
    try:
        manifest, _ = read_record_with_digest(directory / 'MANIFEST.json')
        manifest = _record(manifest, {'schema', 'progress_sha256'})
        state, digest = read_record_with_digest(directory / 'progress.json')
        if (
            manifest['schema'] != 'topomt.reference-validator.power-bundle/1'
            or manifest['progress_sha256'] != digest
        ):
            raise ValueError('Power bundle manifest or digest differs')
        check_progress(model, state)
        return state
    except OSError as exc:
        raise ValueError('Incomplete power bundle') from exc


class PowerSession:
    """Own checked progress within one process, without trusting saved flags.

    Parameters
    ----------
    model : Model
        Immutable original model.
    progress : object or None
        Optional untrusted saved prefix; fully checked on entry.
    limits : PowerLimits
        Finite limits for a new construction; saved limits must match.

    Raises
    ------
    ValueError
        Input, saved prefix or executable identity differs.
    """

    def __init__(
        self,
        model: Model,
        *,
        progress: object = None,
        limits: PowerLimits = PowerLimits(),
    ) -> None:
        self._model = model
        self._pid = os.getpid()
        state = (
            _initial_state(model, limits) if progress is None else deepcopy(progress)
        )
        check_progress(model, state)
        if not isinstance(state, dict):
            raise ValueError('Progress must be a record')
        if state['limits'] != limits.to_record():
            raise ValueError('Session work limits differ')
        self._payload = json.dumps(state, sort_keys=True)
        self._kernel = kernel_identity()

    def __reduce_ex__(self, protocol: SupportsIndex) -> Any:
        raise TypeError('Save proof data; checked sessions cannot be serialized')

    @property
    def snapshot(self) -> dict[str, Any]:
        """Detach proof data; fresh consumers must check this untrusted record."""
        if os.getpid() != self._pid:
            raise ValueError('Power session belongs to another process')
        if kernel_identity() != self._kernel:
            raise ValueError('Power session executable changed')
        return json.loads(self._payload)

    def advance(
        self, *, cell_budget: int = 1, stop: Optional[Callable[[], bool]] = None
    ) -> dict[str, Any]:
        """Check only newly constructed cells and preserve the verified prefix.

        Parameters
        ----------
        cell_budget : int
            Maximum additional cells, in 1..128.
        stop : callable or None
            Cooperative cancellation predicate.

        Returns
        -------
        dict
            Detached progress; an incomplete prefix has no global count.

        Raises
        ------
        ValueError
            Invalid work limit or executable identity changed.
        """
        state = _advance(self._model, self.snapshot, cell_budget, stop)
        self._payload = json.dumps(state, sort_keys=True)
        return self.snapshot

    def save(self, directory: Path) -> None:
        """Save the owned checked prefix without reconstructing unchanged cells.

        Parameters
        ----------
        directory : Path
            Exclusive manifest-last destination. Fresh loading always checks it.

        Raises
        ------
        ValueError, FileExistsError
            Changed kernel, record size excess or occupied destination.
        """
        _write_power_bundle(directory, self.snapshot)

    def finish(self) -> dict[str, Any]:
        """Assemble complete cells and independently check the entire proof.

        Returns
        -------
        dict
            Complete independently verified topology certificate.

        Raises
        ------
        ValueError
            Any source cell is missing or final checking fails.
        """
        state = self.snapshot
        if state['remaining_atom_ids']:
            raise ValueError('Power construction is incomplete')
        proof = _assemble(self._model, state['cells'])
        verify(self._model, proof)
        return proof
