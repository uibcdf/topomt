# DFND Implementation Status

This document separates the DFND design intent from the current code state.

## 1. Strategic Status

DFND is the native TopoMT pocket/topography method.

External methods and server outputs remain useful for validation and comparison,
but they are not the hidden specification for DFND. CASTp, fpocket,
AlphaSpace2, Pocketeer, and related engines should be treated as references,
not as definitions of DFND semantics.

## 2. What Exists in Code

Current code lives under `topomt/dfnd/`:

- `api.py` exposes `dfnd(...)` (raw-first dict) and `dfnd_to_topography(...)`;
- `graph.py` defines `DelaunayFlowNetwork` (the engine; emits `wet_components`,
  `family`, etc. — the zero-legacy contract per [`object_model.md`](object_model.md));
- `data.py` defines `DFNDData`, the single `topography.dfnd` container
  (`raw / mesh / dfn{ parameters, graph, components }`, mesh/dfn split, and the
  `at_probe(...)` probe re-query that reuses the cached mesh);
- `components.py` defines the typed `Component` / `WetComponent` / `DryComponent`
  and the `Components` registry (mirrors `Topography`), plus the wet motif layer
  (`topological_depth`, `depth_regions`, and experimental
  `throat_candidates` / `chamber_candidates` / `bottleneck`);
- `core/clearance.py` contains the face-gate and tetrahedron-residence clearance solvers;
- `core/permeability.py` contains face permeability logic;
- `core/utils.py` contains geometric helpers;
- `synthetic.py` generates dummy-atom (argon / noble-gas) benchmark shapes with
  topography known by construction;
- `interfaces.py` prototypes interface-feature extraction from raw records
  (the multi-body-lining rule; see [`interfaces.md`](interfaces.md)).

The active implementation now covers the first v1 substrate:

- load a molecular system through MolSysMT;
- accept explicit MolSysMT `selection` plus `hydrogen_policy` and `radii_model`;
- build a standard Delaunay mesh;
- compute `R_residence` for tetrahedra through `tetrahedron_residence_radius`;
- compute `R_gate` for faces through `face_gate_radius`;
- record raw tetrahedron and face states;
- build a finite transit graph for a selected probe radius;
- expose `transit_policy = resident_only | with_connectors`;
- expose `gate_intrusion_policy = flag_only | block_suspect`;
- classify finite components by `n_external_links x has_residence` into a `family`
  (`void` / `pocket` / `channel` / `surface_concavity` / `nonresident_passage` /
  `degenerate_subprobe`); no `_domain` suffix (zero-legacy contract);
- keep `wet_open` only as `has_open_interior`;
- emit `wet_components`, `residence_regions`, `external_links` raw records;
- organize all DFND output under the single `topography.dfnd` (`DFNDData`); the
  public `Topography` top level holds only the promoted features (no `dfnd_*`
  attributes). Wet components promote to `Pocket`/`Void`/`Channel` with mouths as
  child `Mouth` features (provenance `component_id`);
- build a dry complement with dry-edge face records, dry interfaces, dry depth, and first candidate dry motifs.

Validated by active tests so far:

- analytic tetrahedron residence radius for a regular tetrahedron;
- residence-radius tangency with unequal radii;
- analytic `R_gate` for an equilateral face;
- `R_gate` rigid-transform invariance;
- `R_residence` and `R_gate` atom-order invariance;
- access x residence classifier;
- wet-sealed regular tetrahedron toy;
- `dry_open_cut` / transit-connector policy divergence.
- `wet_coast_pocket_1link` classifier regression.
- `channel` end-to-end fixture.
- `nonresident_passage_2links` non-resident multi-link classifier regression.
- `degenerate_subprobe` no-link/no-residence classifier regression.
- public dfnd(...) smoke test exercises MolSysMT file input and input-policy recording.
- get_topography(method=dfnd) now returns a normal Topography object with DFND raw records attached as dfnd_records.
- get_topography(method=dfnd) has a real-system smoke test on topomt/data/CASTp_3.0_server/3ptb.pdb.
- tests/test_dfnd_real_system_stability.py checks engineering stability on small CASTpFold real systems without judging cavity-detection quality, including `selection='all'` versus protein-only composition smoke tests.
- tests/test_dfnd_input_policy.py covers defensive input-policy errors before triangulation.
- alternate-location resolution is explicitly delegated to MolSysMT; DFND v1 does not expose `altloc_policy`.
- devtools/dfnd/run_stability_report.py can generate broader local stability reports; the current checkpoint is devguide/DFND/checkpoint_real_system_stability.md.
- devguide/DFND/checkpoint_input_policy_hardening.md records the current MolSysMT-backed input policy.
- the naked `volume` field is intentionally not exposed; `volume_topological_resident` and `volume_solvent_estimate` remain explicitly named.
- `intrusion_suspect` flag and `block_suspect` policy are covered by a toy test.
- `min_size` filtering now applies to compatibility/reporting views, not raw component decomposition.
- `surface_dent_1link` non-resident one-link classifier regression.
- external-link edge-connectivity clustering.
- Delaunay face identity is tested against oriented-simplex neighbor semantics; see checkpoint_face_identity_external_links.md.
- Basic dry-component invariants and dry-edge face records are covered; see checkpoint_dry_graph_basics.md.
- Dry interfaces and dry-depth propagation are implemented and tested; see checkpoint_dry_interfaces_depth.md.
- Probe-radius monotonicity sweeps on five small real systems are green using one cached `DelaunayFlowNetwork` per system; see checkpoint_probe_radius_sweep.md.
- Query-time thresholding/edge filtering, Topography raw accessors, solvent-volume tests, quality snapshots, and first internal dry motifs are covered; see checkpoint_dfnd_hardening_stint.md and checkpoint_quality_snapshot.md.
- A synthetic-shape battery (65 catalogued dummy-atom PDBs across success,
  interface, and pathological tiers) validates known-ground-truth topography; see
  tests/test_dfnd_synthetic_benchmarks.py, tests/test_dfnd_pathological.py,
  tests/test_dfnd_interface_features.py, and the catalog builder
  devtools/dfnd/build_synthetic_catalog.py.
- ~25 pathological systems pin current failure modes as regression markers
  (segmentation fragmentation, sampling/packing sensitivity, threshold
  instability, quantification/radius/bodies); see
  [`pathological_systems.md`](pathological_systems.md) and
  [`synthetic_review_guide.md`](synthetic_review_guide.md).
- the `topography.dfnd` container, typed `Components` registry, probe re-query
  (`at_probe`), the canonical wet motif layer (topological depth / depth regions),
  and the experimental throat/chamber/bottleneck descriptors are covered by
  tests/test_dfnd_data.py and tests/test_dfnd_pockets.py.

## 3. What Is Not Yet Production-Ready

The implementation is not yet a validated production method.

Known gaps:

- `tests/test_dfnd_pockets.py` is now an active public-API smoke test through MolSysMT input.
- Direct dfnd(...) calls still return the raw-first nested dictionary used for method development and validation.
- get_topography(method=dfnd) currently converts only compatibility void, pocket, and channel components into Topography features; provisional surface-concavity, nonresident-passage, degenerate-subprobe, and dry records remain available through dfnd_records.
- Feature objects receive atom indices, tetrahedron indices, centers, topological resident volume, deterministic local solvent-volume estimate, mouth counts, mouth area, flags, and the raw component record.
- The working `COAST` rule is defined, but its contribution to reported metrics remains a policy decision.
- Face-index, gate identity, shared-face consistency, and external-link clustering have graph-contract coverage; more pathological near-threshold cases still need expansion.
- Basic near-threshold residence and gate cases are covered; broader degenerate and molecular near-threshold sweeps still need expansion.
- Dynamic topology is documented but not implemented.

## 4. Current Documentation Status

The DFND documentation now covers:

- conceptual overview;
- algorithmic model;
- public API contract (`api_contract_v1.md`);
- mathematical primitives;
- technical design;
- feature definitions;
- numerical policy;
- metrics contract;
- input policy;
- dynamic topology;
- pharmacophore extensions;
- risks and future ideas;
- synthetic benchmark design ([`synthetic_benchmarks.md`](synthetic_benchmarks.md))
  and the per-case review playbook ([`synthetic_review_guide.md`](synthetic_review_guide.md));
- known failure modes on synthetic ground truth ([`pathological_systems.md`](pathological_systems.md));
- the interface model and extraction prototype ([`interfaces.md`](interfaces.md));
- the authoritative object model and `component → component → feature` terminology
  ([`object_model.md`](object_model.md)).

The remaining documentation work is to keep the design documents consistent with the active implementation as validation, reporting policy, and performance work continue.

## 5. Immediate Engineering Interpretation

The next DFND phase should continue implementation hardening, not new method invention.

The main objective is to make the existing DFND idea executable, testable, and
consistent with the documented semantics:

- standard Delaunay substrate;
- explicit `R_residence` and `R_gate` physics;
- unambiguous DFN, external-link, and component definitions with the `family`
  axis (`void` / `pocket` / `channel` / `surface_concavity` / …);
- conservative handling of `COAST` as boundary/contact metadata until metric behavior is validated;
- clean `Topography` integration via the single `topography.dfnd` container and the typed `Components` registry;
- active tests and focused checkpoints rather than skipped placeholders.
