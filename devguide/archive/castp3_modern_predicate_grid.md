---
summary: Align modern CASTp3 exact predicates and event ranks with its decimal weighted input geometry.
issue: uibcdf/topomt#89
status: resolved
opened: 2026-10-02
closed: 2026-10-02
severity: medium
verification: measured
area: [castp]
guard: tests/methods/castp/test_castp3_modern_predicates.py::test_modern_exact_order_preserves_thin_neighbor_power_order
normative:
blocked_by: []
supersedes: []
---

# Modern CASTp3 predicate grid

## What

The modern route triangulated decimal PDB coordinates but materialized its exact
predicates and event spectrum with the classical decimal-to-double-to-floor
conversion. Tiny changes on that grid reversed neighboring power radii in 1CDO,
creating a false finite flow sink and joining a channel to a branched channel.
This is a local reconstruction defect, not evidence of a CASTp server defect.

## How

A five-atom witness uses serials 3156, 4800, 4807, 4976 and 3232. Decimal inputs
give neighboring squared power radii 19.917802154 and 19.920704398 angstrom
squared; historical truncation gives 19.917831744 and 19.915468534. The thin
neighbor amplifies the grid discrepancy. The independent failing-first guard
checks the mathematical ordering without oracle memberships or fitted epsilon.

Modern exact predicates now use nearest-grid Python integers at five decimal
places throughout. The classical implementation retains historical conversion.
This correction is shared by both explicit pocket definitions in #88. General
higher-precision trajectory inputs retain the finite-grid precision boundary;
this PDB result does not certify every possible input resolution.

## Why

Incorrect event ordering changes the hidden-face graph and pocket decomposition.
The modern implementation also requires actual Python integers for exact Bareiss
arithmetic: floating objects in an object array are insufficient.

## What was refuted

The 1CDO defect is not missing input atoms, radius assignment, an absent regular
facet or a need for a molecule-specific radius cutoff. Both neighboring weighted
spheres are empty under the original input.

## Scope and exclusions

Modern numeric materialization only. Pocket-definition choice and geometric
mouth reporting belong to #88. Input heterogen inclusion is separate. No DFND or
Topography semantic change; Python 3.11/3.12 CI work remains deferred.

## Acceptance criteria

Protect independent thin-neighbor ordering and integer materialization. Recover
separate 1CDO channel and branched-channel memberships under the CASTp3
compatibility definition. Re-evaluate the forty-system membership panel and
preserve all 225 closed-void memberships and 900 analytical SA/MS values within
printed server precision. Retain classical fixed-point behavior.

## Outcome

The independent ordering regression passes with nearest-grid Python integers.
The new molecular guard recovers every 1CDO atom class, including three channels
and three branched channels. A complete fresh forty-input production panel has
39 exact systems, with only the separately identified 1HIV heterogen-input
boundary remaining. All 388 closed-void sets match that panel. The separate
968-test run passes, preserving all 225 closed-void memberships and all 900
analytical SA/MS quantities within absolute printed precision. Full evidence
and source/input identities are in the
[definition checkpoint](../castp/checkpoint_2026_10_02_pocket_definitions.md).
Classical materialization is unchanged. This closes the local numerical defect;
it does not certify open metrics, arbitrary input precision or server internals.
