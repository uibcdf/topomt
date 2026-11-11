---
summary: Register explicit DFND radius-model validation at the public dispatcher.
issue: uibcdf/topomt#171
status: resolved
opened: 2026-11-09
closed: 2026-11-11
severity: low
verification: reproduced
area: [api, dfnd]
guard: tests/test_dfnd_dispatch_lengths.py::test_explicit_dfnd_radii_model_has_a_digester_and_preserves_geometry
normative:
blocked_by: []
supersedes: []
---

# Explicit radius-model keyword emits a missing-digester warning

## What

The public `get_topography(..., method='dfnd', radii_model='vdw')` route emits
`DigestNotDigestedWarning`, although the analysis completes and the inner
`DFNDMeshConfig` validates the radius-model name.

## How

Observed while executing #170's frozen four-atom documentation example at source
`a5a81deee74b97301b88425cee122e3f1f3e28d8`, at probes 1.2/1.4/1.7 Å under nm
and pm policies. Removing only the explicit default keyword removes the warning;
the example checks the actual retained `vdw` model and received radii. No
scientific radius-default change was made.

A separate single-call replay at 1.4 Å retained the warning and successful
completion in `.cache/dfnd-documentation/radii_model_dispatch.json`. This is the
retained diagnostic receipt; the example's later green log has no warning.

## Why

An explicit supported model should have consistent validation and diagnostics
at the dispatcher. A missing adapter warning makes a correct documented call
look incompletely validated.

## What was refuted

This is not evidence of wrong radius assignment or a failed scientific engine.
The example initially also indexed a set returned by `get_features`; that
example error was corrected independently and is not the cause of the warning.

## Scope and exclusions

The earlier #147 length-digester correction has a separate, closed scope. #171
owns this keyword follow-up; #170 can deliver the method documentation without
changing the scientific core or dispatcher in the same patch.

## Acceptance criteria

Test the explicit valid/invalid keyword first, register/reuse its adapter,
preserve inner configuration validation, and verify argument-specific diagnostics
without a spurious missing-digester warning. Run existing length/query guards.

## Resolution — 2026-11-11

Register `digest_radii_model` through the existing ArgDigest discovery route.
For the selected DFND route, accept exactly `vdw`, `protor` and `provided`,
matching the unchanged inner
`DFNDMeshConfig` name contract; other values produce the argument-specific
SMonitor `ArgumentError`, including unhashable containers. This does not extend
the scientific input routes supported by any individual model.

The regression selection first fails 11 cases: two valid explicit nm/pm calls
emit the missing-adapter warning, three supported-name adapter imports are
absent, and six invalid values escape the expected public diagnostic. After
registration, **37 tests pass** across dispatch, input policy and the executable
method-book example. They preserve received atom radii and the tetrahedron's
1.4 Å public Void under nm/ps and pm/fs. The maintained example now explicitly
selects `vdw` instead of avoiding the warning by omitting the keyword.

Final cross-route review adds 15 controls and scopes validation through the
digested method/engine arguments, including the dispatcher's engine override.
The first context controls expose six rejected CASTp calls and three missing
adapter dependency parameters. After correction, the **52-test** dispatch,
input-policy and method-book selection passes. CASTp's distinct model names
remain forwarded to their existing owner; these admission-only controls do not
claim CASTp execution. Invalid DFND names are rejected through canonical,
case-normalized and legacy/overriding engine selectors.

Only the public admission/diagnostic gap is resolved. Defaults, numerical core,
inner validation, frozen BenchLab notebooks and downloads retain their prior
bytes. Shared-source verification and remaining qualification boundaries are
recorded in [the batch receipt](../evidence/api_maintenance_2026_11_11.json).
