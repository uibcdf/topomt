# TopoMT Architecture

## Purpose

TopoMT provides a common representation for molecular surface topography.

The goal is not only to detect cavities or pockets with one particular method,
but to express heterogeneous geometric findings in a shared hierarchy that can
be analyzed, compared, and visualized consistently.

## Core objects

### `Topography`

`Topography` is the central registry for detected features associated with a
molecular system and an optional atom selection.

Its responsibilities are:

- store the detected features;
- assign feature identifiers;
- maintain feature lookup indexes by type, shape, and dimensionality;
- maintain parent/child relations between features;
- preserve the link to the input molecular system.

### `Feature`

Features are the semantic building blocks of the model.

The base hierarchy is:

- `Feature0D`
- `Feature1D`
- `Feature2D`

Topography-specific types currently include:

- `Pocket`
- `Void`
- `Channel`
- `BranchedChannel`
- `Mouth`

Each feature is expected to carry, when available:

- `feature_id`
- `feature_type`
- `shape_type`
- `atom_indices`
- `source`
- `source_id`

For topographic features such as pockets, `atom_indices` should be interpreted
as the atoms that geometrically delimit the feature: lining, tangent, or
osculating atoms of the receptor. They should not be interpreted as arbitrary
nearby atoms selected by a loose distance heuristic.

Engine-specific metadata may also be attached, such as:

- `center`
- `volume`
- `score`
- `mouth_area`
- alpha-sphere or probe-sphere data

## Detection engines

TopoMT currently exposes a public orchestrator:

- `topomt.get_topography()`

This function dispatches to different engines and converts their outputs into a
common `Topography` object.

The relevant non-DFND engines are:

- `pocketeer`
- `fpocket4`
- `alphaspace2`
- `castp`
- `pycasta`

In addition, `pocket_geometry` acts as a geometry utility layer used by some
engines and is likely to become a more explicit part of the production path.

## `methods/` versus `wrappers/`

TopoMT needs a strict architectural distinction between native methods and
external integrations.

### `topomt/methods/`

This package should contain TopoMT's own implementations of the supported
engines.

That means:

- methods should be runnable without requiring the original upstream package or
  binary at runtime;
- methods may be inspired by, validated against, or benchmarked against the
  original engine;
- but the production implementation should belong to TopoMT itself.
- a faithful reimplementation does not mean copying upstream code line by line;
- instead, TopoMT should reproduce the algorithmic semantics while using its
  own code, data model, and ecosystem tools such as `molsysmt`,
  `pyunitwizard`, and the common feature contracts.

### `topomt/wrappers/`

This package should contain helper integrations with external tools.

Typical responsibilities include:

- invoking an external binary or package;
- parsing or normalizing the external output;
- loading third-party result folders;
- and supporting parity testing or import workflows.

Wrappers are useful and should remain available, but they are not the target
architectural endpoint for `topomt.methods`.

### Practical reading for the current codebase

At the moment, the repository contains a mix of native methods and
wrapper-backed transitional paths.

The intended end state is:

- `topomt.methods.*`: native TopoMT implementations;
- `topomt.wrappers.*`: external-tool integrations used for comparison, testing,
  import, or auxiliary workflows.

## DFND within the architecture

DFND should be understood as a separate architectural track inside TopoMT, not
as the definition of the whole library.

Its role is to explore a richer Delaunay-flow interpretation of molecular
topography, with more explicit network semantics for pockets, voids,
channels, and dry components.

Relevant design references are:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/Algorithm.md](DFND/Algorithm.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md)

For the time being, DFND is best treated as:

- a documented experimental subsystem;
- a source of conceptual guidance for future feature semantics;
- a postponed implementation priority.

## Current internal contract

The practical internal contract for native engine methods should be:

1. Work on a well-defined atom selection.
2. Filter atoms explicitly when needed.
3. Keep a reliable mapping between local indices and original atom indices.
4. Return or build `Pocket`-like features with canonical atom ownership.
5. Store geometric metadata without breaking the common feature API.

This local-to-global atom-index mapping is critical for both analysis and
future visualization.

For wrapper layers, the internal contract is different:

1. preserve the upstream semantics as faithfully as possible;
2. parse external identifiers and descriptors without lossy remapping;
3. expose enough information to compare TopoMT against the reference engine;
4. support import and regression testing.

## Units

TopoMT should follow MolSysSuite conventions:

- coordinates in nanometers;
- time in picoseconds;
- temperatures in kelvin;
- angles in radians when derived;
- user inputs and outputs managed via PyUnitWizard.

Internal geometric kernels should operate on raw NumPy magnitudes in canonical
units whenever possible.

## Dependencies

TopoMT is expected to follow the same dependency model used in MolSysSuite:

- hard dependencies imported normally;
- soft dependencies imported lazily;
- dependency checks mediated by `depdigest`.

Optional scientific tools must not leak through top-level imports.

## Architectural direction

The short-term architectural direction is:

1. stabilize `Topography` and feature invariants;
2. normalize engine outputs;
3. strengthen tests around those normalized outputs;
4. expose a viewer-friendly representation for pockets and related features;
5. build the MolSysViewer addon on top of that stable surface.

Longer term, once the non-DFND path is stable, DFND may enrich the architecture
with:

- stronger channel and void semantics;
- dry/wet network decomposition;
- richer topological relations between features.
