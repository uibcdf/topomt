# Four openings on the tetrahedron boundary

At probe radius **1.2 Å**, the frozen tetrahedron has **four separate free
patches on its hull boundary**. Each patch has a collision-free straight path
from the center. The six shared edges are blocked, so the patches cannot join
on that boundary. This gives a precise geometric reference for studying what
DFND's exterior groups and public objects represent.

The current native result groups the four admitted faces into **one exterior
link**, classifies the resident component as `percolating`, and creates one
public `Percolating` with **no `Mouth` children**. This follows the current
discrete contract. It does not mean that the four physical boundary patches
are connected, or that every point of the hull boundary is free.

| Same frozen input | Independent boundary result | Current native/public result |
| --- | --- | --- |
| Probe 1.2 Å | Four disconnected patches; all four connect to the free center. | One face cluster; one `Percolating`; no `Mouth` children. |
| Probe 1.4 Å | Entire boundary covered; center remains free. | One `Void`; no exterior link or `Mouth`. |
| Probe 1.7 Å | No free probe center anywhere in the finite hull. | No resident wet component; substrate remains. |

```{figure} artifacts/boundary_connectivity_v1/boundary_patches.png
:alt: Unfolded tetrahedron with four separate free patches surrounded by excluded regions and blocked shared edges, plus a detailed face view.

The same hull unfolded into four triangles. Colors distinguish the free
probe-center patches. A point marks the central ray's crossing on the detailed
face. The retained witnesses establish the count; the plotted grid illustrates it.
```

## Why there are four patches

The input still has edge length 5.3 Å and four atomic balls of radius 1.7 Å.
For the 1.2 Å probe, excluded centers lie in closed expanded balls of radius
2.9 Å. Every edge is covered by its two endpoint balls: every edge point is
within half the edge, 2.65 Å, of an endpoint. The coverage margin is **0.25 Å**.

On each triangular face, intersect all four expanded balls with that face.
The three vertex balls have nonempty single and pair intersections; their
triple intersection is empty because the face circumradius, 3.059956427 Å,
exceeds 2.9 Å. The opposite atom's ball misses the face. These decisions are
verified directly, rather than inferred from symmetry or a rendered image:

- Positive intersections have barycentric point witnesses inside the triangle.
- Negative intersections have convex-weight and separating-direction lower
  bounds on the distance needed to satisfy the selected balls simultaneously.
- The complete required inventory has eight decisions per face, 32 in total.
  Its smallest decision margin is **0.159956427 Å**, exceeding the declared
  0.000001 Å requirement.

The resulting nerve on each face has three vertices, three edges, no triangles
and first Betti number one. The [closed-convex nerve theorem](https://arxiv.org/pdf/2203.03571v6)
identifies this with the first homology of the covered union: all nonempty
intersections are compact convex sets. [Planar complement duality](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf)
then counts one bounded complementary component. The triangle boundary is
covered, so exactly one free component lies inside the face. Covered shared
edges separate the four face interiors on the hull, giving **four** patches.
These theorems supply the topological step; the certificate checks this input's
geometric hypotheses with numerical margins, without formal interval arithmetic.

Four rays from the atomic centroid through the face centroids have minimum
all-atom clearance **1.359956427 Å**. Each ray crosses its face interior and
continues to infinity without collision. Thus all four separate boundary
patches connect to the same free central region and to the exterior. Separate
patches on a boundary need not be separate components of free space.

For the other probes, a convex-combination squared-distance bound covers every
face at 1.4 Å with minimum margin **0.040043573 Å**, while the centroid clearance
is **1.545573909 Å**. The analogous bound over the whole finite hull excludes
all free centers at 1.7 Å with margin **0.154426091 Å**. These are sufficient
controls, not newly fitted transition thresholds.

## What this means for DFND

Native exterior grouping joins admitted whole faces sharing an atomic edge.
Here that merges all four faces, even though the shared edges are blocked to
probe centers. Similarly, zero native wall faces means that every carrier face
passes the native permeability predicate; it does not prove a fully free
boundary. The classifier's `percolating` override and the public bridge preserve
these native semantics.

[Issue #151](https://github.com/uibcdf/topomt/issues/151) owns physical boundary
refinement and its relation to `Mouth` and `Percolating`. That work remains
open. Renaming this case `Channel` alone would not resolve the geometric
question. The four-patch reference, the opened shell's
[one-patch certificate](../shell_with_opening/opening_connectivity.md) and the
[covered shell boundary](../closed_shell/closure_at_0p2.md) provide controls for
the next bounded implementation decision.

This observable depends on the declared atomic-center hull. It does not define
an intrinsic biological mouth, free aperture area, general native graph paths,
exact solvent volume or detector accuracy on proteins. It neither validates
all current family names nor invalidates the independently justified sealed
and excluded controls.

## Evidence and replay

Protocol commit `c85549f` precedes formal capture. Existing native outcomes and
analytic formulas were already known: this is retrospective characterization,
not a blind evaluation. All **161** earlier scientific files retain their
protocol hashes; notebooks and original reports remain historical evidence.
No DFND runtime, classifier, public API or input-model change is made here.

Download the {download}`protocol <artifacts/boundary_connectivity_v1/protocol.json>`,
{download}`complete witnesses <artifacts/boundary_connectivity_v1/certificate.json>`,
{download}`independent verification <artifacts/boundary_connectivity_v1/verification.json>`,
{download}`actual native/public correspondence <artifacts/boundary_connectivity_v1/native_correspondence.json>`
and {download}`source/resource receipt <artifacts/boundary_connectivity_v1/execution_receipt.json>`.
The {download}`standalone figure <artifacts/boundary_connectivity_v1/boundary_patches.png>`
is also available.

From the repository root, replay the independent checker with:

```bash
python devtools/verify_tetrahedron_boundary.py
```

It imports no TopoMT detector and runs no optimizer or external service. It
reuses the explicit-unit convex-intersection verifier from the shell study.
Tests reject incomplete inventories and false witnesses, check alternate unit
policies and a translated/rotated/permuted input, and exercise the real public
route. The prior shell verification is reproduced unchanged. Source-workspace
Python 3.14 evidence remains separate from installed-package and support-matrix
qualification. Volume, broader reference and general public-support gates remain
under #75, #76 and #60 respectively.
