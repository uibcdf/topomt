# Checkpoint — kernel/catalog refactor (pause point)

Date: 2026-06-24. Resume point for the kernel/catalog split. Authoritative target:
[`taxonomy_architecture_decision.md`](taxonomy_architecture_decision.md). This file
is a *where-we-are*, not a re-derivation.

**Status: phases 1-4 done** (10 commits, `305f896`..`aff20cd`; all additive,
green, the catalog coexists with the legacy family, the viewer is untouched).
**The solo-doable refactor is complete.** What remains is phase 5 -- the
**coordination-gated** step (retire `family`, re-type `feature_type`, viewer) --
plus additive phase-3 refinements. Next move: coordinate phase 5 with the
collaborator (the viewer owner).

## Why (pre-validation verdict, before the refactor)

DFND was run on **8 real proteins** with known ligands (3ptb, 1ATP, 3LKF, 1stp,
2ifb, 7cpa, 1blh, 1hyt). Under the correct, characterization-first criterion --
**does the functional site appear in the characterization?** (not: is it ranked
druggable, which is not topological) -- **8/8 sites appear**: enclosed pockets as
chambers, open clefts (kinase/thermolysin) as funnel/transit space, each form
honestly reflecting the site's physical nature. The dominant real-protein
phenomenon is the **mega-pocket / access funnel** (the binding site is a sub-feature
of one large wet component): a *feature*, not a bug -- DFND gives the site in its
access context, which isolated-pocket tools discard. Practical confidence
(characterization, not druggability ranking): ~75%. The refactor's two-level
premise (component = access landscape; chambers/voids = sub-sites) was validated.

## Done (all additive, green, no behaviour change)

| Phase | What | Commits |
| --- | --- | --- |
| **1. Inversion** | `topomt/dfnd/classify.py` is the single classification source: `classify_topology(n_external_links, n_resident_nodes, n_wall_faces)` reproduces every family (cross-product + percolating override). `graph.py` delegates (`family = classify_topology(...)`); `_classify_component` is a delegating wrapper. The green suite with identical strings **is the completeness proof**. | `305f896` |
| **2. Grounded boundary layer** | `_attach_boundary_helpers` -> `component.boundary`: `n_connected_walls` (clusters of non-permeable boundary faces; `== 0` is percolating), `n_dry_contacts` (interface = `>= 2`), `n_septa` (wet<->wet constrictions), per-wall composition (coast/exterior/constriction). | `8988a6f`, `ab10c8a` |
| **3. Catalog morphology (core)** | `classify.classify(...) -> {name, marginal}` refines the 1-mouth resident family by aperture (pocket=occluded / groove=open), exposed as `component.classification` **alongside the unchanged `family`**. `morphometrics['per_mouth_occlusion']` (per-mouth entrance constriction). | `3d6ef95`, `7013551` |
| **4. Reconciliation** | Docs: known_limitations L1.1/L3.1, feature_definitions §5 (reframe, not delete). output_status reframed to also track the catalog: kind `classification`, registers `groove`, guard `test_catalog_classification_is_total` ("classify is total"), coexisting with the kernel-family guard. nonresident_passage already diagnostic (non-curated). | `8ebcc0e`, `2fa6fa4` |

New surface (all additive, coexisting with the legacy model): `classify.py`
(`classify_topology`, `classify`, `GROOVE`); `component.boundary`,
`component.classification`; `morphometrics` fields `per_mouth_occlusion` (+ the
earlier `occlusion`/`occlusion_gap`/`enclosable`/`buriedness`/`deepest_chamber`).

## Remaining (where the nature changes -- resume here)

The work done so far is additive. The remaining steps are **not** purely additive
and/or need coordination -- this is why we paused.

- **Phase 3 rest** (additive, low-risk): full per-threshold confidence (units are
  heterogeneous -- probe-radius / ratio / count, see decision §7); characteristic
  radii as a first-class derived view (seal/residence-death exist as
  `mouth_radius`/`interior_radius`; add merge radii = septa `R_gate`, split radii =
  throat `separation_radius`); re-home morphometrics/hierarchy as derived helpers.
- **Phase 4** -- **done** (`8ebcc0e`, `2fa6fa4`). output_status now tracks the
  catalog (kind `classification`, `groove` registered, totality guard) alongside the
  kernel-family guard; the two coexist during the migration. nonresident_passage is
  already diagnostic/non-curated, so no `SIDE_BY_FAMILY` change was needed. Minor
  remaining: doc pointers (Glossary, Algorithm, Overview, interfaces,
  metrics_contract) and the septum->constriction rename in prose (low priority).
- **Phase 5** (coordination) -- **topomt side wired** (`42e7be5`): both paths to the
  viewer now carry the catalog. Front **1.a** (components → layer 0): the bridge
  attaches `feature.classification` ({name, marginal}: pocket / `open_concavity` /
  …), `feature.morphometrics`, `feature.boundary`, `feature.motifs`. Front **2**
  (components → viewer direct): `component.classification`/`morphometrics`/`boundary`
  are exposed by build_components. **Viewer side (the coordinated part)**: Front
  **1.b** -- the feature payload includes `feature.classification` and the feature
  renderer keys on it; Front **2** -- the component renderer keys its representation
  map on `component.classification['name']` (add `open_concavity → groove_ribbon`)
  instead of `component.family`. Morphology stays additive (`feature_type` unchanged)
  until a later coordinated re-typing; `groove` is now the generic `open_concavity`
  (see feature_catalog.md). Optional later: unify Pocket/Void/Channel into one
  parameterized class.
- **Deferred**: dry-side dual scheme; systematic real-system validation
  (acceptance bars / PDB panel).

## How to resume

- Tracking tasks: #34 (phase 3 rest -- additive, can be done solo), #36 (phase 5 --
  coordination with the viewer owner). Task #35 (phase 4) is done. Each carries a
  precise note of what is left.
- Target/contract: `taxonomy_architecture_decision.md` (the rule, the 7 gaps, the
  migration §9, the impl status §10, the reconciliation debt §11).
- Memory: `project_dfnd_taxonomy_decision.md`.
- Tree is clean; only the collaborator's viewer WIP is unstaged (untouched).
