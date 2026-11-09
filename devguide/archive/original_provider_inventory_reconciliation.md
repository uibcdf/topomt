---
summary: Reconcile original-provider tooling and current packaged-resource declarations.
issue: uibcdf/topomt#169
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [packaging, third-party]
guard: devtools/tests/test_distribution_contract.py::TestDistributionContract::test_all_routes_source_roles_and_contexts_use_the_shared_preflight
normative: MOLSYSSUITE_GUIDE.md
blocked_by: []
supersedes: []
---

# Original-provider and runtime-resource inventory reconciliation

## What

The declared dependency-route check rejected the already committed optional
`original_local_env.yaml`. Its file and the route inventory were unchanged from
`b7f4e85`. The distribution guard also found omitted current original-provider
modules, argument adapters and synthetic assets. This surfaced during #157.

## How

Classify the opt-in compiler/SWIG/Java/source-build profile as `build-only` and
explain that it does not install TopoMT's runtime. Preserve the existing YAML
bytes and scientific pins. Reconcile the explicit package-resource inventory:
45 additions, including the three new attribution modules and 42 pre-existing
source/assets; no previous resource is removed. Update the existing preflight
expectation from 19 to 20 declared routes.

The missing-library control for original AlphaSpace2 previously passed `None`.
Current source admission correctly rejects that missing source before dependency
discovery. Use a non-None input sentinel to reach the deliberately failing
dependency boundary, preserving that admission contract.

## Why

Declared metadata and archive omission guards must cover current source. A
build-tool profile is not evidence of a solved/installed TopoMT runtime.

## What was refuted

Ackredit's new development-tool input did not introduce the unclassified
original-provider profile. This is owner inventory drift, not a shared SDK defect.
Changing scientific source pins or installing an environment is unnecessary.

## Scope and exclusions

Only declarations and stale administrative controls change. Real package builds,
installed receiving, complete scientific testing and public qualification remain
under #16. The synthetic payload used by distribution tests is an administrative
archive control, not a new deliverable.

## Acceptance criteria

The declared-route check and environment-generation check pass. The selected
distribution, environment-tool and dependency-contract modules pass: 32 tests,
5.47 seconds, one CPU. Three expected attribution diagnostics arose from controls
that deliberately force every optional dependency check to fail. Existing
resource omission tests remain active. Original engine/tooling inputs and
scientific assets retain their original bytes.
