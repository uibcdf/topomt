# Certified face flux: construction and remaining precision gate

Owner [#76](https://github.com/uibcdf/topomt/issues/76), performance stage S4.
This developer prototype supplies conservative bounds on a reconstructed power
partition. The original k=24 request remains unmet. It is not public API or a
qualification of native DFND, general molecular performance or the entire plan.

## Reduction to one expanded ball in each exact cell

Independent topology checking reconstructs every clipped power cell from all
source inequalities. For a cell owned by atom i, `power_i(x) <= power_j(x)`
throughout the cell for every j. Therefore a point in that cell is free of
every expanded ball exactly when it is outside the owner's expanded ball.
This reduction uses the complete power ordering; proximity heuristics do not
justify dropping other atoms. It holds for unequal radii and a center outside
its own clipped cell as well as the equal-radius controls.

Distinct full-dimensional cells have disjoint interiors, except identical
power functions. The latter require the same center and expanded radius;
identical reconstructed polytopes are counted once. A different owner ball on
an identical full-dimensional cell is rejected. Empty and lower-dimensional
cells contribute zero 3D volume while retaining their topology in the original
certificate. Domain boundaries and strict obstacle contact have zero volume;
their topological conventions are unchanged.

## A continuous vector field with zero sphere flux

Let y=x-c, where c is the owner center and R its expanded radius. Define

```text
F(x) = y * (1 - R^3/|y|^3) / 3    for |y| > R
       0                         for |y| <= R.
```

For R>0 this field is continuous at the sphere, has divergence one outside
and zero inside, and has zero flux on the spherical boundary. Indeed
`div(y)=3` and `div(y/|y|^3)=0` away from the center. For R=0 use F=y/3,
including its continuous value at the center; the excluded point has zero
3D measure. Applying the divergence theorem to a convex polytope yields
its free volume as a sum of flux through its planar facets.

For an outward-oriented triangle (a,b,d), put

```text
C = det(a-c, b-c, d-c) / 6
w(r) = max(0, 1 - R^3/r^3).
```

Its flux is C times the area-average of w(|x-c|) on the triangle. This is
because `(x-c).n` is constant on a planar face, while the oriented area vector
is `(b-a) cross (d-a) / 2`. C is rational and signed. Faces through the center
have C=0 and contribute exactly zero. Negative C is required when the center
lies outside its cell; replacing signed contributions by absolute values is
incorrect. Internal power faces are integrated for each cell with that cell's
field; the fields differ, so their fluxes must not be canceled automatically.

## Complete boundary subdivision and conservative local bounds

The checker rebuilds the outward facet cycles from the already verified exact
vertices and supporting planes, and triangulates each polygon as a complete
fan. Every nonzero triangle receives a stable root index. Four-child midpoint
subdivision preserves orientation and covers a parent with disjoint interiors.
The certificate contains root/path pairs, not trusted numerical totals or
producer-selected face lists. The checker rejects omitted roots/children,
overlapping ancestors, duplicates, invalid order and excessive depth/work.
Current limits are 4096 triangles, depth 12 and 64/128/256/512 dyadic bits.

For each triangle, an axis-aligned enclosure supplies a rational lower bound
on squared distance from c. Convexity supplies the maximum squared distance
at a vertex. Monotonicity of w turns those distance bounds into bounds on its
area-average. Dyadic square roots round outward, with rational division;
when the denominator cannot be certified positive the weight remains [0,1].
No unresolved cut is classified by its centroid.

Before long reductions, a nonexact flux interval is rounded outward to a common
dyadic grid in canonical nm**3. Each rounding adds less than `2^-bits` at
each endpoint; this error remains in the emitted bounds. Exact contributions
are preserved exactly, including zero-radius/full-domain controls. This avoids
the huge rational least-common-multiple growth observed in the unrounded pilot.
It does not remove geometric uncertainty. Increasing bits alone cannot cure
loose face-distance bounds.

## Region assignment and signed uncertainty

If complete topology has one region, all free contributions belong to it.
With multiple regions, a whole triangle strictly outside its owner ball is
free of every atom by the power ordering. It is convex and connected; a
checked supporting-root query of its centroid assigns its entire flux to
one region. The centroid identifies this already proved connected subset.

Otherwise a cut triangle can carry pieces of several regions. For an interval
[l,u] with constant flux sign, each candidate region receives
`[min(0,l), max(0,u)]`. This includes any fraction of the triangle's flux;
negative ambiguity must lower candidate bounds rather than disappear.
The total receives [l,u] once. Summing candidate upper bounds is not the total.
Final enclosures intersect the known nonnegative/domain-volume constraints.
Topology, available boundary patches and region identity come from the complete
proof; small or zero current lower bounds never discard a positive region.

## Evidence, trusted base and next construction

The source producer chooses refinement priorities; the independent reader
reconstructs coverage and recomputes every bound. Both share exact convex-face
ordering, rational predicates and bounded interval primitives as an explicit
trusted base. This is not a machine-checked proof or an independent second
implementation of those primitives. Fresh saved checking imports no producer,
native DFND or scientific floating-point dependency.

Controls cover a contained ball, an unequal-radius pair with signed faces,
eight-region/duplicate-obstacle geometry, full/empty/zero-radius volume,
missing coverage and process-equivalent partitions. They do not constitute an
exhaustive independent audit of arbitrary clipped cells or every degeneracy.
The original tetrahedron 1.4 Å pilot preserves its Model and original absolute
and relative k=24 request. At 4095 retained triangles the request is still
unresolved. See [performance evidence](../evidence/reference_validator_performance_v1/README.md).

The next S4 task is a tighter certified face integral, for example exact
sphere/face cut pieces and bounded higher-order integration away from cuts,
with independently derived analytic/tiny/asymmetric controls. The current
range enclosure is a correct conservative prototype, not a demonstrated
high-precision solution. Retain finite feasibility experiments and do not
replace this gate by automatic grid growth or more workers. S5--S8 production
qualification keeps its serial precision prerequisites.
