# Origin of topographic feature attributes

This register distinguishes attributes whose **definition belongs to an
external application** from general topographic concepts. It covers feature
attributes exposed by current adapters. The feature's `source`, `source_id`,
and `provider_run_id` identify the actual result; attributed
`external_measurements` additionally give the source field, artifact, unit,
definition, and calculation issue. These links matter even for general
concepts because different tools may use different probes or estimators.

An attribute is application-specific when its score table, normalization,
atom typing, clustering index space, or naming is defined by that tool.
Keep its origin explicit in the documentation and in its reported-measurement
record. General quantities such as pocket depth, mouth area, center, volume,
and solvent-accessible area keep neutral names. Their calculation method and
source still belong in measurement provenance.

| Application | Application-specific feature attributes | Reason |
|---|---|---|
| fpocket | `score`, `druggability_score`, `local_hydrophobic_density_score`, `mean_alpha_sphere_solvent_access`, `hydrophobicity_score`, `volume_score`, `polarity_score`, `charge_score`, `proportion_polar_atoms`, `flexibility`, `apolar_alpha_sphere_ratio`, `alpha_sphere_density` | fpocket ranking/model, residue tables, electronegativity threshold, apolar typing, cross-pocket B-factor normalization, or a reported “density” defined as a mean distance |
| fpocket | `mean_alpha_sphere_sasa`, `mean_b_factor` | Legacy fpocket aliases: the first is a dimensionless sphere-access descriptor, not SASA; the second holds normalized flexibility, not the raw mean B-factor. Migrate callers using the accurately named attributes. |
| Pocketeer | `score`, `provider_mask`, `provider_residues`, `n_provider_residues`, `alpha_sphere_provider_atom_indices`, `alpha_sphere_measurements` | Pocketeer scoring and its original Biotite array/index spaces; the per-sphere measurements retain its reported radius and mean defining-atom SASA |
| AlphaSpace2 | `score`, `alpha_space`, `alpha_nonpolar_ratio`, `alpha_nonpolar_space`, `beta_space`, `beta_nonpolar_space`, `beta_scores`, `alpha_indices`, `beta_indices`, `beta_alpha_indices`, `alpha_lining_provider_atom_indices`, `provider_snapshot_properties`, `beta_provider_properties` | AlphaSpace2 alpha/beta decomposition, nonpolar typing, Vina probe scoring, and snapshot index spaces |
| CASTp/CASTpFold | `surface_triangles_excluding_mouth_count`, `provider_aggregates_multiple_mouths` | The triangle count excludes mouth triangles in CASTp's surface representation, as defined in the bundled CASTpFold README; the aggregation flag identifies a CASTp `.mouthInfo` row that summarizes multiple mouths rather than separate geometric mouth features |
| pyCASTA | `score`, `provider_tetrahedron_indices`, `provider_validation_method` | `score` uses the upstream volume/flow/connectivity ranking formula and maps to `ranking_scores`, not `pocket_volumes` ([#35](https://github.com/uibcdf/topomt/issues/35)); tetrahedron IDs and `Mesh`/`SASA`/`FakeBall` validation belong to pyCASTA's own computation |

Provider-specific technical links such as `provider_run_id`,
`provider_snapshot_source_artifact`, `atom_source_artifact`, and
`alpha_sphere_source_artifact` identify provenance rather than describing
shape. Their naming already signals the provider-output contract. Original
provider fields remain queryable in `provider_raw_fields`,
`external_measurements`, and `topography.provider_runs` where implemented.
The mouth attribute `n_triangles` describes a general mesh count; its value
still needs the CASTp artifact and mesh-resolution provenance.

This is a **definition register**, not a claim of scientific parity. The
current [checkpoint](third_party_results_checkpoint.md) records which
application routes and attributes have independent comparison evidence. As
CASTp and pyCASTA adapters mature, update this register alongside their field
inventories and tests. Do not assign an application-specific label to a
shared geometric concept solely because one provider first supplied it.
