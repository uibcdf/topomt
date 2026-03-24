# Codebase Map

This page gives a short map of the repository from a developer perspective.

## Main package areas

- `topomt/topography/`
  Core `Topography` container and feature-relation logic.

- `topomt/features/`
  Feature hierarchy and concrete feature classes.

- `topomt/methods/`
  Detection engines and geometry-related production logic.

- `topomt/io/`
  Loaders for external results, currently centered on CASTp.

- `topomt/alpha_spheres/`
  Internal alpha-sphere representation and utilities.

- `topomt/wrappers/`
  Wrapper-oriented code, especially around fpocket artifacts.

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
