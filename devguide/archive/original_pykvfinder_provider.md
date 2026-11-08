---
summary: Add source-bound original pyKVFinder execution and engine-independent recovery.
issue: uibcdf/topomt#136
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

# Original pyKVFinder provider

## What

Implement the original engine/files route under the accepted #135 batch, with
its own scientific record kind, original bytes and source-bound recovery.

## How

Use [the provider contract](../pykvfinder/overview.md) and the shared
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

The explicitly separate 0.9.6+uibcdf.2 compatibility source compiled on Python
3.14.10/NumPy 2.5.4 and passed 266 upstream/compatibility unit cases. The
tomlkit>=0.14 route passed floor/current controls; no future 0.16 execution is
claimed. Scientific kernels/defaults remain unchanged. The original workflow
returned 12 cavities on retained 1AKD input, and direct volume/area/residue
comparison, valid-empty handling and engine-free source-bound reconstruction
passed. Original evidence and checksums are committed; the durable guard always
reconstructs the captured fourth-provider result under both unit policies.
The designated live source gate separately executed both nonempty and empty
cases. This closes this bounded source integration, with installed/public
qualification and the support matrix retaining their separate owners.
