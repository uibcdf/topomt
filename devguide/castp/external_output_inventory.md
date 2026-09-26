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
For explicit individual files, the run retains every supplied file as an
output artifact and uses the supplied PDB, or the first available file, as
its input artifact. A `.pocInfo`-only import remains attributable without a
molecular system.

The loader uses pocket IDs from both `.poc` and `.pocInfo`; a reported
surface without atom rows remains a feature with unknown atom ownership.
For mouths, `.mouthInfo` also contains zero rows for voids (`N_mth = 0`),
which have no matching `.mouth` atom rows. Those zero rows remain in the
original artifact but do not create fictitious Mouth features. A positive
`N_mth` row is retained even if its atom records are absent. The file loader
still needs explicit coverage for directory-only inputs, nested ZIP layouts,
alternate filenames, absent
optional files, and invalid archives. Submitted-atom matching under selection
and multiple chains needs independent tests. Server tests do not yet compare
results returned by a live service.

## `1tcd` field-level reading

| Original field | TopoMT feature field | Meaning and remaining work |
|---|---|---|
| `.poc` record ID and atom rows | Surface feature `source_id` and atom labels | One reported surface pocket ID. Feature class is inferred from `N_mth`: zero void, one pocket, two channel, more branched channel. This is a TopoMT interpretation of the CASTp mouth count. |
| `.pocInfo` `N_mth` | `n_mouths`, attributed count | Number of mouths for that pocket; independent calculation [#51](https://github.com/uibcdf/topomt/issues/51). |
| `.pocInfo` `Area_sa`, `Area_ms` | `solvent_accessible_area`, `molecular_surface_area` | Distinct CASTp surface definitions; original Å² values are attributed and feature quantities use nm². Independent-calculation issues [#41](https://github.com/uibcdf/topomt/issues/41) and [#42](https://github.com/uibcdf/topomt/issues/42). |
| `.pocInfo` `Vol_sa`, `Vol_ms` | `solvent_accessible_volume`, `molecular_surface_volume` | Distinct CASTp volume definitions; original Å³ values are attributed and feature quantities use nm³. Independent-calculation issues [#43](https://github.com/uibcdf/topomt/issues/43) and [#44](https://github.com/uibcdf/topomt/issues/44). |
| `.pocInfo` `Lenth` | `length`, attributed measurement | Original Å, feature nm. The bundled CASTpFold README defines it as the sum of arc lengths where two pocket atoms meet and the edge alpha value is negative. Independent calculation [#49](https://github.com/uibcdf/topomt/issues/49). |
| `.pocInfo` `cnr` | `surface_triangles_excluding_mouth_count`, attributed count | The bundled CASTpFold README defines this as the number of surface triangles excluding mouth triangles. This is specific to CASTp's surface representation; independent calculation [#50](https://github.com/uibcdf/topomt/issues/50). |
| `.mouth` record ID and atom rows | Mouth feature `source_id` and atom labels | The row ID matches the parent pocket ID in this fixture. One record may summarize multiple mouths. |
| `.mouthInfo` `N_mth` | Mouth `n_mouths`, attributed count, `provider_aggregates_multiple_mouths` | This column is a count, not a parent-pocket ID. The row ID links the parent; `N_mth > 1` marks an aggregate. `N_mth = 0` remains only in the original record. Independent calculation [#51](https://github.com/uibcdf/topomt/issues/51). |
| `.mouthInfo` `Area_sa`, `Area_ms` | Mouth `solvent_accessible_area`, `molecular_surface_area` | Original aggregate Å² values are attributed; feature quantities use nm². Independent-calculation issues [#45](https://github.com/uibcdf/topomt/issues/45) and [#46](https://github.com/uibcdf/topomt/issues/46). |
| `.mouthInfo` `Len_sa`, `Len_ms` | Mouth `solvent_accessible_length`, `molecular_surface_length` | Original aggregate Å values are attributed; feature quantities use nm. Independent-calculation issues [#47](https://github.com/uibcdf/topomt/issues/47) and [#48](https://github.com/uibcdf/topomt/issues/48). They are not silently renamed to a generic mouth perimeter because the surface definitions differ. |
| `.mouthInfo` `Ntri` | Mouth `n_triangles`, attributed count | Triangle count of the reported surface representation; independent calculation [#52](https://github.com/uibcdf/topomt/issues/52). |

General physical concepts retain neutral names. CASTp-specific choices of
surface, probe, discrete triangle representation, aggregation, and feature
classification are documented in the
[attribute-origin register](../third_party_attribute_origins.md) and remain
necessary provenance for numerical comparisons. All 13 numeric columns of
the fixed `.pocInfo` and `.mouthInfo` records now have attributed original
values, definitions, source fields, and calculation issues. The nine physical
columns use canonical PyUnitWizard nm, nm², or nm³ quantities on features;
counts remain integers. Additional optional columns and atom-level output
still require audit. The pinned `1psn.zip` has job-named result files and a
native README, which supplies the definitions above and is retained in
`ProviderRun`. This is not an accepted
fidelity milestone.

The same native ZIP includes `.4.contrib.csv`: atom identifiers plus absolute
and percentage SA/MS area and volume contributions. It also includes
`.bulb.json`, whose per-pocket arrays contain display sphere centers and
radii. Both files survive byte for byte in `ProviderRun`, and the test checks
their recovery. They are not yet parsed into typed TopoMT atom-level
measurements or pocket geometry. The CASTp 3.0 `1tcd.zip` fixture has neither
file, so this route must treat them as optional.
The [CASTp 3.0 paper](https://academic.oup.com/nar/article/46/W1/W363/5026264)
describes analytic SA and MS measurement from alpha shapes. The
[CASTpFold tutorial](https://cfold.bme.uic.edu/castpfold/infos/allabout/tutorial.html)
states that its interface displays SA area and volume only; CASTp 3.0 ZIP
fields must therefore not be assumed present in every CASTpFold response.
