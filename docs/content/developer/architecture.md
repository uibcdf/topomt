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
- `OpenConcavity`
- `Groove`
- `Cleft`
- `Void`
- `Channel`
- `BranchedChannel`
- `Mouth`
- `Percolating`

The registered class set and a canonical scientific classification are distinct
concerns. Native DFND naming is derived from grounded observations; some
morphological refinements remain provisional. A third-party reported pocket
label does not by itself establish every DFND pocket predicate.

## Detection path

The main public orchestration path is `get_topography()`, which dispatches to
different engines and converts their outputs into a common `Topography`
representation.

The currently relevant non-DFND engines are:

- `pocketeer`
- `fpocket4`
- `alphaspace2`
- `castp`
- `pycasta`

## Design principles

The practical design principles are:

- normalize heterogeneous engine outputs into a shared feature model;
- preserve delimiting/accessibility atom roles, overlapping geometric membership
  and local-to-source index mapping;
- use canonical MolSysSuite units and conventions internally;
- keep the representation suitable for later visualization and analysis.

## Relationship to DFND

DFND is TopoMT's native method and semantic reference. Its geometric support,
observables and catalog classification remain distinguishable. Native substrate
objects live under `topography.dfnd`; the public model permits working with
features without knowing that substrate.

The accepted conceptual direction makes analysis context, spatial support,
molecular participants, typed relations, contextual evaluations and provenance
explicit. Runtime adoption of those contracts is pending; this page does not
announce new classes, call signatures or a changed default engine.

An interface associates participants and describes its spatial realization. A
participant is not necessarily a DFND dry bank, and interface status can coexist
with a Pocket, Void or Channel classification. Contact/occupancy evaluations
declare their definition, support and pose; characterization of a reference
region differs from geometry calculated for an occupied assembly.

External engines preserve their own labels, measurements and artifacts while
declaring which public capabilities their evidence supports. Equal attribute
names do not prove equivalent geometry or measures.

The repository's
[conceptual contract](https://github.com/uibcdf/topomt/blob/main/devguide/topography_conceptual_contract.md)
and [implementation route](https://github.com/uibcdf/topomt/blob/main/devguide/topography_implementation_route.md)
define the decision, compatibility obligations and bounded adoption gates.
