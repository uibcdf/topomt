# Checkpoint 2026-04-16: Probe Rank As Canonical Beta

## Decision

The native CASTp path must build open features with:

- `rank1 = alf_rank(0.0)` (the base union threshold)
- `rank2 = alf_rank(probe_radius^2)` (the beta threshold)

and not with `rank2 = max_rank`.

## Evidence

The historical MKALF and Alvis flow treats pockets as a difference between two
alpha thresholds:

- the lower threshold (`rank1`) is the alpha-zero boundary;
- the upper threshold (`rank2`) is the selected beta threshold.

In the interactive historical path:

- `render_pocket_new(rank1, rank2)` stores the larger rank as the upper
  threshold and the smaller rank as the lower threshold;
- it then calls `alf_init_pockets(display.pocket_rank2, display.pocket_rank1, FALSE)`,
  meaning `alf_init_pockets(lower_rank, upper_rank, FALSE)`.

This matches the theoretical CAST formulation in the papers: pockets are
computed between an alpha and a beta threshold, not between alpha and the full
maximum spectrum rank.

## Native Correction

The native implementation previously used:

- `size_limit_rank = len(spectrum_values)`

inside `build_castp_feature_records()`.

That was non-canonical. The implementation now uses:

- `size_limit_rank = _probe_rank(geometry, probe_radius)`

so the pocket construction, mouth boundary logic, and `rV` materialization all
share the same canonical beta rank.

## Implication

Any parity observations collected before this correction should not be treated
as evidence about final CAST faithfulness for open features, because the native
pipeline was still using the wrong upper threshold.
