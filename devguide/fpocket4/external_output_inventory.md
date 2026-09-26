# fpocket external-output inventory

Status: active; scalar `_info.txt` mapping verified for pinned 3LKF and 1tcd
fixtures and one locally installed CLI build.
Plan: [third-party results](../third_party_results_plan.md)
Checkpoint: [third-party results checkpoint](../third_party_results_checkpoint.md)

## Reference and limits

The scalar definitions below were checked against the local clean mirror of
`Discngine/fpocket` at commit
[`4bb0d8447f62fee77e2c3c29f54b5fcaf5e2c066`](https://github.com/Discngine/fpocket/tree/4bb0d8447f62fee77e2c3c29f54b5fcaf5e2c066),
especially `src/descriptors.c`, `src/pocket.c`, `src/asa.c`, and `src/fpout.c`.
The exact build that produced the bundled 3LKF output is **unknown**. Its
`3LKF_info.txt` SHA-256 is
`1a716e05078ed78777bd5abca58b16bfad544a6644aa0204d44ca80491999be3`.
The fixture is a parser and attribution reference, not proof of numeric parity
with every fpocket binary. Future live CLI fixtures must record the executable
identity and parameters. Current CLI `ProviderRun.metadata` records the
executable name, SHA-256, and extra arguments; imported historical output has
no trustworthy executable identity until its provenance is established.

For every field below, `pocket.external_measurements[name]` holds the exact
reported `_info.txt` number, interpreted unit, source label and artifact,
definition, run ID, calculation status, and issue URL when local calculation is
missing. `pocket.provider_raw_fields` retains parsed PDB/PQR header precision;
the exact files remain in `topography.provider_runs`. Existing feature aliases
are retained, even where their names or bare-float types need migration.
`pocket.unmapped_provider_fields` exposes unexpected info fields rather than
silently discarding them.

## Pocket `_info.txt` fields

All 19 fields in each pocket of the bundled 3LKF info report are mapped.
`Available` means TopoMT's native fpocket route contains a calculation; it does
**not** mean independent numerical parity has been established. The reported
values remain separate from local calculations.

| Original field | Measurement name | Interpreted unit | Local calculation |
|---|---|---|---|
| Score | `score` | 1 | Available; parity pending |
| Druggability Score | `druggability_score` | 1 | Available; parity pending |
| Number of Alpha Spheres | `n_alpha_spheres` | count | Available; parity pending |
| Total SASA | `total_sasa` | Å² | [#20](https://github.com/uibcdf/topomt/issues/20) |
| Polar SASA | `polar_sasa` | Å² | [#21](https://github.com/uibcdf/topomt/issues/21) |
| Apolar SASA | `apolar_sasa` | Å² | [#22](https://github.com/uibcdf/topomt/issues/22) |
| Volume | `volume` | Å³ | Available; parity pending |
| Mean local hydrophobic density | `local_hydrophobic_density_score` | count | Available; parity pending |
| Mean alpha sphere radius | `mean_alpha_sphere_radius` | Å | Available; parity pending |
| Mean alp. sph. solvent access | `mean_alpha_sphere_solvent_access` | 1 | [#23](https://github.com/uibcdf/topomt/issues/23) |
| Apolar alpha sphere proportion | `apolar_alpha_sphere_ratio` | 1 | Available; parity pending |
| Hydrophobicity score | `hydrophobicity_score` | 1 | [#24](https://github.com/uibcdf/topomt/issues/24) |
| Volume score | `volume_score` | 1 | [#25](https://github.com/uibcdf/topomt/issues/25) |
| Polarity score | `polarity_score` | 1 | [#26](https://github.com/uibcdf/topomt/issues/26) |
| Charge score | `charge_score` | 1 | [#27](https://github.com/uibcdf/topomt/issues/27) |
| Proportion of polar atoms | `proportion_polar_atoms` | percent | [#28](https://github.com/uibcdf/topomt/issues/28) |
| Alpha sphere density | `alpha_sphere_density` | Å | Available; parity pending |
| Cent. of mass - Alpha Sphere max dist | `alpha_sphere_max_distance` | Å | Available; parity pending |
| Flexibility | `flexibility` | 1 | [#29](https://github.com/uibcdf/topomt/issues/29) |

## Definition traps

- `_info.txt` prints three decimals; pocket PDB/PQR headers often print four.
  For example, 3LKF pocket 1 reports `Score: 33.993` in the info report and
  `Pocket Score: 33.9933` in its pocket PDB. Both source numbers are retained.
- `Mean alp. sph. solvent access` is the mean of center-to-contact-barycenter
  distance divided by alpha-sphere radius. It is dimensionless. The existing
  `mean_alpha_sphere_sasa` alias names this incorrectly and remains only for
  compatibility until callers can migrate.
- `Alpha sphere density` is the mean pairwise distance between sphere centers,
  in Å. The report's `Cent. of mass - Alpha Sphere max dist` is the maximum
  pairwise sphere-center distance in the studied upstream source, despite its
  label; neither value should be redefined from its English name.
- `Flexibility` is a pocket mean of contacted-atom B factors, then min-max
  normalized across all detected pockets; a single pocket gets zero. It is
  dimensionless. The pocket PDB header calls it `Mean B-factor`, and the
  existing `mean_b_factor` alias must not be treated as the raw B-factor mean.
- `Volume score` is a residue-table score, not the geometric `Volume` field.
  The polar/apolar SASA split depends on fpocket atom typing and its 1.4 Å
  probe, so generic molecule SASA is not automatically equivalent.

## Remaining output levels

| Artifact | Already exposed | Remaining audit |
|---|---|---|
| Pocket `*_atm.pdb` | Contacted atom serials, their original order, positional TopoMT indices (or `None`), unmatched serials, and source artifact; header values in `provider_raw_fields` | Verify atom identity across chain, insertion code, alternate location, nonconsecutive IDs, and selections; finish header-field provenance |
| Pocket `*_vert.pqr` | Alpha-sphere centers, radii, IDs, charge-column values, polar/apolar types, source artifact and original order | Four defining atoms are not written in these PQR files; seek a supported upstream sidecar or instrumentation; verify all columns across builds |
| Global pockets PQR/PDB | Exact bytes in `ProviderRun`; global PQR sphere records checked against ordered per-pocket files for 3LKF and 1tcd | Audit global PDB annotations and further builds |
| PyMOL/VMD scripts | Exact bytes in `ProviderRun` | No scientific field mapping expected; retain as original artifacts |

This inventory milestone remains open until those levels and a clean,
identified fpocket build are validated across more than one structure and
every useful source field has a `Topography` mapping.

The 3LKF PQR repeats some sphere serials, so `alpha_sphere_ids` preserves
original order and does not claim that a serial is a unique sphere key. A
previous parser slice read `APOL` as `POL`; the four-character PQR atom name is
now retained exactly. The PQR charge-column values are preserved as reported
numbers without assigning a physical charge unit until their upstream meaning
is verified.

The 3LKF and 1tcd pocket atom files contain 232 and 551 contact records,
respectively; every serial maps to an input atom in these fixtures and neither
set has duplicate pocket contacts. A deliberately unmatched serial is retained
as `None` in the positional mapping and listed in `unmapped_atom_serials`.
This preserves the original record even if a molecular-system conversion cannot
identify its atom.

The global PQR has 400 sphere records for 3LKF and 686 for 1tcd, in the same
order and with the same non-serial columns as the per-pocket files. In 1tcd,
626 global serial fields differ because the global writer numbers spheres
continuously while the per-pocket writer starts over for each pocket. This
matches `src/writepocket.c` in the inspected source mirror. The source stores
four atom neighbors for each Voronoi vertex (`src/voronoi.c`), but its PQR
writer emits only sphere type, coordinates, charge-column zero, and radius.
Therefore the four defining atom identities cannot be recovered exactly from
the bundled PQR files. A future upstream integration can expose them through
a dedicated output or in-process result if supported; geometric inference
alone must not be labeled as the original identity.

The independent regression tests read every numeric `_info.txt` line from the
original artifact and compare its label and value with `ExternalMeasurement`
for all pockets in both fixtures and a locally executed CLI run. These tests
verify reported-value fidelity; they do not establish native-calculation
equivalence, historical binary identity, or parity for other structures.
