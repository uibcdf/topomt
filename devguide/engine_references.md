# Engine References

## Purpose

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
- CASTp loading through [topomt/io/load_CASTp.py](/home/diego/repos@uibcdf/topomt/topomt/io/load_CASTp.py).

### Current status

The current integration target is faithful import and normalization of CASTp
results rather than parity against a local binary/package run.

This means CASTp is currently a loader/integration reference, not yet a fully
specified executable parity target like `fpocket4`.

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
`topomt.methods.alphaspace2` implementation is still a simplified
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
[to_be_checked.md](/home/diego/repos@uibcdf/topomt/to_be_checked.md):

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
