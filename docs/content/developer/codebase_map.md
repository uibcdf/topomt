# Codebase Map

This page gives a short map of the repository from a developer perspective.

## Main package areas

- `topomt/topography/`
  Core `Topography` container and feature-relation logic.

- `topomt/features/`
  Feature hierarchy and concrete feature classes.

- `topomt/dfnd/`
  Native TopoMT method line.

- `topomt/third_party/`
  Third-party provider integrations and backend adapters.

- `topomt/io/`
  Loaders for external results, currently centered on CASTp.

- `topomt/delaunay_mesh.py`
  Shared Delaunay substrate and alpha-sphere-derived geometric view.

- `topomt/_private/`
  Internal utilities, digestion helpers, diagnostics metadata, and support
  code.

## Supporting areas

- `topomt/data/`
  Bundled example and reference data.

- `tests/`
  Unit and integration tests.

- `docs/`
  Public documentation.

- `devguide/`
  Internal developer guide and source of truth for ongoing engineering work.

## Practical warning

Not all areas have the same maturity level. The core `Topography` and feature
path is where the current stabilization effort is focused.
