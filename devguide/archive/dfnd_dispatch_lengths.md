---
summary: Register the three missing native length digesters in the public dispatcher.
issue: uibcdf/topomt#147
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: reproduced
area: [dfnd, api]
guard: tests/test_dfnd_dispatch_lengths.py::test_explicit_dfnd_lengths_have_digesters_and_preserve_the_probe_model
normative:
blocked_by: []
supersedes: []
---

# DFND lengths at the public dispatcher

## What

Explicit `epsilon`, `residence_tolerance` and `permeability_tolerance` produce
missing-digester warnings in `get_topography(method='dfnd')`. Invalid list
values escape to PyUnitWizard and lose the argument name in their diagnostic.

## How

The initial #146 receiving run produces 72 warnings, 24 for each missing
argument. `tests/test_dfnd_dispatch_lengths.py` first fails five cases: two
non-default-unit valid calls emit missing-digester warnings, and three vector
inputs fail with a generic unsupported-form diagnostic rather than their
native argument names.

## Why

The public route should validate its explicit options without warnings about
missing library contracts. Native downstream validation protects the geometry,
but it does not provide complete public admission/diagnostics.

## What was refuted

This is not evidence of wrong geometry or feature classification. Do not
suppress warnings or use `skip_digestion` to make the receiving audit pass.

## Scope and exclusions

Three ArgDigest value adapters and one shared native length admission helper.
Keep finite nonnegative lengths, explicit PyUnitWizard conversions and legacy
bare-number angstrom conversion/deprecation. No kernel, default, tolerance,
dependency, provider contract or scientific interpretation change.

## Acceptance criteria

Actual public calls under nm/ps and pm/fs policies have registered digesters;
valid scalar/quantity and zero inputs retain their meaning. Invalid vectors,
negative/nonfinite values and wrong-dimensional quantities identify the right
argument. Bare-number warnings/conversion remain observable. Existing three-case
raw/catalog/registry results stay unchanged.

## Resolution

Register three argument modules through existing ArgDigest package discovery.
A shared native length adapter checks finite nonnegative scalars, explicit
quantity dimension/conversion and argument-specific errors. Bare numbers retain
their angstrom interpretation and native deprecation; zero remains valid.
No warning suppression, digestion bypass, dependency change, default change or
scientific-kernel change is introduced.

Fifteen focused guards cover explicit lengths under nm/ps and pm/fs, invalid
vectors/negative/nonfinite values, wrong dimensions and legacy conversion plus
deprecation. All pass. Actual public receiving of all three cases passes
without missing-digester warnings. The 100-check source selector, repository
Ruff, scoped mypy and full HTML build pass as recorded under #146. Broader
support-library and installed/matrix gates retain their owners; only the
reproduced native admission/diagnostic defect is resolved here.
