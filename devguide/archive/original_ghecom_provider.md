---
summary: Add source-bound original GHECOM execution and engine-independent recovery.
issue: uibcdf/topomt#137
status: resolved
opened: 2026-11-07
closed: 2026-11-07
severity: medium
verification: measured
area: [third-party]
guard: tests/test_new_provider_evidence.py::test_original_cli_evidence_reconstructs_without_engine
normative:
blocked_by: []
supersedes: []
---

# Original GHECOM provider

## What

Implement the original engine/files route under the accepted #135 batch, with
its own scientific record kind, original bytes and source-bound recovery.

## How

Use [the provider contract](../ghecom/overview.md) and the shared
[source checkpoint](../original_provider_expansion_checkpoint.md). Reuse
MolSysMT source/selection/frame/chemistry, registered argument/dependency/
diagnostic/unit tools and the existing immutable ProviderRun evidence.

## Why

Controlled comparison needs the original method and a faithful adapter.
Native DFND admission and independent scientific truth are separate.

## What was refuted

Do not treat available files as proof of completed detection, a missing engine
as an empty result, or original labels as source indices without a qualified
map. Geometry and measurements retain each original definition.

## Scope and exclusions

One reviewed local original protocol and captured-file recovery. No new native
reproduction, automatic remote submission, full descriptor parity, release or
platform/interpreter qualification. Preserve the remaining #19/#16/#58/#81 gates.

## Acceptance criteria

Original execute/save/recover passed on the frozen 1AKD input, with 41 morphological grid pockets. Complete original evidence and checksums are committed. The durable guard reconstructs those exact bytes without subprocesses under two unit policies and checks exposed fields against the original format. Additional argument, malformed/empty, source mismatch and failed-receipt controls live in the new-provider test modules. This resolves this bounded source integration; installed/public qualification remains deferred.
