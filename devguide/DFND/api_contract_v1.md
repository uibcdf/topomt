# DFND API Contract v1

This document defines the current public API contract for DFND while the method
is still being hardened.

## 1. Two API Layers

DFND currently has two intentionally different API layers.

`dfnd(...)` is the raw-first development and validation API. It returns the full
DFND result as a nested dictionary with `raw`, `wet`, and `dry` sections. This is
the authoritative output for auditing the algorithm, inspecting provisional
component families, and validating internal records.

`get_topography(method='dfnd')` is the TopoMT integration API. It returns a
normal `Topography` object and converts only the wet components that already
have stable TopoMT feature counterparts.

The returned `Topography` object also encapsulates the entire DFND substrate
under a single `topography.dfnd` object (which exposes `raw`, `mesh`, and
`dfn` sections for debugging, re-querying, and visual rendering). There are
no `dfnd_*` attributes at the `Topography` top level.

## 2. Public Feature Mapping

The v1 public `Topography` view exposes only compatibility concavity features:

| DFND family | Public TopoMT feature |
| --- | --- |
| `void` | `Void` |
| `pocket` | `Pocket` |
| `channel` | `Channel` |

`channel` is the raw topological name. `Channel` is the
current public shorthand used by the compatibility TopoMT view.

## 3. Provisional Records

The following DFND wet components remain raw/provisional in v1 and are not converted to
public `Topography` features yet:

- `surface_concavity`
- `nonresident_passage`
- `degenerate_subprobe`
- dry components and dry motifs

These raw records are not exposed as direct properties on `Topography` but
are fully accessible through `topography.dfnd.raw['wet_components']` and the direct
`dfnd(...)` output dictionary.

This avoids promoting names whose biological or geometric interpretation is
still under validation, while preserving the complete audit trail.

## 4. Guaranteed Public Feature Fields

Every DFND feature exposed through `get_topography(method='dfnd')` must provide:

- `source`
- `source_id`
- `family`
- `atom_indices`
- `tetrahedron_indices`
- `resident_tetrahedron_indices`
- `transit_connector_tetrahedron_indices`
- `center`
- `volume_topological_resident`
- `volume_solvent_estimate`
- `n_mouths`
- `mouth_area`
- `mouths`
- `mouth_face_clusters`
- `flags`
- `raw_record`

`source` is always `dfnd`. For promoted parent concavity features, `source_id`
is the contextual `component_key` defined in
[`component_identity_contract.md`](component_identity_contract.md). A promoted
mouth uses its contextual `external_link_key` as its own `source_id` and carries
`parent_component_key` to identify its parent component context. Neither field is
temporal identity.

Every promoted DFND `Mouth` must also expose the source external-link
provenance and gate metrics: `external_link_id`, `external_link_key`,
`external_link_support_key`, `external_link_record`, `face_ids`,
`tetrahedron_ids`, `faces`, `flags`, `area`, `R_gate_min`, `R_gate_mean`, and
`R_gate_max`. `area` is a PyUnitWizard quantity in `nm**2`; gate radii are
quantities in `nm`.

## 5. Metrics Contract

`volume_topological_resident` is a topological resident-cell volume descriptor.
It is not a solvent-excluded or CASTp-comparable physical pocket volume.

`mouth_area` is the current face-cluster area descriptor. It is useful for
internal characterization and comparison between DFND runs, but physical solvent
mouth metrics remain pending.

`volume_solvent_estimate` is the current deterministic local estimate of
empty volume inside resident tetrahedra after excluding the four local atomic
spheres of each tetrahedron. It is not an analytic sphere-tetrahedron
intersection formula and does not yet include non-local atom intrusions.

Future higher-precision physical metrics should be added with explicit names
rather than overloading existing topological fields.

## 6. Input Contract

`probe_radius`, `epsilon`, `residence_tolerance`, and
`permeability_tolerance` should be supplied as PyUnitWizard quantities. Legacy
bare floats are still accepted by the public compatibility facade, emit a
`FutureWarning`, and are interpreted as angstroms before normalization to DFND
raw nm. `DFNDData.at_probe()` follows the same compatibility rule for a bare
`probe_radius`.

The molecular input path is MolSysMT-based. `selection`, `structure_indices`,
`hydrogen_policy`, `radii_model`, `transit_policy`, and
`gate_intrusion_policy` are recorded in the raw `parameters` section for
reproducibility.

## 7. Mesh, Query, and Reporting Contract

`DFNDMeshConfig` records fields that determine the cached substrate, including
normalized-nm `epsilon`. `DFNDQuery` records only fields that can change while
reusing that substrate and stores normalized-nm lengths. Both are frozen typed
objects and expose canonicalizable `to_dict()` mappings. The existing
keyword-based API remains a compatibility facade.

`substrate_key` includes the mesh configuration. `result_key` combines that
substrate identity with `DFNDQuery`; it reuses the canonical identity machinery
in `identity.py`. Reporting filters do not affect result identity.

Raw DFND records carry `schema_version = 'dfnd.raw.nm.v1'` and a `units` mapping;
raw lengths, coordinates, areas, and volumes are bare nm/nm**2/nm**3 values.

`min_size` is currently a compatibility/reporting filter: every wet and dry
component remains in the decomposition and records whether it belongs in the
compatibility view. `sea_level` is not part of DFND. `DFNDData.at_probe()`
preserves all unspecified query and reporting fields and rejects changes to mesh
configuration.

## 8. Stability Policy

The public feature mapping and guaranteed fields above are the current v1
contract. Raw records may contain more fields than listed here, but downstream
code should not treat provisional raw-only component families as stable public
features until they are promoted explicitly.
