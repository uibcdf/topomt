# CASTp Checkpoint 2026-04-08

## Summary of the session

Starting from the state recorded in `checkpoint_2026_04_07.md` (9/14 parity on 1HIV
pockets+channels), this session investigated the 5 residual cases and implemented
a key algorithmic fix that brings parity to **12/14**.

---

## Key finding: wrapping depth (`compute_tetra_depth2`)

The CASTp server uses **wrapping depth** — MKALF's `compute_tetra_depth2` — instead
of the standard max-rho pocket depth (`compute_tetra_depth`).

### Standard depth (previous implementation, `compute_tetra_depth`)

- For each tet, follows hidden-triangle links and takes the **maximum-rho** sink.
- A hull-attached face **always** routes depth to infinity, regardless of interior
  hidden neighbours.
- Result: 9/14 parity on 1HIV.

### Wrapping depth (current implementation, `compute_tetra_depth2`)

- For each tet, follows hidden-triangle links and takes the **minimum-rho** sink.
- A hull-attached face sets depth to infinity **only if no interior hidden neighbour
  has been found yet**; a finite interior hidden neighbour overrides the hull-attached
  infinity.
- Result: **12/14 parity** on 1HIV (+3 recovered: CHA-1, POC-8, POC-13).

The change is localised to `_compute_pocket_depths` in
`topomt/third_party/castp/core/castp_core/components.py`.  All 194 tests still pass (11 skipped).

### MKALF C reference (`voids.c`)

```c
// compute_tetra_depth2 (wrapping, do_wrap=1):
int min_ix = -1;
int min_rho = num_ranks+2;
// Hull-attached: only if min_ix == -1
if (alf_is_attached(...) && (min_ix == -1)) {
    min_ix = t_hash_m+1; min_rho = num_ranks+1;
}
// Interior hidden neighbour: override if rho is smaller
if (hidden_triangle(tri[i])) {
    if (new_rho < min_rho) { min_rho = new_rho; min_ix = ...; }
}
if (min_ix == -1) wrapping_depth[ix] = ix;  // self = sink
else              wrapping_depth[ix] = min_ix;
```

---

## Triangulation identity (confirmed)

`compare_triangulations.py` showed that **scipy and MKALF produce 100% identical
triangulations** when using the same radii (castp_param / pdb2alf):

```
Common: 10809 (100.0% of MKALF), Only in MKALF: 0, Only in scipy: 0
```

The earlier apparent discrepancy (9,833 vs 10,809 tets) was due to protor radii vs
castp_param radii — different radii, not different algorithms.

---

## Remaining 2/14 residuals (root cause analysis)

### POC-11 (jaccard = 0.00) — irreducible with protor radii

Oracle atoms: {855, 858, 860, 861, 867, 871, 1262, 1264, 1267, 1270, 1283}

All 44 open tets in this region flow to infinity.  Root cause:

- Tet 1054 (atoms: 875, 1267, 1286, 1305) has a hull-attached face `{875, 1286, 1305}`
  (rho=0, on the convex hull).
- **All min-rho paths** from every POC-11 tet eventually pass through sinks whose
  depth is infinity (rho = infinity_rank+1).  No finite sink is reachable from
  this cluster.
- The oracle/server likely uses slightly different radii for atoms 875/1286/1305,
  making the hull face non-attached and routing the cluster to a finite sink.
- MKALF 4.1 binary (with pdb2alf radii) also does NOT produce this as a pocket.

**Conclusion:** not fixable without the exact server radii.

### POC-12 (jaccard = 0.87) — 2 extra atoms

Oracle atoms: {869, 870, 872, 873, 877, 884, 1246, 1247, 1248, 1250, 1252, 1259, 1263}
Our native: oracle ∪ {1266, 1302}

Root cause:
- Tets 1044, 1119, 2442 contain atoms 1266/1302 and sink to component 1044 (our
  native POC-12 region).
- The server's triangulation (protor-like but not identical) likely routes these
  tets to infinity or a different sink.

**Conclusion:** radii-induced triangulation artefact; not fixable without server radii.

---

## Current parity status

| System | Feature | Oracle | Matches |
|--------|---------|--------|---------|
| 1HIV   | voids   | 3      | 3/3 ✓  |
| 1TCD   | voids   | 36     | 35/36 (1 residual = SoS triangulation) |
| 1HIV   | pockets+channels | 14 | **12/14** |

---

## Code state after this session

| File | Change |
|------|--------|
| `topomt/third_party/castp/core/castp_core/components.py` | `_compute_pocket_depths` replaced with wrapping-depth logic |
| All other files | Unchanged |

### Test command

```bash
python -m pytest tests/ -n 12 -q
# → 194 passed, 11 skipped
```

---

## What remains

1. **POC-11 / POC-12**: accept as radii-induced residuals (12/14 is the practical
   limit with protor radii + scipy QHull).
2. **DFND** (deformable protein pocket detection): tests still skipped.
3. **Mouths as top-level records**: `castp()` could emit mouth records separately
   for downstream analysis.
4. **1TCD void residual (tet 69)**: traced to SoS triangulation difference; accept
   or investigate further.
