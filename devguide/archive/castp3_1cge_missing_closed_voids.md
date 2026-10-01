---
summary: Resolve three missing native closed cavities in the pinned 1CGE CASTpFold output.
issue: uibcdf/topomt#85
status: resolved
opened: 2026-10-01
closed: 2026-10-01
severity: medium
verification: reproduced
area: [castp, geometry, validation]
guard: tests/methods/castp/test_castp_void_measurement_audit.py::test_pinned_1cge_voids_match_all_memberships_and_measures
normative:
blocked_by: []
supersedes: []
---

# Missing closed cavities in 1CGE

## What

With the exact archived PDB, protein/peptide selection, `castp3_protor`,
1.4 Å probe and base alpha rank, native analysis initially produced four closed voids
against seven archived cavities. Four exact lining-atom sets and all sixteen
associated SA/MS quantities agree; three sets remain absent.

## How

The original reproduction used `python -m devtools.castp.audit_castp3_void_measurements
--ids 1cge --output /tmp/1cge.json` and returned failure. Investigation found
273 explicit protein hydrogens assigned the 1.8 Å heavy-atom fallback radius.
ProtOr already represents attached hydrogens implicitly. Both geometry cores
now obtain hydrogen indices with `molsysmt.select(atom_type == "H")` and omit
them from the selected working geometry, retaining original atom indices and
requested order. Explicit sphere overrides and classical parameter routes
retain their selected atoms. This operation precedes geometric construction.

## Why

The full parity denominator must include all seven cavities. Missing serial
sets are `[776, 876, 878, 881, 898, 900, 1144]`,
`[72, 133, 471, 1190, 1510]` and `[163, 190, 311, 340, 513]`.
All are protein heavy atoms. All 231 archived 1CGE bulbs are compatible under
the current radius audit, which does not establish component topology.

## What was refuted

The original residual survived the corrected serial mapping in #83. Its cause
was input preparation, rather than faulty alpha-rank connectivity or a fitted
radius discrepancy. Omitting explicit H recovers all seven exact memberships
and all 28 SA/MS values at the unchanged output-rounding allowance. No epsilon,
coordinate, probe or heavy-atom radius fit was needed.

## Scope and exclusions

Pinned 1CGE closed-void parity and ProtOr united-atom preparation. Open pockets
and mouths remain separate themes. The former known-discrepancy guard is
replaced with an actual seven-void/twenty-eight-measure parity assertion.

## Acceptance criteria

Recover all seven exact archived memberships and all twenty-eight independent
SA/MS measurements; replace the known-discrepancy guard with passing parity
tests when the cause and general correction are demonstrated. These conditions
are met by the molecular guard and small independent geometry tests for both
ProtOr cores, explicit overrides, classical radii and reordered selections.
