# Reference validator: performance implementation plan

Date: 2026-11-15. Owner: [TopoMT #76](https://github.com/uibcdf/topomt/issues/76).
First native consumer: [#181](https://github.com/uibcdf/topomt/issues/181).
Reviewed repository: `c972b13`; executable baseline:
`86b95d371256c1d54500da9c8a05f6ee642a37ac`.

**Status: partial implementation; the eight-stage plan remains open.**
The goal is to reduce the time to a checked answer at unchanged scientific
guarantees, first on one CPU and later with explicitly bounded local processes.
Correctness, complete topology and certified error retain priority over speed.
The [A--F workplan](reference_validator_improvement_workplan.md) owns the active
scientific sequence; this document supplies its detailed performance follow-up.

### Current serial precision receiving — 2026-11-15

S4 is **delivered for the selected nineteen original profiles and controls**.
The [analytic edge route](reference_validator_edge_integration.md) and
[receiving](../evidence/reference_validator_edge_volume_v1/README.md) meet every
unchanged k=24 total/per-region request, including sixteen positive regions.
The sixteen clipped-boundary ladder and nine region controls also pass. Original
workers run sequentially on one CPU (1354.837 wall seconds; 43.73 MiB peak RSS).
Fresh checking needs no producer or scientific dependency.

A measured Fraction-atan hotspot led to certified integer dyadic arithmetic;
matched 32-piece primitive medians are 2.912799 versus 0.299421 seconds. This is
not a full-analysis speedup over the retained incomplete dumbbell attempt.
Declarative proposals avoid evaluating the full integral twice while earning
no completion credit. Optional Rust remains deferred pending an additional
justified hotspot and its independent qualification. S1/S3/S5/S6/S7/S8 retain
unexecuted parts. The former unmet-precision statements below describe the
earlier range-based method; parallel prototypes do not qualify this analytic
route. The current scientific continuation is common canonical native receiving
under #76/#60 and #181, with broader public/installed gates separate.

### Earlier range-based implementation receiving — 2026-11-15

The [versioned evidence](../evidence/reference_validator_performance_v1/README.md)
records matched measurements, actual checked-state reuse, incremental box-volume
accounting, a [signed face-flux construction](reference_validator_face_flux.md)
and bounded local-process prototypes. S2 is delivered for the tested in-process
query/session receiving scope. S1/S3/S4/S6/S7/S8 remain partial. S5's bounded
denominator reduction is implemented; optional Rust remains deferred while
serial precision and a justified compiled hotspot are unqualified.

The original tetrahedron at 1.4 Å still misses k=24 with 4095 face triangles.
Two-process certificates agree with serial results, but process overhead makes
this small case slower. Neither a generic multicore speedup nor the original
positive-volume precision gate is passed. Source prototypes do not override
the serial scientific prerequisites for complete P7 admission.

## Historical starting evidence and preserved scope

All nineteen original profiles have complete checked topology and conservative
total/per-region volume bounds. Six exact-zero profiles pass their k=24 request;
thirteen nonempty profiles, containing sixteen regions, still miss it. Sixteen
restricted clipped-cube controls pass k=8/16/24/32. Their formula does not yet
integrate the general original power-cell geometry. See the
[source checkpoint](reference_validator_checkpoint.md) and
[BenchLab report](../../docs/content/benchlab/synthetic/reference_validator_report.md).

The saved [dumbbell profile](../evidence/reference_validator_remaining_topology_v1/dumbbell/profile_0/receiving/dumbbell_profile_0/phases.json)
spends 56.197 seconds in verification and 56.849 in anchor queries.
`query_anchors` independently verifies the same topology again. Power-cell
checkpoint construction also checks individual cells and repeatedly rechecks
the retained prefix. These are concrete reuse opportunities; neither timing
establishes the saving obtainable after a change. Recorded construction phases
include checking and checkpoint work and cannot be treated as pure geometry cost.

The current `_vertices` implementation already uses integer Cramer numerators,
exact inequality rejection and delayed rational construction. A compiled
backend must target the measured remaining cost of that integer pipeline.

This plan preserves the six selected synthetic systems, all original Models,
requests, artifacts and current admission limits. It selects no new protein,
geometry, external engine, public API or distributed-machine execution.
Profiling and bounded serial improvements may precede the remaining precision
construction. P7 scaling and compiled-backend qualification follow the serial
scientific gates in the A--F workplan. The first implementation tranche has delivered bounded S1/S2/S3 receiving;
S4 was the scientific continuation selected at that baseline.

## Guarantees every stage must preserve

- Preserve exact centers, radii, probe, units, atom/frame mappings, declared
  finite domain and contact convention. Near-equal inputs remain distinct.
- Retain every relevant atomic constraint. A skipped constraint needs a
  conservative mathematical bound or a checked redundancy argument.
- Recover the complete region and boundary-patch inventory and incidence.
  An unfinished cell collection has no global component count.
- Count each integration contribution once, including coincident cells and
  uncertainty shared by regions. Keep all original absolute and relative
  requirements for both total and individual region volumes. Tiny positive
  regions and unresolved contact decisions receive no size cutoff.
- Keep an independently runnable checker which reconstructs the accepted
  geometry/accounting. Producer caches and accelerators do not become proofs.
  A saved digest identifies bytes; it does not certify their geometry.
- Keep valid bounds, topology completeness, requested precision, cancellation
  and resource exhaustion as separate outcomes. Preserve readable old proofs.

## Implementation sequence

Each stage uses a focused test-first change and an additive measurement record.
Only an executed acceptance gate changes its status. Optional work can be
deferred with its measured reason and revisit condition in #76.

| Stage | Deliverable | Depends on | Current disposition |
| --- | --- | --- | --- |
| S1 | Reproducible cost breakdown and equivalence protocol | Existing serial baseline | Partial: matched phase/call pilot; full accounting pending |
| S2 | Checked immutable context and incremental progress reuse | S1 | Delivered for tested in-process query/session scope |
| S3 | Exact invariant reuse and incremental volume accounting | S1/S2 | Partial: volume ledger delivered; wider invariants pending |
| S4 | General certified boundary integration and precision receiving | A--F D/E; S1 measurements | Delivered: all 19 original total/per-region requests and selected controls; wider admission separate |
| S5 | Measured exact geometry acceleration, optionally Rust | S1--S4 serial gates | Partial: denominator control and measured integer dyadic atan; optional Rust deferred |
| S6 | Bounded parallel power-cell construction/checking | Qualified serial route; S1/S2 | Prototype; full fault/resume/panel qualification pending |
| S7 | Bounded parallel integration with verified ownership | S4/S6 | Earlier range prototype only; analytic-route parallel/failure/resume qualification open |
| S8 | End-to-end qualification, evidence and operating guide | Selected preceding stages | Partial: original serial precision panel delivered; broader optimized/parallel/public receiving open |

### S1 — measure the actual work and freeze comparisons

Extend the existing receiving harness and phase receipts. Separate model/hull
validation, cell proposal, local independent checks, prefix rechecks, global
assembly/checking, saved reading, queries, integration, serialization and fsync.
Record call counts, completed cells/plane triples, leaf evaluations, operand
bit lengths, artifact bytes, CPU and elapsed time, and simultaneous memory use.
Use bounded counters/samples so instrumentation does not create a new bottleneck.
Capture a focused call profile separately from uninstrumented timing runs.

Start with the original tetrahedron and small existing exact controls. Then use
one retained shell and dumbbell as representative larger inputs after estimating
cost. Reuse old receipts for orientation; a performance comparison needs matched
new runs of baseline and candidate with the same Model, observable and request.
Include cold construction, saved checking, queries and same-model resumption.
Run short comparisons three times sequentially; retain individual measurements
and host load. Expand expensive repetitions only when variability warrants it.

Freeze two comparisons: fixed work/partition for cost isolation, and complete
time to the same requested checked answer. Separate profiler overhead, cache
warmth, producer time, final checker time and end-to-end time. A timeout or an
unmet precision target cannot supply a successful speedup denominator.

**Acceptance:** receipts reconcile phase totals and parent/child CPU accounting;
baseline repeatability is described; original proofs pass fresh independent
reading; each proposed optimization names its measured hotspot and test cases.
Begin without rerunning the complete historical panel.

Freeze comparison rules before changing code: compare canonical mathematical
payloads separately from timestamps/source/execution receipts, preserving every
geometry, mapping and scientific field. For the same partition require exact
equality; for a new admitted integration partition require independent proofs,
unchanged requests and compatible certified intervals. Interval overlap alone
does not prove correctness.

### S2 — reuse genuinely checked state within one process

Introduce a private checked context constructed only through real independent
validation. Bind it to detached immutable Model/proof data, request/limits,
schema and checker identity. Reuse its reconstructed topology for a bounded
query batch and subsequent compatible operations. Preserve existing raw-record
entry points: they still validate untrusted input. No caller-supplied flag or
claimed digest can instantiate a checked context.

For in-process construction, reuse checked cells and validate new cells plus
the transition/coverage bookkeeping. Avoid repeatedly reconstructing the same
unchanged prefix during internal advance/save operations. Persist only proof
data and provenance; fresh processes and imported bundles fully validate them.
Retain manifest-last atomic writes, finite work limits and the final exhaustive
independent topology check. Choose checkpoint frequency from measured cost and
recoverable work, preserving cooperative cancellation.

Add failure tests for changed geometry/probe/domain/frame, altered cells,
limits/kernel mismatch, aliased mutable inputs, forged contexts, missing cells,
corrupted checkpoints and interruption/resume. Check actual verification calls
as well as mathematical outputs to demonstrate that reuse reaches the workflow.

**Acceptance:** identical canonical scientific outputs, fresh saved verification
and corruption rejection; repeated checks measurably decrease in the admitted
in-process path. Fresh reading remains independent of the producer/context.

### S3 — avoid rebuilding exact invariants and volume totals

Prepare immutable integer planes, expanded squared radii and other exact
model constants once per compatible context. Reuse bounds and cross products
only where their defining inputs agree. Preserve the existing checked
`reprobe_certificate` route: geometry reuse across probes requires equality of
the complete power inequalities. Unequal radii can change that partition.

In `region_volume._refine`, maintain exact producer-side known-free volume per
region, total unresolved volume, counts and refinement priorities. Replacing
one leaf updates its old contribution and its children once. Check the frozen
precision rule from those totals instead of repeatedly reclassifying every
leaf through `_summarize`. The independent reader still reconstructs the entire
partition and all contributions from the emitted proof.

Test fixed refinement traces, empty/full cases, eight-corner/tiny-region and
asymmetric three-region controls, shared uncertainty, resume and bad ledgers.
The producer's stopping decision must agree with the independent checker.

**Acceptance:** unchanged exact results for the same partition, unchanged
unresolved outcomes at the same budget, accepted saved proofs and measured
reduction in invariant construction/leaf evaluations. Interval arithmetic
continues to round outward wherever nonrational quantities enter.

### S4 — reach precision with a better integration construction

Complete the existing A--F D/E task before treating faster refinement as a
solution to the original precision gap. Follow the
[region-volume construction](reference_validator_region_volume_construction.md)
and [restricted boundary derivation](reference_validator_boundary_precision.md).
Start on original `regular_tetrahedron` at 1.4 Å, derive complete oriented
clipped-cell boundary pieces and their region assignment, and bound all
integration error. Cover overlaps, coincident ownership, sphere/face cuts,
degenerate contacts and cancellation in tiny positive volumes.

Prototype and independently check this route on existing analytic controls;
then receive the original positive families. Retain the conservative box route
as a separately identified fallback and cross-check. Reuse a derivation only
within its proved admission scope. Report valid enclosure and attained
precision independently at every attempted budget.

**Acceptance:** checked total/per-region requests pass at the selected scope,
including the original k=24 requirement and tiny/asymmetric controls. Full
original-panel precision stays open until every required profile passes. Compare
time-to-precision only for equal Models/requests with successful final checking.
Failure retains an explicit scientific next task rather than selecting larger
parallel grids automatically.

### S5 — accelerate measured exact geometry kernels

Use S1 measurements after serial reuse and S4. Candidate hotspots are exhaustive
supporting-plane intersections, exact inequality tests and all-atom local bounds.
Try a bounded exact algorithmic improvement first where justified. Spatial
pruning or active-constraint reduction needs a coverage/redundancy argument;
nearest-neighbor heuristics alone cannot remove source constraints.

If interpreter overhead remains material, prototype one producer kernel in
Rust with arbitrary-precision integers/rationals, canonical encodings and
checked conversions. Keep the existing Python implementation and standalone
checker. An optional approximate filter needs proved error bounds and exact
fallback for every undecided or degenerate case; replacing predicates with
ordinary floating point does not meet this stage.

Differentially test exact outputs, large operands, degeneracies, contacts and
permuted inputs. Record build/compiler/dependency identity, conversion cost and
build/platform availability. An accelerator remains explicitly optional; its
absence or failure cannot silently change the scientific method.

**Acceptance:** independent Python verification accepts the certificates and
measured end-to-end benefit justifies the maintenance/dependency cost. Otherwise
defer this stage with evidence and continue using the qualified Python route.

### S6 — distribute power cells across bounded local processes

Keep one process as the default. Add an explicit worker ceiling and finite task
queue to the developer runner. For the current GIL-enabled Python, start with
processes for CPU-bound Python work. First qualify two workers; consider four
only after measuring resources and benefit. A worker gets the complete immutable
Model/constraints and one canonical source-cell task, not a truncated local
atom neighborhood. Never create a pool inside another worker.

Use stable task identities bound to Model, kernel, limits and source owner.
Workers produce local certificates; a separate checking pass can distribute
independent local reconstruction. The coordinator verifies completeness,
uniqueness and canonical ordering before assembling the global graph. Retain
the existing full serial checker on the final emitted proof. Measure this
final cost before proposing a parallel global-checking design.

Aggregate results independently of completion order. Checkpoint only accepted
cell inventory; preserve valid completed cells on cooperative stop. Missing,
duplicated, conflicting, stale or failed tasks cannot imply empty cells or a
complete result. Test out-of-order completion, child failure, malformed results,
missing tasks, cancellation and process-spawn/fresh-import behavior.

**Acceptance:** one/two-worker canonical mathematical proofs agree with serial
construction; each passes fresh final checking. Resource accounting includes
coordinator, every worker, queues and serialization. Four-worker receiving is
an additional measured gate, not an automatic setting.

### S7 — distribute integration with an explicit partition

Start with a fixed canonical frontier of disjoint subdomains or owned boundary
pieces from the qualified serial integrator. Specify coverage and contribution
ownership before scheduling tasks. Each worker returns checked local bounds
and region mapping; the coordinator performs exact/outward interval reduction
and applies the original global and per-region precision rules.

Shared uncertainty contributes once to the total and conservatively to each
affected region. Local tolerances must compose into the global target; equal
relative tolerances for unrelated tasks do not establish the requested error.
Use deterministic batched refinement and canonical tie-breaking for reproducible
search. Keep task failure/retry idempotent and prevent parent/child partitions
from being counted simultaneously during refinement or resume.

Test the same difficult controls as S3/S4, worker counts and completion orders,
tiny contributions, missing work, duplicate retries and interrupted reduction.

**Acceptance:** fixed-work partitions reproduce canonical serial bounds.
Different admitted adaptive partitions each pass independent checking and the
same precision request; their certified intervals must be compatible. Preserve
the distinction between identical mathematical results and identical execution
receipts. Report speedup including final proof checking and process overhead.

### S8 — qualify the delivery and report measured limits

Receive the nineteen original profiles and existing difficult controls through
the selected serial candidate and admitted worker configurations. Preserve all
355 original frozen files and the existing portable capsule. New protocols,
proofs, source/build identities and failure receipts go in additive versioned
evidence directories. Fresh-process checking must work without the producer,
accelerator or caches, including after saved resume.

Report per-phase and end-to-end elapsed/CPU time, maximum simultaneous memory,
artifact size, worker count, precision status and host load. Separate one-CPU
improvement, multicore speedup `T1/Tp` and CPU efficiency `T1/(p*Tp)` for matched
successful tasks. Include regressions and tasks dominated by serial checking;
make no linear-scaling promise. Runtime variability remains explicit.

Update the workplan/checkpoint, #76 report and issue, developer commands and
BenchLab evidence. Performance qualification does not close #181 or other
native findings; follow their own acceptance/reconciliation workflows. Public
API/installed/platform qualification stays under #16 and P6. Broader protein,
GPU or multi-machine work needs its own scientific and resource admission.

**Acceptance:** repeatable benefit at the declared scope, unchanged scientific
guarantees, complete failure/resource evidence and truthful operating defaults.

## Source and test entry points

Paths below are existing starting points, relative to
`devtools/reference_validator/` and `tests/`. New focused modules/tests may be
added after their contracts are specified; the table does not create exports.

| Stage | Source boundary | Existing behavioral tests to extend |
| --- | --- | --- |
| S1 | `capture_power_cells.py`, `capture_volume.py`, `receiving.py`; retain the versioned region-volume receiving protocol | `test_reference_validator_power_capture.py`, `test_reference_validator_receiving.py`, `test_reference_validator_region_receiving.py` |
| S2 | `verify/power_cells.py`, `power_runs.py`, `verify/power_progress.py` | `test_reference_validator_power_cells.py`, `test_reference_validator_power_resume.py` |
| S3 | `power_cells.py`, `region_volume.py`, `verify/region_volume.py` | `test_reference_validator_reprobe.py`, `test_reference_validator_region_volume.py` |
| S4 | `edge_volume.py`, `verify/edge_volume.py`, `verify/edge_math.py`; retain earlier region/corner routes | `test_reference_validator_edge_volume.py`, `test_reference_validator_edge_receiving.py`, region/corner controls |
| S5 | `verify/polytope.py`, `verify/geometry.py`, measured `verify/edge_math.py`; optional producer accelerator | Exact geometry controls and integer dyadic/independent Fraction atan tests in `test_reference_validator_edge_volume.py` |
| S6 | `power_runs.py`, `capture_power_cells.py`; bounded orchestration | `test_reference_validator_power_resume.py`, `test_reference_validator_power_capture.py`; add focused process/failure tests |
| S7 | `region_volume.py` and saved region bundles | `test_reference_validator_region_volume.py`, `test_reference_validator_region_receiving.py`; add partition/process tests |
| S8 | Additive evidence, active checkpoint and BenchLab report | `test_reference_validator_followup.py`, existing per-family receiving and reporting guards |

## Resource controls and implementation closeout

Before a costly run inspect scheduler context, CPU/load, available RAM, swap
activity and memory pressure. Current execution is local without Slurm. Keep
one CPU/thread by default and at least 20% physical RAM available with an
adequate minimum reserve (initially 4 GiB). Free memory is not reserved memory.

Use finite CPU, elapsed-time, mathematical-work and memory budgets. Begin with
the existing serial 2 GiB address-space cap. For a process pool, choose and
enforce an aggregate envelope as well as per-process caps: multiplying 2 GiB
by the worker count is not a reservation. Bound task payloads, pending results
and process/native thread counts, including any threaded numerical libraries.
Measure total CPU across coordinator/workers and the maximum simultaneous
memory footprint; a single child's peak is insufficient. Monitor normally at
five-second intervals, stop new work on pressure and keep the last valid state.
State whether a limit was enforced or only sampled; do not claim a hard pool
cap from monitoring alone. Do not stop another user's processes.

Initialize limits in every child before scientific work and test them under
process spawning. Allocate any global task/work budget across the pool; adding
workers must not silently multiply it. Preserve the original per-cell limits.

For each implementation increment: add meaningful behavioral tests first,
run its bounded affected selection with `--receptor=llm`, Ruff/format and local
typing, then independent saved-result and relevant reporting checks. Reuse
applicable existing tests; prose-only plans need no tests of their headings.
Preserve the current public/native mathematical scope and review DFND chapters
if an actual operator or physical interpretation changes. No extra dependency
or environment change is selected by this planning document.

Commit coherent increments with `[skip ci]`. Record accepted scope, source,
commands, budgets, outcome, remaining work and next stage in the active checkpoint
and #76. Keep full-suite/minor/platform evidence pending under its owning gate.
Archive completed planning records through the reporting protocol when their
whole scope is resolved; retain the dated evidence and deferral reasons.
