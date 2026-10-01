---
summary: Audit radius-profile evidence across the archived corpus and expand analytical closed-void comparisons.
issue: uibcdf/topomt#82
status: resolved
opened: 2026-10-01
closed: 2026-10-01
severity: medium
verification: measured
area: [castp, geometry, validation]
guard: tests/methods/castp/test_castp_radius_audit.py::test_radius_audit_finds_unanticipated_oxygen_radius_without_label_filter
normative:
blocked_by: []
supersedes: []
---

# Radius coverage and expanded closed-void panel

## What

The four-system closed-void panel in #80 does not certify the full radius table
or exclude differences outside ASP/GLU. Audit all 89 existing archives and
expand the molecular membership/SA/MS comparisons in controlled batches.

## How

The provider-specific offline operation belongs to `devtools/castp` and reuses
the existing radius assignment helpers. Check both profiles against exported
orthospheres using the four-decimal rounding bounds, noncoplanar equal-power
contacts and the absence of interior protein atoms. Record per-label observed
atom identity, unobserved labels, conditional candidates and unresolved bulbs.
The 0.25 Å candidate search window is not a pass tolerance or a fitted radius.
Only a unique fourth candidate with three unchanged anchors is reported;
multiple changed anchors, ambiguous supports and excluded atoms remain limits.

## Why

The previous exploratory candidate search explicitly filtered for ASP/GLU.
The new independent small-geometry tests detect an arbitrary unanticipated
radius change without residue filtering and reject coplanar, interior and
ambiguous support. A matched total measure alone can hide compensating errors.

## What was refuted

Neither presence of a residue in a PDB nor a matching lining-atom set proves
its atomic-radius assignment. The server publishes ProtOr O1H0 = 1.42 Å,
while pinned geometric output supports a different assignment for four labels.
The authors' rationale and current live-server generality remain unknown.

## Scope and exclusions

Offline archived protein geometry and closed-void measures. No new server
submissions, fitted radii, default changes, DFND changes or migration of the
historical numeric table. Candidate associations are not certified server
atom IDs; unsupported residues and simultaneous unknown changes need more data.

## Acceptance criteria

Account for all 89 inputs with hashes and explicit coverage; retain reproducible
scientific guards; expand membership and four-measure checks beyond four PDBs;
record new discrepancies with owning follow-up issues. The checkpoint will
state what is confirmed, conditional, ambiguous or unobserved.

## Delivered outcome

All 89 archives and 59,080 bulbs are accounted for with hashes and explicit
label coverage. The twenty-system panel records nineteen passing systems
(136 closed voids and 544 measures) plus 1CGE's four matches and three missing
cavities. Compact radius and full per-measure artifacts are pinned under
`devguide/castp/artifacts/`; the maintained checkpoint is
`devguide/castp/checkpoint_2026_10_01_radius_coverage_and_void_panel.md`.
The comparator identity defect was reproduced and resolved in #83; unresolved
OXT inclusion/radii and 1CGE topology belong respectively to #84 and #85.
This closes the bounded audit delivery, not complete server equivalence.
