# Checkpoint 2026-04-16: Canonical Pocket-Depth Semantics

## Decision

The native CASTp pocket path must use the historical non-wrapping depth
semantics from `compute_tetra_depth()`, not the wrapping-depth semantics from
`compute_tetra_depth2()`.

## Evidence

In the historical MKALF / Alvis path:

- `render_pocket_new(rank1, rank2)` calls
  `alf_init_pockets(display.pocket_rank2, display.pocket_rank1, FALSE)`;
- `alf_init_pockets(..., FALSE)` selects `depth = pocket_depth`;
- `pocket_depth` is built by `alf_compute_pocket_depths()`;
- that function uses `compute_tetra_depth()`, not `compute_tetra_depth2()`.

The two routines differ materially:

- `compute_tetra_depth()` follows the hidden-triangle flow toward the
  **maximum-rho** sink and sends hull-attached tetrahedra to infinity
  immediately;
- `compute_tetra_depth2()` is the wrapping variant and uses the
  **minimum-rho** sink, with different infinity handling.

So using the wrapping variant inside the native pocket path was a direct
algorithmic deviation from MKALF.

## Native Correction

`_compute_pocket_depths()` now mirrors `compute_tetra_depth()` semantics:

- it chooses the maximum-rho reachable sink;
- a hull-attached attached face immediately assigns infinity;
- it no longer implements the wrapping/minimum-rho logic.

## Implication

Any parity observations collected while `_compute_pocket_depths()` still
implemented the wrapping-depth recursion should not be treated as evidence
about final CAST faithfulness for open features.
