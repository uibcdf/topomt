# DFND API Contract v1

This document defines the current public API contract for DFND while the method
is still being hardened.

## 1. Two API Layers

DFND currently has two intentionally different API layers.

`dfnd(...)` is the raw-first development and validation API. It returns the full
DFND result as a nested dictionary with `raw`, `wet`, and `dry` sections. This is
the authoritative output for auditing the algorithm, inspecting provisional
domain families, and validating internal records.

`get_topography(method='dfnd')` is the TopoMT integration API. It returns a
normal `Topography` object and converts only the domain families that already
have stable TopoMT feature counterparts.

The returned `Topography` object also keeps the raw DFND records attached as
`topography.dfnd_records`. The full raw-first result is attached as
`topography.dfnd_result` for debugging and development.

## 2. Public Feature Mapping

The v1 public `Topography` view exposes only compatibility concavity domains:

| DFND domain family | Public TopoMT feature |
| --- | --- |
| `void_domain` | `Void` |
| `pocket_domain` | `Pocket` |
| `multi_external_link_domain` | `Channel` |

`multi_external_link_domain` is the raw topological name. `Channel` is the
current public shorthand used by the compatibility TopoMT view.

## 3. Provisional Records

The following DFND records remain raw/provisional in v1 and are not converted to
public `Topography` features yet:

- `surface_concavity_domain`
- `nonresident_passage_domain`
- `degenerate_subprobe_domain`
- dry components and dry motifs

The `Topography` object may expose these records through `dfnd_*` convenience attributes, but this does not make them public feature classes.

They are still available through `topography.dfnd_records` and direct
`dfnd(...)` output.

This avoids promoting names whose biological or geometric interpretation is
still under validation, while preserving the complete audit trail.

## 4. Guaranteed Public Feature Fields

Every DFND feature exposed through `get_topography(method='dfnd')` must provide:

- `source`
- `source_id`
- `domain_family`
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

`source` is always `dfnd`. `source_id` is stable within one DFND run and encodes
the source, domain family, and raw domain identifier.

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

`probe_radius` accepts either a float in angstroms or a quantity convertible by
PyUnitWizard to angstroms.

The molecular input path is MolSysMT-based. `selection`, `structure_indices`,
`hydrogen_policy`, `radii_model`, `transit_policy`, and
`gate_intrusion_policy` are recorded in the raw `parameters` section for
reproducibility.

## 7. Stability Policy

The public feature mapping and guaranteed fields above are the current v1
contract. Raw records may contain more fields than listed here, but downstream
code should not treat provisional raw-only domain families as stable public
features until they are promoted explicitly.
