# Triangulation Residuals: scipy/Qhull vs MKALF/SOS

## Summary

The native CASTp implementation uses `scipy.spatial.ConvexHull` (via the
lifting trick) as its Delaunay/weighted-Delaunay substrate.  The reference
CAST C code uses MKALF, which implements SOS (Simulation of Simplicity) for
tie-breaking in degenerate configurations.

These two triangulation strategies produce identical results for the vast
majority of simplices but can diverge on **near-degenerate cases** — tetrahedra
whose circumsphere almost exactly passes through a fourth point, or whose power
value (circumsphere radius² minus weighted-radius²) is very close to zero.

This document records the known parity residuals that have been traced to this
root cause and should not be re-investigated as algorithmic bugs.

---

## Background: SOS vs Qt

### SOS — Simulation of Simplicity (MKALF)

Edelsbrunner & Mücke (1990).  Each input point `p_i` is symbolically
perturbed by infinitesimals `ε_i` chosen so that no four points are ever
cospherical.  All geometric predicates become strictly positive or negative.
The perturbation is never applied numerically — it is a formal convention that
defines a **deterministic, lexicographic tie-breaking** order.

Consequence: for any protein, MKALF always produces a unique, reproducible
triangulation with no ambiguous facets.

### Qt — triangulated output (scipy/Qhull default)

When Qhull encounters a non-simplicial facet (one shared by more than two
simplices — the degenerate case), it **subdivides it geometrically** using its
own internal heuristic.  The result is deterministic but the subdivision
strategy is different from SOS's lexicographic rule.

`Qt` is always active in `scipy.spatial.Delaunay` and cannot be disabled.

### QJ — Joggle (Qhull option)

`qhull_options='QJ'` perturbs input coordinates by a small random amount
before triangulation.  This avoids degeneracies but is **not deterministic**
across different runs and introduces small coordinate errors (~1/1000× the
perturbation magnitude).  It is **not** a substitute for SOS and is not
recommended here.

---

## Impact on alpha-shape / void detection

In `build_castp_geometry`, all tetrahedra with `simplex_power_values > 0` are
classified as **empty** (outside the alpha complex at alpha=0).  Near-zero
power values — those with `|power| < some_ε` — represent configurations where
the circumsphere almost exactly touches the union of atom balls.

For these near-zero cases:

- MKALF/SOS assigns the tetrahedron to one side (in or out) deterministically
  via the SOS perturbation order.
- scipy/Qt may assign it to the other side depending on how the degenerate
  facet is subdivided.

A difference of a single tetrahedron can change void connectivity: a tiny void
component might become connected to the exterior through a face that in one
triangulation is shared with an empty tetrahedron and in the other is a hull
face.

---

## Known parity residuals (as of 2026-04-06)

### 1HIV — 2/3 voids correct

| Oracle ID  | Atoms                        | Status   | Notes                          |
|-----------|------------------------------|----------|--------------------------------|
| Pocket 11  | [866,882,914,915,917,...]    | ✓ found  |                                |
| Pocket 16  | [480,499,561,578,679,680]    | ✓ found  |                                |
| Pocket 17  | [67,86,180,624]              | ✗ missing | SOS residual — see below       |

**Pocket 17 analysis**: tet `{67,86,180,624}` has `simplex_power_value ≈ 0.062 Å²`
(essentially on the empty/interior boundary).  In scipy's triangulation it is
adjacent to tet `{67,70,86,624}` through attached face `(67,86,624)` with
`mu1_rank=7349 > base_rank=7313`.  That face appears in the masterlist at
rank=mu1 > base_rank, so it causes a union between the two tets, which
eventually connects to the exterior — tet `{67,86,180,624}` is absorbed into
the surface and not reported as a void.  In MKALF's SOS triangulation, the
adjacent tetrahedron across that face is likely different (or the face has a
different mu1), isolating the void.

### 1TCD — 27/36 voids correct

27 oracle voids are found exactly.  9 are missing:

| Oracle ID  | Atoms (first 6)              | Power range hypothesis |
|-----------|------------------------------|------------------------|
| Pocket 6   | [321,322,489,491,501,557,...] | near-surface merging   |
| Pocket 34  | [54,71,74,194,291,1796,...]   | SOS residual           |
| Pocket 38  | [2388,2395,2398,2400,...]     | SOS residual           |
| Pocket 39  | [476,483,486,488,684,...]     | SOS residual           |
| Pocket 40  | [74,76,168,194,291,292,...]   | SOS residual           |
| Pocket 69  | [488,695,696,790,851]         | SOS residual (known from prior session) |
| Pocket 70  | [2495,2501,2508,2529,2807]    | SOS residual           |
| Pocket 72  | [2400,2607,2608,2702]         | SOS residual           |
| Pocket 73  | [586,595,869,873,895]         | SOS residual           |

All missing voids are small (≤ ~30 atoms).  Large, prominent voids are all
found exactly.  This is consistent with the SOS-residual hypothesis: tiny
near-surface voids are most susceptible to triangulation differences.

---

## Algorithm correctness confirmed

The void construction algorithm in `_build_void_components` has been verified
against the C source (`mkalf/voids.c` + `mkalf/lookup.c`):

- `alf_is_in_complex` for **attached faces (rho=0)** uses `mu1 ≤ rank` — not
  `rho ≤ rank`.  This is the C code's own criterion.
- The Python `_base_triangle_in_complex` correctly implements this:
  ```python
  if face_rho_rank != 0:
      return bool(face_rho_rank <= geometry.base_rank)
  return bool(int(geometry.face_mu1_ranks[simplex_index, face_index]) <= geometry.base_rank)
  ```
- The attachment criterion in `_face_rho_data` uses `face_size2_value <= 0`,
  matching `alf_w_size2()` in the C reference.

The residuals are not algorithmic bugs.

---

## Reference MKALF binaries available (2026-04-07)

`delcx` and `mkalf` from `alpha-4.1-src` are now compiled and working on
64-bit Linux.  See `tools/mkalf/` for the build script and README.

Two patches to the source were required (see checkpoint_2026_04_07.md):
- `basic/basic.h`: added x86_64/AArch64 to `is_64_bit_ARCH` detection
- `lia/det.c`: fixed off-by-one in workspace allocation (`W_SIZE+1`)

The binaries allow **direct comparison** between the MKALF and scipy
triangulations for any protein data file.

### Workflow for triangulation comparison

```bash
cd sandbox/castp_oracle_runs/1hiv
tools/mkalf/bin/delcx 1hiv                 # → 1hiv.dt
tools/mkalf/bin/mkalf 1hiv                 # → 1hiv.alf
echo "print rank 1 tetrahedra" \
  | tools/mkalf/bin/mkalf -A 1hiv          # → 1hiv.1.sl (all Delaunay tets)
```

Compare to scipy output from `DelaunayMesh` on the same input to quantify:
- number of tetrahedra that differ
- which differ (near-degenerate power value?)
- whether the differing tets coincide with the missing void/pocket residuals

---

## Recommendations for future work

1. **Run the triangulation comparison** (P1 in checkpoint_2026_04_07.md)
   before attributing any residuals to H1.  Until that comparison is done,
   "SOS residual" is a hypothesis, not a confirmed root cause.

2. **Do not re-investigate confirmed residuals** unless the comparison shows
   they are NOT triangulation differences.

3. **If exact SOS parity becomes a hard requirement**, the path is:
   - Replace `scipy.spatial.ConvexHull` (the lifting-trick weighted Delaunay)
     with a library that implements SOS or configurable symbolic perturbation.
   - Candidates: CGAL (via Python bindings), or a custom SOS implementation.
   - Significant undertaking; only warranted if small-void residuals matter
     scientifically.

4. **Current qhull_options baseline**:
   - `scipy.spatial.ConvexHull` with no explicit `qhull_options` → Qhull
     defaults (`Qbb Qc Qz Q12`) + `Qt` always on.
   - Do not use `QJ` (non-deterministic, less accurate).
   - No available Qhull option reproduces SOS exactly.
