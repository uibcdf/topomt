# Reference validator: the six-system report

All six current synthetic BenchLab systems were run with their **19 frozen
probe profiles**, dated **2026-11-13**, under [#76](https://github.com/uibcdf/topomt/issues/76).
Every scheduled analysis completed. This report preserves that source's answers
and measured cost, followed by later complete-topology and volume receiving; it is not
full qualification of the future connected-region validator.

**Current coverage, 2026-11-15:** **all nineteen original profiles** have complete
free-region/hull-patch inventories and meet their original k=24 volume requests,
for the total and every region. The topology results follow immediately below;
{ref}`certified volume precision <reference-validator-edge-volumes>` has its own
table, resources and downloadable proofs. Original query-run downloads remain
unchanged. Native DFND qualification and public-validator admission remain open.

The important result is the distinction between a verified local fact and a
complete global answer. Points and supplied continuous paths are checked against
every atomic ball. Only the tetrahedron at 1.7 Å receives a complete zero-region
proof in this run. General component enumeration and per-region precision are
unavailable on the other profiles **at that source**. The subsequent topology
receiving below strengthens the tetrahedron and both tubes; the original measurements and
downloads retain their historical source scope.

(complete-topology-across-the-six-original-systems-2026-11-15-utc)=

## Complete topology across the six original systems — 2026-11-15 UTC

The exact construction now covers every original profile. These counts concern
strictly free **probe-center positions inside the closed atomic-center hull**.
They are distinct from native graph components, public morphology and space
outside the hull.

| System | Probes (Å) | Complete free regions | Free hull patches |
| --- | --- | --- | --- |
| Regular tetrahedron | 1.2, 1.4, 1.7 | 1, 1, 0 | 4, 0, 0 |
| Narrow dense straight tube | 1.2, 1.4, 2.5 | 1, 1, 0 | 2, 2, 0 |
| Wide sparse straight tube | 1.4, 2.5, 5 | 1, 1, 0 | 2, 2, 0 |
| Closed shell | 0.05, 0.2, 1.4, 5 | 1, 1, 1, 0 | 13, 0, 0, 0 |
| Shell with an opening | 1.4, 3, 5 | 1, 1, 0 | 1, 0, 0 |
| Dumbbell | 1.4, 2.2, 6 | **3**, 2, 0 | 2, 0, 0 |

The small-probe closed shell has thirteen boundary patches attached to **one**
free region. At 0.2 and 1.4 Å its single region is enclosed. The opening shell
has one boundary-touching region at 1.4 Å, an enclosed region at 3 Å and none
at 5 Å. All original point-availability references are replayed on the exact
saved numerical Models.

The dumbbell illustrates why named anchors and a global inventory answer
different questions. At 1.4 Å both chamber anchors and the origin lie in one
enclosed region. **Two additional regions each touch a separate hull patch.**
The earlier chamber-connection proof remains correct; it never excluded these
extra regions. At 2.2 Å there are exactly two enclosed regions, with one chamber
anchor in each and a blocked origin. At 6 Å the hull contains no free center.
This does not settle the separate historical five-domain observation at 2.0 Å
under [#188](https://github.com/uibcdf/topomt/issues/188), nor imply that the
two hull patches are mouths to infinity.

The three new family geometries are built, checkpointed and checked once at
`d9680c2`. Source `2cd59a0` then reads or reprobes those proofs only after
checking identical full power inequalities. It independently checks each
target and its named queries. Positive global counts were unknown in the
frozen protocols. The [structured receiving](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_remaining_topology_v1/family_summary.json)
retains all raw proof, query, source and resource links.

| New receiving | Wall seconds | CPU seconds | Peak RSS MiB |
| --- | ---: | ---: | ---: |
| Three geometry initializations, including checkpoint checks | 2359.405 | 2306.471 | 41.32 |
| Ten saved-geometry target checks and queries | 1364.182 | 1362.163 | 37.92 |
| Sum of those completed workers | 3723.587 | 3668.633 | 41.32 |

All workers are sequential with one CPU/thread and a 2 GiB address-space cap.
The dumbbell initialization uses the recorded grace between its 900-second
soft CPU threshold and 1080-second hard ceiling; its measured CPU is 1031.571 s.
Every target finishes within its separate 480 soft/600 hard CPU-second and
720 wall-second envelope, without sampled host-memory pressure. Totals exclude
development and the separately retained diagnostic preflight. These are
resource receipts for rigorous checking, not performance comparisons.

Topology alone does not supply precise region volumes. The separate integration
receiving below now supplies them at the original requested precision. Neither
result qualifies native DFND's physical promotion policy, which remains under
[#181](https://github.com/uibcdf/topomt/issues/181).

(reference-validator-edge-volumes)=

## Certified volume precision for all six original systems — 2026-11-15

The independent validator now meets the original **k=24 absolute and relative
volume requirements for all nineteen profiles**, for the total and every region.
This resolves the requested precision of the thirteen positive profiles and
their sixteen regions. Six excluded profiles retain exact zero volume.

The new construction integrates signed flux over the exact power-cell faces,
then reduces each face to analytic edge integrals with exact sphere-cut decisions
and outward numerical bounds. Region assignment is reconstructed from the
complete checked topology. The original Models, probes, radii, inputs and native
DFND observations are unchanged. This certifies probe-center volume in each
finite domain; native public qualification remains a separate task.

| Original case | Probe (Å) | Regions | Volume (nm³, approx.) | Relative width (approx.) | Worker seconds | Peak RSS (MiB) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `closed_shell` | 0.05 | 1 | 0.391781717 | 3.50e-33 | 113.659 | 41.02 |
| `closed_shell` | 0.2 | 1 | 0.343932389 | 6.93e-34 | 108.708 | 40.85 |
| `closed_shell` | 1.4 | 1 | 0.113003533 | 8.39e-33 | 106.245 | 40.49 |
| `closed_shell` | 5 | 0 | 0 | exact zero | 47.140 | 30.84 |
| `dumbbell` | 1.4 | 3 | 0.506127414 | 3.05e-33 | 148.083 | 43.73 |
| `dumbbell` | 2.2 | 2 | 0.232003479 | 1.25e-32 | 141.403 | 43.64 |
| `dumbbell` | 6 | 0 | 0 | exact zero | 59.096 | 34.39 |
| `regular_tetrahedron` | 1.2 | 1 | 0.000918450981 | 2.69e-34 | 0.110 | 20.56 |
| `regular_tetrahedron` | 1.4 | 1 | 5.0841273e-05 | 5.55e-33 | 0.091 | 20.64 |
| `regular_tetrahedron` | 1.7 | 0 | 0 | exact zero | 0.041 | 20.43 |
| `shell_with_opening` | 1.4 | 1 | 0.119933998 | 6.48e-33 | 90.085 | 38.80 |
| `shell_with_opening` | 3 | 1 | 0.00982842986 | 2.51e-31 | 87.950 | 38.44 |
| `shell_with_opening` | 5 | 0 | 0 | exact zero | 38.558 | 29.20 |
| `straight_tube_narrow_dense` | 1.2 | 1 | 0.0153698025 | 1.51e-31 | 90.405 | 41.63 |
| `straight_tube_narrow_dense` | 1.4 | 1 | 0.00466733155 | 5.80e-31 | 80.867 | 40.90 |
| `straight_tube_narrow_dense` | 2.5 | 0 | 0 | exact zero | 22.390 | 31.69 |
| `straight_tube_wide_sparse` | 1.4 | 1 | 0.549362246 | 2.16e-33 | 97.330 | 41.94 |
| `straight_tube_wide_sparse` | 2.5 | 1 | 0.194638391 | 1.39e-32 | 92.989 | 41.60 |
| `straight_tube_wide_sparse` | 5 | 0 | 0 | exact zero | 29.688 | 32.20 |


Volumes are rounded midpoints; relative widths are approximate summaries of
exact rational intervals. They describe numerical error for the fixed input
Model, not biological or experimental uncertainty. Every individual region
also passes the original absolute AND relative requirements.

The nineteen analyses run sequentially on one CPU with a 2 GiB address-space
limit: 1354.837 worker elapsed / 1353.655 CPU seconds in total, peak worker RSS
43.73 MiB. This includes independent saved checking. All monitored host samples
preserve the shared-machine reserve. Sixteen boundary precision controls and
nine earlier region-volume controls also pass; the tiny-region and asymmetric
assignments are retained.

[Download the standalone receiving capsule](artifacts/reference_validator_edge_v1/README.md).
It contains the exact Models, certificates, checker source and mathematical
derivation. Fresh reading needs no producer, DFND, scientific floating package,
process pool or cached accepted state. Full records, attempted budgets and
remaining gates live in the [versioned evidence](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_edge_volume_v1/README.md).
The performance plan and public/molecular admission remain open under
[#76](https://github.com/uibcdf/topomt/issues/76) and
[#16](https://github.com/uibcdf/topomt/issues/16). This reference delivery does
not fix native #181/#180/#184/#188.

The sections below preserve earlier methods and source-scoped outcomes. Their
unmet positive-volume targets describe those earlier receiving records, rather
than the current analytic edge route.

## Earlier range-based face-integration feasibility — 2026-11-15

The validator now reuses genuinely checked in-process topology and updates
box-volume totals incrementally. Three matched measurements on the original
tetrahedron at 1.4 Å preserve exactly the queries, 512-leaf partition and
numerical bounds. Median query time changes from 0.0338 to 0.0026 seconds,
and fixed-work integration from 0.6132 to 0.2443 seconds. Independent saved
checking remains separate. These are small fixed-work observations; the
volume target is still unresolved, so they establish no general speedup or
time-to-requested-precision claim.

A second conservative integration construction sums signed flux through the
oriented faces of the checked power cells. Its certificate reconstructs every
face subdivision and retains ambiguity in region assignment. At a ceiling of
4096 triangles, the original tetrahedron uses 4095 and receives the enclosure
approximately **[0.00002874752, 0.00006295033] nm³**, in 3.714 seconds and about
27.5 MiB peak RSS on one CPU. **The original k=24 request remains unmet.**
Outward rounding error stays in the bounds; the displayed decimals abbreviate
the exact endpoints in the saved proof. This prototype still needs tighter
certified face integration before original positive-volume precision is qualified.

Two-process construction and integration reproduce the serial certificates
on this original input. Process startup/communication makes this small example
slower with two workers; serial remains the routine route. Larger parallel
receiving and the complete eight-stage performance plan remain open under
[#76](https://github.com/uibcdf/topomt/issues/76). The
[versioned evidence and stage disposition](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_performance_v1/README.md)
retain timings, source identities, failed attempts, resource limits and a fresh
saved-checker capsule. Earlier Models, findings and evidence below keep their
original scope; this continuation changes no native DFND classification.

## Certified region-volume bounds and achieved precision — 2026-11-15 UTC

The new volume panel reuses the **same nineteen original Models** and complete
power proofs. At source `4573dbe`, a checked all-atom box cover supplies total
and per-region lower/upper bounds, retaining every unknown contribution.
The request is absolute `V(hull)*2^-24` and relative `2^-24`, both required
for the total and each region. With the finite 512-leaf panel, **six excluded
profiles certify exact zero and pass; thirteen positive profiles, containing
sixteen regions, retain unresolved requested precision**. Their bounds are
valid; a zero coarse lower bound does not remove a known nonempty region.

Displayed lower endpoints are rounded down and upper endpoints up to ten
places. The saved rational proofs retain full endpoints and per-region states.
These are probe-center volumes in the declared hull, separate from native
local volume proxies or swept solvent volume.

| System / probe (Å) | Regions | Total volume enclosure (nm³) | k=24 | Wall / CPU s | Peak RSS MiB |
| --- | ---: | --- | --- | ---: | ---: |
| `regular_tetrahedron`, 1.2 | 1 | [0.0000128505, 0.0067465536] | unresolved | 1.319 / 1.287 | 23.27 |
| `regular_tetrahedron`, 1.4 | 1 | [0, 0.0024930122] | unresolved | 1.220 / 1.205 | 23.29 |
| `regular_tetrahedron`, 1.7 | 0 | [0, 0] | resolved | 0.268 / 0.221 | 23.31 |
| `straight_tube_narrow_dense`, 1.2 | 1 | [0, 0.3379134563] | unresolved | 142.385 / 142.252 | 32.70 |
| `straight_tube_narrow_dense`, 1.4 | 1 | [0, 0.2176348099] | unresolved | 134.037 / 133.914 | 32.34 |
| `straight_tube_narrow_dense`, 2.5 | 0 | [0, 0] | resolved | 83.931 / 83.837 | 31.31 |
| `straight_tube_wide_sparse`, 1.4 | 1 | [0.1389825586, 1.6504178846] | unresolved | 172.938 / 172.793 | 33.08 |
| `straight_tube_wide_sparse`, 2.5 | 1 | [0.0021716024, 0.639898864] | unresolved | 163.237 / 162.404 | 32.96 |
| `straight_tube_wide_sparse`, 5 | 0 | [0, 0] | resolved | 93.931 / 93.823 | 31.64 |
| `closed_shell`, 0.05 | 1 | [0.1337751612, 0.8398750755] | unresolved | 196.140 / 195.966 | 31.92 |
| `closed_shell`, 0.2 | 1 | [0.113708887, 0.8398750755] | unresolved | 183.040 / 180.388 | 31.84 |
| `closed_shell`, 1.4 | 1 | [0.0267550322, 0.3319296189] | unresolved | 169.588 / 169.460 | 31.68 |
| `closed_shell`, 5 | 0 | [0, 0] | resolved | 96.878 / 96.789 | 30.57 |
| `shell_with_opening`, 1.4 | 1 | [0.0306944786, 0.3564396335] | unresolved | 149.088 / 145.598 | 30.97 |
| `shell_with_opening`, 3 | 1 | [0.0036929294, 0.0220616566] | unresolved | 144.788 / 144.631 | 30.66 |
| `shell_with_opening`, 5 | 0 | [0, 0] | resolved | 81.778 / 81.692 | 29.96 |
| `dumbbell`, 1.4 | 3 | [0.0472397041, 3.0631770621] | unresolved | 254.749 / 254.516 | 35.50 |
| `dumbbell`, 2.2 | 2 | [0, 1.2376802482] | unresolved | 247.395 / 247.184 | 34.72 |
| `dumbbell`, 6 | 0 | [0, 0] | resolved | 146.133 / 145.996 | 33.71 |

The nineteen original workers take **2462.845 wall / 2453.956 CPU seconds**,
peak RSS **35.50 MiB**, one CPU and 2 GiB each. Repeated independent checks,
serialization and saved reading are included. Nine separate controls take
5.765 wall / 5.395 CPU seconds, and the saved tetrahedron refinement pilot
16.121 wall / 16.039 CPU seconds. The [structured volume summary](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_region_volume_v1/summary.json)
retains each request, proof, transition and resource receipt, including the
separate incomplete harness attempt.

For the original tetrahedron at 1.4 Å, checked refinement from ceilings
1/8/64/512 to 4096 leaves narrows the total enclosure from approximately
`[0, 0.0175453228]` to `[0.0000186232, 0.0001226076]` nm³. Every saved transition
has nested bounds; the target still fails. This measured boundary convergence
selects a more accurate integration construction before further grid growth.
General original positive-volume precision remains open under
[#76](https://github.com/uibcdf/topomt/issues/76).

### A restricted boundary integral passes the full control ladder

A separate cap/wedge integral now certifies a single ball cutting a centered
cube into **eight** free corner regions. Complete topology and reflection
symmetry justify the per-region assignment. Outward rational intervals bound
square roots, pi, atan and their series tails. Independently derived simplex
bounds check tiny regions; a cap/annulus enclosure checks the edge transition.

All **sixteen retained controls**, four radii at k=8/16/24/32, pass both total
and every region's requested precision at source `86b95d3`. The most demanding
rational radius approaches the corner at sub-binary64 separation and uses
512-bit dyadic work; no region is discarded for its size. The controls take
14.547 wall / 14.020 CPU seconds, peak RSS 23.46 MiB, on one CPU with 2 GiB.
The [derivation](https://github.com/uibcdf/topomt/blob/main/devguide/DFND/reference_validator_boundary_precision.md)
and [retained receiving](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_boundary_volume_v1/summary.json)
state this symmetric admission explicitly. It supplies a precision control for
future general clipped-cell integration; the original thirteen positive hull
profiles remain unqualified at k=24.

(exact-model-native-carrier-comparisons-2026-11-15-utc)=

## Exact-model native carrier comparisons — 2026-11-15 UTC

A strict input check first rejects numerical equality between the older
molecular receiving route and the reference Model. The narrow diagnostic
finds 136 coordinate entries changed by an Å round trip, at most `2^-52` nm;
assigned vdW radii differ by one binary64 step. The failed attempts and exact
arrays remain in the [receiving record](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_native_comparison_v1/summary.json).

The accepted fresh public route uses canonical nm coordinates and **actual
MolSysMT vdW radii**. These define two additional exact numerical Models,
separate from the nineteen originals. Their center hulls are unchanged. The
old partitions are submitted as untrusted candidates and independently checked
against every new inequality and radial predicate. Each actual native input
then matches its newly checked reference Model exactly. No tolerance-based
match or replacement of an original Model is used.

| Actual-input profile | Stored centers: blocked inside / outside hull | Complete submitted native carriers | Source tetrahedra | Public objects retained |
| --- | --- | --- | ---: | ---: |
| Narrow tube, 2.5 Å | 22 / 8 | All three carrier unions excluded | 36 | 4 |
| Wide tube, 5 Å | 0 / 1 | Its carrier union excluded | 1 | 2 |

The point query checks the declared domain first. `outside_domain` does not
assert absence of atomic collision. Floating support tolerances and the earlier
obstacle-clearance diagnosis remain separate evidence. Full carrier exclusion
follows from exact source-vertex containment in the completely excluded hull,
including the connector-only bank; it does not depend on a stored center.

The two completed workers take 146.660 wall / 146.473 CPU seconds, peak RSS
301.52 MiB, one CPU and 2 GiB. Source `d7abb46` records native inputs, quantities,
source supports, public observations, actual attribution and independent target
checks. The local capacity definitions, wet banks and public promotion are
unchanged. [#181](https://github.com/uibcdf/topomt/issues/181) still owns the
physical qualification/reporting policy; #180/#184/#188 keep their separate
native questions. Wider common-receiver qualification remains #76/#60.

## Download the additive follow-up evidence

- {download}`Models, complete topology, volume proofs, controls and standalone checker <artifacts/reference_validator_followup_v1/receiving.zip>`
- {download}`Capsule integrity manifest <artifacts/reference_validator_followup_v1/bundle_manifest.json>`
- [Reading instructions](artifacts/reference_validator_followup_v1/README.md)

The capsule checks saved proofs with Python's standard library. All original
notebooks/downloads retain their bytes. Source qualification, supported public
API, installed-package/platform matrix and hosted publication keep their
separate gates.

## Subsequent exact topology receiving — 2026-11-14 UTC

A separate construction at source `bb308ba` partitions the same fixed-probe
ball-exclusion problem into clipped power cells. An independent checker
reconstructs the complete cells and their incidence, checks every source atom
and certifies all connected free regions and free hull patches. Its first
receiving reuses the exact saved tetrahedron models from this report:

| Probe (Å) | Complete free regions | Free hull patches | Interpretation |
| --- | ---: | ---: | --- |
| 1.2 | 1 | 4 | All four patches connect to the same free region. |
| 1.4 | 1 | 0 | One enclosed region. |
| 1.7 | 0 | 0 | No free center in the finite hull. |

These are complete inventories of the declared strict ball model, not counts
of successful sample rays or native DFND catalog features. Seventeen additional
analytic controls include exact-contact transitions and tiny regions. The
twenty-profile process takes **1.764 s**, peak RSS **23.24 MiB**, on one CPU
with a 2 GiB cap. This small different task is not a speed comparison with the
six-system query panel. Nonempty per-region volume precision is still pending.

The [derivation and receiving record](https://github.com/uibcdf/topomt/blob/main/devguide/DFND/reference_validator_power_cell_construction.md)
and [raw receipt](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_power_cells_v1/receiving/receipt.json)
retain the source, complete proofs, supports and anchor checks. A separate first
narrow-tube attempt at 1.4 Å ends without a certificate after 52.030 s under
its initial 50 CPU-second ceiling; it retains unknown counts. That execution
stop is not physical exclusion or separation. Its subsequent result follows
below. At that first tetrahedron delivery, the remaining original profiles
have not received this complete topology route; native qualification and certified region-volume work remain
under #76/#181.

### Narrow tube at 1.4 Å: complete topology and checked anchor connection

Source `fd3eeb7` now constructs and independently verifies the same original
81-atom narrow-tube Model: **one connected free region and two free hull
patches**. Both patches attach to that region. The origin is blocked, while
the earlier lower/upper interior anchors are free and connected. A newly
recovered 28-point piecewise-linear path is checked against every expanded
atomic ball and the exact hull. An occupied axis/origin therefore does not
exclude the connected off-axis space.

The construction/first verification completes before a later repeated-query
capture reaches its CPU ceiling. The complete proof is preserved. Source
`92679fc` then independently replays that **saved** certificate and completes
the anchor queries in one detached batch, preserving its original producer
identity and raw checksum. It performs no new construction.

| Execution scope | Wall seconds | CPU seconds | Peak RSS MiB | Outcome |
| --- | ---: | ---: | ---: | --- |
| Construction, first complete verification and later interrupted repeated queries | 190.237 | 179.713 | 36.69 | Complete topology proof; broader capture incomplete. |
| Saved-proof replay and completed batch queries | 68.683 | 66.497 | 33.34 | Complete receiving and checked anchor connection. |

The replay spends 34.878 s in the complete verification phase and 32.577 s
in the query phase, including its separate one-per-batch check. These are
workflow costs, not the time of a fresh complete constructor. Both attempts
use one CPU/thread, 2 GiB and finite 180 CPU/240 wall-second ceilings, with
host checks every five seconds. The replay's fourteen samples retain at least
49.80 GiB available RAM and no measured memory pressure.

The [completed receipt](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_power_cells_v3/receiving/receipt.json)
and [execution record](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_power_cells_v3/execution.json)
bind the exact Model, original certificate, independent verification,
anchor/path result, phase costs and source. Earlier interrupted attempts
remain historical evidence. This strengthens only the declared 1.4 Å profile;
the other two narrow-tube probes, certified nonempty region volumes and
native/public candidate qualification retain their separate gates at that
delivery. The later receiving below completes the other two narrow probes.
No native
DFND operator, Topography classification or provider result is changed.

### Complete narrow-tube probe family — 2026-11-14

The two remaining **unchanged original** Models now have complete independent
inventories at source `d73477c`. Their atomic radii are equal, so changing the
probe leaves every power-cell inequality exactly unchanged. The new route
checks the old source proof, reuses only its cell geometry, and recomputes all
target free vertices, whole-edge collisions and region/boundary partitions.
Each resulting target certificate is independently checked again. No previous
count or free-state label supplies the target answer.

| Probe (Å) | Complete free regions | Free hull patches | Origin | Checked interior-anchor path |
| --- | ---: | ---: | --- | --- |
| 1.2 | 1 | 2 | free | 28-point continuous path. |
| 1.4 | 1 | 2 | blocked | 28-point continuous path from the earlier receiving. |
| 2.5 | 0 | 0 | blocked | No free center anywhere in the finite hull. |

At 2.5 Å, the total probe-center volume is **exactly zero** in the declared
hull, consistent with the earlier independent conservative cover. At the two
positive probes, the complete inventory does not supply a certified nonempty
region volume. The exterior outside the finite hull is a separate context.

The negative certificate covers the hull with complete checked convex power
cells, each entirely covered by its own expanded atomic ball. Squared distances
at every cell vertex certify that whole-cell cover by convexity. It is an
exhaustive geometric cover, rather than a negative conclusion from sampling.

| New execution | Wall seconds | CPU seconds | Peak RSS MiB | Actual scope |
| --- | ---: | ---: | ---: | --- |
| 1.2 Å | 123.483 | 114.327 | 35.18 | Source-proof check, target reclassification, target checks and queries. |
| 2.5 Å | 79.879 | 79.782 | 33.86 | Source-proof check, target exclusion and blocked-origin query. |

Both workers run sequentially on one CPU/thread, each bounded by 2 GiB and
180 CPU/240 wall seconds. Their total cost is **203.362 wall / 194.109 CPU
seconds**; this excludes the earlier 1.4 Å work and original cell construction.
The 41 host samples show no measured memory pressure and at least 49.62 GiB
available RAM. Phase costs distinguish source-geometry checking/reclassification,
target verification and query checking; these are not fresh constructor timings.

The [structured family summary](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_power_cells_v4/family_summary.json)
binds all three profile Models, proofs, exact volume enclosures, query outputs,
execution records and original producer scopes. The
[1.2 Å receipt](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_power_cells_v4/probe_1_2/receiving/receipt.json)
and [2.5 Å receipt](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_power_cells_v4/probe_2_5/receiving/receipt.json)
retain the new target proofs and raw checksums. Geometry reuse is rejected if
any nonprobe input or complete power inequality changes, including incompatible
unequal-radius probe changes. No monotone component-count assumption is used.

At this stage, six of the nineteen original profiles have complete topology on this
route: the three tetrahedron probes and all three narrow-tube probes. The
remaining thirteen profiles, nonempty per-region precision and native/public
qualification remain under their existing issues. The 2.5 Å reference does
not correct the native local-candidate discrepancy tracked by #181.

### Complete wide-tube probe family — 2026-11-14

The same reference construction now receives all three **unchanged original
77-atom wide-tube Models**. Its independent inventory is:

| Probe (Å) | Complete free regions | Free hull patches | Origin | Checked hull-end path |
| --- | ---: | ---: | --- | --- |
| 1.4 | 1 | 2 | free | 26-point continuous path. |
| 2.5 | 1 | 2 | free | 26-point continuous path. |
| 5 | 0 | 0 | blocked | No free center in the finite hull; exact zero volume. |

The two positive end anchors belong to different boundary patches and the
same complete free region. Every path segment is checked against all atomic
balls. At 5 Å, complete convex cells are each covered by their owner's expanded
ball, yielding an exhaustive hull cover. Nonempty per-region volume precision
remains pending.

The boundary result also agrees **face by face** with the earlier independent
certificates, identifying faces by their source atom IDs. At 1.4 Å each end
patch contains free pieces on three hull faces; at 2.5 Å it contains two.
All free faces lie at the ends, with none on the 68 wall faces. The numerical
margin in #184 belongs to the native boundary routine; this later reference
does not change that implementation or qualify its unresolved 2.5 Å result.
Reference, validator and native face ordinals are not assumed identical.

| Execution scope | Wall seconds | CPU seconds | Peak RSS MiB |
| --- | ---: | ---: | ---: |
| Initial 1.4 Å cell construction and full verification, no anchor queries | 183.539 | 178.553 | 37.27 |
| 1.4 Å saved-proof checks and anchor queries | 84.379 | 84.307 | 33.96 |
| 2.5 Å checked geometry reprobe, target checks and queries | 138.635 | 138.489 | 35.50 |
| 5 Å checked geometry reprobe, target exclusion and query | 100.525 | 97.615 | 34.40 |

The three profile workers total **323.540 wall / 320.410 CPU seconds**.
Including initialization, summed worker costs are **507.079 wall / 498.963 CPU
seconds**; time between execution stages is excluded. All four run sequentially
on one CPU/thread with 2 GiB ceilings. Initialization has 300 CPU/360 wall-
second limits; later workers have 240 CPU/300 wall-second limits. The 103
five-second host samples show no measured memory pressure and at least
49.68 GiB available RAM. These are different execution scopes, not comparable
fresh-construction timings.

The [wide-family summary](https://github.com/uibcdf/topomt/blob/main/devguide/evidence/reference_validator_power_cells_wide_v1/family_summary.json)
binds Models, certificates, source identities, per-stage costs, queries and
the earlier face-partition references. Source `38f5a86` constructs the original
wide geometry; `9c79ad7` reads that proof or reclassifies its exactly unchanged
cells for the other probes. Earlier native observations and all original
scientific artifacts retain their bytes and source scope.

At that wide-family delivery, nine of nineteen original profiles have complete topology on this route:
the tetrahedron and both tubes, each with three probes. Ten remain, alongside
certified nonempty region volumes and native qualification under #181/#184.

## What was run

Inputs, radii and probes are the unchanged sources from the
[joint six-case review](six_case_review.md). The domain is the closed convex hull
of every atomic center; strict expanded-ball contact is excluded. Received nm
binary64 values are interpreted as exact rationals. Exactness concerns this
declared rigid-ball model and its numbers.

The fixed queries are the origin, six signed coordinate rays ending exactly on
the hull, four additional face-centroid rays for the tetrahedron, the earlier
bent interior tube candidate and the dumbbell's named chamber anchors/axis.
There is no new path search or native DFND execution. Valid-ray counts below
are counts of these specific candidates, **not counts of openings or regions**.

Each saved model and proof is independently checked. An occupied point or an
invalid path never establishes that its entire component is absent. The common
whole-hull route supplies sufficient complete-cover/free tests; otherwise it
reports unknown. For the four-center tetrahedron, a fresh exact partition also
runs on `conv(the same four centers)`, retaining its separate model/proof with
identical atoms, radii, probe and source. This is the same physical hull, not a
bounding-box substitution or general hull-subdivision admission.

## Measured resources by system

All cases use **one CPU and one numerical thread**, sequentially in fresh worker
processes. Times include startup, source receiving, verification, queries and
proof persistence. Each case contains three probe profiles except the closed
shell, which contains four. A larger total is therefore not a direct algorithm
speed comparison between equal tasks.

| System | Probes | Wall time (s) | CPU time (s) | Peak RSS (MiB) | Initial receiving / hull check (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Regular tetrahedron](regular_tetrahedron/index.md) | 3 | 2.469 | 2.448 | 51.43 | 0.422 |
| [Closed shell](closed_shell/index.md) | 4 | 62.124 | 62.056 | 56.59 | 12.394 |
| [Shell with an opening](shell_with_opening/index.md) | 3 | 37.972 | 37.937 | 55.64 | 9.621 |
| [Narrow, densely sampled tube](straight_tube_narrow_dense/index.md) | 3 | 2.973 | 2.936 | 52.07 | 0.872 |
| [Wide, sparsely sampled tube](straight_tube_wide_sparse/index.md) | 3 | 13.422 | 13.339 | 53.38 | 3.492 |
| [Dumbbell](dumbbell/index.md) | 3 | 45.921 | 45.886 | 55.71 | 11.658 |

Total batch wall time: **164.953 s**. Summed worker CPU: **164.602 s**. Maximum worker RSS: **56.59 MiB**.

The host CPU was **Intel Xeon E5-2630 v4 at 2.20 GHz**, Linux x86_64. These are
single samples on shared infrastructure, without an exclusive resource
reservation. Workers had at most 2 GiB address space, 180 CPU seconds and 240
wall seconds. Memory/pressure was monitored every five seconds; no case was
stopped or deferred. The parent's separate peak RSS was 24.77 MiB. Peak memory
is measured per case worker; independent per-probe memory peaks were not measured.

Each case receives/validates its existing original hull proof once and reuses
that immutable geometry across probes. Every persisted probe model independently
rechecks hull equality. Hull construction from scratch is not included. The
following phase totals explain most of the measured cost; small startup,
serialization and shutdown overhead is included only in the complete totals.

| System | Initial receiving / hull check (s) | Saved-model checks, all probes (s) | Queries / proof checks (s) | Extra tetrahedral partitions (s) |
| --- | ---: | ---: | ---: | ---: |
| Regular tetrahedron | 0.422 | 0.011 | 0.113 | 1.748 |
| Closed shell | 12.394 | 48.768 | 0.747 | 0.000 |
| Shell with an opening | 9.621 | 27.666 | 0.505 | 0.000 |
| Narrow, densely sampled tube | 0.872 | 1.317 | 0.600 | 0.000 |
| Wide, sparsely sampled tube | 3.492 | 9.218 | 0.498 | 0.000 |
| Dumbbell | 11.658 | 33.372 | 0.708 | 0.000 |

## All nineteen observations

`Unknown` is an unavailable global answer, not zero regions. The last column is
the probe phase after shared case receiving, including its own saved-model
recheck. Exact CPU and per-phase samples are retained in the downloads.

| System | Probe (Å) | Origin | Valid axis rays | Additional selected checks | Complete component count | Profile time (s) |
| --- | ---: | --- | ---: | --- | --- | ---: |
| Regular tetrahedron | 1.2 | free | 0/6 | 4/4 face rays valid | Unknown | 0.899 |
| Regular tetrahedron | 1.4 | free | 0/6 | — | Unknown | 0.839 |
| Regular tetrahedron | 1.7 | blocked | 0/6 | — | 0 | 0.137 |
| Closed shell | 0.05 | free | 0/6 | — | Unknown | 12.266 |
| Closed shell | 0.2 | free | 0/6 | — | Unknown | 12.371 |
| Closed shell | 1.4 | free | 0/6 | — | Unknown | 12.452 |
| Closed shell | 5 | blocked | 0/6 | — | Unknown | 12.465 |
| Shell with an opening | 1.4 | free | 1/6 | — | Unknown | 9.446 |
| Shell with an opening | 3 | free | 0/6 | — | Unknown | 9.420 |
| Shell with an opening | 5 | blocked | 0/6 | — | Unknown | 9.333 |
| Narrow, densely sampled tube | 1.2 | free | 2/6 | bent interior reference: valid | Unknown | 0.689 |
| Narrow, densely sampled tube | 1.4 | blocked | 0/6 | bent interior reference: valid | Unknown | 0.656 |
| Narrow, densely sampled tube | 2.5 | blocked | 0/6 | bent interior reference: invalid candidate | Unknown | 0.600 |
| Wide, sparsely sampled tube | 1.4 | free | 2/6 | — | Unknown | 3.308 |
| Wide, sparsely sampled tube | 2.5 | free | 2/6 | — | Unknown | 3.241 |
| Wide, sparsely sampled tube | 5 | blocked | 0/6 | — | Unknown | 3.197 |
| Dumbbell | 1.4 | free | 0/6 | chamber axis: valid; chamber anchors free/free | Unknown | 11.365 |
| Dumbbell | 2.2 | blocked | 0/6 | chamber axis: invalid candidate; chamber anchors free/free | Unknown | 11.361 |
| Dumbbell | 6 | blocked | 0/6 | chamber axis: invalid candidate; chamber anchors blocked/blocked | Unknown | 11.388 |

### Regular tetrahedron

At 1.2 Å, the four face-centroid paths are all free; the six coordinate-axis
paths are all blocked. This illustrates why a finite choice of directions can
miss access. At 1.4 Å the origin remains free while the four tested face paths
fail. Those failures alone are not an enclosure proof.

The fresh tetrahedral partition produces rigorous free-volume enclosures. Its
1.7 Å full cover certifies zero components and exact zero volume. The positive
profiles have conservative bounds and no complete component count or requested
precision. Displayed decimal lower bounds are rounded down and upper bounds up;
downloads retain the exact rational endpoints in nm³.

| Probe (Å) | Free-volume lower bound (nm³) | Free-volume upper bound (nm³) | Global count |
| --- | ---: | ---: | --- |
| 1.2 | 1.60632226963e-06 | 0.0135108435400 | Unknown |
| 1.4 | 1.40553198592e-06 | 0.0104941703177 | Unknown |
| 1.7 | 0 | 0 | 0, complete |

### Closed shell

The origin is free at 0.05, 0.2 and 1.4 Å, and occupied at 5 Å. None of the six
fixed axis rays is free. **This does not certify a sealed shell:** the earlier
0.05 Å reference independently establishes 13 access paths along other
directions. Those paths are not replayed by this query policy. Likewise, this
run's occupied 5 Å origin does not replace the older whole-hull cover reference.
Global connected-region count and a precise free volume remain unknown here.

### Shell with an opening

At 1.4 Å the origin and the +Y path to the exact hull boundary are free. At 3 Å
the origin remains free but all six tested axis paths fail. At 5 Å the origin
is occupied. The first result certifies one supplied route; it does not count
all boundary patches. The later failures do not independently prove enclosure
or full exclusion. Earlier complete references retain their separate scopes.

### Narrow, densely sampled tube

At 1.2 Å, both axial rays and the selected bent interior polyline are free.
At 1.4 Å the origin is occupied and those origin-based rays fail, but the bent
polyline remains continuously free against **all 81 atoms**. At 2.5 Å that
candidate also fails. A blocked straight route can coexist with another free
route; rejecting the last tested candidate does not prove all routes absent.
The older complete exclusion reference at 2.5 Å is not reclassified as a newly
computed general-cover certificate by this run.

### Wide, sparsely sampled tube

At 1.4 and 2.5 Å the origin and the two axial hull-reaching rays are free.
Together these rays provide a continuous axis through the finite hull. They do
not enumerate physical ends or disconnected small regions. At 5 Å the origin
is occupied and all tested rays fail. Complete exclusion remains established
by its older separate reference, not by these point/path failures.

### Dumbbell

At 1.4 Å both named chamber anchors are free and their supplied connecting axis
is continuously free. At 2.2 Å both anchors remain free, while the origin is
occupied and that connecting candidate fails. This run **does not certify that
the anchors are disconnected**; that stronger conclusion belongs to the earlier
separator reference. At 6 Å both anchors and the origin are occupied; this is
not a new whole-domain exclusion proof. No global region count is assigned.

## Evidence and next development gate

The run retains **305 checked query outcomes**: **187 accepted proofs** and **118 invalid path candidates**. These are successful checks of their declared outcomes, not that many detected regions. **One of 19 profiles** receives a complete global count; the other **18 remain unknown** under the available routes.

Producer/source and protocol are fixed at
`2b21cb2ee63093734ff71f1f70bd4ede7a53ebbb`. The archive retains exact models,
all proposed certificates and checked outcomes, worker logs/resources, original
inputs/proofs/references and the exact standalone checker source. A manifest
binds every included byte. Saved proof checking needs no DFND or quantity
dependency; full receiving needs the recorded quantity stack and source checkout.

- {download}`Structured summary <artifacts/reference_validator_panel_v1/summary.json>`
- {download}`Frozen protocol <artifacts/reference_validator_panel_v1/protocol.json>`
- {download}`Measured receiving receipt <artifacts/reference_validator_panel_v1/receiving_receipt.json>`
- {download}`Proofs, exact models and checker <artifacts/reference_validator_panel_v1/receiving.zip>`
- {download}`Archive manifest <artifacts/reference_validator_panel_v1/bundle_manifest.json>`

All 355 earlier frozen case files retain their bytes. These observations do not
change DFND, Topography labels or the current #181/#180/#184/#188 dispositions.
There is no third-party speed/accuracy comparison or protein generalization.

The next scientific gate is complete hull-clipped free-region construction,
including separation and boundary incidence, followed by certified per-region
volume precision. Execution of all 19 profiles here is coverage of the current
queries; it does not complete the planned P5 qualification or make the developer
validator a supported public API.
