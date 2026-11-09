---
summary: Certify the opened shell's connected probe-center boundary patch at 1.4 angstroms.
issue: uibcdf/topomt#149
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [dfnd, validation]
guard: tests/test_opening_connectivity_certificate.py::test_opening_has_one_connected_free_boundary_patch_with_an_origin_path
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

## Resolution

Protocol `7f6c0ff` fixes the unchanged input, 1.4 Å probe, strict-clearance
hull-boundary observable, numerical margins, budgets and primary mathematical
sources before formal certificate capture. The native/public outcome and
successful preflight were already known; this is retrospective characterization.
All 155 earlier scientific files retain their hashes. No DFND runtime,
classifier, public API, input model or scientific-kernel code changes.

The certificate covers exactly the other 127 hull faces with 193 subdivision
leaves. Their shared edges block the selected face's boundary. Minimum cover
margin is 0.007968988 Å. On parent-ID face [6,7,8], all 66 single-set decisions,
all 91 pairs among the 14 active sets and all 24 required triples have verified
point or convex-weight/separating-direction witnesses. Minimum decision margin
is 0.027267560 Å against the declared 1e-6 Å requirement. Optimizer convergence
is not accepted as evidence: every final witness is checked directly.

The convex intersection nerve has 14 vertices, 31 edges, 24 triangles, one
graph component and boundary-two rank 17 over F2, hence beta1=1. The
closed-convex nerve theorem and planar complement duality apply to the compact
planar covered union; with the blocked triangle boundary this establishes one
connected free patch inside it. Other hull faces are blocked, so it is also
the sole strict-clearance opening on the declared hull. The all-atom origin
ray crosses it at (0,4.770076949,0) Å with minimum clearance 1.819726044 Å.

Current actual public receiving gives a Pocket and one child Mouth on that
face, agreeing with the independently certified count/localization at 1.4 Å.
The original geometric triangle area and local gate are not thereby qualified
as free aperture area or all-atom bottleneck. Native graph paths, other probes
and cases, exact global cavity counts and intrinsic biological mouth semantics
retain their own scientific gates. The observer uses numerical safety margins,
not formal interval arithmetic. #76/#75/#60 remain open.

The versioned artifact set includes protocol, complete witnesses, independent
verification, actual native/public correspondence, source/resource receipt and
reviewed standalone figure. The new case page explains the proof and cites
the exact primary mathematical sources. Earlier notebook/report bytes and
weaker reference scopes remain intact; current navigation links the extension.

`devtools/verify_opening_connectivity.py` checks without TopoMT/DFND, a detector
or an optimizer. It reuses the explicit-unit triangle-cover checker extracted
from the closed-shell verifier, whose historical verification remains identical.
Tests check full inventories/partitions/rank, reject missing or false witnesses
and unsafe tolerances, and preserve results under unit policy, rigid motion
and source atom permutation. The current native/public Mouth is inspected too.
Receipts retain historical source hashes; current verification must reproduce
the mathematical result rather than freeze future verifier source evolution.

Validation: 114 selected current/prior-case, dispatch/query and reporting tests
pass on shared Python 3.14.10. Repository Ruff passes (554 formatted files),
focused mypy passes for three affected Python files, and full Sphinx HTML builds
with the same twelve existing warnings and no new warning. Six downloads,
the figure and current case navigation are byte-verified. Generation used
one CPU/numerical worker and 6 GiB process address-space ceiling, with a bounded
90-second CPU budget; measured process peak RSS was 92568 KiB. Verification/
receiving used bounded one-CPU execution; full HTML peak RSS was 279312 KiB.
These are execution receipts, not comparative performance measurements.

Required scientific evidence is versioned. Task-owned auxiliary search/plot
code, exploratory logs and rendered preview remain in ignored cache for review;
the redundant copied docs source can be removed after publication. Shared
environments/processes and the pre-existing human version-file edit remain
untouched. Full suite/matrix/installed qualification is deferred to its owning
gates; incremental commits carry the maintainer-requested [skip ci].

Continue boundary connectivity and compatible-path controls on the same three
systems, then the declared volume/uncertainty work. The tube and protein phase
remain deferred; this closes the one-input/probe reference extension only.
