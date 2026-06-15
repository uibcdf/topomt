# DFND Atom-Index Spaces Checkpoint - 2026-06-14

## Decision

DFND keeps two atom-index spaces because both are necessary:

- `mesh_local`: positions in the selected atom array used to construct the Delaunay mesh and its coordinate arrays;
- `molecular_system`: atom indices in the original molecular system.

The space must be explicit at every boundary. It must not be inferred from the values. NumPy kernels and mesh geometry continue using local indices. Public records, MolSysMT queries, and payloads consumed by a view of the original molecular system use global indices.

No typed NumPy index wrappers are introduced. The contract is enforced through field naming, mandatory `atom_index_space` labels on addon-owned payloads and metadata, centralized conversion helpers, and boundary regression tests.

## Implementation

`molsysviewer_topomt/index_spaces.py` defines the canonical labels and helpers:

- `atom_indices(..., space=...)` validates and normalizes a known space;
- `atom_index_payload(...)` creates labeled addon-owned payloads;
- `mesh_local_from_molecular_system(...)` performs the explicit global-to-local conversion required before indexing cached DFND coordinates.

The viewer audit retained correct local geometry in tetrahedra, faces, barycenters, and graph rendering. It corrected global-to-local leaks in mouth gate rings, dry scaffold geometry, body/contact-sheet grouping, pharmacophore chemistry, and affinity-sphere chemistry. Simplex and feature payloads now declare `atom_index_space='molecular_system'`; face and edge render metadata declare `atom_index_space='mesh_local'`.

MolSysViewer shape methods do not currently expose a general top-level `atom_index_space` argument. The addon therefore validates indices immediately before direct MolSysViewer calls and labels every payload or metadata object it owns. Frontend active-selection operations still receive view-local indices after MolSysViewer's index mapper, while the addon retains the corresponding global selection as labeled metadata.

## Corrected Defect

`DFNDData.info()` previously queried the original molecular system using `local_atom_indices`. It now uses the tetrahedron's global `atom_indices`.

## Verified Invariants

- A hydrogen-excluded mesh can have local tetrahedron atoms `[0, 1, 2, 3]` and global atoms `[1, 2, 3, 4]`; `DFNDData.info()` queries only the latter.
- A nonconsecutive global simplex selection is resolved in global space, retained as a labeled addon selection, and mapped to the view's local space only for the host active-selection operation.
- Addon-owned edge/face metadata and simplex/feature payloads declare their atom index space.
- Geometry helpers reject molecular-system atoms absent from the selected mesh.

## Remaining Boundary

Future MolSysViewer API work may provide first-class index-space labels on all shape and selection methods. Until then, TopoMT must keep conversion at the call site and must not pass mesh-local indices to a view loaded with the original molecular system.
