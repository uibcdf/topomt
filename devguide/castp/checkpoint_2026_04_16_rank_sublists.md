# Checkpoint 2026-04-16: Rank-Sublists Pocket Admission

## Purpose

Record the canonicalization step that removes a clear divergence from the
historical `alf_init_pockets()` workflow.

## Change

The native pocket builder no longer admits tetrahedra through a prefilter based
only on the "empty simplex mask".

Instead:

- `build_castp_geometry()` now stores `simplex_rank_sublists`
- `_build_rank_driven_components()` scans tetrahedra rank by rank through those
  sublists
- tetrahedra enter the pocket construction when their tetrahedron `rho` rank is
  reached, matching the historical `alf_init_pockets(rank1, rank2, do_wrap)`
  workflow more closely

This is still a tetrahedron-facing simplification of the full MKALF master
list, but it removes the most obvious non-canonical shortcut:

- before: "candidate tetrahedra = empty-mask selection"
- now: "candidate tetrahedra = tetrahedra whose rho event appears in the
  current rank window"

## Why This Is Canonical

In `voids.c`, `alf_init_pockets()`:

- scans master-list sublists from `rank1 + 1` to `rank2`
- reacts to tetrahedron entries as they appear
- then decides sink / delay / exterior fate

It does **not** first define pockets by connected components of a global
"outside-alpha-complex tetrahedron mask."

The new native code is therefore structurally closer to the original algorithm.

## Consequence

This change should be judged by canonical fidelity, not by immediate parity on
any one system.

If it improves some systems and worsens others in isolation, that is not
evidence against the change. It only means other canonical layers are still
pending.

## Validation

Focused regression checks passed:

- `tests/test_castp_core.py -k "simplex_rank_sublists or rank_driven_components or build_castp_feature_records_uses_canonical_base_rank"`

The broader parity regressions were started but not allowed to run to
completion in this checkpoint session.

## Remaining Fronts Immediately Above This Layer

After this change, the next higher-value canonical fronts remain:

1. exact spectrum / rank semantics
2. attached simplex `mu1/mu2` tables
3. literal mouth seed selection and `Fnext` combinatorics

This checkpoint closes one workflow shortcut, not the full rank-layer audit.
