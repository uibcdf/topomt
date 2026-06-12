# DFND Data Model v1

> [!NOTE]
> **Terminology Authority**: Per [`object_model.md`](object_model.md), this data model has been fully migrated to the zero-legacy **`component`** $\rightarrow$ **`component`** $\rightarrow$ **`feature`** ladder.
> The wet graph-decomposition records are unified under **`wet_components`** (represented by the Python-side `WetComponent` class) and use simplified family names (`void`, `pocket`, `channel`) without the `_domain` suffix. Legacy terms like `ConcavityDomain` or `TransitDomain` are obsolete.

This document defines the minimal DFND data model to implement before adding
higher-level heuristics, visualizations, or production Topography conversion.

The guiding rule is strict layering:

```text
DelaunayMesh
-> primitive measurements
-> residence, transit, and dry graph records
-> transit/residence decomposition records
-> motif descriptors
-> semantic Topography features
```

The v1 implementation should prioritize raw, traceable records. Public feature
objects can be built after the raw contract is stable.

## 1. Design Goals

The first data model must be:

- explicit enough to debug every classification decision;
- small enough to implement and test quickly;
- compatible with the existing `DelaunayMesh` substrate;
- independent of CASTp or fpocket object models;
- ready for later conversion into `Topography` and `Feature` objects.

## 2. Naming Policy

Use CamelCase names for conceptual records and snake_case for fields.

Core raw records:

```text
DFNDParameters
DFNDMeshRecord
TetrahedronRecord
FaceRecord
DelaunayFlowNetwork
Component
ResidenceRegion
ExternalLink
Motif
DryComponent
DryInterface
DryMotif
RawDFNDRecord
```

Semantic output records or classes:

```text
TopographyFeature
ConcavityFeature
ConvexityFeature
BoundaryFeature
MixedFeature
```

The first implementation may use dataclasses, dictionaries, or lightweight
classes internally, but field names should follow this contract.

## 3. DFNDParameters

`DFNDParameters` records the policy used to build one DFND result.

Required fields:

```text
probe_radius
radii_model
coordinate_unit
radius_unit
epsilon_length
epsilon_relative
threshold_policy
marginal_policy
external_link_connectivity
dry_connectivity_policy
transit_connector_policy
terminal_contact_policy
input_selection_policy
include_hydrogens_policy
alternate_location_policy
```

Initial defaults:

```text
probe_radius = 1.4 angstrom
epsilon_length = explicit user/default value
epsilon_relative = explicit user/default value
threshold_policy = open_closed_marginal
marginal_policy = conservative
environment = one_global_ocean
external_link_connectivity = face_edge_connectivity
dry_connectivity_policy = non_permeable_face_connectivity
transit_connector_policy = non_resident_with_at_least_two_permeable_contacts
terminal_contact_policy = non_resident_with_one_permeable_contact
```

No hidden tolerance or input-filtering decision should affect graph construction
without being represented here.

## 4. Primitive Records

### 4.1. TetrahedronRecord

One record per finite Delaunay tetrahedron.

Required fields:

```text
tetrahedron_id
simplex_index
atom_ids
atom_indices
center
volume
R_residence
R_residence_center
residence_state
wet_state  # compatibility alias derived from residence_state
local_class
combined_class
transit_state
n_permeable_contacts
marginal_R_residence
flags
```

Recommended identity:

```text
tetrahedron_id = stable key from sorted atom ids plus frame/context
```

`residence_state` values:

```text
resident
non_resident
marginal
```

`wet_state` is a compatibility alias and should be derived from
`residence_state`, not stored as an independent source of truth.

`local_class` values:

```text
open
coast
sealed
marginal
```

`combined_class` examples:

```text
wet_open
wet_coast
wet_sealed
dry_open
dry_coast
dry_sealed
marginal
```

`combined_class` is derived from `residence_state` and `local_class`.

`transit_state` values:

```text
resident_transit
transit_connector
terminal_contact
non_transit
marginal
```

### 4.2. FaceRecord

One record per unique finite face.

Required fields:

```text
face_id
atom_ids
atom_indices
owner_tetrahedron_ids
neighbor_tetrahedron_ids
is_hull_face
R_gate
permeability_state
marginal_R_gate
area_geometric
flags
```

Recommended identity:

```text
face_id = stable key from sorted atom ids plus frame/context
```

`permeability_state` values:

```text
permeable
non_permeable
marginal
```

A hull face has one finite owner and exterior neighbor context. It does not
create a finite tetrahedron on the other side.

## 5. Transit and Residence Graph Records

### 5.1. DelaunayFlowNetwork

The DFN is the probe-specific movement graph built from finite transit nodes,
permeable finite faces, and the virtual exterior node `OCEAN`. Transit nodes
include resident tetrahedra and non-resident transit connectors.

Required fields:

```text
node_ids
edge_ids
external_edge_ids
ocean_node_id
parameters
```

Invariants:

- resident tetrahedra become transit nodes;
- non-resident tetrahedra with at least two permeable contacts become transit
  connectors;
- non-resident tetrahedra with exactly one permeable contact are terminal
  contacts, not transit nodes;
- finite DFN edges require permeable shared finite faces between transit nodes;
- `OCEAN` is wet by definition and has no geometry;
- external edges connect finite transit nodes to `OCEAN` through permeable hull
  faces.

### 5.2. Component

A `Component` is a connected component after removing `OCEAN` and its
incident edges from the transit graph.

Required fields:

```text
component_id
component_index
node_count_rank
support_key
component_key
transit_node_ids
resident_node_ids
transit_connector_node_ids
internal_face_ids
external_link_ids
n_transit_nodes
n_resident_nodes
n_transit_connectors
flags
```

The identity semantics and migration from the currently implemented
`size_rank` field are defined in
[`component_identity_contract.md`](component_identity_contract.md).

### 5.3. ResidenceRegion

A `ResidenceRegion` is resident-node content inside one `Component`.

Required fields:

```text
residence_region_id
component_id
resident_tetrahedron_ids
atom_ids
residue_ids
volume_topological_resident
volume_solvent_estimate_resident
R_residence_min
R_residence_mean
R_residence_max
flags
```

### 5.4. WetComponent

A `WetComponent` is the topographic connected component representing a wet flow region, its
resident sub-graphs, external links, and physical metrics.

Required fields:

```text
id
family
residence_region_ids
tetrahedron_ids
resident_tetrahedron_ids
transit_connector_tetrahedron_ids
internal_face_ids
external_link_ids
atom_ids
residue_ids
n_nodes
n_edges
n_external_links
volume_topological_transit
volume_topological_resident
volume_solvent_estimate_resident
R_residence_min
R_residence_mean
R_residence_max
R_gate_min
R_gate_mean
R_gate_max
topological_depth_max
flags
```

Allowed `family` values:

```text
void
surface_concavity
pocket
channel
channel  # optional public shorthand after morphology policy
```

The component family is decided before motif analysis.
`surface_concavity` is provisional until validated by toy systems or
geometric sweeps. `channel` should not imply a biological tunnel or pore
without additional path or morphology evidence.

### 5.5. ExternalLink

An `ExternalLink` is the DFN primitive connecting one transit component or
concavity component to `OCEAN` through a connected cluster of permeable boundary
contacts.

Required fields:

```text
external_link_id
id
component_id
face_ids
tetrahedron_ids
atom_ids
residue_ids
n_faces
area_geometric
R_gate_min
R_gate_mean
R_gate_max
flags
```

Initial clustering policy:

```text
Two external boundary faces belong to the same ExternalLink if they share an
edge and belong to the same Component.
```

`Mouth` is not required in v1. A mouth descriptor may be derived from an
`ExternalLink` later.

## 6. Dry Graph Records

### 6.1. DryComponent

A `DryComponent` is a connected component of dry tetrahedra through
non-permeable shared faces.

Required fields:

```text
dry_component_id
tetrahedron_ids
dry_edge_face_ids
dry_interface_ids
atom_ids
residue_ids
n_nodes
n_edges
R_residence_min
R_residence_mean
R_residence_max
dry_depth_min
dry_depth_mean
dry_depth_max
local_class_composition
flags
```

A large dominant dry component is expected in many systems. It should not be
filtered during graph construction.

### 6.2. DryInterface

A `DryInterface` records contact between a dry component and wet components,
external links, `OCEAN`, or hull/exterior context.

Required fields:

```text
dry_interface_id
dry_component_id
dry_tetrahedron_ids
wet_tetrahedron_ids
face_ids
atom_ids
residue_ids
adjacent_component_ids
adjacent_external_link_ids
touches_ocean
touches_hull
permeability_states
area_geometric
flags
```

Dry interfaces are the bridge between the dry graph and later convexity,
boundary, and mixed features.

### 6.3. Dry Depth

`dry_depth` is stored per dry tetrahedron and summarized per dry component or
motif.

Initial definition:

```text
dry_depth(v) = shortest dry-graph distance from v to any dry boundary node in
               the same DryComponent
```

A dry boundary node is any dry node incident to a `DryInterface`.

## 7. Motif Records

### 7.1. Motif

`Motif` is a candidate or derived descriptor inside a concavity component.

Required fields:

```text
motif_id
id
motif_type
supporting_tetrahedron_ids
supporting_face_ids
supporting_external_link_ids
metrics
flags
```

Initial motif types can be limited to:

```text
topological_depth
capacity_profile
external_link_path
```

Throat, bottleneck, and chamber labels should remain candidate descriptors.

### 7.2. DryMotif

`DryMotif` is a candidate descriptor derived from dry components and dry
interfaces.

Required fields:

```text
dry_motif_id
dry_component_id
motif_type
supporting_tetrahedron_ids
supporting_face_ids
supporting_dry_interface_ids
adjacent_component_ids
adjacent_external_link_ids
metrics
flags
```

Candidate motif types:

```text
dry_core_candidate
dry_island_candidate
protrusion_candidate
ridge_candidate
rim_candidate
wall_candidate
separator_candidate
lining_region
```

These are not public feature families in v1.

## 8. RawDFNDRecord

`RawDFNDRecord` is the reproducible output container for one frame and one
probe radius.

Required fields:

```text
parameters
mesh_record
tetrahedra
faces
wet_network
wet_components
external_links
component_motifs
dry_components
dry_interfaces
dry_motifs
flags
```

The first `dfnd(...)` implementation should be allowed to return this raw
record even before full `Topography` conversion is complete.

## 9. Topography Conversion

The conversion layer is intentionally downstream.

Initial mapping:

```text
void -> Void
surface_concavity -> SurfaceConcavity, once the class exists
pocket -> Pocket
channel -> Channel or BranchedChannel only after morphology/path analysis
nonresident_passage -> raw/provisional record, not public Channel by default
degenerate_subprobe -> raw/filter record, not public Void
ExternalLink -> descriptor attached to the parent feature
Mouth -> Mouth child feature promoted from external_mouth motif
DryMotif -> candidate annotation, not public feature by default
```

Convexity, boundary, and mixed features should not be created as public objects
until dry motif rules are validated.

## 10. v1 Implementation Boundary

Must implement first:

- primitive tetrahedron and face records;
- wet/dry and permeable/non-permeable/marginal states;
- transit DFN;
- concavity-component decomposition;
- external-link clustering;
- dry graph;
- dry components;
- dry interfaces;
- dry depth;
- raw output record.

Can be postponed:

- exact physical solvent volume beyond a first `volume_solvent_estimate`;
- geometric mouth descriptors;
- rim geometry;
- public convexity features;
- public boundary and mixed features;
- weighted depth;
- chamber/throat validation;
- ElastNetMT coupling.


## 11. Access x Residence Component Fields

Every `WetComponentRecord` must include the classification fields below:

- `n_external_links`: integer count of direct contacts to `OCEAN`.
- `n_resident_nodes`: number of nodes with `R_residence >= probe_radius`.
- `has_residence`: derived boolean, `n_resident_nodes >= 1`.
- `n_open_resident_nodes`: number of resident nodes with all finite faces permeable.
- `has_open_interior`: derived boolean, `n_open_resident_nodes >= 1`; descriptor only.
- `family`: one of `void`, `degenerate_subprobe`, `pocket`, `surface_concavity`, `channel`, or `nonresident_passage`.

`family` must be derived from `n_external_links` and `has_residence`. It must not be independently assigned from `has_open_interior`.
