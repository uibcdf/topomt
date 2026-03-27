# Engine Acceleration Plan

## Purpose

This document records a future cross-cutting line of work for TopoMT:
evaluate whether each pocket-detection strategy can be accelerated through:

- CPU parallelization across a local pool of cores;
- distributed execution across nodes when the workflow allows it;
- GPU offloading for geometry-heavy or distance-heavy stages.

This should be treated as an engine-wide planning document, not as a note tied
only to `fpocket4`.

## Scope

The evaluation should eventually cover:

- native TopoMT implementations;
- wrapper-backed third-party engines;
- future engines added to `topomt.methods.*` or `topomt.wrappers.*`.

The question is not only whether an engine can run faster. The question is also
which parts of its workflow can be parallelized or offloaded without breaking
the method contract that TopoMT wants to preserve.

## Current motivation

Large systems such as `2HGR.pdb` already show that some pocket workflows can
become expensive enough to justify a separate scalability track.

This affects at least:

- geometry generation;
- candidate filtering;
- clustering;
- descriptor calculations;
- and future trajectory-oriented use cases.

Even when exact upstream parity remains the goal for `implementation='native'`,
TopoMT should still maintain a future-oriented view of which workloads are good
candidates for:

- CPU core pools;
- task partitioning;
- distributed execution;
- GPU kernels.

## Evaluation rule for engines

For each supported engine, TopoMT should eventually answer these questions:

1. Can the workflow be partitioned safely across a pool of CPU cores?
2. Can some stages be distributed across processes or nodes without invalidating
   the algorithmic semantics?
3. Are there geometry-heavy kernels that could be moved to GPU?
4. Which accelerated path, if any, still preserves the intended validation
   target?
5. If exact parity cannot be preserved under acceleration, should the fast path
   live under a separate implementation mode?

This rule should apply both to engines already under active work and to future
engines that enter the repository later.

## Near-term candidate engines

The following engines should be revisited explicitly under this lens:

- `fpocket4`
  already identified as a likely candidate for a future
  `implementation='topomt-scalable'` path.
- `alphaspace2`
  not yet evaluated in a structured way for CPU-pool execution,
  distribution, or GPU offloading.
- `pocketeer`
  future candidate once its native path is better defined.
- `pycasta`
  future candidate once its computational hotspots are clearer.

Additional engines added in the future should be reviewed under the same rule
instead of treating acceleration as an afterthought.

## Architectural constraint

Acceleration work should not silently change the semantics of the fidelity
paths.

In particular:

- `implementation='native'` should remain the parity-oriented path;
- `implementation='topomt'` should remain the corrected TopoMT path;
- accelerated or scalability-oriented strategies should live in explicitly
  named modes when they relax cost or exactness constraints.

## Related documents

- [roadmap.md](roadmap.md)
- [native_methods_plan.md](native_methods_plan.md)
- [gpu_opportunities.md](gpu_opportunities.md)
- [fpocket4_scalable_options.md](fpocket4_scalable_options.md)
