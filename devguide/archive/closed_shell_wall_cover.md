---
summary: Certify the frozen closed-shell wall at the historical 0.2 angstrom probe.
issue: uibcdf/topomt#148
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [dfnd, validation]
guard: tests/test_closed_shell_wall_cover.py::test_complete_convex_ball_cover_certifies_the_historical_probe
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

## Resolution

Protocol `3206fc6` fixes the existing input/probe, 1e-6 Å safety margin,
depth-eight/node-20000 limits and the convexity/complete-partition proof.
Initial preflight and historical native labels were already known. The retained
certificate covers 140 original hull faces with 1037 accepted leaves, 1336
visited nodes, maximum depth five and no unresolved pieces. Minimum vertex
safety margin is 0.000051741549 Å; origin free-space margin after expansion
is 3.968062464 Å, with strict hull containment.

The offline `devtools/verify_closed_shell_wall_cover.py` reconstructs every
leaf from the original face and ordered midpoint path, verifies covering-atom
inequalities, explicit units/input/protocol identity and complete prefix-free
four-way trees. It imports no TopoMT/DFND and calls no detector. Convexity
covers each full leaf; complete covered hull plus free strictly interior
origin establishes a bounded origin-containing probe-center component.
Floating-point distances retain the declared margin; this is not formal
interval arithmetic.

Five guards verify two non-default unit policies, missing-leaf and wrong-atom
rejection and actual public receiving at 0.2 Å. That route produces one Void
and no Mouth, consistent with the independent enclosure. The case extension
page links protocol/certificate/verification records and a reviewed standalone
plot. All earlier scientific files/notebooks retain their frozen bytes and
originally inconclusive weaker bounds; the new conclusion is linked explicitly.

The 100-check source selector, repository Ruff, scoped mypy and full HTML build
pass with no new warning; ten new downloads match their source bytes. Small
sequential one-CPU generation/verification changes no scientific kernel. This
resolves 0.2 Å origin enclosure only: exact global cavity/mouth counts, volume,
general path validity, #75/#76/#60 and installed/full-matrix gates remain open.
The maintainer's deeper three-case priority continues before any new geometry.
