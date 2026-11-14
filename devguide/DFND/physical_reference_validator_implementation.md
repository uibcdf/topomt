# Physical reference validator: implementation plan

Date: 2026-11-12, repository-local date. Owner:
[#76](https://github.com/uibcdf/topomt/issues/76); first DFND consumer:
[#181](https://github.com/uibcdf/topomt/issues/181).

**This is the detailed implementation plan.** The
[critical design](physical_reference_validator_plan.md) owns the scientific
requirements and their rationale. Its precision-first priority applies here:
correctness, justified exact decisions and certified error bounds outrank
runtime. Runtime/memory measurements plan feasible execution; competitive
speed is not an acceptance criterion.

Planning baseline: `0b68206b0af2210b3f27fc3d70fd5837512148c5`.
The [input/tool inventory](../evidence/reference_validator_planning_inventory_v1.json)
checks six original models, 19 selected profiles and all 355 previously frozen
files without changing their bytes. It is an inventory, not execution of the
new validator. The [first implemented P0 checkpoint](reference_validator_checkpoint.md)
now delivers exact model/primitive checking, a bounded partition pilot and ten
retained tetrahedron proofs. The bounded P0 input/proof/run/checkpoint contracts
and checked resume are now source-delivered; P1's geometry construction is
unselected. The [one-ball box feasibility tranche](reference_validator_p1_feasibility.md)
now proves nontrivial exhaustive region inventories on its admitted analytic
scope, including exact throat closure. It does not select the general multi-ball
construction or pass P1's precision gate. The checkpoint states the remaining
scientific gates explicitly. The [analytic precision tranche](reference_validator_precision_feasibility.md)
now passes the frozen k=8/16/24/32 total-volume ladder on contained singleton/pair
clusters. General construction and clipped/per-region precision remain unqualified.
The [hull domain route](reference_validator_hull_checkpoint.md) now proves exact
center-hull identity and closed box intersections on retained small controls.
All six original center hulls now have independently checked saved receiving
at `9a276cd`, using the maintainer's selected bounded local execution without
Slurm. The [steric integration](reference_validator_hull_sterics_checkpoint.md)
now source-delivers verified HullDomain, full-sphere receiving and exact
point/path/whole-convex-domain checking. Source `833a774` retains all ten selected
analytic/original profiles and forty outcomes with independent saved replay;
complete sphere-cut region construction remains open.

The [measured six-case panel](reference_validator_six_case_checkpoint.md) at
`2b21cb2` now executes all nineteen original query profiles with isolated worker
wall/CPU/RSS and independent saved proof checks. That coverage does not supply
the still-missing general topology/precision: only the fresh four-center
tetrahedral 1.7 Å partition has a complete global count in this run. P5 retains
its full scientific acceptance, beyond execution of finite candidate queries.

## Scope and acceptance of the first complete validator

Admit fixed, nonperiodic atomic balls with nonnegative radii, a nonnegative
spherical probe and an explicitly represented bounded full-dimensional convex
domain. The scientific object is the strict all-atom probe-center free set in
that domain, as defined in the critical design. First use the unchanged six
synthetic models; molecular admission remains after the synthetic phase.

The first complete scientific delivery must provide:

- Exhaustive connected free regions with checked source/model/domain identity.
- Anchor occupancy and connectivity, including continuous positive paths and
  justified separation/enclosure decisions when requested.
- Free boundary patches and their incident 3D regions under the same domain
  and strict contact convention.
- Total and per-region volume intervals meeting explicitly requested precision,
  or a separate unresolved-precision result retaining valid bounds.
- A separately executable certificate checker and recoverable evidence.

Complete enumeration concerns connected regions and boundary incidence. It does
not automatically supply every Betti number, a full homotopy type, globally
optimal bottlenecks, swept-probe volumes, periodic transport or biological
classification. A partial reference can be useful, but must not be described as
this complete delivery. Public API/package qualification has a later gate.

## Work breakdown and dependencies

| Stage | Work and concrete deliverables | Entry | Exit criterion |
| --- | --- | --- | --- |
| P0 — model and proof contracts | Canonical model reader/writer, proposed schemas, exact primitive checker, analytic fixtures and frozen receiving protocol. | Current design and original inputs. | Exact round trips and positive/negative/corruption tests pass; model/domain/contact/precision meanings are frozen. |
| P1 — construction feasibility | Bounded candidate prototypes, certificate/checker demonstration, high-precision integration options and an explicit architecture decision. | P0. | Choose a concrete completeness construction with justified assumptions and executable evidence; otherwise retain an unresolved design result. |
| P2 — qualified kernel | Selected geometry/arithmetic backend, domain validation, all-atom predicates, partitioning and producer/checker interchange. | P1 decision. | Predicate/domain/partition controls pass, including nonlocal blockers and altered certificates; no unsupported generic runtime claim. |
| P3 — connected regions | Complete topology certificates, component labels, paths, separations, exterior/boundary incidence and independent checking. | P2. | Prove exhaustive inventories on the admitted controls; retain unresolved status elsewhere. Counts alone cannot pass. |
| P4 — volume precision | Conservative baseline integrator plus the qualified high-precision route; component assignment and absolute/relative bounds. | P2; P3 for complete per-region results. | Requested bounds pass with consistent total/per-region accounting; zero-volume claims have an exclusion proof. |
| P5 — synthetic receiving | All 19 frozen profiles, retained runs/checker receipts, comparisons and additive BenchLab presentation. | P3/P4 at admitted scope. | Every profile has an evidenced disposition; complete-validator claims cover the required scope and every unresolved item has an owner. |
| P6 — public admission | Supported API, diagnostics, quantities, optional dependencies/attribution, saved readers, docs and packaging qualification. | Qualified scientific route. | Public contracts and applicable installed/Python/platform gates pass at their stated scope. |
| P7 — controlled scaling | Bounded CPU parallelism and optional GPU experiments with equivalent proof guarantees. | Qualified serial baseline. | Equivalent validated outputs/certificates and measured total resource use; no weaker acceptance for speed. |

P0/P1 are the immediate tranche. Do not build a large Rust spatial engine before
P1. P4 prototype work can inform P1; complete per-region reporting still depends
on P3. P7 is an optional improvement, not a prerequisite for scientific use of
an otherwise qualified serial validator. All stages currently remain under #76;
split independently closable themes into issues before separately scheduling
them. #181, #180/#184, #188 and #16 retain their own acceptance gates.

## P0: exact model and certificate contracts

### Model identity and units

Separate the source input, the numerical model actually validated and a later
native receiving being compared. Their identities must not be conflated.

1. Preserve the original input/protocol hashes and atom-row/frame maps. Protocol
   case names identify current cases; historical identifiers embedded in frozen
   files are not rewritten or adopted as new current names.
2. For the first matched native comparison, capture the normalized binary64
   coordinates, radii and probe in nm, independently of DFND classification.
   Interpret each captured number as its exact rational value. Record the
   receiving/conversion source and compare it with the actual native input
   before interpreting any discrepancy.
3. Keep the original qrec units/dtype/shape/block identities and the conversion
   record. Decoding and block-digest verification require their own tests;
   matching a file SHA-256 does not by itself qualify the decoder.
   Reuse PyUnitWizard's public `QuantityRecord.from_dict(...).to_quantity(...)`
   route, already used by the existing ball readers; do not implement another
   generic qrec decoder in the validator.
4. An intended decimal/rational model or an exactly converted source-unit model
   is also admissible, with a different model ID where its numbers differ.
   Do not silently treat it as the identical post-conversion binary64 model.
5. Store exact scalar numerator/denominator strings, reduced with positive
   denominator, and optional original hexadecimal floats for provenance.
   Signed zeros canonicalize to zero. Reject nonfinite scalars and invalid
   radii; do not approximate denominators to make the model simpler.

Compute expanded radii as the exact sum of the admitted atomic/probe values.
Avoid another rounded sum before the predicate. Input uncertainty, floating
receiving effects and arithmetic error in the solver remain distinct.

Public receiving later uses supported MolSysMT operations and PyUnitWizard.
The isolated checker consumes the frozen numerical model, without importing
DFND, consulting its wet supports or requiring a molecular package to search
for the reference regions.

### Domain identity

Exact boxes/tetrahedra and the separate checked center-hull/box domain route
are implemented at the [current hull scope](reference_validator_hull_checkpoint.md).
The steric Model now receives a verified original center hull for selected
primitive and whole-domain proofs. Its general clipped subdivision is not yet
admitted. Receive finite atomic-center hulls only with a certificate
that represents the declared hull, not just some enclosing polytope. Checking
that all atoms lie inside candidate facets is insufficient to prove equality
with their convex hull: missing facets could enlarge it.

Record domain halfspaces/vertices, orientation, source maps and construction
proof/backend. Floating Qhull output may suggest facets; it cannot acquire an
exact-hull certificate merely through a tolerance. Empty or lower-dimensional
domains receive explicit states, not a fabricated 3D volume/component count.

Use the same finite hull for matched finite-support observations. Later global
exterior studies need a separately identified domain and a proven free outer
collar; that domain must not replace the hull during comparison. Strict
`clearance > 0` excludes contact. No mesh epsilon inflates the physical set.

### Independent primitive tests before production code

Implement a small standard-library rational reference checker before optimizing
predicates. Python's [Fraction documentation](https://docs.python.org/3.14/library/fractions.html)
distinguishes an exact floating value from the decimal a reader may intend;
use constructors compatible with every supported minor, not a 3.14-only API.

Test and certify point/sphere signs, squared minimum/maximum sphere-box
distances, whole-cell one-ball covers, convex-domain membership and complete
segment clearance. For a segment, minimize the squared distance to each center
over its full parameter interval with exact endpoint/clamped-projection tests.
No square root is needed for these comparison predicates.

The first concrete test tranche, before producer/refinement code, covers:

| Planned test module | Required assertions |
| --- | --- |
| `tests/test_reference_validator_model.py` | Binary/rational round trips, exact radius expansion, units/maps/frame identity, model digest and malformed input rejection. |
| `tests/test_reference_validator_predicates.py` | Strict point and whole-segment clearance, sphere-box bounds, exact contact, nonlocal/unequal-radius blockers and domain membership. |
| `tests/test_reference_validator_certificates.py` | Model binding, complete one-ball domain cover and rejection of missing leaves/atoms, altered radius/domain/path and wrong arithmetic/schema identity. |
| `tests/test_reference_validator_topology_controls.py` | Independently justified corner/throat fixture definitions and expected transitions; no assertion that an unimplemented solver already resolves them. |

Each implementation tranche first demonstrates its failing behavioral tests,
then supplies the minimal implementation and records its actual scope. Avoid
tests that merely count plan sections or mirror implementation details.

The rational checker is a scientific certificate tool, not a replacement public
distance/neighbor API. Molecular representation and generic analysis remain
with their owning providers. Do not copy private MolSysMT Rust kernels.

### Logical records to freeze in P0

These are proposed records, not an already supported serialization API:

| Record / proposed schema | Required content |
| --- | --- |
| `topomt.reference-validator.model/1` | Input hashes, exact scalar encoding, units, atoms/frame maps, radii/probe, domain and contact policy; canonical model digest. |
| `topomt.reference-validator.run/1` | Model ID, requests/precision, backend/source/build identities, proof coverage, resource policy, stopping reason and certificate manifest. |
| `topomt.reference-validator.certificate/1` | Partition/domain proofs, geometric region/incidence coverage, path/separation witnesses, volume enclosures and trusted-base identifiers. |
| `topomt.reference-validator.verification/1` | Checked model/certificate digests, verifier revision, accepted/rejected proof obligations, available outputs and resource receipt. |
| `topomt.reference-validator.checkpoint/1` | Model/config/kernel identities, complete current partition including unresolved work, exact bounds and resumable frontier. |

Each observable has its own state: `resolved`, `unresolved`, `not_computed` or
`unsupported`, plus a reason and relevant proof IDs. Invalid input/certificates
are rejected, never reinterpreted as a valid empty result. `topology_complete`
requires an accepted completeness construction; it cannot follow from small
volume uncertainty or matching two graph counts.

Region/patch IDs are scoped to their model/run. Changed probes, transformed
models or native display labels require explicit correspondence, not equality
of ordinal IDs.

P0 tests must reject missing atoms, wrong radii/probe/units/frame maps, altered
domains, hash mismatches, malformed rationals and inconsistent schema versions.
Saved reading preserves original producer/model identities without crediting a
new computation. Separate trusted parser/arithmetic operations from search.

## P1: topology and integration feasibility

### Candidate constructions

| Candidate | Prototype work | Proof evidence required for selection |
| --- | --- | --- |
| Local arrangements with certified subdivision | Resolve free pieces cut out by actual spheres/domain planes; certify coverage and local incidences; join across adaptive-cell seams. | Exhaustive local pieces and attachments, strict-contact handling and a complete global assembly rule. All-free corners or sample labels are insufficient. |
| Global geometric decomposition with independent integration | Recover the expanded-ball boundary and clipped free regions globally, then assign integration cells/patches to those regions. | Exhaustive clipped regions, labels and boundary incidence, plus a checked integration-to-region map. Whole occupied-union topology alone is insufficient. |

Evaluate source/build/license and exact arithmetic modes before adding an
external dependency. A local source checkout belongs in the upstream reference
area and needs a pinned revision/clean-state record before use. Do not pull or
overwrite another checkout automatically. No SBL/CGAL runtime has been qualified
by this planning delivery.

The [SBL boundary package](https://sbl.inria.fr/doc/Union_of_balls_boundary_3-user-manual.html)
is a concrete lead for union geometry. Its
[volume package](https://sbl.inria.fr/doc/Union_of_balls_surface_volume_3-user-manual.html)
uses boundary-based constructions and interval results. Neither manual proves
our future adapter's clipping, region labels or independent verification.
The [CGAL spherical kernel](https://doc.cgal.org/latest/Circular_kernel_3/index.html)
is a primitive library; select explicit number types and qualify degeneracies
rather than trusting a build's default "exact" label.

Do not require every cut cell to use the same local construction if a global
proof supplies the complete regions. Conversely, a global library returning a
count without recoverable regions is insufficient. The checker must verify
coverage/incidence obligations or explicitly identify its qualified trusted
geometric base; merely rerunning the producer's topology function is not an
independent proof of that function.

Compare both candidates, but do not build two complete engines. A demonstrated
contract/API/geometry gap can reject a candidate without an expensive prototype;
retain the evidence and prototype only the viable unresolved decision points.

### Decisive analytic qualification fixtures

These small validator fixtures do not select new BenchLab geometry families.
Freeze their formulas and expected answers before prototype execution.

| Fixture | Independently justified obligation |
| --- | --- |
| No atoms in a box | One connected region, full exact box volume and boundary incidence. |
| Box entirely covered by one ball | Empty free set with a full-domain exclusion certificate. |
| Unit ball strictly inside `[-2,2]^3` | One connected free region; volume `64 - 4*pi/3`, enclosed with an independently bounded pi. |
| Two disjoint internal balls; nested/coincident balls | Known union-volume formulas; redundant obstacles cannot change the result or lose source attribution/maps. |
| One ball, eight corner regions | In `[-1,1]^3`, expanded radius `3/2` gives exactly eight free components, despite a single obstacle. Use the proof below. |
| Very small corner regions | Repeat with rational `R = 173205/100000`, satisfying `2 < R**2 < 3`; all eight components remain required, however small. |
| Exact throat closure | In `[-10,10] x [-3,3] x [-4,4]`, use radius 4 and probes `1 - 2**-20`, `1`, `1 + 2**-20`. Strict free space has respectively one, two and two components. |
| Free endpoints, blocked segment | Reject the straight segment across the central obstacle; endpoint tests cannot certify its interior. |
| Unequal radii and distant blocker | Catch nearest-center-only or local-atom exclusion; retain the full obstacle set. |

For the corner fixture, each coordinate plane is covered because its points in
the cube have squared distance at most 2, while `R**2 > 2`. A free path cannot
change an octant sign. Each cube corner is free because `R**2 < 3`. Within an
octant, the segment from any free point to its corner increases each absolute
coordinate, hence squared distance, and stays free. This proves exactly eight
components independently of a grid or DFND.

For exact throat closure, the entire `x=0` section is blocked at `R=5`, including
the four touching corners. Both end sections are free. In either half, moving
outward along x stays free and reaches its connected end section, proving two
components. For `R<5`, the line `(x,3,4)` is free and joins the two ends; the
same outward argument puts every free point in that one region. This also
checks the strict-contact policy at an exact degeneracy.

Then attempt selected frozen tetrahedron, tube-exclusion and dumbbell-anchor
questions. Their existing sufficient references do not become exhaustive
component counts. The whole 19-profile qualification follows later in P5.

### Precision feasibility belongs in this gate

A whole-cell enclosure is a valuable baseline but can converge too slowly
for very small volume errors: surface-cut cells dominate its unresolved volume.
Do not lock high precision to an ever finer octree. Prototype a validated
curved-boundary integral or another rigorously bounded high-order route, with
exact region/patch assignment and certified transcendental evaluations.
Unqualified quadrature order differences do not supply this error proof.

For each construction, retain producer/verifier time, peak memory, certificate
size, achieved precision and the undecided locations. Select by mathematical
coverage, arithmetic correctness, auditability and attainable precision first.
If neither candidate can support the complete contract, record that result and
the concrete missing construction under #76 before extensive implementation.

P1 exits with a versioned architecture decision naming algorithm, proof
assumptions, trusted base, admitted/unsupported degeneracies, external revision
and licence, precision strategy, resource envelope and remaining qualification.
An implementation stub, black-box agreement or volume-only demonstration cannot
pass this gate. No wall-time speed target is part of the scientific acceptance.

Current bounded evidence: the [one-ball box tranche](reference_validator_p1_feasibility.md)
implements a complete finite monotone-sector cover and independently checked
incidences for the decisive corner/throat fixtures. Its retained thirteen controls
do not qualify additional obstacles, general clipping or high-precision volume.
General candidate selection and clipped/region-assigned precision remain open
under #76. The [analytic integration prototype](reference_validator_precision_feasibility.md)
now supplies checked requests, bounds and actual success/budget-stop evidence
for a separate contained-ball cluster scope. It does not pass the complete P1 gate.

## Planned module boundaries

Develop outside the production namespace. Model, bounded producer, checker,
receiving and CLI paths below now exist at the P0 scope documented in the
checkpoint; comparison and native-backend paths remain proposed. None is a
supported production export.

| Planned location | Responsibility |
| --- | --- |
| `devtools/reference_validator/model.py` | Immutable numerical model, source maps and canonical encoding; no DFND import. |
| `devtools/reference_validator/certificates.py` | Versioned producer records and proof-manifest writing. |
| `devtools/reference_validator/producer.py` | Selected backend orchestration, partition/frontier, budgets and checkpointing. |
| `devtools/reference_validator/verify/` | Separately runnable parser, exact primitive/domain/coverage checks, topology obligations and volume verification. No import of producer search code. |
| `devtools/reference_validator/receiving.py` | Read original protocols, freeze the actual validated model and create additive source-bound results. |
| `hull_model.py`, `center_hull.py`, `verify/center_hull.py`, `verify/polytope.py` under the developer directory | Exact source hull/equality proof and closed geometric clipping; Model's proof-backed HullDomain admits steric point/path and sufficient whole-domain certificates. General hull subdivision/regions remain pending. |
| `devtools/reference_validator/box_topology.py`, `verify/box_topology.py` | Implemented scoped one-ball/axis-box completeness construction and its standalone sector/incidence checker. This is P1 control evidence, not the selected general engine. |
| `analytic_volume.py`, `volume_request.py`, `verify/analytic_volume.py`, `verify/_interval.py` under the same developer directory | Implemented contained singleton/pair cluster total-volume proof, explicit precision requests and declared trusted rational interval/constants. General clipping and region assignment remain pending. |
| `devtools/reference_validator/compare.py` | Mapped occupancy/connectivity comparisons; keeps morphology/count semantics distinct. |
| `devtools/reference_validator/__main__.py` | Implemented `freeze-tetrahedron`, `produce`, `box-topology`, `volume`, `verify`, `start`, `resume`, `verify-run`, `freeze-hull-source`, `hull`, `clip-hull`, `verify-hull`, `freeze-hull-model`, `domain-proof`; native comparison remains planned. |
| `devtools/reference_validator/native/` | Optional Rust crate/backend after P1, with exact arithmetic strategy and a bounded standalone process interface. |
| `tests/test_reference_validator_*.py` | Model, exact arithmetic, certificate rejection, topology, precision, receiving and resource/resume controls. |

Do not create empty production modules to mimic progress. The producer and
checker may share the schema specification; they should not share the same
unchecked geometric conclusion. Cross-language agreement is a test, not a proof
of algorithmic independence. Document the actually trusted operations.

MolSysMT owns molecular receiving and generic analysis. At the inspected clean
source `ff25f120243319ca9515009b4971e24a2eb0dc22`, public distance/neighbor
operations are exported. Its local tracking snapshot is behind 50 commits
without a fetch; refresh the relevant public contracts before implementation.
Those approximate distance APIs are not automatically conservative pruning
oracles. Ask for an owning provider tool if a missing reusable public capability
is actually required; keep topography-specific proof interpretation in TopoMT.

## P2/P3: partition, topology and checking

If using subdivision, encode a complete prefix-free dyadic partition of the
root region. A split has all eight children; no duplicate/overlapping leaves or
missing frontier is allowed. Prove the root contains the declared domain.
Outside-domain leaves require evidence; clipped leaves remain unresolved unless
their relevant geometry is certified.

Whole free cells require clearance against every potentially reaching expanded
ball. A one-ball cover suffices for a blocked cell; several balls jointly covering
it need a separate proof. A conservative index must retain checkable exclusion
bounds; the first small-case verifier scans all source atoms independently.

Inner connectivity supplies positive paths; conservative outer connectivity can
supply separation. Ensure optimistic adjacency includes every possible physical
transition, including adaptive seams. Never use a missed search or an omitted
adjacency as proof of disconnection. Check full rational path segments and
their domain membership; attach free boundary patches using compatible routes.

Complete topology certificates must establish every local/global free piece,
all required attachments and exhaustive assembly. Retain unresolved geometry
and an explicitly incomplete inventory until those obligations pass. A small
unknown volume, equal inner/outer counts or a visually convincing mesh cannot
replace them. The verifier rejects changed incidences, omitted components,
fabricated joins, uncovered leaves and wrong input/domain identities.

Test exact rational translations, axis permutations/sign changes, rational
orthogonal rotations and uniform scaling of coordinates/radii/probe. Compare
exact transformed models; a rounded floating rotation is a new nearby model,
not necessarily an exact rigid motion. Validate source-atom permutations and
unit receiving without assuming two rounded conversions have identical bits.

## P4: controlled volume precision

Produce lower/upper enclosures `[L,U]`, not an unqualified number of digits.
For exact zero require a full exclusion proof. For positive volume, retain
region identity and the proof that the integrator measures that region.

Use exact dyadic/rational partition sums or outward-rounded intervals for a
baseline. Its lower bound must not decrease and upper bound must not increase
on a valid refinement of the same model/partition. A higher-order or analytic
boundary route can replace it after its own rigorous error and patch-coverage
checks. Point estimates, empirical convergence and Monte Carlo agreement are
secondary diagnostics.

Volume requests include an absolute tolerance in volume units and an optional
dimensionless relative tolerance. Every enabled constraint must pass:
`U-L <= absolute_tolerance`, and, for a positive lower bound,
`(U-L)/L <= relative_tolerance`. If relative precision is requested and
`L=0<U`, retain unresolved relative precision. Handle certified `[0,0]`
explicitly. These are configurable requests, not minimum component sizes.

Reject negative/nonfinite tolerances and requests with no enabled precision
constraint. A zero-error request only succeeds with an appropriate exact-value
certificate; it does not silently become a small floating-point tolerance.

Use a pilot precision ladder with `k=8,16,24,32`: absolute tolerance
`V(D)*2**(-k)` and relative tolerance `2**(-k)`, recorded independently for each
requested total/component. These are progressively stronger experiments, not a
claim that all levels already pass or a ceiling on precision. Start bounded at
the first level; inspect achieved error/cost before attempting the next. Do not
relax a requested level silently when it proves difficult.

The initial P5 volume qualification target is `k=24` for the requested total
and each independently identified nonempty region; `k=32` is an additional
precision stress study. Freeze these requests before receiving new reference
results. If a target is not attainable with the admitted construction/budget,
retain that unresolved precision and its owner instead of declaring the target
passed or changing it retrospectively. These targets concern the exact admitted
numerical model, not experimental uncertainty or an empirical superiority claim.

Test full-box and contained-ball formulas with independent certified constant
enclosures; exact-zero controls; tiny components; interval summation/cancellation;
and stopped/resumed runs. Per-region accounting must respect disjoint physical
regions. Bounds for possibly merged regions can overlap while topology remains
unresolved; they cannot be presented as a sum of known disjoint components.

## P5: frozen six-case receiving and BenchLab

Use the original inputs/probes listed in the planning inventory. The independent
initial obligations are:

| Case | Probes, Å | Required receiving questions |
| --- | --- | --- |
| `regular_tetrahedron` | 1.2, 1.4, 1.7 | Common-origin access to four hull patches; origin enclosure; complete hull exclusion; independent volume controls. |
| `closed_shell` | 0.05, 0.2, 1.4, 5 | Existing origin-access/13-patch and enclosure controls; exclusion; enumerate any additional regions independently. |
| `shell_with_opening` | 1.4, 3, 5 | Origin-to-opening communication; enclosure; exclusion; patch-to-region incidence. |
| `straight_tube_narrow_dense` | 1.2, 1.4, 2.5 | Bent continuous route and end patches; reject colliding proposed skeleton; complete finite-hull exclusion. |
| `straight_tube_wide_sparse` | 1.4, 2.5, 5 | Axial route/end questions; explicit treatment of the marginal boundary; complete finite-hull exclusion. |
| `dumbbell` | 1.4, 2.2, 6 | Named anchors in one enclosed region, then separated enclosed regions, then hull exclusion; independently enumerate other regions. |

Do not demand decreasing component counts as the probe grows. Do not equate
physical boundary patches with native links or public Mouth children, or count
every native motif as a physical component. Compare model, domain, observable
and declared physical claims before diagnosing missing regions or false joins.

A reference path inside the hull does not validate a path claimed to remain
inside a particular native carrier: the latter also needs complete segment
coverage by that support. Restrict convex-domain reference queries to admitted
boxes/tetrahedra/hulls; do not silently pretend a nonconvex union of native
cells has already been admitted as a general domain. Likewise, a blocked stored
center does not prove its carrier empty. A full-hull exclusion does exclude
every subset of that same hull/model, supplying a stronger distinct proof.

Freeze model/requests/reference acceptance before new native observation.
Historical reference margins are prior evidence, not automatically a new exact
certificate under changed arithmetic/model interpretation. Retain all original
inputs, downloads, notebooks, observations and failed attempts unchanged.

Write new case evidence under versioned additive artifact directories, with
input/protocol/model, producer result, complete certificate, independent verifier
receipt, resources, stop reasons and exact dependency/source/build identities.
The case-level study should show the system/reference question, result with
availability and precision, mapped DFND observation and scoped interpretation.
New readers must consume qualified records rather than expose experimental
private code as a supported public API. Preserve portable saved attribution.

Each of the 19 profiles needs a disposition. An unresolved profile is visible
progress, not qualification of that scope. Completing the selected six-case
panel requires all of its required topology/precision gates, not merely 19
populated result rows. Reconcile any actual finding change
through the [comparative-finding workflow](../comparative_findings.md); updating
the validator does not automatically close #181 or reinterpret old artifacts.

## Resources, dependency admission and P6/P7

### Initial resource envelope

For cheap contract/predicate tests, start serially with one CPU, one numerical
thread, a 2 GiB address-space ceiling and a 60-second wall limit. These are
initial operational caps, not scientific time targets. Geometry pilots have
explicit cell/work/certificate-size limits derived from the first measurement;
they must not inherit an unlimited "use everything" default.

Before costly builds/runs, inspect scheduler availability and actual allocation,
CPU load, available RAM, swap activity and memory pressure. Plan a conservative
reserve and honor stricter infrastructure rules. If Slurm is applicable, obtain
and stay within a suitable allocation. Free resources are not reserved ones.
For the present phase the maintainer explicitly selects bounded local execution
without Slurm; the [hull checkpoint](reference_validator_hull_checkpoint.md)
records its limits, host observations and actual six-source receiving. Scheduler
availability is not an execution gate for this selected phase.
Increase pilot budgets only after measuring a representative case and checking
the current conditions; otherwise stop with recoverable unresolved work.

Implement checkpoint/resume before long reference runs. A resumed run must
verify identical model, domain, configuration and kernel identities, complete
partition/frontier and valid retained bounds. Recompute only under an explicit
new run identity when those change. Check interrupted writes, cancellation and
changed-checkpoint rejection in tests. Monitor producer and verifier peaks.

### Dependency and packaging decisions

The inventory finds Python 3.14.10, Rust 1.99.1, Cargo/CMake paths and module
specs for gmpy2/mpmath/SymPy. This is discovery, not arithmetic/ABI qualification.
P0's rational baseline requires no new arithmetic dependency. Do not change or
reinstall the shared Conda prefix to make a prototype work; existing migration
and environment qualification remain separately governed.

TopoMT currently uses Setuptools and a `noarch: python` Conda recipe. The first
native prototype should therefore be an explicitly selected developer backend
or standalone process, without silently embedding architecture-specific bytes
in the existing package. P6 decides optional external executable versus compiled
distribution only after scientific qualification and the appropriate #16 gates.

Any adopted external kernel needs licence/source/build review and offline
bibliography. Public arguments/units, optional availability and diagnostics use
the registered ArgDigest/PyUnitWizard, DepDigest and SMonitor contracts. Follow
[attribution](../attribution.md) at actual completion, including evaluated-empty
results, reuse, real-provider failure/absence and saved reading. Native or library
adaptation is not execution of an original detector. Do not add unjustified
version ceilings or dependencies before selecting the consumed API.

P6 tests include fresh import without optional kernels, genuine absence/failure,
explicit units and atom/frame maps, saved reading outside the checkout, supported
Python minors and the selected native delivery platforms. A source pilot does
not qualify this package or every platform. Public documentation needs an
executed supported workflow and relevant Sphinx/example checks.

The routine public workflow should return a reference report with its verified
model, availability, regions, bounds and proof receipt. Producer output awaiting
independent checking stays explicitly unverified; it cannot be advertised as a
certified result. Keep physical reference regions distinct from Topography
features and avoid creating catalog names by physical component count alone.
Default execution is serial with bounded work and explicit volume precision;
advanced users can inspect certificates, run a saved checker and request
stronger precision without rebuilding a DFND analysis. Final public export
names follow the existing API owner at P6, rather than creating placeholder
production exports during P0.

P7 may parallelize independent work with deterministic assembly and the same
proof contract. A GPU is optional: use it only with qualified conservative
predicates or CPU/exact rechecking. Record transfer, producer and verifier costs;
unqualified FP32/fast-math pruning cannot decide a certified answer. Thread count,
arithmetic precision and budgets must remain explicit and bounded.

## Immediate implementation sequence and definition of progress

The bounded P0 model/proof and operational-record tranches are source-delivered,
including tests, frozen protocols and retained runs. P1 is next: use the
corner/throat fixtures and small real frozen controls to choose a complete
geometry construction before expanding a native engine. Delivery of resumable
volume enclosures does not pass that scientific geometry gate.

Use scoped test-first changes with repository Ruff/format and applicable local
type checks; run selected tests under resource limits. Commit and push under
the existing maintainer route with `[skip ci]`; keep unexecuted full-suite,
installed/platform and scientific gates visible under their owners. Do not
announce a working validator from this plan or from inventory checks alone.

At each stage retain the producer revision, inputs, requested/achieved guarantees,
verifier identity and finite remaining obligations in #76 and its local record.
The first complete validator requires the scientific gates above, even if early
availability/path controls already help #181. Further native DFND changes use
that evidence deliberately; no new geometry family, provider/server run or
protein characterization is selected here.

## Verification of this planning delivery

The report-index and offline comparative-register checks pass. The selected
reporting, finding and original six-case artifact guards pass 17 tests with
`--noconftest --receptor=llm`, one CPU and a 2 GiB address-space ceiling:
1.70 seconds elapsed, peak RSS 65,292 KiB. All 211 local file links across the
eight changed Markdown documents resolve. The existing human version-file edit
is preserved. These are planning/evidence checks, not P0/P1 implementation,
scientific validator execution, full-suite evidence or installed/public delivery.
