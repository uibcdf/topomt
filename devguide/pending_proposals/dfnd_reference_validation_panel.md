---
summary: Reconcile DFND synthetic reference assumptions and freeze independent validation evidence.
issue: uibcdf/topomt#76
status: open
opened: 2026-10-01
closed:
severity: high
verification: inspected
area: [dfnd, validation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Independent DFND reference panel

## What

Classify the physical assumptions in the synthetic/pathological suite and freeze
a small independent validation panel before tuning segmentation or morphology.

## How

For each case retain coordinates, atom radii, probe/query, precision, expected
observables and reference method. Classify it as confirmed algorithm error,
model/input sensitivity, valid topology change, reporting question or unresolved
reference. Start with decisive closed/open controls, narrow passage and volume
cases; verify any real-system annotation before admitting it to a frozen panel.

## Why

The 2026-10-01 selector passes 312 tests with two skips at source
`7bd47faba6179a6e02444331e442acd251572564`, including tests preserving current
problematic behavior. Some stated ideal answers do not follow from the
atomic-ball model: changed density/radii can change physical topology; deleting
available graph nodes/edges can increase component count; a sampled shell is
not automatically an analytic continuum shell. An unsuccessful fixture search
is not a proof. See [the audit](../DFND/audit_topography_2026_10_01.md).

## What was refuted

A green pathological suite does not mean the method is scientifically correct.
These reference concerns also do not prove all observed fragmentation legitimate.
External fpocket/CASTp agreement cannot replace an independent reference when
the methods use different definitions.

## Scope and exclusions

A bounded reference inventory, independent checks and reproducible versioned
report. Retain existing measured history. Broad biological generalization,
publication-scale benchmarking and engine segmentation changes are subsequent
work; Topography context/support remains #60.

## Acceptance criteria

Freeze fixture models and numeric acceptance before tuning code. Publish a
structured reproducible report with independent expected answers, evidence and
explicit unresolved cases. Add meaningful test guards for adopted references.
Do not close on documentation alone or alter the kernel merely to match a peer.
