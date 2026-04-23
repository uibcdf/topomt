# Checkpoint 2026-04-16: Exact Hidden Predicates

## Purpose

Record the canonicalization step that replaces floating-point attachment tests
with exact fixed-point determinant predicates modeled on `weighted.c`.

## Change

The native CASTp path now evaluates:

- triangle attachment through an exact `hidden2` predicate
- edge attachment through an exact `hidden1` predicate

The implementation now follows the historical weighted predicates more closely:

- exact minors are computed with integer Bareiss elimination
- lifted rows are built on a fixed-point grid
- edge attachment no longer uses only a floating-point power-center test

Affected code:

- `topomt/third_party/castp/core/castp_core/geometry.py`

## Why This Is Canonical

In the historical code:

- `spectrum_triangle()` uses `alf_hidden2(...)`
- `spectrum_edge()` uses `alf_hidden1(...)`
- both come from `weighted.c`
- both are exact determinant predicates, not floating-point geometric tests

Our old implementation already mirrored the branch structure of `hidden_triangle`
in `voids.c`, but the underlying attachment predicates still ran in floating
point. That was a real deviation from the historical algorithm.

## Validation

Focused predicate regressions passed:

- `tests/test_castp_core.py -k "weighted_hidden1 or weighted_hidden2 or hidden_triangle"`

Key parity regressions were started but not allowed to complete in this
checkpoint session.

## Remaining Caveat

This closes the floating-point shortcut in the attachment predicates, but it is
still not the same as full DELCX / SoS semantics. The remaining gap is now more
specific:

- exact fixed-point determinant predicates: now present
- full symbolic perturbation / DELCX triangulation semantics: still open

## Consequence

The "hidden / attached" layer should now be treated as significantly closer to
canonical MKALF than before. The next fronts above it remain:

1. full spectrum / rank fidelity
2. attached simplex `mu1/mu2` propagation fidelity
3. literal master-list style pocket construction
