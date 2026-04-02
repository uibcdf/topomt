**PyCasta Contract**

Purpose: record the active contract for the upcoming TopoMT-native
`pycasta` method so the implementation stays focused on the reproducible
geometric core of the upstream workflow while keeping track of the current
drift between the paper description and the public repository.

## Upstream references

- Source repository: <https://github.com/giorgioluciano/pycasta>, local clone at
  `~/repos@others/pycasta`
- Paper: "pyCAST, a Python package for the detection of cavities on surface proteins",
  Comput Struct Biotechnol J. 2025. DOI: <https://doi.org/10.1016/j.csbj.2025.07.054>

## Current technical reading

The current repository implements a practical pipeline centered on:

1. loading a PDB structure and separating receptor and ligand coordinates;
2. assigning per-atom radii;
3. tetrahedralizing the receptor coordinates;
4. computing an alpha complex by circumsphere-radius thresholding;
5. running a discrete flow over empty tetrahedra;
6. grouping tetrahedra by sink and merging nearby clusters;
7. computing pocket volumes, representative points, and a ranking score;
8. deriving mouth and dual-set information;
9. optionally validating pockets against a bound ligand with SASA, fake-ball,
   or mesh-extrusion checks.

The code landmarks are mainly:

- `src/pycasta/run_analysis.py`
- `src/pycasta/pocket_detection.py`
- `src/pycasta/alpha_shape.py`
- `src/pycasta/dual_sets.py`
- `src/pycasta/ranking.py`
- `src/pycasta/utils/pocket_utils.py`

## Paper-versus-repository drift

The paper and the current public repository are not identical in all key
claims, and this must stay explicit during the TopoMT implementation.

Paper-side claims:

- weighted Delaunay triangulation;
- alpha threshold chosen through persistent homology;
- flow phrased in terms of lower average edge length;
- emphasis on CAST faithfulness and analytical cavity characterization.

Repository-side behavior currently observed:

- `cgal_wdelaunay.py` is a placeholder and falls back to standard
  `scipy.spatial.Delaunay`;
- the active alpha threshold comes from mutable global config
  (`MANUAL_ALPHA`, `set_alpha`, `get_alpha`) rather than a persistent-homology
  implementation;
- the active flow code uses circumsphere-radius-derived proxy values;
- much of the ligand validation and output/export logic is coupled directly to
  the main analysis script.

Practical implication:

- TopoMT should not silently pretend that repository parity and paper parity
  are the same target;
- the first native contract should reproduce the effective repository workflow;
- any later effort to recover the paper-described weighted-Delaunay and
  persistent-homology variants should be documented as a distinct audit step.

## What TopoMT must reproduce first

1. Receptor preparation semantics equivalent to the upstream run, but using
   `molsysmt` instead of Biopandas.
2. Per-atom radii assignment compatible with the upstream `atomic_radii.py`
   table.
3. The repository's effective tetrahedral workflow:
   standard Delaunay over receptor heavy atoms, alpha-complex filtering by
   circumsphere radii, empty-tetrahedra selection, discrete flow grouping, and
   centroid-distance cluster merging.
4. Pocket descriptors that are part of the core geometric output:
   tetrahedra per pocket, representative point, pocket volume, pocket depth,
   ranking score, mouth area/perimeter, and pocket atom ownership.
5. Dual-set and mouth decomposition outputs when they are deterministically
   derivable from the detected pocket tetrahedra.

## What TopoMT should replace intentionally

- Structure loading, atom selection, and index mapping should use `molsysmt`,
  not Biopandas.
- Physical quantities should use the normal TopoMT `pyunitwizard` policy.
- Optional capabilities should be guarded through the project `depdigest`
  layer, not ad hoc imports.
- Warnings/signals should use the TopoMT `smonitor` integration.

## What is not part of the first native contract

- paired bound/unbound analysis orchestration;
- Excel-driven dataset tables;
- result-directory caching and `VERSION_TAG` workflows;
- PyMOL-based SASA machinery as a runtime dependency target;
- mesh export and downstream benchmark-report generation.

These may be reintroduced later as optional layers if they are needed to
reproduce a specific published benchmark, but they should not define the first
native method contract.

## SASA and ligand validation note

The upstream repository mixes core pocket detection with downstream ligand
validation.

For TopoMT:

- the geometric pocket detector should remain usable without a ligand;
- ligand-contact or SASA-based validation can exist as optional postprocessing;
- and if SASA is needed, it should be obtained through `molsysmt`-compatible
  infrastructure rather than through a hard dependency on `pymol`, `pymol2`,
  or `freesasa`.

## Validation target

The initial validation target should be repository parity on a small audited
set, comparing at least:

- pocket count and ranking order;
- tetrahedra-per-pocket membership;
- pocket atom ownership;
- representative points;
- pocket volumes and depths within explicit tolerances;
- mouth counts and mouth geometry when available;
- dual-set boundary outputs where the repository produces them deterministically.

After that baseline exists, a second audit can evaluate whether the paper-level
claims require an additional TopoMT mode or an upstream clarification note.

## Current audited subset

The current small audited bounded subset is:

- `2pk4`
- `1stp`
- `2ifb`
- `1hew`

These are the first repository-parity cases now used to anchor the local
TopoMT battery because they are relatively small and already reproduce pocket
counts, top-pocket/group sizes, and pocket volumes consistently.

## Upstream dataset inventory

The local upstream mirror currently ships the following benchmark ids.

Bounded:

- `1a4j`, `1a6w`, `1acj`, `1apu`, `1bid`, `1blh`, `1byb`, `1cdo`, `1dwd`,
  `1fbp`, `1gca`, `1hew`, `1hfc`, `1hyt`, `1ida`, `1igj`, `1imb`, `1inc`,
  `1ivd`, `1mrg`, `1mtw`, `1okm`, `1pdz`, `1phd`, `1pso`, `1qpe`, `1rbp`,
  `1rne`, `1rob`, `1snc`, `1srf`, `1stp`, `1ulb`, `2ctc`, `2h4n`, `2ifb`,
  `2pk4`, `2sim`, `2tmn`, `2ypi`, `3gch`, `3mth`, `3ptb`, `4dfr`, `4phv`,
  `5cna`, `5p2p`, `6rsa`, `7cpa`

Unbounded:

- `1a4j`, `1a6u`, `1ahc`, `1bbs`, `1brq`, `1bya`, `1cge`, `1chg`, `1djb`,
  `1esa`, `1gcg`, `1hel`, `1hsi`, `1hxf`, `1ifb`, `1ime`, `1krm`, `1krn`,
  `1l3f`, `1nna`, `1npc`, `1pdy`, `1phc`, `1psn`, `1pts`, `1qif`, `1stn`,
  `1swb`, `1ula`, `1ypi`, `2cba`, `2ctb`, `2ctv`, `2fbp`, `2sil`, `2tga`,
  `3app`, `3lck`, `3p2p`, `3phv`, `3ptn`, `3tms`, `4ca2`, `5cpa`, `5dfr`,
  `6ins`, `7rat`, `8adh`, `8rat`

Practical policy:

- keep only a small audited subset as local parity fixtures for now;
- document the full upstream dataset inventory in `devguide`;
- and expand the audited battery gradually instead of copying the entire
  benchmark corpus into TopoMT immediately.

## Paired benchmark correspondence

The upstream repository also ships an explicit bound/unbound pairing table in:

- `src/pycasta/data/tables/correspondence.xlsx`

Current mapping:

| Unbounded | Bounded |
|---|---|
| `1a6u` | `1a6w` |
| `1qif` | `1acj` |
| `3app` | `1apu` |
| `3tms` | `1bid` |
| `1djb` | `1blh` |
| `1bya` | `1byb` |
| `8adh` | `1cdo` |
| `1hxf` | `1dwd` |
| `2fbp` | `1fbp` |
| `1gcg` | `1gca` |
| `1hel` | `1hew` |
| `1cge` | `1hfc` |
| `1npc` | `1hyt` |
| `1hsi` | `1ida` |
| `1a4j` | `1igj` |
| `1ime` | `1imb` |
| `1esa` | `1inc` |
| `1nna` | `1ivd` |
| `1ahc` | `1mrg` |
| `2tga` | `1mtw` |
| `4ca2` | `1okm` |
| `1pdy` | `1pdz` |
| `1phc` | `1phd` |
| `1psn` | `1pso` |
| `3lck` | `1qpe` |
| `1brq` | `1rbp` |
| `1bbs` | `1rne` |
| `8rat` | `1rob` |
| `1stn` | `1snc` |
| `1pts` | `1srf` |
| `1swb` | `1stp` |
| `1ula` | `1ulb` |
| `2ctb` | `2ctc` |
| `2cba` | `2h4n` |
| `1ifb` | `2ifb` |
| `1krn` | `2pk4` |
| `2sil` | `2sim` |
| `1l3f` | `2tmn` |
| `1ypi` | `2ypi` |
| `1chg` | `3gch` |
| `6ins` | `3mth` |
| `3ptn` | `3ptb` |
| `5dfr` | `4dfr` |
| `3phv` | `4phv` |
| `2ctv` | `5cna` |
| `3p2p` | `5p2p` |
| `7rat` | `6rsa` |
| `5cpa` | `7cpa` |

This table should stay in `devguide` even before the paired workflow becomes
part of the audited TopoMT parity battery.
