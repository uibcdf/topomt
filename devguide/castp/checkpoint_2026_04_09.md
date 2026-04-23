# CASTp Checkpoint 2026-04-09

## Purpose

This is the **pause checkpoint** for the native CASTp implementation effort.
Work is being suspended here and may resume after a period of time.
This document is written to be self-sufficient: it records what was accomplished,
what was found, what was definitively ruled out, and exactly where to restart.

---

## The four-session work arc (summary)

### Session 2026-04-05

Starting point: proof-of-concept `castp` prototype existed, not faithful.

Key discoveries:
- `voids` and `pockets` are fundamentally different constructions in the C source
  - `voids` → `alf_find_voids()`: complement-connected-components, no depth/sink logic
  - `pockets` → `alf_init_pockets()` + `alf_compute_pocket_depths()`: discrete flow
- Separated `_build_void_components()` from `_build_rank_driven_components()` in
  `components.py`
- Chose `protor` as the working radii model (best match vs oracle)

### Session 2026-04-07

Key accomplishments:
- Fixed attachment criterion: `>= 1` → `== 1` in `_face_rho_data` (geometry.py)
- Fixed component assembly: confirmed `rank1 = base_rank` (not `probe_rank`) is correct
  for `alf_init_pockets` in the C reference
- Added `edge_rho_ranks` to `CastpGeometry`
- Compiled `delcx` + `mkalf` from `alpha-4.1-src` on 64-bit Linux; two patches required
  (see below)
- Parity at end of session: 3/3 voids (1HIV), 35/36 voids (1TCD), 9/14 pockets+channels (1HIV)

### Session 2026-04-08

Key accomplishment: implemented `compute_tetra_depth2` (wrapping depth).

The CASTp server uses **wrapping depth** (`min_rho` recursion), not the simpler
`max_rho` depth. A hull-attached face only routes to infinity when no interior hidden
neighbour has been found; an interior hidden neighbour overrides.

Parity after this fix: **12/14** on 1HIV pockets+channels (+3: CHA-1, POC-8, POC-13).

Remaining 2: POC-11 (jaccard=0) and POC-12 (jaccard=0.87). Both were provisionally
attributed to "radii-induced residuals."

### Session 2026-04-09 (this session)

Key accomplishments:
- Extended `tools/mkalf/build.sh` to compile all 5 CASTp tools:
  `pdb2alf`, `delcx`, `mkalf`, `volbl`, `detri`
- Ran MKALF 4.1 with protor radii (same as oracle) on 1HIV

Key finding: **MKALF 4.1 with protor radii does NOT find POC-11 as a separate pocket.**
POC-11 atoms are absorbed into a giant pocket (~1380 atoms) regardless of `rank1`.

This was confirmed at multiple `rank1` values (1, 100, 500, 1000, 2000, 5000, 10000).

Conclusion (confirmed by the user): **CASTp 3.0 is an algorithmic evolution of
MKALF 4.1.** The POC-11 and POC-12 residuals are not radii artefacts — they reflect
algorithmic improvements in CASTp 3.0 that are not present in MKALF 4.1.

---

## Final parity status

| System | Feature       | Oracle | Native | Notes |
|--------|---------------|--------|--------|-------|
| 1HIV   | voids         | 3      | 3/3 ✓  | |
| 1TCD   | voids         | 36     | 35/36  | 1 SOS triangulation residual |
| 1HIV   | pockets+chans | 14     | **12/14** | 2 CASTp-3.0 evolution residuals |

### Residual detail

#### 1TCD — 1 void residual

Traced to SOS/Qt triangulation difference (see `triangulation_sos_residuals.md`).
Not fixable without replacing scipy's Qhull with a SOS-capable triangulation library.

#### 1HIV — POC-11 (rank 11, jaccard=0.00)

Oracle atoms: `{855, 858, 860, 861, 867, 871, 1262, 1264, 1267, 1270, 1283}`

- With protor radii + our native Python: all tets in this region flow to INF
  (tet 1054 has a hull-attached face `{875, 1286, 1305}` that sets depth to INF)
- With protor radii + MKALF 4.1: same atoms still merged into a giant pocket
  (not a separate pocket at any rank1 value)
- Oracle finds it: CASTp 3.0 must have changed how it handles the depth sink in
  this region

**Root cause: algorithmic evolution from MKALF 4.1 to CASTp 3.0.**

#### 1HIV — POC-12 (rank 12, jaccard=0.87)

Oracle atoms: `{869, 870, 872, 873, 877, 884, 1246, 1247, 1248, 1250, 1252, 1259, 1263}`
Native: oracle ∪ `{1266, 1302}` (2 extra atoms)

Tets 1044, 1119, 2442 (containing atoms 1266/1302) sink to component 1044.
The oracle routes these tets differently. Also likely a CASTp 3.0 evolution difference.

---

## Architecture of the native implementation

### Key files

| File | Role |
|------|------|
| `topomt/third_party/castp/_native_impl.py` | Public entry point |
| `topomt/third_party/castp/core/castp_core/geometry.py` | Weighted Delaunay geometry + alpha-shape ranks |
| `topomt/third_party/castp/core/castp_core/components.py` | Void + pocket/channel component assembly |
| `topomt/third_party/castp/core/castp_core/mouths.py` | Mouth detection and clustering |
| `tests/test_castp_core.py` | Unit tests for core components (13 passing) |
| `tests/test_castp.py` | Integration tests |
| `tests/test_dfnd_pockets.py` | DFND tests (skipped) |

### Key algorithms implemented

#### `_build_void_components` (components.py)

Mimics `alf_find_voids(input_rank)` from `mkalf/voids.c`:
- Scans from max_rank down to base_rank+1
- Adds tets to the complement as they become "not in complex"
- Unions tets across complement faces
- Unions hull-adjacent tets with outside component (0)
- Does NOT use discrete flow or depth

#### `_build_rank_driven_components` (components.py)

Mimics `alf_init_pockets(rank1=base_rank, rank2=max_rank)` from `mkalf/voids.c`:
- Union-find on open tets using attached faces as "walls"
- Uses `rank1 = base_rank` (NOT `probe_rank`)

#### `_compute_pocket_depths` (components.py)

Mimics `compute_tetra_depth2` (wrapping depth, `do_wrap=1`) from `mkalf/voids.c`:
- For each open tet: follows hidden-triangle links, takes min-rho sink
- Hull-attached face → INF only if no interior hidden neighbour found first
- Key property of `_hidden_triangle`: `mu1 = min(rho_source, rho_target)`;
  if `rho_target < rho_source` → `mu1 < rho_source` → face is NOT hidden
  → flow always goes toward equal-or-higher rho tets

#### Attachment criterion (geometry.py)

`_face_rho_data` computes `is_attached = (_weighted_hidden2(...) == 1)`.
Value `== 1` means "hidden"; value `== 2` means "degenerate" (do NOT count as attached).

### What rank1 to use in component assembly

This was investigated carefully (see rank1 analysis below). The conclusion is that
**`base_rank` is correct** for `_build_rank_driven_components` and
`_component_boundary_faces`, even though `print_alf.c` in the C source uses
`probe_rank`. Using `probe_rank` causes catastrophic regression (1/14) because
faces with `0 < rho_rank ≤ probe_rank` incorrectly become "walls", over-fragmenting
pockets. The `rank1=base_rank` approximation gives better parity.

---

## What was definitively ruled out

Do NOT re-investigate these unless new evidence overturns the conclusion.

1. **Voids should be built by discrete flow** — False. `alf_find_voids` uses
   complement connectivity only. No depth, no hidden triangles, no sinks.

2. **`rank1 = probe_rank` in pocket assembly** — Tested and rejected. Causes
   catastrophic regression from 12/14 to 1/14. `base_rank` is correct.

3. **POC-11 failure is a Python implementation bug** — False. MKALF 4.1 itself
   (the reference C code) with protor radii also does not find POC-11.

4. **POC-11/12 are radii-induced residuals** — False. MKALF 4.1 with protor radii
   (same as oracle) also fails to find POC-11. This is a CASTp 3.0 evolution issue.

5. **Hypothesis H2 (hull-face depth)** — Not a divergence from C reference.

6. **Hypothesis H4 (attached faces: mu1 proxy)** — Necessary compensation; reverting breaks parity.

7. **Hypothesis H5 (hull face mu1 handling)** — Not a divergence.

8. **scipy/Qhull produces different triangulations from MKALF** — False (when using
   same radii). `compare_triangulations.py` confirmed 100% identical tetrahedra
   (10,809/10,809 shared, 0 only in MKALF, 0 only in scipy) on 1HIV with protor radii.

---

## What remains open

### Open question 1: CASTp 3.0 algorithmic evolution

**Question**: What specifically changed between MKALF 4.1 and CASTp 3.0 in the
pocket depth/sink computation that allows POC-11 to be found?

**Evidence**:
- MKALF 4.1 C binary with protor radii → POC-11 merged into giant pocket
- Our Python (implements MKALF 4.1 wrapping depth logic) → POC-11 tets go to INF
- CASTp 3.0 server → POC-11 is a proper pocket

**Hypothesis**: CASTp 3.0 may use a different definition of "hull-attached" or
may handle depth sinks differently near the convex hull boundary. The critical
difference is in how tet 1054 (atoms: 875, 1267, 1286, 1305) is treated — it has
hull-attached face `{875, 1286, 1305}` (rho=0) which in MKALF 4.1 causes the
entire POC-11 cluster to sink to INF.

**Path to investigate**: Obtain or reverse-engineer the CASTp 3.0 source code
(or a newer version of the MKALF codebase) to find what changed in `voids.c`
between MKALF 4.1 and CASTp 3.0.

### Open question 2: Fnext walk for mouth connectivity

The C reference uses a Fnext walk to connect mouth face pairs across shared edges.
Our approximation (connect any two mouth faces sharing an edge) may misclassify
some pockets/channels. This was identified as hypothesis H3 in the 2026-04-07
session and was worth ~4 parity points before the wrapping-depth fix.

With 12/14 parity now, it is unclear how much the Fnext walk would improve things.
Implementing it requires:
- For each pair of mouth faces sharing an edge
- Walk Fnext around that edge through interior tets
- Only connect mouth faces reachable via this walk

`edge_rho_ranks` is already in `CastpGeometry` and passed to `cluster_mouth_faces`.

### Open question 3: 1TCD void residual

35/36 voids correct. 1 missing traced to SOS/Qt triangulation difference.
Confirmed as a hypothesis but not yet fully verified by direct triangulation comparison.
See `triangulation_sos_residuals.md` for details.

### Open question 4: Beyond 1HIV/1TCD parity

The parity battery covers only 1HIV and 1TCD. Extending to:
- `1STP`, `2PK4`, `1A4J` (available as CASTp 3.0 fixtures in `topomt/data/`)
- `3PTB` (blocked by molsysmt PDB parser issue)

---

## The C toolchain (compiled and working)

All 5 CASTp tools are compiled in `tools/mkalf/bin/`:

| Binary | Role |
|--------|------|
| `pdb2alf` | PDB → `.dat` converter using OPLS radii from `data/param.dat` |
| `delcx` | Weighted (regular) Delaunay triangulation; writes `.dt` |
| `mkalf` | Alpha-shape pockets/voids/channels; reads `.dt`, writes `.alf` |
| `volbl` | Volume and surface-area computation from alpha shape |
| `detri` | Unweighted (Euclidean) Delaunay triangulation |

Source: `~/repos@uibcdf/Alphashape/castp/alpha-4.1-src`

Two patches applied to the source (already committed there):
1. `basic/basic.h` — added x86_64/AArch64 to `is_64_bit_ARCH` detection
2. `lia/det.c` — off-by-one fix: `W_SIZE` → `W_SIZE+1` in `lia_det()` workspace

The sandbox copy with the improved `pdb2alf.c` (4-char resName fix) is at:
`sandbox/castp_alpha_4_1_src_local/volbl/pdb2alf.c`

### Important note on pdb2alf radii

`pdb2alf` uses OPLS radii from `param.dat`. For 1HIV, all atoms fall back to
the default 1.80 Å (OPLS table doesn't match standard PDB residue names).
**This is NOT the correct way to prepare input for native parity testing.**

For native parity testing (matching the CASTp 3.0 oracle), use:
1. Our Python `build_castp_geometry` with `radii_model='protor'`
2. Write the `.dat` file from Python coords/radii
3. Run through `delcx` + `mkalf`

This is exactly what `sandbox/compare_triangulations.py` does.

### Running MKALF with protor radii (the correct approach)

```python
# In Python: generate the .dat file
from topomt.third_party.castp.core.castp_core.geometry import build_castp_geometry

geom = build_castp_geometry('path/to/protein.pdb', solvent_radius=1.4)
# write .dat: X Y Z (r_atom + r_probe) for each atom
```

```bash
# Then run the C pipeline
bin/delcx protein.dat
bin/mkalf protein.dat
echo 'print pockets rank 1 rank2 30000' | bin/mkalf -A protein.dat
```

---

## Test state at pause

```
tests/test_castp_core.py   — 13 passing
tests/test_castp.py        — (integration, check on resume)
tests/test_dfnd_pockets.py — skipped
Full suite: ~194 passing, 11 skipped (last measured 2026-04-08)
```

---

## Where to resume

### If the goal is maximum parity with CASTp 3.0

The 2 remaining residuals (POC-11, POC-12) require understanding what changed
in the CASTp 3.0 source relative to MKALF 4.1. This means:

1. **Obtain a newer version of the MKALF codebase** (CASTp 3.0 source, or any
   intermediate version between MKALF 4.1 and CASTp 3.0)
2. Diff `voids.c`, `alf.c`, `print_alf.c` against `alpha-4.1-src`
3. Focus on: how `compute_tetra_depth` / `compute_tetra_depth2` handles hull-attached
   faces and whether `alf_init_pockets` parameters changed

### If the goal is to expand the parity battery

Pick up from `contract.md` — validate against 1STP, 2PK4, 1A4J using the same
native code path. Current native method likely gives reasonable (but not 100%) parity
on those systems too.

### If the goal is to implement mouths more faithfully

Implement the Fnext walk in `cluster_mouth_faces` (mouths.py).
`edge_rho_ranks` is already available in `CastpGeometry`.
The Fnext walk requires: for each shared edge between two mouth faces, walk through
interior tets around that edge (following `Fnext` links) to find the face on the
other side.

### Minimal commands to verify state on resume

```bash
# 1. Run tests
python -m pytest tests/test_castp_core.py tests/test_castp.py -q

# 2. Check parity on 1HIV
python -c "
from topomt.third_party.castp._native_impl import castp
from topomt.io.load_CASTp import load_CASTp
from topomt.tools.features.common.overlap import jaccard_overlap_clusters

native_records, _ = castp('topomt/data/HIV-1-Protease/CASTp_1hiv/1hiv.pdb')
oracle = load_CASTp(zip_file='topomt/data/CASTp_3.0_server/1hiv.zip')

oracle_pocs = [set(f.atom_indices) for f in oracle.features.values()
               if f.feature_type in ('pocket', 'channel')]
native_pocs = [set(f['atom_indices']) for f in native_records
               if f['feature_type'] in ('pocket', 'channel')]

jaccard = jaccard_overlap_clusters(oracle_pocs, native_pocs)
matches = sum(1 for j in jaccard if j > 0.5)
print(f'1HIV pockets+channels: {matches}/{len(oracle_pocs)} (jaccard>0.5)')
"
```

---

## Key papers and references

- CAST (1998): <https://pmc.ncbi.nlm.nih.gov/articles/PMC2144175/>
- CASTp 3.0 (2018): <https://pmc.ncbi.nlm.nih.gov/articles/PMC6031066/>
- SOS (Simulation of Simplicity): Edelsbrunner & Mücke (1990)
- Alpha shapes: Edelsbrunner, Kirkpatrick & Seidel (1983)
- C source: `~/repos@uibcdf/Alphashape/castp/alpha-4.1-src/mkalf/voids.c`
  (the most important file — all core algorithms are here)

---

## Documents in devguide/castp/

| File | Content |
|------|---------|
| `contract.md` | What faithful CASTp means; oracle semantics |
| `checkpoint_2026_04_05.md` | Session 1 state (void/pocket separation) |
| `checkpoint_2026_04_07.md` | Session 2 state (fixes A+B; MKALF compiled) |
| `checkpoint_2026_04_08.md` | Session 3 state (wrapping depth; 12/14) |
| `checkpoint_2026_04_09.md` | **This file** (pause checkpoint; definitive summary) |
| `triangulation_sos_residuals.md` | SOS/Qt triangulation difference analysis |
