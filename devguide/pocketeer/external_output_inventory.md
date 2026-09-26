# Pocketeer external-output inventory

Status: library route partially integrated; local 6qrd and 2xjx parity references.
Plan: [third-party results](../third_party_results_plan.md)
Checkpoint: [third-party results checkpoint](../third_party_results_checkpoint.md)

## Reference

The audited local upstream mirror is Pocketeer 0.3.0 at commit
[`25a06df9a905f3dab2ba6e05757392594191dda3`](https://github.com/cch1999/pocketeer/tree/25a06df9a905f3dab2ba6e05757392594191dda3).
The library returns Python `Pocket` and `AlphaSphere` objects. Its official
`write_pockets_json` export includes pocket IDs, centroids, volumes, scores,
residues, sphere IDs, centers, radii, mean SASA, and four defining atom indices,
but deliberately omits `Pocket.mask`. TopoMT captures that official export
unchanged as `output/pocketeer_pockets.json` and writes the masks to the
separately named `output/topomt_masks.json` snapshot. Both are retained as
bytes in `topography.provider_runs`, along with the exact PDB submitted to
Pocketeer. The run records version, API-file SHA-256, normalized arguments and
input atom mappings; each feature links to the run ID.

## Mapping

| Upstream field | TopoMT location | Unit / note |
|---|---|---|
| `Pocket.pocket_id` | `source_id` | Original ID; score order does not redefine it |
| `Pocket.centroid` | `center` | Å converted to nm |
| `Pocket.volume` | `volume`, `external_measurements['volume']` | Å³ converted to nm³ for existing feature alias; reported value preserved |
| `Pocket.score` | `score`, `external_measurements['score']` | Dimensionless reported value |
| `Pocket.residues` | `provider_residues` | Original `(chain_id, res_id, res_name)` tuples |
| `Pocket.n_residues` | `n_provider_residues` | Count of upstream residue tuples |
| `Pocket.mask` | `provider_mask`, `atom_indices`, mask snapshot | Mask indexes the original Biotite atom array and selects all atoms in pocket residues; it is not a four-atom lining set |
| `AlphaSphere.sphere_id` | `alpha_sphere_ids` | Upstream identifiers, not list positions |
| `Pocket.n_spheres` | `n_alpha_spheres` | Count of retained spheres |
| `AlphaSphere.center` | `alpha_sphere_centers` | Å converted to nm |
| `AlphaSphere.radius` | `alpha_sphere_radii`, `alpha_sphere_measurements[id]['radius']` | Å; original scalar preserved |
| `AlphaSphere.mean_sasa` | `alpha_sphere_mean_sasa`, `alpha_sphere_measurements[id]['mean_sasa']` | Å²; local independent calculation [#30](https://github.com/uibcdf/topomt/issues/30) pending |
| `AlphaSphere.atom_indices` | `alpha_sphere_provider_atom_indices`, `alpha_sphere_defining_atom_indices` | Four indices in the filtered upstream atom array, then mapped to the molecular system |

Pocketeer filters hydrogens, water, and hetero atoms before tessellation by
default. The four defining-atom indices refer to that filtered array. TopoMT
reconstructs the filter in upstream order and stores both source and mapped
indices. It raises an error when the input Biotite atom count differs from
the selected MolSysMT atom count, because an unchecked positional mapping
could silently assign the wrong atom.

Pocketeer's sphere mean SASA is the arithmetic mean of Biotite atom SASA for
the four defining atoms with the configured probe radius; it determines the
buried-sphere filter. Its value is retained as an external measurement and
issue #30 tracks an independent TopoMT calculation and comparison. Pocket
volume and score already have native TopoMT implementations but still need
numerical parity checks under matched parameters.

## Evidence and remaining gate

The local 6qrd test calls Pocketeer independently, then compares every
returned feature's exported data, mask, residue membership, IDs, sphere
SASA/radius and source atom indices against the adapter for up to five highest
ranked pockets. It also checks the official JSON and supplementary mask
snapshot against all original pockets. A 2xjx test uses a 1.7 Å probe, retains
hetero atoms, and lowers the minimum sphere count; it compares masks, sphere
IDs, defining-atom mapping, and mean SASA for every pocket. A package-route
test through the public `get_topography` API passes. This covers two local
structures and one source version, but does not establish exhaustive parity.
Add a selection/chain case, round-trip recovery of this provider run, a clean
package installation matrix, and failure cases before closing this inventory
milestone.
