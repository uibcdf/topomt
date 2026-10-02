---
summary: Recalculate CASTp3 pocket and mouth membership after verified input preparation corrections.
issue: uibcdf/topomt#87
status: resolved
opened: 2026-10-01
closed: 2026-10-02
verification: measured
area: [castp, validation]
guard: tests/methods/castp/test_castp3_oracle_comparison.py::test_pinned_corrected_membership_panel_is_complete_and_source_identified
normative:
blocked_by: []
supersedes: []
---

# Corrected CASTp3 pocket and mouth membership audit

## What

Recalculate the historical 38-system feature sweep and the two additional
systems in the current 22-system closed-void panel (1A4J and 1CDO). The combined
forty-system panel uses the preparation corrected under #83, #84 and #85.

## How

Reuse the owning `devtools.castp.compare_castp3_oracles` comparison operation.
Persist exact source hashes, explicit `castp3_protor`, protein/peptide
selection, 1.4 angstrom probe, full depth and disabled diagnostic switches.
Compare PDB-serial atom-set multisets, retaining missing and extra memberships
and duplicate multiplicity. Treat exported aggregate mouth records separately
from individual topological mouths. Keep calculation errors and mismatches in
the requested-case denominator.

## Why

The historical sweep recorded many exact pockets, but its affected atom IDs
were mapped incorrectly for alternate-location inputs and it predates corrected
hydrogen/terminal preparation. Recent 22-system evidence covers closed-void
measurements only. Neither is a complete current open-pocket comparison.

## What was refuted

Equal feature counts do not establish equal atom sets. Coincident pocket or
mouth memberships do not establish independent SA/MS metric parity.

## Scope and exclusions

Current feature counts and exact lining/rim atom sets. No fitting of radii,
epsilon or local atom expansion, no new method semantics and no certification
of open-feature SA/MS quantities or exact mouth boundary topology.

## Acceptance criteria

Complete all forty cases or explicitly record every failed case. Persist the
source-identified comparison, aggregate coverage and all mismatches. Keep the
historical sweep intact with a dated correction. Add independently useful
audit-contract tests and permanent representative molecular regressions,
update maintained guidance and hand off residual mismatches to owning issues.

## Delivered

All forty calculations completed. Exact memberships match 468/534 pockets,
388/388 voids, 45/52 channels, 8/17 branched channels and 520/603 exported
aggregate mouth records. Duplicate multiplicity and every missing/extra set
are preserved in the source-identified artifact. The two previously problematic
micro-pockets (3PTB 27 and 1BMQ 34) now match their pocket and mouth sets.

The complete-artifact guard, six original molecular controls, two micro-pocket
guards and reusable contract tests provide 23 passing tests. The
`castp/checkpoint_2026_10_02_corrected_pocket_membership.md` checkpoint and its
linked per-PDB table document scope and results. Residual discrepancies are
handed off to #88; #41–#52 retain independent open-feature metric work. The
comparison is complete, while full modern-server parity remains unclaimed.
