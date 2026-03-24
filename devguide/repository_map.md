# Repository Map

## Purpose

This document summarizes what each major part of the repository is for.

It is not a replacement for reading the code, but it should help developers
understand where responsibilities currently live and where the repository still
shows signs of transition.

## Source tree

### `topomt/`

Main Python package.

Important subareas:

- `topomt/topography/`
  Core `Topography` container and registry logic.

- `topomt/features/`
  Feature hierarchy used to represent pockets, mouths, channels, voids, and
  related objects.

- `topomt/methods/`
  Detection engines and geometry-related production code. This includes both
  current priorities and older or more experimental paths.

- `topomt/io/`
  Input/output helpers. Right now this mainly includes loading external CASTp
  results through [topomt/io/load_CASTp.py](/home/diego/repos@uibcdf/topomt/topomt/io/load_CASTp.py).

- `topomt/alpha_spheres/`
  Internal alpha-sphere object model and related helper logic.

- `topomt/wrappers/`
  External wrapper-oriented code, currently focused on fpocket artifacts and
  parsing helpers.

- `topomt/_private/`
  Internal support code: digestion helpers, optional import handling, unit
  helpers, exception definitions, and diagnostics metadata.

- `topomt/data/`
  Bundled example and reference data used by demos and some tests.

## Tests

### `tests/`

Current test suite.

The coverage is still uneven:

- there are basic tests for `Topography`, pockets, alpha-spheres, and CASTp;
- AFND has a dedicated test file of its own;
- some areas, such as loaders and several engines, are still lightly covered.

## Documentation

### `docs/`

Sphinx-based user and developer documentation.

This area contains useful conceptual material, especially:

- the future-oriented feature catalog;
- the future-oriented feature attributes catalog;
- notes on pocket-geometry approaches.

At the moment, the public developer pages under `docs/content/developer/` are
still much thinner than the internal `devguide/`.

### `devguide/`

Internal engineering guide for the repository.

This is where the project should describe:

- current architecture;
- actual status and priorities;
- roadmap;
- internal engineering decisions;
- integration plans with the rest of MolSysSuite.

### `devguide/AFND/`

Dedicated design and planning area for AFND.

This subdirectory is much richer than the rest of the historical `devguide`
and remains the main reference for the AFND track.

## Development tooling

### `devtools/`

Build, environment, and historical development tooling.

This directory contains useful environment definitions, but also clear legacy
material from earlier packaging and CI phases. It should be treated as
partially transitional rather than fully curated.

## Practical interpretation

The repository is organized enough to work productively, but not yet uniformly
mature. Developers should expect:

- a strong conceptual core;
- a partially stabilized code surface;
- mixed levels of maturity across methods, tests, and tooling.
