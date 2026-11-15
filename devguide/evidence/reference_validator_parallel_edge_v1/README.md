# Canonical analytic integration with bounded workers

Owner [TopoMT #76](https://github.com/uibcdf/topomt/issues/76), S7 continuation.
Contract: [parallel analytic checker](../../DFND/reference_validator_parallel_edge.md).
The frozen 51-module source keeps the same atom balls, probe, contact policy,
finite domain, power-cell/region assignment, signed analytic frontier, dyadic
bits and original absolute AND relative precision requests.

## Actual receiving

`plan.json` selects three existing original 1.4 Å Models (tetrahedron, closed
shell and dumbbell), each in direct serial and explicit two-worker modes.
Every configuration independently admits complete geometry, evaluates two face
pieces, saves work, recovers in a new process, completes the frontier, and
receives a further producer-free serial read. All six configurations preserve
**every mathematical field** of the frozen original verification, including all
per-region intervals, identities/counts and precision states. Only actual
checker-source/runtime provenance is compared separately.

The same receiving also executes sixteen original boundary precision controls
and nine earlier region controls in both modes: **50 configurations**. All total
and per-region requirements pass, including tiny eight-region and asymmetric
three-region controls. Each is also compared with a new serial recomputation
and the original verification. Control arithmetic caches are reset before each
configuration; their small timings are not a scaling benchmark.

## Exact work and trust boundary

The canonical face frontier is reconstructed from the complete checked topology.
Each worker is part of the independent checker and evaluates the existing exact/
outward `triangle_flux` on one oriented triangular face piece. The parent reduces
all pieces once, with signed contributions and every error retained. No producer-
supplied numerical result or accepted flag is used. Ordinary local runtime and
process transport share the declared trusted software base; this is not a proof
of remote computation or fault-tolerant hardware.

Partial arithmetic carries no whole-domain enclosure. Every saved contribution
binds its explicit nm**3 unit, Model, complete certificate/request, kernel,
canonical frontier and index. Recovery reconstructs geometry and recalculates
every stored interval; correctly rehashed forged bounds are rejected. The final
ordinary symbolic certificate remains portable and the serial saved reader needs
no task cache, pool or original producer. The source snapshot makes source-bound
work reproducible; reading a digest alone does not verify geometry or arithmetic.

## Timing and resources

The [phase table](table.md) distinguishes numerical tasks, full recovery,
additional serial reading and the complete bounded workflow. The remaining
numerical tasks take 34.368 → 23.458 seconds for closed shell and 46.655 → 31.561
for dumbbell. Complete elapsed is 257.367 → 237.898 and 343.681 → 335.794 seconds,
respectively. Each pair is **one observation on a shared host**, not a repeatable
or causal scaling claim. Geometry/recovery and independent serial reading
substantially limit the full-workflow benefit. Tetrahedron is slower with two
workers (0.807 → 1.458 seconds); direct serial remains the default.

Successful phases/configurations run sequentially, using at most two explicitly
allowed logical CPUs. Each parent has 2 GiB AS and 300/330 CPU-second ceilings;
each phase has a finite 420-second external deadline. Two-worker pools retain
256 MiB per worker and a 120 CPU-second pool allowance divided across workers.
At most 512 new pieces are scheduled per step, with checkpoints between steps.
Host reserve checks and signal-forwarding launchers protect the shared system;
observing free resources does not reserve them. No Slurm/GPU/multi-machine run
is selected. All successful monitored host samples retain the reserve.

Five-second process-group RSS samples include coordinator, workers and tracker,
but exclude the outer monitoring launcher. They can double-count shared pages
and miss peaks; tetrahedron phases are too short to resolve pool memory. Kernel
peak individual-process RSS and separate parent/waited-child CPU phases remain
in the records. Operational floating-second counters do not imply exact timing.

## Retention and qualification

`receiving_index.json` maps original/control inputs, protocols, exact outputs,
work snapshots and resources. `receiving.zip` preserves all working/input JSON
bytes at their original evidence-relative paths, plus exact source and derivations.
Working receiving trees are removed only after archived byte verification.
`capsule_manifest.json` binds archive/members. Inputs remain in this evidence tree
for protocol inspection; existing evidence and all 355 original frozen files are
unchanged. `source.zip` and the driver archive retain executable provenance.

Unit/regression controls cover source/PID/serialization binding, malformed raw
headers, task loss/duplication, out-of-order failure/retry, cooperative stop,
negative owner flux, exact zero/free/blocked cases, tiny/asymmetric regions,
literal-zero/unmet requests and rehashed false saved arithmetic. Fresh extracted
serial/parallel readers run without producer/scientific imports or site packages.
Generic progress storage has matching 16 MiB write/read limits; the older custom
power-writer 128 MiB/reader 16 MiB mismatch is separately retained under #76/S2/S6
and is not claimed fixed by this route.

The two disjoint selected test groups pass **224 tests (149 + 75)**, including
the actual extracted parallel checker and serial reader, earlier certificates,
volume controls, the executable DFND example and report governance. Ruff check
and format pass for 738 selected Python files; local mypy passes all 51
validator modules. The one-CPU strict Sphinx build succeeds with notebook
execution disabled, and its analytic-report anchor and method-book link are
checked. This is local rendering, not a hosted deployment. Raw test/build logs
and bounded execution records are retained alongside
`source_qualification.json`; `MANIFEST.json` binds every evidence payload.

S7 is qualified at this selected **fixed-frontier** scope. The full parallel
nineteen-profile/four-worker panel, remaining S1/S3/S5 and broader S8/P6/P7 keep
their gates. Old source-bound checkpoints require their recorded source/runtime;
the earlier serial nineteen-profile precision retains its source scope. Native
#181/#180/#184/#188, canonical native #76/#60 and public/installed/platform/full-
suite #16 remain separate. No native DFND operator/promotion, new geometry,
protein or original provider run is changed or selected.
