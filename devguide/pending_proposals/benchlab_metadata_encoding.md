---
summary: Preserve bibliographic strings in quantity-aware study evidence.
issue: uibcdf/topomt#185
status: active
opened: 2026-11-10
closed:
severity: medium
verification: measured
area: [validation, attribution]
guard:
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
