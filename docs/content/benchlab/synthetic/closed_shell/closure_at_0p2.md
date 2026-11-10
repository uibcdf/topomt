# A stronger enclosure reference at 0.2 Å

The original system notebook's conservative whole-face bound was inconclusive
at **0.2 Å**. A new independent certificate now establishes that the **same
frozen 72-ball wall encloses the free origin at this probe**. The old bounds,
notebook outputs and native observations retain their original bytes and scope.
This is retrospective reference strengthening: the earlier native `void` label
was already known, so this is not a blind evaluation.

This complete cover supplies the zero-patch control in the
[physical-boundary acceptance proposal](https://github.com/uibcdf/topomt/blob/main/devguide/DFND/boundary_connectivity_contract.md)
under [#151](https://github.com/uibcdf/topomt/issues/151). The bounded source
implementation now resolves zero global hull patches at this probe, alongside
actual public receiving. The independent reference is unchanged; it does not
become a production input. Wider geometry/path qualification remains #76.

## Why the certificate proves enclosure

Expand every explicit atomic radius by the 0.2 Å probe. Subdivide each original
convex-hull triangle into four midpoint triangles as needed. Accept a small
triangle only if one expanded atomic ball contains all three vertices with a
strict **1e-6 Å** safety margin.

A ball is convex. If its three vertices belong to that ball, their entire
triangle belongs to it. A complete subdivision cover of every hull face is
therefore a covered wall. The origin is strictly inside that hull and has
positive all-atom clearance after probe expansion. Any continuous free path
from it to infinity would have to cross the blocked wall, so the origin's free
probe-center component is bounded.

| Verified quantity | Result |
| --- | --- |
| Original hull faces | 140 |
| Covered leaf triangles | 1037 |
| Maximum subdivision depth | 5; declared limit 8 |
| Visited tree nodes | 1336; declared limit 20000 |
| Minimum expanded-ball vertex safety margin | 0.000051742 Å, above the 0.000001 Å requirement |
| Origin free-space margin after probe expansion | 3.968062464 Å |
| Unresolved or missing pieces | None |

The verifier checks both every distance inequality and complete, prefix-free
four-way trees for every original face. A missing leaf or an incorrect covering
atom is rejected. A sum of triangle areas alone would not exclude overlapping
pieces and is not the completeness check used here.

```{figure} artifacts/wall_certificate_v1/wall_cover.png
:alt: Complete subdivided hull cover and one original face, colored by positive expanded-ball vertex safety margin.

The colored triangles constitute an independent wall-cover certificate, not
DFND regions or a molecular surface reconstruction. The right panel shows the
subdivision of the face with the largest old circumcover bound.
```

## Evidence and independent verification

Download the {download}`protocol <artifacts/wall_certificate_v1/protocol.json>`,
{download}`reconstructable certificate <artifacts/wall_certificate_v1/certificate.json>`,
{download}`verification summary <artifacts/wall_certificate_v1/verification.json>`
and {download}`standalone figure <artifacts/wall_certificate_v1/wall_cover.png>`.
From the repository root run:

```bash
python devtools/verify_closed_shell_wall_cover.py
```

This tool uses the frozen coordinates/radii, PyUnitWizard, NumPy and SciPy;
it never imports or calls DFND. It reconstructs every leaf from the original
face and its ordered subdivision path, verifies the covering atom and input/
protocol identity, and checks hull containment and origin freedom. Explicit
quantities are checked under both nm/ps and pm/fs session policies. The numerical
certificate has the stated floating-point safety margin; it is not a formal
interval-arithmetic proof.

At 0.2 Å the actual public route produces one `Void` and no `Mouth`, consistent
with this enclosure reference. The [public receiving record](topography.md)
retains that additional control. This establishes the origin enclosure, not an
exact global cavity count, volume or validity of all graph paths. Broader
independent references remain under [#76](https://github.com/uibcdf/topomt/issues/76).
