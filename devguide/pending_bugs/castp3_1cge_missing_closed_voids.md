---
summary: Resolve three missing native closed cavities in the pinned 1CGE CASTpFold output.
issue: uibcdf/topomt#85
status: open
opened: 2026-10-01
closed:
severity: medium
verification: reproduced
area: [castp, geometry, validation]
guard: tests/methods/castp/test_castp_void_measurement_audit.py::test_pinned_1cge_audit_retains_missing_voids_in_parity_denominator
normative:
blocked_by: []
supersedes: []
---

# Missing closed cavities in 1CGE

## What

With the exact archived PDB, protein/peptide selection, `castp3_protor`,
1.4 Å probe and base alpha rank, native analysis produces four closed voids
against seven archived cavities. Four exact lining-atom sets and all sixteen
associated SA/MS quantities agree; three sets remain absent.

## How

Run `python -m devtools.castp.audit_castp3_void_measurements --ids 1cge
--output /tmp/1cge.json`. The operation preserves the missing sets and exits
nonzero. The pinned twenty-system report records hashes and all comparisons.
Investigate archived orthospheres and base-rank connectivity without fitting
per-PDB epsilon parameters or relaxing the pass tolerance.

## Why

The full parity denominator must include all seven cavities. Missing serial
sets are `[776, 876, 878, 881, 898, 900, 1144]`,
`[72, 133, 471, 1190, 1510]` and `[163, 190, 311, 340, 513]`.
All are protein heavy atoms. All 231 archived 1CGE bulbs are compatible under
the current radius audit, which does not establish component topology.

## What was refuted

This residual survives the corrected serial mapping in #83. The sixteen
matched measures are correct; their agreement does not recover the missing
cavities or their unmeasured quantities. The cause is not yet established.

## Scope and exclusions

Pinned 1CGE closed-void topology and subsequent measurements. Open pockets and
mouths remain separate themes. The diagnostic guard preserves honest failure
reporting; it does not certify recovered native parity.

## Acceptance criteria

Recover all seven exact archived memberships and all twenty-eight independent
SA/MS measurements; replace the known-discrepancy guard with passing parity
tests when the cause and general correction are demonstrated.
