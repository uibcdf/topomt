# CASTp Checkpoint 2026-04-07

## Purpose

Records the exact state of the native CASTp implementation after this session,
before starting the triangulation comparison work.

---

## What was done in this session

### 1. Two algorithmic fixes confirmed correct

Both fixes were identified from direct C source comparison in a previous
session.  Both are applied and verified: 16/16 tests pass.

#### Fix A — attachment criterion: `>= 1` → `== 1`

**File:** `topomt/third_party/castp/core/castp_core/geometry.py`, `_face_rho_data`

In the original code, `alf_hidden2()` returns 1 for "hidden" (attached) and 2
for degenerate.  Our attachment check used `>= 1`, which incorrectly treated
degenerate cases as attached.  Now `== 1`.

```python
is_attached = (_weighted_hidden2(...) == 1)
```

#### Fix B — component assembly uses `base_rank`, not `probe_rank`

**File:** `topomt/third_party/castp/core/castp_core/components.py`

`alf_init_pockets(rank1, rank2)` in the C source uses `rank1 = base_rank` (the
rank of rho=0), not `rank1 = probe_rank`.  Both `_build_rank_driven_components`
and `_component_boundary_faces` were updated accordingly.

### 2. `edge_rho_ranks` added to `CastpGeometry`

**File:** `topomt/third_party/castp/core/castp_core/geometry.py`

`build_castp_geometry` now returns `edge_rho_ranks: dict[tuple[int,int], int]`
— a dict keyed by sorted vertex pairs, mapping each mesh edge to its rho rank
(0 for attached edges).  This is the data structure needed for a future Fnext
walk in mouth connectivity.

`cluster_mouth_faces` signature was updated to accept
`(faces, edge_rho_ranks=None, rank1=0)` but the parameters are not yet used as
a filter (Fnext walk not yet implemented).

### 3. Hypotheses tested (H1–H5)

Five divergence hypotheses were systematically evaluated.

| ID | Hypothesis | Result |
|----|-----------|--------|
| H1 | SOS vs Qt triangulation | Real divergence; not fixable without replacing scipy |
| H2 | Hull-face depth assignment | Not a divergence — C code identical |
| H3 | Mouth connectivity (Fnext walk) | Real divergence; fix requires Fnext walk (non-trivial) |
| H4 | Attached faces: mu1 proxy | Necessary compensation for extra attached faces from Qt triangulation; reverting breaks parity |
| H5 | Hull face mu1 handling | Not a divergence |

**Current parity status (16/16 unit tests pass):**
- `1HIV` voids: 3/3 exact
- `1TCD` voids: 35/36 (1 residual traced to SOS triangulation difference)
- `1HIV` pockets+channels: 9/13 (4 residuals; main cause = Fnext walk not implemented for mouths)
- `1TCD` pockets+channels: lower (Fnext walk + triangulation residuals)

### 4. MKALF/DELCX compiled for 64-bit Linux

**Reference implementation:** `~/repos@uibcdf/Alphashape/castp/alpha-4.1-src`  
**Build script:** `tools/mkalf/build.sh`  
**Compiled binaries:** `tools/mkalf/bin/delcx`, `tools/mkalf/bin/mkalf`

Two patches to the source were required:

**Patch 1 — `basic/basic.h`**

Added x86_64 and AArch64 to the 64-bit architecture detection.  The original
code only detected MIPS and Alpha.  Without this, `Lia_DIGITS` uses the 32-bit
formula (divides by 9) despite `unsigned long` being 8 bytes on x86_64, so all
multi-precision integer buffers are half the required size.

```c
/* x86-64 / AMD64 (modern Linux/macOS 64-bit) */
#if defined (__x86_64__) || defined (__x86_64) || defined (_M_X64) || defined (_M_AMD64)
# define is_64_bit_ARCH
#endif
/* AArch64 (Apple Silicon, AWS Graviton, etc.) */
#if defined (__aarch64__)
# define is_64_bit_ARCH
#endif
```

**Patch 2 — `lia/det.c`**

`lia_det()` allocates `MALLOC(Lia_ptr, W_SIZE)` = 15 elements but the loop
`upfor(i, 0, W_SIZE)` is inclusive and writes 16 elements (indices 0..15).
Off-by-one that was hidden on 32-bit systems by malloc alignment padding.
Fix: allocate `W_SIZE + 1`.

```c
w = MALLOC (Lia_ptr, W_SIZE + 1);  /* +1: upfor(i,0,W_SIZE) writes index W_SIZE */
```

**Verified working on 1HIV:**

```
delcx 1hiv
→ 10809 tetrahedra, 0 degenerate, 1hiv.dt written

mkalf 1hiv
→ 25743 ranks, 1hiv.alf written

echo "print pockets rank 1 rank2 25744" | mkalf -A 1hiv
→ pockets output in 1hiv.1.25744.poc
```

---

## Current open problems (priority order)

### P1 — Triangulation comparison (next task)

We cannot know how many of the parity residuals come from triangulation
differences (H1) vs algorithmic differences until we compare tetrahedra
directly.

**Plan:**
1. Extract the full tetrahedra list from MKALF for 1HIV and 1TCD using
   ABC mode: `print rank 1 tetrahedra`
2. Compare to the scipy triangulation (from `DelaunayMesh`) atom-by-atom
3. Count: how many tets differ? Which ones? Do they correspond to the missing
   voids/pockets?

Oracle runs are already in `sandbox/castp_oracle_runs/1hiv/` and
`sandbox/castp_oracle_runs/1tcd/`.  The `.dt` and `.alf` files for 1HIV have
just been regenerated.

### P2 — Fnext walk for mouth connectivity (H3)

The C reference uses a Fnext walk to traverse interior tetrahedra and connect
mouth face pairs across a shared edge.  Our current implementation connects any
two mouth faces sharing an edge, which is an approximation.

The divergence from H3 costs approximately 4/13 pockets on 1HIV.

Implementing the Fnext walk requires:
- for each pair of mouth faces sharing an edge
- walk Fnext around that edge, through interior tets, to find opposite face
- only connect mouth faces that are reachable via this walk

`edge_rho_ranks` is already in `CastpGeometry`; it needs to be used in
`cluster_mouth_faces`.

### P3 — Void residual in 1TCD (Pocket 69 and others)

After triangulation comparison (P1), we will know whether the 1 void residual
in 1TCD is a genuine SOS difference or an algorithmic issue.

---

## Current code state

### Relevant files

| File | State |
|------|-------|
| `topomt/third_party/castp/core/castp_core/geometry.py` | Fixes A applied; `edge_rho_ranks` added |
| `topomt/third_party/castp/core/castp_core/components.py` | Fix B applied; `edge_rho_ranks` passed to mouths |
| `topomt/third_party/castp/core/castp_core/mouths.py` | API updated; Fnext walk not yet implemented |
| `tests/test_castp_core.py` | 16/16 passing |
| `tests/test_castp.py` | 16/16 passing (combined) |
| `tools/mkalf/build.sh` | New; builds delcx + mkalf from source |
| `tools/mkalf/README.md` | New; workflow documentation |
| `~/Alphashape/castp/alpha-4.1-src/basic/basic.h` | Patched (x86_64 detection) |
| `~/Alphashape/castp/alpha-4.1-src/lia/det.c` | Patched (W_SIZE+1) |

### Test command

```bash
python -m pytest -q tests/test_castp_core.py tests/test_castp.py
# → 16 passed
```

### Reference oracle runs

```
sandbox/castp_oracle_runs/1hiv/   # 1hiv input + 1hiv.dt + 1hiv.alf + .poc files
sandbox/castp_oracle_runs/1tcd/   # (1tcd.dt may need to be regenerated)
```

---

## What not to do next

- Do not touch mouth connectivity before completing the triangulation comparison
- Do not patch individual void residuals by hand
- Do not revisit hypotheses H2, H4, H5 (resolved)

---

## Minimal commands to resume

### Run tests

```bash
python -m pytest -q tests/test_castp_core.py tests/test_castp.py
```

### Run MKALF comparison

```bash
cd sandbox/castp_oracle_runs/1hiv
/path/to/tools/mkalf/bin/delcx 1hiv
/path/to/tools/mkalf/bin/mkalf 1hiv
echo "print rank 1 tetrahedra" | /path/to/tools/mkalf/bin/mkalf -A 1hiv
```

### Build the reference binaries (once per machine)

```bash
cd tools/mkalf
./build.sh
```
