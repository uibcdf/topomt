# Independent reference for the small-probe shell

Date: 2026-11-10. Owner: [#76](https://github.com/uibcdf/topomt/issues/76).
Status: **protocol frozen; reference implementation being received**.
The production pilot reports 13 patches at 0.05 Å; that known candidate is not
the reference's expected answer. Native ten-link grouping is also not an oracle.
The frozen protocol in `closed_shell/artifacts/small_probe_boundary_v1/` fixes
input identity, strict set, margin and bounded computational work before capture.

## A face count that allows free edges

The earlier one-face certificate used a covered triangle perimeter. That
hypothesis cannot be assumed here: the longest hull edge is about 3.822 Å,
while the expanded atomic diameter at this probe is 3.5 Å.

For a hull triangle T let K_i be its intersection with expanded ball i. Choose
a compact square Q in its plane, strictly containing T. Add three convex sets
B_j = Q intersected with the exterior closed halfplane opposite barycentric
coordinate j (`lambda_j <= 0`). Their union covers Q outside the triangle
interior, including Q's boundary. Each K_i and B_j is compact and convex, and
every nonempty finite intersection is convex. The finite closed-convex nerve
theorem therefore identifies their union's homotopy type with its nerve.
[Primary theorem: Bauer, Kerber, Roll and Rolle, Theorem 3.1](https://arxiv.org/pdf/2203.03571v6).

The union is compact and semialgebraic, hence locally contractible. It contains
the square boundary, so its plane complement consists of one unbounded outside
component and the free components inside T. Alexander duality identifies the
number of those bounded components with its first cohomology rank; over F2 this
is the first Betti rank of the nerve. Only the complete two-skeleton is needed
for H1. [Primary theorem: Hatcher, Corollary 3.45](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf#page=264).
This augmented-cover construction is our application of those theorems, not a
claim that the cited sources analyze this shell or supply its numerical answer.

Intersections containing atomic sets and one exterior piece reduce to the
opposite triangle edge; two exterior pieces reduce to a vertex. Three exterior
pieces cannot meet inside T because the barycentric coordinates sum to one.
Without atomic sets, the exterior pieces have all pair intersections and no
triple intersection. This supplies a complete, independently checkable inventory.

## Evidence and discovery

For each required singleton, active pair and clique triple, positive decisions
retain convex barycentric weights and an actual point strictly inside every
selected expanded ball by more than 1e-6 Å. Negative decisions retain convex
ball-center weights and a unit separating direction. For all points x of the
relevant triangle/edge/vertex domain, the weighted squared distance is at least
weighted center variance plus the squared projected separating distance. A
lower bound strictly larger than the common expanded radius proves emptiness.

The generator may use bounded convex dual optimization to discover weights.
The verifier does not call an optimizer: it checks every margin and inventory,
then computes the exact finite F2 boundary-matrix rank. Solver success alone
is never an accepted decision. Numeric records declare a fixed angstrom schema;
input quantities are decoded with the shared codec and explicit target units.
These are floating witnesses with decision margins, not formal interval proofs.

## Global hull count and paths

This bounded reference accepts global joining only if every face has zero or
one independently established free interior component. More complicated faces
are unsupported rather than reduced to one. All edges get independent quadratic
ball-entry inventories and strict free intervals. Each positive free interval
joins its two incident one-component faces. Every hull vertex is covered by its
own positive-radius ball, excluding an omitted vertex-only connection. Connected
components of this face/seam graph then count the global boundary patches.

Positive continuous paths need their own all-atom segment/ray evidence. A face
count or an unsuccessful path search does not establish a component attachment,
curved-path exclusion, physical aperture area or globally optimal bottleneck.
The new reference does not import production DFND geometry, outputs or witnesses.
Its original input and established independent homology/quantity helpers are
reused with their exact provenance.

## Budgets and receiving

One CPU/numerical thread, 6 GiB address-space and 120 s CPU limits; at most
20,000 intersection decisions, 2,000 solver calls and 100 iterations per call.
The pilot on canonical face [0,1,2] verifies a zero free-component count with
100 decisions and a 0.0174 Å minimum margin, about 0.1 s / 89 MiB process RSS.
Complete hull capture and falsification/actual DFND comparison remain pending.
