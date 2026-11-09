---
summary: Register explicit DFND radius-model validation at the public dispatcher.
issue: uibcdf/topomt#171
status: open
opened: 2026-11-09
closed:
severity: low
verification: reproduced
area: [api, dfnd]
guard:
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
