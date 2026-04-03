# Tools Architecture Proposal

## Purpose

This document proposes an internal organization for `topomt.tools` so that
geometry, tessellation logic, feature-specific characterization, and lightweight
visualization helpers stop accumulating inside `topomt/methods/pocket_geometry.py`
as a mixed-responsibility module.

The goal is not to remove useful functionality. The goal is to classify it,
define its semantic scope, and place it under a clearer architectural contract.

## Why `tools/` should exist

TopoMT needs a distinction between:

- `topomt.methods`: algorithms that detect or construct topographical features
  from a molecular system;
- `topomt.tools`: reusable analysis and characterization utilities that operate
  on geometry, tessellation data, or already detected features.

This separation keeps detection engines focused while making shared utilities
more reusable and easier to validate.

## Keystone geometric objects

The `tools/` hierarchy should not absorb TopoMT's keystone geometric objects.

Those objects belong to the core internal architecture:

- `DelaunayMesh`
- `DelaunayFlowNetwork`

`DelaunayMesh` is the primary persistent geometric representation. It should
store the Delaunay simplices and the main derived geometric fields needed by
multiple engines:

- atom coordinates and atom radii;
- simplices, oriented simplices when method parity depends on simplex-local
  ordering, and simplex neighbors;
- simplex-centered geometric descriptors such as circumcenters, circumsphere
  radii, and insphere-derived metrics when needed;
- face-level helpers such as simplex-face atom triples and boundary-face
  records;
- alpha-sphere-derived arrays as a secondary view over the same mesh.

`DelaunayFlowNetwork` should sit above that mesh and provide the
probe-dependent flow interpretation:

- node-state classification;
- face permeability filtering;
- wet/dry decomposition;
- pocket, void, channel, and mouth queries.

As a consequence, `AlphaSpheres` should no longer be treated as a keystone
class. The alpha-sphere representation remains important, but as a derived
view of `DelaunayMesh`, not as the primary architectural ontology.

## Proposed top-level layout

```text
topomt/tools/
├── __init__.py
├── geometry/
│   ├── __init__.py
│   ├── hulls.py
│   ├── meshes.py
│   ├── planes.py
│   ├── primitives.py
│   └── sampling.py
├── tessellation/
│   ├── __init__.py
│   ├── mouths.py
│   ├── tetrahedra.py
│   └── representatives.py
├── features/
│   ├── __init__.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── descriptors.py
│   │   └── overlap.py
│   ├── channels/
│   │   ├── __init__.py
│   │   └── profiles.py
│   ├── pockets/
│   │   ├── __init__.py
│   │   ├── contacts.py
│   │   ├── physicochemistry.py
│   │   └── ranking.py
│   ├── mouths/
│   │   ├── __init__.py
│   │   └── descriptors.py
│   └── voids/
│       ├── __init__.py
│       └── descriptors.py
└── visualization/
    ├── __init__.py
    └── py3dmol.py
```

## Design rule by subpackage

### `tools/geometry/`

General spatial and mesh utilities.

These tools should not depend conceptually on pockets, voids, or channels.
They should remain useful for any future TopoMT feature type.

Examples:

- triangle area;
- convex hull metrics;
- mesh area/volume;
- clipping a mesh with a plane;
- Monte Carlo volume estimation.

### `tools/tessellation/`

Utilities tied specifically to Delaunay/Voronoi/alpha-sphere style
representations and simplex-based reasoning.

This layer is more specific than generic geometry, but still more general than
one individual feature type or one engine.

Examples:

- exact tetrahedral volume;
- boundary-mouth extraction from tetrahedra;
- representative points derived from tetrahedra.
- helper operations that act on `DelaunayMesh` or on its alpha-sphere-derived
  arrays without owning the mesh itself.

### `tools/features/`

Feature-oriented characterization utilities.

This layer should organize methods by semantic feature type rather than by
historical origin inside one engine.

Examples:

- channel profiles and bottlenecks;
- pocket lining physicochemistry;
- pocket-ligand contacts;
- mouth descriptors;
- overlap clustering between features.

### `tools/visualization/`

Only lightweight helper utilities for inspection or simple conversions.

The main interactive visualization path for TopoMT should remain in
`molsysviewer_topomt`, not in the core library.

## Mapping from the current `pocket_geometry.py`

### `tools/geometry/primitives.py`

- `_triangle_area`

### `tools/geometry/hulls.py`

- `convex_hull_metrics`

### `tools/geometry/meshes.py`

- `_mesh_volume_area`
- `marching_cubes_union`

### `tools/geometry/planes.py`

- `clip_mesh_with_plane`

### `tools/geometry/sampling.py`

- `union_volume_monte_carlo`

### `tools/tessellation/tetrahedra.py`

- `analytic_tetra_volume`

### `tools/tessellation/mouths.py`

- `mouth_area_from_faces`
- `mouth_metrics_from_tetrahedra`

### `tools/tessellation/representatives.py`

- `representative_points_from_tetra`

### `tools/features/common/descriptors.py`

- `bounding_metrics`
- `effective_center_radius`

### `tools/features/common/overlap.py`

- `jaccard_overlap_clusters`

### `tools/features/channels/profiles.py`

- `cross_section_profile`
- `min_cross_section_radius`
- `shortest_path_length`
- `thickness_profile`

### `tools/features/pockets/contacts.py`

- `ligand_contact_distances`
- `ligand_contact_mask`
- `sasa_contact_validation`
- `probe_scoring`

### `tools/features/pockets/physicochemistry.py`

- `get_physicochemical_properties`
- `nonpolar_ratio_from_sasa`
- `apolar_ratio`

### `tools/features/pockets/ranking.py`

- `simple_ranking`

### `tools/features/mouths/descriptors.py`

- `mouth_area_on_plane`

### `tools/visualization/py3dmol.py`

- `view_pockets_py3dmol`
- `_color_palette`
- `_element_color`

## Stability classification

The current material should not be treated as equally mature.

### Stable-core candidates

- `analytic_tetra_volume`
- `_triangle_area`
- `mouth_area_from_faces`
- `_mesh_volume_area`
- `convex_hull_metrics`
- `bounding_metrics`
- `effective_center_radius`

### Useful but heuristic

- `mouth_metrics_from_tetrahedra`
- `mouth_area_on_plane`
- `cross_section_profile`
- `min_cross_section_radius`
- `shortest_path_length`
- `thickness_profile`
- `simple_ranking`
- `union_volume_monte_carlo`

### Optional-capability helpers

- `marching_cubes_union`
- `view_pockets_py3dmol`

## Current implementation checkpoint

This architecture is no longer purely aspirational.

The following slices are now already materialized in the repository:

- `topomt.tools.geometry`
  with the first shared mesh and hull helpers;
- `topomt.tools.tessellation`
  with tetrahedral, mouth, and representative-point helpers;
- `topomt.tools.features.common.descriptors`
  with the first shared feature-level geometry descriptors;
- `topomt.tools.features.pockets.physicochemistry`
  as the first feature-oriented extraction from `pocket_geometry.py`.

At the moment, `castp` already consumes the new pocket physicochemistry module
directly, while `pocket_geometry.py` still re-exports the migrated functions as
a compatibility bridge during the larger refactor.

### Domain-specific characterization helpers

- `get_physicochemical_properties`
- `nonpolar_ratio_from_sasa`
- `apolar_ratio`
- `ligand_contact_distances`
- `ligand_contact_mask`
- `sasa_contact_validation`
- `probe_scoring`
- `jaccard_overlap_clusters`

## Practical migration rule

When refactoring the current `pocket_geometry.py` content:

1. move functions without changing behavior first;
2. keep import shims or compatibility re-exports during the transition;
3. add focused tests for the stable-core functions before broader cleanup;
4. only after the structure is stable, revisit names, units, or heuristic
   contracts that need refinement.

## Immediate architectural consequence

The current `AlphaSpheres` responsibilities should be split in two:

- mesh-native structural data should move toward `DelaunayMesh`;
- only sphere-centric convenience queries, if still useful, should remain as a
  lightweight derived view rather than as an independent keystone class.

This allows `fpocket4`, `pocketeer`, `alphaspace2`, and `DFND` to share the
same audited Delaunay infrastructure while still exposing an alpha-sphere view
where that representation is convenient.

## Migration table: `AlphaSpheres` -> `DelaunayMesh`

The current `AlphaSpheres` responsibilities should not migrate as a single
block. They should be split according to whether they describe:

- the primary Delaunay-derived geometric substrate; or
- a sphere-centric convenience view over that substrate.

### Responsibilities that should move to `DelaunayMesh`

- atomic coordinates and atomic radii already normalized for the mesh;
- simplex-to-atom mappings (`points_of_alpha_sphere`-like data when it is
  really tetrahedron membership);
- simplex neighbors and face-derived neighbor relations;
- alpha-sphere centers as Delaunay-derived circumcenters;
- alpha-sphere radii as Delaunay-derived circumradii;
- counts and masks of valid simplices / valid alpha-sphere-derived entries;
- basic geometric filtering by radius or validity;
- cached arrays needed by several methods, even if historically exposed
  through `AlphaSpheres`.

### Responsibilities that should remain outside `DelaunayMesh`

- pocket clustering;
- pocket ranking or engine-specific scores;
- ligand-contact heuristics;
- engine-specific filtering rules;
- feature labeling (`Pocket`, `Void`, `Channel`, etc.);
- any method contract that is specific to `fpocket4`, `pocketeer`,
  `alphaspace2`, or `DFND`.

Those responsibilities belong in:

- `topomt.methods.*`
- `topomt.tools.features.*`
- `topomt.tools.tessellation.*`
- `DelaunayFlowNetwork` when they are part of DFND flow semantics

### Optional residual sphere-centric view

If a dedicated sphere-centric API still proves useful, it should be reduced to
a lightweight derived view, for example through `DelaunayMesh` properties or a
small helper object, not as a keystone class.

Typical examples:

- `mesh.alpha_sphere_centers`
- `mesh.alpha_sphere_radii`
- `mesh.alpha_sphere_atom_indices`
- `mesh.get_alpha_sphere_neighbors()`
- `mesh.filter_alpha_spheres(...)`

## Migration table: `pocket_geometry.py` -> `topomt.tools`

The current `topomt/methods/pocket_geometry.py` mixes general geometry,
tessellation logic, feature characterization, and lightweight visualization.
The migration should split those responsibilities as follows.

### Move first to `tools/tessellation`

These functions are the clearest tessellation-layer candidates and should be
the first migration slice:

- `analytic_tetra_volume`
- `mouth_area_from_faces`
- `mouth_metrics_from_tetrahedra`
- `representative_points_from_tetra`

### Move first to `tools/features`

These functions are better read as feature characterization than as general
geometry:

- `bounding_metrics`
- `effective_center_radius`
- `cross_section_profile`
- `min_cross_section_radius`
- `shortest_path_length`
- `thickness_profile`
- `get_physicochemical_properties`
- `ligand_contact_distances`
- `ligand_contact_mask`
- `probe_scoring`

Suggested destinations:

- `tools/features/common/descriptors.py`
- `tools/features/channels/profiles.py`
- `tools/features/pockets/physicochemistry.py`
- `tools/features/pockets/contacts.py`

### Move first to `tools/geometry`

These are general spatial helpers and should leave `pocket_geometry.py`
without depending on a pocket-specific context:

- `_triangle_area`
- `convex_hull_metrics`
- `_mesh_volume_area`
- `clip_mesh_with_plane`
- `union_volume_monte_carlo`

## Execution plan by slices

The migration should be done incrementally rather than as one large refactor.

### Slice 1: `DelaunayMesh` + stable tessellation helpers

Goals:

- introduce `DelaunayMesh` as the keystone geometric object;
- move the most stable tetrahedron- and face-based helpers into
  `tools/tessellation`;
- keep compatibility shims where needed;
- do not yet try to rewrite every engine around the new class.

Scope:

- define `DelaunayMesh`
- move stable tessellation primitives
- add focused tests for those primitives

### Slice 2: absorb alpha-sphere structural data into `DelaunayMesh`

Goals:

- make alpha-sphere data a derived view of `DelaunayMesh`;
- reduce `AlphaSpheres` to a lightweight view or remove it as a keystone class;
- keep engine behavior stable while the internal substrate changes.

Scope:

- move mesh-native alpha-sphere arrays into `DelaunayMesh`
- expose sphere-centric convenience accessors there
- adapt the engines without changing their semantics

### Slice 3: converge engines on the shared mesh

Goals:

- make `fpocket4`, `pocketeer`, `alphaspace2`, and `DFND` reuse the same
  audited Delaunay substrate;
- reduce duplicated geometry code across methods.

Scope:

- adapt `DFND` to consume `DelaunayMesh`
- adapt `fpocket4`, `pocketeer`, and `alphaspace2`
- keep parity/regression tests green throughout

### Slice 4: migrate the remaining feature-characterization helpers

Goals:

- finish moving the remaining `pocket_geometry.py` content to
  `tools/features` and `tools/geometry`;
- leave only compatibility re-exports or a very thin transitional module.

Scope:

- move descriptors, contacts, physicochemistry, and optional visualization
  helpers
- tighten tests around the new module boundaries

## Immediate consequence for contributors

New utilities should not be added to `topomt/methods/pocket_geometry.py`.

Until the refactor happens, contributors should already think in terms of the
future `tools/` hierarchy:

- general geometry;
- tessellation-specific helpers;
- feature-specific characterization;
- lightweight visualization only when justified.
