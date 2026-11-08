# Engine References

Current MOLE execution reference: official maintained
`sb-ncbr/webchemistry@fe0e84582a6bd42bc69224fd3a3022bf5c51cec3`, clean
consultation clone at `.cache/mole-originality-review/reference/webchemistry`.
The separate `~/repos@others/MOLE` clone remains clean at
`e0df21c35a1116d712e5a09094aae62e130f698c` (legacy standalone project).
The unchanged maintained source was compiled in `.cache/mole-integration/source`
with .NET SDK 10.0.114/runtime 10.0.14; executable `dist/mole2` reports
2.5.26.10.26. Keep those two source trees, the Python API server and a live
MOLEonline deployment distinct. See [the source checkpoint](mole/source_checkpoint.md)
and inspect exact revision/dirty state before updating a reference.

**Historical reference notes.** Current installation, integration status and
provider roadmaps are maintained in the [external-tool catalogue](external_tools_catalog.md)
and its provider overviews. The sections below preserve earlier reference
decisions; their native-default recommendations and status summaries are not
current original-provider delivery guidance or fresh parity certificates.

## Purpose

Current pyKVFinder consultation checkout: `~/repos@others/pyKVFinder`, clean
upstream `20add3537319ffd11e5e660a9181dd986651e928` (v0.9.6). Its `origin`
still points to LBC-LNBio; the `uibcdf` remote exposes the explicitly separate
compatibility branch at `e0f0fa6d32109ebd02d951ef4d7f84f3e1a88fb9`.
The separate clean checkout `~/repos@others/pyKVFinder-uibcdf` tracks that fork
branch while the original consultation checkout stays on upstream main.
See [the new-provider checkpoint](original_provider_expansion_checkpoint.md)
for the fork's bounded native/TOML qualification. Inspect revision and dirty
state again before consulting or updating either source.

This document records the external reference points used to design, validate,
and compare the main TopoMT engine integrations.

The goal is to make engine work reproducible and auditable. For each engine, we
should know:

- the upstream implementation or conceptual reference;
- the package, binary, or installation channel used as the practical reference;
- the validation target expected in TopoMT;
- and the current level of confidence in that mapping.

## Current reference table

| TopoMT engine | Upstream/reference implementation | Package or binary reference | Installation/channel reference | Validation target in TopoMT | Current status |
|---|---|---|---|---|---|
| `fpocket4` | `fpocket` by Discngine | `fpocket` binary | Audited local source build for native parity; `conda-forge::fpocket` only as a wrapper-build reference | Same pockets, same atom membership, same ranking, same `Pocket Score`, same `Drug Score` | Native/source parity confirmed on audited PDB set; wrapper parity depends on fpocket build |
| `castp` | CASTp methodology and CASTp exported files | CASTp precomputed outputs | Imported external results, not a local package dependency | Faithful loading and normalization of CASTp pockets/mouths | Partial, loader-oriented |
| `alphaspace2` | AlphaSpace2 by Redesign Science | `alphaspace2` Python package | `pip install alphaspace2` from upstream/PyPI-style distribution | Comparable alpha-space generation, pocket clustering, and lining-atom semantics | Reference formalized, parity not yet validated |
| `pocketeer` | Pocketeer project/method <https://pocketeer.readthedocs.io/en/latest/>, <https://github.com/cch1999/pocketeer> | `pocketeer` Python package (upstream) | Local mirror `/home/diego/repos@others/pocketeer` for source comparison | Implement the `find_pockets` workflow, map pocket scores and atom masks, compare key numerics | Contract and tests now under active development (see `devguide/pocketeer_contract.md`) |
| `pycasta` | pyCAST / pycasta project and paper | `pycasta` Python package | Upstream repository <https://github.com/giorgioluciano/pycasta>, local mirror `/home/diego/repos@others/pycasta`, paper DOI <https://doi.org/10.1016/j.csbj.2025.07.054> | Comparable tetrahedral cavity decomposition, pocket ranking, mouth geometry, and pocket atom ownership | Sources reviewed; contract being formalized, with paper/repository drift noted |

## `fpocket4`

### Upstream code reference

- Repository: <https://github.com/Discngine/fpocket>

### Practical package reference

- Audited source-build reference for native parity:
  - local build compiled from `../../repos@others/fpocket`
- Practical wrapper-binary reference currently seen in the environment:
  - `conda-forge::fpocket`

These two references must now be treated separately because different fpocket
builds are known to produce different final pocket sets on some systems.

### Validation target

When parity is claimed, the intended target is:

- same number of pockets;
- same pocket ranking;
- same atom membership per pocket;
- same `Pocket Score`;
- same `Drug Score`.

### Current status

TopoMT now reaches this parity target natively against the audited local source
build on the full currently audited PDB set.

Wrapper mode remains useful, but wrapper-based parity claims are now known to
depend on the fpocket binary build and should not be treated as a universal
source oracle unless the binary identity is fixed explicitly.

### Practical recommendation

If someone asks which `fpocket4` path should be used in TopoMT, the current
recommendation is:

- prefer `implementation='native'` when the goal is faithful reproduction of
  the audited upstream `fpocket` source behavior;
- use `implementation='topomt'` only when the goal is to opt into the
  TopoMT-side corrections to behaviors that look undesirable in upstream
  `fpocket`;
- use `implementation='wrapper'` only when an external binary is explicitly
  needed for compatibility, historical comparison, or binary-audit work, and
  only when the binary identity is controlled.

In other words:

- `native` is now the default fidelity-oriented recommendation;
- `topomt` is the explicit corrected variant;
- `wrapper` is an integration/audit route, not the preferred default when
  faithful audited-source reproduction is the goal.

Current practical reading of `topomt`:

- it is expected to stay very close to `native` on the audited systems;
- `E15ALA.pdb` currently matches `native` exactly at the final pocket level;
- `3LKF.pdb` currently shows only a minimal local drift relative to `native`
  (one pocket differs by one atom in the current audit), which is consistent
  with the corrected B-factor semantics being a local acceptance/refinement
  change rather than a global pocket-layout change.

The currently audited native/source parity systems are:

- `1ATP.pdb`
- `1CEN.pdb`
- `1GG0.pdb`
- `1N57.pdb`
- `1YCR.pdb`
- `2GI9.pdb`
- `2H05.pdb`
- `2HGR.pdb`
- `3LKF.pdb`
- `E15ALA.pdb`

`2HGR.pdb` remains a special case only in operational terms:

- parity is now confirmed there too;
- but it is still treated as a deep-validation and profiling case rather than
  as a routine parity-battery member because of cost.

## `castp`

### Upstream/reference basis

For CASTp, the practical reference is currently more file-oriented than
package-oriented.

TopoMT already works with:

- CASTp-style exported files;
- CASTp-derived demo folders;
- CASTp loading through [topomt/io/load_CASTp.py](../topomt/io/load_CASTp.py).

### Current status

The current integration target is faithful import and normalization of CASTp
results rather than parity against a local binary/package run.

This means CASTp is currently a loader/integration reference, not yet a fully
specified executable parity target like `fpocket4`.

The active contract for making it a real parity target now lives in:

- [castp/contract.md](castp/contract.md)
- [castp/native_implementation_plan.md](castp/native_implementation_plan.md)

### Role of `pyCAST`

`pyCAST` is currently useful as a secondary methodological reference for the
classical CAST workflow, but it should not be treated as the parity oracle for
TopoMT's `castp` work.

Reason:

- its paper is useful for interpreting the classical workflow;
- but the audited public repository does not currently justify treating it as a
  fully authoritative executable reference for CASTp fidelity.

For TopoMT, the practical oracle remains:

- CAST/CASTp literature;
- CASTp 3.0 server outputs.

## `alphaspace2`

### Upstream code and documentation references

- Repository: <https://github.com/RedesignScience/AlphaSpace2>
- Project web site: <https://yzhang.hpc.nyu.edu/AlphaSpace2/>
- Tutorials repository: <https://github.com/Vanabins28/AlphaSpace2_Tutorials>

The local source mirror currently used for inspection is:

- `/home/diego/repos@others/AlphaSpace2`

### Practical package reference

- Package: `alphaspace2`
- Practical installation reference: Python package installation from the
  upstream project distribution

### Current technical reading

The upstream implementation is not just "Voronoi vertices plus one clustering
step". Its core workflow is centered on a `Snapshot` object that:

- generates alpha spheres from receptor coordinates using Delaunay/Voronoi
  construction;
- filters alpha spheres by radius range;
- assigns four exact lining atoms to each alpha sphere;
- computes alpha-space volumes and nonpolar ratios;
- clusters alpha spheres into pockets with average-linkage clustering;
- clusters pocket alphas into beta atoms with a second clustering stage;
- and optionally annotates contact and beta scores.

This is an important distinction for TopoMT because the current native
`topomt.third_party.alphaspace2.native` implementation is still a simplified
AlphaSpace2-like detector rather than a faithful reproduction of the upstream
package semantics.

### Validation target

For TopoMT, the minimum acceptable validation target should be:

- comparable alpha-sphere detection semantics;
- comparable pocket clustering semantics;
- faithful mapping of pocket lining atoms;
- and preservation of the most important upstream descriptors when possible.

If TopoMT later claims a strong AlphaSpace2 parity level, that claim should be
made against specific receptor test systems and should explicitly state whether
the comparison includes:

- pocket count and ranking;
- alpha-sphere membership;
- lining atoms;
- beta clusters;
- and descriptor values.

### Current status

The native reimplementation now reaches parity in the current audited set for:

- alpha-sphere counts;
- alpha radii within a tight numerical tolerance;
- total alpha-space volume;
- pocket counts;
- and pocket atom ownership.

The current audited set includes:

- `1GG0.pdb`
- `3LKF.pdb`
- `protein_1c70.pdb`
- `protein_1hvi.pdb`
- `protein_1pro.pdb`

Important caveat: this does not yet mean full upstream parity for every
descriptor or scoring route. The geometry and pocket-membership layers are now
in a much stronger position, but later work is still needed for the remaining
semantic layers.

## `pocketeer`

### Existing repository notes

`pocketeer` is part of the current priority engine set, but its upstream
reference information is not yet normalized in the documentation.

### Current status

We still need to record explicitly:

## `pycasta`

### Upstream code and paper references

- Repository: <https://github.com/giorgioluciano/pycasta>
- Local source mirror: `/home/diego/repos@others/pycasta`
- Paper: <https://doi.org/10.1016/j.csbj.2025.07.054>
- Public article mirror: <https://pmc.ncbi.nlm.nih.gov/articles/PMC12357058/>

### Practical package reference

- Package: `pycasta`
- Current practical reference: direct inspection of the upstream repository and
  paper, not a wrapper integration already validated inside TopoMT

### Current technical reading

The repository currently exposes a script-centered workflow rather than a small
clean public API.

The effective algorithmic core appears to be:

- receptor/ligand extraction from a PDB;
- atomic-radius assignment;
- Delaunay tetrahedralization of receptor coordinates;
- alpha-complex filtering by circumsphere radius;
- discrete flow over empty tetrahedra;
- sink-based pocket grouping;
- centroid-distance cluster merging;
- pocket ranking, volume/depth estimation, and mouth/dual-set derivation.

### Important repository-versus-paper drift

The paper describes pyCAST in stronger terms than the current public
repository currently implements.

In particular, the paper describes:

- weighted Delaunay triangulation;
- alpha-threshold determination via persistent homology;
- and a CAST-faithful flow description phrased around lower-edge-length
  descent.

The current repository, however, currently appears to use:

- standard `scipy.spatial.Delaunay` in practice, because
  `cgal_wdelaunay.py` is a placeholder fallback;
- a mutable config-driven alpha threshold (`MANUAL_ALPHA` / `set_alpha`) rather
  than an implemented persistent-homology alpha selector;
- and a discrete-flow proxy driven by circumsphere-radius-derived values.

This means TopoMT should treat two validation questions separately:

- parity against the effective repository behavior;
- and consistency with the stronger paper-level claims.

### Validation target

The first native validation target should be repository parity for the core
geometric detector, not for the whole benchmark script stack.

That means comparing at least:

- pocket count and ranking;
- tetrahedra-per-pocket grouping;
- pocket atom ownership;
- representative points;
- pocket volumes/depths within explicit tolerances;
- and mouth/dual-set outputs where deterministic.

Current concrete checkpoint:

- `tests/methods/pycasta/test_parity.py` now covers the public upstream
  bounded examples `2pk4`, `1stp`, `2ifb`, and `1hew`.
- `2pk4` currently anchors the strongest check, confirming parity of the top
  pocket at the tetrahedron-membership and top-pocket-volume level.
- the other three currently extend the small audited battery at the
  pocket-count, pocket-size, and pocket-volume level.

The longer-term audit should then decide whether the paper-described weighted
Delaunay and persistent-homology pieces require:

- an additional TopoMT mode;
- or an upstream clarification/report if the repository is intentionally using
  a simpler practical approximation.

- the upstream repository;
- the practical package/distribution reference;
- the validation target we expect from TopoMT.

## `pycasta`

### Existing repository notes

The repository already contains one useful external note in
[to_be_checked.md](../to_be_checked.md):

- <https://github.com/giorgioluciano/pycasta>

### Current status

This is enough to identify the upstream code reference, but not yet enough to
declare the full validation contract.

We still need to record explicitly:

- the practical installation source used for validation;
- the expected parity/comparison target in TopoMT.

## `topomt.tools`

`topomt.tools` is not a wrapper around one single external tool. It is the
internal shared utility layer used by multiple methods.

This means it should not be documented in terms of executable parity to one
upstream package in the same way as `fpocket4`.

The right reference strategy here is:

- cite the concrete geometry algorithms or papers where relevant;
- document internal measurement conventions clearly;
- validate behavior through focused geometry and feature-helper regression
  tests.

## Practical rule

Before claiming that a TopoMT engine is "faithful" to an external method, this
document should record at least:

- one upstream code or methodological reference;
- one practical package/binary/channel reference;
- one concrete validation target.

## Local source consultation after migration

The transferred references are available under `~/repos@others/`. Use the files
below to trace original definitions, output fields and example data. The
historical notes above retain their original paths and evidence; installed
reference identities remain attached to their own versions, commits and artifact
hashes.

| Directory | Useful source and data | Consultation scope |
| --- | --- | --- |
| `AlphaSpace2` | `alphaspace2/Snapshot.py`, `Cluster.py`, `functions.py`, `VinaScoring.py`, `View.py`; `cookbooks/DataSet/` | Original detection, alpha/beta/pocket membership, space/contact/score definitions and output examples. |
| `fpocket` | `src/fpocket.c`, `voronoi.c`, `descriptors.c`, `pscoring.c`, `writepocket.c`; `headers/fparams.h`, `src/pertable.c`; `tests/reference_output/`, `data/sample/` | Original C detector, radii, descriptors, distinct scores and writers. Its volume estimator and upstream tests have their own approximation limits. |
| `pocketeer` | `src/pocketeer/api.py`, `core/{tessellation,geometry,scoring,types}.py`, `utils/io.py`; `tests/data/` | Detection, voxel volume, residue masks, ranking and JSON fields. The JSON writer omits the mask. |
| `pycasta` | `src/pycasta/{run_analysis,pocket_detection,alpha_shape,ranking,atomic_radii,cgal_wdelaunay}.py`, `utils/`, `dual_sets.py`; `src/pycasta/data/`, `data/coach420/` | Detector/ranking/radius definitions, optional triangulation routes and paired/benchmark inputs. Saved results retain their own provenance. |
| `castp-Script` | `src/castpfoldpy/client.py`; `data/j_68e5495011fa9.zip` | Remote submission/download client and saved-output coordinate reader; the server performs detection and SA/MS measurements. |
| `CastpFold` | `public/submit_calc.php`, `src/UrlManager.js`, viewer/measurement components; `public/infos/allabout/`; saved example folders | Historical frontend, server-method documentation and result schemas. The scientific `arsenal` invoked by PHP is absent from this checkout. |
| `scripts_view_pockets` | `CASTpyMOL_v3.py`, `castp.py`, `GPSS-PyMOL-Plugin/`, `caver-pymol-plugin-3.0.3/` | Historical membership/viewing tools. CAVER supplies a separate tunnel method; these files do not provide the CASTpFold kernel. |

The inspected AlphaSpace2 checkout (`1283f73db757`, declaring `0.1.2`) differs
from the qualified original `0.1.2` package bytes. The Pocketeer checkout
(`25a06df9a905`, declaring `0.3.0`) also differs from the qualified `0.4.0` wheel.
Consultation or a later source update requires a separately identified revision
and applicable revalidation before it changes an engine or scientific oracle.

Static parsing of the transferred pycasta `src/pycasta/run_analysis.py` failed at
line 457 in checkout `f3418f38cd3d`. This observation applies to that file and
revision; it does not characterize every published pycasta release or qualify
TopoMT's independent native implementation. Current receiving status remains in
the [provider plan](provider_handoff_plan.md) and provider overviews.

Other transferred references under the same directory support narrower queries:

- Molecular formats and chemistry: `mdanalysis`, `mdtraj`, `biopython`, `openmm`, `AmberClassic`, `ParmEd`, `pdbfixer`, `rdkit`, `Meeko`, `openff-toolkit` and `pytraj`.
- Visualization: `molstar`, `ngl`, `nglview`, `anywidget` and `ProteinView`.
- Quantity handling: `astropy` and `physipy`; docking definitions and outputs: `AutoDock-Vina`.

The local review receipts are `.cache/reference-repositories/provider-code-map.json`
and `.cache/reference-repositories/pull-assessment.json`. The remote observation
at `2026-11-06T21:42:51Z` found 10 identical branches, 14 proven behind and one
unknown ancestry (`AutoDock-Vina`); 12 clean checkouts were candidates for a later
fast-forward, while five dirty checkouts were protected. Pocketeer was 23 commits
behind its observed remote; preserve the identified reference revision before
any separately authorized update and revalidation. This inspection performed no
fetch or pull and changed no external checkout.
