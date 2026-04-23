# Checkpoint 2026-04-17: Pocket Sequence State Machine

## Summary

The native pocket builder now includes a much more literal analogue of
historical `alf_pocket_sequence()` / `handle_tetra_seq()`.

Specifically:

- `handle_tetra_seq` now exists explicitly in the native code
- the native path exposes historical pocket-sequence event types:
  - `ALF_POC_RANK`
  - `ALF_POC_TETRA`
  - `ALF_POC_BURIED`
  - `ALF_POC_UNION_SAME`
  - `ALF_POC_UNION_TWO`
  - `ALF_POC_MOUTH`
- delayed tetrahedra keyed by sink are now drained in **LIFO** order,
  matching the historical `basic_istaque_push/pop` stack behavior
- the native union-find now uses **union by size** with special handling for
  the exterior set, matching the semantics of historical `basic_uf_union()`

## Historical Basis

The relevant historical flow is:

- `alf_pocket_sequence()`
  - scans tetrahedron rho sublists rank by rank
  - delays tetrahedra under their sink tetrahedron
  - drains delayed tetrahedra before the sink itself
  - signals end-of-rank via `p_hook(..., ALF_POC_RANK)`
- `handle_tetra_seq()`
  - emits tetra / buried / union / mouth events
  - unions pocket sets through regular triangles

The native path now mirrors these structural steps instead of reducing the
builder to "rank-driven component growth" alone.

## Native Changes

### Explicit pocket-sequence events

The native builder can now emit a direct analogue of the historical pocket
sequence event stream. This does not yet drive public reporting, but it removes
another compressed internal layer and makes the state machine explicit.

### LIFO delayed tetrahedra

Historically, delayed tetrahedra are stored in `basic_istaque` stacks and
therefore drained in last-in / first-out order.

The native builder previously drained delayed tetrahedra in list insertion
order. That was non-canonical. It now drains them in LIFO order.

### Union-find semantics

Historically, `basic_uf_union()` is not a trivial "pick the smaller root id"
merge. It:

- unions by set size
- keeps the exterior set special

The native union-find now follows the same rule instead of root-id ordering.

## Why This Matters

This does not immediately change the public feature taxonomy by itself, but it
removes a real conceptual divergence in the core pocket builder:

- the historical builder is a rank-driven state machine with delayed sink
  stacks and typed events
- the native builder is now much closer to that machine, instead of only
  reproducing its final connected components

## Residual State-Machine Gaps

Still open:

- whether every remaining union / ownership detail of `handle_tetra_seq()`
  is now literal enough for a strict MKALF fidelity claim
- whether the native path should expose or reuse the pocket-sequence event
  stream more directly in later reporting / signature layers
