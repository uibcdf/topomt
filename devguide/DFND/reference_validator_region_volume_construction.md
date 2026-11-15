# Certified region-volume bounds and spatial comparison

Owner [#76](https://github.com/uibcdf/topomt/issues/76), work packages D/E/F of
the [active workplan](reference_validator_improvement_workplan.md).
This is a developer construction, not a supported production detector. Source
controls, retained original receiving and requested precision have separate
qualification gates in the [checkpoint](reference_validator_checkpoint.md).

The [face-flux prototype](reference_validator_face_flux.md) supplies a second
conservative construction within the actual power cells; its range-based
original tetrahedron pilot misses k=24. The later
[analytic edge construction](reference_validator_edge_integration.md) qualifies
all nineteen original total/per-region requests and selected tiny/asymmetric
controls. The box-cover results below retain their original definitions and
precision scope; they are a conservative baseline, not the latest precision
limit of the validator.

## First integration decision

Use a complete rational box partition of an enclosure of the **same declared
convex domain**, with exact all-atom predicates and labels from independently
checked power-cell topology. This is the first conservative baseline; the
planned integration within individual power cells remains a candidate for
higher precision. It is not an approximation replacing the declared hull by
a box: boxes crossing its boundary retain uncertainty and cannot contribute
their whole volume to a region's lower bound.

This baseline avoids introducing another unqualified polytope triangulator
before receiving error enclosures. It integrates the domain once, so identical
positive-volume power cells from coincident atoms cannot duplicate volume.
No native DFND tetrahedra, local wet selection or classifications are consumed.

The root box encloses every vertex of the verified convex domain. Therefore
it encloses the whole domain. Its recursive eight-child exact subdivision is
complete and has disjoint interiors. The checker reconstructs the entire tree,
rejecting absent branches, overlapping leaves, invalid paths and work excess.

## Local proofs and allocation

For each box B:

1. Exact linear extrema of a domain inequality can prove B outside the domain.
   Otherwise every domain inequality must hold throughout B before treating
   the complete box as inside. No center-membership test substitutes for this.
2. An expanded ball covering all box vertices covers its convex interior.
   This proves zero free volume in that box.
3. A strict lower bound on squared box-to-center distance against **every**
   source ball proves whole-box steric availability. Combined with whole-box
   domain containment, B is a connected free subset. Its exact center's
   independently checked supporting-root association identifies one region.
4. All other boxes remain unresolved, with their entire geometric volume
   contributing conservative uncertainty. Contact remains excluded; no epsilon
   changes the free set.

Let L_i be the free-box volume assigned to region i, and M the sum of unresolved
box volumes. A conservative total enclosure is
`[sum(L_i), min(V(D), sum(L_i)+M)]`. For each region, use
`U_i=min(L_i+M, U_total-sum(L_j for j!=i))`. Every unknown box is counted once
in the total; candidate upper mass can be shared by several regions. Thus
`sum(U_i)` need not equal U_total. Region identities and complete counts come
from topology, including tiny regions whose current lower volume bound is zero.

The simple bound assigns unresolved mass to every possible region; it can be
loose. A future tighter candidate set needs its own exclusion proof. A nearest
representative or the region of one sample cannot safely prune other regions.

Complete empty topology proves exact zero volume. A separately sufficient
whole-convex-domain free predicate gives its exact rational domain volume to
the single verified region, including a non-box hull. These are explicit
global shortcuts, rather than an inference from a finite sample count.

For an ideal unlimited fair refinement, box diameters tend to zero and only
domain/ball boundaries remain uncertain. Those finitely many plane/spherical
boundaries have zero 3D measure. This explains convergence of the conservative
bounds, not a promised finite runtime or precision. Actual runs retain finite
depth/leaf/time/memory limits and their measured unmet error when applicable.

## Independent checking and precision

`region_volume_certificate` proposes a partition; `verify` reconstructs it,
checks complete topology and recomputes all allocations. Producer search and
tree checking are separate. They share the declared trusted elementary box
bounds, exact subdivision and supporting-root predicates. This is not a second
independent implementation of those primitives or a machine-checked proof.

The admitted analytic singleton/pair route can supply total volume to a region
only when complete same-model topology independently proves exactly one region.
Its original strict contained-ball/box and error-enclosure admissions remain;
it does not become an integrator for a clipped hull or several regions.

The separate `analytic_corner_regions` admission implements a
[cap/wedge boundary integral](reference_validator_boundary_precision.md) for
one expanded ball centered in a cube with `2*a^2<R^2<3*a^2`. Complete topology
and an independent orthant/reflection argument assign one eighth of its total
to every one of its eight regions. A strict scheme/bit record selects bounded
outward rational interval arithmetic, square roots, Machin pi and atan series
tails. This high-precision clipped-boundary control leaves the original
center-hull precision gate separate. Exact contact and rejected asymmetric/
multi-atom geometry cannot be replaced by the symmetric formula.

`VolumeRequest` preserves explicit nm**3 absolute and dimensionless relative
constraints. Both enabled constraints must pass for the total and every
requested region. Valid bounds have `volume_enclosure_status=resolved` even
when `precision_status=unresolved`; per-region entries retain their own states.
`total_precision_status` distinguishes total success from aggregate success.
Literal zero error needs an exact value. The original k=24 target is unchanged.

Current adaptive limits are 4096 leaves and depth at most 24. A smaller
`max_leaves` call is a per-step operational ceiling within that fixed envelope.
The generic checker honors a smaller caller leaf limit too. Larger envelopes
or a more accurate boundary integrator require their own measured qualification;
this baseline does not promise all original positive profiles meet k=24.

## Saved refinement

Each certificate retains the complete leaf partition, Model/topology binding,
request, fixed envelope, parent digest and source/runtime kernel identity.
The unknown frontier is independently reconstructed from the retained leaves.
`save_region_bundle` writes exclusive Model/proof records and publishes their
checksum manifest last. `load_region_bundle` reads exactly the bytes whose
digests were checked and independently checks the proof. Torn/changed bundles
are rejected and older complete bundles are preserved.

`refine_region_volume` rechecks a saved certificate and admits only the same
source/kernel/request. `check_volume_transition` independently checks both
proofs, full refinement and nested total/per-region bounds. A parent digest
alone does not establish lineage; standalone checking labels it unchecked.
Changed source or requests require an explicit new run rather than retroactive
precision credit. No production package/installed-platform claim follows.

## Spatial comparisons with native supports

`compare_reference_claims` first matches the complete provided numerical Models.
It records exact point locations/region membership and all-atom whole-segment
path checks. Paths in the declared convex domain do not automatically remain
inside a particular native carrier. Path vertices and original source maps
remain recoverable; result supports are detached from mutable input arrays.

Named native carriers can supply unions of tetrahedra specified by original
source atom IDs. Exact vertex containment proves every convex tetrahedron,
and hence the union, lies inside the reference domain. Complete domain
exclusion then proves the entire submitted carrier empty. Separately, complete
one-ball tetrahedral covers can prove exclusion. Otherwise this first route
retains unresolved carrier qualification; a clear or blocked stored center
alone does not decide its entire carrier or connectivity.

This is the first #181 consumer. The comparison function checks supplied
supports; the receiving harness separately identifies fresh native execution
or saved reuse. The [qualified native panel](../evidence/reference_validator_native_comparison_v1/qualified_plan.json)
uses canonical nm coordinates and captures actual MolSysMT vdW radii. Those
radii differ by one binary64 step from the old provided-radius reference;
each target therefore has a **distinct exact numerical Model**. Its original
center hull remains valid, and the old complete partition is proposed only
as an untrusted candidate. The target checker reconstructs every full
inequality, cell and availability predicate before comparison. Original Models,
native observations and unsuccessful matching attempts remain unchanged.

The exact point query gives domain membership priority: 22 new narrow centers
are blocked inside the hull, eight are outside it, and the single wide center
is outside. `outside_domain` does not assert absence of atomic collision.
Native floating support tolerances and the older obstacle-clearance diagnosis
are separate observations. The complete submitted carrier unions lie in the
hull by source-vertex convexity and are independently excluded; this conclusion
does not depend on classifying a stored center as inside its carrier.
Native promotion/qualification policy, biological morphology and general
solver-correctness interpretation retain their owning issues.

For a possible later boundary-based integration route, the existing design
also identifies [SBL's surface/volume package](https://sbl.inria.fr/doc/Union_of_balls_surface_volume_3-user-manual.html).
Its manual describes interval treatment of boundary contributions for a union
of balls. That documentation does not qualify our clipped-domain/per-region
adapter, build, arithmetic mode or saved checker; no such engine is selected
or executed by this source tranche.
