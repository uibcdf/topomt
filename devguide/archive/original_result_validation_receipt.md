---
summary: Rejected original-provider results retained a completed receipt.
issue: uibcdf/topomt#142
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: reproduced
area: [third-party]
guard: tests/test_new_provider_workflows.py::test_rejected_original_result_keeps_failed_receipt_and_auxiliary_input
normative:
blocked_by: []
supersedes: []
---

# Invalid original-result receipts

## What

Original-local orchestration captured a completed run before parsing. If parsing
rejected its files, the raised ProviderExecutionError attached that completed
receipt. The public operation correctly failed, but its retained status misled
inspection. Observed in the #141 pyKVFinder and CAVER tetrahedron controls.

## How

Reproduce with analytical missing-result bytes across all four existing local
provider workflow fixtures. Retain source context, original stdout, auxiliary
inputs and return code, but capture failed status and result_validation stage.
The initial four regression cases failed on completed versus failed status.

## Why

Process termination alone does not qualify an original scientific output. Failed
bundles must remain inspectable and must not enter engine-free success recovery.

## What was refuted

The adapter did not accept the invalid geometry as zero results. This is a
receipt-state defect; neither weakening parsers nor changing scientific kernels
would address it. Historical bundles remain unchanged.

## Scope and exclusions

Shared original-local result-validation failure path only. Upstream detector
limitations and the comparison notebook remain #141. This does not qualify the
full suite, installed packages or additional Python/platform combinations.

## Acceptance criteria

Tests retain original inputs/artifacts and return code, distinguish failure stage
and refuse saved success recovery. Applicable parser/workflow checks pass.

## Resolution

Re-capture the same original files with failed status and explicit validation
stage after a parse rejection. Existing valid-result captures are unchanged.
The relevant workflow, original-evidence, parser, MOLE and case-protocol
selection passed 73 tests on shared Python 3.14.10 in 11.00 seconds. The initial
four failing regressions now pass. Ruff and focused type checking cover the
modified source/tests; full matrix and installed-package evidence remain #16,
#19 and #81, while #141 owns the resulting study and rendered documentation.
