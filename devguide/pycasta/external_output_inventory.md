# pyCASTA external output inventory

Status: library adapter in progress. Source inspected at local revision
`75d7baf988fc02ff39d51784ac9a9ea8e5aef62b` of
`~/repos@others/pycasta`. The default configuration uses `VERSION_TAG=bov1`,
`SAVE_ALPHA=True`, `FILTER_ALPHA_BY_SASA=False`, and a placeholder
`cgal_weighted_delaunay()` that calls SciPy Delaunay. A future source revision
may change these assumptions; the run records the source hash and active
settings.

## Retained execution evidence

The library adapter executes pyCASTA in an isolated temporary working
directory. `Topography.provider_runs` retains the submitted PDB, all native
files under `results/` (including the alpha NPZ, pocket PDBs, property CSV,
and any optional files emitted by the active configuration), the complete
returned `process_pdb()` dictionary as JSON, and captured stdout/stderr.
The returned-result JSON and execution-configuration JSON are TopoMT
supplements. A non-finite returned number is tagged as
`{"nonfinite": "nan"}` or the corresponding infinity spelling; it is not
silently converted to zero. The source may omit native result JSON even when
it returns a populated dictionary. The portable `ProviderRun` ZIP recovers
each stored artifact byte for byte after temporary-directory cleanup.

The adapter verifies that the upstream alpha NPZ tetrahedron positions and
protein coordinates exactly match the reconstructed SciPy Delaunay indexing
before deriving pocket atom membership. It raises an error if this proof is
unavailable or fails. This protects against silently attaching the wrong
atoms when a future weighted or SASA-filtered route changes the index space.
The mapping from pyCASTA `ATOM` coordinates to MolSysMT atom IDs still needs
chain, HETATM-order, altloc, and selection tests.

## Field mapping

| Upstream `process_pdb()` field | TopoMT location | Unit/meaning | Status |
|---|---|---|---|
| `ranked_pockets[i]` | `pocket.provider_tetrahedron_indices`, original snapshot | Upstream tetrahedron indices; ordering retained | Mapped, index-array proof required |
| `ranking_scores[i]` | `pocket.score`, attributed `score` | pyCASTA-specific ranking score; source mixes raw volume and log terms, so physical unit is unresolved | Mapped; independent calculation [#36](https://github.com/uibcdf/topomt/issues/36); alias defect [#35](https://github.com/uibcdf/topomt/issues/35) fixed locally |
| `pocket_volumes[i]` | `pocket.volume`, attributed `volume` | Å³ in source, nm³ on feature | Mapped; upstream depth/volume index-space audit still required |
| `pocket_depths[i]` | `pocket.depth`, attributed `depth` | Å in source, nm on feature | Mapped; source currently treats tetrahedron indices as atom indices; [#37](https://github.com/uibcdf/topomt/issues/37) |
| `mouth_area[i]` | `pocket.mouth_area`, attributed `mouth_area` | Å² in source, nm² on feature; sum of selected boundary triangle areas | Mapped; [#38](https://github.com/uibcdf/topomt/issues/38) |
| `mouth_perimeter[i]` | `pocket.mouth_perimeter`, attributed `mouth_perimeter` | Å in source, nm on feature; sum of triangle-edge lengths, including shared boundary edges | Mapped; [#39](https://github.com/uibcdf/topomt/issues/39) |
| `representative_points[i]` | `pocket.representative_point`, attributed measurement | Å coordinates in source, nm on feature; tetrahedron vertices counted with multiplicity | Mapped; independent calculation [#40](https://github.com/uibcdf/topomt/issues/40) |
| `validation_methods[i]` | `pocket.provider_validation_method` | pyCASTA's `Mesh`, `SASA`, `FakeBall`, or `None` outcome | Mapped; method dependencies and meaning remain upstream-defined |
| `ligand_containment_mesh[i]`, `ligand_mesh_distances[i]` | Original snapshot | Conditional mesh-validation outcomes; distance may be `None` when `rtree` is absent | Feature mapping and units pending |
| `ligand_to_pocket_distances`, `step_to_ligand` | Original snapshot | Current source leaves the former empty; the latter is the first validated rank | Run-level interpretation pending |
| `protein_coords`, `protein_atoms`, `ligand_coords`, `pdb_path` | Original snapshot and submitted PDB | Input and preprocessing evidence; `pdb_path` names the transient file | Retained; exact atom-order audit pending |

General concepts such as depth, area, perimeter, volume, and representative
point have neutral feature names. pyCASTA-specific scoring, validation,
tetrahedron indices, and ranking rules are named or attributed as such in the
[attribute-origin register](../third_party_attribute_origins.md).

## Current parity evidence and remaining gate

Local `pytest --receptor=llm` comparisons on bounded 2pk4, 1stp, 2ifb, and
1hew check every returned pocket's rank, score, volume, depth, mouth area,
mouth perimeter, representative point, and tetrahedron list against separate
upstream calls. The 2pk4 test also verifies native artifact types and ZIP
recovery. This is a narrow library-route test, not complete provider parity.
Further gates: active configuration and clean installation, atom order under
selection and HETATM interleaving, empty/invalid results, bound and unbound
structures, ligand validation with optional dependencies installed, and
field-by-field interpretation of all conditional native files.
