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
- [topomt/alpha_spheres/alpha_spheres.py](/home/diego/repos@uibcdf/topomt/topomt/alpha_spheres/alpha_spheres.py)
- [topomt/io/load_CASTp.py](/home/diego/repos@uibcdf/topomt/topomt/io/load_CASTp.py)

This is the surface that should be stabilized first.

## Priority engines

For the current development cycle, the important engines are:

- `pocketeer`
- `alphaspace2`
- `fpocket4`
- `pocket_geometry`
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

### `wrappers/`

[topomt/wrappers/](/home/diego/repos@uibcdf/topomt/topomt/wrappers) contains useful code and
reference material, especially around fpocket, but it is not yet clearly
positioned relative to the higher-level method API.

This area should be treated as transitional until its role is described more
explicitly.

## Experimental areas

### `pocket_geometry`

[topomt/methods/pocket_geometry.py](/home/diego/repos@uibcdf/topomt/topomt/methods/pocket_geometry.py)
contains useful geometry helpers, but also mixes several responsibilities and
some more exploratory pieces.

It should be treated as a mixed stable/experimental area.

### AFND

AFND is an explicit experimental track with rich design documentation in:

- [AFND/Overview.md](AFND/Overview.md)
- [AFND/Technical_Design.md](AFND/Technical_Design.md)
- [AFND/checkpoint.md](AFND/checkpoint.md)

AFND is part of the project vision, but not part of the immediate stabilization
priority.

## Practical rule for contributors

When making new changes:

- prefer building on `get_topography()`, `Topography`, and the feature model;
- avoid extending legacy helpers unless there is a strong reason;
- document clearly when a module is experimental, transitional, or part of the
  intended stable surface.
