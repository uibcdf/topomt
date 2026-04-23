"""Checkpoint for exact rank thresholds in the native CASTp path."""

# Checkpoint 2026-04-17: Exact Threshold Ranks for `base_rank` and `probe_rank`

## Purpose

This checkpoint records a real canonical correction in the native rank layer.

The goal is to remove one important remaining shortcut in the way the native
path computes:

- `base_rank = rank(0.0)`
- `probe_rank = rank(probe^2)`

## Problem

Until now, the native path already built exact `rho` event ratios for spectrum
construction, but then still recovered threshold ranks through float support:

- `base_rank` from `searchsorted(spectrum_values, 0.0)`
- `probe_rank` from `searchsorted(spectrum_values, probe^2)`

That was directionally correct, but not yet faithful to the exact-rank layer we
were already building for the events themselves.

## Native Correction

The native geometry path now keeps:

- `spectrum_ratios`
- `spectrum_decimals`

alongside `spectrum_values`.

Two new helpers now support exact threshold ranking:

- `_rank_of_ratio(...)`
- `_exact_threshold_ratio(...)`

And the operational path now uses them for:

- `base_rank = rank(0.0)`
- `probe_rank = rank(probe^2)`

The native path no longer accepts a float-only operational fallback for
`probe_rank`: canonical probe-rank evaluation now requires

- `spectrum_ratios`
- `spectrum_decimals`

and raises if they are missing.

## Why This Matters

This is not a cosmetic change. `base_rank` and `probe_rank` are central
thresholds for:

- pocket admission
- pocket depth interpretation
- mouth openness
- regular vs interior semantics

So keeping them on the same exact rank scale as the `rho` events is a real
canonical improvement.

This also removes one more ambiguity from the native path: `probe_rank` is no
longer allowed to drift back to a float `searchsorted(...)` path while the rest
of the geometry is already using exact ratio order.

## Structural Regression

`tests/test_castp_core.py` now includes regressions for:

- `_rank_of_ratio(...)`
- `_exact_threshold_ratio(...)`
- `build_castp_feature_records()` using exact `probe_rank` when the geometry
  carries `spectrum_ratios`
- `_probe_rank()` rejecting float-only geometry support

The structural block remained green after the change.

## Status

This does **not** close the entire `rank` front:

- the triangulation substrate still differs from DELCX/SoS
- and full rank equivalence is still not formally proved on all relevant cases

But it removes a real remaining float shortcut from the canonical rank path.
