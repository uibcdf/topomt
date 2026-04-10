# API Surface

## Purpose

This document describes the practical status of the TopoMT API surface.

The repository currently contains public entry points, legacy helpers, and
experimental or transitional modules. This should be made explicit so that
developers know which areas to build on and which areas to treat with caution.

## Current public core

The practical public core is centered on:

- [topomt/get_topography.py](/home/diego/repos@uibcdf/topomt/topomt/get_topography.py)
- [topomt/topography/Topography.py](/home/diego/repos@uibcdf/topomt/topomt/topography/Topography.py)
- [topomt/features/](/home/diego/repos@uibcdf/topomt/topomt/features)
- [topomt/delaunay_mesh.py](/home/diego/repos@uibcdf/topomt/topomt/delaunay_mesh.py)
- [topomt/io/load_CASTp.py](/home/diego/repos@uibcdf/topomt/topomt/io/load_CASTp.py)

This is the surface that should be stabilized first.

## Priority engines

For the current development cycle, the important engines are:

- `pocketeer`
- `alphaspace2`
- `fpocket4`
- `pycasta`

These engines matter both because of functionality and because they define the
feature payloads that later need to be consumed by MolSysViewer.

For those payloads, `atom_indices` should be understood as the receptor atoms
that delimit the feature geometrically, i.e. lining or tangential atoms of the
cavity/topographic object.

## Legacy or transitional areas

### `get_pockets()`

[topomt/get_pockets.py](/home/diego/repos@uibcdf/topomt/topomt/get_pockets.py) does not fit the
current `Topography`-centric architecture.

It should be treated as legacy until it is either:

- removed;
- deprecated explicitly;
- or rebuilt on top of the current public model.

### `third_party/`

[topomt/third_party/](/home/diego/repos@uibcdf/topomt/topomt/third_party) now contains the
provider integrations and backend-specific adapters that previously lived under
legacy wrapper paths.

This area is part of the active runtime surface, but most provider internals
should still be treated as integration code rather than long-term stable API.

## Experimental areas

### `tools/`

[topomt/tools/](/home/diego/repos@uibcdf/topomt/topomt/tools) now contains the
shared geometry, tessellation, and feature-characterization helpers that were
previously concentrated in the transitional `pocket_geometry.py` module.

This area should now be treated as the active shared utility layer for
non-engine-specific geometry and characterization code.

### DFND

DFND is an explicit experimental track with rich design documentation in:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md)
- [DFND/checkpoint.md](DFND/checkpoint.md)

DFND is part of the project vision, but not part of the immediate stabilization
priority.

## Practical rule for contributors

When making new changes:

- prefer building on `get_topography()`, `Topography`, and the feature model;
- avoid extending legacy helpers unless there is a strong reason;
- document clearly when a module is experimental, transitional, or part of the
  intended stable surface.
