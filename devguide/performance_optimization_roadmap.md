# TopoMT Performance Optimization Roadmap

Date: 2026-04-22

## Scope

TopoMT is increasingly moving from prototype-level algorithms to production
scientific workloads. CASTp/VOLBL parity work has made this clear: algorithmic
fidelity can be achieved in pure Python, but large systems require an explicit
performance engineering phase across the library.

This document records the optimization direction for TopoMT as a whole. It is
not limited to CASTp.

## Current principle

Correctness and canonical algorithm fidelity come first. Optimization must not
silently change scientific semantics.

The preferred workflow is:

1. Establish a trusted oracle or invariant.
2. Add regression tests for the current semantics.
3. Profile the real workload.
4. Optimize the measured bottleneck.
5. Re-run oracle and invariant tests.

## Optimization layers

### 1. Algorithmic and data-structure optimization

This is the first layer to exhaust.

Examples:

- avoid rebuilding topology maps inside inner loops;
- reuse expensive geometric contexts and primitive caches;
- precompute event-local atom tuples and rank predicates;
- remove repeated format conversions;
- represent repeated topology queries with compact arrays where possible.

This layer usually preserves readability and has low dependency risk.

### 2. Scalar micro-optimization in hot paths

Small geometric kernels can be faster as explicit scalar arithmetic than as
many small NumPy calls.

Examples already observed in CASTp/VOLBL:

- replacing repeated `np.cross` in 3D scalar kernels;
- replacing `np.linalg.norm` for point-to-point 3D distances;
- replacing many tiny `np.linalg.det` calls by explicit 3x3/4x4 determinant
  helpers.

This layer should be limited to profiled hot paths. It should not spread into
ordinary code by default.

### 3. NumPy vectorization

NumPy vectorization is appropriate when the same operation is applied to large
homogeneous arrays.

Good candidates:

- bulk coordinate transforms;
- large batches of distances or triangle areas;
- array-level filtering and classification;
- dense per-atom or per-simplex descriptors.

Poor candidates:

- deeply branched traversals;
- exact-predicate code with many heterogeneous calls;
- small local 3D kernels called one at a time;
- code where vectorization would obscure the canonical algorithm.

### 4. Multithreading and multiprocessing

Parallelism should be considered when independent units are clear.

Potential units:

- independent systems in a benchmark matrix;
- independent features after connected components are established;
- independent frames in trajectory analysis;
- independent oracle comparisons.

Risks:

- Python GIL limits pure-Python threading;
- multiprocessing has serialization costs;
- shared caches must be either immutable or process-local;
- deterministic output ordering must be preserved.

### 5. Numba or compiled kernels

Numba is a strong candidate for stable scalar kernels after the Python version
is correct and profiled.

Potential CASTp/VOLBL candidates:

- determinant kernels;
- cap/segment/cap2/cap3 formulas;
- torus helper formulas;
- dense event accumulation loops after data is array-normalized.

Rules before introducing Numba:

- keep the pure-Python canonical implementation as the reference path;
- guard the accelerated path with parity tests;
- avoid making Numba a hard dependency unless project policy explicitly changes;
- measure warmup cost separately from steady-state cost.

### 6. GPU acceleration

GPU acceleration is a later-stage option, not an immediate default.

Potential candidates:

- very large batched geometric descriptors;
- trajectory-scale repeated calculations;
- dense distance or surface grids.

Poor candidates:

- branch-heavy graph traversals;
- exact symbolic predicates;
- small single-structure calculations dominated by setup overhead.

GPU work should not begin until CPU bottlenecks and data movement costs are
understood.

## CASTp/VOLBL lessons

The CASTp/VOLBL port produced several general lessons:

- Full NumPy vectorization is not always the right answer.
- For many small scalar geometric calls, explicit Python arithmetic can beat
  repeated NumPy function calls.
- Cache reuse can be more important than low-level arithmetic speed.
- A combined high-level API can be faster than calling independent blocks,
  because internal primitive caches are shared.
- Performance work must be backed by oracle values, because small formula
  changes can silently break scientific parity.

## Near-term priorities

For CASTp/VOLBL:

- keep `volbl_measurements(...)` as the preferred full-global-metric entry
  point;
- profile larger systems before adding Numba;
- reduce exact hidden-predicate setup overhead if it remains hot;
- precompute event-local atom tuples for master-list scans;
- keep expanding the CASTp 1.0 oracle matrix.

For TopoMT generally:

- identify workflows expected to run on large systems;
- add representative benchmark fixtures;
- separate correctness tests from performance benchmarks;
- define acceptable runtimes for common system sizes;
- document optional acceleration dependencies before adding them.

## Open decision

TopoMT should eventually decide whether accelerated backends are:

- optional extras, for example `topomt[accel]`;
- runtime-detected enhancements;
- required dependencies for selected methods;
- or separate experimental modules until stable.

No global decision is made here. This document only records that a dedicated
optimization phase is necessary for production-scale systems.
