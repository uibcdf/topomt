(dfnd-theory)=
# DFND: Theory and Method

A cavity may accommodate a probe even when access from outside is blocked.
Changing the probe size can change both accommodation and the contacts between
regions. These distinctions matter when interpreting a buried cavity, an open
depression or a possible access route in a molecular structure.

**Delaunay Flow Network Decomposition (DFND)** is TopoMT's native approach to
organizing these geometric observations. It represents atoms as balls, measures
local accommodation and face contacts for a spherical probe, and groups the
resulting graph into regions that you can inspect through `Topography`.

```{figure} ../benchlab/synthetic/regular_tetrahedron/artifacts/native_study_v1/system_geometry.png
:alt: Four equal atomic balls at tetrahedron vertices, with a central position and four face centers marked.
:width: 460px

Four atoms are enough to separate two questions: can a probe fit inside, and
can it enter? The [worked example](worked_tetrahedron.md) answers them at three
probe sizes using independently justified geometry. Its simplicity lets us
understand the observations before studying proteins.
```

You can follow the explanation without executing code. The examples provide
stored outcomes first, with downloads and Python inspection available when you
want to reproduce them.

## What you can obtain today

| Layer | Present scope | Read more |
| --- | --- | --- |
| Public findings | Void, Pocket/Channel, Percolating and supported morphological refinements; native-link Mouth children on pocket/channel families. | [Classification](classification.md), [public results](results_and_provenance.md) |
| Native descriptions | Resident/transit supports, dry banks, boundaries, depth, provisional chamber/throat and interface descriptors; skeleton and matching helpers. | [Decomposition](network_and_decomposition.md), [dry side](dry_topography.md), [paths](hierarchy_and_paths.md) |
| Developing extensions | Complete physical boundary patches and their attachment; general relief features and localized molecular interface relations. | [Boundaries](exterior_and_boundaries.md), [interfaces](interfaces.md) |

These are availability statements. A software output called canonical is not
thereby a certified physical path or a validated biological detector. Current
graph connectivity is a local construction; [validation and scope](validation_and_scope.md)
explain the independent evidence and outstanding questions.

## Choose a reading route

**To start with a result:** read [the overview](overview.md), then follow the
[worked example](worked_tetrahedron.md). It predicts three probe outcomes before
running the analysis and traces one public finding back to its native support.
Return to [the geometric model](geometry_and_probe.md) and
[local capacities](local_capacities.md) for the definitions behind each step.

**To study or implement the method:** follow the four parts below, then the
derivations, conditional properties and pseudocode. The
[notation sheet](appendices/notation.md) is available throughout.

For a many-cell example with a public Mouth, use the
[three-case public walkthrough](../benchlab/synthetic/public_topography.md).
For task-oriented calls and installation context, use the
[User guide](../user/dfnd_geometry.md).

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
