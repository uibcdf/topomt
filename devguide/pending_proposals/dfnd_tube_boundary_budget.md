---
summary: Resolve bounded physical boundary receiving on the frozen straight tube.
issue: uibcdf/topomt#180
status: active
opened: 2026-11-10
closed:
severity: medium
verification: measured
area: [dfnd, validation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Straight-tube physical boundary budget

## What

At source b07a20e the three #178 native controls report an unresolved physical
hull, with unknown patch count: face 17 exhausts the arrangement work budget.
The same full-precision 81-ball input independently has two strict free hull
patches at 1.2 and 1.4 Å. At 2.5 Å the entire finite hull is covered.

## How

Preserve `straight_tube_narrow_dense/artifacts/straight_tube_narrow_dense_v1/native_observations.json` and
the separate wall/end certificates and receipts. The actual-public two-end
targets in `tests/test_tube_study.py` first failed; they remain strict expected
failures with this owner. They are pending scientific targets, not passing
qualification. A bounded positive-cover attempt before the expensive circle
arrangement is a candidate generic improvement; it is not implemented here.
The independent wall-first checker proves a complete convex-ball subdivision
cover on all 32 lateral carrier triangles and resolves the 14 end triangles.

## Why

A truthful unknown is preferable to a fabricated zero, but this small finite
tube is useful receiving scope. A complete cover can avoid arrangements whose
free set is empty. Charge all work, retain recoverable certificates and fall
back without treating an incomplete cover search as proof of an opening.

## What was refuted

The earlier #151 source correction remains resolved on its five selected
controls. It did not qualify arbitrary many-cell hulls. Raising every budget or
accepting a face-cluster count would not establish the missing physical result.

## Scope and exclusions

One newly selected fixed tube and its public physical receiving. No change to
native link grouping, local capacity definitions, public catalog promotion,
biological validation or installed-release qualification. #181 owns the
separate high-probe candidate/free-set discrepancy; #76 retains wider paths.

## Acceptance criteria

Make the same two-end targets pass through a generic bounded implementation;
qualify the independently excluded control; preserve explicit unknown results
outside proved scope. Run prior physical controls, certificate/support and unit
guards, measure resources and review the matching DFND book chapter. Reconcile
the comparative card, hub, register, current case and report before closure.
