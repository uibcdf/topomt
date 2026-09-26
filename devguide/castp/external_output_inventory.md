# CASTp/CASTpFold external output inventory

Status: file and server ZIP retention in progress. The pinned CASTp 3.0
`topomt/data/CASTp_3.0_server/1tcd.zip` is the initial parser fixture;
1a4j, 1hiv, 1stp, 2pk4, and 3ptb now cover aggregate mouth rows and
surface counts.
CASTpFold and CASTp 3.0 server routes have mocked-download tests against that
same ZIP; these tests establish route and parser behavior, not live-server
availability or CASTpFold-specific numeric parity.

## Retained artifacts and feature identity

For an imported ZIP, `Topography.provider_runs` retains the exact ZIP as its
input and every extracted file as an output artifact. For a server response,
the run retains the exact submitted PDB as input, the untouched downloaded
ZIP under `output/raw_server_zip/`, and every extracted file. All parsed
pocket, void, channel, branched-channel, and mouth features link to the run.
Their atom-label source is `.poc` or `.mouth`; their metric source is
`.pocInfo` or `.mouthInfo`. The portable bundle round trip is tested on 1tcd.

The loader uses pocket IDs from both `.poc` and `.pocInfo`; a reported
surface without atom rows remains a feature with unknown atom ownership.
For mouths, `.mouthInfo` also contains zero rows for voids (`N_mth = 0`),
which have no matching `.mouth` atom rows. Those zero rows remain in the
original artifact but do not create fictitious Mouth features. A positive
`N_mth` row is retained even if its atom records are absent. The file loader
still needs explicit coverage for individual-file and
directory-only inputs, nested ZIP layouts, alternate filenames, absent
optional files, and invalid archives. Submitted-atom matching under selection
and multiple chains needs independent tests. Server tests do not yet compare
results returned by a live service.

## `1tcd` field-level reading

| Original field | TopoMT feature field | Meaning and remaining work |
|---|---|---|
| `.poc` record ID and atom rows | Surface feature `source_id` and atom labels | One reported surface pocket ID. Feature class is inferred from `N_mth`: zero void, one pocket, two channel, more branched channel. This is a TopoMT interpretation of the CASTp mouth count. |
| `.pocInfo` `N_mth` | `n_mouths` | Number of mouths for that pocket. |
| `.pocInfo` `Area_sa`, `Area_ms` | `solvent_accessible_area`, `molecular_surface_area` | Distinct CASTp surface definitions; original Å² values are attributed and feature quantities use nm². Independent-calculation issues [#41](https://github.com/uibcdf/topomt/issues/41) and [#42](https://github.com/uibcdf/topomt/issues/42). |
| `.pocInfo` `Vol_sa`, `Vol_ms` | `solvent_accessible_volume`, `molecular_surface_volume` | Distinct CASTp volume definitions; original Å³ values are attributed and feature quantities use nm³. Independent-calculation issues [#43](https://github.com/uibcdf/topomt/issues/43) and [#44](https://github.com/uibcdf/topomt/issues/44). |
| `.pocInfo` `Lenth` | `length` | Reported linear extent in Å; exact algorithm needs source-level definition audit and calculation issue. |
| `.pocInfo` `cnr` | `corner_points_count` | Count specific to CASTp's discrete surface representation; attribute origin is CASTp. Definition and calculation issue pending. |
| `.mouth` record ID and atom rows | Mouth feature `source_id` and atom labels | The row ID matches the parent pocket ID in this fixture. One record may summarize multiple mouths. |
| `.mouthInfo` `N_mth` | Mouth `n_mouths`, `provider_aggregates_multiple_mouths` | This column is a count, not a parent-pocket ID. The parser uses the row ID for the pocket link; `N_mth > 1` marks an aggregate. `N_mth = 0` remains only in the original record. No individual mouth geometry is invented. |
| `.mouthInfo` `Area_sa`, `Area_ms` | Mouth `solvent_accessible_area`, `molecular_surface_area` | Reported aggregate areas in Å². Attributed records and independent calculations pending. |
| `.mouthInfo` `Len_sa`, `Len_ms` | Mouth `solvent_accessible_length`, `molecular_surface_length` | Reported aggregate lengths in Å. They are not silently renamed to a generic mouth perimeter because the surface definitions differ. |
| `.mouthInfo` `Ntri` | Mouth `n_triangles` | Triangle count of the reported surface representation; original artifact retained. |

General physical concepts retain neutral names. CASTp-specific choices of
surface, probe, discrete corner representation, aggregation, and feature
classification are documented in the
[attribute-origin register](../third_party_attribute_origins.md) and remain
necessary provenance for numerical comparisons. The four pocket area/volume
fields now use canonical PyUnitWizard quantities and keep their original
numbers, units, definitions, source fields, and issue links in
`ExternalMeasurement`. The remaining pocket length/corner and mouth fields
still need equivalent treatment; this is not an accepted fidelity milestone.
The [CASTp 3.0 paper](https://academic.oup.com/nar/article/46/W1/W363/5026264)
describes analytic SA and MS measurement from alpha shapes. The
[CASTpFold tutorial](https://cfold.bme.uic.edu/castpfold/infos/allabout/tutorial.html)
states that its interface displays SA area and volume only; CASTp 3.0 ZIP
fields must therefore not be assumed present in every CASTpFold response.
