---
summary: Audit the three frozen BenchLab cases through the public Topography registry.
issue: uibcdf/topomt#146
status: active
opened: 2026-11-08
closed:
severity: medium
verification: inspected
area: [dfnd, topography, docs]
guard:
normative:
blocked_by: []
supersedes: []
---

# Public Topography receiving on the first three BenchLab units

## What

The maintainer directs development to remain with the regular tetrahedron,
closed shell and exact opening variant before adding a tube. Audit the actual
public registry, rather than inferring promotion correctness from raw dictionaries.

## How

Call `get_topography(method='dfnd')` on an in-memory MolSysMT input whose
topology comes from the retained dummy PDB. Restore full-precision coordinates
from the frozen quantity-aware JSON before analysis. Verify every received
atomic radius against the frozen array; never assume encoding preserves it.
For the child select parent atoms 6–71 from the closed parent input, retaining
source correspondence. Reuse the frozen probes, physical query and epsilon.

Inspect kernel family, native catalog refinement, public Python type, shape,
dimensionality, registry filters, Mouth parent/child relationships, units,
source/support identity, reporting suppression and valid empty output. Separate
these engineering checks from independently justified physical references.

## Why

The current three native notebooks stop at raw results and compatibility
buckets. Public promotion adds morphological classification and a feature
registry; agreement at the first layer does not validate that later layer.

## What was refuted

A raw `pocket` family is not necessarily the final public `Pocket` class.
Threshold confidence does not quantify scientific correctness. A dry native
component is not an already-promoted public convexity. Exact atom mapping does
not by itself provide the neutral support/availability contract tracked in #60.

## Scope and exclusions

One bounded public-receiving audit on existing frozen examples. Preserve all
earlier scientific files and notebooks. No new geometry, detector/server run,
provider integration, biological or installed/full-matrix qualification.
Volume precision #75, physical connectivity/reference #76 and neutral public
support #60 retain separately closable implementation/scientific gates.

## Acceptance criteria

Test the actual public route without mocking its native engine; verify received
geometry/radii/map, public catalog and relations, filters/empty output, and
reporting versus raw support under both nm/ps and pm/fs unit policies. Retain
versioned protocols/reports and case-local readable evidence. Record the new
three-case deepening priority, explicit unresolved questions, owning issues
and the evidence required to advance. File any reproduced defect separately.
