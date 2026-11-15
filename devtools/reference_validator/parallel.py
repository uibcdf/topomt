"""Opt-in bounded local process proposals; final checking remains independent.

This developer route uses spawn and complete numerical Models. It is not a
distributed executor or a public TopoMT backend. The caller must impose a finite
parent address-space limit, affinity and a whole-command wall/CPU deadline.
"""

import multiprocessing
import os
import resource
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .model import Model
from .power_contracts import PowerLimits
from .verify import verify
from .volume_request import VolumeRequest

_state: tuple = ()


@dataclass(frozen=True)
class LocalPolicy:
    """Explicit worker/resource ceilings; no automatic use of machine cores."""

    workers: int = 1
    worker_address_bytes: int = 256 * 1024**2
    worker_cpu_seconds: int = 60

    def __post_init__(self) -> None:
        if type(self.workers) is not int or not 1 <= self.workers <= 4:
            raise ValueError('Local worker count must be in 1..4')
        if (
            type(self.worker_address_bytes) is not int
            or not 128 * 1024**2 <= self.worker_address_bytes <= 512 * 1024**2
        ):
            raise ValueError('Worker address-space cap must be 128..512 MiB')
        if (
            type(self.worker_cpu_seconds) is not int
            or not self.workers <= self.worker_cpu_seconds <= 120
        ):
            raise ValueError('Worker CPU cap must be 1..120 seconds')


def _reserve(policy: LocalPolicy) -> None:
    memory = {
        row.split(':')[0]: int(row.split()[1]) * 1024
        for row in Path('/proc/meminfo').read_text().splitlines()
    }
    parent_cap = resource.getrlimit(resource.RLIMIT_AS)[0]
    if parent_cap == resource.RLIM_INFINITY or parent_cap > 2 * 1024**3:
        raise ValueError('Parallel caller requires a finite address-space cap <=2 GiB')
    parent_cpu = resource.getrlimit(resource.RLIMIT_CPU)[0]
    if (
        parent_cpu == resource.RLIM_INFINITY
        or parent_cpu > 300
        or len(os.sched_getaffinity(0)) > 4
    ):
        raise ValueError(
            'Parallel caller requires finite CPU <=300 seconds and affinity <=4 CPUs'
        )
    # Include parent and spawn resource tracker, which inherits the parent cap.
    envelope = 2 * parent_cap + policy.workers * policy.worker_address_bytes
    if memory['MemAvailable'] - envelope < max(memory['MemTotal'] // 5, 4 * 1024**3):
        raise InterruptedError('Insufficient shared-host memory reserve')
    pressure = Path('/proc/pressure/memory').read_text().splitlines()
    if any(float(row.split()[1].split('=')[1]) > 0.1 for row in pressure):
        raise InterruptedError('Shared-host memory pressure')


def _initialize(
    model: Model,
    topology: object,
    checked: object,
    policy: LocalPolicy,
    cpus: tuple[int, ...],
) -> None:
    global _state
    os.sched_setaffinity(0, set(cpus))
    for limit, requested in [
        (resource.RLIMIT_AS, policy.worker_address_bytes),
        (resource.RLIMIT_CPU, policy.worker_cpu_seconds // policy.workers),
    ]:
        soft, hard = resource.getrlimit(limit)
        actual_hard = (
            requested if hard == resource.RLIM_INFINITY else min(requested, hard)
        )
        actual_soft = (
            actual_hard if soft == resource.RLIM_INFINITY else min(actual_hard, soft)
        )
        resource.setrlimit(limit, (actual_soft, actual_hard))
    for key in (
        'OMP_NUM_THREADS',
        'OPENBLAS_NUM_THREADS',
        'MKL_NUM_THREADS',
        'NUMEXPR_NUM_THREADS',
    ):
        os.environ[key] = '1'
    _state = (model, topology, checked)


def _task(task: tuple) -> tuple:
    model, proof, checked = _state
    kind, identity, payload = task
    result: Any
    if kind == 'cell':
        from .power_cells import propose_cell
        from .verify.power_cells import checked_cells

        atoms = sorted(model.atoms, key=lambda a: a.source_id) or [None]
        row = propose_cell(model, atoms[identity])
        checked_cells(
            model, [row], limits=PowerLimits(), complete=False, offset=identity
        )
        result = row
    elif kind == 'face':
        from .verify.boundary_volume import leaf_bound

        center, radius, triangle, bits = payload
        result = leaf_bound(model, proof, checked, center, radius, triangle, bits)
    else:
        raise ValueError('Unknown exact source task')
    return (
        identity,
        result,
        {
            'pid': os.getpid(),
            'address_space_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
            'cpu_seconds': time.process_time(),
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    )


class _Pool:
    def __init__(
        self, model: Model, proof: object, checked: object, policy: LocalPolicy
    ):
        _reserve(policy)
        self.policy = policy
        self.records: dict[int, dict] = {}
        self.cpus = tuple(sorted(os.sched_getaffinity(0))[: policy.workers])
        self.executor = ProcessPoolExecutor(
            max_workers=policy.workers,
            mp_context=multiprocessing.get_context('spawn'),
            initializer=_initialize,
            initargs=(model, proof, checked, policy, self.cpus),
        )

    def map(self, tasks: list[tuple]) -> list:
        results = []
        for start in range(0, len(tasks), self.policy.workers):
            _reserve(self.policy)
            batch = tasks[start : start + self.policy.workers]
            futures = [self.executor.submit(_task, task) for task in batch]
            for task, future in zip(batch, futures):
                while True:
                    try:
                        identity, result, record = future.result(timeout=5)
                        break
                    except TimeoutError:
                        if future.done():
                            raise
                        _reserve(self.policy)
                if identity != task[1]:
                    raise ValueError('Worker task identity differs')
                self.records[record['pid']] = record
                results.append(result)
        return results

    def close(self) -> None:
        self.executor.shutdown(wait=True, cancel_futures=True)

    def receipt(self) -> dict[str, Any]:
        parent = resource.getrlimit(resource.RLIMIT_AS)[0]
        return {
            'worker_count': self.policy.workers,
            'worker_records': list(self.records.values()),
            'worker_affinity': list(self.cpus),
            'parent_address_space_bytes': parent,
            'aggregate_address_space_bound_bytes': 2 * parent
            + self.policy.workers * self.policy.worker_address_bytes,
            'aggregate_bound_includes_spawn_tracker': True,
            'aggregate_rss_peak_status': 'not_measured',
            'worker_cpu_scope': 'pool budget divided across workers; external command deadline also required',
        }


def parallel_power_topology(
    model: Model, *, policy: LocalPolicy = LocalPolicy()
) -> tuple[dict, dict]:
    """Construct canonical source cells locally and independently check assembly.

    Parameters
    ----------
    model : Model
        Complete exact all-atom numerical model.
    policy : LocalPolicy
        Explicit bounded workers and child memory/CPU ceilings.

    Returns
    -------
    tuple
        Complete checked certificate and execution resource receipt.

    Raises
    ------
    ValueError, InterruptedError
        Invalid resources/tasks, host pressure or final proof rejection.
        Child failures propagate without a geometric result.
    """
    from .power_cells import _assemble

    if len(model.atoms) > PowerLimits().max_atoms:
        raise ValueError('Parallel model exceeds original source-cell envelope')
    pool = _Pool(model, None, None, policy)
    try:
        cells = pool.map([('cell', i, None) for i in range(max(1, len(model.atoms)))])
    finally:
        pool.close()
    proof = _assemble(model, cells)
    verify(model, proof)
    return proof, pool.receipt()


def parallel_boundary_volume(
    model: Model,
    topology: object,
    request: VolumeRequest,
    *,
    max_leaves: int = 4096,
    policy: LocalPolicy = LocalPolicy(),
) -> tuple[dict, dict]:
    """Propose the same deterministic face partition with bounded local workers.

    Parameters
    ----------
    model, topology : Model, object
        Exact model and complete untrusted power-cell proof.
    request : VolumeRequest
        Unchanged total/per-region precision requirements.
    max_leaves : int
        Finite face-partition envelope, at most 4096.
    policy : LocalPolicy
        Explicit worker resource ceilings.

    Returns
    -------
    tuple
        Independently checked boundary certificate and execution receipt.

    Raises
    ------
    ValueError, InterruptedError
        Invalid proof, work/resources or host pressure; failures give no answer.
    """
    from .boundary_volume import _construct

    topology = deepcopy(topology)
    checked = verify(model, topology)
    if checked['kind'] != 'power_cell_topology':
        raise ValueError('Complete power-cell proof required')
    if not isinstance(topology, dict):
        raise ValueError('Topology must be a record')
    pool = _Pool(model, topology, checked, policy)
    try:

        def evaluate(center, radius, triangles, bits):
            return pool.map(
                [
                    ('face', i, (center, radius, triangle, bits))
                    for i, triangle in enumerate(triangles)
                ]
            )

        proof = _construct(model, topology, checked, request, max_leaves, 64, evaluate)
    finally:
        pool.close()
    verify(model, proof)
    return proof, pool.receipt()
