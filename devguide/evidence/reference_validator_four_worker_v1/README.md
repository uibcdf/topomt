# Bounded four-worker assessment

Owner [TopoMT #76](https://github.com/uibcdf/topomt/issues/76).
Base: `293fc69e83ae06928eb88e597e433b2b79994954`.

This frozen pilot compares the same cold independent analytic verification and
saving workflow with direct serial execution and two/four explicit workers.
Requests, arithmetic, complete geometry/frontier and every signed contribution
are unchanged. Each input receives one further fresh serial saved read shared
by all configurations. Producer/scientific imports are blocked; no public API,
native DFND operator or new scientific system is selected.

The tetrahedron 1.4 Å and closed-shell 1.4 Å profiles each have three fresh
repetitions per mode. The mode order rotates each round (1/2/4, 2/4/1, 4/1/2).
All commands use lower scheduling priority (niceness at least 10), one command
at a time, with at most four allowed CPUs. Parent AS stays at 2 GiB, parent CPU
soft/hard ceilings at 300/330 seconds, and the external deadline at 420 seconds.
Each worker keeps 256 MiB AS; the same total 120 CPU-second pool allowance is
divided across workers (30 seconds each at four). At most four tasks are pending,
with no more than 512 new pieces per pool. The four-worker aggregate virtual
envelope, including parent and spawn tracker, is 5 GiB; observed free memory is
not reserved. The 20%/minimum host reserve and pressure checks remain in force.

The multiregion dumbbell 1.4 Å block is **conditional**: after the closed-shell
pilot, all mathematical/resource gates must pass, actual four task workers must
be reached on large batches, the four-worker median must improve on two workers
by at least 5%, and `max(T4) < min(T2)` must hold. Otherwise that block is not
executed and the negative/inconclusive pilot is retained. These are a bounded
operating decision, not a universal performance threshold or statistical test.
Twenty-five existing analytic controls are selected for four-worker receiving
and further fresh serial reads. There is no automatic full nineteen-profile or
four-worker default expansion.

Five-second group RSS/priority samples can miss short worker lifetimes and
double-count shared pages. A four-worker configuration need not use all four
task workers on a tiny input. Actual worker records and matched timings must
remain distinct from requested resources. Full source-construction/resume,
broader S8/P6/P7, remaining S1/S3/S5, canonical #76/#60, native
#181/#180/#184/#188 and installed/platform/full-suite #16 keep their scopes.

Status: **completed at the selected scope — 2026-11-16 UTC**.
All 52 solve configurations and 28 shared serial reads pass (80 scientific
commands). Every mathematical field and total/per-region request equals its
frozen original. `expansion_decision.json` retains the executed closed-shell
gate: 5.18% median elapsed reduction with four versus two workers, separated
ranges, actual four task workers and sampled niceness 10. It authorizes the
selected dumbbell extension, whose corresponding reduction is 9.46%.

The [matched median/range table](table.md) shows all three fresh repetitions
per mode. Direct serial remains fastest for the tiny tetrahedron. Per-phase
timing and CPU receipts show that geometry/checking limit the total gain; no
linear/general scaling or zero-impact claim is made. The 80 science commands
sum to 2122.669 bounded elapsed / 2431.147 waited CPU seconds, counting each
shared read once. Peak sampled group RSS is 160.33 MiB. Scheduling gaps,
bootstrap, packaging, tests and building are outside those scientific totals.

The larger profiles spend approximately 3.5–4.8% more median waited CPU
with four than two workers. Actual CPU accounting, finite concurrency and
headroom remain distinct from resource reservations or guarantees for others.

The initial large-case launch omitted the declared source path and exits before
Model import with `ModuleNotFoundError`; `bootstrap_attempt1_execution.json`
and its raw log are retained beside that protocol. Setting the explicit source
path corrects startup. This 0.117-second pre-calculation failure is excluded
from the successful scientific durations, not used as a comparison baseline.

`receiving.zip` preserves all exact inputs, protocols/working JSON at their
repository-relative paths, the 51-module source and independent reader. Every
byte is verified before removing duplicate working trees. Protocols/resource
records/raw logs remain visible; `receiving_index.json` maps accepted scope and
resources. Source/test/preservation checks are recorded in
`source_qualification.json`; `MANIFEST.json` binds this evidence tree. Exact
drivers are retained before temporary cleanup. The original 355 frozen files
and all prior evidence remain unchanged.

The 23 selected receiving/report/DFND-example tests pass, including a fresh
producer-free serial read from the extracted capsule. A separate bounded
four-worker solve also runs successfully from the extracted source capsule
under Python `-S`, with its receipt/result/resources retained outside the 80-run
panel totals. Ruff check/format passes for 742 Python files; local mypy passes
51 validator modules; report-index/offline comparative checks and strict
single-CPU Sphinx rendering pass. This is source/local-rendering qualification,
not hosted deployment or full-suite/installed/platform admission.

The broader eight-stage plan remains partial. This receives four-worker
analytic verification on selected inputs, without expanding source-construction,
four-worker failure/resume, the full nineteen-profile four-worker panel or
native/public/installed scientific admission. The next source work remains
cost accounting and exact geometric invariant reuse under #76/S1/S3/S5.
