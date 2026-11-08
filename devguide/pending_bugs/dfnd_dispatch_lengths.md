---
summary: Register the three missing native length digesters in the public dispatcher.
issue: uibcdf/topomt#147
status: active
opened: 2026-11-08
closed:
severity: medium
verification: reproduced
area: [dfnd, api]
guard:
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
