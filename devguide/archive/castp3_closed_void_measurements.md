---
summary: Validate and expose local CASTp3 closed-void SA/MS measurements.
issue: uibcdf/topomt#79
status: resolved
opened: 2026-10-01
closed: 2026-10-01
severity: medium
verification: measured
area: [castp, geometry, units]
guard: tests/methods/castp/test_castp_modern_void_measurements.py::test_native_void_metrics_reach_topography_with_units
normative:
blocked_by: []
supersedes: []
---

# Local CASTp3 closed-void measurements

## What

Local CASTp3 closed voids now expose independent solvent-accessible and
molecular-surface area and volume in existing Topography attributes. All four
2PK4 closed cavities match pinned modern-server atom membership and sixteen
analytical measures within three-decimal output rounding.

## How

Reuse the Python VOLBL closed-component construction at the base alpha rank,
match measurements by simplex support, and transfer record Å²/Å³ values to
explicit nm²/nm³ quantities. Runtime calculation does not read the test oracle.
Tests compare pinned CASTp3/Fold geometric files in four systems and independently
calculate 2PK4 voids. Consumer-policy conversion is checked in a subprocess.

Correct requested-rank component construction in both CAST cores. Classical
radius-table and explicit-radius routes no longer request unused bond metadata;
ProtOr still propagates connectivity failures.

## Why

Historical source and papers are algorithmic references; archived modern
server outputs are the result oracle. Generic polyhedral feature area/volume
could not supply the four distinct SA/MS definitions. This bounded positive
comparison establishes a first measurable modern reconstruction milestone.

## What was refuted

Successful feature membership or global VOLBL totals alone cannot establish
modern per-feature SA/MS parity. A fragile historical binary is not the modern
oracle. Classical geometry does not require chemical bonds when its radii come
from a table or an explicit override. No geometric epsilon fitting was needed
for the sixteen validated measures.

## Scope and exclusions

Only closed voids at the base alpha rank gain analytical fields. Generic
polyhedral fields retain their meanings. Open pockets, mouths, cusp correction,
altered-alpha measurement contexts and general CASTp3 equivalence remain open
under #41–#52. Original result routes, DFND semantics and public feature classes
are unchanged. MolSysMT's independent zero-bond defect remains under
`uibcdf/molsysmt#283`.

## Acceptance criteria

Exact 2PK4 void lining atoms and sixteen SA/MS values, modern archive agreement
on the four pinned cases, unit-bearing Topography delivery, preservation of
consumer unit policy, requested-rank consistency and radii-specific metadata
requirements are protected by the two new CAST regression modules.
The [checkpoint](../castp/checkpoint_2026_10_01_modern_void_measurements.md)
records inputs, tolerances, limits and follow-up order.
