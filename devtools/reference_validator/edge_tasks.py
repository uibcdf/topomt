"""Bounded serial/parallel execution of the independent analytic edge checker."""

import json
import os
from collections.abc import Callable, Iterator
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from typing import Any, Optional, SupportsIndex

from .model import Model
from .parallel import LocalPolicy, _Pool
from .storage import read_progress_bundle, write_progress_bundle
from .verify import _receipt
from .verify._interval import _Interval
from .verify.edge_progress import (
    BUNDLE_SCHEMA,
    WORK_SCHEMA,
    _restore_progress,
    encode_bound,
    kernel_identity,
    prepare_work,
)
from .verify.edge_volume import reduce_bounds, triangle_flux


class EdgeVerificationSession:
    """Independently admit a frontier, then evaluate each signed piece once.

    Parameters
    ----------
    model : Model
        Immutable exact all-atom numerical model in nm.
    certificate : object
        Untrusted symbolic power_edge_volume certificate.
    progress : object or None
        Optional raw saved work. Every stored bound is recomputed on entry.

    Raises
    ------
    ValueError, ArithmeticError
        Invalid model/proof, source mismatch or unproved arithmetic.
    """

    def __init__(
        self, model: Model, certificate: object, *, progress: object = None
    ) -> None:
        self._model = model
        self._pid = os.getpid()
        if progress is None:
            self._plan = prepare_work(model, certificate)
            self._done: dict[int, _Interval] = {}
        else:
            self._plan, self._done = _restore_progress(model, progress)
            if json.dumps(certificate, sort_keys=True) != self._plan.certificate_json:
                raise ValueError('Requested edge certificate differs from saved work')
        if isinstance(progress, dict):
            self._reason = progress['stop_reason']
        elif len(self._done) == len(self._plan.pieces):
            self._reason = 'pieces_complete'
        else:
            self._reason = 'piece_budget'
        self._execution: dict[str, Any] = {}

    def __reduce_ex__(self, protocol: SupportsIndex) -> Any:
        raise TypeError('Save proof data; edge sessions cannot be serialized')

    def _guard(self) -> None:
        if (
            os.getpid() != self._pid
            or json.dumps(kernel_identity(), sort_keys=True) != self._plan.kernel_json
        ):
            raise ValueError('Edge session process or executable changed')

    @classmethod
    def from_bundle(cls, model: Model, directory: Path) -> 'EdgeVerificationSession':
        """Read checksum-bound bytes and independently reconstruct saved work.

        Parameters
        ----------
        model : Model
            Exact original Model.
        directory : Path
            Complete source-bound bundle from save().

        Returns
        -------
        EdgeVerificationSession
            New owned session, with every stored contribution re-evaluated.

        Raises
        ------
        ValueError, ArithmeticError
            Torn/altered data, changed source/model or false saved arithmetic.
        """
        raw = read_progress_bundle(directory, schema=BUNDLE_SCHEMA)
        if not isinstance(raw, dict) or 'certificate' not in raw:
            raise ValueError('Edge progress requires its original certificate')
        return cls(model, raw['certificate'], progress=raw)

    @property
    def snapshot(self) -> dict[str, Any]:
        """Detach untrusted proof data without claiming a partial total volume."""
        self._guard()
        return {
            'schema': WORK_SCHEMA,
            'model_sha256': self._plan.model_sha256,
            'certificate': json.loads(self._plan.certificate_json),
            'kernel': json.loads(self._plan.kernel_json),
            'frontier_sha256': self._plan.frontier_sha256,
            'items': [
                {
                    'piece_index': i,
                    'task_sha256': self._plan.task_ids[i],
                    'bound': encode_bound(self._done[i]),
                }
                for i in sorted(self._done)
            ],
            'stop_reason': self._reason,
        }

    @property
    def execution(self) -> dict[str, Any]:
        """Detach last-step execution metadata separately from scientific output."""
        return deepcopy(self._execution)

    def advance(
        self,
        *,
        piece_budget: int = 32,
        policy: Optional[LocalPolicy] = None,
        stop: Optional[Callable[[], bool]] = None,
    ) -> dict[str, Any]:
        """Execute missing checker tasks under an explicit finite work budget.

        Parameters
        ----------
        piece_budget : int
            Maximum newly evaluated pieces in 1..4096.
        policy : LocalPolicy or None
            None uses direct serial arithmetic. An explicit policy opts into
            bounded local processes; the external command still needs limits.
        stop : callable or None
            Cooperatively stop before the next finite task batch.

        Returns
        -------
        dict
            Detached progress. No partial volume/precision result is supplied.

        Raises
        ------
        ValueError, ArithmeticError, RuntimeError, InterruptedError
            Bad work/input, failed worker, pressure or numerical admission error.
            Completed tasks remain available; failure never implies zero volume.
        """
        self._guard()
        if type(piece_budget) is not int or not 1 <= piece_budget <= 4096:
            raise ValueError('Edge piece budget must be in 1..4096')
        self._execution = {'mode': 'serial', 'worker_count': 0}
        missing = [i for i in range(len(self._plan.pieces)) if i not in self._done][
            :piece_budget
        ]
        workers = 1 if policy is None else policy.workers
        pool = None
        try:
            for start in range(0, len(missing), workers):
                if stop is not None and stop():
                    self._reason = 'cancelled'
                    break
                indices = missing[start : start + workers]
                tasks = [
                    ('analytic_edge', i, (*self._plan.pieces[i][:3], self._plan.bits))
                    for i in indices
                ]
                results: Iterator[tuple[int, _Interval]]
                if policy is None:
                    results = ((i, triangle_flux(*payload)) for _, i, payload in tasks)
                else:
                    if pool is None:
                        pool = _Pool(self._model, None, None, policy)
                    results = pool.iter_map(tasks)
                for i, bound in results:
                    if (
                        type(i) is not int
                        or i not in indices
                        or i in self._done
                        or not isinstance(bound, _Interval)
                        or not isinstance(bound.lower, Fraction)
                        or not isinstance(bound.upper, Fraction)
                    ):
                        raise ValueError('Invalid or duplicate checker task result')
                    self._done[i] = bound
                if any(i not in self._done for i in indices):
                    raise ValueError('Checker batch omitted a required piece')
            else:
                self._reason = 'piece_budget'
        except Exception:
            self._reason = 'failed'
            raise
        finally:
            if pool is not None:
                pool.close()
                self._execution = pool.receipt()
            if len(self._done) == len(self._plan.pieces):
                self._reason = 'pieces_complete'
        return self.snapshot

    def save(self, directory: Path) -> None:
        """Publish an exclusive manifest-last snapshot of owned computed work.

        Parameters
        ----------
        directory : Path
            New destination; existing data is never overwritten.

        Raises
        ------
        ValueError, FileExistsError
            Changed session, excessive serialization or an occupied destination.
        """
        write_progress_bundle(directory, self.snapshot, schema=BUNDLE_SCHEMA)

    def finish(self) -> dict[str, Any]:
        """Reduce all independently evaluated pieces and check every request.

        Returns
        -------
        dict
            Verification receipt with the same mathematical fields as the
            ordinary serial reader; actual checker source identities are retained.

        Raises
        ------
        ValueError
            Missing work or changed session/PID/source. An unmet precision request
            remains explicit even when the complete enclosure is accepted.
        """
        self._guard()
        if len(self._done) != len(self._plan.pieces):
            raise ValueError('Edge integration is incomplete')
        checked = json.loads(self._plan.checked_json)
        cert = json.loads(self._plan.certificate_json)
        if self._plan.exact_json is not None:
            result = json.loads(self._plan.exact_json)
        else:
            result = reduce_bounds(
                self._model,
                checked,
                self._plan.request,
                self._plan.bits,
                [
                    (self._done[i], self._plan.pieces[i][3])
                    for i in range(len(self._plan.pieces))
                ],
            )
        receipt = _receipt(self._model, cert)
        receipt['verifier_files_sha256'].update(
            json.loads(self._plan.kernel_json)['files']
        )
        receipt.update(result)
        return receipt
