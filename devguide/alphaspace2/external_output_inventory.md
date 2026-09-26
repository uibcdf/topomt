# AlphaSpace2 external-output inventory

Status: library route partially integrated on the 1GG0 reference structure.
Plan: [third-party results](../third_party_results_plan.md)
Checkpoint: [third-party results checkpoint](../third_party_results_checkpoint.md)
Attribute origins: [provider-specific attributes](../third_party_attribute_origins.md)

## Source and record

The audited mirror is
[`RedesignScience/AlphaSpace2@1283f73`](https://github.com/RedesignScience/AlphaSpace2/tree/1283f73db75743a0fe856d9e45707d5079b55503).
The upstream package exposes `Snapshot` numeric arrays and lazy `_Pocket`,
`_Beta`, and `_Alpha` properties. It does not advertise a package version in
its root module, so the `ProviderRun` records the SHA-256 of `Snapshot.py`,
the snapshot settings, the selected atom mapping, and the exact submitted PDB.

TopoMT calls the upstream `Snapshot.save()` with the receptor and keeps its
exported PDB files byte for byte. It also creates
`output/topomt_snapshot.json`, a versioned supplement containing every
`Snapshot.__dict__` field and the derived properties of every pocket and beta
site. Nonfinite upstream ratios are represented explicitly as, for example,
`{"nonfinite": "nan"}` in this JSON. The artifact is captured before the
temporary directory is removed and can be exported with `ProviderRun.save()`.
The upstream PDB export is ordered by pocket volume; the supplement and
`source_id` retain original snapshot indices.

## Mapping

| Provider output | TopoMT location | Unit / meaning |
|---|---|---|
| Pocket index, alpha and beta memberships | `source_id`, `alpha_indices`, `beta_indices`, `beta_alpha_indices` | Original snapshot indices |
| Alpha lining atom indices | `alpha_lining_provider_atom_indices`, `alpha_lining_atom_indices` | Four source indices per alpha and mapped MolSysMT indices |
| Alpha centers and radii | `alpha_sphere_centers`, `alpha_sphere_radii` | Å converted to nm |
| Alpha space, nonpolar ratio, nonpolar space | `alpha_space`, `alpha_nonpolar_ratio`, `alpha_nonpolar_space` | Å³, dimensionless, Å³ |
| Beta centers, space, nonpolar space, scores | `beta_centers`, `beta_space`, `beta_nonpolar_space`, `beta_scores` | Å converted to nm; Å³; Å³; score unit unverified |
| Full derived beta records | `beta_provider_properties` | Original best probe type, contact, occupied volumes, and occupancy for the pocket's beta indices |
| Alpha and beta contact flags | `alpha_contact`, `beta_contact` | Boolean, in original index order |
| Pocket centroid, volume, nonpolar volume, score, contact | `center`, `volume`, `nonpolar_volume`, `score`, `is_contact` | Coordinates and volumes converted to nm / nm³; reported scalars also in `external_measurements` |
| Occupied space, occupied nonpolar space | `occupied_space`, `occupied_nonpolar_space`, `external_measurements` | Å³; independent calculations [#31](https://github.com/uibcdf/topomt/issues/31) and [#32](https://github.com/uibcdf/topomt/issues/32) pending |
| Occupancy, nonpolar occupancy | `occupancy`, `occupancy_nonpolar`, `external_measurements` | Fractions; independent calculations [#33](https://github.com/uibcdf/topomt/issues/33) and [#34](https://github.com/uibcdf/topomt/issues/34) pending |
| Residue names, elements, atom names and every internal numeric array | `topography.provider_runs[run_id]` snapshot supplement | Exact reported values, array order and source relationships |

The wrapper checks that the MDTraj receptor and selected MolSysMT system have
the same atom count before mapping lining atoms. Equal counts do not prove
identical atom order; chain, alternate-location, insertion-code, and selection
cases remain to validate. `min_vertices` filters returned TopoMT pockets only;
the provider record retains the entire unfiltered snapshot.

## Evidence and remaining work

The 1GG0 test compares the snapshot arrays and selected pocket fields against
an independent upstream run. It compares every upstream-exported file byte for
byte with `ProviderRun` and verifies a portable bundle round trip. The
upstream code emits a runtime warning for nonpolar occupancy when a zero
denominator yields an undefined ratio; the snapshot supplement preserves that
state rather than inventing a numeric value.

The current library wrapper runs without a binder or advanced atom types, so
contact metrics are normally zero and beta scores usually zero. Binder input,
the richer Vina-aware score path, multiple structures, chain/selection mapping,
and a clean installed-package version are required for scientific parity.
The score's physical unit is not established by the audited source and remains
marked `unspecified` rather than assumed dimensionless.
