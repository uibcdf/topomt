---
summary: Independently certify four tetrahedron boundary patches and contrast native grouping.
issue: uibcdf/topomt#150
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [dfnd, validation]
guard: tests/test_tetrahedron_boundary_certificate.py::test_four_disconnected_boundary_patches_all_reach_the_origin
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

## Resolution

Protocol `c85549f` fixes the unchanged tetrahedron and probes before formal
capture. Earlier outcomes/formulas were known; this is retrospective reference
characterization. All 161 earlier scientific files retain their hashes.

The six shared edges are covered with minimum margin 0.25 Å. On each face,
eight certified subset decisions yield a three-vertex/three-edge nerve with
beta1=1; minimum decision margin is 0.159956427 Å against 1e-6 Å. The complete
convex-intersection witnesses, closed-convex nerve theorem and planar complement
duality justify exactly one free patch inside each blocked face boundary. Thus
the whole hull has four disconnected strict-clearance patches. Four rays from
the free centroid through the face centroids continue to infinity with minimum
all-atom clearance 1.359956427 Å, connecting the four patches to the same region.
The sealed 1.4 Å control covers every face with margin 0.040043573 Å while the
centroid remains free; the 1.7 Å finite-hull exclusion margin is 0.154426091 Å.
These are sufficient bounds with floating-point safety margins, not formal
interval arithmetic or newly inferred exact transition thresholds.

Actual public receiving preserves one native exterior cluster containing all
four faces, zero native wall faces, native percolating and one Percolating
without Mouth children. The discrete face grouping does not measure physical
boundary-patch connectedness. Issue #151 and its separate open proposal own the
runtime/contract refinement; this reference delivery does not fix it or silently
rename the family. Calling this hull fully collision-free would overstate the
native predicate. Current case prose qualifies this interpretation while the
historical notebooks/results retain their bytes.

The quantity-aware witnesses, independent verification, current native/public
source correspondence, standalone reviewed figure and source/resource receipt
are versioned under regular_tetrahedron/artifacts/boundary_connectivity_v1/.
The maintained case page explains the proof and links primary mathematical
sources. The independent checker imports no TopoMT detector or optimizer. The
shell study's convex-intersection routine is now reusable with an explicit
length-unit boundary, preserving that shell's frozen verification exactly.
Tests reject missing faces/edges/subsets and false positive/negative witnesses,
exercise explicit nm/pm boundaries and unit policies, and preserve the result
under rigid motion with source permutation and equivalent-unit input/protocol
records. A strict float-equality check initially rejected converted probe values;
it now allows representation roundoff without widening the physical reference. Actual native/public receiving and
all earlier scientific hashes are guarded too.

Validation: 127 selected reference, three-case, dispatch/query, comparison and
reporting tests pass on shared Python 3.14.10 (11.31 seconds). Repository Ruff
passes (556 formatted files); focused mypy passes for the three affected Python
files. Full Sphinx HTML builds with the same twelve existing warnings, no new
warning; six download bytes, the figure and case navigation are verified.
Generation/receiving uses one CPU/numerical worker, 6 GiB process address-space
ceiling and 60-second CPU budget; peak RSS is 275836 KiB. Full HTML takes
0:08.63 wall time with peak RSS 278452 KiB under one CPU, 6 GiB and 120 CPU seconds.
These are bounded execution receipts, not comparative performance measurements.

No runtime scientific kernel, classifier, public API, provider or input-model
changes. The source fingerprint honestly includes the untouched pre-existing
human version-file edit. Required evidence is versioned; task-owned generator,
plot code, logs and HTML preview remain in ignored cache for review. Remove the
redundant copied docs source after publication. No shared processes/environments
are changed. Maintainer-authorized incremental commits use [skip ci]; full-suite,
Python/support-matrix and installed qualification are deferred to #16 and its
checkpoint recovery route. #75/#76/#60 remain open. Continue physical refinement
on these same three cases before any new geometry or proteins.
