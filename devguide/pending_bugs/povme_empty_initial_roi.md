---
summary: Review the original POVME empty-initial-region execution failure before comparative reuse.
issue: uibcdf/topomt#195
status: open
opened: 2026-11-11
closed:
severity: low
verification: measured
area: [third-party, api]
guard:
normative:
blocked_by: []
supersedes: []
---

# POVME empty initial point field

## What

Original modern-source POVME raises a zero-size minimum-reduction error when
all inclusion points are removed by exclusions before the frame calculation.
Original frame handling filters the error entry into an empty result mapping.
The TopoMT adapter rejects this as an execution failure, retains original
diagnostics/identity and awards no completed-provider citation. It does not
manufacture a successful zero-volume result. A separate control where atom
exclusion removes points later returns a valid evaluated zero.

Provider/fork follow-up: [uibcdf/POVME#1](https://github.com/uibcdf/POVME/issues/1).
Broader family/observable assessment remains [#159](https://github.com/uibcdf/topomt/issues/159).
The compatibility integration #193 does not resolve this finding.

## How

Exact observed profile: fork `0c55f591dea3156e1ca76a486cf1f71d56c3a192`, version
2.2.2+uibcdf.1, original scientific modules/serial methods unchanged from
`8a9f1973c25eb52e36e0d7b20183bf896cb66729`; pymolecule
`614a95a0b792f83fbee77e4c7eed7d5ce046dee1`. Python 3.14.10, NumPy 2.5.4,
SciPy 1.18.1, Pydantic 2.14.3, Loguru 0.7.3, no Ray, one worker.

Use `tests/data/original_local/pisa/input.pdb` (40 atoms, two synthetic chains),
an inclusion sphere of radius 1 Å and exclusion sphere of radius 4 Å, both at
[0,0,0], grid spacing 1 Å, cutoff 1.09 Å, hull disabled and default contiguous
criterion 4 with no seeds. The included domain is independently empty after
exclusion because the larger sphere covers it. Atomic radii do not enter the
failed early reduction. Original `points/hull.py:546` calls `np.min(pts, 0)`
with shape `(0,3)` and raises `ValueError`.

Retained original failed bundle:
`tests/data/original_local/povme/povme-failed.zip`, including source context,
submitted coordinates, configuration, empty original point field, CSV header,
diagnostics and attempted-engine identity. The explicit original failure gate
is `tests/test_specialist_original_execution.py::test_original_specialist_failures_never_become_empty_success`.
This guard protects adapter error semantics; it is not a provider correction.

## Why

Keep an execution/empty-input contract observation separate from a valid empty
volume, unsupported-input policy and geometric accuracy. A source-specific
operational failure cannot establish DFND superiority. The finding remains
`needs_review`, outside current manuscript claims, until applicability and the
provider's intended empty-input contract are assessed.

## What was refuted

Installing the provider, seeing exit zero or receiving an empty mapping is
insufficient evidence of a completed zero-volume calculation. Closing #193 or
changing packaging/Ray bootstrap is not a correction of scientific frame code.
No upstream Python 3.12 execution, Ray, historical POVME3, matched DFND comparison
or general algorithmic failure is established by this observation.

## Scope and exclusions

This issue owns consumer applicability review, evidence and comparative-record
reconciliation; the fork issue owns any proposed provider change. Preserve the
compatibility fork's unchanged scientific scope in the present delivery. A
future kernel fix requires separately reviewed scope and same-query evidence.
No external upstream issue/PR is authorized by this report. No new BenchLab
unit or molecular DFND characterization is selected.

## Acceptance criteria

Establish the intended empty initial-region domain and target source/runtime.
If corrected, require an explicit zero result or deliberate admission error,
a focused provider regression and same-query consumer receiving. Otherwise
record an accepted retained-domain decision and revisit trigger. Reconcile
the finding card, hub, lifecycle register, method summary and both owner issues;
archive only with the appropriate correction or retained-limit evidence.
