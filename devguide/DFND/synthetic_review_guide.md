# DFND Synthetic Review Guide

Recorded on 2026-05-22. An ordered playbook for reviewing the synthetic systems
one by one — to confirm what DFND gets right and to drive fixes for what it gets
wrong. It ties together the catalog (`topomt/data/synthetic/`), the generators
(`topomt/dfnd/synthetic.py`) and the tests. Every catalogued system has a row.

## How to run a case

```python
from topomt.dfnd import synthetic as syn
from topomt.dfnd.graph import DelaunayFlowNetwork
coords, radii = syn.<generator>(...)                 # or read the .pdb
net = DelaunayFlowNetwork.from_coordinates_and_radii(coords, radii, epsilon=1e-7)
topo = net.get_topography(probe_radius=<probe>, min_size=0)
components = topo['raw']['wet_components']           # wet features
dry = topo['dry']['components']                       # dry banks (interfaces)
```

Conventions used throughout:
- **significant** component = `n_resident_nodes >= 5` (filters sub-probe texture).
- **dominant** component = the one with the most resident nodes.
- families: `void` (0 mouths), `pocket` (1), `channel`/channel (>=2),
  `surface_concavity` (1 mouth, no residence).
- The PDBs are dummy **argon** (1.88 Å); mixed-radii PDBs use other noble gases
  (radius encoded by element). Build/refresh with
  `python devtools/dfnd/build_synthetic_catalog.py`.

Tests that pin each behaviour:
`tests/test_dfnd_synthetic_benchmarks.py`, `tests/test_dfnd_interface_features.py`,
`tests/test_dfnd_pathological.py`. Failure mechanisms are described in
[`pathological_systems.md`](pathological_systems.md); interfaces in
[`interfaces.md`](interfaces.md).

## Recommended review order

1. **Phase 1 — success battery**: confirm DFND still recovers known-good shapes.
2. **Phase 2 — interfaces & adversarial-but-handled**: the harder cases DFND
   already passes.
3. **Phase 3 — pathological (the work)**: grouped by the four diseases; fix a
   disease, then re-run all of its rows.
4. **Phase 4 — robustness regressions**: must stay green after any change.

Each table is `PDB | case (what it is) | probe | check | expected`.

---

## Phase 1 — Success battery (expected to PASS)

| PDB | case | probe | check | expected |
|---|---|---|---|---|
| `argon_cube` | 8 argon at cube vertices; body diagonal = 2·(r_Ar+r_probe) | 1.3 (and 1.4) | family at 1.3 vs exactly 1.4 | 1 void at probe<1.4; **empty at exactly 1.4** (marginal knife-edge) |
| `tetrahedron_void` | minimal 4-atom cell | 1.4 | runs; sanity | runs; no significant component |
| `hollow_sphere_void` | sealed Fibonacci sphere | 1.4 | family, links, volume | 1 void, 0 links, 1000<vol<5000 |
| `hollow_sphere_pocket` | sphere with one polar cap removed | 1.4 | family, links | 1 pocket, 1 mouth |
| `hollow_sphere_leaky` | sphere whose wall leaks small probes | 1.0 & 1.8 | probe sweep | 1.0 leaks (0 voids); 1.8 sealed (>=1 void) |
| `tube_channel` | open cylinder | 1.4 | dominant family, mouths | channel, >=2 mouths |
| `dumbbell` | two chambers + throat | 1.4 & 2.2 | significant voids | 1 void @1.4, 2 @2.2 (volume != connectivity) |
| `solid_ball_control` | filled ball | 1.4 | negative control | no void; all vol<5 |
| `blind_well_d6_r6` | shallow bored well | 1.4 | family count | **fragments to ~3 pockets** (mild over-seg; cf. Disease 1) |
| `blind_well_d8_r6` | deep bored well | 1.4 | dominant family | 1 pocket |
| `blind_well_d12_r6` | very deep bored well | 1.4 | dominant family | 1 pocket |
| `slab_pore_r4_t6` | pore through a slab | 1.4 | dominant family | 1 channel, >=2 mouths |
| `two_voids_gap14` | two disjoint hollow spheres | 1.4 | void count | exactly 2 voids, ~equal volume |
| `surface_bowl_shallow_d2` | shallow surface dent | 1.4 | family, texture | no void; >=1 pocket + small texture pockets |
| `surface_bowl_deep_d6` | deeper bowl | 1.4 | family, texture | no void; dominant pocket + texture pockets |
| `branched_tube_y` | Y junction of three tubes | 1.4 | dominant family, mouths | 1 channel, 3 mouths |
| `nested_spheres` | sphere inside a sphere | 1.4 | void count | exactly 2 voids (core + shell gap) |
| `curved_tube_120` | bent tube (120° arc) | 1.4 | dominant family | 1 channel, >=2 mouths |
| `flask_neck_narrow` | chamber + narrow neck | 1.4 | void presence | chamber sealed -> >=1 void (+ neck pocket) |
| `flask_neck_wide` | chamber + wide neck | 1.4 | void presence | open -> 0 voids |
| `two_openings_pinhole` | sphere, one big + one pinhole opening | 1.4 | dominant family | pocket (pinhole ignored) |
| `two_openings_open` | sphere, two real openings | 1.4 | dominant family | channel, >=2 mouths |
| `asymmetric_dumbbell` | unequal chambers + offset throat | 1.4 & 2.2 | significant voids | 1 @1.4, 2 @2.2 |
| `swiss_cheese_percolating` | block of overlapping carved voids | 1.4 | mega-cluster | 0 significant voids; one dominant cavity >300 residents |
| `swiss_cheese_sparse` | block of wider-spaced carved voids | 1.4 | partial separation | partially separated (several pockets + a void) |
| `void_with_island` | hollow sphere with a central solid island | 1.4 | void count | exactly 1 void (genus intentionally not tracked) |
| `helical_tube` | tube along a helix | 1.4 | dominant family | 1 channel, >=2 mouths |
| `onion_shells_3` | three concentric shells | 1.4 | void count | exactly 3 voids |

---

## Phase 2 — Interfaces and adversarial-but-handled (expected to PASS)

| PDB | case | probe | check | expected |
|---|---|---|---|---|
| `two_blocks_fused` | two blocks, narrow gap | 1.4 | dry bodies | 1 dry body (gap fuses) |
| `two_blocks_interface` | two blocks, solvent-wide gap | 1.4 | dry bodies + lining | 2 dry banks (>=50) + dominant wet component lined by both |
| `three_blocks_interface` | three blocks in a row | 1.4 | dry bodies | 3 dry banks |
| `interface_pocket` | cavity carved at the contact plane | 1.4 | lining bodies | dominant cavity lined by both bodies (minority fraction >0.3) |
| `interface_pocket_open` | interface cavity with a mouth | 1.4 | family + lining | dominant 1-mouth pocket lined by both bodies |
| `three_body_junction` | three blocks at 120° + central cavity | 1.4 | lining bodies | dominant cavity lined by 3 bodies |
| `sliver_sheet` | flat near-coplanar sheet | 1.4 | adversarial (alpha-shape trap) | no void, no significant channel (no false tunnel) |
| `pocket_intruder_open` | sphere with a 3-atom wall mouth | 1.4 | family | dominant pocket |
| `pocket_intruder_sealed` | same + one atom in the mouth | 1.4 | family | dominant void (4th-atom intrusion seals it) |
| `flask_cryptic` | gated chamber | 1.4 & 1.0 | probe sweep | void @1.4 (0 links) -> pocket @1.0 (>=1 link) |
| `rough_surface` | slab with sub-probe bumps | 1.4 | over-reporting | >15 tiny components, max <40 residents (none real) |

Interface body labels: use `topomt.dfnd.interfaces.annotate_interfaces`. The
native (dry-component) route only resolves bodies when a wet layer separates them
(`two_blocks_interface`); tightly fused cases (`interface_pocket`) need explicit
labels.

---

## Phase 3 — Pathological (KNOWN FAILURES — the work items)

"Expected" here is the **current, wrong** behaviour the test pins; "ideal" is the
target after a fix. Grouped by the disease a fixer would tackle together.

### Disease 1 — Fragile single-scale segmentation (priority #1)
| PDB | case | probe | current (wrong) | ideal |
|---|---|---|---|---|
| `pathological_deep_narrow_well` | deep narrow blind well | 1.4 | >=3 stacked pockets | 1 pocket |
| `pathological_long_pore` | long thin through-pore | 1.4 | 0 channels, >=2 pockets | 1 channel |
| `pathological_thin_tube_r20` | tube, radius 2.0 | 1.4 | nothing significant | 1 channel |
| `pathological_thin_tube_r25` | tube, radius 2.5 | 1.4 | pockets, 0 channels | 1 channel |
| `pathological_thin_tube_r30` | tube, radius 3.0 | 1.4 | a spurious void | 1 channel |
| `pathological_oblate_void` | thin disk-shaped sealed void | 1.4 | 2 voids | 1 void |
| `pathological_conical_channel` | tapering (wide→sub-probe) channel | 1.4 | pockets, 0 channels | 1 channel |
| `pathological_star_void` | central chamber + radial arms | 1.4 | fragments; void not dominant | 1 void |
| `pathological_toroidal_void` | donut-shaped (genus-1) sealed void | 1.4 | 2 voids | 1 (genus-1) void |
| `pathological_pocket_in_pocket` | bowl with a deeper well in its floor | 1.4 | >=4 flat pockets | ~2 nested (hierarchy) |
| `pathological_u_channel` | U-tunnel, both mouths on one face | 1.4 | 0 channels + spurious void | 1 channel |
| `pathological_edge_cavity` | bowl at a block corner | 1.4 | >=3 pockets | 1 pocket |

Likely fix: probe-sweep persistence + watershed merging of shallow basins.

### Disease 2 — Dependence on sampling / packing, not geometry
| PDB | case | probe | current (wrong) | ideal |
|---|---|---|---|---|
| `pathological_flat_slab` | flat convex slab (spacing 4.0) | 1.4 | >=1 spurious void | 0 cavities |
| `pathological_parallel_plates` | two plates, 3 Å gap | 1.4 | >=1 spurious void | 0 enclosed voids |
| `pathological_perfect_cube` vs `pathological_jittered_cube` | cubic shell, jitter 0 vs 0.1 | 1.4 | different family counts | identical |
| `pathological_undersampled_sphere` | sphere, sparse wall (spacing 4.6) | 1.4 | channel | void |
| `pathological_patchy_sphere` | closed sphere, one hemisphere sparse | 1.4 | open (channel) | void |
| `pathological_packed_blob_loose` | random blob, min-sep 3.8 (no cavity) | 1.4 | >=5 phantom features (~70–115/1000 atoms) | 0 |

Also a property check (no single PDB): sweeping `hollow_sphere` wall spacing at
fixed probe reclassifies the same cavity void→pocket→channel. Fix direction: the
gate should reason about the implied surface, not the bare Delaunay face.

### Disease 3 — Numerical / threshold instability
| PDB / system | case | probe | current (wrong) | ideal |
|---|---|---|---|---|
| `pathological_marginal_gate_sphere` | wall gate at the probe threshold | 1.4 (8 seeds) | void/pocket/channel flickers across seeds | 1 stable family |
| `argon_cube` (at exactly 1.4) | probe sized to fit exactly | 1.4 | empty (probe "just" doesn't fit) | void |
| marginal residence (`tetrahedron` edge 5.4) | R_residence ≈ probe | 1.4 (10 seeds) | resident in 6/10 seeds | all-or-nothing |
| non-monotone probe (`dumbbell`) | feature count vs probe | 1.4 vs 2.0 | 2 then 5 significant (more at bigger probe) | non-increasing |

Fix direction: explicit degeneracy handling (SoS / consistent tie-break) and a
documented tolerance band around the threshold instead of a hard `>=`.

### Disease 4 — Quantification, radius model, bodies, topology
| PDB / system | case | probe | current (wrong) | ideal |
|---|---|---|---|---|
| `pathological_mixed_radii_shell` | noble-gas mixed-radii wall | 1.4 | differs from uniform argon (same coords) | stable |
| `pathological_two_balls` | two convex balls with a gap | 1.4 | phantom inter-body pocket | 0 (label bodies first) |
| volume accuracy (`hollow_sphere_void`) | void volume vs analytic | 1.4 | estimate ~+40% vs analytic | within a few % |
| isolated outlier (`hollow_sphere` + far atom) | one atom 100 Å away | 1.4 | adds a phantom component | unchanged |
| genus (`void_with_island`) | void wrapping an island | 1.4 | reports 1 simple void | track the handle |

---

## Phase 4 — Robustness regressions (must stay PASS after any change)

| PDB / system | case | probe | expected |
|---|---|---|---|
| `packed_blob_dense` | random blob at vdW contact (min-sep 3.0) | 1.4 | 0 significant features (clean) |
| `two_chambers_septum` | two chambers, 1 Å septum | 1.4 | exactly 2 voids (septum holds) |
| `thin_tube_r35` | tube, radius 3.5 | 1.4 | 1 channel (finally recognised) |
| epsilon stability (`hollow_sphere_leaky`) | tolerance sweep | 1.4 | same family for epsilon 1e-9 … 1e-2 |
| extreme probes (`hollow_sphere_void`) | very large probe | 5.0 / 8.0 | void at 5.0; clean empty at 8.0 |

---

## Working a fix

1. Pick a disease in Phase 3. Run all its rows, reproduce the current behaviour.
2. Make the change (e.g. persistence merging for Disease 1).
3. Re-run that disease's rows: tests asserting the *wrong* behaviour will now
   fail — **update them to the corrected expectation** and move the row's "ideal"
   into "expected".
4. Re-run Phase 1, 2 and 4 to confirm no regression (especially the false-positive
   rate on `packed_blob_dense` and the success battery).
5. Note the change in [`pathological_systems.md`](pathological_systems.md).

Coverage note: every catalogued PDB appears in exactly one Phase 1/2/3/4 row;
property-based checks that are not a single PDB (probe/seed/epsilon sweeps,
volume, outlier) are listed inline in the relevant disease.
