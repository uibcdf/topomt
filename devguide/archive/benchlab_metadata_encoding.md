---
summary: Preserve bibliographic strings in quantity-aware study evidence.
issue: uibcdf/topomt#185
status: resolved
opened: 2026-11-10
closed: 2026-11-10
severity: medium
verification: measured
area: [validation, attribution]
guard: tests/test_benchlab_quantity_capture.py::test_capture_preserves_bibliography_strings_and_quantity_units
normative:
blocked_by: []
supersedes: []
---

# Study metadata encoding

## What

The study encoder asked PyUnitWizard whether arbitrary bibliographic strings
were quantities. Numeric-looking versions, pages and issue numbers could be
parsed as expressions and lose their original metadata identity.

## How

First reproduce with version `2.5.4`, pages `357-362`, issue `7825` and a real
1.88 Å quantity. Preserve JSON primitives before dimensional detection. Retain
the initial wide-tube attempt and recapture before treating saved attribution
as portable evidence. Earlier frozen study records remain historical bytes.

## Why

Faithful bibliographic metadata is needed to reproduce citations; scientific
DFND outputs and source geometry are separate from their serialization.

## What was refuted

Successful numerical receiving alone does not verify saved bibliography.
This does not establish that the underlying Ackredit calculation is incorrect.

## Scope and exclusions

The development evidence encoder, not public attribution or quantity kernels.
No rewriting of earlier frozen study files and no installed-release claim.

## Acceptance criteria

Round-trip plain metadata unchanged, preserve real dimensional quantities,
replay the new capture with faithful detached attribution and retain the failed
attempt. Add a durable serializer regression and run applicable checks.

## Resolution — 2026-11-10

Source 3ad9515019e722c0ccf4ade7a3024de4166e217e preserves JSON primitives before
quantity detection. The regression first failed, then passed. The wide original
attempt remains `native_attempt_metadata_encoding.json`; the new
`native_observations.json` captures the same scientific profiles with both
original-result and completed-operation attribution equality assertions before
serialization. Its NumPy version and paper pages also pass the saved-evidence
guard in `tests/test_wide_tube_study.py`. No earlier frozen evidence was rewritten.
This corrects new source captures only; historical misencoded metadata is not
retroactively accepted as portable saved-attribution evidence.
