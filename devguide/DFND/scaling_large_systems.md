# DFND Scaling to Large Systems

Point-in-time design note recorded on 2026-05-21, after vectorizing the DFND
geometric primitives. It analyzes how the current implementation scales toward
very large systems (e.g. an all-atom viral capsid) and records the changes that
will be needed. None of the scaling work below is implemented yet; this is a
design contract so it is not lost.

## 1. Current State (the baseline this note builds on)

The geometric primitives are vectorized over all tetrahedra at once and validated
bit-for-bit against the scalar oracles plus Monte-Carlo references:

- `tetrahedron_residence_radius_batch` (R_residence), `face_gate_radius_batch`
  (R_gate), and the solvent-volume batch.
- The face gate is deduplicated per unique face (each internal face is shared by
  two tetrahedra).
- No per-tetrahedron Python loops remain in `_initialize_geometry`.

Measured on `3ptb` (1629 heavy atoms → 10601 tetrahedra), warm build ≈ 4.3 s:

| Phase | Time | Notes |
|---|---|---|
| DelaunayMesh (scipy + mesh module) | ~1.7 s | separate concern |
| residence batch | ~1.28 s | ~0.12 ms/tetra; 106 candidate slots/tetra |
| volume batch | ~1.21 s | 512 samples/tetra (resolution 8) |
| gate batch (unique faces) | ~0.4 s | 50% of 4T faces |

Residence candidate budget per tetrahedron: `interior4 = 2`, `face3 = 4×4×2 = 32`,
`edge2 = 6×6×2 = 72` → ~106 candidate slots.

## 2. How It Scales

A Delaunay triangulation of `N` atoms yields about `T ≈ 6N` tetrahedra.

- All-atom capsid, `N ≈ 1M` → `T ≈ 6M`.
- Larger capsid, `N ≈ 10M` → `T ≈ 60M`.

**Time is linear in `T`** (Delaunay is `O(N log N)`; the per-tetrahedron work is
`O(T)`). Complexity is fine. The problem is memory, and then absolute time.

## 3. The Wall: Batch Memory

The current vectorization materializes candidate arrays of shape `(T, K, …)` with
`K ≈ 106` for **all** tetrahedra simultaneously:

```text
C    = (T, 106, 3) float64
dist = (T, 106, 4) float64
```

| T | C | dist |
|---|---|---|
| 10601 (3ptb) | ~36 MB | ~48 MB (trivial) |
| 6,000,000 (≈1M-atom capsid) | ~15 GB | ~20 GB (infeasible) |

The solvent-volume batch (512 samples/tetra) and the gate batch (over ~2T unique
faces) scale the same way. So the "compute everything at once" vectorization
trades time for memory: ideal at 10k tetrahedra, catastrophic at millions.

## 4. The Fix: Chunking

Process tetrahedra in blocks (e.g. 100k at a time):

```text
C per block = 100k × 106 × 3 × 8 B ≈ 250 MB   (bounded)
```

- Loop over `ceil(T / block)` chunks; each chunk is fully vectorized.
- Peak memory is `O(block · K)`, independent of `T`.
- Time stays linear in `T`; speed per chunk is unchanged.
- Blocks are independent → trivially parallelizable (threads/processes).

Implementation shape: wrap `tetrahedron_residence_radius_batch`,
`face_gate_radius_batch`, and the volume batch in a chunk loop that accumulates the
per-tetra `(T,)` outputs. The frozen brute (non-chunked) reference validates that
the chunked result is identical.

This is the one change that is *required* to run millions of atoms; everything
else below is absolute-time tuning.

## 5. Other Limits at Capsid Scale (in priority order)

1. **scipy / QHull Delaunay.** Handles millions of points but is heavy: memory
   `O(N)` (6M tetra × 8 ints ≈ 400 MB of simplices + neighbors is fine), time on
   the order of minutes. For tens of millions of points it may need a different
   Delaunay backend or an out-of-core / domain-decomposed approach.
2. **Absolute time.** ~0.12 ms/tetra (residence) → 6M tetra ≈ 12 min for residence
   alone, linear. The **volume batch (512 samples/tetra) is the heaviest** term.
   Total capsid build: tens of minutes to hours. Mitigations: chunking +
   Numba/parallelism per block; coarser volume sampling; or skipping the volume
   estimate for cells that are clearly dry or clearly resident.
3. **`np.unique` over 4T faces** (face dedup / global ids): 24M rows × 3 ints,
   `O(4T log 4T)` sort, ~GB of memory. Feasible but watch memory; can also be
   chunked or replaced by a hashing scheme if needed.
4. **Do NOT trigger the mesh's Python face-index cache at scale.** The mesh's
   `get_face_index` builds a Python dict over 4T faces (GBs, slow). Production DFND
   no longer calls it — `face_ids_per_tet_face` is built vectorized via `np.unique`
   reproducing the mesh's 1-based first-appearance numbering. Keep it that way; the
   dict is only exercised by a traceability unit test on tiny fixtures.
5. **`get_topography` (query side).** `connected_components` over a sparse graph of
   `T` nodes scales well (scipy sparse). The remaining per-domain Python loops run
   over the number of domains (≪ T), likely fine, but should be profiled at scale.

## 6. What Is NOT Worth Doing (already analyzed)

Edge-candidate deduplication — **and this stays true at capsid scale, because the
benefit is scale-invariant.** Each tetrahedron edge is shared by a ring of ~5
tetrahedra, but only the "self-pair" 2-tangent candidate (6 of 36 edge combos)
depends solely on the edge atoms and is dedupable; the 30 "cross-pair" candidates
depend on the tetrahedron's other atoms and are inherently per-tetrahedron.

Crucially, deduplication would save only the candidate-*center generation*, not its
*evaluation*: a shared self-pair center still has to be tested for
inside-tetrahedron membership and clearance (min over the cell's four atoms)
*separately for each tetrahedron in the ring*, because both depend on the specific
cell. The evaluation (the `(T, 106, 4)` distance/clearance pass) dominates the
residence batch; the self-pair generation is ~15 ms of ~1.28 s on 3ptb (~1%).

All the relevant ratios are constant in `N`: the mean edge ring (~5.2) is a local
property of 3D Delaunay (independent of `N`), self-pairs are 6 of 36 combos, and
generation is a fixed fraction of the batch. So at 6M tetrahedra (residence ≈ 12
min) the dedup still buys ~1% (~7 s) at the same high restructuring cost. Memory
is unaffected too: `K` per tetrahedron is unchanged, so the `(T, K, …)` arrays do
not shrink. Contrast with face deduplication, which removed the *entire* gate
computation for a face shared by exactly two tetrahedra (a clean 2×), and was
therefore worth doing.

Verdict: not worth it at any scale. See also [`known_limitations.md`](known_limitations.md).

## 7. Recommendation

The capsid-scale roadmap, in order:

1. **Chunked batching** (required for memory; bounded `O(block·K)`, linear time,
   parallelizable). Validate the chunked result against the frozen brute reference.
2. **Per-block parallelism** (Numba or multiprocessing) for absolute time.
3. **Volume-estimate cost control** (coarser sampling or skip clearly dry/resident
   cells) — the dominant per-tetra term.
4. Evaluate the Delaunay backend for tens-of-millions-of-atom systems.

Not started yet. This note is the design contract; the optimization is paused at a
~4.3 s warm build for protein-scale systems (3ptb), all primitives vectorized,
gate deduplicated per face, validated bit-for-bit against the scalar oracles and
Monte-Carlo references.
