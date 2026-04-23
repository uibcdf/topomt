"""Checkpoint for direct triangle-index return in native `Fnext` steps."""

# Checkpoint 2026-04-17: `Fnext` Step Returns Triangle Index Directly

## Purpose

This checkpoint records another tightening of the native mouth walk.

The goal is to stop recomputing the triangle identity of an `Fnext` exit from
the face atoms when the mesh already knows that identity directly.

## Historical Motivation

In MKALF, the combinatorial step already moves on an edge-facet object whose
triangle identity is immediately available through `TrIndex(...)`.

That means the triangle identity is part of the primitive operation itself, not
an after-the-fact geometric reconstruction.

## Native Correction

The native `_edge_facet_fnext()` now returns:

- the next oriented triangle
- the neighboring tetrahedron index
- and the triangle index directly, via `get_face_index(...)` when the mesh
  provides it

As a consequence, `_fnext_walk_around_edge()` no longer needs to recover that
triangle index from `face_atoms`.

## Why This Matters

This removes another small but real source of non-canonical reconstruction.

Before this change:

- the native walk already returned a triangle index
- but it still derived that index later from the exit face atoms

Now the triangle identity comes out of the primitive step itself, which is
closer to the historical operational model.

## Structural Regression

`tests/test_castp_core.py` now checks that:

- `_edge_facet_fnext()` returns a direct triangle index
- `_fnext_walk_around_edge()` still preserves the correct exit semantics

## Status

This does not finish the whole edge-facet audit, but it removes another
remaining place where the native code reconstructed information that the
combinatorial step itself should already carry.
