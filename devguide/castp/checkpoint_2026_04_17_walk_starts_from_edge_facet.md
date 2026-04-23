"""Checkpoint for starting the native `Fnext` walk from an edge-facet record."""

# Checkpoint 2026-04-17: `Fnext` Walk Starts from `EdgeFacetRecord`

## Purpose

This checkpoint records another fine structural correction in the native
`alf_init_mouths()` path.

The goal is to remove one more residual shortcut from the mouth walk:
the walk should start from an explicit edge-facet object, not from a detached
tuple of atoms plus a simplex index that is immediately reassembled into an
edge-facet inside the walk body.

## Historical Reference

In MKALF, `alf_init_mouths()` does not conceptually start from a set of scalars
that are later converted into an edge-facet.

It starts from `tri[j]`, which is already one explicit edge-facet of the mouth
triangle, and then repeatedly applies `Fnext(...)` to that object.

So the start state of the walk is itself part of the combinatorial vocabulary.

## Native Correction

The native `_fnext_walk_around_edge()` no longer receives:

- `a`
- `b`
- `start_third_vertex`
- `start_tet`

It now receives one explicit `EdgeFacetRecord`.

This makes the walk state explicit from the first step and removes one more
TopoMT-specific compression from the `alf_init_mouths()` path.

`_cluster_mouth_faces_fnext()` now passes the initial edge-facets produced by
`_mouth_face_initial_edge_facets()` directly into the walk.

## Why This Matters

Before this correction, the walk core was already close to MKALF, but the entry
point still depended on one avoidable reconstruction:

- build the initial edge-facet
- decompose it into scalars
- then rebuild it immediately inside the walk

That was operationally harmless, but structurally less faithful.

The new version:

- starts from the explicit edge-facet object
- keeps the walk state explicit from the first step
- and makes the native code closer to the object-level style of MKALF

## Structural Regression

`tests/test_castp_core.py` now exercises `_fnext_walk_around_edge()` starting
from an explicit `EdgeFacetRecord`, and the focused `Fnext` block remains green.

## Status

This does not complete the edge-facet audit, but it removes another remaining
shortcut from the mouth-walk entry path.
