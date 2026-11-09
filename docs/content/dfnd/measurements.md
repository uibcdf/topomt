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

The bulk pass uses deterministic barycentric sampling with its recorded local
resolution. It avoids statistical randomness but still has discretization error.
Testing the four vertex balls can miss nonlocal intruders. Resident-only
aggregation excludes connector support, intentionally keeping the two roles
separate.

Past-beach descriptors add neighboring dry-coast estimates to the resident
estimate, producing the compatibility `volume_solvent_accessible` field. This
is an additive contact-related proxy. It does not reconstruct the actually
swept region or certify an exact globally accessible volume. Its atom extension
likewise does not prove contact by a particular ligand.

## On-demand evaluations

The Monte Carlo route spreads samples over carrier cells in proportion to cell
volume and checks the relevant atom balls. A fixed seed supplies reproducibility.
Its reported error is approximately two estimated standard errors, not a
deterministic error bound. In particular, all-hit or no-hit samples can produce
zero estimated error without proving the true volume exact.

If the carrier has volume $V_R$, $N$ samples are drawn and $K$ are empty,
the current estimate and reported half-width are

$$\hat f=K/N,\qquad \hat V=V_R\hat f,\qquad
e_{\rm MC}=2V_R\sqrt{\hat f(1-\hat f)/N}.$$

The last expression explains the endpoint problem: $K=0$ or $K=N$ sets it to
zero regardless of whether unobserved small empty or occupied subsets remain.
It also explains why changing the carrier changes both the target integral and
the scaling of its sampling error.

The compatibility `method='exact'` route performs nested numerical quadrature
with a fixed order. Union of covered intervals handles overlaps along an
integration line, but exact interval union does not make the surrounding
quadrature exact. A returned `None` uncertainty means no statistical error
estimate is supplied, not zero integration error.

These accuracy/uncertainty questions remain tracked under
[#75](https://github.com/uibcdf/topomt/issues/75). Increase resolution only within
an explicit convergence/error protocol; a visually stable result is not a
publication-grade bound.

## Areas, radii and depth

`Mouth.area` and native `area_geometric` refer to complete carrier triangles.
Free aperture area would integrate over a clipped free patch on a declared
surface, with its own geometric and accuracy contract.

`R_gate_min/mean/max` summarize local face capacities in a link. The minimum
along a selected skeleton is conditional to that route; it is not automatically
the maximum achievable bottleneck among all physical paths. Graph depth counts
edges and has no length unit.

## Units and comparison

Raw DFND geometry uses nm, areas nm² and volumes nm³ in its explicit schema.
Public primary quantities use PyUnitWizard. Convert before presenting angstrom
values: a numerical volume changes by a factor of 1000 between nm³ and Å³.
Nested compatibility dictionaries can retain native bare numbers; inspect their
declared schema rather than assuming every public nested value is a quantity.

A fair comparison states carrier/support, selected atoms/radii, probe, exclusion
model, estimator, resolution and uncertainty. Equal attribute names across
providers do not establish equal geometric definitions.
