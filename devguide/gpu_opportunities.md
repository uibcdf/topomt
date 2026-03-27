# GPU Opportunities

## Purpose

This document records which parts of TopoMT and its upstream dependencies look
like plausible GPU targets.

The goal is not to promise immediate GPU support. The goal is to identify
where acceleration is technically reasonable and where it is not yet mature
enough to drive design decisions.

The discussion here is about static kernels and reusable building blocks.
On-the-fly pocket detection during molecular dynamics is intentionally
postponed to a later design stage.

## General rule

GPU work should target kernels that are:

- numerically heavy;
- data-parallel;
- repeatedly executed;
- separable from high-level TopoMT feature semantics.

By contrast, control-heavy feature bookkeeping and small graph operations are
usually poor first GPU targets.

## Strong candidates

### Distance and overlap kernels

- atom-point distance fields;
- point-to-atom overlap tests;
- point-cloud to atom-cloud contact kernels;
- neighborhood construction around atom or point sets.

These appear repeatedly in pocket detection and characterization and are
naturally data-parallel.

### ASA and SASA style workloads

- sampling-based accessible-surface calculations;
- sphere-point accessibility masks;
- per-atom exposed-area aggregation;
- probe-radius variants of the same calculation.

These are among the most obvious GPU candidates because they spend most of
their time in repeated distance and masking operations.

### Grid and voxel occupancy

- occupancy grids around a region of interest;
- cavity masks on regular lattices;
- neighborhood propagation on voxelized spaces;
- region labeling on grids used as intermediate approximations.

This class of workload is often easier to accelerate than full
Delaunay/Voronoi pipelines.

### Batch characterization

- pocket descriptor evaluation over many candidate pockets;
- repeated local density or surrounding-atom calculations;
- batched scoring once descriptors have already been computed.

The more independent the candidate pockets are, the easier this is to batch.

## Plausible but harder targets

### Alpha-sphere supporting kernels

- repeated circumsphere-related calculations;
- candidate filtering over already generated tetrahedra;
- per-alpha descriptor evaluation.

These can benefit from GPU acceleration, but only if the data flow around
them is organized cleanly.

### Delaunay and Voronoi geometry

Native `fpocket4` and `alphaspace2` both depend on SciPy Delaunay/Voronoi
machinery today.

This is an important dependency point, but it is not the easiest first GPU
target:

- mature and portable GPU replacements are not as straightforward as for
  distance kernels;
- the surrounding algorithm often spends significant effort before and after
  triangulation anyway;
- moving only the triangulation may not dominate total runtime unless the full
  workload is profiled carefully.

For now, these steps should be treated as possible future work, not the first
acceleration milestone.

## Poor first targets

- `Topography` bookkeeping;
- feature hierarchy construction;
- graph relations between already detected features;
- documentation-facing serialization and conversion layers;
- engine dispatch and wrapper logic.

These are not where the time is usually spent.

## Relation to MolSysMT

Several GPU-friendly kernels are not specific to TopoMT and may belong in
`molsysmt` instead, especially if they become reusable molecular observables.

Likely examples:

- generic distance and overlap kernels;
- generic ASA or SASA primitives;
- general neighborhood searches;
- regular-grid occupancy helpers.

If a GPU acceleration effort produces a reusable molecular-system primitive,
the default action should be to discuss moving that primitive to `molsysmt`
rather than keeping it private inside TopoMT.

## Immediate guidance

For the current phase of TopoMT, the most reasonable GPU-oriented direction is
to think in terms of kernels, not full engines:

- first identify repeated distance, masking, and accessibility workloads;
- then isolate them behind clean APIs;
- only after that evaluate whether GPU acceleration is worth the added
  complexity.

This keeps the native engines faithful first, and only then optimizable.
