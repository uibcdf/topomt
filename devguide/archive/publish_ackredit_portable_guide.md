---
summary: Publish the canonical Ackredit portable-attribution guide in TopoMT.
issue: uibcdf/topomt#91
status: resolved
opened: 2026-10-03
closed: 2026-10-03
severity: low
verification: inspected
area: [documentation, governance]
guard:
normative: MOLSYSSUITE_GUIDE.md#common-development-baseline
blocked_by: []
supersedes: []
---

# Publish the synchronized Ackredit portable-attribution guide

## What

Publish the consumer guide prepared through the suite's guarded canonical
guide synchronization. This resolves the documentation handoff in
[TopoMT #91](https://github.com/uibcdf/topomt/issues/91).

## How

Preserve the prepared `ACKREDIT_GUIDE.md` without editing its generated text.
Its SHA-256 is
`24615e3a8894c7cba67fc92fd0323369e725c3bd88096df9eda9311ab8890ff5`.
The canonical committed source is
[Ackredit 840aab3](https://github.com/uibcdf/ackredit/blob/840aab3d415312144e4f5754d5def11b3068832f/standards/ACKREDIT_GUIDE.md).

On 2026-10-03 the prepared copy equals the clean canonical source checkout
byte for byte. Its Git blob ID
`9317b21f0abbdc03f057e7ea993a8cd8394e7cbd` also equals the source file
returned by GitHub for Ackredit's remote `main`. TopoMT's Ruff configuration
already excludes the exact generated-guide path; no configuration change is
needed. Future prose changes remain owned by the canonical provider.

## Why

The guide documents the reviewed portable `Attribution`, `capture` and
`get_attribution` contract, contextual uses and detached bibliography semantics.
Consumers need the accepted guidance while preserving the separate provider
publication and runtime adoption gates.

## What was refuted

The local modification is a verified canonical synchronization, rather than an
unreviewed local fork. Delivering a guide does not establish runtime use or a
released dependency floor. The issue's handoff identifies the 0.9.0 candidate
as awaiting public artifact delivery; this change makes no release claim.

## Scope and exclusions

Generated guide delivery and its resolution record only. Scientific engines,
runtime imports, dependency requirements and CI workflows are unchanged.
Shared guide coordination remains under
[MolSysSuite #71](https://github.com/uibcdf/molsyssuite/issues/71).

## Acceptance criteria and resolution

The synchronized guide is published with the byte identity above and retains
its existing Ruff exclusion. This archived record and generated archive index
preserve the handoff. The normative requirement is the common development
baseline's rule that synchronized integration guides are generated, read-only
content with exact-path Ruff exclusions. Index validation and reporting tests
are run before committing; closure links the published commit and this record.
