---
summary: Certify the frozen closed-shell wall at the historical 0.2 angstrom probe.
issue: uibcdf/topomt#148
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

# A stronger closed-shell wall certificate

## What

Resolve the historical 0.2 Å enclosure question on the unchanged 72-ball input.
The old whole-face circumcover bound is inconclusive at that probe; a stronger
independent coverage certificate can establish the answer without tuning DFND.

## How

Recursively subdivide each hull triangle into four midpoint triangles. Accept
a leaf only if its three vertices lie in one atom ball expanded by the probe,
with 1e-6 Å safety margin. A ball is convex, so it contains the entire leaf.
Check complete prefix-free four-way partition trees and every recorded
covering-atom/vertex inequality. A free origin strictly inside the covered hull
then belongs to a bounded free probe-center component.

## Why

The initial bounded preflight covers 140 original faces with 1037 leaves,
1336 visited nodes and maximum depth five. No unresolved leaf remains under
the predeclared depth-eight/node-20000 limits. This answers a reference question
that native labels or unsuccessful ray searches could not resolve.

## What was refuted

Failure of the old sufficient bound is not a leak proof. A wall cover proves
closure of the origin-containing region, not an exact global cavity count,
volume, mouth census or correctness of every graph path. The historical native
label was already known; this is retrospective characterization, not blind
evaluation. Preserve the earlier reference/report bytes.

## Scope and exclusions

One versioned independent certificate and verifier for the unchanged input and
historical probe, with current documentation and scoped native/public checks.
No new geometry, scientific-kernel change, original provider/server or installed
qualification. Larger #75/#76/#60 gates remain separate.

## Acceptance criteria

Freeze protocol and retain a reconstructable certificate. Verify all leaf
coverage, complete partitions, origin freedom/hull containment, explicit units
and rejection of damaged/incomplete covers. Compare the existing native/public
0.2 Å central region at the proved scope. Preserve all prior scientific bytes
and update the current reference disposition without rewriting history.
