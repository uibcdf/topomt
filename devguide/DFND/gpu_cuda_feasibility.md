# DFND GPU / CUDA Feasibility

Point-in-time feasibility note recorded on 2026-05-21. It evaluates which parts of
DFND could be moved to the GPU (CUDA). Nothing here is implemented; this is a
forward-looking design note so the option is not forgotten. Read alongside
[`scaling_large_systems.md`](scaling_large_systems.md).

## Summary Verdict

**Yes — the dominant cost of DFND is an excellent fit for the GPU.** The geometric
primitives (residence, gate, solvent volume) are *embarrassingly parallel over
tetrahedra/faces*, with fixed-size, branch-light work per element (small
closed-form linear solves + a reduction). That is the SIMD/CUDA sweet spot. A
custom kernel would also dissolve the capsid-scale memory wall described in
`scaling_large_systems.md`.

Delaunay construction, face deduplication, graph decomposition, and the
`get_topography` query side are less suitable and would stay on the CPU (or need a
separate effort).

## Per-Component Suitability

| Component | GPU fit | Notes |
|---|---|---|
| `tetrahedron_residence_radius_batch` | **High** | One thread per tetra; ~106 candidates, 3×3 Cramer solves, quadratic roots, min/argmax reduction. |
| `face_gate_radius_batch` | **High** | One thread per (unique) face; 2D version of the same. |
| solvent-volume batch | **High** | 512 samples/tetra of point-in-ball tests — pure independent FLOPs, GPUs love this. |
| `np.unique` face dedup | Medium | GPU sort exists (cupy/thrust); the inverse/first-appearance mapping is fiddly but doable. |
| Delaunay triangulation | Low (separate) | scipy/QHull is CPU-only. GPU Delaunay libraries exist (e.g. gDel3D / GPU-DT) but are a large separate integration. |
| graph decomposition (`connected_components`) | Medium | cuGraph exists; small part, irregular. |
| `get_topography` per-component loops | Low | Control-heavy, irregular, but small (over #components ≪ T). Keep on CPU. |

## Why the Kernels Fit So Well

The per-tetrahedron work is what GPUs are built for:

- **Fixed work per element**: every tetra enumerates the same ~106 candidates; no
  data-dependent loop bounds.
- **Branch-light, closed-form math**: the 3×3 solves use determinants/Cramer
  (no pivoting branches), the quadratics are explicit, the barycentric
  inside-test is dot products. Minimal warp divergence.
- **Independent elements**: tetrahedra do not interact during the primitive
  computation → no inter-thread communication, no locks.
- **Reduction, not materialization**: the result per tetra is `max` clearance over
  its candidates (and the winning kind). A thread can keep a *running best* and
  never store all candidates.

## The Key Win: a Custom Kernel Solves Memory AND Speed at Once

The current NumPy vectorization trades memory for speed: it materializes
`(T, K, …)` candidate arrays (~15–20 GB at 6M tetrahedra — the capsid wall).

A custom CUDA kernel inverts that trade:

```text
thread t (one tetrahedron):
    best = 0
    for each candidate c in {interior4, face3, edge2}:
        center = solve(c)                 # closed form
        if center inside tetra t:
            clr = min_i(|center - c_i| - r_i)
            best = max(best, clr)
    write best, kind  -> global memory
```

- **Memory: O(T)** (only the per-tetra outputs), not `O(T·K)`. The capsid memory
  wall disappears — no chunking needed, or arbitrarily large chunks.
- **Speed**: T tetrahedra spread over thousands of cores; the heavy
  `(T, K, 4)` distance pass becomes per-thread registers.
- **Determinism**: each thread reduces its own candidates sequentially, so the
  result is deterministic (no cross-thread atomics on the reduction).

This is the single most impactful GPU target.

## Implementation Paths (increasing effort / payoff)

1. **cupy (quick).** The batch functions are pure NumPy; cupy is largely a drop-in
   (`import cupy as np`). Gets GPU speed fast, but still materializes `(T, K, …)`
   on the GPU → bounded by GPU RAM (often 24–80 GB) → still needs chunking for
   capsids. Good first experiment / speed win.
2. **numba.cuda (middle).** Write the per-tetra kernel as a `@cuda.jit` function in
   Python. The closed-form solves, quadratics, and barycentric test are simple
   scalar arithmetic with no dynamic allocation → kernel-friendly. Gets the
   running-reduction memory benefit. Pythonic, no separate CUDA toolchain in the
   source.
3. **Hand-written CUDA / C++ extension (max).** Most control and performance
   (shared memory, occupancy tuning), but a build/maintenance burden and a harder
   dependency for the MolSysSuite install story.

Recommended sequence: prototype with **cupy** to confirm the win and validate
numerics, then move the residence/gate/volume kernels to **numba.cuda** for the
memory-efficient running reduction.

## Caveats

- **Float64 precision.** DFND clearances are in ångström with thresholds at ~1e-6;
  the marginal policy relies on that. GPUs are much faster in FP32, but FP32 could
  flip near-threshold decisions. Use FP64 (data-center GPUs — A100/H100 — have
  strong FP64; consumer GPUs are weak in FP64) or carefully bound FP32 use to
  non-decisive arithmetic.
- **Delaunay stays on the CPU** unless a GPU Delaunay backend is adopted. The
  kernels consume the mesh arrays (`simplices`, `coords`, `radii`) as input; at
  tens of millions of atoms, CPU Delaunay (time and memory) becomes its own
  bottleneck and would need separate attention.
- **Validation transfers unchanged.** The frozen CPU "brute" batch (and the
  Monte-Carlo references) validate the GPU kernels by differential testing within
  a floating-point tolerance — the same methodology that already caught two real
  bugs during CPU vectorization.
- **Dependency / install story.** A CUDA path is optional and hardware-gated; keep
  the CPU NumPy implementation as the default and the validated reference, with GPU
  as an accelerated backend selected when available.

## Recommendation

GPU acceleration is **feasible and well-matched** to DFND's hot path. The
highest-value target is a custom (numba.cuda) kernel for residence/gate/volume with
a per-thread running reduction, which delivers both large speedups and removes the
capsid-scale memory wall in one move. Keep Delaunay, dedup, graph decomposition and
the query side on the CPU initially.

Not started. This note is the design contract; the CPU implementation remains the
default and the validation reference.
