# TopoMT Architecture

Public semantic direction: [Topography conceptual contract](topography_conceptual_contract.md)
(accepted design, 2026-09-30). Runtime adoption:
[implementation route](topography_implementation_route.md), issues #60–#63.
The responsibilities below distinguish implemented foundations from that target;
they do not announce new Topography registry classes or signatures.

Current delivery priority: [provider pocket output checkpoint](provider_pocket_output_checkpoint.md).
Original-engine outputs have provider-specific provisional classes and shared
pocket access. Full Topography runtime adoption and DFND consolidation are
deferred; the conceptual contract continues to govern their eventual integration.

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

The target additionally makes analysis context, spatial support, participants,
typed relations, evaluations and provenance explicit. These contracts are
pending runtime adoption. A result derives from identified inputs; changing a
live system reference must not silently retarget an already computed result.

### `Feature`

Features are the semantic building blocks of the model.

The base hierarchy is:

- `Feature0D`
- `Feature1D`
- `Feature2D`

`TopographyFeature` denotes the broad semantic umbrella, not an implemented
class. Current registered classes include Pocket, Void, Channel, OpenConcavity,
Groove, Cleft, Mouth, BranchedChannel and Percolating. Native naming is derived
from grounded observations through the [DFND catalog](DFND/feature_catalog.md);
some refinements remain provisional. Convex and mixed-feature promotion remain
future gates. Do not populate a speculative class hierarchy or use Python class
identity as geometric or temporal identity.

Not every raw engine object should become a public feature. DFND, for example,
uses components, external links, dry interfaces and motifs before building
semantic Topography features. The retired intermediate `domain` rung is not
part of the model. Promotion can yield a feature subgraph, but subregion
promotion must establish support and public invariants first.

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

These attribute names do not establish equivalent measures across engines.
Declare support, definition, units, capabilities and source occurrence. Preserve
provider-reported classification separately from a justified TopoMT inference.

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

In addition, `topomt.tools` now acts as the shared geometry, tessellation, and
feature-characterization layer used by those engines.

## `dfnd/` versus `third_party/`

TopoMT needs a strict architectural distinction between native methods and
external integrations.

### `topomt/dfnd/`

This package is the current home of TopoMT's own native method line.

DFND implements TopoMT's native scientific semantics and does not require a
third-party pocket engine at runtime. It uses ecosystem molecular/unit tools
and shared geometry while preserving its own validation and numerical policy.
Benchmarking against another method does not redefine DFND as that method.
Faithful local reproductions of third-party algorithms belong to the provider
namespace below, retaining their original method identity and parity gates.

### `topomt/third_party/`

This package now contains provider-organized integrations with external tools.

Typical responsibilities include:

- invoking an external binary or package;
- parsing or normalizing the external output;
- loading third-party result folders;
- and supporting parity testing or import workflows.

These integrations are part of the runtime surface, but they are no longer
split into a separate top-level `wrappers/` tree.

### Practical reading for the current codebase

The repository now separates native TopoMT code from provider integrations more
explicitly.

The intended end state is:

- `topomt.dfnd.*`: native TopoMT implementation work;
- `topomt.third_party.*`: external-provider integrations and backend-specific
  access paths.

## DFND within the architecture

DFND is TopoMT's native method and semantic reference for public topography.
Its implemented kernel/catalog split separates support and observables from
derived names; the mesh/query split identifies invalidation and context.
Topography expresses those scientific distinctions without requiring users or
third-party adapters to implement a DFND graph.

Relevant design references are:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/Algorithm.md](DFND/Algorithm.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md) — original design (historical)
- [DFND/feature_definitions.md](DFND/feature_definitions.md)
- [DFND/abstract_contract.md](DFND/abstract_contract.md)
- [DFND/component_motifs.md](DFND/component_motifs.md)
- [DFND/numerical_policy.md](DFND/numerical_policy.md)
- [DFND/metrics_contract.md](DFND/metrics_contract.md)
- [DFND/input_policy.md](DFND/input_policy.md)
- [DFND/implementation_status.md](DFND/implementation_status.md)
- [DFND/Implementation_Route.md](DFND/Implementation_Route.md)

DFND already contributes public concavity and Mouth features, accessibility
and interface descriptors, contextual identities and native records. Remaining
scientific validation, provisional morphology thresholds, dry/mixed promotion
and public-contract adoption retain their own gates. Historical green
checkpoints are not current product-matrix evidence.

## Internal geometric keystone

`DelaunayMesh` is the internal geometric keystone of DFND and reusable
Delaunay-based local implementations. It is not a required public support
representation for every external result.

The intended architectural reading is:

- `DelaunayMesh`: primary persistent geometric representation;
- `DelaunayFlowNetwork`: flow-based interpretation of that mesh for DFND-like
  queries;
- `WetComponent`: native decomposition together with its spatial representation;
- `DryComponent`: dry-graph decomposition object built from probe-excluded
  tetrahedra connected through non-permeable faces;
- `ExternalLink` and `DryInterface`: raw boundary/interface records used before
  semantic feature construction;
- feature objects: semantic outputs built from components and validated
  substructures, boundaries, or interface realizations. Planned names are not
  evidence that those promotions have been implemented.

In this model, alpha-spheres remain important but are no longer a keystone
class. They should be understood as a derived view of `DelaunayMesh`, useful
for engines such as `fpocket4`, `pocketeer`, and `alphaspace2`, rather than as
the main architectural ontology.

This keeps the shared geometry infrastructure aligned across:

- `fpocket4`
- `pocketeer`
- `alphaspace2`
- `DFND`

while preserving a clean distinction between:

- geometric substrate;
- flow/topology interpretation;
- feature-level semantics.

## Current internal contract

The practical internal contract for native engine methods should be:

1. Work on a well-defined atom selection.
2. Filter atoms explicitly when needed.
3. Keep a reliable mapping between local indices and original atom indices.
4. Promote justified features with recoverable support and declared
   delimiting/accessibility atom roles; preserve overlapping incidence.
5. Record classification evidence, context, capabilities and provenance while
   preserving the established feature API.

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

Deliver original-provider results under #65 first. Consumers use the small
shared pocket contract while retaining each method's definitions and original
evidence. Existing adapters can be reused privately; returned result objects
have independent ownership. This does not require the following deferred gates.

Adopt the [conceptual contract](topography_conceptual_contract.md) through its
[bounded gates](topography_implementation_route.md): analysis context/support,
participants/relations, contextual evaluations, and provider admission.
Interfaces retain both participant association and spatial realization;
reference-region characterization differs from occupied-assembly geometry.

Third-party preservation/parity remains under its existing plan, followed by
the separate native provider-method review. Neither is a prerequisite to
stating DFND-grounded public semantics. Runtime changes need test-first,
compatibility-aware slices. Original-provider viewer adoption is now explicit
under [#66](provider_output_viewer_checkpoint.md), with provider state separate
from canonical Topography. DockingMT and PharmacophoreMT adoption remain deferred.
