# Modern CASTp closed-void measurements checkpoint

## Subsequent coverage and molecular-panel expansion

The [later corpus checkpoint](checkpoint_2026_10_01_radius_coverage_and_void_panel.md)
accounts for all 89 archives and expands the molecular panel to twenty systems.
Nineteen reproduce 136 voids and 544 measures; 1CGE still lacks three closed
cavities. It also corrects alternate-location oracle identity and separates
terminal-oxygen candidates from established radius assignments. The initial
milestone and next-step list below retain their original scope.

## Subsequent radius-profile qualification

The later [expanded panel](checkpoint_2026_10_01_castp3_radius_profile.md) found
two SA/MS residuals with standard ProtOr despite exact lining atoms. Server
bulb geometry identified a distinct carboxylate radius. The explicit
`castp3_protor` profile now reproduces thirteen voids and fifty-two measures
across four systems. The first 2PK4 evidence below retains its original inputs;
do not extend its standard-ProtOr agreement to all modern-server cases.

Date: 2026-10-01. Bounded implementation theme:
[#79](https://github.com/uibcdf/topomt/issues/79).

## Accepted direction

The user resumed local CASTp reconstruction while the two-case DFND notebook
laboratory is paused. The historical C source and the CAST papers describe the
algorithm; they are not a variable-by-variable numerical oracle. Pinned CASTp
3.0 and CASTpFold outputs define the modern result target. DFND remains TopoMT's
native semantic method; external reconstruction does not redefine Topography.

The source investigation found build/seed-sensitive vertex retention and an
assertion failure in a fresh historical build. These observations do not prove
that a particular historical executable faithfully represents either modern
server. No rebuilt binary or generated historical oracle is added to the
repository. Historical source debugging is deferred.

## First result and exact comparison contract

The bundled CASTp 3.0 and CASTpFold archives for `1stp`, `1tcd`, `2pk4` and
`3ptb` have identical `.poc`, `.pocInfo`, `.mouth` and `.mouthInfo` files and
identical PDB atom records. This establishes agreement for those artifacts,
not universal server equivalence or current live-service availability.

The local CASTp3 reconstruction reproduces all four closed cavities in the
pinned `2pk4` output: exact lining-atom sets and all sixteen SA/MS measurements.
Inputs are the archive's PDB, protein/peptide selection, `radii_model='protor'`,
probe radius 1.4 Å and the base alpha rank. Features are matched by PDB atom
serial sets rather than local feature numbering.

| Server ID | Lining atoms | SA area (Å²) | MS area (Å²) | SA volume (Å³) | MS volume (Å³) |
|---|---:|---:|---:|---:|---:|
| 7 | 4 | 0.048 | 29.154 | 0.000 | 13.716 |
| 6 | 6 | 0.058 | 28.958 | 0.000 | 14.370 |
| 4 | 8 | 1.030 | 38.945 | 0.051 | 21.752 |
| 5 | 9 | 0.876 | 54.136 | 0.013 | 30.393 |

The regression uses absolute tolerance `0.00050001` and zero relative tolerance
because the server prints three decimal places. This is an output-rounding
allowance, not an adjusted geometric epsilon. Small SA volumes printed as zero
remain nonzero in local full-precision results.

## Implementation and public boundary

The existing Python VOLBL closed-component construction supplies the four
independent quantities without cusp correction. Runtime calculation needs no
historical executable, archive or network. The local CASTp3 records now carry:

- `solvent_accessible_area` and `molecular_surface_area` in Å²;
- `solvent_accessible_volume` and `molecular_surface_volume` in Å³.

The adapter transfers these quantities to existing Feature attributes with
explicit nm²/nm³ units. A subprocess regression checks that conversion remains
correct under a consumer's angstrom standard-unit policy and preserves that
policy. No new public feature class or DFND concept is introduced.

Generic `area` and `volume` retain their historical polyhedral definitions.
Analytical SA/MS fields are emitted only for closed voids at the base alpha
rank. Open-feature metrics and measurements at altered alpha ranks are not yet
validated; missing fields remain missing. No guarantee of full native CASTp3
equivalence is made. Original server/file routes and `CASTpOutput` remain
separate; `get_provider_output()` still rejects `backend='native'`.

Two reproduced defects are corrected in both local CAST cores:

1. Classical radius-table and explicit-radius geometry no longer request atom
   types or chemical bonds unnecessarily. ProtOr still requires connectivity and
   propagates its failures. The upstream no-bonds failure is tracked separately
   in [MolSysMT #283](https://github.com/uibcdf/molsysmt/issues/283).
2. `voids_measurements(input_rank=...)` builds components at the requested rank
   rather than mixing its masks with components from the base rank. Geometry's
   stored base rank remains unchanged.

## Verification and limits

The CAST regression selector (geometry metadata, modern voids, classical core,
ProtOr, probe-limited depth and existing oracle comparison) passed 128 tests,
with 11 skips and 5 existing expected failures. The skips require historical
local oracle files; the expected failures compare the classical route with
modern-server results. Neither is treated as modern parity evidence. Additional
focused verification passed 49 tests covering preserved ProtOr failures,
original loaders, consumer unit policy and reporting governance. Ruff's full
repository lint/format checks pass; the two modified output modules pass the
bounded mypy check with imported implementation bodies skipped.
The HTML documentation builds successfully with 11 diagnostics elsewhere in
the documentation, including a malformed transition, notebook headings,
bibliography links and an unavailable PlantUML executable. This is not a
warning-free documentation gate; documentation hardening remains under #64.

Primary reproducible selectors:

```bash
python -m pytest --receptor=llm \
  tests/methods/castp/test_castp_geometry_metadata.py \
  tests/methods/castp/test_castp_modern_void_measurements.py
```

The controlled local validation uses PyUnitWizard source `23554a7`, as CI does.
The broader Python/OS matrix is still an independent, unmet gate under #16;
passing these CAST tests does not certify the entire repository.

## Next steps

1. Expand exact closed-void membership and per-component SA/MS comparisons to
   additional pinned systems; prioritize previously promising `1ifb`, `3phv`
   and `1hew` references. Preserve disagreements as regressions and measurements.
2. Audit analytical boundaries and measures for open pockets and mouths under
   #41–#52. Generic tetrahedral volume or planar triangle area cannot stand in
   for those quantities.
3. Isolate the `3ptb`/`1bmq` near-boundary opening differences, `5dfr`/`1a6w`
   cavity birth/death and `1stn`/`2ifb` lining-atom attribution. Existing epsilon
   heuristics remain off; do not fit them to one molecule.

The broader native review of other providers remains deferred. Frozen synthetic
notebooks continue to be the DFND comparison seed; this milestone does not
claim completed synthetic CASTpFold jobs or change DFND kernels.
