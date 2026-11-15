# Resumable local source-cell construction

Owner [#76](https://github.com/uibcdf/topomt/issues/76), performance stage S6.
This developer route extends the bounded process prototype without changing the
atom/probe model, power partition, complete topology checker or volume method.
It is not a public TopoMT backend. The
[performance plan](reference_validator_performance_plan.md) owns wider admission.

## What is retained and what is proved

`parallel_runs.ParallelPowerSession` owns individually checked source cells.
A source task is identified by the exact Model digest, original atom ID and
canonical source index, complete finite work limits, executable kernel and
operation. Every proposal receives the entire immutable Model and all atomic
constraints. Proximity is not a reason to omit an obstacle.

A worker proposes a cell; the coordinator independently reconstructs that cell
with `checked_cells` before accepting or saving it. Results can arrive in any
order. The saved inventory is sorted by canonical source index and can contain
gaps: a finished task with index 1 is useful even if task 0 fails. Unique task
identities prevent duplicate contributions, stale work and changed-owner reuse.
No contiguous-prefix assumption turns a missing cell into an empty cell.

A partial inventory has **no global component count**. The independent
`verify.parallel_progress.check_progress` validates every retained local cell
and reports only the source inventory. Only `finish()` assembles all cells in
canonical order and runs the existing complete serial topology checker. Its
output is an ordinary portable `power_cell_topology` certificate, not a new
scientific definition or a worker assertion that the calculation succeeded.

## Failure, interruption and storage

The pool submits at most the explicit worker count at once. A failed child does
not erase other successful results from its finite batch: they are yielded,
checked and can be saved before the failure propagates. No subsequent batch is
submitted after a child failure. An invalid or foreign result is rejected.
Cooperative cancellation is checked between batches; in-flight tasks finish
within their resource envelope. A hard process/host failure can still lose work
that has not reached a durable checkpoint.

With `checkpoint_root`, each accepted cell gets a new exclusive `cells_NNNN`
bundle. The data file is flushed/fsynced before its manifest is published.
Incomplete, changed, duplicate-key, rehashed-but-geometrically-invalid and
occupied bundles cannot be loaded as successful work. An existing directory is
never overwritten. Frequent full snapshots incur serialization and fsync cost;
measure this cost before choosing a longer checkpoint interval or another
storage design under S1/S2.

Owned sessions are PID-bound, reject serialization and check their executable
identity. Their snapshots are detached proof data, not transferable trusted
contexts. `load_parallel_power_bundle` checks exactly the bytes named by the
manifest and independently reconstructs every saved task. A fresh session
checks raw imported state again; no caller-supplied accepted flag is consumed.
Changing Model, atom/frame/domain, executable or limits rejects resume. Use the
retained source snapshot to replay an old source-bound checkpoint; the final
portable topology proof retains the ordinary independent-reader contract.

## Developer workflow

The numerical Model is the same exact nm Model used by the serial reference.
The following is a developer example; the surrounding command must impose
finite process-group CPU/wall/address-space limits and explicit CPU affinity.
These calls do not reserve shared-host resources.

```python
from pathlib import Path
from devtools.reference_validator.parallel import LocalPolicy
from devtools.reference_validator.parallel_runs import (
    ParallelPowerSession, load_parallel_power_bundle,
)

session = ParallelPowerSession(model)
partial = session.advance(
    cell_budget=2,
    policy=LocalPolicy(workers=2),
    checkpoint_root=Path('new_checkpoints'),
)
# A later process loads the same Model and exact executable source.
progress = load_parallel_power_bundle(Path('new_checkpoints/cells_0002'), model)
resumed = ParallelPowerSession(model, progress=progress)
while len(resumed.snapshot['cells']) < max(1, len(model.atoms)):
    state = resumed.advance(cell_budget=4, policy=LocalPolicy(workers=1))
    resumed.save(Path('resumed_checkpoints') / f'cells_{len(state["cells"]):04d}')
certificate = resumed.finish()
```

Use the independent progress checker for partial data, and the ordinary saved
`verify` command for the final certificate. Both readers work without importing
the producer or scientific floating-point libraries. Empty, singleton and
coincident-source controls preserve their complete source coverage.

## Resources and qualification

The default is one worker. Linux local execution requires external finite CPU,
wall and address-space ceilings and bounded affinity, plus a conservative host
reserve. Worker memory is capped, the finite worker CPU allowance is divided
across the pool, and the parent/tracker/workers are included in the admitted
address-space envelope. Nested pools are rejected before launching children.
A memory-pressure stop is an operational interruption, never a geometric result.
The CPU allowance applies to a pool's lifetime, not separately to each task.
For longer construction, use small explicit `cell_budget` steps and save between
steps, with an external whole-command deadline. An early unchunked shell attempt
ended with `BrokenProcessPool` near its worker CPU ceiling; the actual child exit
signal was not retained. That failure motivates four-cell pools in the new
larger receiving, rather than raising or removing the child ceiling.
No Slurm allocation, GPU or distributed-machine execution is selected.

An outer batch-launch session also terminated with exit 143 during an initial
dumbbell continuation. Its initiating cause was not established; its detached
child continued and a retry collided with an occupied checkpoint. Exclusive
writes rejected that collision. Task-owned stop markers ended the leftover run
at its next checkpoint. Surviving checkpoints and observations are retained;
an unlinked log tail and an overwritten execution record are unavailable. These
overlapping attempts cannot support a matched timing claim.

The task launcher now forwards termination to its owned command process group.
A separate signal test confirms the command and its descendant cease and the
caller receives a nonzero interruption status, even if the child exits cleanly.
Each later phase uses its own bounded execution session. Fresh isolated dumbbell
directories start from the original two-cell handoff, so the completed timing
scope is matched; failed/unknown development costs are excluded from that table.

The [versioned receiving](../evidence/reference_validator_parallel_resume_v1/README.md)
records actual one/two-worker interruption, fresh-process resume, canonical
assembly/full checking and subsequent producer-free saved reading on three
original 1.4 Å Models: tetrahedron, closed shell and dumbbell. It keeps original
source/input/proof hashes, local/final phase timing, parent/child CPU and sampled
process-group RSS. Unit controls separately inject out-of-order delivery, child
failure, corrupt tasks/bundles, cooperative stop and forbidden nesting.

One-worker and two-worker timings compare the **same checkpoint/resume workflow**,
including final checking and a further saved read. A one-worker spawned workflow
is not the direct serial constructor. Single larger observations do not qualify
repeatable scaling; queue/process/checkpoint and serial-checking cost remain
visible. Four workers, the complete parallel nineteen-profile panel and S7
parallel analytic integration require their own evidence. Earlier nineteen-profile
serial volume precision remains qualified at its retained source; this work does
not rerun or change it, fix native #181/#180/#184/#188, or admit public/installed P6.
