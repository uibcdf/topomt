---
summary: Audit the three frozen BenchLab cases through the public Topography registry.
issue: uibcdf/topomt#146
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [dfnd, topography, docs]
guard: tests/test_benchlab_public_topography.py::test_public_three_case_projection_retains_native_catalog_and_relations
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

## Resolution

Protocol/priority commit `3206fc6` precedes recorded receiving; initial public
tests and historical native outcomes were already known. Actual public calls
restore full-precision coordinates through MolSysMT and verify every received
radius against the frozen explicit arrays. The opening selects parent atoms
6–71. All 145 earlier scientific artifact/notebook hashes remain unchanged.

The nine primary controls produce tetrahedron Percolating / Void / empty;
closed shell Channel plus ten Mouth children / Void / empty; and opening Pocket
plus one Mouth / Void / empty. The guard verifies actual Python classes, catalog
names, shape/dimensionality/type filters, bidirectional Mouth relations, units,
input snapshots and contextual support keys under two unit policies. Reporting
removes regions and child mouths while retaining raw support/result identity.
Large-probe emptiness retains the mesh/dry substrate. The stronger 0.2 Å
reference under #148 additionally agrees with the public Void/no-Mouth result.

Three case-local public pages link versioned protocols/reports; a common
walkthrough explains refinement, threshold confidence, legacy dimensionality,
reporting and native-only dry structures. Its documented code executes. Reports
carry actual source/software identities and bounded resource measurements; the
prior human version-file edit remains intact and is included in the source hash.
The admission defect discovered here is resolved separately under #147.

No classification/scientific-kernel correction was needed on these inputs.
This does not establish complete static/public schema adoption: the runtime
neutral percolating shape works, but the existing `ShapeType` Literal omits
`neutral`; the inspected mismatch is handed to #60's public-type follow-up.
Dry components are not already public convexities/interfaces. Mouth clusters
and threshold confidence do not gain independent physical validity by storage.

Validation: 100 selected current/prior-case, public dispatch/query and governance
tests pass on shared Python 3.14.10. Repository Ruff passes (552 files formatted)
and focused mypy passes for eight affected Python files. Full HTML builds with
the same twelve existing warnings and no new warning; three public case pages,
the common example, certificate page/figure and ten new byte-matched downloads
are checked. Receiving uses one CPU/numerical worker, 6 GiB process address-space
ceiling and bounded CPU; primary observed process RSS stays below 300 MiB.
These are execution receipts, not comparative performance measurements.

The three-case deepening priority is recorded in root AGENTS.md, the active
checkpoint and the owned plan. Physical mouth patches/paths, then analytic
tetrahedron volume and #75 uncertainty/convergence remain necessary work.
#75/#76/#60 stay open; the tube and proteins remain deferred. Full suite/matrix
and installed qualification are not claimed. Required evidence is versioned;
task-owned builders/logs/rendered preview remain in ignored cache for review,
and the redundant copied docs source can be removed after publication.
