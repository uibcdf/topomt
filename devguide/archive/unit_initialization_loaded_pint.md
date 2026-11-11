---
summary: Preserve an existing Pint registry when initializing TopoMT's unit policy.
issue: uibcdf/topomt#174
status: resolved
opened: 2026-11-10
closed: 2026-11-11
severity: low
verification: reproduced
area: [units, api]
guard: tests/test_unit_initialization.py::test_import_preserves_unit_registry_and_policy
normative:
blocked_by: []
supersedes: []
---

# Importing after Pint use without an active policy

## What

TopoMT configures Pint's cache when no standard-unit policy is active, even if
the backend has already constructed its registry. PyUnitWizard warns that this
late configuration is ineffective. OpenCASTp reported the observation in #174;
the warning did not establish a numerical failure.

## How

Construct a Pint quantity with PyUnitWizard before importing TopoMT, without
calling `set_standard_units`. Import TopoMT and capture the late-cache warning.
Fresh-process controls must also cover no prior use and active application/suite
policies. Use supported `configure.get_libraries_loaded()` to inspect backend
state; do not inspect private kernel state or suppress the warning.

## Why

Policy authority and backend initialization are distinct. A library may declare
the baseline when no policy exists, while preserving an already constructed
registry and its cache choice.

## What was refuted

The originating successful numerical qualification does not imply that the
import-order warning is harmless configuration. Rebuilding the registry or
silencing warnings would not satisfy the preservation contract.

## Scope and exclusions

TopoMT's import configuration only; no unit baseline, numerical method,
PyUnitWizard implementation or sibling configuration changes. Shared guide
examples retain their owning provider's separate maintenance route.

## Acceptance criteria

Fresh imports retain early cache setup. Previously loaded Pint avoids the late
setter and retains its registry/cache. Active user/suite policies and all three
TopoMT fast tracks remain valid, including under pm/fs standards.

## Resolution — 2026-11-11

Within the existing no-active-policy branch, consult the supported
`configure.get_libraries_loaded()` and request Pint caching only if Pint is
unloaded. The baseline declaration and unconditional fast-track registration
retain their original boundaries. No warning filtering, registry replacement,
policy reset, dependency addition or provider edit is introduced.

Four independent real-process imports cover fresh, previously used/no-policy,
application pm/fs/degrees and existing suite nm/ps/radians sessions. Initially
only the loaded/no-policy case fails, reproducing the exact warning. All four
pass after the guard. They check the loaded registry's bound quantity class,
cache setting, conversions of pre-import quantities, policy/provenance and all
three fast tracks. Fresh imports still select the early cache.

Read-only provider consultation used clean PyUnitWizard source
`c81916e65ce61e905008e8931af3c0e527157251`. The canonical-guide example's separate
maintenance already has owner
[PyUnitWizard #144](https://github.com/uibcdf/pyunitwizard/issues/144); no duplicate
provider issue or local edit to its synchronized guide is needed. This is
TopoMT source receiving, not public provider/release qualification. See
[the batch receipt](../evidence/api_maintenance_2026_11_11.json).
