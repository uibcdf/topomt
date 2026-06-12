# Proposal: High-Performance GPU and Parallelization Roadmaps for Spatial Topology & Pocket Analysis

**Status:** pending; requires profiling and dependency evaluation  
**Created:** 2026-06-06  
**Last reviewed:** 2026-06-06

> This document is an exploratory option catalog. Proposed backends, complexity
> claims, and speedups are hypotheses until measured against representative
> TopoMT workloads. No dependency or execution model is approved by this
> proposal.

## Abstract

We propose a comprehensive parallelization and GPU-acceleration design system for `topomt`. Because topological pocket characterizations (such as AlphaSpace2 cavity voxelization, CASTp alpha shape triangulation, and pycasta pocket search) are extremely compute-intensive spatial solvers, implementing Numba JIT multi-threading, GPU-accelerated spatial indexing, and zero-copy data views will significantly accelerate pocket-detection pipelines, unlocking high-throughput dynamic trajectory pocket monitoring.

---

## 1. Numba JIT Compilation and Thread-Safe CPU Parallelization

### Context
Many of `topomt`'s core analytical algorithms (e.g., calculating grid volumes, filtering Voronoi vertices, and extracting pocket boundary descriptors) are implemented in pure Python with nested loops, resulting in high runtime latencies on large proteins or long trajectories.

### The Proposal
Introduce a dynamic JIT compile-and-dispatch layer using Numba:
1. **Parallel Loop Execution**: Wrap heavy geometric loops in `@lazy_njit(parallel=True)` JIT compilation, replacing standard ranges with Numba's multi-core `prange` loops.
2. **Strict Thread-Safety Patterns**: Enforce strict thread-isolation by ensuring all temporary array buffers, indices, and coordinate slices are allocated *inside* the parallel loop block. This eliminates race conditions on shared arrays.
3. **Dynamic Thread Allocation**: Integrate thread dispatching with the `molsysmt.configure` core, dynamically adjusting active worker hilos using Numba's `nb.set_num_threads()` based on the trajectory length and structure size.

```python
# Proposed Numba-accelerated thread-safe voxelization kernel
import numba as nb
import numpy as np

@nb.njit(parallel=True, cache=True)
def voxelize_pocket_grid_parallel(points, grid_origins, resolution, threshold):
    n_points = len(points)
    n_grids = len(grid_origins)
    results = np.zeros(n_grids, dtype=nb.boolean)
    
    # Safely parallelized outer loop using Numba prange
    for i in nb.prange(n_grids):
        origin = grid_origins[i]
        # Thread-local storage allocated inside the parallel loop block
        local_accum = False
        for j in range(n_points):
            dx = points[j, 0] - origin[0]
            dy = points[j, 1] - origin[1]
            dz = points[j, 2] - origin[2]
            dist_sq = dx*dx + dy*dy + dz*dz
            if dist_sq <= threshold * threshold:
                local_accum = True
                break
        results[i] = local_accum
    return results
```

---

## 2. GPU-Accelerated Spatial Indexing and Grid Voxelization

### Context
When characterizing binding pockets over massive trajectories, calculating pocket volume overlaps and spatial distances between alpha spheres across thousands of frames becomes the primary performance bottleneck.

### The Proposal
Provide a transparent GPU execution pathway using CuPy or custom CUDA kernels:
1. **O(N) GPU Cell Lists**: Port the spatial indexing of pocket atoms and alpha spheres to a GPU-based Cell List layout, enabling fast O(N) neighbor lookups and bypassing heavy O(N^2) CPU distance matrices.
2. **GPU-Bound Grid Volumes**: Execute pocket voxelization (`grid_volume`) directly in parallel GPU threads. Each grid voxel distance calculation is mapped to a dedicated CUDA thread, delivering **10x to 50x speedups** compared to multi-core CPU execution.
3. **Covariance and Overlap Matrices**: Offload pocket intersection and union matrices calculation (`overlap_matrices`) to CuPy array operations, doing highly optimized boolean intersections on device memory.

---

## 3. Unified Dispatch and Synchronization with MolSysMT Configure

### Context
Having disconnected parallelization policies between `molsysmt` and `topomt` leads to thread over-subscription, resource contention, and poor API usability (e.g. setting threads in MolSysMT does not affect TopoMT).

### The Proposal
Create a shared, thread-safe configuration bridge:
1. **Implicit Configuration Inheritance**: Design `topomt` execution kernels to query `molsysmt.configure` for active settings (`parallel_mode`, `num_threads`, `use_gpu`, `gpu_threshold`).
2. **Unified Override Contexts**: Ensure that local context managers inside `molsysmt` (like `msm.configure.context(...)`) seamlessly cascade down to internal `topomt` solvers.
3. **Coordinated Payload Thresholding**: Define unified computational payload bounds where parallelization or GPU offloading is triggered, preventing thread-creation overhead from dominating execution time on small, fast-calculating pockets.

---

## 4. Zero-Copy View Ingestion

### Context
Extracting pocket boundaries over large molecular systems currently requires deep copies of coordinates arrays across multiple boundary wrappers, generating unnecessary garbage collection pressure.

### The Proposal
Leverage `molsysmt`'s zero-copy architecture:
1. **Zero-Copy Trajectory Slicing**: Ensure `topomt` direct solvers consume the write-protected read-only NumPy coordinate views returned by `molsysmt` native structures.
2. **Immutable Boundary Checks**: Perform all boundary geometric measurements directly on the read-only coordinate views without writing to or copying the coordinate array buffers, ensuring maximum memory efficiency and speed.

---

## 5. OpenCL-Driven Pocket Voxelizers & Alpha Shape Solvers (SPIR-V)

Because Delaunay triangulation, alpha shape determination, and cavity grid voxelization are massive parallel sorting and distance-checking tasks:
1. **SPIR-V OpenCL Kernels**: Compile geometric pocket boundary solver routines into standard SPIR-V intermediate binaries.
2. **Hardware-Agnostic GPU Acceleration**: Using `pyopencl`, `topomt` can execute these pre-compiled pocket voxelization kernels on any client GPU or CPU platform (such as AMD cards, integrated Intel HD graphics, or Apple Silicon GPUs). This ensures massive acceleration factors (up to **50x**) compared to standard CPU single-threaded execution while maintaining 100% open-source, vendor-independent software pipelines.
3. **OpenGL Sharing Interoperability**: Share the voxel grid and alpha shape index buffers directly from the PyOpenCL compute context to `molsysviewer` WebGL rendering VBOs, eliminating expensive Device-to-Host (GPU to CPU) and Host-to-Device (CPU to GPU) memory transfers.
---

## 6. Evaluation Gates

This proposal remains pending until it answers the following questions with
measurements and small prototypes:

1. Which first-party TopoMT kernels dominate runtime and memory on representative
   static systems, probe sweeps, and trajectories?
2. Which bottlenecks are already implemented in optimized NumPy/SciPy or external
   libraries, and therefore unlikely to benefit from Python-level JIT work?
3. What is the smallest useful CPU-parallel contract before adding GPU backends?
4. Which optional dependency strategy preserves a lightweight, installable core?
5. How are numerical parity, determinism, units, and index mapping validated across
   CPU and accelerator implementations?
6. Which configuration belongs to TopoMT and which requires a separate proposal in
   MolSysMT's own `devguide/pending_proposals/`?

The following claims are explicitly unapproved until demonstrated:

- fixed speedup ranges such as 10x to 50x;
- one transparent backend covering Numba, CuPy, CUDA, and OpenCL;
- direct sharing between Python OpenCL buffers and browser WebGL buffers;
- zero-copy ingestion without an explicit molecular-system ownership and
  invalidation contract.

### Required evidence before acceptance

- reproducible profiler reports and benchmark datasets;
- one prioritized kernel with CPU baseline and correctness tests;
- measured crossover sizes for serial, multicore, and accelerator execution;
- dependency, packaging, and CI impact;
- fallback behavior on machines without accelerator support;
- a decision on whether the work belongs in TopoMT, MolSysMT, or a lower-level
  shared numerical package.

