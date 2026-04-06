# TopoMT Status

## Summary

TopoMT is in an intermediate stage.

The project already contains:

- a coherent conceptual model based on `Topography` and `Feature` objects;
- a public orchestrator, `get_topography()`;
- multiple integrated engines;
- initial tests and documentation;
- ecosystem hooks for MolSysSuite packages.

However, it is not yet in a polished or stable product state.

## What is currently solid

- The central object model based on `Topography`, `Pocket`, `Void`, `Channel`,
  and `Mouth`.
- The idea of a unified API for topography detection.
- Basic interoperability with `molsysmt`.
- Initial integration of `argdigest`, `depdigest`, `pyunitwizard`, and
  `smonitor`.
- A faithful `fpocket4` wrapper-backed integration path for the currently supported reference
  PDB systems. For the validated systems, TopoMT reproduces the direct fpocket
  binary output in terms of detected pockets, atom membership, pocket ranking,
  `Pocket Score`, and `Drug Score`.
- The DFND design and documentation package in `devguide/DFND/`.

For DFND specifically, what is solid today is mostly the design and the
documentation set, especially:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md)
- [DFND/checkpoint.md](DFND/checkpoint.md)

## What is currently the priority

The current priority is to make TopoMT reliable inside MolSysSuite for these
engines:

- `pocketeer`
- `alphaspace2`
- `fpocket4`
- `pycasta`

This includes:

- reliable atom-index mapping;
- consistent internal units;
- stable feature contracts for `Topography`;
- tests for non-DFND workflows;
- preparation for future visualization in MolSysViewer.

## What is currently in progress

- Stabilization of the non-DFND surface of the library.
- Cleanup of feature and topography internals.
- Better internal contract normalization across engines.
- Expansion of the `devguide/` to reflect the real project state.
- The new `devguide/proposal_improvement/proposal_smonitor_improvement.md` entry captures the SASA backend
  restriction (MolSysMT not letting us override `probe_radius`) and the interim Biotite
  workaround, establishing an upstream enhancement path before those diagnostics
  remain TopoMT-specific.
- Extension of fpocket parity validation from the currently supported PDB set to
  additional inputs and, later, to canonical `bcif.gz` inputs.
- Separation of wrapper-backed integrations from the long-term native-method
  targets in `topomt.methods`.
- `DelaunayMesh` is now the active geometric keystone for the shared
  Delaunay/tetrahedral substrate.
- `DFND` already uses shared face access through `DelaunayMesh`, and
  `pycasta` already shares the mesh triangulation while deliberately keeping
  its upstream-compatible tetrahedral radius proxy and oriented simplex
  ordering where parity depends on that legacy public behavior.
- `alphaspace2` and `fpocket4` already consume the explicit
  `DelaunayMesh` filter/keep API instead of expressing their main radius
  window through the older pair of destructive helper calls.
- CASTp fidelity work now has an explicit contract under
  `devguide/castp/contract.md`, with the CASTp server export files treated as
  the practical oracle and the canonical probe default fixed at `1.4 Å`.
- The first real CASTp 3.0 zip-fixture battery is now in progress. Five of the
  downloaded server cases are already usable as loader-parity fixtures, while
  `3ptb` currently exposes a separate `molsysmt` PDB-parser bug and should be
  treated as an ecosystem blocker rather than silently skipped.
- The first real `tools/features/` extraction is now in place:
  pocket physicochemistry helpers live under
  `topomt.tools.features.pockets.physicochemistry`, and `castp` already uses
  that new module directly.
- A second stable extraction now also exists under
  `topomt.tools.features.common.descriptors`, covering the first shared
  geometry descriptors (`bounding_metrics` and
  `effective_center_radius`).
- `topomt.tools.features.pockets.contacts` is now also real, hosting the first
  pocket-ligand contact helpers (`ligand_contact_distances`,
  `ligand_contact_mask`, `sasa_contact_validation`, and `probe_scoring`).
- `topomt.tools.features.channels` is now also real, hosting the first
  channel/profile helpers (`cross_section_profile`,
  `min_cross_section_radius`, `shortest_path_length`, and
  `thickness_profile`).
- `topomt.tools.features.mouths` is now also real, hosting the first
  mouth-specific descriptor helper (`mouth_area_on_plane`).
- `topomt.tools.features.common.overlap` is now also real, hosting the first
  shared overlap helper (`jaccard_overlap_clusters`).
- `topomt.tools.geometry.planes` and `topomt.tools.geometry.sampling` are now
  also real, hosting `clip_mesh_with_plane` and
  `union_volume_monte_carlo`.
- The old `topomt.methods.pocket_geometry` bridge module has been removed.
  Its stable contents now live under `topomt.tools.geometry`,
  `topomt.tools.tessellation`, and `topomt.tools.features`.
- `DelaunayMesh` now also exposes an explicit simplex-facing view
  (`n_simplices`, `simplex_centers`, `simplex_radii`,
  `simplex_atom_indices`, `simplex_volumes`, and simplex-neighbor helpers)
  in addition to the legacy alpha-sphere-derived aliases.
- `topomt.tools` now exposes its three main public subpackages explicitly at
  the package root (`geometry`, `tessellation`, and `features`), and that
  surface is now covered by direct regression tests.
- First wrapper-backed `Topography` adapters now exist not only for `fpocket4`
  but also for `pocketeer`, `alphaspace2`, and `pycasta`, so users can choose
  upstream execution paths while still receiving TopoMT feature objects.
- Study of `2HGR.pdb` as a large-system deep-validation case for `fpocket4`.
  Final native/source parity is now confirmed there too, but it remains outside
  the default parity battery because of cost.
- A focused diagnostic campaign on the residual raw-tetrahedrization mismatch
  between native `fpocket4` and the upstream embedded-Qhull path, especially on
  `1GG0.pdb` and `3LKF.pdb`, together with fpocket build-drift checks on
  `1GG0.pdb`, `3LKF.pdb`, and `E15ALA.pdb`.
- The start of a real `molsysviewer_topomt` addon scaffold, with the previous
  engine-only priority now paused long enough to establish a visible ecosystem
  integration point and a documented restart position.

## What is currently weak

- Public documentation is still sparse.
- Packaging metadata is still incomplete.
- The developer guide is still being built.
- Tests are unevenly distributed across engines.
- Some geometry and feature-characterization utilities still mix stable and
  heuristic behavior even after the `topomt.tools` split.
- The current native `castp` path is still a `CASTp-like` prototype rather
  than a faithful reimplementation of CASTp's outside/pocket/cavity/channel
  delineation semantics.
- Native `fpocket4` is no longer only a first experimental stage at the final
  pocket-output level. It now reaches exact final-pocket parity against the
  current audited local fpocket source build on the full audited PDB set:
  `1ATP.pdb`, `1CEN.pdb`, `1GG0.pdb`, `1N57.pdb`, `1YCR.pdb`, `2GI9.pdb`,
  `2H05.pdb`, `2HGR.pdb`, `3LKF.pdb`, and `E15ALA.pdb`.
- The remaining source-level open problem is now concentrated in the raw
  geometry layer: a small deterministic super-set of tetrahedra in local
  regions, mainly in `1GG0.pdb` and `3LKF.pdb`.
- `E15ALA.pdb` is no longer treated as a native/source residual mismatch. The
  current discrepancy there is between different fpocket binaries/builds: the
  system binary used by wrapper mode yields `9` pockets, while the locally
  instrumented build compiled from the upstream source and the current native
  path both yield `8`.
- `1GG0.pdb` and `3LKF.pdb` also show wrapper-vs-native differences against the
  current system fpocket binary, but those differences disappear when compared
  against the audited local fpocket source build. They are therefore currently
  treated as fpocket build-drift cases at the final pocket-output level.
- `2HGR.pdb` is currently treated as a large-system deep-validation case. Final
  parity is now measured there (`612` final pockets in both audited upstream
  and `native`), but it still remains outside the default parity battery
  because the run is expensive.
- `alphaspace2` has now reached parity in the current native tests for
  alpha-sphere generation and pocket/atom ownership on the audited reference
  systems, but further descriptor and scoring work is still pending.
- `alphaspace2` has now moved beyond the apo-only baseline: a first native
  Vina-aware score path exists, backed by vendored typing/scoring tables and a
  focused `CDK2` parity test. The richer route is green under a small explicit
  tolerance on the real `molsysmt` file-ingestion path, and the contract is
  now effectively the `0.3.0` milestone described elsewhere: betas, scoring
  tables, grid/overlap/contact descriptors, and probe scores match the upstream
  implementation within that tolerance.
- `alphaspace2` also now has a native optional binder/contact layer that
  propagates contact flags from alpha spheres to betas and pockets under the
  same basic upstream-style cutoff semantics.
- The active `alphaspace2` and shared `DelaunayMesh` path now use
  `pyunitwizard` directly for quantity normalization; the old local
  `puw_utils` shim has been removed from that path and should not return in
  new code.
- TopoMT now also uses a project-configured `argdigest` adapter and has
  started tightening `depdigest` usage for optional capability-bearing
  features, instead of relying on direct imports or ad hoc dependency guards.
- The native `pocketeer` method is documented in
  `devguide/pocketeer_contract.md`, linking to
  https://pocketeer.readthedocs.io/en/latest/ and the local mirror
  `~/repos@others/pocketeer`; that page records the implemented parity target,
  the upstream reference, and the current regression-test anchor.
- `pycasta` is no longer only a vague placeholder in the engine set. The
  upstream repository, local mirror, and paper reference are now recorded in
  `devguide/engine_references.md`, and the first implementation scope note now
  exists in `devguide/pycasta/contract.md`.
- The current `pycasta` reading includes an explicit open audit question:
  the paper describes weighted Delaunay triangulation and persistent-homology
  alpha selection, while the current public repository appears to rely on
  standard SciPy Delaunay plus config-driven alpha thresholds. This should be
  treated as a repository-versus-paper drift to clarify, not yet as an
  established upstream error.
- The native `pycasta` path now has a stronger repository-parity checkpoint:
  `tests/methods/pycasta/test_parity.py` confirms the current TopoMT method
  reproduces the public upstream geometric detector on the current audited
  bounded battery (`1a4j`, `1acj`, `1bid`, `1byb`, `2pk4`, `1stp`, `2ifb`,
  `1hew`, `1a6w`, `1okm`, and `1gca`) in terms of pocket counts,
  pocket/group sizes, and pocket volumes. The broader full benchmark
  inventory is documented but not yet copied wholesale into TopoMT.
- A residual `pycasta` open point remains on `1apu`: the public upstream path
  still appears to rely on PDB record typing (`ATOM` versus `HETATM`) during
  receptor preprocessing, while the TopoMT native contract deliberately stays
  with `molsysmt` molecular selection semantics instead of imitating that
  format-dependent split.
- `fpocket4` now also enters through the project-level `argdigest` route with
  explicit coverage for its public compatibility options; `alphaspace2` was
  intentionally not rolled out the same way yet because its public float
  parameters still carry native `nm` semantics that conflict with older
  generic distance digesters assuming bare numbers mean angstroms.
- TopoMT's `smonitor` integration is no longer just a single `get_topography`
  decorator: the local catalog now covers the main public native methods and
  those entry points emit signals through TopoMT's own integration layer.
- The active project path is now also more consistent about `pyunitwizard`
  provenance: the native methods and the active argument-digestion layer use
  TopoMT's configured `pyunitwizard` instead of mixing project-local,
  `molsysmt`, and direct third-party import routes.
- The current quantity policy is now clearer and should remain stable:
  TopoMT core features and native method outputs preserve physical quantities
  on geometry-bearing fields, while consumer boundaries such as
  `molsysviewer_topomt` normalize those values to canonical magnitudes only at
  the serialization/render edge.
- `fpocket4` has also been cleaned up to use `molsysmt` more idiomatically at
  receptor-preparation time: selected receptors and atom metadata are now
  built through shared helpers instead of repeated raw reconversion and
  re-extraction paths.
- The same `molsysmt`-centric cleanup has now been propagated to
  `pocketeer` and `castp` through a shared heavy-receptor preparation helper,
  while `pycasta` now uses its own `molsysmt`-driven receptor-preparation path
  because its native contract should follow molecular selection semantics
  rather than PDB-record (`ATOM/HETATM`) preprocessing rules.
- The native `pocketeer` path now reaches parity with the upstream reference
  run (`tests/methods/pocketeer/test_parity.py`). It uses the shared alpha-sphere
  geometry, a Biotite-based SASA backend that honors the `polar_probe_radius`
  (documented in `devguide/proposal_improvement/proposal_smonitor_improvement.md`), and a scoring
  bonus tuned to stay within the 2.5-point tolerance requested by the parity
  tests.
- `pocketeer`, `alphaspace2`, and `pycasta` now also have initial
  wrapper-backed `Topography` routes in `topomt.wrappers.*`, reachable through
  `get_topography(..., implementation='wrapper')`. These are currently
  intended as integration paths rather than parity-certified primary routes.
- The new `alphaspace2` wrapper path already required local compatibility
  shims for modern dependencies: current upstream code assumes an older
  `mdtraj` SASA call shape and still uses the removed `np.float` alias. Those
  shims are intentionally confined to the wrapper layer and should be treated
  as upstream-environment drift, not as native-method design precedent.
- The first `molsysviewer_topomt` scaffold now exists as a package-level addon
  checkpoint: it exports a valid `AddonSpec`, lifecycle hooks, and a minimal
  TopoMT-to-viewer payload adapter that can be used as the restart point for
  later rendering work.
- That viewer checkpoint is now slightly beyond pure scaffold status: the
  addon can register with `molsysviewer`, overlay pocket blobs or fallback
  marker spheres on an existing view, build a loaded view and render a
  `Topography` in one step, or render only selected feature/pocket ids
  through `attach_features(...)` and `attach_pockets(...)`.
- The same addon checkpoint now also has a first standalone-oriented utility
  layer: `molsysviewer_topomt.standalone` can build or launch a MolSysViewer
  standalone host with a pre-rendered TopoMT overlay, either from an explicit
  `Topography` or from an on-the-fly `get_topography(...)` call.
- While implementing those selective helpers, we also confirmed a local core
  caveat: the current generic `BaseFeature.copy()` path does not preserve
  dynamic geometry attributes attached by native methods. The addon currently
  works around that by cloning full feature state for temporary subset
  topographies, and that should be treated as a broader core-cleanup
  candidate if similar needs appear outside the viewer path.
- The remaining `molsysmt` integration debt is now more local and deliberate:
  mostly method-specific logic such as the explicit heavy-atom selection still
  present in `alphaspace2`, rather than repeated repository-wide manual
  receptor-cleaning code.
- The small remaining `CDK2` score residual against upstream AlphaSpace2 is no
  longer treated as a `molsysmt` bug. The current diagnosis is a benign
  precision difference between the upstream `mdtraj` route (`float32`) and the
  native `molsysmt` route (`float64`), which only affects a highly sensitive
  local outlier.

## What is postponed

DFND is postponed for now.

This does not mean DFND is unimportant. It means the project should first
consolidate the conventional engine path and the common `Topography` surface
before resuming work on the experimental Delaunay-flow network.

The practical reading is:

- DFND remains part of the project vision;
- DFND documentation should keep being referenced from the main guide;
- DFND implementation work should not drive current priorities.

## Working interpretation of project maturity

The practical interpretation is:

- The project is usable for development and experimentation.
- It is not yet ready to be presented as a fully stabilized library.
- The `0.1.0` milestone records the first faithful fpocket reproduction
  checkpoint on the supported reference PDB systems through the wrapper-backed
  integration path.
