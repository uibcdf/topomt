# CASTp Checkpoint 2026-04-17: Rank + Mu + Pocket Block

## Purpose

This checkpoint closes the first large canonicalization block:

- rank semantics
- mu propagation semantics
- pocket state machine

The goal of this pass was to stop making micro-adjustments and instead leave
the operational path materially closer to MKALF in one shot.

## What was consolidated

### 1. Exact threshold ranks are now the only operational threshold path

The native path now uses exact ratio thresholds for:

- `base_rank = rank(0.0)`
- `probe_rank = rank(probe^2)`

The old float-only operational fallback for `probe_rank` is gone.

This means the main pocket path no longer depends on float threshold lookup for
its canonical alpha/beta gates.

### 2. `mu1/mu2` semantics remain rank-driven, not value-driven

The operational semantics continue to be:

- `rho != 0 -> rho <= rank`
- `rho == 0 -> mu1 <= rank`
- `interior -> mu2 <= rank`

But after this block, that semantics is also reflected in the structure of the
implementation:

- the operational path is no longer carrying parallel `mu` value arrays as if
  they were part of the decision machinery
- the geometry substrate keeps the rank tables that actually drive the native
  behavior

### 3. The pocket state machine no longer carries the non-canonical `empty_mask` admission path

The current pocket construction no longer takes an `empty_mask` as part of the
admission rule for tetrahedra.

This is closer to MKALF:

- tetrahedra enter through rank-driven scanning of tetrahedron rho events
- not through a prior mask deciding admission

The void path still uses the complement mask, which is correct for the void
construction.

### 4. Pocket depth and delayed tetrahedra now sit in a cleaner state machine

Within the same block, the pocket route now keeps together:

- `compute_tetra_depth` semantics
- rank-driven tetrahedron scanning
- delayed tetrahedra by sink
- owner-based unions
- event-style handling of buried faces / unions / mouths

That logic was already moving in the right direction, but this pass removed
another layer of residual compatibility and split operational state from dead
state more cleanly.

## What was removed from the operational path

The following pieces are no longer part of the main rank/mu/pocket execution
path:

- pocket-depth API carrying an `empty_mask` parameter that was already ignored
- pocket-construction API carrying `empty_mask` as if it were part of
  canonical tetrahedron admission
- stored geometry fields for:
  - `simplex_rho_values`
  - `face_mu1_values`
  - `face_mu2_values`

Those values were still useful historically as an audit aid, but they were not
part of the live native semantics anymore. Removing them from the operational
geometry surface makes the implementation less ambiguous.

## What this does not claim

This block does **not** claim that TopoMT now reproduces DELCX/SoS or that
rank identity is fully proved identical to MKALF in every medium case.

What it does claim is narrower and stronger:

- the native operational path for rank + mu + pocket assembly is now much less
  compressed
- much less bifurcated
- and much closer to the historical logic as code, not only in output

## Validation

The block was validated with:

- focused rank/pocket tests
- the accumulated structural block in `tests/test_castp_core.py`

Both remained green after the consolidation.

## Effect on open fronts

After this block, the main conceptual fronts still open are now better framed
as:

1. exact rank equivalence as a proved property, not just exact-threshold usage
2. remaining fine semantic differences in mouths / `Fnext`
3. reporting layers still not fully CAST-shaped
4. triangulation / `DELCX/SoS`

So `rank + mu + pocket state machine` should no longer be treated as a loose
collection of micro-fixes. It is now one substantially consolidated canonical
block.
