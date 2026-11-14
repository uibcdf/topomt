# Exact multi-ball regions through clipped power cells

Owner [#76](https://github.com/uibcdf/topomt/issues/76); first native consumer
#181. This is the P1 topology construction implemented after the measured six-case
panel. Correctness/completeness outrank speed. No native DFND operator changes.
Implementation, retained receiving and qualification are recorded separately
below; this derivation alone is not executed qualification.

## Fixed-probe partition

For the frozen expanded radius `R_i=r_i+p`, write
`q_i(x)=||x-c_i||^2-R_i^2` and define the closed clipped power cell
`P_i=D intersect {q_i<=q_j for every j}`. Differences of the q functions are
affine, so each P_i is a bounded rational convex polytope. Their union is D;
empty and lower-dimensional cells are retained, not silently discarded.
On P_i the strict physical free set is exactly `P_i minus closed_ball(c_i,R_i)`.
Every source atom participates in deriving the inequalities, including distant
large-radius blockers and coincident centers. Equal coincident balls can have
identical cells; their shared geometry is glued rather than counted twice.

[Aurenhammer 1987](https://doi.org/10.1137/0216006) supplies the established power-
diagram definition and polyhedral context. The completeness argument below is
explicitly derived here from convexity and polyhedral linear programming; it is
not attributed as a theorem proved in that article. No external geometry engine
is executed. This is not a claim of method novelty.

Power is used only to partition the **fixed-probe** exclusion problem. Its sign
is equivalent to spherical exclusion; its magnitude/order is not additive
clearance or a bottleneck. Weights `(r_i+p)^2` depend on p. This does not replace
DFND's ordinary Delaunay carrier or additive local capacities with weighted ones.

## Local completeness lemma: a convex polytope outside one ball

Let P be any nonempty bounded convex polytope, including lower-dimensional ones,
and K a closed ball. Construct a graph of the vertices outside K and precisely
those polytope edges whose **entire** segments avoid K. The graph components
are in bijection with the connected/path-connected components of `P minus K`.
The graph is not claimed to recover higher homotopy or every Betti number.

The proof has four parts:

1. **Open convex caps cover the free set.** For any x outside a ball centered
   at c, put u=x-c. The cap `P intersect {u*(y-c)>R*||u||}` contains x and is
   wholly outside K by Cauchy--Schwarz. Every nonempty cap contains a vertex
   of P: a linear functional reaches its maximum at a vertex. Every free
   point thus connects to a free polytope vertex inside such a convex cap.
2. **A cap's vertex graph is connected.** From any non-maximal vertex, an
   increasing edge exists for its linear functional. Following increasing
   edges stays strictly inside the cap and reaches its maximizing face.
   That face has a connected vertex-edge graph. Flat maximizing faces and
   non-simple vertices do not require perturbation.
3. **Two intersecting caps have an edge/vertex bridge.** Write their strict
   affine inequalities as f>0 and g>0. Maximize t over
   `x in P, t<=f(x), t<=g(x)`. The optimum is positive. At an optimal vertex
   of this lifted polyhedron, at most two active inequalities are the new
   t bounds; the remaining active constraints put x on a face of P of
   dimension at most one. Thus the caps intersect a polytope vertex or edge.
   On that edge each cap occupies an interval adjacent to an endpoint.
   They either share a vertex or their overlapping intervals cover the
   whole edge and join free endpoints. That edge avoids K completely.
4. **These bridges prove completeness.** Associate a free point with the graph
   component of any cap containing it. Parts 2--3 make this independent of
   the chosen cap. Unions of caps associated with different graph components
   are disjoint relatively open sets partitioning the free set. Within each
   union, convex-cap paths and graph edges connect every point. No additional
   component can lack a free polytope vertex.

The irrational supporting thresholds above are existential proof tools, not
numerical inputs to the algorithm. All implemented decisions use rational
vertices and exact squared whole-segment distance comparisons. For a free
point x, maximizing `(x-c)*(v-c)` over the cell vertices gives a supporting-root
vertex v: its value is at least `||x-c||^2`. The segment x--v therefore has
nondecreasing squared distance and is independently checkable.

## Global completeness and free boundary patches

Two clipped power cells meet in a common exposed face (`q_i=q_j`), including
degenerate and identical-cell cases. Every component of the free subset of
that face contains a face vertex by the local lemma. Face vertices/edges are
vertices/edges of both cells. Consequently two local free pieces intersect
exactly when their graph components share a free geometric vertex.

Glue identical rational free vertices and all checked free edges. Local free
components form a **finite relatively closed cover** of the physical free set:
cells are closed and their finitely many components are relatively closed.
Intersection-graph gluing therefore proves all global components and their
separations. Omitting a source cell or a lower-dimensional incidence is invalid.

Apply the same argument to the finite cover by cell/domain-face intersections
to recover free patches of the declared domain boundary. Retain free vertices
on a domain face and free edges whose endpoints share that **same** domain
face. An edge connecting different boundary points through the interior must
not merge boundary patches. Each boundary patch has one incident global free
region; one region may meet several patches or none. No biological Mouth label,
area, optimal bottleneck or infinite-exterior interpretation follows by itself.

## Producer/checker separation

The producer clips an exact bounding box successively by the domain/power
halfspaces, retaining full vertex geometry and degeneracies. The box is only a
computational enclosure. It proposes a bounded supporting subset per cell.

The checker independently enumerates **all** feasible independent plane triples
for that subset. All six enclosing box planes must be included. Every resulting
vertex must satisfy **all** original domain and all-atom power inequalities.
Since the subset contains the true cell and is bounded, this proves reverse
containment as well: the subset polytope equals the true cell. An empty bounded
subset proves emptiness; a coincident dominating ball has a direct algebraic
infeasibility witness. Cell/atom coverage is exhaustive and source-bound.

The producer finds edges from shared vertex-active-plane ranks. The checker
instead enumerates independent plane pairs and their common verified vertices.
It recomputes free vertices/whole edges against the original atomic balls and
independently assembles components with disjoint sets, rather than trusting the
producer's graph search or proposed counts. The same independent checks apply
to boundary incidence. Arithmetic, convex/polyhedral lemmas above and the
declared exact enumeration are the trusted base, not a machine-checked proof
of Python or a second copy of an unchecked topology routine.

Region supports are recoverable through source cells, strict sphere exclusion
and vertex-component membership. A free anchor is assigned using the checked
supporting-root segment. Different complete region IDs prove separation;
equal IDs yield a continuous path through checked graph edges. IDs are scoped
to the model/certificate; no cross-probe ordinal identity is assumed.

## First implementation controls and remaining scope

Freeze analytic multi-ball controls before receiving: two transverse ball
barriers with three free regions, their exact-contact `1/3/3` transition,
unequal radii, coincident/identical/dominated cells, lower-dimensional gluing,
and eight corner balls enclosing a tiny central region followed by exact
complete union coverage. Preserve gaps of `2^-80` without float conversion.
Test missing cells/edges, false joins/separations, wrong weights/source units,
corrupt bounds and fresh saved reading without DFND, producer or NumPy.

The [20-profile protocol](../evidence/reference_validator_power_cells_v1/protocol.json)
contains seventeen analytic controls and three **reused saved** original
tetrahedron models from the previous panel archive. Analytic fixture definitions
and assertions were written test-first; the JSON protocol was frozen after
unit prototypes and before retained committed-source receiving. It is not
presented as a blind pre-prototype experiment. Positive original tetrahedron
counts are left unspecified in that protocol: complete counts must come from
the checked construction, not a label or assumed ideal answer.

The two-barrier controls use centers `(+/-8,0,0)`, atomic radii 4 and domain
`[-20,20] x [-3,3] x [-4,4]`. At expanded radius 5 each complete `x=+/-8`
section is covered. Every free point in each of the three open slabs can move
monotonically away from its nearest barrier toward an end section or `x=0`;
these sections are free and connected. This proves three regions. Just below
5, the corner line `(x,3,4)` also joins the slabs, giving one. The same argument
survives the `2^-80` positive/negative perturbations and the unequal 5/6-radius
control. The boundary surface connects around each excluded cross-section,
giving respectively one or three free boundary patches.

For eight centers `(+-1,+-2,+-2)` in their center hull, the nearest-center
squared distance is `(1-|x|)^2+(2-|y|)^2+(2-|z|)^2`, whose maximum is 9 at
the origin. Radius `3-2^-80` leaves a connected central free set: moving each
absolute coordinate toward zero increases every nearest-center distance.
The boundary has maximum nearest-center distance `sqrt(8)<3-2^-80` and is
covered. Radius 3 or larger covers the entire hull exactly. This independently
establishes the `1/0/0` region and `0/0/0` boundary transition.

For the rational regular tetrahedron with vertices `(1,1,1)`, `(1,-1,-1)`,
`(-1,1,-1)`, `(-1,-1,1)`, all centers have squared norm 3. Along a ray from
the origin inside the tetrahedron, the nearest-center squared distance is
`3-2*t*max_i(u*c_i)+t^2*||u||^2`; it decreases up to the hull boundary
because that boundary lies before the nearest-center radial minimum. Hence
every free point connects toward the origin. Edge midpoint distance `sqrt(2)`,
face circumradius `sqrt(8/3)` and origin distance `sqrt(3)` independently give
`(regions,patches)=(1,4),(1,0),(0,0)` at radii `3/2,5/3,7/4`. These statements
refer to these rational controls; the original binary64 tetrahedron is received
and checked as its own exact numerical model.

Then measure small original inputs before expanding. Initial execution is local,
one CPU/thread, finite memory/time/work ceilings and conservative host reserves;
Slurm is not needed in this phase. A budget stop is unresolved, never empty.

This route initially qualifies topology/boundary incidence and anchor claims.
Nonempty per-region volumes still require certified integration (P4); tight
volume bounds are not substituted for topology. No native fix, general release,
protein phase or comparative-superiority claim is inferred from this design.

`docs/content/dfnd/geometry_and_probe.md`, `validation_and_scope.md` and the
worked tetrahedron were reviewed for interpretation. This independent reference
construction changes no native operator, public promotion, probe convention or
Topography classification; no method-book formula needs replacement. The
previous BenchLab panel remains historical source-scoped evidence.

## Complementary tetrahedral reference proposed by the maintainer

Any full-dimensional tetrahedron with vertices v0..v3 has coordinates
`x=v0+u*(v1-v0)+v*(v2-v0)+w*(v3-v0)`, with `u,v,w>=0` and `u+v+w<=1`.
Uniform steps in these barycentric coordinates give a reproducible sampling
inside each tetrahedron; they are not necessarily uniform physical distances
on skew/slender cells. Ordinary Delaunay is a convenient complete hull carrier,
not a requirement for the physical exclusion test.

Every sample must test the probe against **all** source atomic balls, not only
the tetrahedron's vertices. Every proposed link needs a complete all-atom
segment check. Shared-face coordinates must match between neighboring cells;
edge/vertex incidences and strict-contact closure remain explicit. For certified
coverage, classify complete subcells, retain unresolved portions and give valid
volume bounds. Point sampling alone cannot exclude a missed narrow passage or
small component. A complete negative/separation statement requires its own
cover/outer-representation proof, not failed finite exploration.

Reusing DFND's entire tetrahedral mesh can give a useful independent physical
checker while sharing a carrier. Verify that the mesh covers the exact hull
without gaps/overlaps and has matching incidences; do not consume only DFND-
selected features or treat shared triangulation as fully independent evidence.
This is a complementary route under #76, not a replacement of the exact
multi-ball construction or an already delivered second validator.
