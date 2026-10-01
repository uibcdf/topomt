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

## First adopted reference and public notebook seed

The [notebook laboratory checkpoint](../DFND/notebook_laboratory_checkpoint.md)
records the active case-by-case route and the first frozen input/observation
artifacts under `docs/content/showcase/dfnd/`. The regular tetrahedron uses
independent circumradius and finite hull-volume formulas, three nonmarginal
probe anchors and a rigid-motion guard in
`tests/test_dfnd_regular_tetrahedron_reference.py`. Its notebook includes input
geometry, an 81-point probe sweep, quantity-aware input/report and an optional
original fpocket invocation. The observed dummy-PDB fpocket run fails at input
reading; it is explicitly a failure with no pocket count, not an oracle.

## Second control and review boundary

The closed-shell notebook independently certifies a probe-tight hull boundary
and a free origin at 1.4 Å. Native containment identifies its central sealed
resident component. Both controls now retain original fpocket, Pocketeer,
AlphaSpace2 and pyCASTA attempts, including successful evidence bundles and
explicit failures. Peer pocket/volume definitions remain separate from native
acceptance. The server-input audit and cached observations record CASTp 3.0
upload failures and two accepted CASTpFold jobs whose completion is unknown.
Notebook reruns do not resubmit. The user requested a pause after this two-case
tranche; no third case or kernel tuning is authorized by that stopping boundary.

This is partial progress. The reviewed opening/passage/neck panel,
independent solvent-volume reference and annotated molecular cases remain.
No DFND kernel changes were needed for these controls. #75 and #60 retain
their own unfinished numerical/public-model gates.
