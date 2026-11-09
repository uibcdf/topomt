---
summary: Certify the opened shell's connected probe-center boundary patch at 1.4 angstroms.
issue: uibcdf/topomt#149
status: active
opened: 2026-11-08
closed:
severity: medium
verification: measured
area: [dfnd, validation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Connected opening on the fixed shell boundary

## What

Count connected components of strictly collision-free probe centers on the
declared atomic-center convex-hull boundary at 1.4 Å. Use the unchanged 66-ball
input, not native contact-cluster cardinality as reference truth.

## How

Cover all hull faces except parent-ID triangle [6,7,8] with convex expanded
atomic balls, including its boundary edges. On that triangle, intersections
with expanded balls form a finite family of compact convex planar sets. A
complete verified nerve 2-skeleton determines H1 of their union. Planar
complement duality counts the uncovered components inside the blocked boundary.
Positive subset intersections have barycentric point witnesses. Negative
intersections have convex-combination/separating-direction lower bounds,
verified without an optimizer. The retained origin ray links to the opening.

## Why

One native contact cluster and one escape ray do not exclude additional
unconnected patches. Preliminary independent geometry covers the other 127
faces with 193 leaves. The candidate nerve has 14 vertices, 31 edges, 24
triangles and beta1=1, with 181 certified subset decisions and no unresolved
decision. This preflight is known before formal certificate capture; it is
retrospective characterization, not blind evaluation.

## What was refuted

Whole-face area is not free aperture area. Connectivity on this declared hull
does not establish an intrinsic biological mouth definition or all paths of
the native graph. Optimizer convergence and rendered pixels are not proofs.

## Scope and exclusions

One input/probe and explicit hull-boundary observable. Reuse the existing
convex-cover verification, keep generation separate from checking, preserve
every earlier scientific byte and run sequential bounded calculations. No
DFND kernel, classifier, public API, provider/server or geometry change.
Other probes/cases, volume #75, public support #60 and broader #76 remain open.

## Acceptance criteria

Frozen protocol, independently checkable positive/negative intersection and
wall-cover witnesses, complete skeleton/rank checks, origin connection, unit
and rigid-motion evidence and rejection of damaged/incomplete certificates.
Inspect current raw/public contact correspondence. Publish a reviewed figure,
case explanation, source/resource receipts and the bounded conclusion with
primary mathematical references and explicit numerical margins.
