# One connected opening at 1.4 Å

The unchanged 66-ball shell has **one connected patch of free probe centers on
its atomic-center convex-hull boundary at probe 1.4 Å**. The origin reaches
that patch along the independently certified +Y ray. This agrees with the one
native exterior-link cluster and its public `Mouth` on parent-ID face [6,7,8].

The observable is explicit: strict all-atom clearance on this declared hull
boundary. It is not an intrinsic biological mouth definition or a validation
of every native graph path. The earlier input, notebooks and observation files
retain their bytes and original, more limited reference scope.

This certificate supplies the one-patch control in the
[physical-boundary acceptance proposal](https://github.com/uibcdf/topomt/blob/main/devguide/DFND/boundary_connectivity_contract.md)
under [#151](https://github.com/uibcdf/topomt/issues/151). Agreement here does
not alone establish a general capability. The bounded source implementation
now supplies one physical patch and a compatible component path on this row,
with wider qualification under #76. Native whole-face clustering retains its
separate meaning, as the tetrahedron demonstrates.

```{figure} artifacts/opening_connectivity_v1/opening_patch.png
:alt: Blocked hull faces and the selected face, with expanded-ball intersections leaving one connected free patch and the origin-ray crossing.

The green triangle is the native carrier face. Its white subset in the planar
view is the free probe-center patch; the rest is blocked by expanded atomic
balls. The star is the certified ray crossing. The picture illustrates the
geometry; the count is verified from witnesses and topology, not pixels.
```

## Evidence that rules out another boundary opening

All explicit atomic radii are 1.7 Å, so a 1.4 Å probe gives expanded obstacle
balls of radius 3.1 Å. Every hull triangle except [6,7,8] has a complete
subdivision cover by these balls, using the same convexity principle as the
[closed-shell wall certificate](../closed_shell/closure_at_0p2.md).

| Verified part | Result |
| --- | --- |
| Other hull faces covered | 127 of the hull's 128 faces |
| Accepted covering triangles | 193, with complete four-way subdivision trees |
| Minimum wall-cover margin | 0.007968988 Å |
| Expanded balls meeting the selected triangle | 14 of the 66 |
| Explicit intersection decisions checked | 181, with no unresolved decision |
| Minimum point-witness or separation margin | 0.027267560 Å |
| Required numerical safety margin | 0.000001 Å |

The other covered hull faces include every edge of the selected triangle.
Consequently, its boundary is blocked and every free hull-boundary patch lies
strictly inside that triangle. The native contact face was already known when
the study began; verifying **every other face** prevents that choice from
silently excluding an additional opening.

## Count the free patches inside the triangle

Intersect the triangle with each expanded atomic ball. These are compact,
convex planar sets. Their intersection pattern defines a nerve complex with
the same homotopy type as their union, by the closed-convex nerve theorem.
[Bauer, Kerber, Roll and Rolle, Theorems 3.1/3.9](https://arxiv.org/pdf/2203.03571v6).

The certificate supplies point witnesses for nonempty intersections and
geometric lower bounds for empty intersections. It checks all 66 single sets,
all 91 pairs among the 14 nonempty sets, and all 24 triples whose pairwise
intersections are nonempty. A triple containing an empty pair is necessarily
empty. The resulting two-skeleton has 14 vertices, 31 edges and 24 triangles.

Only the two-skeleton is needed for first homology. Exact binary linear algebra
gives boundary-two rank 17; the covered union is connected. Thus

$$\beta_1 = 31 - 14 + 1 - 17 = 1.$$

For a compact, locally contractible planar set, complement duality relates this
first Betti number to its bounded complementary components. Here the triangle's
covered boundary separates its interior from the unbounded exterior, so the
one bounded complementary component is exactly the one free patch inside it.
[Hatcher, *Algebraic Topology*, Corollary 3.45, p. 255](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf).

## Why checking does not depend on optimizer success

A positive intersection record gives nonnegative barycentric weights. They
construct a point inside the triangle whose distances to all atoms of that
subset are strictly below 3.1 Å, with the declared safety margin.

A negative record gives nonnegative normalized atom weights, their weighted
center m, and a unit direction n. Define

$$V=\sum_i\lambda_i\lVert a_i-m\rVert^2,\qquad
s=\max\left(0,\min_{v\text{ vertex of }T} n\cdot(v-m)\right).$$

For every x in triangle T,

$$\sum_i\lambda_i\lVert x-a_i\rVert^2
=\lVert x-m\rVert^2+V\ \geq\ s^2+V.$$

If the square root of that lower bound exceeds 3.1 Å, x cannot lie in all of
those balls simultaneously. The verifier checks the weights, direction and
inequality directly; it does not invoke an optimizer. SLSQP only searches for
candidate witnesses during generation. Failure to find a sufficiently separated
witness would leave the decision unresolved rather than supply an empty set.

The retained +Y ray has minimum all-atom clearance **1.819726044 Å**. It crosses
the selected triangle at **(0, 4.770076949, 0) Å**, strictly inside its free
patch. This links the unique boundary opening to the origin-containing region.
Numerical distances use explicit safety margins; this is not formal
interval-arithmetic verification.

## Reproduce the verification and inspect DFND correspondence

Download the {download}`protocol <artifacts/opening_connectivity_v1/protocol.json>`,
{download}`complete certificate <artifacts/opening_connectivity_v1/certificate.json>`,
{download}`independent verification <artifacts/opening_connectivity_v1/verification.json>`,
{download}`actual raw/public correspondence <artifacts/opening_connectivity_v1/native_correspondence.json>`,
{download}`execution receipt <artifacts/opening_connectivity_v1/execution_receipt.json>`
and {download}`standalone figure <artifacts/opening_connectivity_v1/opening_patch.png>`.
From the repository root:

```bash
python devtools/verify_opening_connectivity.py
```

The verifier imports no TopoMT/DFND, runs no detector/optimizer and makes no
provider/server request. It checks complete partitions and intersection
inventories, point/separation witnesses, exact homology rank and the all-atom
ray. Tests reject missing wall pieces, missing decisions and false witnesses;
unit-policy changes, rigid motion and atom permutation preserve the result.

The protocol was frozen at `7f6c0ff` before recorded certificate capture.
Native/public outcomes and preliminary geometric results were already known:
this is retrospective characterization, not a blind evaluation. All 155 earlier
scientific files retain their hashes.

The current `Pocket` has one child `Mouth` on this face, matching the certified
boundary-patch count and localization for this probe. Its **16.148008 Å²**
geometric triangle area is still not a free aperture-area measurement, and its
local gate radius is not newly qualified as an all-atom bottleneck threshold.
Other probes/cases, general graph-path validity, volume accuracy, dry-feature
promotion and neutral public support retain their separate gates. Development
continues within the first three systems before adding another geometry.
