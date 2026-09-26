# Third-party results checkpoint

Updated: 2026-09-26
Plan: [third_party_results_plan.md](third_party_results_plan.md)
Tracking issue: [#19](https://github.com/uibcdf/topomt/issues/19)

## Progress rule

The percentage below measures completion of fixed engineering milestones,
not the fraction of scientifically validated output fields. A milestone earns
its full weight only when its acceptance evidence exists; work in progress
earns zero. The weights total 100. Changes to weights or scope must be recorded
here before reporting a new percentage. The provider coverage table remains a
separate scientific check against an inflated engineering percentage.

| Milestone | Weight | State | Acceptance evidence or next gate |
|---|---:|---|---|
| Plan and initial measurement backlog | 5 | Done | Plan and issues [#19](https://github.com/uibcdf/topomt/issues/19), [#20](https://github.com/uibcdf/topomt/issues/20), [#21](https://github.com/uibcdf/topomt/issues/21), [#22](https://github.com/uibcdf/topomt/issues/22) |
| Portable original-output record | 5 | Done | `ProviderRun` bundle round trip and changed/missing artifact tests |
| fpocket output survives CLI temporary-directory cleanup | 5 | Done | CLI and persisted-output tests recover original input and info bytes |
| fpocket total/polar/apolar SASA with source and issue links | 5 | Done | 3LKF fixture checks values and square-angstrom units |
| Remaining fpocket field inventory and typed mapping | 10 | In progress | All 19 scalar info fields checked line by line in two fixtures and a local CLI run; sphere and contact-atom provenance retained; defining atoms, global PDB, historical build identity, and broader parity remain |
| Pocketeer result fidelity and output record | 10 | In progress | Library result and mask captured for 6qrd and 2xjx; sphere IDs, SASA, defining atoms, residues and masks mapped; selection/chain, clean install and broader parity remain |
| AlphaSpace2 result fidelity and output record | 10 | Not started | Pinned fixture, full field inventory, state and source links |
| CASTp/CASTpFold result fidelity and output record | 10 | Not started | Pinned ZIP, mouth aggregation, SA/MS definitions, server evidence |
| pyCASTA result fidelity and output record | 10 | Not started | Pinned fixture, tetrahedron/depth validation, source links |
| Independent TopoMT calculations and comparisons | 15 | Not started | Definition-specific issues closed by matching-input numerical tests |
| Cross-provider edge-case and server validation | 5 | Not started | Selection, ligand, chain, void/channel/interface, version and live-server matrix |
| Final exhaustive provider parity regression suite | 10 | Not started | Every provider and supported route compared field by field with pinned upstream output in CI; live server checks tracked separately |

**Verified engineering progress: 20/100 (20%).** The remaining 80% includes
full field inventories, four other providers, independent calculations,
cross-provider validation, and the final parity battery. This percentage must
be reduced if an accepted milestone regresses.

## Provider coverage at this checkpoint

| Provider | Original output retained in `Topography` | Typed attributed measurements | Scientific parity |
|---|---|---|---|
| fpocket CLI and persisted files | Yes, input and all output files | All 19 scalar info fields, sphere ID/type/charge, ordered contact serials and positional atom mapping; four defining atoms are absent from PQR output | Reported scalars match original info lines in two fixtures and a local CLI run; native-calculation parity pending |
| Pocketeer library | Yes, submitted PDB, official JSON and omitted-mask supplement | Volume, score, centroid, residues, mask, sphere IDs/geometry/mean SASA/four defining atoms | 6qrd and non-default 2xjx against local source; broader parity pending |
| AlphaSpace2 | Pending | Pending | Pending |
| CASTp/CASTpFold | Pending | Pending | Pending |
| pyCASTA | Pending | Pending | Pending |

## Next checkpoint

Continue the [fpocket field inventory](fpocket4/external_output_inventory.md):
seek an upstream-supported way to expose each sphere's four defining atoms,
validate atom/residue mapping across chain, insertion code, alternate location,
selection and nonconsecutive serials, audit the global PDB, and identify the
historical fixtures' binary. The global PQR sphere records already match the
ordered per-pocket records in both fixtures after accounting for renumbered
serials. Compare a clean identified binary and persisted-file routes across
more structures before closing the fpocket milestone. The seven additional missing scalar
calculations now have separate issues
[#23–#29](https://github.com/uibcdf/topomt/issues/23).

The [Pocketeer inventory](pocketeer/external_output_inventory.md) now covers
the Python-library route. Its official JSON omits the atom mask; a separate
snapshot preserves it. Per-sphere mean SASA is reported with its original
value and source and has independent-calculation issue
[#30](https://github.com/uibcdf/topomt/issues/30). The 6qrd and 2xjx
comparisons pass, including a non-default probe and hetero-atom setting.
Selection/chain mapping and clean-install/version coverage remain before its
10-point milestone can be accepted.

Verification for this checkpoint: `pytest --receptor=llm` reported 88 passed,
4 skipped, and 24 warnings across provider-output, fpocket-provider, full
fpocket parity, Topography registry, and public get-topography tests. The skips
are four unavailable BCIF fixtures; the warning groups are unknown LO1/LO2
atom names and two native fpocket divisions. The new tests compare all 19
reported scalar fields for every pocket in 3LKF, 1tcd, and one local CLI run;
contact-atom and global-PQR provenance are independently checked for the two
pinned structures. This does not establish equivalence of TopoMT's native
calculations to fpocket's calculations.
The joint Pocketeer, Topography, public-API and provider-output
`pytest --receptor=llm` selection reported 28 passed. A follow-up focused
Pocketeer selection reported 3 passed after count-field mapping.
The remote `gh run-receptor` inspection of Ruff run 36227804844 reported PASS,
but its commit predates these uncommitted changes. Local `ruff check`,
`ruff format --check` on newly formatted modules, YAML parsing, and
`git diff --check` passed. The older `test_parity.py` file retains pre-existing
whole-file formatting debt; its imports now pass `ruff check`.
