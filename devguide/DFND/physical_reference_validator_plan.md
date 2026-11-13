# Independent physical reference validator

Critical design review: 2026-11-12. Owner:
[#76](https://github.com/uibcdf/topomt/issues/76); first DFND consumer:
[#181](https://github.com/uibcdf/topomt/issues/181).

**Status: proposed implementation and acceptance plan, not a delivered validator.**
Source inspection baseline: `bc69b608dfbd7f6a5c40b0773e7f3570563ec5e8`,
the current #76/#181 records and the retained six-case protocols.
The maintainer prioritizes reliability and precision over execution speed and
accepts a reference calculation costing substantially more than DFND or a peer
detector. The existing [six-case review](../../docs/content/benchlab/synthetic/six_case_review.md)
and its frozen inputs remain the starting panel. This proposal does not change
DFND, previous observations, finding dispositions or the synthetic-first scope.

## Decision

Build a reference engine for connected probe-center free space, with checked
geometric certificates, explicit numerical bounds and a separately executable
verifier. Adaptive subdivision is a candidate spatial representation, not a
complete topology algorithm or an irrevocable architecture choice. Full
component enumeration needs a qualified construction proving exhaustive free
regions and their incidences, including the reporting boundary. Local cut-cell
geometry and a global geometric decomposition are alternative ways to supply
that proof; choose through the feasibility gate below.

Use Rust where measured cost justifies it, initially on CPUs. Do not make a
Rust-only implementation an obstacle to reusing a qualified exact geometry
library. Resolve the topology construction before describing the whole design
as an oracle. Monte Carlo and dense grids remain useful secondary checks.

## Second critical review and readiness for detailed planning

Review baseline: the first design at `cd88e5d`, checked against the
[native component contract](residence_transit_contract.md),
[physical boundary semantics](../../docs/content/dfnd/exterior_and_boundaries.md)
and [classification policy](../../docs/content/dfnd/classification.md).

The requirements are sufficiently defined to start detailed implementation
planning. Another broad review is not a prerequisite. Four refinements prevent
the plan from committing too early or promising a stronger result than its
evidence supports:

1. **Move the completeness-construction decision to the beginning.** It was
   too late in the first delivery sequence. Require a small feasibility study
   before building an extensive subdivision engine. A path/volume prototype
   alone does not retire this architectural risk.
2. **Specify the proof, not a mandatory cut-cell implementation.** Compare
   local certified arrangements with a global geometric decomposition plus
   independent volume integration. Either must prove clipped-region coverage,
   connectivity, labeling and boundary incidence. Global occupied-union Betti
   numbers alone do not provide these outputs.
3. **Separate physical and morphological acceptance.** The reference's regions
   are not automatically DFND components, motifs, native links or public Mouth
   objects. Compare model/domain/observable and the particular physical claim
   before diagnosing a false split, merge or count.
4. **Bound both the initial scientific scope and the trusted checker.** The
   first complete release targets connected probe-center regions in admitted
   fixed, nonperiodic convex domains, with volumes and boundary incidence.
   Full homotopy type, every Betti number, optimal bottlenecks, swept volumes,
   periodic transport and biological classification are separate capabilities.
   The checker must state which arithmetic/geometric facts it trusts; a second
   program repeating the same unverified topology routine is not independent
   confirmation of that routine.

The detailed plan should now define modules, certificate schemas, dependency
decisions, test fixtures, resource budgets, stages and observable exit criteria.
Its first stage must choose a concrete completeness construction or explicitly
record that decision as unresolved. No additional general audit is needed unless
that study contradicts the model, proof obligations or intended input scope.

## Scientific object and admitted model

Freeze atomic centers `a_i`, radii `r_i`, a spherical probe radius `p`, units,
atom/frame identities and a declared domain `D`. For the initial nonperiodic,
rigid-ball model, require nonnegative radii/probe and define

\[
g_p(x)=\min_i(\lVert x-a_i\rVert-r_i)-p,\qquad
F_p(D)=\{x\in D:g_p(x)>0\}.
\]

With no obstacle atoms, take `g_p = +infinity`, so the admitted domain is free.

The primary observables are connected components of `F_p(D)`, their volumes,
anchor membership, connectivity and incidence with free patches on the
declared domain boundary. At positive clearance these describe where a rigid
spherical probe center can be placed and moved continuously. Excluded contact
(`g_p = 0`) must not become a usable passage through a numerical tolerance.

This is steric validation under a specified model. Experimental coordinates,
radii, protonation and conformational uncertainty remain separate scientific
inputs. Static ball exclusion does not determine equilibrium solvent density,
energetics or flexibility. Those require additional models; molecular dynamics
is not needed to decide the fixed geometric question.

Two different domains must stay explicit:

- For the matched synthetic DFND studies, use the exact declared finite
  atomic-center hull `H`. Its construction/clipping requires checked geometric
  predicates too. Crossing a carrier boundary alone is not escape to infinity.
- For a later whole-molecule study, a padded bounding box may enclose all
  expanded balls with a certified obstacle-free exterior collar. Connections
  through that collar establish exterior access. Do not connect arbitrary box
  boundary patches without this justification, or substitute the box for `H`.

The initial general domain contract should admit a full-dimensional convex
polytope, including boxes and the existing hulls. Empty/degenerate domains,
nonfinite data, invalid radii and unsupported boundary conditions need explicit
outcomes. Periodic boundaries require a separate wrapping/percolation contract;
the isolated-box interpretation does not transfer automatically.
For finite studies, communication between declared boundary patches/ports must
not acquire an unqualified periodic or infinite-medium percolation claim.

Probe-center volume differs from the spatial volume swept by a probe,
`union(B(x, p) for x in component)`. Swept volume is a later observable with
its own overlap and boundary conventions. Neither equals an unqualified
"pocket volume" from every external tool.

## What existing tools already provide

The following source inspection is not new execution evidence:

| Existing route | Useful evidence | Why it is not the proposed complete reference |
| --- | --- | --- |
| `DFNDData.solvent_volume_measurement()` in [data.py](../../topomt/dfnd/data.py) | Quantity-aware carrier, bare-empty and probe-center measurements; all reaching atoms can participate, including nonlocal blockers. | Its domain is selected by a native resident/transit component. It cannot independently discover everything DFND missed. |
| `region_occupancy_grid()` in [solvent_volume.py](../../topomt/dfnd/core/solvent_volume.py) | Discretized shape and volume cross-check. | Center sampling, finite spacing and native-selected carriers do not certify whole-cell availability or connectivity. The current public occupancy route uses bare balls. |
| [Volume precision helpers](../../topomt/dfnd/core/volume_precision.py) | IID sampling intervals and numerical quadrature diagnostics, plus sufficient analytic cases. | Sampling confidence and order differences are not deterministic geometric error enclosures. The legacy `exact` method names fixed numerical quadrature, not a certified exact integral. |
| [Tube passage verifier](../../devtools/verify_tube_passage.py), shell covers and existing boundary certificates | Independent positive paths, sufficient exclusions and selected boundary/enclosure proofs. | Their declared finite questions do not enumerate every 3D component or measure every component volume. Keep their original arithmetic/precision qualification. |

Use these as controls and evidence sources with their existing scopes. Do not
silently promote a legacy grid or a previously measured sufficient bound to
the stronger new contract.

## Alternatives and their roles

| Method | Strength | Remaining obligation | Proposed role |
| --- | --- | --- | --- |
| Monte Carlo / randomized search | Simple occupancy/volume estimates and positive witnesses. | Rare components and passages can be missed; no finite unsuccessful search proves absence or separation. | Secondary cross-check and search aid. |
| Uniform grid / marching cubes | Straightforward debugging and visualization. | Finer spacing alone does not prove topology or exclude hidden subvoxel features. | Small diagnostic baseline. |
| Adaptive subdivision with rigorous predicates | Checked occupied/free regions, conservative volume bounds, positive paths and some negative decisions. | Mixed cells can conceal components or attachments indefinitely near difficult configurations. | Candidate spatial engine and certificate producer, subject to early feasibility review. |
| Exact/validated sphere geometry | Can resolve the obstacle boundary and difficult topology without relying on sampled voxel centers. | A concrete construction, domain clipping, degeneracies and component-label recovery must be qualified. | Candidate local/global topology construction; secondary analytic volume check where available. |

These are complementary parts of the proposed validator. More runtime spent
on an uncertified approximation does not turn it into a proof.

## Numerical and cell certificates

Record whether the frozen model interprets canonical binary inputs exactly or
uses exact decimal/rational inputs. Unit conversion, radius expansion and domain
construction belong to that model record. Certifying the converted numerical
model does not prove an uncertainty-free experimental geometry.

Use filtered arithmetic with rigorous error enclosures and exact rational or
arbitrary-precision interval fallback for undecided predicates. Increased
precision alone is not an enclosure. Treat exact contact separately; do not
perturb radii or coordinates to force a decision without declaring a different
model.

Each subdivision cell must be one of:

- **Free:** the whole admitted cell lies outside every expanded atomic ball.
- **Blocked:** the whole admitted cell lies in the union of expanded balls.
- **Unresolved:** neither assertion has been proved, including mixed cells.

For axis-aligned boxes, minimum and maximum squared distances to a sphere give
simple proof predicates without square roots. One ball covering a whole box is
a sufficient blocking proof, not a necessary one; multiple-ball coverage needs
its own proof or subdivision. All corners being free does not imply a free
cell: an obstacle can lie inside it.

Every potentially reaching atom must participate. A nearest-center query is
insufficient for heterogeneous radii. Spatial indexes may eliminate atoms only
through conservative, checkable distance/radius bounds. The first small-case
checker can scan all original atoms to avoid trusting the producer's pruning.

Use a complete, nonoverlapping partition with checkable child coverage. Domain
cut cells remain unresolved unless their clipping is proved. Exact dyadic cell
volumes or outward-rounded summation give lower/upper total-volume bounds from
free and unresolved cells. Refinement priorities may consider volume error and
topological ambiguity separately.

## Connectivity is a separate proof obligation

Construct conservative inner and outer free-space representations satisfying

\[
F^-\subseteq F_p(D)\subseteq F^+.
\]

For checked free anchors, connection in the inner representation proves a
physical connection. Separation even in the outer representation proves
physical separation. Otherwise the anchor-pair answer remains unresolved.
The optimistic adjacency construction must include every possible transition;
an accidentally missing edge could manufacture a false negative.

Retain a continuous path certificate for a positive result. Check every entire
segment against every potentially reaching expanded ball and the declared
domain. Checking endpoints, sparse trajectory frames or only the graph nodes
does not validate the path between them.

**Neither a narrow volume interval nor equal inner/outer component counts proves
that all physical components have been enumerated.** A tiny unresolved throat
can connect large regions. An unresolved band can contain an additional small
cavity. Set inclusion also does not order component counts. Per-component
upper bounds may overlap while their possible merger remains unresolved;
they must not be summed as volumes of disjoint known components.

### Cut-cell candidate for topology completion

One candidate resolves cut-cell topology using a checked decomposition induced
by the actual sphere surfaces and domain/cell planes:

1. Enumerate the local free pieces with predicates for the strict inequalities
   `||x-a_i||**2 > (r_i+p)**2` and the declared domain inequalities.
2. Establish that these pieces exhaust the free portion of each cut cell;
   recover their connectivity and all relevant face/edge/vertex incidences.
3. Match incidences across neighboring cells with the same contact policy.
   Include the topology of free boundary patches and their incident 3D pieces.
4. Assemble global components and verify that no unresolved cell or missing
   attachment could hide another component, connection or boundary patch.

This is a specification for a construction and its proof/checker obligations,
not an implemented theorem about our current grid. A local arrangement of
spheres/planes with exact predicates and algebraic constructions is one
candidate. A qualified semialgebraic decomposition with certified incidences is
an alternative for especially small difficult configurations. Do not substitute
sign samples or an unqualified arrangement routine for the coverage proof.

Alternatively, a global geometric construction could supply exhaustive
domain-clipped free components and their labels, while an independent adaptive
integrator bounds their volumes. It must also certify how integration cells
and boundary patches map to those regions. This avoids requiring the same
local arrangement construction in every cut cell; it does not remove any
completeness, incidence or labeling obligation.

Before the first implementation claims complete component enumeration, choose
and qualify that concrete construction. Until then, deliver useful certified
volumes/anchor answers with an explicitly incomplete component inventory.
Refining until memory runs out is not a substitute for this gate. A declared
minimum feature size can define a useful restricted study, but cannot establish
absence of smaller components in the unrestricted model.

### Existing geometric work worth evaluating

The [SBL union-boundary documentation](https://sbl.inria.fr/doc/Union_of_balls_boundary_3-user-manual.html)
describes exact combinatorics with exact or interval geometric constructions
and identifies exterior/cavity boundaries. Its
[surface/volume package](https://sbl.inria.fr/doc/Union_of_balls_surface_volume_3-user-manual.html)
describes bounded numerical results; the
[Vorlume application](https://sbl.inria.fr/doc/Space_filling_model_surface_volume-user-manual.html)
also documents cavity information. This is a substantive implementation lead,
not merely an analogy with alpha shapes.

It is not yet a qualified solution for our clipped complement, independent
verification or probe-center component output. Inspect exact versions, source,
license, arithmetic/template/build settings, degeneracy handling, clipping and
recoverable output before adoption. The documented examples switch geometric
kernels with build configuration; an "exact" label alone is insufficient.

The [CGAL spherical kernel](https://doc.cgal.org/latest/Circular_kernel_3/index.html)
provides primitives for spheres, circles and arcs; it is not a turnkey free-space
component/volume solver. Similarly, knowing the homotopy of an occupied union
from an alpha complex does not automatically supply the labels, paths and
volumes of our domain-clipped free complement.

[Plantinga and Vegter's isotopic meshing work](https://www.math.rug.nl/~gert/documents/2004/pv-sgp-2004.pdf)
illustrates why certified topology needs more than sampling. Its regular implicit
surface assumptions must not be transferred without proof to a minimum-of-ball
clearance field, nonsmooth sphere junctions or singular contacts.
[Chiang and Yap's subdivision planning](https://cs.nyu.edu/~exact/doc/motion-planning-socg12.pdf)
provides another relevant reference, with resolution/clearance qualifications;
the proposed implementation does not inherit those guarantees merely by using
free/blocked/unresolved cells.

## Result record and independent verification

Use separate availability states for occupancy, volume, anchor connectivity,
complete component enumeration and boundary incidence. A budget-limited run
may prove some of these and leave others unresolved. Do not compress them into
one success boolean or replace unavailable results with zero.

Retain the following in a versioned, resumable evidence bundle:

- Exact input/model identities, atom/frame maps, units, radii, probe and domain;
  source/dependency/backend/build identities and arithmetic policy.
- Complete partition and geometric certificates; independently checked path,
  separation and topology witnesses with decision margins and uncertainties.
- Total and, when justified, per-component volume intervals; checked seeds and
  boundary patches; component-inventory completeness and unresolved locations.
- Requested precision and achieved bounds, stopping reason, resources and
  work limits; separate model sensitivity from numerical uncertainty.

The checker must read the original model and serialized certificates without
calling DFND or accepting its component names, local residence values, gates
or wet carriers as truth. It must reject missing atoms/cells, inconsistent
units/radii/maps, broken paths and fabricated attachments. Corruption tests
are part of acceptance, not just ordinary producer/checker agreement.

Keep the checker smaller and operationally separate from search/refinement.
Document its trusted arithmetic/geometric base. This is independently checkable
numerical geometry, not a claim of a machine-checked proof of every source line.

For volume, request explicit absolute and relative error budgets per admitted
observable/component. Connectivity has an independent acceptance decision:
small numerical volume error is never its stopping criterion. Report an exact
critical-contact decision only when the predicate/construction supports it;
otherwise retain a bracket or unresolved state. Physical-radius sensitivity can
be studied with additional explicitly different probes/models.

MC/QMC can cross-check intervals and discover seeds, but cannot certify missed
components or negative connectivity. Statistical intervals must match their
sampling assumptions; correlated QMC points do not inherit an IID binomial
interval simply because their count is large.

## Initial synthetic acceptance panel

Replay the frozen six models and selected probes. The controls below name
existing independently justified questions, not assumed exhaustive answers.

| Existing case | First reference obligations |
| --- | --- |
| `regular_tetrahedron` | Small-probe origin communication with four hull patches; the intermediate enclosed region; large-probe finite-hull exclusion. Cross-check available analytic volumes. |
| `closed_shell` | Known origin access/enclosure controls, including the small-probe patch study, and whole-hull exclusion. Determine additional components through the new completeness construction rather than assuming the central region is the only one. |
| `shell_with_opening` | Known origin-to-opening communication, enclosure at the larger control, and exclusion. Recover patch-to-region incidence without using the public Pocket/Mouth count as a reference. |
| `straight_tube_narrow_dense` | Validate the bent all-atom route and two end patches at the positive controls; prove finite-hull exclusion at 2.5 Å. Reject colliding proposed paths. |
| `straight_tube_wide_sparse` | Validate the known axial route/end controls, keep the marginal boundary question explicit and prove finite-hull exclusion at 5 Å. |
| `dumbbell` | Same enclosed anchor region at 1.4 Å; separated enclosed anchor regions at 2.2 Å; finite-hull exclusion at 6 Å. Enumerate other components independently. Do not impose monotone component counts. |

Add small analytic primitive/unit controls for empty/full domains, single balls,
overlapping/nested/coincident balls, unequal radii, tangencies and near tangencies,
and a blocked segment whose endpoints are free. Include cavities/passages lying
between sample points, rotation/translation, atom permutation, units and
scale-relative numerical tests. These are validator qualification fixtures,
not a selection of another BenchLab geometry family.

Freeze new acceptance protocols and original model bytes before reference
receiving, including failed/unresolved runs. Do not tune the reference to match
DFND. A valid comparator requires the same model, domain and observable; a
native motif is not automatically a distinct physical connected component.

## Comparing the reference with DFND

Maintain distinct levels of acceptance:

- **Occupancy:** qualify a claimed probe-center position or available region
  against the complete obstacle model, using the declared numerical meaning.
- **Connectivity:** qualify a claimed continuous route, enclosure or separation
  in the same domain. Allow many-to-many correspondence between native supports
  and reference regions; an ambiguous correspondence is an unresolved result.
- **Morphology:** assess Pocket, Channel, Groove, motif or Mouth claims against
  their own definitions. Physical connectedness alone does not validate or
  invalidate a morphological subdivision or choose a catalog name.

For example, globally exterior-accessible pockets can communicate through the
exterior while remaining distinct useful topographic features. The native
contract removes OCEAN before defining finite graph components. A whole-space
reference that includes exterior communication cannot score that finite native
segmentation by requiring equal component counts. Similarly, free hull patches,
native links and public Mouth children remain distinct observables.

Before reporting a false split/merge or missing region, name the model, domain,
physical output obligation and mapped supports. Distinguish an unqualified
local candidate from a result explicitly claiming global physical validation.
The validator supplies evidence for #181's policy decision; it does not silently
choose or change that policy. Its own inventory must remain independent of the
native support selection so that false negatives can also be investigated.

## Early architecture feasibility gate

The detailed implementation plan starts with a bounded comparison of:

| Candidate | Required prototype evidence |
| --- | --- |
| Certified subdivision with local sphere/plane arrangements | Complete local free-piece and incidence certificates, conservative joining across cells, domain clipping and an independently checkable completeness argument. |
| Global validated geometric decomposition with separate integration | Exhaustive clipped free regions and labels, boundary incidence, and a checked map from integration cells to regions. A global cavity count without recoverable regions is insufficient. |

For each candidate, document the concrete algorithm/backend, mathematical
assumptions, exact/interval arithmetic and trusted checker operations, source
revision/license/build requirements, degeneracies and failure states. Qualify
complete inventories first on independently justified analytic primitive
fixtures. Then attempt selected frozen tetrahedron/tube/dumbbell questions,
keeping the limited existing anchor/path/exclusion references distinct from
previously unknown complete inventories. Do not fit counts to DFND.

Measure producer plus verifier time, memory and certificate size in a small
bounded pilot. Cost is secondary to reliability, but it must be predictable
enough to execute safely. A shared unverified topology routine in producer
and checker does not resolve that routine's proof obligation. Record the trusted
base explicitly and use analytic/corruption controls and independent checks
where they address that boundary.

Exit with a justified concrete construction and its remaining qualification
work, or an explicit unresolved design result. Do not lock the Rust/native
packaging architecture or start a large spatial-engine implementation merely
because the volume-only prototype works. This pilot belongs to the future
implementation plan; it has not been executed in this documentary review.

## Delivery order and completion gates

1. **Contract and trusted predicates.** Freeze model, boundary/contact policy,
   exact input interpretation, certificate schema and analytic controls.
   Perform the early architecture feasibility gate and choose the concrete
   completeness construction before extensive engine implementation. Develop
   independent checker/predicate tests before production/refinement code.
2. **Availability and total volume.** Deliver complete domain partitioning,
   rigorous bounds and sufficient full-domain exclusions. Start with the
   tetrahedron and the two tube exclusion controls consuming #181 evidence.
3. **Anchor connectivity and boundary incidence.** Deliver continuous positive
   paths, conservative separation, enclosure/exterior proofs and recovered
   patch relationships on the same six models.
4. **Complete component inventory.** Implement and qualify the construction
   selected at the first gate; exhaust the component/incidence obligations on
   the admitted panel and bind per-component volume bounds to those regions.
   Steps 2–3 alone do not complete the maintainer's requested validator.
5. **Independent DFND comparison.** Compare full reference regions with native
   supports under the separate occupancy, connectivity and morphology
   obligations above. Diagnose unavailable, missing, split or merged regions
   only where the declared physical claim warrants that comparison. Preserve
   all previous evidence and reconcile any actual finding change through the
   [comparative-finding workflow](../comparative_findings.md). #181 is a first
   consumer, not the owner of every reference capability.
6. **Measured scaling and later admission.** Optimize qualified CPU execution;
   evaluate bounded parallelism/GPU work only with measurements. Molecular
   inputs follow explicit admission after the synthetic phase; no protein
   characterization is started by this design review.

All stages remain under #76 until split into genuinely independently closable
implementation themes. Existing #180/#184 boundary availability, #181 public
qualification and #188 interpretation retain their own unresolved gates.
No issue is closed or finding changed by this proposal.

## Rust, CPU/GPU and shared-resource execution

Python should own molecular receiving, quantity conversion, orchestration and
reporting. A Rust core is a reasonable candidate for subdivision, conservative
spatial indexing, certified primitive filters and deterministic assembly, with
a supported exact arithmetic or qualified geometry backend where needed. Rust
does not by itself establish numerical correctness or a speedup over existing
compiled numerical code. Packaging/ABI/build support is a separate decision;
no new native runtime dependency is introduced here.

Inspect supported MolSysMT tools before implementing generic molecular/distance
operations. Existing private Rust internals are not a reusable public contract.
TopoMT owns the topography-specific reference algorithm and interpretation;
missing independently useful provider tools follow the common ownership route.
Any adopted scientific algorithm or external numerical backend also needs its
actual completion/attribution boundary, offline bibliography and optional
failure behavior under the [attribution procedure](../attribution.md).

Start measured pilots sequentially with explicit CPU/thread, memory, cell/work
and wall-time limits, checkpoint/resume and graceful cancellation. Inspect the
scheduler, load, available RAM, swap and memory pressure before costly work.
Free resources are not reserved resources. The maintainer's acceptance of
costlier calculations does not authorize exhausting a shared machine.

Parallelize independent cell work only within a declared resource allocation;
the merged result and certificate checks must preserve the same guarantees.
Avoid unbounded worker/thread pools. Record producer and verifier costs, not
only the fast inner loop.

GPU evaluation is a later measured option for batches of candidate predicates
or broad-phase discovery, with conservative bounds and CPU/exact verification.
Unqualified floating-point pruning, fast math or FP32 sampling cannot decide
the certified answer. Transfer cost, device memory, arithmetic guarantees and
irregular topology work may outweigh a GPU benefit; no speedup is assumed.

## Assessment of this proposal

The adaptive-grid idea remains useful, but the earlier formulation was
incomplete if interpreted as a complete connected-volume oracle. The essential
additional work is topology completion, checked arithmetic, exhaustive domain
coverage, explicit result availability and an independent verifier. A staged
implementation can provide valuable early decisions without overstating them.
The complete goal remains an exhaustive, independently checked description of
the admitted model's connected habitable volumes with controlled error.

## Checks on the initial review delivery

At `cd88e5d`, the report-index and comparative-finding offline checks pass.
The selected reporting/finding checks pass 16 tests with `--noconftest --receptor=llm`;
the bounded one-CPU execution takes 0.95 seconds and peaks at 51,932 KiB RSS.
The local file links in this plan and its three navigation/owner documents
resolve, and the pre-existing human edit to `topomt/_version.py` is preserved.
These are documentation/governance checks, not validator numerical execution,
a full test-suite run, a package qualification or hosted documentation delivery.

For the second review, the same offline checks and 16 selected tests pass;
the bounded one-CPU test execution takes 0.99 seconds and peaks at 52,000 KiB
RSS. The 37 local file links across the three changed documents resolve.
No scientific prototype or new topology certificate was executed.
