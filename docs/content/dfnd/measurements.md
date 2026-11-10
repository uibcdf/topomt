# Measurements and their numerical meaning

Before comparing two values, identify the measured set. A volume of carrier
cells, a volume of bare empty space and a volume of admissible probe centers can
all be correct answers to different questions.

## Supports and definitions

For a declared finite carrier union $R$, bare empty volume is

$$V_{\rm empty}(R)=\int_R\mathbf1[c_{\rm all}(x)>0]\,dx.$$

Probe-center volume instead uses $\mathbf1[c_{\rm all}(x)>p]$. Exterior-accessible
center volume further restricts to an exterior-reachable subset. Swept probe
volume measures a union of occupied probe balls. These distinctions survive
even if some boundaries have zero measure for volume: they remain crucial for
connectivity and interpretation.

| Current quantity/operation | Measured support/model |
| --- | --- |
| `volume_topological_resident` | Sum of complete resident tetrahedron volumes. |
| Transit carrier volume | Sum over resident cells and selected connectors. |
| `volume_solvent_estimate` | Deterministic barycentric estimate of bare empty volume against each cell's four vertex balls, aggregated over resident support. |
| `DFNDData.solvent_volume(..., region='resident')` | On-demand bare empty volume over resident carrier support, including nonlocal balls that can reach it. |
| `region='transit'` in that operation | Same exclusion definition over resident plus connector support. |
| `occupancy_grid` | A grid representation of empty sample locations within the declared carrier support, not a solvent occupancy probability. |

Current on-demand empty-volume evaluation uses original atomic radii, not radii
expanded by the query probe. The probe selects the carrier region; that does not
make its empty-volume integral equal to probe-center-accessible volume.

## Fast local estimation

The bulk pass fixes resolution 8. It enumerates four nonnegative integers
$i_0+\cdots+i_3=8$ and samples barycentric weights
$w_j=(i_j+0.5)/10$, giving a stencil of **165 interior points** per cell. The
estimate is the complete cell volume times the fraction outside its four vertex
balls, with epsilon included in that exclusion decision. The half-step shift
avoids sampling directly on vertex atoms. This resolution is an internal fixed
choice, not a public query control. Cells at or below the current numeric volume
cutoff return zero samples; records retain the actual count rather than
guaranteeing 165 evaluations for every cell.
It avoids statistical randomness but still has discretization error.
Testing the four vertex balls can miss nonlocal intruders. Resident-only
aggregation excludes connector support, intentionally keeping the two roles
separate.

Past-beach descriptors add neighboring dry-coast estimates to the resident
estimate, producing the compatibility `volume_solvent_accessible` field. This
is an additive contact-related proxy. It does not reconstruct the actually
swept region or certify an exact globally accessible volume. Its atom extension
likewise does not prove contact by a particular ligand.

## On-demand evaluations

The Monte Carlo route draws an IID uniform mixture over disjoint-interior
carrier cells, with cell probabilities proportional to volume, then checks all
relevant balls. If the carrier volume is $V_R$ and $K$ of $N$ points are empty,
$\hat V=V_R K/N$. Its **95% Clopper–Pearson interval** is the binomial
proportion interval multiplied by $V_R$. The compatibility scalar `error` is
the larger distance from $\hat V$ to either endpoint. It therefore encloses
the asymmetric interval around the estimate; it is not a standard deviation.
The interval method follows {cite:t}`DFNDClopperPearson1934`.

Sampled $K=0$ or $K=N$ still gives positive uncertainty. Zero sampling error
is reserved for separately established geometric cases: zero-volume support,
no positive-radius ball reaching the carrier bounding box, or one ball covering
all vertices of each carrier cell. A fixed seed makes the run repeatable; a
confidence interval describes repeated sampling, not the probability that a
fixed unknown volume lies in one already observed interval. It excludes physical
model error and errors in selecting the carrier or its accessible subset.
Distance temporaries are batched, with at most 262,144 point/atom pairs each.

`method='quadrature'` performs bounded successive Gauss-order doubling. Two
consecutive differences must meet `absolute_tolerance + relative_tolerance *
carrier_volume`. The reported error is the larger of those two differences:
**a convergence diagnostic, not a rigorous integration bound**. A record keeps
all evaluated orders/values. An exhausted order/work ceiling is `unresolved`,
with unknown error; if no order could run, the estimate is also unavailable.
The work ceiling is the declared sum of $K q^2\max(1,A)$ across orders, for
$K$ cells, order $q$ and $A$ obstacle balls. It is a budget proxy, not wall time.

Legacy `method='exact'` preserves the fixed-order numerical result and
`(volume, None)`. Exact interval union along a line handles overlapping balls;
the surrounding two-dimensional quadrature still has unknown error. This
compatibility name does not establish exact integration. The new refinement
route is available when a convergence history is needed.

For detailed inspection use `DFNDData.solvent_volume_measurement`. Its
`dfnd.volume_measurement.v1` dictionary retains quantity-valued volume,
interval/error, method, status, sample/order evidence, finite carrier support,
source correspondence and attribution. `observable='carrier'`, `'bare_empty'`
and `'probe_center'` select distinct integrals on the same declared support.
The last expands excluding radii by this query's probe and gathers nonlocal
balls using that expansion. It does not restrict the integral to an
exterior-reachable subset. The shorter `solvent_volume` tuple route continues
to measure bare empty volume.

```python
component_id = next(c.component_id for c in topography.dfnd.dfn.components.values()
                    if c.side == 'wet')
measurement = topography.dfnd.solvent_volume_measurement(
    component_id, observable='bare_empty', n_samples=40000, seed=0)
print(measurement['volume'], measurement['interval'], measurement['status'])
```

Use the selected method's status before interpreting its error. Software
maturity describes the metric's meaning; it does not certify a particular
numerical error, every release or biological accuracy. The frozen three-case
volume protocol and scoped qualification remain owned by
[#75](https://github.com/uibcdf/topomt/issues/75) and
[#76](https://github.com/uibcdf/topomt/issues/76).

## Areas, radii and depth

`Mouth.area` and native `area_geometric` refer to complete carrier triangles.
Free aperture area would integrate over a clipped free patch on a declared
surface, with its own geometric and accuracy contract.

`R_gate_min/mean/max` summarize local face capacities in a link. The minimum
along a selected skeleton is conditional to that route; it is not automatically
the maximum achievable bottleneck among all physical paths. Graph depth counts
edges and has no length unit.

## Centers and placement

For component transit cells $T$ with volumes $v_T$ and vertex barycenters $b_T$,
the public `feature.center` is the carrier centroid

$$\bar x=\frac{\sum_T v_T b_T}{\sum_T v_T}.$$

The sum includes selected connectors, not just resident cells, and uses complete
tetrahedra without atomic exclusion. If the total carrier volume is zero, the
implementation falls back to the unweighted mean of their barycenters.

This averaging is distinct from the optimized residence center stored for each
cell and used by PCA. It supplies a geometric summary, not a guaranteed free
placement point, maximum-clearance location or skeleton station. In a nonconvex
region a centroid need not even lie inside the carrier union. The single-cell
tetrahedron has coincident centers, so use the
[many-cell recovery example](network_and_decomposition.md#advanced-inspection-a-many-cell-center)
to inspect the general definition.

## Units and comparison

Raw DFND geometry uses nm, areas nm² and volumes nm³ in its explicit schema.
Public primary quantities use PyUnitWizard. Convert before presenting angstrom
values: a numerical volume changes by a factor of 1000 between nm³ and Å³.
Nested compatibility dictionaries can retain native bare numbers; inspect their
declared schema rather than assuming every public nested value is a quantity.

A fair comparison states carrier/support, selected atoms/radii, probe, exclusion
model, estimator, resolution and uncertainty. Equal attribute names across
providers do not establish equal geometric definitions.
