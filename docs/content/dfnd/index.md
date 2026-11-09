(dfnd-theory)=
# DFND: Theory and Method

**Delaunay Flow Network Decomposition (DFND)** is TopoMT's native approach to
characterizing molecular topography with atomic geometry, a spherical probe
and a network of local spatial capacities. Its questions include where a probe
can be accommodated, how regions communicate, which boundaries delimit them,
and how their internal structure changes with the scale of observation.

This section develops the model and the implemented method together. Start with
the intuition, follow the mathematical definitions when needed, and inspect the
same small system throughout the [worked tetrahedron example](worked_tetrahedron.md).

```{figure} figures/method_pipeline.svg
:alt: Atomic input and a Delaunay mesh feed local capacities, a probe query, region decomposition, descriptors and a public Topography result.

The executed pipeline. Continuous free space is the physical reference against
which the local, discrete construction is interpreted and tested.
```

## Choose a reading route

**To start with a result:** read [the overview](overview.md), then follow the
[worked example](worked_tetrahedron.md). It predicts three probe outcomes before
running the analysis and traces one public finding back to its native support.
Return to [the geometric model](geometry_and_probe.md) and
[local capacities](local_capacities.md) for the definitions behind each step.

**To study or implement the method:** follow the four parts below, then the
derivations, conditional properties and pseudocode. The
[notation sheet](appendices/notation.md) is available throughout.

| Your question | Continue here |
| --- | --- |
| What exactly is empty or accessible, and why Delaunay? | [Geometry and the probe](geometry_and_probe.md) |
| How do local cells become regions? | [Decomposition, with a multi-cell illustration](network_and_decomposition.md#follow-a-multi-cell-graph-by-hand) |
| Why do links, physical patches and Mouth counts differ? | [Exterior and boundaries](exterior_and_boundaries.md) |
| What makes a result a Pocket, Groove or Percolating? | [Classification and descriptor formulas](classification.md) |
| What about protrusions or interfaces? | [Dry banks and relief](dry_topography.md), then [interfaces](interfaces.md) |
| What do hierarchy, paths and a changing probe tell me? | [Internal structure](hierarchy_and_paths.md), then [scale and dynamics](scale_and_dynamics.md) |
| What volume was measured, and how accurately? | [Measurements](measurements.md) |
| How do I inspect and reproduce the result? | [Results and provenance](results_and_provenance.md), then [numerical policy](numerics_and_reproducibility.md) |

## Foundations and design

```{toctree}
:maxdepth: 1

overview
geometry_and_probe
local_capacities
```

## Construction of topography

```{toctree}
:maxdepth: 1

network_and_decomposition
exterior_and_boundaries
classification
dry_topography
interfaces
hierarchy_and_paths
```

## Quantification and changing systems

```{toctree}
:maxdepth: 1

scale_and_dynamics
measurements
results_and_provenance
```

## Reliability and applicability

```{toctree}
:maxdepth: 1

numerics_and_reproducibility
validation_and_scope
```

## Worked example and formal reference

```{toctree}
:maxdepth: 1

worked_tetrahedron
appendices/notation
appendices/clearance_derivations
appendices/mathematical_properties
appendices/algorithm
references
```

## How to read the evidence

A definition states the modeled object. A mathematical implication names its
assumptions. An implemented operator describes what the software calculates.
An independently checked example establishes a result for its stated input.
These have different evidential roles. Each chapter distinguishes them where
the distinction changes the interpretation.

The account describes the source method reviewed in November 2026. Physical
boundary refinement, general public support and several numerical/scientific
questions remain under development; their current owners are linked in
[validation and scope](validation_and_scope.md). The chapters explain the present
approach and identify intended extensions with their implementation status;
they do not claim that every extension or physical inference is certified.

For task-oriented geometry/query operations, use the
[User guide](../user/dfnd_geometry.md). For fixed systems, independent references
and original-method comparisons, use [BenchLab](../benchlab/index.md).
