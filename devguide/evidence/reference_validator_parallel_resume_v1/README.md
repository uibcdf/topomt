# Resumable source-cell receiving

Owner [TopoMT #76](https://github.com/uibcdf/topomt/issues/76), S6 continuation.
Implementation and trust contract:
[resumable local source work](../../DFND/reference_validator_parallel_resume.md).
The source snapshot contains 49 exact developer modules; no native DFND operator,
original atom/probe input, public promotion policy or volume definition changes.

## Selected receiving

`plan_final.json` names six completed configurations: original 1.4 Å tetrahedron,
closed shell and dumbbell, each with explicitly one and two local workers.
Each workflow saves checked work after two source cells, cooperatively stops,
loads it in a new process, constructs all remaining cells and checks the complete
canonical proof. A further fresh process verifies that saved proof with producer
and scientific imports blocked. Each final mathematical certificate equals the
original saved serial certificate. Partial work carries no global component count.

`receiving_index.json` binds Models, protocols, sources, phase receipts and
archive paths. `receiving.zip` retains every working JSON byte, including all
intermediate checkpoints and failed-pilot partials, at its original evidence-
relative path. The archive also contains the source and exact Models. Working
receiving trees are removed only after their archived bytes are verified.
`capsule_manifest.json` binds every member and archive bytes; integrity does not
prove the mathematics or authenticate an original producer.

## Timing and resources

The generated [table](table.md) reports the same interrupted/resumed workflow
with one/two-worker pools, full final checking and an additional independent saved
read. Bounded elapsed includes process startup. Parent and waited-child CPU have
separate measured phases; their sums are reconciled with floating-time rounding
allowance. Counters are operational floating-second measurements, not certified
scientific quantities. A spawned one-worker workflow is not the direct serial
constructor. `comparisons.json` gives scoped T1/T2 and T1/(2T2); one observation
per larger configuration cannot establish repeatable or general scaling.

All completed comparison phases run sequentially; only explicit pools use two logical CPUs.
Each parent has a 2 GiB address-space cap and finite 300/330 CPU-second ceilings.
Workers retain 256 MiB caps and a total pool allowance of 120 CPU seconds divided
across its workers. Larger continuation uses four-cell pools and saves between
pools, with a finite 720-second external phase deadline. Parent/tracker/workers
are included in the declared pool address-space envelope. No resources are
reserved by observing availability, and no Slurm/GPU/multi-machine run is used.

Host reserve and process-group RSS are sampled every five seconds. All retained
successful samples are safe. Group RSS is a sampled sum, can count shared pages
twice and can miss short peaks; tiny tetrahedron runs are too short to resolve
pool memory this way. Kernel peak RSS for individual waited processes is recorded
separately. The outer monitoring launcher is outside that sampled child group.

## Operational failures and their disposition

- The first launch lacks the checkout import path and fails before evaluating
  geometry. Its raw error and corrected explicit launch context are retained.
- An unchunked closed-shell continuation ends with `BrokenProcessPool` near its
  declared worker CPU ceiling. No actual child exit signal was captured, so the
  cause is not asserted as an independently proved signal diagnosis. Its partial
  work remains readable. Four-cell pools retain the ceilings and complete the
  new receiving without silently raising or removing a worker limit.
- An outer batch-launch session returns 143 during dumbbell continuation while
  its detached child continues. A retry collides with an occupied checkpoint;
  exclusive writes reject it. Task-owned stop markers halt the leftover execution
  at its next checkpoint. The outer termination's initiating cause is unknown.
  Surviving checkpoint/log bytes and observations are retained under `attempts/`
  and the old dumbbell receiving tree. An unlinked old log tail and an overwritten
  execution record are unavailable; their event-to-record attribution is partial.
  None of those overlapping timings is used as matched performance evidence.
- The task launcher now forwards SIGTERM/SIGINT to its owned command process
  group and reports interruption to its caller even if a child handles its signal
  with exit zero. `launcher_signal_check.json` confirms both the command and its
  descendant cease. Each subsequent phase uses its own bounded execution session
  and exclusive new dumbbell directories. This test is of the local task launcher,
  not admission of a production infrastructure/execution API.

The completed timing table excludes failed/interrupted attempts. Unknown costs
are not invented or included in an alleged total cost of all development work.

## Qualification and remaining work

The unit controls cover out-of-order non-prefix work, actual child failure,
cooperative stop, missing/duplicate/foreign task identities, corrupt/rehashed/torn
storage, changed bindings, process/serialization constraints, empty/coincident
sources and producer-free partial reading. The final selected regression run passes 115 tests. Repository Ruff/format,
49-module local mypy, report-index/offline comparative checks and strict
one-CPU Sphinx pass. Resource receipts and `source_qualification.json`
record the boundaries; full suite/platform/public gates remain separate.

S6 is qualified at these controlled and three-original-Model scopes. Full parallel
nineteen-profile/four-worker admission, S7 analytic integration, remaining S1/S3/S5
work and broader S8/P6/P7 remain open. Original nineteen-profile serial volume
precision keeps its independent source/evidence scope. Native #181/#180/#184/#188,
canonical native receiving #76/#60 and public/installed/platform #16 are unchanged.
No new geometry, protein or original-provider phase is selected.

The separate `one_cell_cost_profile.json` isolates an original cold closed-shell
proposal, whose checked cell equals the saved original. Its profiled 14.729
seconds include 14.203 in clipping, 129 edge reconstructions and 315,540 exact
plane evaluations. Inclusive call times are not added. Profiler overhead prevents
using this as an uninstrumented speed denominator. #76/S3/S5 owns measured exact
incidence/invariant reuse before a compiled-kernel decision; no such optimization
is claimed delivered here.
