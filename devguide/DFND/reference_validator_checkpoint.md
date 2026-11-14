# Exact reference-validator foundation: source checkpoint

Owner [#76](https://github.com/uibcdf/topomt/issues/76); first consumer #181.
Initial proof producer: `3b75f595eb6f52d9e6ff66a8f02bdcb0efb4633a`.
Operational continuation: `997f69b3d496333d7c89e2fc18dcd5a487ab38c1`.
One-ball topology feasibility: `0aac0c04e1ea49f0ca3f8c485f9b508c4d840e9e`.
Analytic precision feasibility: `580f1c016db48cc7041d9731ddc88501b87fd45a`.
Center-hull equality and geometric clipping: `2b6985bfb8a3ee8a2b856060435a7c3b93fbab6b`.
These are bounded implemented P0/P1 tranches of the
[implementation plan](physical_reference_validator_implementation.md), not a
complete topology-plus-precision validator or a supported public TopoMT detector.

## Remaining narrow profiles: probe-family source continuation — 2026-11-14

The [probe-family continuation](reference_validator_power_cell_construction.md#probe-family-geometry-reuse--2026-11-14)
checks a detached source proof and exact equality of all power inequalities
before reusing geometry. It permits only a probe change, then recomputes every
target free vertex/whole edge and all global/boundary partitions. The target
proof remains independently checked. Common radii in the original narrow tube
meet the algebraic criterion; general unequal-radius changes are rejected.

The frozen v4 panel selects only the original saved 1.2/2.5 Å profiles, with
separate sequential one-CPU/2 GiB/180 CPU/240 wall-second envelopes. It leaves
the positive global count unspecified and preserves all earlier source Models,
proofs and independent references. Actual receiving is a separate next gate;
source API/control implementation does not qualify these original profiles.

The source selection passes **305 tests** (61.48 seconds, peak RSS 96,328 KiB,
one CPU and 2 GiB), with repository Ruff/format and scoped mypy on all 32
validator modules. The focused 53-test reprobe/old-certificate selection also
passes after making the sorted-atom typing explicit; no geometry or numerical
decision changes in that typing adjustment. Full suite, public API/admission
and installed/minor/platform qualification remain separate under #16/#76.

## Narrow-tube exact-working-set continuation — 2026-11-14

The [working-plane continuation](reference_validator_power_cell_construction.md#exact-working-plane-continuation--2026-11-14)
profiles original atom 0 and removes only strictly slack constraints from the
producer's edge-working set. Every source inequality and the unchanged exact
checker retain their roles. All twenty frozen certificates are reproduced
exactly. The receiving helper saves input before construction and records
separate construction/saved-check/query costs for completed profiles.

The source selection passes **284 tests**, including those exact-proof
equivalence and interrupted-input/phase controls; one CPU, 2 GiB, 26.41 seconds
and peak RSS 97,900 KiB. Repository Ruff/format and scoped mypy on 32 modules
pass. An initial selection used a 60 CPU-second wrapper, which the older hull
capture correctly rejects because its contract requires at most 50; repeating
with the required 50-second cap passes. No scientific input or checker was
changed to bypass that operational guard.

The separately frozen repeat retains the same narrow 1.4 Å physical Model and
anchors. Its finite 180 CPU/240 wall-second budget follows the measured earlier
stop and first-cell profile; one CPU/thread, 2 GiB and conservative five-second
host checks remain. Actual committed-source receiving is separate from this
source qualification. Wider profiles, region-assigned precision and native
#181/#180/#184/#188 retain their scientific scopes.

The actual `fd3eeb7` repeat now constructs and independently verifies a complete
original narrow-tube 1.4 Å proof: **one free region, two free hull patches**.
The later per-anchor repeated checks reach the 180 CPU-second ceiling (190.237
wall seconds, 179.713 child CPU, peak RSS 37,568 KiB), without the final query/
manifest receipt. The construction record and v2 disposition preserve both
the accepted mathematical proof and that incomplete broader capture.

The next source continuation supplies a detached anchor batch with one complete
topology check, plus explicit raw-hash/original-producer saved-certificate
reading. The v3 protocol freezes reuse of the v2 proof; no new construction or
physical change is claimed. Actual saved receiving remains a separate gate.

Saved receiving now completes at `92679fc2d97c3d72108f35c79fc1a0c06c3cd471`,
using the original `fd3eeb7` certificate by exact raw SHA. Its final receipt
binds Model/proof/verification/anchor/path/phase files and records the saved
origin explicitly. The same narrow 1.4 Å Model has one complete free region,
two free hull patches and a separately checked 28-point path between the
earlier lower/upper anchors, despite its blocked origin. The process takes
68.683 wall / 66.497 CPU seconds, peak RSS 34,144 KiB, one CPU/thread and 2 GiB.
The fourteen host samples show no memory pressure and at least 49.80 GiB
available. This is saved replay cost; the earlier construction/repeated-query
attempt's 190.237 wall seconds remain recorded separately. Both earlier stops
remain historical; missing complete topology/query receiving is superseded only
for this exact source/model/probe. Other probes, region-assigned precision and
native qualification stay open.

Final validation passes **292 selected tests**, including a fresh independent
original-N81 saved replay without producer/DFND/NumPy/PyUnitWizard, complete
file/provenance/resource/phase guards and all 355 original artifact checks.
The bounded process takes 62.93 seconds, peak child RSS 95,700 KiB, one CPU and
2 GiB; the initial 287-code selection and five new receiving guards retain
their separate source stages. The added raw-log checksum assertion also passes
its focused test. Repository Ruff/format, mypy on all 32 validator modules,
report indexes, offline finding consistency and 168 local Markdown targets
pass. A full single-worker Sphinx HTML build passes with zero warnings and
notebooks unexecuted (20.07 seconds, peak child RSS 291,800 KiB, 2 GiB cap),
including inspection of the new BenchLab result/resource section. The prior
20.32-second build preceded a conservative available-RAM rounding correction;
the final build includes it. Existing PlantUML is selected explicitly, without
changing shared environments. Full suite, installed/minor/platform and P6
remain deferred under #16/#76; no hosted deployment or release is claimed.

## Exact multi-ball topology continuation — 2026-11-14 UTC

The [power-cell construction](reference_validator_power_cell_construction.md)
source-delivers a complete clipped polytopal partition and exact strict-free
region enumeration. Its independent checker re-enumerates cell vertices/edges,
tests all original spheres and reconstructs global regions and free domain-
boundary patches. Recoverable cell/face supports and anchor membership supply
checked continuous paths or separation by complete region identity. Degenerate,
identical and empty cells remain in the exhaustive source inventory.

This selects the topology portion of P1, with the documented cap/skeleton proof
and rational arithmetic as its explicit trusted base. A frozen twenty-profile
protocol covers seventeen analytic controls and three reused exact original
tetrahedron models. Test-first controls precede the JSON freeze; actual retained
committed-source receiving follows separately. Nonempty region-assigned volume
precision, all-nineteen-profile qualification, public P6 and native #181 remain
open. No Rust engine or complementary tetrahedral-grid implementation is claimed.

The source selection passes 275 validator/report/finding tests; adding the
original six-case integrity guard is retained for the final selection. Ruff and
format pass repository-wide; mypy passes all 32 validator modules. The process
uses one CPU, a 2 GiB cap, 26.68 seconds and peak RSS 83,660 KiB. These are
bounded source checks, not a full suite, installed package or support matrix.
The retained receiving below binds actual source/evidence identities.

The [retained twenty-profile receiving](reference_validator_power_cell_construction.md#retained-committed-source-receiving--2026-11-14-utc)
now runs at committed source `bb308baddc52098f73f1fe9e8b5a185dc7aa7c21`, with
all saved files independently replayed. The original tetrahedron probes
1.2/1.4/1.7 Å have respectively **1/1/0 complete regions and 4/0/0 free hull
patches**. All seventeen analytic controls pass. The bounded process takes
1.764 seconds, peak RSS 23,800 KiB, one CPU/thread and 2 GiB. This supersedes
the former missing complete inventories only for these models at this source;
it supplies no nonempty per-region precision or all-profile P5 qualification.

The separately frozen narrow-tube 1.4 Å attempt ends with signal 9 after
52.030 seconds under its hard 50 CPU-second ceiling (peak RSS 28,908 KiB),
without a complete certificate. Its recorded disposition is unresolved, not
empty or disconnected. Profiling and a justified sequential budget/construction
order remain under #76; no native #181 fix or other case qualification follows.

The final selection passes **281 tests**, including all saved twenty-profile
checks, a fresh producer/scientific-library-free original-model replay, the
historical narrow-stop guard and the original 355-file integrity check. The
bounded test process takes 25.41 seconds, peak RSS 96,324 KiB, one CPU and a
2 GiB cap. Repository Ruff/format, scoped mypy on 32 modules, report indexes
and offline finding consistency pass. A complete one-worker Sphinx HTML build
passes with zero warnings and notebook execution disabled (15.83 seconds,
peak child RSS 291,596 KiB, 2 GiB cap); the new report section is inspected.
The existing PlantUML launcher is selected explicitly from `topomt-dev`, with
bounded Java settings; no shared environment is changed. Full suite, installed
package, supported-minor/platform and public P6 qualification remain deferred
under #16/#76. No remote CI/deployment or competitive performance is inferred.

## Measured six-case panel — 2026-11-13 UTC

The [current panel checkpoint](reference_validator_six_case_checkpoint.md) and
[BenchLab report](../../docs/content/benchlab/synthetic/reference_validator_report.md)
record actual producer `2b21cb2` execution of all six original systems and all
nineteen frozen probes. Every case completes locally and sequentially, with
separate worker wall/CPU/RSS and source/hull/per-probe phases. Batch wall time
is 164.953 seconds, summed worker CPU 164.602 seconds, maximum worker RSS
56.59 MiB; one CPU/thread and at most 2 GiB per worker.

The run retains 305 checked outcomes (187 accepted proofs and 118 rejected path
candidates) with a downloadable exact-model/proof/checker archive. A fresh
tetrahedral partition supplies a complete zero-region/zero-volume proof at
1.7 Å on the same four-center physical hull. The other eighteen profiles retain
unknown complete topology; a finite candidate failure does not prove closure,
separation or global exclusion. Executing these nineteen query sets does not
complete P5's exhaustive-region/precision gates. Earlier stronger references
and all 355 frozen original files retain their scopes/bytes. No native finding
or public-package qualification changes.

## Certified hulls in the physical Model — 2026-11-13 UTC

The [hull/steric integration](reference_validator_hull_sterics_checkpoint.md)
adds immutable proof-backed HullDomain, full coordinate/radius/probe receiving,
exact point/continuous-path checks and sufficient whole-convex-domain proofs.
Every source atom remains present. The saved reader rechecks hull equality
without the constructor or quantity libraries. Box/tetrahedron subdivision and
run/resume explicitly reject hulls until certified clipping is implemented.

The [frozen pilot](../evidence/reference_validator_hull_sterics_v1/protocol.json)
contains four analytic fixtures and six original tetrahedron/narrow-tube
profiles. Actual source `833a774` receiving now retains all ten models and forty
outcomes: 35 accepted proofs and five deliberately rejected path candidates.
The original narrow tube has a free bent interior path at 1.2/1.4 Å against
all 81 atoms; its occupied origin at 1.4 Å does not exclude that path. The full
reference path's exterior tails are rejected in the finite-hull context;
boundary incidence and native-carrier qualification are not inferred.

The [retained receipt](../evidence/reference_validator_hull_sterics_v1/receiving/receipt.json)
contains 91 JSON files, 448,941 bytes. The one-CPU/2 GiB capture takes 3.55 seconds,
peak RSS 53,576 KiB, with a 50 CPU-second/60 wall-second ceiling. The
[execution record](../evidence/reference_validator_hull_sterics_v1/execution.json)
preserves both this run and an earlier equivalent capture. All-profile saved
replay is included in **240 passing selected tests** (19.10 seconds, peak RSS
96,552 KiB); Ruff/format and scoped mypy on 27 modules pass. All 355 original
files and native/finding dispositions remain unchanged.
General mixed-region construction, boundary incidence and per-region precision
remain open under #76. Earlier tranche statements below retain their dates and
source scopes; this integration supersedes the former missing steric-hull API.

## Certified hull identity and closed box clips — 2026-11-13 UTC

The [hull checkpoint](reference_validator_hull_checkpoint.md) implements an
exact incremental proposal and an independent halfspace checker. Full-dimensional
source containment, positive normal equilibrium/full rank, exhaustive feasible
plane intersections and complete source-vertex membership prove equality with
`conv(all received centers)`. A larger containing polytope is rejected. This
does not trust a floating hull, sample count or the producer's mesh topology.

Closed hull/box intersection now retains empty, point, edge, face and positive
3D outcomes, including a `2^-80` sliver. Outward facet cycles and exact geometric
volumes are recoverable. These are geometric domain quantities, not probe-free
volumes or connected regions. The separate immutable CenterSource consumes
only coordinates and preserves row/frame/file/unit identities. Public quantity
receiving is explicit under a nondefault policy; the earlier full steric Model
still admits boxes/tetrahedra until the next integration gate.

The [retained small receiving](../evidence/reference_validator_hulls_v1/receiving/receipt.json)
contains three analytic hulls and six clips: 28 JSON files, 70,653 bytes. They are
saved, read and independently checked at source `2b6985b`. The bounded ordinary control uses
one CPU, a 2 GiB address cap, 0.25 seconds and peak RSS 23,512 KiB. It schedules
no original sources, reports no original qualification, and claims no Slurm
reservation. Earlier pre-commit original-source probes only sized the requested
envelope; they are not a retained, source-pinned six-case receiving.

The full original-source batch is now **received and checked**, at source
`9a276cd9827f4d84fc048d94e06ee6d043779106`. The maintainer selected local
execution without Slurm for this phase. The
[additive local receiving](../evidence/reference_validator_hulls_v1/local_receiving/receipt.json)
retains all six original center sources, their hull certificates and independent
saved-file checks, alongside the small controls: 52 JSON files, 682,226 bytes.
One CPU, one numerical thread, a 2 GiB cap and individual 30 CPU/40 wall-second
limits contain the sequential work. The whole process takes 90.94 seconds;
peak child RSS is 56,816 KiB. Host samples show no memory pressure or active
swap, with more than 51 GiB available. The
[execution record](../evidence/reference_validator_hulls_v1/local_execution.json)
binds the receipt and external limits; no scheduler allocation is claimed.

This supersedes the earlier receiving deferral, not its historical evidence. The
[managed allocation attempt](../evidence/reference_validator_hulls_v1/scheduler_attempt.json)
requested one CPU/2 GiB in Slurm `tests` with immediate admission. Job 5 failed
allocation; execution never started and no queued job remained. The observed
node states were `inval` for `tests` and `unk*` for `normal`; their cause is not
diagnosed. No calculation started in that attempt. Its former managed-retry
action is superseded by the maintainer's local execution decision and successful
receiving; Slurm availability is not a prerequisite for this phase. Context is
[uibcdf-infrastructure#1](https://github.com/uibcdf/uibcdf-infrastructure/issues/1).
The failed attempt remains history, not a current blocker or algorithmic
limitation. Steric primitive Model integration is now delivered above; general
connected-region construction and region-assigned precision remain under #76.

The continuation selection passes **211 tests**: the previous 202 plus nine
original-source receiving, integrity, resource/scope and representative saved
replay guards. The selected process uses one CPU and a 2 GiB cap (18.27 seconds,
peak RSS 95,692 KiB); all 355 original case files remain unchanged. The full
capture already independently checked every saved original hull; routine tests
replay the tetrahedron and narrow tube to keep that selection small. Full-suite/
installed/minor/platform evidence remains separate under #16. No native/finding
disposition or public P6 admission changes.

Repository Ruff/format, report indexes, offline finding consistency and all
274 local Markdown file targets in the nine changed guidance files pass.
Scientific implementation bytes are unchanged from the qualified source above;
this delivery adds retained execution evidence, regression guards and guidance.

## Actual requested volume precision — 2026-11-13 UTC

The [analytic precision tranche](reference_validator_precision_feasibility.md)
implements exact geometric admission and certified total-volume bounds for balls
strictly contained in an axis box. After exact containment reduction, positive
overlap clusters must have size one/two, with disjoint interiors across clusters.
Every source atom remains mapped. Larger clusters and domain clipping are
rejected. Sphere/cap formulas, exact interval arithmetic, bounded Machin pi and
dyadic square-root intervals replace empirical volume convergence on this scope.

The [frozen 23-profile protocol](../evidence/reference_validator_analytic_volume_v1/protocol.json)
precedes the [retained receiving](../evidence/reference_validator_analytic_volume_v1/receiving/receipt.json).
All five models pass absolute `V_box*2^-k` and relative `2^-k` at
`k=8,16,24,32`, including partially overlapping balls at irrational center
distance. One empty-obstacle control also passes exact zero error. Two
deliberate stops retain valid enclosures with unresolved precision: a zero-budget
irrational pair and finite-budget zero error for a positive sphere. Expected
formulas/dispositions do not drive the numerical solver or checker.

The receiving retains 71 JSON files, 129,323 bytes, including an explicitly
selected directed-rounding audit with gmpy2 2.3.2 / MPFR 4.2.2 at 1024 bits.
That audit is secondary; saved certificate validity and producer arithmetic
need neither provider. The bounded process uses one CPU, a 2 GiB address cap,
0.28 seconds and peak RSS 27,112 KiB. The receipt separately retains its internal
timing/resource sample. These are small-control resource receipts, not speed
comparisons or whole-engine feasibility evidence.

A maximal 512-term/4096-bit regression exposed Python's default integer-string
limit. A bounded 20,000-digit exact codec now preserves those certificates
without changing global policy; oversize values are rejected. Earlier canonical
encodings and all original case artifacts retain their bytes. Invalid CLI
fractions fail cleanly without creating an output or implying physical results.

The final selection passes **161 tests**: the prior 106 plus 53 volume controls
and two exact-codec controls. Repository Ruff/format and scoped mypy on 21
validator files pass. Tests use one CPU and a 2 GiB cap (12.64 seconds, peak RSS
95,060 KiB); all 355 original case files remain unchanged. Full-suite, installed,
supported-minor and platform evidence retain their separate gates under #16.

This is total-volume precision for an explicitly admitted decomposition, not
P5 per-region qualification, an exhaustive multi-ball region inventory, general
hull clipping or a #181 correction. P1 remains partial for the general
construction and clipped/region-assigned integration decision. All earlier
method/finding dispositions remain scoped as before.

## Exact nontrivial region inventories — 2026-11-13 UTC

The [P1 feasibility result](reference_validator_p1_feasibility.md) now contains
an executable completeness construction for exactly one expanded ball clipped
by an axis-aligned box. A finite monotone-sector cover, every pair intersection
and checked continuous witnesses recover all connected regions. The independently
runnable checker imports no topology producer, DFND or NumPy. It rejects multiple
atoms and other domains rather than dropping obstacles or substituting a box.

The [pre-execution protocol](../evidence/reference_validator_box_topology_v1/protocol.json)
and [retained receipt](../evidence/reference_validator_box_topology_v1/receiving/receipt.json)
record thirteen controls. Both the ordinary and tiny corner controls have eight
proved regions. The throat's probes `1-2^-80`, `1`, `1+2^-80` give one, two and
two regions, including exact contact; a barely free corner is also retained.
Other controls cover empty/full domains, internal/external/boundary centers and
a zero-radius obstacle. No size cutoff discards a region. Each region's piece
supports, strict inequality and representative remain recoverable from the
model/certificate, rather than only a returned count.

The receiving retains 40 JSON files, 158,395 bytes, with source/code
identities and raw checksums. It takes 0.21 seconds as a bounded process, peak
RSS 21,548 KiB, one CPU and a 2 GiB address-space cap. These are tiny-control
resource receipts, not competitive benchmarks. All earlier evidence stays intact.

The new route does not compute region volumes or boundary-patch incidence.
`nonempty` refers to the sector's strict free subset; it never declares the
whole sector free. The [elementary completeness proof](reference_validator_p1_feasibility.md#completeness-argument-checked-by-this-construction)
uses one-obstacle outward monotonicity and a finite relatively closed cover.
Multiple atoms can destroy that monotonicity. P1 remains partial: no general
local/global architecture is selected or qualified, and multi-ball clipping,
exhaustive regions and validated high-precision integration remain open.
Original six-case/DFND/finding dispositions are unchanged.

The final continuation passes **106 selected tests**, including 27 new topology,
capture and retained-reading controls, plus repository Ruff/format and scoped
mypy on sixteen validator files. The bounded process uses one CPU and a 2 GiB
address cap (10.78 seconds, peak RSS 91,980 KiB). All 355 original case files
remain unchanged. See the feasibility record for scope and deferred evidence;
these checks do not qualify a full suite, installed package or support matrix.

## Direct inputs and checked resume — 2026-11-13 UTC

The three steric inputs are centers `(N,3)`, radii `(N,)` and the probe radius.
`Model.from_spheres(centers_nm, radii_nm, probe_nm, domain=...)` now receives
them directly and creates detached exact values, row IDs and a numerical source
digest. No bonds, chemical types or DFND results are needed. Units are explicit.
The extra domain is the finite observation context; the three sphere inputs
already define the globally excluded set. A hull and an exterior box ask
different volume/connectivity questions and cannot be silently interchanged.

Run/checkpoint contracts are implemented for the admitted box/tetrahedron
partition prototype. A run binds the model, fixed depth/leaf ceilings and exact
code/runtime identity; only per-step split budgets may change. Every unknown
cell remains in its frontier, including cells at a ceiling. Source changes
require a new run, while original mathematical certificates remain checkable.

Independent validation checks model/kernel/configuration identity, complete
coverage, counters, run summaries, parent links, preserved resolved cells and
nested volume bounds. It imports no producer or run-search module. Storage
uses exclusive new directories and a checksum manifest written last; incomplete
or altered bundles are rejected. This is not a universal power-loss durability
claim or atomic-directory-publication promise.

The [frozen resume protocol](../evidence/reference_validator_resume_v1/protocol.json)
reuses the original normalized 1.7 Å tetrahedron model. Its
[retained receipt](../evidence/reference_validator_resume_v1/receiving/receipt.json)
contains nine saved/read-back states plus an uninterrupted control:

| Step | Cumulative splits | Checked disposition |
| --- | --- | --- |
| 0 | 0 | Unresolved root; per-step budget reached. |
| 1–7 | 17, 34, 51, 68, 85, 102, 119 | Checked refinements with nested exact bounds; unresolved cells remain explicit. |
| 8 | 120 | 121 covered cells; complete finite-domain exclusion. |

The final mathematical certificate is identical to the uninterrupted control.
The capture uses one CPU and a 2 GiB address-space ceiling; 2.17 seconds elapsed,
peak RSS 21,508 KiB. It uses the saved exact model and standard-library checking,
without reloading quantities, DFND or an external geometric engine. These are
resource receipts for a small operational control, not competitive benchmarks.

## Implemented and checked

- Immutable exact nm models, explicit source atom/frame IDs, input SHA-256,
  strict probe contact, exact radius expansion and canonical rational JSON.
  Binary64 values retain their actual rational value, including conversion
  effects; no decimal approximation or hidden geometric epsilon is introduced.
- Admitted convex domains are boxes and nondegenerate tetrahedra. General
  atomic-center hulls are rejected by the first four-ball receiving route;
  it cannot substitute a box and change the validation question.
- Sufficient full-cell exclusion/availability predicates, exact convex-domain
  membership and whole-segment checks against every expanded atom. Nearest-center
  or four-local-atom checks cannot discard another blocker.
- A bounded Python partition pilot produces complete proof trees: box octants
  or tetrahedron longest-edge bisection. The independent checker reconstructs
  their coverage and recomputes all claims, without importing producer search,
  DFND, NumPy or the quantity codec. Shared trusted primitives are exact rational
  arithmetic and convexity, not an unchecked topology result.
- Exact total probe-center volume enclosures. Unknown cells remain in the upper
  bound; no requested volume precision is claimed. In this original partition
  route, only complete exclusion or an entirely free convex domain supplies an
  exhaustive zero/one component count; the P1 analytic route has its own scope.
- Standalone point/path and partition verification, schema/model/arithmetic
  binding, checker source fingerprints, finite work/input limits and saved CLI
  reading. Corrupt/missing/overlapping leaves, false covers/free claims and
  colliding paths are rejected.
- The four-ball reader uses the public PyUnitWizard quantity codec, propagating
  its RecordError on altered records. Received binary64 nm arrays are frozen
  exactly, without a claim of fresh equality to a newly executed DFND input.

The [developer usage guide](../../devtools/reference_validator/README.md) describes
the commands. The [frozen pilot protocol](../evidence/reference_validator_p0_v1/protocol.json)
precedes retained receiving. All ten proofs, exact models and original checker
receipts are in [the captured run](../evidence/reference_validator_p0_v1/receiving/receipt.json).
It records producer and dependency/source identities, checksums and resources.

## Actual frozen tetrahedron receiving

| Question | Checked result | Scope |
| --- | --- | --- |
| 1.2 Å, depth 6 | 38 leaves, 28 unknown; a valid broad volume enclosure with lower bound zero. | No component inventory or requested precision. |
| 1.4 Å, depth 6 | 38 leaves, 28 unknown; a valid broad volume enclosure with lower bound zero. | No enclosure/void or component-count proof. |
| 1.7 Å, depth 10 | 117 leaves, four unknown. | Small remaining volume does not prove exclusion. |
| 1.7 Å, depth ceiling 18 | 121 leaves, each covered by a specified expanded atomic ball; `[0,0]` volume. | Complete finite-tetrahedron exclusion; zero components. |
| Exact centroid, 1.2/1.4 Å | Two strict-free point certificates. | Positive point availability; no exhaustive component count. |
| Centroid to each of four face centroids, 1.2 Å | Four entire segments independently checked against all atoms and the tetrahedron. | Four access paths, not a boundary-patch inventory or global optimality proof. |

The positive points coexist with zero **lower** bounds from coarse cell
enclosures: those are conservative intervals, not zero-volume claims. No native
component label is used as reference truth. The 1.7 Å proof strengthens one
already studied finite negative control; it does not qualify #181's tubes.

The run takes 0.72 seconds internally (0.87 seconds for the bounded process),
peak RSS 51,844 KiB, one CPU and a 2 GiB address-space cap with a 60-second
external deadline. These measurements describe this tiny pilot, not performance
against DFND or another engine. Original case/notebook/download bytes remain
unchanged; retained proofs are new developer evidence.

Later source hardening in this delivery additionally rejects a decoded model
whose source binding differs from the frozen protocol, and rejects rational
inputs incorrectly labeled as received binary64 values. Dedicated failing tests
preceded both guards. The original receipt/source fingerprints remain historical
at `3b75f59`; saved models and mathematical proofs are independently replayed by
the final checker without overwriting the original verification records.

## Verification and remaining work

Test-first development began with absent-module failures. The first real-input
checks retained an insufficient depth-10 negative attempt and propagated the
owning codec's rejection type; tests now explicitly retain both unresolved and
proved outcomes. Coverage includes sub-float rational gaps, large translations,
exact contact, nonlocal radii, false endpoint-only paths, schema/model corruption,
budget ceilings, fresh-process checking without DFND/producer and saved replay.

For the initial tranche, repository Ruff/format and scoped mypy on all eight
source files pass, with Python 3.11 syntax and the actual 3.14 environment.
That bounded selection
passes **55 tests**: 38 new model/proof/receiving controls plus 17 existing
report/finding/original-artifact checks. It takes 4.45 seconds, peak RSS
90,624 KiB, one CPU and a 2 GiB address-space limit. The original 355 files
are checked unchanged. Report indexes, offline comparative metadata and 212
local file links pass. No full-suite or supported-platform matrix is inferred.
Linux-only capture/resource controls do not qualify a portable distribution.

The operational continuation passes **79 selected tests**, including 24 new
direct-input/run/storage/resume controls and all earlier selected checks.
It takes 14.30 seconds, peak RSS 91,336 KiB, one CPU and a 2 GiB address-space
limit. Repository Ruff/format and scoped mypy on thirteen source files pass;
report indexes and offline finding checks pass. The original 355 case files
remain unchanged. This is source evidence, not a full suite or public/platform
qualification.

The bounded P0 model/proof and operational run/checkpoint contracts above are
source-delivered; their initial absence is superseded by the continuation.
Center-hull geometry/clipping now has its separate checked developer route;
full steric-domain primitive integration is now source-delivered above. The six
original center-only hulls have retained receiving. The power-cell continuation
above supplies the topology construction; P1/P4 still need general clipped/
region-assigned precision and validated
integration; the earlier partition enclosures do not meet k=24, while the
analytic route above passes it only for its separate total-volume scope.
Full topology/precision qualification of all 19 profiles, complete apertures/attachments, biological
classification and public API/package qualification remain subsequent gates.

This standalone developer checker retains host/source/model provenance; it adds
no public scientific-client attribution boundary or original external kernel.
The planned P6 automatic attribution/API admission remains under #76. Do not
credit DFND, SBL or another detector as executed by the rational checker.
#180/#181/#184/#188 and the existing comparative findings keep their dispositions;
no native correction, original-provider run or protein phase is claimed.
