---
summary: Independently certify four tetrahedron boundary patches and contrast native grouping.
issue: uibcdf/topomt#150
status: active
opened: 2026-11-08
closed:
severity: medium
verification: inspected
area: [dfnd, validation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Four free patches on the fixed tetrahedron boundary

## What

Count strictly collision-free probe-center patches on the unchanged atomic-center
convex hull at 1.2 Å, with the unchanged 1.4/1.7 Å controls. Compare the physical
boundary observable with native whole-face clustering and actual public receiving.

## How

Freeze the protocol before formal capture. Reuse the convex-intersection checker:
on each face the three vertex sets make a three-edge cycle without its triangle.
All six shared edges are blocked. Four explicit all-atom rays connect the free
centroid through separate face interiors. Circumcover/enclosing-ball bounds
independently justify sealed and excluded controls. Reject incomplete or false
witnesses; check explicit units, rigid motion and source-ID permutation.

## Why

At 1.2 Å the expanded radius 2.9 Å exceeds half the edge (2.65 Å), but is below
the face circumradius (3.059956 Å). Existing DFND groups four admitted faces into
one link and reports Percolating with no Mouth children. These native outcomes
are known; the reference is retrospective characterization rather than blind
validation. A face cluster is not a physical connected-component count.

## What was refuted

Shared atomic edges do not establish a collision-free path for probe centers
between face interiors. A rendering does not prove connectivity. The present
native contract alone does not settle a physical mouth or family definition.

## Scope and exclusions

Same three systems/probes, no new geometry or provider requests. Preserve old
scientific bytes. No speculative clustering/classifier/API rewrite. Track any
required physical-refinement decision separately; #60/#75/#76 remain open.

## Acceptance criteria

Frozen protocol and independently checkable complete witnesses, unit/invariance
and damaged-certificate guards, actual raw/public correspondence, reviewed figure,
public explanation and bounded source/resource receipts. Keep any implementation
limitation open in its owning issue instead of equating documentation with a fix.
