---
summary: Identify an explicit modern CASTp radius profile and resolve two closed-void residuals.
issue: uibcdf/topomt#80
status: resolved
opened: 2026-10-01
closed: 2026-10-01
severity: medium
verification: measured
area: [castp, geometry, validation]
guard: tests/methods/castp/test_castp_modern_void_measurements.py::test_castp3_profile_reproduces_pinned_1hew_void_bulbs
normative:
blocked_by: []
supersedes: []
---

# Closed-void residuals and modern radius profile

## What

Standard ProtOr matched thirteen void atom sets but only forty-four of fifty-two
SA/MS values in the four-system panel. 1IFB cavity 1 and 1HEW cavity 7 each
differed in all four analytical quantities. An explicit `castp3_protor` profile
now reproduces all fifty-two values and all thirteen atom sets.

## How

Independently exported bulb geometry identifies 1.40 Å for ASP/GLU carboxylate
oxygens. The new provider-specific profile reuses standard ProtOr assignments
and overrides only ASP OD1/OD2 and GLU OE1/OE2. Standard `protor` remains
available with its original values. Radius-array precedence and connectivity
error semantics are preserved.

## Why

The initial eight failing scalar regressions establish the residuals. Two
affected 1HEW bulbs independently identify the different atomic radius; a
multi-archive exploratory scan corroborates all four labels. A permanent guard
solves weighted-center equations independently and reproduces six server bulbs.
The corrected molecular comparison supplies the independent SA/MS verification.

## What was refuted

Matching lining atoms alone did not establish matching input balls or measures.
The small-cavity numerical area probe agrees with the original local result for
its old sphere model. A universal change to standard ProtOr, a larger output
tolerance, a geometric epsilon fit or an analytical formula correction was not
needed to resolve these two cases.

## Scope and exclusions

This closes the two measured residuals using an explicitly selected empirical
server profile. Unverified protonation variants, the wider molecular panel,
open-pocket/mouth metrics and general modern parity remain open. Original
provider routes, default radius policy, standard ProtOr and DFND are preserved.

## Acceptance criteria

The four-system molecular panel, independent 1HEW bulb equations, separate
standard/server profiles, explicit-radius precedence and connectivity-failure
guards pass. The [checkpoint](../castp/checkpoint_2026_10_01_castp3_radius_profile.md)
records the inference, exact inputs, numerical allowances and broader limits.
