# Thirteen openings in the sampled wall

At **0.05 Å**, the unchanged 72-ball shell admits **13 connected free patches
on its atomic-center hull**. Each patch has an independently verified path
from the original origin, followed by a collision-free continuation to infinity.
They provide access to the same origin-containing volume; this is **not a
count of thirteen volumetric channels** or an exact census of interior cavities.

## Why counting faces is insufficient

There are 18 free regions on 17 hull faces. Five free edge intervals join
regions on neighboring faces, leaving thirteen connected hull patches. One
face, with source atoms **[18, 31, 39]**, contains two disconnected openings.
Neither of these two regions touches a free hull edge.

```{figure} artifacts/small_probe_boundary_v2/two_face_regions.png
:alt: Whole hull face and two enlarged views showing separate free probe-center regions between expanded atomic balls.
:width: 100%

The gray section is excluded by the 1.75 Å expanded balls; blue marks allowed
probe centers inside the carrier triangle. Stars identify independently checked
free points. The enlargements reveal two distinct regions. The certificate,
rather than the plotted resolution or the number of stars, establishes the count.
```

The reference counts free face regions from the complete convex-intersection
nerve, with compact exterior pieces to handle free triangle edges. Covered
cycles and winding signatures distinguish regions within a face. Every free
edge interval has a checked inward connection on both sides. The resulting
graph uses **face regions** as nodes. All hull vertices are excluded by their
own atomic balls. This gives a complete boundary count for this fixed model.

Every origin-to-patch segment and infinite outward-normal ray is checked against
all expanded balls. The smallest segment safety margin is approximately
**0.0009524 Å**, above the declared **1e-6 Å** requirement. Such narrow margins
make the full-precision quantity-aware input essential; a rounded PDB is a
different geometric model.

## What actual DFND returns

| Observable | Independent reference | Actual raw / public DFND |
| --- | --- | --- |
| Connected free hull patches | 13 | 13, resolved physical boundary view |
| Free regions on individual faces | 18 on 17 faces | All 140 source-face region counts agree |
| Patches with common-origin access | 13, whole segment and outward ray | All 13 have supported component associations |
| Native exterior-link clusters | Different definition | 10 retained clusters |
| Catalog result and children | Not prescribed by this reference | Central `Channel`, 10 native `Mouth` children |

Physical observations are recoverable through raw `boundary_connectivity` and
the typed DFN view. Public region boundary records expose `physical_openings`,
with patch identities and separate association availability. Native link
grouping and `Mouth` promotion retain their compatibility meaning. See the
[boundary chapter](../../../dfnd/exterior_and_boundaries.md) for support, units,
budgets and unresolved outcomes.

## Evidence and limits

The independent capture uses source `3720b19` and imports no TopoMT module.
Actual-public receiving uses source `e1af4ef`; production physical geometry is
unchanged since `4fc2353`. These are source-bound observations, not qualification
of every installed release, a held-out benchmark or evidence of superiority.
The candidate count was known before the independent reference was developed.

Download the {download}`protocol <artifacts/small_probe_boundary_v2/protocol.json>`,
{download}`complete certificate <artifacts/small_probe_boundary_v2/certificate.json>`,
{download}`independent verification <artifacts/small_probe_boundary_v2/verification.json>`,
{download}`capture receipt <artifacts/small_probe_boundary_v2/capture_receipt.json>`,
{download}`native receiving protocol <artifacts/small_probe_boundary_v2/native_receiving_protocol.json>`
and {download}`actual native/public observations <artifacts/small_probe_boundary_v2/native_receiving.json>`.
The earlier {download}`v1 unsupported receipt <artifacts/small_probe_boundary_v1/unsupported_receipt.json>`
is preserved: its one-region-per-face restriction correctly refused a global
count. It was a reference limitation, not a DFND failure.

The maintained derivation and repository-root replay use
`devguide/DFND/small_probe_boundary_reference.md` and
`devtools/verify_small_probe_regions.py`. Witness discovery may fail within its
budget; verifier acceptance requires complete inventories and checked margins.
These are floating-point certificates, rather than formal interval proofs.

An exact aperture area, maximum bottleneck, every possible curved interior path
and a global cavity count remain unavailable. Wider qualification is owned by
[#76](https://github.com/uibcdf/topomt/issues/76); volume precision has its
separate owner [#75](https://github.com/uibcdf/topomt/issues/75).
