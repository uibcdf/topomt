"""Checkpoint for literal `Enext` edge-facet ordering on mouth faces."""

# Checkpoint 2026-04-17: `Enext` Edge-Facet Order

## Purpose

This checkpoint records a small but real canonical correction in the native
`alf_init_mouths()` path.

The goal is to remove another local TopoMT convention and make the mouth walk
follow the same operational edge-facet sequence used by MKALF.

## Historical Reference

In `alf_init_mouths()`, once the outward-oriented mouth triangle has been
chosen, the historical code enumerates:

- `tri[0]`
- `tri[1] = Enext(tri[0])`
- `tri[2] = Enext(tri[1])`

At the level of an outward-oriented triangle `(a, b, c)`, this corresponds to:

- edge `(a, b)` with opposite vertex `c`
- edge `(b, c)` with opposite vertex `a`
- edge `(c, a)` with opposite vertex `b`

## Native Correction

The native code now makes that sequence explicit through
`_mouth_face_edge_facets()`.

Before this change, the code iterated the same three undirected edges, but in a
TopoMT-specific order. That was close in practice, but not literal.

Now the order is the direct analogue of:

- `tri[0]`
- `Enext(tri[0])`
- `Enext(Enext(tri[0]))`

## Why This Matters

This is not a parity tweak. It is a structural correction.

The native implementation should not rely on "the same set of edges anyway"
when the historical algorithm specifies an operational traversal order. Even if
that order often does not change the final union result, keeping it literal
reduces hidden degrees of freedom and makes later audits easier.

## Structural Regression

`tests/test_castp_core.py` now includes a regression that checks the exact
edge-facet sequence for an outward-oriented mouth triangle.

## Status

This does not close the remaining `Fnext` / edge-facet gap by itself, but it
removes another small non-canonical detail from the mouth walk.
