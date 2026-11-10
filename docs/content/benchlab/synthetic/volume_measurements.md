# Three volumes on the same finite support

The carrier, the space outside original atomic balls and the space available
to a probe center answer different questions. The new study measures each
explicitly, retains its support and checks the numerical result independently.

```{figure} figures/volume_definitions_v1.png
:alt: Three panels compare carrier, bare empty and probe-center volumes, with native confidence intervals and independent reference bounds.
:width: 100%

Each panel uses one fixed resident carrier. Native Monte Carlo intervals have
95% confidence; independent Cartesian bounds have 99.9% confidence. Different
panels use different systems, probes and vertical scales. Their values are
neither detection scores nor a comparative performance ranking.
```

## What is measured

| Integral | Domain | Excluding balls |
| --- | --- | --- |
| Carrier volume | Selected complete tetrahedra | None |
| Bare empty volume | The same carrier | Original atomic radii |
| Probe-center volume | The same carrier | Every relevant radius plus the query probe |

`resident` uses resident cells; `transit` additionally includes connector cells.
None of these integrals alone reconstructs the globally exterior-reachable or
swept-probe volume. The fast bulk `volume_solvent_estimate` remains a different,
provisional four-local-ball stencil.

| Case / probe | Support | Carrier (Å³) | Bare empty estimate (Å³) | Probe-center estimate (Å³) |
| --- | --- | ---: | ---: | ---: |
| Tetrahedron, 1.2 Å | Resident = transit | 17.5453 | 13.9775 | 0.9137 |
| Tetrahedron, 1.4 Å | Same support | 17.5453 | 13.9775 | 0.0504 |
| Closed shell, 0.2 Å | Resident, 95 cells | 750.5379 | 413.8654 | 347.5929 |
| Closed shell, 0.2 Å | Resident + 3 connectors | 755.1011 | 412.3607 | 346.9312 |
| Shell with opening, 1.4 Å | Resident = transit, 35 cells | 589.1068 | 414.6870 | 121.1204 |

These are point estimates; the downloadable records retain their intervals.
For example the closed-shell bare intervals are **[410.20, 417.53] Å³** and
**[408.66, 416.05] Å³**. The larger carrier has a slightly smaller sampled
estimate, within the overlapping uncertainties. Independent random allocations
need not preserve the exact ordering of two true nested volumes.

## Independent checks and achieved precision

For the bare tetrahedron all six edges equal 5.3 Å, all radii equal 1.7 Å,
vertex balls do not overlap, and none reaches its opposite face. The solid
angle at each vertex is $\Omega=3\arccos(1/3)-\pi$. Subtracting the four
untruncated sectors gives **13.9340345 Å³**. Bounded quadrature gives
**13.9341380 Å³**, an absolute error about **0.0001035 Å³**, below the
predeclared $10^{-4}$ carrier-volume target. Expanded balls overlap; their
volume is evaluated as a union rather than by subtracting independent sectors.

A second integrator draws **524,288 Cartesian bounding-box points** for each
distinct frozen domain/probe. Direct simplex membership and all-atom exclusion
are independent of the production simplex sampler and interval calculation.
Hoeffding bounds use **99.9% per-observable confidence**. All eight declared
support/probe rows meet the predeclared bound-width and overlap criteria;
identical resident/transit domains reuse the same independent reference.
Reference half-widths are 0.56–0.81% of carrier volume, below the 2.5% target.
This is conditional statistical evidence, not a deterministic integration proof.

That target is relative to the carrier. At tetrahedron 1.4 Å the independent
probe-center interval is **[0, 0.1932] Å³**, broad relative to the small free
volume. It does not establish high relative precision for that small remainder.
The native 95% interval is **[0.0417, 0.0605] Å³**. The independent geometric
free-origin certificate separately establishes positive enclosed free space.

The prescribed 128-seed analytic control has **125 covering intervals** at
nominal 95% confidence. The exact finite-binomial coverage guards, sampled
endpoint regressions and two quadrature controls also pass. This calibrates
the stated controls rather than every geometry or random seed.

## Removing the cap on a common domain

Comparing the two natural carrier hulls would also change the domain. A separate
paired experiment therefore keeps the **parent hull**, 839.8751 Å³, for both
unchanged-radii atom unions and uses identical Cartesian points.

| Freed space after deleting the cap | Estimate (Å³) | 99.9% conditional interval (Å³) |
| --- | ---: | --- |
| Bare empty | 29.8545 | [25.2443, 34.4646] |
| Centers of a 1.4 Å probe | 9.9123 | [5.3021, 14.5225] |

Every paired freed-space indicator is zero or one: removing balls cannot
decrease free space on that same domain. These gains are not a comparison of
the different native component carriers or an exterior-accessible-volume claim.

## Public inspection and retained evidence

Use `topography.dfnd.solvent_volume_measurement(component_id, ...)` to inspect
the observable, carrier/source mapping, quantities, uncertainty kind, status,
sample/order evidence and attribution. The shorter `solvent_volume` tuple route
continues to measure bare empty volume. See the
[method chapter](../../dfnd/measurements.md) for the interval and compatibility
`exact`/bounded-quadrature contracts.

| Case | Frozen domain protocol | Independent integration | Actual public measurement |
| --- | --- | --- | --- |
| Tetrahedron | {download}`protocol <regular_tetrahedron/artifacts/volume_study_v1/protocol.json>` | {download}`reference <regular_tetrahedron/artifacts/volume_study_v1/independent_reference.json>` | {download}`receiving <regular_tetrahedron/artifacts/volume_study_v1/native_receiving.json>` |
| Closed shell | {download}`protocol <closed_shell/artifacts/volume_study_v1/protocol.json>` | {download}`reference <closed_shell/artifacts/volume_study_v1/independent_reference.json>` | {download}`receiving <closed_shell/artifacts/volume_study_v1/native_receiving.json>` |
| Shell with opening | {download}`protocol <shell_with_opening/artifacts/volume_study_v1/protocol.json>` | {download}`reference <shell_with_opening/artifacts/volume_study_v1/independent_reference.json>` | {download}`receiving <shell_with_opening/artifacts/volume_study_v1/native_receiving.json>` |

The common-domain {download}`protocol <shell_with_opening/artifacts/volume_study_v1/common_parent_protocol.json>`
and {download}`paired reference <shell_with_opening/artifacts/volume_study_v1/common_parent_reference.json>`
retain their separate input/domain identity. The
{download}`predeclared seed/quadrature receiving <../../../../devguide/evidence/volume_precision_sampling_v1.json>`
contains analytic hypotheses, numerical errors and attribution.

Production precision changed at `b7b5a60`; actual public receiving uses `e7f4f41`.
Independent domain integration uses `6f39143`, and paired cap comparison
`d7aad00`. The independent processes import no TopoMT module or production
sample/estimate. All runs use one CPU/thread with declared time/memory ceilings;
reference peak RSS is below 90 MiB and public receiving below 320 MiB.
These source-bound observations retain [#75](https://github.com/uibcdf/topomt/issues/75)
as their numerical-contract owner; wider support/path/geometry acceptance stays
[#76](https://github.com/uibcdf/topomt/issues/76), with no installed or biological claim.
