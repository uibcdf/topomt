# CASTp 1.0 Metric Parity Checkpoint

Date: 2026-04-21

## Scope

The current CASTp 1.0 native parity is structural:

- `iT`
- `iF`
- `rF`
- `iE`
- `rE`
- `iV`
- `rV`

The structural matrix is green for the current local MKALF oracle battery, but
that does not imply metric parity for all CASTp-family outputs.

This checkpoint separates the metric contracts before implementation continues.

## Metric layers in the historical source

The CASTp 1.0 source has at least two distinct metric layers.

### 1. MKALF pocket metric signatures

Source:

- `sig/poc-metric.c`
- `sig/poc-comb.c`
- `mkalf/calc.c`

These signatures are driven by `alf_pocket_sequence(alpha_rank, max_rank, ...)`.

Important behaviors:

- `psig_volume` increments on `ALF_POC_TETRA` by `alf_volume(...)`.
- `psig_buried_area` increments on `ALF_POC_BURIED` by
  `alf_triangle_area(...)`.
- `psig_mouth_area` increments on `ALF_POC_MOUTH` and subtracts on
  `ALF_POC_UNION_TWO` and `ALF_POC_UNION_SAME`.
- `alf_volume` is ordinary tetrahedral Euclidean volume.
- `alf_triangle_area` is ordinary triangular Euclidean area.

This layer is close to the metric helpers currently used by the native path:

- `component_volume(...)` sums tetrahedral volumes.
- `component_area(...)` sums triangular boundary areas.
- `mouth_area(...)` sums triangular mouth patch areas.
- `mouth_perimeter(...)` sums boundary-edge lengths of the mouth patch.

The remaining work here is not to invent new formulas, but to make the native
records explicitly follow the CASTp 1.0 event-signature semantics where the
final reported quantity depends on `ALF_POC_*` sequence updates rather than only
post-hoc component faces.

### 2. VOLBL SA/MS analytical metrics

Source:

- `volbl/metric.c`
- `volbl/volbl.c`
- `volbl/volbl.h`

This is a different metric engine. It computes solvent-accessible and
molecular-surface quantities through ball, cap, sector, wedge, pawn, shell,
torus, and cusp-correction terms.

Examples from the source:

- `ball_volume`
- `cap_volume`
- `cap2_volume`
- `cap3_volume`
- `sector_volume`
- `wedge_volume`
- `pawn_volume`
- `shell`
- `torus`

This layer is not currently implemented natively.

## Why existing `pocInfo/mouthInfo` files are not a CASTp 1.0 oracle yet

The files `sandbox/castp_oracle_runs/1crn/1crn.pocInfo` and
`sandbox/castp_oracle_runs/2pk4/2pk4.pocInfo` exist, but they are not aligned
with the explicit-rank MKALF structural files used in the green CASTp 1.0
matrix.

Example observations:

| Case | Explicit-rank `.poc` components | `pocInfo` rows | Interpretation |
|---|---:|---:|---|
| `1crn` | 1 | 1 | Row count matches, but `N_mth` and metrics do not match the explicit-rank mouth structure. |
| `2pk4` | 10 | 7 | Row count does not match the explicit-rank structural oracle. |

Therefore, those `pocInfo/mouthInfo` files should not be used as the pass/fail
oracle for CASTp 1.0 metric parity unless their generation command and rank
contract are recovered.

They are still useful later for CASTP 3.0/server parity.

## Current native metric status

The native values currently reported in records are best interpreted as partial
MKALF-style geometric metrics:

- feature `volume`: sum of Delaunay tetrahedron volumes in the component;
- feature `area`: sum of boundary triangle areas;
- `mouth_area`: sum of mouth-triangle patch areas;
- `mouth_perimeter`: perimeter of the mouth-triangle patch.

They should not be interpreted as:

- `Vol_sa`
- `Vol_ms`
- `Area_sa`
- `Area_ms`
- `Len_sa`
- `Len_ms`

Those SA/MS fields belong to the VOLBL/server metric contract and remain
unimplemented in the native CASTp 1.0 path.

## Required work to close metric parity

### A. Close MKALF pocket-signature metrics

Implement or expose a native metric path driven by the same events as
`alf_pocket_sequence`:

- `ALF_POC_TETRA`
- `ALF_POC_BURIED`
- `ALF_POC_MOUTH`
- `ALF_POC_UNION_TWO`
- `ALF_POC_UNION_SAME`
- `ALF_POC_RANK`

The native code already emits these event types during
`_build_rank_driven_components(...)`; this should be reused rather than
reconstructed independently.

Minimum checks:

- aggregate pocket volume by rank matches the sum of `ALF_POC_TETRA`
  tetrahedral volumes;
- aggregate mouth area by rank follows the `+MOUTH -UNION` update semantics;
- component-level reported mouth areas remain consistent with the final mouth
  clusters.

### B. Decide whether VOLBL is in scope for CASTp 1.0 closure

Strict reproduction of `Vol_sa`, `Vol_ms`, `Area_sa`, `Area_ms`, `Len_sa`, and
`Len_ms` requires porting the VOLBL analytical metric engine or wrapping it as a
temporary oracle.

For a 100% independent native implementation, wrapping `volbl` is not the final
answer. It is useful only as an oracle while porting.

### C. Generate aligned metric oracles

Before testing SA/MS parity, regenerate metric artifacts from the same input and
rank policy as the structural CASTp 1.0 matrix. Existing `pocInfo/mouthInfo`
files are not enough because they are not proven to correspond to the explicit
rank commands:

```text
print pockets rank R rank2 R2
print voids rank R
```

## Current decision

The CASTp 1.0 structural phase is green, but the CASTp 1.0 metric phase remains
open.

Do not claim full CASTp 1.0 parity until one of these is true:

- MKALF-style geometric metric signatures are implemented and verified; and
  VOLBL SA/MS metrics are explicitly declared out of scope for CASTp 1.0
  closure; or
- both MKALF pocket-signature metrics and VOLBL SA/MS metrics are implemented
  and verified against aligned local oracles.

## Implemented in this checkpoint

The native code now has an internal MKALF-style pocket metric signature helper:

- `castp1_pocket_metric_signatures(...)`

It reuses the same `_build_rank_driven_components(...)` event stream as the
structural pocket construction and applies the update rules from
`sig/poc-metric.c` and `sig/poc-comb.c`:

- `ALF_POC_TETRA`: add tetrahedral volume;
- `ALF_POC_BURIED`: add buried triangle area;
- `ALF_POC_MOUTH`: add mouth triangle area and increment mouth-triangle count;
- `ALF_POC_UNION_TWO` / `ALF_POC_UNION_SAME`: subtract mouth triangle area and
  decrement mouth-triangle count;
- `ALF_POC_RANK`: snapshot the current signature values for that rank.

The helper currently reports:

- `num_pockets`
- `num_tetra`
- `num_buried_triangles`
- `mouth_triangles`
- `max_tetra`
- `pocket_volume`
- `buried_area`
- `mouth_area`
- `max_pocket_volume`

For `max_tetra` and `max_pocket_volume`, the helper maintains a local
union-find state over `ALF_POC_UNION_TWO`, mirroring the historical signature
logic. `mouth_area` follows CASTp 1.0's `correct(...)` behavior by clamping
negative numerical residue only at rank snapshot time.

This closes the first implementation step for MKALF-style geometric and
combinatorial pocket signatures. It does not close VOLBL/server-style SA/MS
metrics.

Verification:

```bash
pytest -q tests/test_castp_core.py -k "castp1_pocket_metric_signatures or build_rank_driven_components_emits_rank"
```

Result: passed.

## VOLBL native port started

The native tree now has a first VOLBL metric primitive layer:

- `topomt.third_party.castp.core.castp_core.volbl.VolblMetricContext`

Implemented from `volbl/metric.c`:

- ball area/volume/radius;
- tetrahedron volume;
- radical centers for 2, 3, and 4 atoms;
- cap height, area, and volume;
- disk radius, length, and area;
- segment and segment2 height/angle/length/area;
- cap2/cap3 area and volume;
- ball2/ball3/ball4 area, length, and volume;
- sector, wedge, and pawn area/length/volume;
- shell shrinkage from solvent-accessible area to molecular-surface area and
  shell volume;
- helper formulas for cone frustum, round pyramid, torus fraction, and VDW
  radical-plane geometry;
- solvent patch terms;
- torus terms, including hidden-ball and cusp/no-cusp branches.

The native tree also now has the main global VOLBL accumulators:

- `space_filling_measurements(...)`
- `voids_measurements(...)`
- `fringe_measurements_cx(...)`
- `shape_volume(...)`
- `envelope_measurements(...)`

This follows `volbl.c`'s inclusion-exclusion sequence over the CASTp master
list up to `input_rank`:

- `ALF_VERTEX`: add ball SA volume/area and shell-corrected MS values;
- `ALF_EDGE`: subtract cap-pair volume/area, add edge length, and apply torus
  and shell corrections to MS values;
- `ALF_TRIANGLE`: add cap2 terms, subtract/add patch and torus terms, and add
  two corners;
- `ALF_TETRA`: subtract cap3 terms, apply patch/torus/shell corrections, add
  ball4 length, and subtract four corners.

This is intentionally a native port of the historical formulas rather than a
post-hoc metric computed from final connected components.

`voids_measurements(...)` follows the historical `find_voids`/`measure_a_void`
contract:

- use the validated complement components as the native equivalent of
  `find_voids`;
- initialize each void with the Euclidean tetrahedral volume sum;
- apply the same `do_tetra_vertex`, `do_tetra_edge`, and
  `do_tetra_triangle` corrections for vertices, edges, and triangles that are
  in the dual complex at `input_rank`;
- report per-void and total SA/MS volume, area, length, and corner counts.

`fringe_measurements_cx(...)` follows the dual-complex fringe path:

- scan master-list entries up to `input_rank`;
- include only first vertex/edge/triangle events that are not interior;
- for tetrahedron events, apply `do_complex_tetrahedron`-style corrections to
  non-interior subfaces;
- perform the final sign correction against total initial void volume and
  measured void totals.

`shape_volume(...)` is the historical dual-complex tetrahedral volume sum up
to `input_rank`. `envelope_measurements(...)` now assembles voids, fringe, and
shape using the same dependency order as `volbl.c`.

The first aligned local VOLBL oracle check is now green for `1crn` at
`alpha = 0`, using the local CASTp 1.0 executable as reference. This does not
yet prove all-system VOLBL parity, but it closes the first end-to-end numerical
checkpoint across space filling, outside fringe, void totals, and alpha-shape
volume.

Verification:

```bash
pytest -q tests/test_castp_core.py -k "volbl_metric_context or space_filling_measurements or voids_measurements or shape_volume or envelope_measurements or castp1_pocket_metric_signatures"
```

Result: passed, 13 tests.

## VOLBL oracle compatibility note

The historical CASTp 1.0 `volbl` executable completed the `1crn` calculation
but aborted on shutdown with modern glibc during `alf_kill(...)` /
`sos_shutdown(...)`. To recover usable stdout from the local oracle, the
checkout under `sandbox/castp_alpha_4_1_src_local/volbl/volbl.c` carries a
local compatibility patch that skips `alf_kill(alp)` after `volbl_clean()`.

This patch is intentionally limited to the local oracle executable. It is not
part of the native TopoMT implementation and should not be interpreted as a
CASTp algorithm change.

The oracle was rebuilt manually from `volbl/volbl.c`, `volbl/metric.c`,
`volbl/voids.c`, and `volbl/bst.c` against the existing local `_alf` library.

## VOLBL parity fixes from the first oracle comparison

Two native divergences were found and corrected before the `1crn` VOLBL check
closed.

### 1. Tetrahedral orientation for `ccw`

CASTp 1.0 routes VOLBL orientation through:

```c
int ccw (int i, int j, int k, int l) { return sos_positive3(i,j,k,l); }
```

With the native coordinate ordering, the direct row-determinant convention had
the opposite sign. This affected oriented `cap3`/`ball4` terms. The native
VOLBL context now uses the CASTp-compatible sign convention for `ccw`.

Observed diagnostic on `1crn` before the fix:

| Quantity | Value |
|---|---:|
| Native direct-orientation `ball4` sum | `28794.520153` |
| Native CASTp-compatible-orientation `ball4` sum | `23291.158379` |
| Difference | `5503.361774` |
| `2 * Vsh` | `5503.361774` |

This explained the space-filling volume discrepancy.

### 2. `ball_radius` uses alpha, not solvent radius

CASTp 1.0 defines:

```c
rdsqr = Sign(B[i].w) * B[i].w * B[i].w + Sign(Alpha) * Alpha * Alpha;
```

The native port initially used `solvent_radius` in this expression. That was
not canonical. It affected sector-volume terms in void/fringe calculations
while leaving most space-filling formulas unchanged. The native
`VolblMetricContext` now separates `alpha` from `solvent_radius`; for the
current CASTp 1.0 oracle runs `alpha = 0.0`.

Observed diagnostic on `1crn` before this fix:

| Quantity | CASTp 1.0 oracle | Native before fix |
|---|---:|---:|
| `Vof_sa` | `6054.747` | `4751.970` |
| `Vof_ms` | `2324.796` | `1022.019` |
| `Aof_sa` | `3013.097` | `3013.097` |
| `Aof_ms` | `2331.009` | `2331.009` |
| `Lof` | `1372.335` | `1372.335` |
| `Cof` | `458` | `458` |

The pattern isolated the error to sector-volume radius semantics rather than
to topology, surface area, edge length, or corner enumeration.

## `1crn` VOLBL oracle parity after fixes

Command used for the CASTp 1.0 oracle:

```bash
cd sandbox/castp_oracle_runs/1crn
../../castp_alpha_4_1_src_local/bin/volbl -s 4 -n 1crn
```

Native command used the same PDB input with `radii_model='castp_param'` and
`input_rank` equal to the native rank of `alpha = 0`.

| Quantity | CASTp 1.0 oracle | Native | Status |
|---|---:|---:|---|
| `Vsf_sa` | `8806.427` | `8806.428050` | Match within oracle print precision |
| `Vsf_ms` | `5076.477` | `5076.477552` | Match within oracle print precision |
| `Vtv_sa` | `0.000` | `0.000000` | Match |
| `Vtv_ms` | `0.000` | `0.000000` | Match |
| `Vtiv` | `0.000` | `0.000000` | Match |
| `Vof_sa` | `6054.747` | `6054.747163` | Match within oracle print precision |
| `Vof_ms` | `2324.796` | `2324.796665` | Match within oracle print precision |
| `Vsh` | `2751.681` | `2751.680887` | Match within oracle print precision |
| `Asf_sa` | `3013.097` | `3013.096811` | Match within oracle print precision |
| `Asf_ms` | `2331.009` | `2331.008815` | Match within oracle print precision |
| `Atv_sa` | `0.000` | `0.000000` | Match |
| `Atv_ms` | `0.000` | `0.000000` | Match |
| `Aof_sa` | `3013.097` | `3013.096811` | Match within oracle print precision |
| `Aof_ms` | `2331.009` | `2331.008815` | Match within oracle print precision |
| `Lsf` | `1372.335` | `1372.335170` | Match within oracle print precision |
| `Ltv` | `0.000` | `0.000000` | Match |
| `Lof` | `1372.335` | `1372.335170` | Match within oracle print precision |
| `Csf` | `458` | `458` | Match |
| `Ctv` | `0` | `0` | Match |
| `Cof` | `458` | `458` | Match |
| Number of voids | `0` | `0` | Match |

Initial performance note for `1crn` on this machine, before the first VOLBL
optimization pass:

| Native block | Runtime |
|---|---:|
| `space_filling_measurements(...)` | about `26 s` |
| `voids_measurements(...)` | about `0.01 s` |
| `fringe_measurements_cx(...)` | about `86 s` |
| `shape_volume(...)` | about `0.03 s` |

The implementation was numerically aligned for this checkpoint but still slow.
Performance was therefore treated as a follow-up optimization task after more
oracle cases confirmed the formulas.

## Remaining metric-parity work

The next CASTp 1.0 metric step is not to change formulas, but to expand and
speed up the VOLBL oracle matrix carefully:

- keep checking `space_filling`, `voids`, `fringe`, and `shape` separately;
- include systems with non-zero void totals;
- avoid formula changes unless a new discrepancy can be traced directly to
  CASTp 1.0 source semantics;
- optimize `fringe_measurements_cx(...)` after the first small-system matrix is
  green.

## Additional VOLBL oracle expansion

After the `1crn` fix checkpoint, two more systems were checked against the
local CASTp 1.0 `volbl -s 4` oracle.

### `1rop`

`1rop` is a larger no-void case than `1crn`.

| Quantity | CASTp 1.0 oracle | Native | Status |
|---|---:|---:|---|
| `Vsf_sa` | `14533.89` | `14533.895911` | Match within oracle print precision |
| `Vsf_ms` | `8127.611` | `8127.612403` | Match within oracle print precision |
| `Vtv_sa` | `0.000` | `0.000000` | Match |
| `Vtv_ms` | `0.000` | `0.000000` | Match |
| `Vtiv` | `0.000` | `0.000000` | Match |
| `Vof_sa` | `9944.091` | `9944.092109` | Match within oracle print precision |
| `Vof_ms` | `3537.808` | `3537.808600` | Match within oracle print precision |
| `Vsh` | `4589.803` | `4589.803802` | Match within oracle print precision |
| `Asf_sa` | `5134.075` | `5134.075258` | Match within oracle print precision |
| `Asf_ms` | `4086.661` | `4086.665002` | Match within oracle print precision |
| `Aof_sa` | `5134.075` | `5134.075258` | Match within oracle print precision |
| `Aof_ms` | `4086.661` | `4086.665002` | Match within oracle print precision |
| `Lsf` | `2169.170` | `2169.169369` | Match within oracle print precision |
| `Lof` | `2169.170` | `2169.169369` | Match within oracle print precision |
| `Csf` | `698` | `698` | Match |
| `Cof` | `698` | `698` | Match |
| Number of voids | `0` | `0` | Match |

Initial native runtime:

| Block | Runtime |
|---|---:|
| `space_filling_measurements(...)` | about `34 s` |
| `voids_measurements(...)` | about `0.01 s` |
| `fringe_measurements_cx(...)` | about `208 s` |
| `shape_volume(...)` | about `0.04 s` |

### `1ubq`

`1ubq` is the first checked case with non-zero void totals.

| Quantity | CASTp 1.0 oracle | Native | Status |
|---|---:|---:|---|
| `Vsf_sa` | `18527.70` | `18527.698246` | Match within oracle print precision |
| `Vsf_ms` | `11365.47` | `11365.472514` | Match within oracle print precision |
| `Vtv_sa` | `0.000838` | `0.000838` | Match within oracle print precision |
| `Vtv_ms` | `38.76370` | `38.764053` | Match within oracle print precision |
| `Vtiv` | `53.67224` | `53.672253` | Match within oracle print precision |
| `Vof_sa` | `10955.90` | `10955.900548` | Match within oracle print precision |
| `Vof_ms` | `3832.437` | `3832.438030` | Match within oracle print precision |
| `Vsh` | `7518.126` | `7518.126284` | Match within oracle print precision |
| `Asf_sa` | `5617.881` | `5617.881589` | Match within oracle print precision |
| `Asf_ms` | `4728.609` | `4728.610663` | Match within oracle print precision |
| `Atv_sa` | `0.095733` | `0.095728` | Match within oracle print precision |
| `Atv_ms` | `81.21760` | `81.218073` | Match within oracle print precision |
| `Aof_sa` | `5617.785` | `5617.785861` | Match within oracle print precision |
| `Aof_ms` | `4647.392` | `4647.392590` | Match within oracle print precision |
| `Lsf` | `2492.963` | `2492.963791` | Match within oracle print precision |
| `Ltv` | `2.182188` | `2.182370` | Match within oracle print precision |
| `Lof` | `2490.781` | `2490.781421` | Match within oracle print precision |
| `Csf` | `836` | `836` | Match |
| `Ctv` | `16` | `16` | Match |
| `Cof` | `820` | `820` | Match |
| Number of voids | `3` | `3` | Match |

Initial native runtime:

| Block | Runtime |
|---|---:|
| `space_filling_measurements(...)` | about `51 s` |
| `voids_measurements(...)` | about `0.65 s` |
| `fringe_measurements_cx(...)` | about `397 s` |
| `shape_volume(...)` | about `0.07 s` |

The small-system VOLBL formula matrix is now green for:

| System | Void totals? | Status |
|---|---:|---|
| `1crn` | No | Green |
| `1rop` | No | Green |
| `1ubq` | Yes, 3 voids | Green |

## VOLBL optimization pass

The first performance profile showed that `fringe_measurements_cx(...)` was not
slow because of VOLBL formulas. It was slow because `_face_is_interior(...)`
rebuilt the same face-rank map for every face query.

Implemented optimization:

- cache `_face_rank_maps_by_atoms(geometry)` by `geometry` object identity;
- keep the cache bounded;
- do not change rank semantics, formula signs, or traversal order.

The second bottleneck was `angle_dihedral(...)`, where repeated `np.cross(...)`
calls dominated the runtime. The implementation now uses the same scalar cross
product and normalized dot-product formula directly. This removes NumPy call
overhead without changing the mathematical definition.

Post-optimization runtimes:

| System | Block | Before | After |
|---|---|---:|---:|
| `1crn` | `space_filling_measurements(...)` | about `26 s` | about `10.8 s` |
| `1crn` | `fringe_measurements_cx(...)` | about `84 s` | about `1.6 s` |
| `1ubq` | `space_filling_measurements(...)` | about `51 s` | about `23.7 s` |
| `1ubq` | `voids_measurements(...)` | about `0.65 s` | about `0.08 s` |
| `1ubq` | `fringe_measurements_cx(...)` | about `397 s` | about `2.8 s` |

Post-optimization numerical checks:

| System | Status |
|---|---|
| `1crn` | Values unchanged within floating-point roundoff; still green against CASTp 1.0 oracle |
| `1ubq` | Values unchanged within floating-point roundoff; still green against CASTp 1.0 oracle, including non-zero void totals |

Current interpretation: the native VOLBL formulas are aligned with CASTp 1.0
for the tested small systems, and the main runtime blocker in
`fringe_measurements_cx(...)` has been removed. The remaining performance cost
is mainly `space_filling_measurements(...)`, but it is now practical enough to
continue expanding the oracle matrix.

The preferred entry point for full global VOLBL totals is now
`volbl_measurements(...)`. It computes `space_filling`, `voids`, `fringe`, and
`shape` with one shared `VolblMetricContext`, so all primitive caches are reused
across blocks. Calling the individual functions independently is still valid,
but slower because each call builds a fresh metric context.

Measured combined runtime through `volbl_measurements(...)`:

| System | Combined runtime | Notes |
|---|---:|---|
| `1crn` | about `8.3 s` | no voids |
| `1ubq` | about `18.7 s` | 3 voids |
| `2pk4` | about `22.0 s` | 1 void |
| `1stp` | about `31.5 s` | 1 void |

Regression coverage:

- `test_native_volbl_matches_local_castp1_oracle_totals` compares the combined
  native VOLBL path against local CASTp 1.0 oracle totals for `1crn` and
  `2pk4`;
- the test skips when local oracle files are absent;
- tolerance is absolute `1.0e-2`, matching the printed precision available from
  the historical `volbl` stdout.

Performance conclusion before considering Numba:

- Broad NumPy vectorization is not the first lever here. The remaining hot path
  is dominated by many small scalar exact-predicate and geometric primitive
  calls, where NumPy call overhead can dominate.
- The useful pure-Python optimizations so far were cache reuse, avoiding
  repeated topology-map construction, replacing small `np.cross` calls by
  scalar arithmetic, and avoiding `np.linalg.norm` for 3D point distances.
- Scalar determinant helpers for `tetrahedron_volume`, `center3`, `center4`,
  and `triangle_dual` are now implemented. They keep the same formulas as the
  CASTp/VOLBL source but avoid many small `np.linalg.det` and `np.cross` calls.
- More speed is still possible without Numba, but it should remain targeted:
  reducing exact hidden-predicate setup overhead and precomputing event-local
  atom tuples are better candidates than trying to vectorize the whole VOLBL
  traversal.

## Additional void-system checks after optimization

Two more systems with non-zero void totals were checked after the VOLBL
optimization pass.

### `2pk4`

`2pk4` has one minimal void. It is useful because the void branch contributes a
small but non-zero `Vtv_sa`, `Vtv_ms`, `Atv`, `Ltv`, and `Ctv`.

| Quantity | CASTp 1.0 oracle | Native | Status |
|---|---:|---:|---|
| `Vsf_sa` | `20654.25` | `20654.255897` | Match within oracle print precision |
| `Vsf_ms` | `12394.57` | `12394.569150` | Match within oracle print precision |
| `Vtv_sa` | `0.000304` | `0.000304` | Match within oracle print precision |
| `Vtv_ms` | `13.94116` | `13.941142` | Match within oracle print precision |
| `Vtiv` | `10.91916` | `10.919162` | Match within oracle print precision |
| `Vof_sa` | `12455.52` | `12455.519325` | Match within oracle print precision |
| `Vof_ms` | `4209.772` | `4209.773415` | Match within oracle print precision |
| `Vsh` | `8187.817` | `8187.817715` | Match within oracle print precision |
| `Asf_sa` | `6558.904` | `6558.903886` | Match within oracle print precision |
| `Asf_ms` | `5394.201` | `5394.199782` | Match within oracle print precision |
| `Atv_sa` | `0.042880` | `0.042879` | Match within oracle print precision |
| `Atv_ms` | `28.38051` | `28.380476` | Match within oracle print precision |
| `Aof_sa` | `6558.861` | `6558.861006` | Match within oracle print precision |
| `Aof_ms` | `5365.820` | `5365.819306` | Match within oracle print precision |
| `Lsf` | `2759.121` | `2759.121113` | Match within oracle print precision |
| `Ltv` | `1.236587` | `1.236576` | Match within oracle print precision |
| `Lof` | `2757.885` | `2757.884537` | Match within oracle print precision |
| `Csf` | `858` | `858` | Match |
| `Ctv` | `4` | `4` | Match |
| `Cof` | `854` | `854` | Match |
| Number of voids | `1` | `1` | Match |

Post-optimization native runtime:

| Block | Runtime |
|---|---:|
| `space_filling_measurements(...)` | about `30.3 s` |
| `voids_measurements(...)` | about `0.05 s` |
| `fringe_measurements_cx(...)` | about `3.7 s` |
| `shape_volume(...)` | about `0.09 s` |

### `1stp`

`1stp` is larger than `2pk4` and has one void with a different correction
pattern (`Ctv = 6`).

| Quantity | CASTp 1.0 oracle | Native | Status |
|---|---:|---:|---|
| `Vsf_sa` | `25697.46` | `25697.458773` | Match within oracle print precision |
| `Vsf_ms` | `16487.74` | `16487.745079` | Match within oracle print precision |
| `Vtv_sa` | `0.000913` | `0.000913` | Match within oracle print precision |
| `Vtv_ms` | `15.21709` | `15.217130` | Match within oracle print precision |
| `Vtiv` | `17.22592` | `17.225951` | Match within oracle print precision |
| `Vof_sa` | `14643.41` | `14643.406823` | Match within oracle print precision |
| `Vof_ms` | `5448.909` | `5448.909346` | Match within oracle print precision |
| `Vsh` | `11036.83` | `11036.826911` | Match within oracle print precision |
| `Asf_sa` | `7219.006` | `7219.006593` | Match within oracle print precision |
| `Asf_ms` | `6081.503` | `6081.502160` | Match within oracle print precision |
| `Atv_sa` | `0.103423` | `0.103429` | Match within oracle print precision |
| `Atv_ms` | `30.41803` | `30.418145` | Match within oracle print precision |
| `Aof_sa` | `7218.903` | `7218.903164` | Match within oracle print precision |
| `Aof_ms` | `6051.085` | `6051.084014` | Match within oracle print precision |
| `Lsf` | `3367.094` | `3367.095534` | Match within oracle print precision |
| `Ltv` | `2.235439` | `2.235448` | Match within oracle print precision |
| `Lof` | `3364.859` | `3364.860086` | Match within oracle print precision |
| `Csf` | `1178` | `1178` | Match |
| `Ctv` | `6` | `6` | Match |
| `Cof` | `1172` | `1172` | Match |
| Number of voids | `1` | `1` | Match |

Post-optimization native runtime:

| Block | Runtime |
|---|---:|
| `space_filling_measurements(...)` | about `43.6 s` |
| `voids_measurements(...)` | about `0.09 s` |
| `fringe_measurements_cx(...)` | about `6.0 s` |
| `shape_volume(...)` | about `0.11 s` |

Updated VOLBL matrix:

| System | Void totals? | Status |
|---|---:|---|
| `1crn` | No | Green |
| `1rop` | No | Green |
| `1ubq` | Yes, 3 voids | Green |
| `2pk4` | Yes, 1 void | Green |
| `1stp` | Yes, 1 void | Green |

This is now enough evidence to treat the native VOLBL formula port as
substantially aligned with CASTp 1.0 for small and medium-small systems. The
remaining validation work should focus on broader system diversity, not on
changing formulas.

## Full local VOLBL matrix attempt

The current local oracle folders with `.pdb`, `.dt`, and `.alf` were checked
with `volbl -s 4` as CASTp 1.0 reference and native `volbl_measurements(...)`
as implementation under test.

| System | Rank `alpha=0` native | Voids native | Oracle runtime | Native runtime | Status | Largest absolute delta |
|---|---:|---:|---:|---:|---|---:|
| `1crn` | `3894` | `0` | `0.97 s` | `10.01 s` | Green | `0.0010` |
| `1rop` | `6251` | `0` | `1.46 s` | `14.05 s` | Green | `0.0059` |
| `1ubq` | `8553` | `3` | `1.88 s` | `21.69 s` | Green | `0.0025` |
| `2pk4` | `9877` | `1` | `2.29 s` | `25.49 s` | Green | `0.0059` |
| `1stp` | `13419` | `1` | `3.18 s` | `33.47 s` | Green | `0.0051` |
| `1pht` | `11327` | `0` | `2.84 s` | `28.70 s` | Green | `0.0041` |
| `1lyz` | `14682` | `6` | `3.22 s` | `35.70 s` | Green | `0.0035` |
| `2lyz` | `14976` | `7` | `3.40 s` | `35.26 s` | Green | `0.0042` |
| `1mbn` | `16057` | `10` | `3.84 s` | `44.21 s` | Green | `0.0062` |
| `1hiv` | `23192` | `2` | `5.72 s` | `55.84 s` | Fail | `Vsf_sa = 969.17` |
| `1tcd` | `58471` | `22` | `12.10 s` | `140.25 s` | Fail | `Vsf_sa = 1748.83` |

Green/total: `9/11`.

The two failures are not small numerical tolerance failures. They are large
global divergences:

| System | `Vsf_sa` oracle | `Vsf_sa` native | Delta |
|---|---:|---:|---:|
| `1hiv` | `42711.04` | `41741.869198` | `969.17` |
| `1tcd` | `95581.31` | `93832.480577` | `1748.83` |

## Diagnosis of `1hiv` and `1tcd`

The first hypothesis was that the native SciPy-based redundant-vertex pruning
was too aggressive. That was tested by adding an explicit
`discard_redundant_vertices` switch to `build_castp_geometry(...)` and running
the failing systems with pruning disabled.

Result:

| System | Pruning | Native vertices | Status |
|---|---|---:|---|
| `1hiv` | enabled | `1657` | Fail |
| `1hiv` | disabled | `1665` | Fail |
| `1tcd` | enabled | `3957` | Fail |
| `1tcd` | disabled | `3983` | Fail |

The failure is therefore not fixed by retaining all vertices.

The decisive difference is triangulation:

| System | Vertices | DELCX tetrahedra | Native tetrahedra | DELCX edges | Native edges | DELCX spectrum | Native spectrum | DELCX master | Native master |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `1hiv` | `1665` | `10809` | `10806` | `12541` | `12530` | `25744` | `25535` | `98784` | `98268` |
| `1tcd` | `3983` | `26227` | `26235` | `30298` | `30280` | `63380` | `63808` | `240486` | `240205` |

Initial interpretation:

- The native VOLBL formulas are not the likely source of these two failures.
- `1hiv` and `1tcd` expose the residual triangulation/SoS front: SciPy/Qhull
  and CASTp 1.0 DELCX do not produce the same regular triangulation and
  therefore not the same spectrum/master list.
- Once the tetrahedra/edges/spectrum differ, global VOLBL totals must diverge.

This interpretation was incomplete. A follow-up audit compared the actual ALF
input used by CASTp 1.0 against the native PDB-derived coordinates and radii.

Coordinate comparison with pruning disabled:

| System | ALF rows | Native atoms | Max coordinate delta | Radius mismatches |
|---|---:|---:|---:|---:|
| `1hiv` | `1665` | `1665` | `7.1e-15` | `1592` |
| `1tcd` | `3983` | `3983` | `1.4e-14` | `3983` |

The coordinates were identical, but the radii were not. Examples:

| System | Atom | Native expanded radius | ALF radius |
|---|---:|---:|---:|
| `1hiv` | `1` | `3.025` | `3.2` |
| `1hiv` | `2` | `3.300` | `3.2` |
| `1hiv` | `3` | `3.275` | `3.2` |
| `1tcd` | `1` | `3.025` | `3.2` |
| `1tcd` | `2` | `3.300` | `3.2` |
| `1tcd` | `3` | `3.275` | `3.2` |

Therefore, the observed triangulation/spectrum differences were a consequence
of different weighted input, not independent proof that DELCX/SoS was the
primary blocker.

## Full matrix resolved with ALF radii for special cases

`build_castp_geometry(...)` now has an `atom_radii_override` audit hook. The
override expects final expanded radii, exactly as stored in the CASTp ALF input.
It is used to test whether a local CASTp 1.0 oracle can be reproduced from the
same weighted input.

Running `1hiv` and `1tcd` with ALF radii and pruning disabled gives:

| System | Native rank `alpha=0` | Atoms | Native tetrahedra | Native edges | Native spectrum | Native master | Status | Largest absolute delta |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| `1hiv` | `23581` | `1665` | `10809` | `12541` | `25743` | `98784` | Green | `Asf_ms = 0.0154` |
| `1tcd` | `58323` | `3983` | `26227` | `30298` | `63379` | `240486` | Green | `Vsf_ms = 0.0097` |

These counts now match the CASTp 1.0 triangulation/master-list counts in the
important structural quantities:

| System | DELCX tetrahedra | Native tetrahedra | DELCX edges | Native edges | DELCX master | Native master |
|---|---:|---:|---:|---:|---:|---:|
| `1hiv` | `10809` | `10809` | `12541` | `12541` | `98784` | `98784` |
| `1tcd` | `26227` | `26227` | `30298` | `30298` | `240486` | `240486` |

Final corrected interpretation:

- VOLBL formula parity is green for all local systems tested when the native
  path uses the same weighted input as CASTp 1.0.
- The previous `1hiv`/`1tcd` failures were caused by radii policy mismatch, not
  by proven DELCX/SoS incompatibility.
- DELCX/SoS remains a theoretical strict-parity risk, but it is not the
  demonstrated blocker for these two large systems.
- Future CASTp 1.0 parity tests must distinguish PDB-derived native radii from
  ALF-oracle radii. Comparing against a CASTp 1.0 `.alf/.dt/.alf-shape` oracle
  requires using the same ALF radii.

## Native PDB2ALF radii policy

The `atom_radii_override` hook above is only an audit tool. It proves that the
remaining metric/triangulation pipeline can reproduce a CASTp 1.0 oracle when
the weighted input is identical, but it is not an acceptable native production
strategy because it depends on CASTp-generated ALF radii.

The native implementation now includes a `castp1_pdb2alf` radii model that
ports the intended PDB2ALF input policy without invoking the CASTp executable:

- read only `ATOM` and `HETATM` PDB records;
- use fixed PDB fields `atom[12:16]` and `residue[17:21]`;
- remap one-letter nucleotide residue names `A`, `T`, `G`, `C` to `ADE`,
  `THY`, `GUA`, `CYT`;
- look up base radii in the historical CASTp `param.dat`;
- fall back to `1.80 Å` for unknown heavy atoms and `1.20 Å` for unknown
  hydrogens;
- add the solvent probe radius after assigning the base radius.

This is the faithful native path for CASTp1-style radii assignment. The older
`castp_param` model remains as a label-based shortcut for molecular systems
that are no longer direct PDB paths.

Important caveat: the historical `pdb2alf.c` source itself has unsafe C string
handling around the parameter table and residue-name buffers. On the current
platform, recompiling and running that C code can mark all atoms as unknown for
some PDB inputs, giving uniform expanded radii around `3.20 Å`. That behavior
matches the local `1hiv`/`1tcd` ALF-oracle radii, but it is a compiler/platform
artifact of the old converter, not the mathematical CASTp alpha-shape
algorithm. If we need to reproduce those exact archived oracles, we should treat
that as explicit `pdb2alf` bug-compatibility rather than as the canonical native
radii policy.

Current radii audit for the native `castp1_pdb2alf` model against local ALF
inputs:

| System | ALF rows | Radius mismatches | Max delta |
|---|---:|---:|---:|
| `1crn` | `327` | `0` | `4.4e-16` |
| `2pk4` | `745` | `0` | `4.4e-16` |
| `1hiv` | `1665` | `1592` | `0.675` |
| `1tcd` | `3983` | `3983` | `0.675` |

Interpretation: `1crn` and `2pk4` are consistent with the intended PDB2ALF
parameter-table policy. The archived `1hiv` and `1tcd` ALF inputs are consistent
with the old converter defaulting many/all atoms to `1.80 + 1.40 = 3.20 Å`;
those cases should not be used to judge native canonical radii unless we
explicitly choose a bug-compatible oracle mode.

## Clean CASTp1 oracle matrix

The historical `pdb2alf.c` was temporarily rebuilt with explicit string
terminators in the parameter-table parser. This produces a clean CASTp1 oracle:
`pdb2alf` assigns radii from `param.dat`, then the standard CASTp1 `delcx`,
`mkalf`, and `volbl` binaries are run on the resulting weighted input. These
clean oracle files were generated outside the repository under:

```text
/tmp/topomt_castp1_clean_oracle
```

The native radii models were checked against this clean converter for every
local benchmark. Both `castp1_pdb2alf` and the label-based `castp_param`
produce identical expanded radii for the current PDB files:

| System | Atoms | Clean PDB2ALF warnings | `castp1_pdb2alf` mismatches | `castp_param` mismatches |
|---|---:|---:|---:|---:|
| `1crn` | `327` | `2` | `0` | `0` |
| `1hiv` | `1665` | `74` | `0` | `0` |
| `1lyz` | `1102` | `1` | `0` | `0` |
| `1mbn` | `1260` | `2` | `0` | `0` |
| `1pht` | `988` | `1` | `0` | `0` |
| `1rop` | `495` | `1` | `0` | `0` |
| `1stp` | `1001` | `17` | `0` | `0` |
| `1tcd` | `3983` | `1` | `0` | `0` |
| `1ubq` | `660` | `1` | `0` | `0` |
| `2lyz` | `1102` | `1` | `0` | `0` |
| `2pk4` | `745` | `10` | `0` | `0` |

Structural alpha-shape counts against the clean `delcx/mkalf` oracle:

| System | Clean actual vertices | Native atoms | Clean ranks | Native spectrum | Clean master | Native master | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| `1crn` | `325` | `325` | `4509` | `4509` | `17795` | `17795` | Green |
| `1hiv` | `1657` | `1657` | `25534` | `25535` | `98261` | `98268` | Residual diff |
| `1lyz` | `1092` | `1092` | `16594` | `16594` | `64395` | `64395` | Green |
| `1mbn` | `1255` | `1255` | `18305` | `18305` | `73997` | `73997` | Green |
| `1pht` | `972` | `972` | `13389` | `13389` | `54843` | `54843` | Green |
| `1rop` | `491` | `491` | `7304` | `7304` | `28012` | `28012` | Green |
| `1stp` | `997` | `997` | `15070` | `15070` | `58423` | `58423` | Green |
| `1tcd` | `3957` | `3957` | `63808` | `63808` | `240205` | `240205` | Green |
| `1ubq` | `656` | `656` | `9757` | `9757` | `37735` | `37735` | Green |
| `2lyz` | `1091` | `1091` | `16913` | `16913` | `64750` | `64750` | Green |
| `2pk4` | `742` | `742` | `11290` | `11290` | `43299` | `43299` | Green |

The only remaining global structural discrepancy is `1hiv`: same effective
vertices, but native spectrum has one extra rank and seven extra master-list
entries. This is a residual degeneracy/ranking difference, not a radii issue.
It did not affect the reported pockets, voids, or global VOLBL metrics at the
tested ranks.

Local audit of the residual `1hiv` discrepancy:

- Clean DELCX and the native path differ only in one 5-atom local cell.
- The differing atom ids are `858`, `904`, `905`, `906`, and `911` in the
  clean weighted input.
- DELCX keeps two tetrahedra in that cell:
  - `{858, 904, 905, 906}`
  - `{858, 904, 905, 911}`
- The native `ConvexHull/Qhull` regular triangulation keeps three tetrahedra:
  - `{858, 904, 906, 911}`
  - `{858, 905, 906, 911}`
  - `{904, 905, 906, 911}`
- This is therefore a single local `2↔3` flip discrepancy.
- The exact five-point `lambda5` determinant for this cell is non-zero in the
  native fixed-point audit, so this does not look like a simple physical tie.
- The remaining plausible cause is that CASTp1 DELCX resolves this cell through
  its incremental flip path and SoS predicates (`positive3[_inf]`,
  `in_sphere_p[_inf]`, `lambda4`, `lambda5`), while the native substrate still
  comes from a direct regular triangulation via lifted convex hull.

Current interpretation:

- The residual `1hiv` discrepancy is now localized and no longer points to
  radii assignment, pocket assembly, or VOLBL characterization.
- It points specifically to the still-open DELCX/SoS parity front.

Global VOLBL metric parity against the clean `volbl -s 4` oracle:

| System | Native runtime | Native voids | Largest delta | Worst metric | Status |
|---|---:|---:|---:|---|---|
| `1crn` | `16.7 s` | `0` | `0.00105` | `Vsf_sa` | Green |
| `1hiv` | `79.0 s` | `2` | `0.00651` | `Vsf_ms` | Green |
| `1lyz` | `51.6 s` | `6` | `0.00349` | `Vsf_sa` | Green |
| `1mbn` | `57.6 s` | `10` | `0.00617` | `Vsh` | Green |
| `1pht` | `41.9 s` | `0` | `0.00406` | `Vsf_ms` | Green |
| `1rop` | `20.5 s` | `0` | `0.00591` | `Vsf_sa` | Green |
| `1stp` | `46.6 s` | `1` | `0.00508` | `Vsf_ms` | Green |
| `1tcd` | `196.1 s` | `22` | `0.01058` | `Vsf_sa` | Green |
| `1ubq` | `29.4 s` | `3` | `0.00251` | `Vsf_ms` | Green |
| `2lyz` | `53.7 s` | `7` | `0.00419` | `Vof_sa` | Green |
| `2pk4` | `33.8 s` | `1` | `0.00590` | `Vsf_sa` | Green |

Clean pocket/void feature parity at `alpha=0` and probe radius `1.4 Å`:

| System | Native pockets | Oracle pockets | Native voids | Oracle voids | Status |
|---|---:|---:|---:|---:|---|
| `1crn` | `1` | `1` | `0` | `0` | Green |
| `1hiv` | `7` | `7` | `2` | `2` | Green |
| `1lyz` | `13` | `13` | `6` | `6` | Green |
| `1mbn` | `16` | `16` | `10` | `10` | Green |
| `1pht` | `6` | `6` | `0` | `0` | Green |
| `1rop` | `3` | `3` | `0` | `0` | Green |
| `1stp` | `4` | `4` | `1` | `1` | Green |
| `1tcd` | `45` | `45` | `22` | `22` | Green |
| `1ubq` | `9` | `9` | `3` | `3` | Green |
| `2lyz` | `16` | `16` | `7` | `7` | Green |
| `2pk4` | `10` | `10` | `1` | `1` | Green |

Conclusion for the clean CASTp1 benchmark set:

- Native CASTp1 radii are faithful to the intended PDB2ALF/`param.dat` policy.
- Native reported pockets and voids match the clean MKALF oracle for all 11
  benchmark systems.
- Native global VOLBL metrics match the clean VOLBL oracle for all 11 systems
  within small decimal/rounding tolerances.
- Strict internal bit-for-bit parity is not yet proven because `1hiv` still has
  a residual `+1` spectrum-rank and `+7` master-entry difference. This is the
  only remaining clean CASTp1 parity caveat observed in the current matrix.
- That remaining caveat is now localized to one `2↔3` local triangulation flip,
  so the only known open block for strict CASTp1 parity is DELCX/SoS fidelity.
