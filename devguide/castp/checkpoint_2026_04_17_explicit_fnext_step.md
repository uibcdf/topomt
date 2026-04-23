"""Checkpoint for an explicit native `Fnext` edge-facet step."""

# Checkpoint 2026-04-17: Explicit `Fnext` Step

## Purpose

This checkpoint records a structural correction in the native
`alf_init_mouths()` path.

The goal is to reduce one more layer of implicit reconstruction in the mouth
walk and make the code expose the same primitive operation used by MKALF:
advance one edge-facet around the same edge with `Fnext`.

## Historical Reference

In `alf_init_mouths()`, MKALF does not reason in terms of a generic
"while-rotate-around-edge" abstraction only.

It performs repeated applications of:

- `next = Fnext(tri[j])`
- then, if still inside the pocket structure, `next = Fnext(next)`

So the basic combinatorial move is itself explicit in the historical code.

## Native Correction

The native implementation now exposes that move explicitly through
`_edge_facet_fnext()`.

That helper returns:

- the next oriented triangle around the same edge
- and the neighboring tetrahedron that owns it

The higher-level `_fnext_walk_around_edge()` now builds directly on that
primitive instead of recomputing the whole step inline.

## Why This Matters

Before this change, the native code already behaved similarly, but the
combinatorial step was embedded in the loop body and therefore remained more
"TopoMT reconstruction" than "native port of MKALF vocabulary".

Making the `Fnext` step explicit:

- reduces hidden implementation freedom
- makes the walk easier to audit against the C code
- and gives a clearer place to keep tightening edge-facet fidelity

## Structural Regression

`tests/test_castp_core.py` now includes a regression proving that one native
`_edge_facet_fnext()` step returns the next triangle around the same edge in a
simple two-tetrahedron configuration.

## Status

This does not yet mean the whole edge-facet combinatorics is a literal port of
MKALF, but it removes another real layer of compression from the native
implementation.
