# Architecture

TopoMT aims to represent molecular surface topography through a shared object
model rather than through one single detection algorithm.

## Core model

The central object is `Topography`, which acts as a registry of detected
features associated with a molecular system and, optionally, a selection.

The feature hierarchy is organized around:

- `Feature0D`
- `Feature1D`
- `Feature2D`

Concrete feature types currently include:

- `Pocket`
- `Void`
- `Channel`
- `BranchedChannel`
- `Mouth`

## Detection path

The main public orchestration path is `get_topography()`, which dispatches to
different engines and converts their outputs into a common `Topography`
representation.

The currently relevant non-AFND engines are:

- `pocketeer`
- `fpocket4`
- `alphaspace2`
- `castp`
- `pycasta`

## Design principles

The practical design principles are:

- normalize heterogeneous engine outputs into a shared feature model;
- preserve correct atom ownership and local-to-global index mapping;
- use canonical MolSysSuite units and conventions internally;
- keep the representation suitable for later visualization and analysis.

## Relationship to AFND

AFND is a separate architectural track inside TopoMT.

It is relevant for the long-term evolution of richer topographic semantics, but
it should not be confused with the current public stabilization path.
