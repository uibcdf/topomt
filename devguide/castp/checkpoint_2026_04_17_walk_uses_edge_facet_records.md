"""Checkpoint for running the native mouth walk directly on edge-facet records."""

# Checkpoint 2026-04-17: Walk Uses Edge-Facet Records

## Purpose

This checkpoint records one more internal cleanup in the native `Fnext` path.

The goal is to make the walk itself operate on explicit edge-facet records,
instead of carrying separate scalar state for:

- `a`
- `b`
- `c`
- `current_tet`

## Historical Motivation

MKALF does not conceptually advance the walk by juggling four separate scalar
variables. It advances an edge-facet object through repeated `Fnext` steps.

The closer the native path gets to that operational model, the less internal
compression remains.

## Native Correction

The native mouth walk now builds an initial `EdgeFacetRecord` and then advances
the walk by repeatedly replacing the current edge-facet with the next one.

So `_fnext_walk_around_edge()` now encodes the same state more explicitly:

- current edge-facet
- next edge-facet
- exit edge-facet

instead of reconstructing that state from loose tuple components on every loop
iteration.

## Why This Matters

This does not change the mathematics of the walk by itself.

It matters because:

- the native implementation becomes easier to audit against MKALF
- future edge-facet refinements have a more literal home
- and one more source of tuple-based reconstruction disappears from the
  combinatorial core

## Structural Verification

The existing structural Fnext tests remain green after this change, which
confirms that the walk can be rewritten around explicit edge-facet records
without changing the already validated behavior.

## Status

This is another internal fidelity step. The remaining edge-facet gap is now
less about missing objects and more about proving that the semantics carried by
those objects matches the historical implementation case by case.
