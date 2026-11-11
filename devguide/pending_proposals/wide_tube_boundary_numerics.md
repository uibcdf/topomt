---
summary: Resolve wide-tube physical boundary ordering within the numerical margin.
issue: uibcdf/topomt#184
status: active
opened: 2026-11-10
closed:
severity: medium
verification: measured
area: [dfnd, validation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Wide-tube boundary numerical margin

## What

At source fdb253cf542e35d7d2b5414b7214677d0a884f24, the 77-ball
`straight_tube_wide_sparse` control at 2.5 Å reports unknown physical patches:
`face 12: critical-section ordering within numerical margin`. The independently
replayed full hull certificate proves two strict-free end patches. The identical
source resolves two patches at 1.4 Å; this is a profile-scoped availability
limitation, not an incorrect computed count.

## How

Retain the frozen input, query, independent certificates and original native
attempt in the case's `artifacts/straight_tube_wide_sparse_v1/`. The actual-public
physical target first failed at 2.5 Å; it remains a strict expected failure in
`tests/test_wide_tube_study.py`, with its passing 1.4 Å control retained.
Diagnose the named face and critical events without weakening the oracle.

## Why

One independently clear path and exactly two boundary patches are available,
but this profile cannot expose the complete physical boundary. The finite
numerical margin is part of its declared query, not permission to invent a count.

## What was refuted

This reason differs from the arrangement-budget exhaustion owned by #180.
The successful 1.4 Å result does not correct the narrower tube's #180 limitation.
Global boundary completeness does not establish every component's attachments:
at 1.4 Å only the Channel's two contacts resolve; ten other attempted
component/patch associations remain unknown. Wider path work remains #76.

## Scope and exclusions

Input SHA-256 77fc6f703dac08084e75398202169c9f8e05fc07e75eec4faf400932a3f2a855,
1.88 Å atomic radii, 2.5 Å probe, with_connectors/flag_only/dryface, zero physical
tolerances and epsilon/boundary margin 1e-6 Å. No scientific fix, original-engine
comparison, all-atom component-count or installed/platform qualification.

## Acceptance criteria

Provide a generic bounded, charged and recoverable treatment of the actual
critical-section ambiguity. Make the same-source physical targets pass without
retuning the frozen profile; verify prior controls and explicit unknown behavior.
Review the matching DFND book and reconcile card/hub/lifecycle/case/report before
closure. Do not count a strict expected failure as passing qualification.

## Repeated source receiving

The metadata-corrected new original execution at
3ad9515019e722c0ccf4ade7a3024de4166e217e reproduces the same physical states.
The first fdb253c attempt is preserved as `native_attempt_metadata_encoding.json`;
its bibliographic strings are not accepted as portable attribution. #185 corrects
new evidence serialization only; it changes no scientific DFND operator.
The maintained card is
https://github.com/uibcdf/topomt/discussions/154#discussioncomment-19535683.
