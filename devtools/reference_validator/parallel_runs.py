"""Resumable bounded source-cell proposals; accepted cells remain exact proofs."""

import json
import os
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional, SupportsIndex

from .model import Model, _record
from .parallel import LocalPolicy, _Pool
from .power_cells import _assemble
from .power_contracts import PowerLimits
from .storage import read_record_with_digest, write_progress_bundle
from .verify import verify
from .verify.parallel_progress import check_progress, kernel_identity, task_identity
from .verify.power_cells import checked_cells


def _write_bundle(directory: Path, state: dict) -> None:
    write_progress_bundle(
        directory, state, schema='topomt.reference-validator.parallel-power-bundle/1'
    )


def load_parallel_power_bundle(directory: Path, model: Model) -> dict[str, Any]:
    """Load exactly hashed bytes and independently recheck every completed task.

    Parameters
    ----------
    directory : Path
        Manifest-last bundle previously saved by an owned session.
    model : Model
        Exact original numerical model.

    Returns
    -------
    dict
        Untrusted proof data whose geometry was independently checked on loading.

    Raises
    ------
    ValueError
        Torn/altered storage, different kernel/model or invalid local geometry.
    """
    try:
        manifest, _ = read_record_with_digest(directory / 'MANIFEST.json')
        manifest = _record(manifest, {'schema', 'progress_sha256'})
        state, digest = read_record_with_digest(directory / 'progress.json')
        if (
            manifest['schema'] != 'topomt.reference-validator.parallel-power-bundle/1'
            or manifest['progress_sha256'] != digest
        ):
            raise ValueError('Parallel bundle manifest or digest differs')
        check_progress(model, state)
        return state
    except OSError as exc:
        raise ValueError('Incomplete parallel work bundle') from exc


class ParallelPowerSession:
    """Own individually checked source cells, regardless of completion order.

    Parameters
    ----------
    model : Model
        Immutable complete all-atom Model.
    progress : object or None
        Untrusted saved work; every retained cell is independently reconstructed.

    Raises
    ------
    ValueError
        Changed model/kernel or invalid prior task/geometry.
    """

    def __init__(self, model: Model, *, progress: object = None) -> None:
        self._model = model
        self._pid = os.getpid()
        self._kernel = kernel_identity()
        state = (
            {
                'schema': 'topomt.reference-validator.parallel-power-progress/1',
                'model_sha256': model.digest,
                'kernel': self._kernel,
                'cells': [],
                'stop_reason': 'cell_budget',
            }
            if progress is None
            else deepcopy(progress)
        )
        check_progress(model, state)
        self._payload = json.dumps(state, sort_keys=True)
        self._execution: dict[str, Any] = {}

    def __reduce_ex__(self, protocol: SupportsIndex) -> Any:
        raise TypeError('Save proof data; parallel sessions cannot be serialized')

    @property
    def snapshot(self) -> dict[str, Any]:
        """Detach proof data; PID and source identity protect in-process reuse."""
        if os.getpid() != self._pid or kernel_identity() != self._kernel:
            raise ValueError('Parallel session process or executable changed')
        return json.loads(self._payload)

    @property
    def execution(self) -> dict[str, Any]:
        """Detach the last execution receipt, separately from scientific proof."""
        return deepcopy(self._execution)

    def advance(
        self,
        *,
        cell_budget: int = 1,
        policy: LocalPolicy = LocalPolicy(),
        stop: Optional[Callable[[], bool]] = None,
        checkpoint_root: Optional[Path] = None,
    ) -> dict[str, Any]:
        """Check new proposals once and optionally persist each accepted cell.

        Parameters
        ----------
        cell_budget : int
            Maximum new source tasks in 1..128.
        policy : LocalPolicy
            Explicit bounded process/memory/CPU ceilings; one worker by default.
        stop : callable or None
            Cooperative stop checked before each finite worker batch. In-flight
            tasks finish within their limits; no further batch is submitted.
        checkpoint_root : Path or None
            Save exclusive cells_NNNN bundles after each accepted result.

        Returns
        -------
        dict
            Detached checked local inventory, never a global topology answer.

        Raises
        ------
        ValueError, InterruptedError, RuntimeError
            Invalid input/result, pressure or child failure. Accepted work stays
            available in snapshot and prior durable bundles; the error propagates.
        """
        if type(cell_budget) is not int or not 1 <= cell_budget <= 128:
            raise ValueError('Parallel cell budget must be in 1..128')
        self._execution = {}
        state = self.snapshot
        accepted = {r['source_index']: r for r in state['cells']}
        missing = [
            i for i in range(max(1, len(self._model.atoms))) if i not in accepted
        ]
        if not missing:
            return state

        def publish(reason: str) -> None:
            state['cells'] = [accepted[i] for i in sorted(accepted)]
            state['stop_reason'] = (
                'cells_complete'
                if len(accepted) == max(1, len(self._model.atoms))
                else reason
            )
            self._payload = json.dumps(state, sort_keys=True)

        pool = None
        try:
            for start in range(0, min(cell_budget, len(missing)), policy.workers):
                if stop is not None and stop():
                    publish('cancelled')
                    break
                if pool is None:
                    pool = _Pool(self._model, None, None, policy)
                indices = missing[start : min(start + policy.workers, cell_budget)]
                for i, cell in pool.iter_map(
                    [('cell_proposal', i, None) for i in indices]
                ):
                    if i not in indices or i in accepted:
                        raise ValueError(
                            'Worker returned duplicate or foreign source work'
                        )
                    checked_cells(
                        self._model,
                        [cell],
                        limits=PowerLimits(),
                        complete=False,
                        offset=i,
                    )
                    accepted[i] = {
                        'source_index': i,
                        'task_sha256': task_identity(self._model, self._kernel, i),
                        'cell': deepcopy(cell),
                    }
                    publish('cell_budget')
                    if checkpoint_root is not None:
                        self.save(checkpoint_root / f'cells_{len(accepted):04d}')
            else:
                publish('cell_budget')
        except Exception:
            publish('worker_failure')
            raise
        finally:
            if pool is not None:
                pool.close()
                self._execution = pool.receipt()
        return self.snapshot

    def save(self, directory: Path) -> None:
        """Exclusively persist owned checked work; publish the manifest last.

        Parameters
        ----------
        directory : Path
            New bundle directory. Existing content is never overwritten.

        Raises
        ------
        ValueError, FileExistsError
            Changed source/PID, excessive record or occupied destination.
        """
        _write_bundle(directory, self.snapshot)

    def finish(self) -> dict[str, Any]:
        """Assemble all source cells canonically and run the full serial checker.

        Returns
        -------
        dict
            Complete independently verified topology certificate.

        Raises
        ------
        ValueError
            Any task is missing, or final exhaustive checking rejects assembly.
        """
        state = self.snapshot
        if len(state['cells']) != max(1, len(self._model.atoms)):
            raise ValueError('Parallel power construction is incomplete')
        proof = _assemble(self._model, [r['cell'] for r in state['cells']])
        verify(self._model, proof)
        return proof
