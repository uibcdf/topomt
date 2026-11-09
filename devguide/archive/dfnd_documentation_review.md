---
summary: Strengthen the DFND method book after a reader and source audit.
issue: uibcdf/topomt#172
status: resolved
opened: 2026-11-09
closed: 2026-11-09
severity: medium
verification: measured
area: [documentation, dfnd]
guard: tests/test_dfnd_documentation.py::test_documented_public_inspection_and_query_blocks_execute
normative:
blocked_by: []
supersedes: []
---

# DFND documentation: post-delivery review

## Delivered outcome — 2026-11-09

The public book retains its 21 pages and now includes explicit carrier/Voronoi/
power definitions, an abstract multi-cell decomposition figure, reproducible
morphology/PCA/funnel/confidence definitions and fallbacks, corrected gate-policy
predicates, the Monte Carlo estimate/error formula, six answered reading checks,
a shorter reading route and the corrected download-directory workflow.

The durable inline-reader guard now recovers the single-cell Void's unavailable
mouth/occlusion/elongation/funnel descriptors. It failed first with a missing
`metrics` observation, then all four example tests passed. The full focused
panel gives **66 passed, 7 xfailed** (pre-existing #151 missing physical views),
10.64 s test time / 12.93 s process wall time, peak RSS 313.0 MiB. Native/public
receiving and independent certificates for all three cases pass; historical
scientific artifacts retain their bytes.

Fresh one-worker Sphinx: exit 0, 10.07 s, peak RSS 275.1 MiB, 21 pages,
1,872 valid local links/assets/anchors, zero DFND warnings. The same eleven
whole-site warnings remain owned by #64. The built downloadable script works
from the documented directory layout, all four SVGs reproduce byte-for-byte,
and the new graph figure was visually inspected. Affected Ruff/format/mypy
checks pass. The [checkpoint](../DFND/documentation_checkpoint.md) retains
source scope, resource controls and receipts in
`.cache/dfnd-documentation-review/`.

No scientific kernel/policy/finding status or dependency changed. Existing
scientific owners retain their scope; this is source documentation qualification,
not a physical algorithm correction, installed release or live deployment.

## What

The first method book was delivered under #170 at `91c7f21`. A subsequent
reader/source audit finds that its broad coverage needs clearer foundations,
more explicit descriptor definitions and a multi-cell explanation. This issue
owns the bounded refinement; the original delivery remains completed history.

## How

Review every chapter against its source/evidence map. Explain Delaunay/Voronoi
and power versus clearance fields; add a clearly abstract graph illustration;
specify morphology/depth/funnel formulas, fallbacks and interpretation; answer
reading checks and make the download workflow unambiguous. Exercise executable
examples and validate rendered navigation with bounded resources.

## Why

A single-cell tetrahedron cannot illustrate removal of a common exterior root,
connectors or several resident regions. A named descriptor without its formula
and availability rule cannot be reconstructed. The initial download prose also
puts all files together while its command assumes a separate input directory.

## What was refuted

The book already covers dry banks, interfaces, hierarchy, scale/time, numerical
scope and public provenance. A second book or a new BenchLab geometry would
duplicate existing material. Clarifying descriptors does not solve the existing
physical-boundary, path or volume questions.

## Scope and exclusions

Documentation, its figure generator and executable-reader guards only. Preserve
scientific code, catalog thresholds, current finding scope and all historical
case artifacts. No new protein characterization or comparative claims.

## Acceptance criteria

The reader can explain the carrier, follow finite decomposition, reconstruct
documented morphology and distinguish unavailable measures from zero. The
downloadable example and inline blocks execute; all section links/anchors render
without new warnings; existing report/comparative checks pass. Record measured
checks in the documentation checkpoint and archive this report on completion.
