# Validation and Tests

## Purpose

This document summarizes the current validation surface of the repository and the main testing priorities.

## Current Test Tree

The current tests include conventional engine tests and an active DFND suite:

- [tests/test_dfnd_geometry_primitives.py](/home/diego/repos@uibcdf/topomt/tests/test_dfnd_geometry_primitives.py)
- [tests/test_dfnd_graph_contract.py](/home/diego/repos@uibcdf/topomt/tests/test_dfnd_graph_contract.py)
- [tests/test_dfnd_input_policy.py](/home/diego/repos@uibcdf/topomt/tests/test_dfnd_input_policy.py)
- [tests/test_dfnd_pockets.py](/home/diego/repos@uibcdf/topomt/tests/test_dfnd_pockets.py)
- [tests/test_dfnd_real_system_stability.py](/home/diego/repos@uibcdf/topomt/tests/test_dfnd_real_system_stability.py)
- [tests/test_dfnd_solvent_volume.py](/home/diego/repos@uibcdf/topomt/tests/test_dfnd_solvent_volume.py)
- [tests/test_delaunay_mesh.py](/home/diego/repos@uibcdf/topomt/tests/test_delaunay_mesh.py)
- [tests/test_weighted_delaunay_mesh.py](/home/diego/repos@uibcdf/topomt/tests/test_weighted_delaunay_mesh.py)
- [tests/methods/pocketeer/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/pocketeer/test_parity.py)
- [tests/methods/pocketeer/test_wrapper.py](/home/diego/repos@uibcdf/topomt/tests/methods/pocketeer/test_wrapper.py)
- [tests/methods/alphaspace2/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/alphaspace2/test_parity.py)
- [tests/methods/alphaspace2/test_wrapper.py](/home/diego/repos@uibcdf/topomt/tests/methods/alphaspace2/test_wrapper.py)
- [tests/methods/fpocket4/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/fpocket4/test_parity.py)
- [tests/methods/pycasta/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/pycasta/test_parity.py)
- [tests/methods/pycasta/test_wrapper.py](/home/diego/repos@uibcdf/topomt/tests/methods/pycasta/test_wrapper.py)
- [tests/io/test_load_castp.py](/home/diego/repos@uibcdf/topomt/tests/io/test_load_castp.py)

## What Is Currently Covered Reasonably

- `Topography` smoke behavior and DFND feature conversion;
- DFND geometry primitives (`R_residence`, `R_gate`);
- DFND graph contract, face identity, external links, dry components, dry interfaces, face depth, and dry motifs;
- DFND input-policy failures before triangulation;
- DFND deterministic `volume_solvent_estimate` bounds and batch/scalar consistency;
- DFND small real-system stability and multi-radius monotonicity;
- `DelaunayMesh` behavior;
- focused upstream/native parity for `pocketeer`, `alphaspace2`, `fpocket4`, and `pycasta` on audited bounded batteries;
- first wrapper smoke/parity coverage for `pocketeer`, `alphaspace2`, and `pycasta`;
- import and loader smoke tests.

## What Is Still Weak

- DFND cavity quality is not yet validated biologically or against a benchmark.
- DFND tiny-domain reporting/filter policy is not settled.
- DFND dynamic topology is documented but not implemented.
- `volume_solvent_estimate` is tested as an estimator, not as a publication-grade analytic volume.
- Cross-engine comparison reports are not yet organized into a stable benchmark battery.
- Some conventional-engine deep-validation paths remain environment/build sensitive.

## DFND Validation Interpretation

Current DFND tests establish engineering correctness of the substrate and raw records. They do not yet establish that DFND detects biologically preferred pockets better than existing methods.

The current validated engineering invariants include:

- finite raw records on small real systems;
- stable `Topography` integration;
- monotonic non-increase of resident tetrahedra, permeable face slots, and resident solvent-volume estimate as probe radius increases;
- traceability of faces, external links, dry interfaces, and dry motifs.

## Why Wrapper Tests Are Not Redundant

Wrapper smoke/parity tests remain distinct from native parity suites.

- Native parity checks whether TopoMT native/provider implementations reproduce intended algorithmic semantics.
- Wrapper parity checks whether the actual external package or binary behaves as expected when routed through TopoMT.
- Build/package/environment drift can affect wrappers without implying native-method regressions.

## Practical Testing Priority

1. Keep expanding DFND hardening tests and qualitative reports.
2. Add reporting/filter-policy tests for tiny voids and near-threshold domains.
3. Build a stable small-system comparison battery across DFND and external methods.
4. Keep conventional engine parity/wrapper tests alive as reference checks.
5. Add performance regression checks once DFND build/query costs are better bounded.

## Environment Caveat

The repository targets Python 3.10, 3.11, and 3.12. Results obtained in newer interpreters can be useful for development, but they should not be confused with the official support story.
