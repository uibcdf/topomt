# CASTp3 Oracle Parity Harness

Date: 2026-04-28

## Purpose

The previous CASTp3/CASTpFold parity tables mixed two comparison frames:

- server-loaded `Topography` atom indices, resolved against the PDB embedded in
  the oracle zip;
- native feature atom indices, emitted from the native CASTp3 geometry
  selection.

Those raw indices are not guaranteed to be the same stable identifiers. The
comparison must use PDB atom IDs or CASTp atom labels instead.

This checkpoint records the corrected harness and the first controlled results.

## New Harness

Script:

```bash
python -u devtools/castp/compare_castp3_oracles.py --ids 3phv
```

The harness does the following for each oracle ZIP:

- extracts the ZIP to a temporary directory;
- uses the PDB embedded in the ZIP as the native input;
- parses `.poc`, `.pocInfo`, and `.mouth` directly;
- converts CASTp atom labels to stable PDB atom serials;
- runs `topomt.third_party.castp3._native_impl.castp`;
- converts native atom indices back to PDB atom serials read directly from the
  fixed-width PDB `ATOM` / `HETATM` records;
- compares multisets of atom-ID sets;
- compares `.mouth` against native aggregated `mouths`, not individual
  `topological_mouths`.

Default native settings:

- `probe_radius=1.4`
- `radii_model='protor'`
- `probe_limited_depth=False`
- `selection='molecule_type in ["protein", "peptide"]'`

Two details are critical:

- MolSysMT `atom_id` is not always the PDB serial used by CASTp exports. The
  parity frame must use the serial in columns 7-11 of the exact PDB bundled in
  the oracle ZIP.
- CASTpFold excludes waters, ions, and ligand/small-molecule records from these
  protein benchmark computations. The native CASTp3 comparison therefore uses
  protein plus peptide molecules, not `selection='all'`.
- The default comparison does not truncate pocket depth by probe radius. A
  `--probe-limited-depth` variant remains available for experiments, but the
  current benchmark subset gives the same counts with and without that variant.

Regression coverage:

```bash
python -m pytest tests/methods/castp/test_castp3_oracle_comparison.py
```

## Controlled Green Cases

With the corrected comparison frame and the protein/peptide-only selection,
multiple systems are exact across all exported feature types:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 1crn | pocket | 0 | 0 | 0 |
| 1crn | void | 1 | 1 | 1 |
| 1crn | channel | 0 | 0 | 0 |
| 1crn | branched_channel | 0 | 0 | 0 |
| 1crn | mouth | 0 | 0 | 0 |
| 1hew | pocket | 4 | 4 | 4 |
| 1hew | void | 3 | 3 | 3 |
| 1hew | channel | 0 | 0 | 0 |
| 1hew | branched_channel | 0 | 0 | 0 |
| 1hew | mouth | 4 | 4 | 4 |
| 1rop | pocket | 3 | 3 | 3 |
| 1rop | void | 0 | 0 | 0 |
| 1rop | channel | 0 | 0 | 0 |
| 1rop | branched_channel | 0 | 0 | 0 |
| 1rop | mouth | 3 | 3 | 3 |
| 2pk4 | pocket | 3 | 3 | 3 |
| 2pk4 | void | 4 | 4 | 4 |
| 2pk4 | channel | 0 | 0 | 0 |
| 2pk4 | branched_channel | 0 | 0 | 0 |
| 2pk4 | mouth | 3 | 3 | 3 |
| 3phv | pocket | 8 | 8 | 8 |
| 3phv | void | 2 | 2 | 2 |
| 3phv | channel | 2 | 2 | 2 |
| 3phv | branched_channel | 1 | 1 | 1 |
| 3phv | mouth | 11 | 11 | 11 |

Interpretation:

- this validates the mouth aggregation correction;
- it also proves that the current native CASTp3 path can reproduce a complete
  CASTpFold export exactly for several benchmark systems;
- `3phv` remains the strongest multi-feature green regression control;
- `2pk4` is now green again once waters/ligands are excluded, confirming that
  the earlier red result was a comparison/preparation error rather than an
  algorithmic regression.

## Current Near-Red Cases

The same parity harness still shows residual divergences in other systems, but
the corrected selection makes them much closer than the previous report:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 2lyz | pocket | 6 | 6 | 5 |
| 2lyz | void | 6 | 6 | 6 |
| 2lyz | channel | 0 | 0 | 0 |
| 2lyz | branched_channel | 0 | 0 | 0 |
| 2lyz | mouth | 6 | 6 | 5 |
| 1a6u | pocket | 21 | 22 | 21 |
| 1a6u | void | 19 | 19 | 19 |
| 1a6u | channel | 2 | 2 | 2 |
| 1a6u | branched_channel | 1 | 1 | 1 |
| 1a6u | mouth | 24 | 25 | 22 |
| 2ifb | pocket | 10 | 11 | 9 |
| 2ifb | void | 6 | 6 | 5 |
| 2ifb | channel | 1 | 1 | 1 |
| 2ifb | branched_channel | 0 | 0 | 0 |
| 2ifb | mouth | 11 | 12 | 10 |
| 5dfr | pocket | 10 | 11 | 8 |
| 5dfr | void | 3 | 2 | 2 |
| 5dfr | channel | 2 | 2 | 1 |
| 5dfr | branched_channel | 1 | 1 | 0 |
| 5dfr | mouth | 13 | 14 | 11 |

These are higher-confidence residuals than the older raw-index tables, but they
are not as severe as the transient report generated with `selection='all'`.

## Correction of the Transient False Red Report

A short-lived version of this checkpoint incorrectly reported much poorer
results, including `2pk4` as fully red. That was caused by two comparison
problems:

1. native atom indices were mapped through MolSysMT `atom_id`, which can differ
   from the PDB serial used in CASTp `.poc` and `.mouth` exports;
2. the native run used `selection='all'`, so waters and ligand/small-molecule
   HETATM records entered the native geometry even though CASTpFold did not
   include them in these benchmark features.

After fixing both points, `2pk4` is exact again:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 2pk4 | pocket | 3 | 3 | 3 |
| 2pk4 | void | 4 | 4 | 4 |
| 2pk4 | channel | 0 | 0 | 0 |
| 2pk4 | branched_channel | 0 | 0 | 0 |
| 2pk4 | mouth | 3 | 3 | 3 |

This correction should prevent future confusion: a red result from this harness
is only meaningful if both stable PDB serial mapping and protein/peptide-only
selection are active.

## Consequences

1. The immediate comparison oracle is now `devtools/castp/compare_castp3_oracles.py`.
2. Future parity statements must cite this harness or an equivalent stable-ID
   comparison.
3. Older tables that compared raw Topography atom indices should be treated as
   exploratory only.
4. Current exact controls include `1crn`, `1hew`, `1rop`, `2pk4`, and `3phv`.
5. Current residual cases include `2lyz`, `1a6u`, `2ifb`, and `5dfr`.

## Next Work

The next diagnostic pass should focus on the smallest near-red case, `2lyz`:

- list unmatched oracle and native pocket atom-ID sets;
- inspect the one non-exact pocket/mouth;
- determine whether the residual is an atom-reporting/rim issue or a true
  component construction issue.

This is a better next target than a large broad batch because the harness has
made the red signal reproducible and frame-stable.

## `2lyz` Residual Analysis

`2lyz` is not a component-count problem:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 2lyz | pocket | 6 | 6 | 5 |
| 2lyz | void | 6 | 6 | 6 |
| 2lyz | channel | 0 | 0 | 0 |
| 2lyz | branched_channel | 0 | 0 | 0 |
| 2lyz | mouth | 6 | 6 | 5 |

The single non-exact pocket is a strict native subset:

- oracle pocket atoms: `{484, 485, 486, 487, 488, 489, 505, 788}`
- native pocket atoms: `{486, 488, 489, 505, 788}`
- missing from native pocket: `{484, 485, 487}`

The single non-exact mouth is also a strict native subset:

- oracle mouth atoms: `{484, 486, 487, 488, 489, 505, 788}`
- native mouth atoms: `{486, 488, 489, 505, 788}`
- missing from native mouth: `{484, 487}`

Those missing atoms are all from `TRP A 62`:

- `484 CB`
- `485 CG`
- `487 CD2`

The native topological pocket is represented by one tetrahedron with serials
`{488, 489, 505, 788}`. Its mouth faces are exactly the four faces of that
tetrahedron:

- `{488, 505, 788}`
- `{488, 489, 788}`
- `{488, 489, 505}`
- `{489, 505, 788}`

CASTpFold nevertheless exports additional TRP62 atoms in `.poc` / `.mouth`.
Those atoms have non-zero global surface/volume contribution rows in
`2lyz.4.contrib.csv`.

Interpretation:

- the pocket and mouth topology are effectively correct;
- the residual is in the CASTp3 exported atom-lining/reporting layer;
- CASTp3 appears to export pocket/mouth atoms from a surface-contribution layer
  that is broader than the strict alpha-component tetrahedron vertices;
- this expansion is not explained by the CASTp1 `print_pockets()` structural
  output alone, which prints `iT`, `iF`, `rF`, `iE`, `rE`, `iV`, and `rV`.

Do not fix this by a local residue-neighbor heuristic. The next faithful step is
to identify the CASTp3 rule for assigning surface-contributing atoms to each
pocket/mouth, or to implement an analytic equivalent from the alpha-shape
surface patches.

## `1a6u` Residual Analysis

`1a6u` is very close globally:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 1a6u | pocket | 21 | 22 | 21 |
| 1a6u | void | 19 | 19 | 19 |
| 1a6u | channel | 2 | 2 | 2 |
| 1a6u | branched_channel | 1 | 1 | 1 |
| 1a6u | mouth | 24 | 25 | 22 |

All oracle pockets are present exactly. The only pocket-count mismatch is one
extra native pocket:

- native extra pocket atoms:
  `{1286, 1288, 1289, 1290, 1298, 1300, 1483}`
- native extra mouth atoms:
  `{1286, 1288, 1290, 1298, 1483}`

The atoms are localized in chain `H`:

- `1286 O LYS H 363`, occupancy `1.00`, B-factor `31.96`
- `1288 CG LYS H 363`, occupancy `0.50`, B-factor `35.70`
- `1289 CD LYS H 363`, occupancy `0.50`, B-factor `37.42`
- `1290 CE LYS H 363`, occupancy `0.50`, B-factor `37.57`
- `1298 CD1 PHE H 364`, occupancy `1.00`, B-factor `31.39`
- `1300 CE1 PHE H 364`, occupancy `1.00`, B-factor `30.73`
- `1483 OE2 GLU H 389`, occupancy `0.50`, B-factor `44.88`

Two of those atoms (`1298`, `1300`) occur in oracle features elsewhere, so the
extra pocket cannot be explained by simply removing all atoms with occupancy
`0.50`.

Important correction:

- do not filter out `occupancy < 1.0` atoms as a fix;
- disordered sites must be resolved by choosing a conformer consistently, not
  by deleting all partial-occupancy records;
- MolSysMT may already resolve part of this on load, so any future comparison
  must inspect the exact conformer/serial mapping kept by the processed
  molecular system.

Interpretation:

- `1a6u` is not a broad CASTp3 failure;
- it is a local extra shallow/open pocket in a region with partial occupancy and
  high B-factors;
- it is a useful later case for input-preparation/conformer policy, but it is
  not the best next case for canonical algorithm debugging.

## Broader Triage After `1a6u`

The next batch with the corrected parity harness gave:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 2ifb | pocket | 10 | 11 | 9 |
| 2ifb | void | 6 | 6 | 5 |
| 2ifb | channel | 1 | 1 | 1 |
| 2ifb | branched_channel | 0 | 0 | 0 |
| 2ifb | mouth | 11 | 12 | 10 |
| 5dfr | pocket | 10 | 11 | 8 |
| 5dfr | void | 3 | 2 | 2 |
| 5dfr | channel | 2 | 2 | 1 |
| 5dfr | branched_channel | 1 | 1 | 0 |
| 5dfr | mouth | 13 | 14 | 11 |
| 1brq | pocket | 10 | 10 | 7 |
| 1brq | void | 7 | 7 | 7 |
| 1brq | channel | 2 | 2 | 1 |
| 1brq | branched_channel | 1 | 1 | 1 |
| 1brq | mouth | 13 | 13 | 9 |
| 1bmq | pocket | 20 | 23 | 13 |
| 1bmq | void | 15 | 16 | 15 |
| 1bmq | channel | 2 | 2 | 1 |
| 1bmq | branched_channel | 0 | 0 | 0 |
| 1bmq | mouth | 22 | 25 | 16 |
| 1rbp | pocket | 14 | 14 | 14 |
| 1rbp | void | 7 | 7 | 7 |
| 1rbp | channel | 3 | 3 | 3 |
| 1rbp | branched_channel | 0 | 0 | 0 |
| 1rbp | mouth | 17 | 17 | 16 |
| 1rob | pocket | 8 | 8 | 4 |
| 1rob | void | 2 | 2 | 2 |
| 1rob | channel | 2 | 2 | 2 |
| 1rob | branched_channel | 0 | 0 | 0 |
| 1rob | mouth | 10 | 10 | 7 |
| 1cge | pocket | 11 | 10 | 1 |
| 1cge | void | 7 | 4 | 4 |
| 1cge | channel | 3 | 0 | 0 |
| 1cge | branched_channel | 0 | 0 | 0 |
| 1cge | mouth | 14 | 10 | 1 |

`1rbp` is the cleanest next target because all parent features are exact and
only one mouth atom set differs.

## `1rbp` Residual Analysis

`1rbp` has exact pockets, voids, and channels:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 1rbp | pocket | 14 | 14 | 14 |
| 1rbp | void | 7 | 7 | 7 |
| 1rbp | channel | 3 | 3 | 3 |
| 1rbp | branched_channel | 0 | 0 | 0 |
| 1rbp | mouth | 17 | 17 | 16 |

The only mismatch is one aggregated mouth of an exact channel parent:

- oracle mouth atoms:
  `{12, 13, 14, 16, 17, 19, 20, 25, 62, 63, 80, 81, 82, 86, 110, 870, 1246, 1247, 1260, 1267, 1271, 1272, 1274, 1288}`
- native mouth atoms:
  `{12, 13, 14, 16, 17, 19, 20, 25, 62, 63, 80, 81, 82, 86, 110, 870, 1246, 1247, 1260, 1267, 1270, 1271, 1272, 1274, 1288}`
- native extra mouth atom: `{1270}`

The parent channel atom set is exact and includes atom `1270`. The mismatch is
therefore not a channel/pocket construction error; it is specifically a mouth
atom-assignment/reporting error.

This is the best next algorithmic target because it isolates the mouth-reporting
rule without confounding pocket count, void count, channel count, or input
preparation.

## 1998 Paper Audit: Mouths

The 1998 CAST papers were re-read to check whether the `1rbp` mouth residual
can be explained by the canonical definition of mouths.

Relevant conclusions from `Anatomy_1998.pdf`:

- CAST identifies atoms forming pockets, atoms forming mouth rims, the number
  of mouths, and mouth opening area/circumference as separate quantities.
- In the 2D explanation, a mouth is the outside boundary edge of the pocket; in
  3D the equivalent objects are Delaunay triangles on the opening.
- The paper explicitly states that mouth area is not the surface area of the
  rim atoms. It is the area of the mouth opening, computed from Delaunay
  triangles after subtracting the portions occupied by rim atoms.
- The paper also states that pocket extent is defined by mouth triangles, a
  unique subset of Delaunay triangles determined by atom positions, probe
  radius, and atom radii.

Relevant conclusions from `On_1998.pdf`:

- Pockets are defined from an acyclic flow relation over Delaunay tetrahedra.
- The flow relation increases orthogonal-ball radius; sinks and the dummy
  outside tetrahedron control which regions are pockets versus outside.
- Mouths are defined as connected components of the pocket boundary not
  contained in the alpha complex: conceptually `Bd P - CpxB`.
- Algorithmically, mouth dual sets are built by collecting boundary triangles
  outside `CpxB` in a union-find structure and merging adjacent triangles.

Implications for `1rbp`:

- The papers support comparing mouth triangles first, not only mouth atom sets.
- They do not justify an ad-hoc rule that removes a mouth triangle because it
  shares an exterior tetrahedron or because a particular atom looks peripheral.
- A discrepancy of `Ntri=22` in CASTpFold versus 24 native triangles should be
  explained by one of these canonical layers:
  - the native pocket boundary `Bd P` differs locally;
  - the native `CpxB` membership for one or two boundary triangles differs;
  - CASTp3/CASTpFold applies an additional server-side measurement/reporting
    layer when exporting `.mouth` and `.mouthInfo`.

Additional `1rbp` trace:

- The two native extra mouth triangles are exactly:
  - `(80, 1270, 1271)`
  - `(80, 1270, 1274)`
- Both are adjacent to native tetrahedron `1225`, with atoms
  `{80, 1270, 1271, 1274}`.
- Native `1225` is classified as outside because its flow crosses attached
  face `(80, 1271, 1274)` toward tetrahedron `2330`, whose depth reaches
  infinity.
- This decision follows the CASTp1 `hidden_triangle` rank rule directly:
  `rho(face) == 0`, `mu1(face) >= rho(current_tet)`, and
  `mu1(face) < rho(neighbor_tet)`.
- The critical values are not close numerical ties:
  - `rho(1225) ~= 4.03`
  - `rho(2330) ~= 7.57`
  - `rho(983) ~= 12.10`

Working conclusion:

The `1rbp` `24 -> 22` mouth-triangle discrepancy is unlikely to be explained by
simple floating-point noise. The strongest current hypotheses are:

- a local difference in the weighted triangulation/rank table, possibly still
  related to DELX/SoS or exact ordering;
- a CASTp3-specific mouth measurement/export layer that reports rim atoms and
  `Ntri` after an additional aperture-processing step not described in the 1998
  papers;
- a remaining native mismatch in how `Bd P - CpxB` is materialized from the
  tetrahedron component.

Rejected global hypotheses:

- using `probe_rank` as the global `alpha_rank` breaks green controls and is
  not compatible with the paper statement that CAST does not use multiple alpha
  values for pocket construction;
- using CASTp1 wrapping-depth globally worsens several controls and does not
  resolve the `1rbp` mouth residual;
- changing from ProtOr to historical CASTp1 radii worsens `1rbp`, so the current
  residual is not explained by the broad radii model.


## Focus Batch: `1stp`, `8rat`, `1hel`, `1hfc`

A new small-system batch was run in parallel against CASTpFold oracles:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 1stp | pocket | 5 | 5 | 4 |
| 1stp | void | 3 | 3 | 3 |
| 1stp | channel | 1 | 1 | 1 |
| 1stp | branched_channel | 0 | 0 | 0 |
| 1stp | mouth | 6 | 6 | 6 |
| 8rat | pocket | 11 | 11 | 8 |
| 8rat | void | 0 | 0 | 0 |
| 8rat | channel | 1 | 1 | 1 |
| 8rat | branched_channel | 0 | 0 | 0 |
| 8rat | mouth | 12 | 12 | 9 |
| 1hel | pocket | 8 | 8 | 7 |
| 1hel | void | 4 | 4 | 4 |
| 1hel | channel | 0 | 0 | 0 |
| 1hel | branched_channel | 0 | 0 | 0 |
| 1hel | mouth | 8 | 8 | 6 |
| 1hfc | pocket | 14 | 14 | 12 |
| 1hfc | void | 5 | 5 | 5 |
| 1hfc | channel | 1 | 1 | 1 |
| 1hfc | branched_channel | 0 | 0 | 0 |
| 1hfc | mouth | 15 | 15 | 12 |

Divergent feature-set pairing shows a repeated pattern:

- `1stp` has one pocket that is a strict native subset of the oracle: missing
  atom `592` (`N SER A 93`). Mouths are fully exact.
- `8rat` has three non-exact pockets and three corresponding non-exact mouths;
  all are strict native subsets of the oracle. Missing atoms are `10`, `13`,
  `506`, `858`, `869`, and `889`.
- `1hel` has one non-exact pocket missing atom `733`; one mouth has the same
  subset pattern, and one mouth has a small mixed rim-atom reassignment.
- `1hfc` has two non-exact pockets, both strict native subsets of the oracle;
  mouths include both subset cases and small mixed rim-atom reassignments.

The divergent atoms are ordinary protein atoms with occupancy `1.00`, not waters,
ligands, ions, or alternate-conformer artifacts. Their CASTpFold `contrib.csv`
rows usually have non-zero molecular-surface area and volume contributions.

Working interpretation:

- Parent topology is often correct: counts of pockets, voids, channels, and
  mouths frequently match.
- Native pocket and mouth atom sets are often too strict because they are derived
  from tetrahedron/triangle vertices.
- CASTp3/CASTpFold appears to export pocket-lining and mouth-rim atoms from a
  surface-contribution or clipped-geometry layer, not only from the literal
  vertices of the pocket tetrahedra or mouth triangles.
- This is consistent with the 1998 papers, which distinguish atom rim/lining
  reports from mouth-opening areas computed by subtracting atom-occupied pieces
  from Delaunay triangles.

Next recommended investigation:

- Do not alter pocket/mouth topology yet.
- Implement or audit an analytic atom-contribution layer for each pocket/mouth,
  aligned with CAST/VOLBL-style area/volume decomposition.
- Use `1stp`, `8rat`, `1hel`, `1hfc`, `2lyz`, and `1rbp` as the focused atom-set
  reporting benchmark before broader CASTp3 parity testing.


## Missing-Atom Follow-up: Are Missing Tetrahedra Enough?

A follow-up audit checked whether missing oracle pocket atoms in `1stp`, `8rat`,
`1hel`, and `1hfc` can be explained by tetrahedra outside the native pocket
components.

Result:

- Some missing atoms are already in immediate neighboring tetrahedra outside the
  native component:
  - `8rat` atom `506`;
  - `8rat` atom `869`;
  - `1hel` atom `733`;
  - `1hfc` atom `277`.
- Several missing atoms are not in immediate neighbors but appear within two or
  three tetrahedron-neighbor steps in tetrahedra that introduce no atoms outside
  the oracle pocket atom set:
  - `1stp` atom `592`;
  - `8rat` atoms `10`, `13`, `858`, `889`;
  - `1hfc` atoms `267`, `364`, `1112`.

This means the earlier interpretation was incomplete. A pure atom-reporting
layer may still be needed, but the repeated subset pattern can also be explained
by native pockets missing peripheral tetrahedra or small layers of tetrahedra.

Updated working interpretation:

- If missing atoms occur only through surface contribution without any plausible
  adjacent tetrahedron support, the defect is likely atom reporting.
- If missing atoms occur in nearby tetrahedra whose atom set remains within the
  oracle feature, the defect is likely pocket construction/flow/component growth.
- The current focused batch strongly suggests that at least part of the
  CASTp3/CASTpFold gap is missing peripheral tetrahedra, not only missing
  lining/rim atom reporting.

Next diagnostic priority:

- For each paired non-exact pocket, inspect the missing-neighbor tetrahedra:
  - their `rho` rank and value;
  - their computed depth/sink;
  - whether they are blocked as outside;
  - which face/hidden relation prevents their inclusion;
  - whether adding the full minimal tetrahedron patch would preserve oracle atom
    sets and mouth counts.
- This should be done before implementing an atom-contribution reporting layer,
  because correcting component growth may solve many atom-set mismatches at the
  source.


## Peripheral-Tetrahedron Patch Experiment

A diagnostic oracle-contained patch was tested for `1stp`, `8rat`, `1hel`, and
`1hfc`: for each paired non-exact native pocket, nearby tetrahedra within three
neighbor steps were allowed to contribute atoms only if their full vertex set was
contained in the matched oracle pocket atom set. This is not an implementable
rule because it uses the oracle; it only measures whether missing atoms are
geometrically supported by nearby tetrahedra.

Result:

| pdb | pocket parity before | pocket parity after oracle-contained patch | added atoms |
|---|---:|---:|---|
| 1stp | 5/5/4 | 5/5/5 | 592 |
| 8rat | 11/11/8 | 11/11/11 | 10, 13, 506, 858, 869, 889 |
| 1hel | 8/8/7 | 8/8/8 | 733 |
| 1hfc | 14/14/12 | 14/14/14 | 267, 277, 364, 1112 |

Most selected tetrahedra are `blocked` or `unassigned` in the native component
assembly, but their computed depth reaches infinity. Therefore, they are not
simplely missing from the pocket because of a union-find merge omission. They
are tetrahedra that native CASTp3 currently treats as exterior through the
canonical max-depth flow rule.

Important interpretation:

- The experiment proves that the missing oracle atoms are geometrically close to
  the native pocket boundary and can be explained by nearby tetrahedral support.
- It does not prove that CASTpFold includes those tetrahedra in the pocket dual
  set.
- Because many candidates have `depth -> infinity`, including them as pocket
  tetrahedra would contradict the CASTp1/paper rule unless CASTp3 changed the
  depth/exterior criterion.
- The safer hypothesis is now split:
  - either CASTp3 uses a different exterior/depth rule for peripheral pockets;
  - or CASTp3 reports lining/rim atoms from adjacent exterior tetrahedra or a
    clipped surface-contribution layer while keeping the canonical pocket dual
    set smaller.

Next canonical question:

For each candidate tetrahedron, decide whether CASTp3 likely treats it as part
of the pocket dual set or only as an atom-contribution/rim source. Evidence to
seek:

- server-side metrics that would change if tetrahedra are included as pocket
  volume/area;
- CAST/VOLBL code paths that assign atom area/volume contributions from
  neighboring exterior tetrahedra;
- whether adding these tetrahedra would alter mouth counts or introduce shallow
  exterior branches.


## Temporary Native Switch: Peripheral Atom Expansion

A temporary diagnostic switch was added to the CASTp3 native path:

- API argument: `peripheral_atom_expansion_steps`
- harness option: `--peripheral-atom-expansion-steps N`
- default: `0`, preserving canonical/default behavior
- scope: reported feature `atom_indices` only
- non-scope: topology, tetrahedron membership, mouth topology, areas, volumes,
  and metrics are not changed

This switch expands reported feature atoms by walking through neighboring
tetrahedra up to `N` steps, excluding tetrahedra that already belong to other
active pocket components. It is intentionally broad and experimental; it is not
proposed as a CASTp3-faithful correction.

Initial result on `1stp`, `8rat`, `1hel`, and `1hfc`:

- default parity remains unchanged;
- with `N=1`, `N=2`, or `N=3`, pocket exact matches drop to zero for all four
  systems;
- mouths are mostly unchanged because the switch currently affects parent
  feature atom reporting, not mouth atom reporting.

Interpretation:

The oracle-contained diagnostic patch showed that the missing atoms are
geometrically near the native pockets, but unconstrained neighbor expansion is
far too broad. Any real correction needs a canonical selection rule for which
exterior/peripheral tetrahedra can contribute atoms, or a VOLBL/CAST-style
surface contribution rule. A plain BFS expansion is useful only as a negative
control.
