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

**To understand a result:** read [the overview](overview.md),
[the geometric model](geometry_and_probe.md), the summaries of
[local capacities](local_capacities.md) and [decomposition](network_and_decomposition.md),
then [classification](classification.md) and the [worked example](worked_tetrahedron.md).
The example connects a public finding to its exact input and native support.

**To study or implement the method:** follow the four parts below, then the
derivations, conditional properties and pseudocode. The
[notation sheet](appendices/notation.md) is available throughout.

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
[validation and scope](validation_and_scope.md). This is a complete explanation
of the present approach and its intended extensions, not a claim that every
extension is implemented or every physical inference certified.

For task-oriented geometry/query operations, use the
[User guide](../user/dfnd_geometry.md). For fixed systems, independent references
and original-method comparisons, use [BenchLab](../benchlab/index.md).
