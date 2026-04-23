"""Checkpoint for making native `Fnext` return only the next edge-facet."""

# Checkpoint 2026-04-17: `Fnext` Returns the Next `EdgeFacetRecord` Only

## Purpose

This checkpoint records another fine structural correction in the native
`alf_init_mouths()` path.

The goal is to remove one more redundant layer from the native `Fnext`
primitive.

## Historical Reference

In MKALF, `Fnext(...)` returns the next edge-facet.

The owner tetrahedron of that next state is implicit in the returned
edge-facet itself; it is not returned as a second detached value.

So a native implementation that returns both:

- the next edge-facet
- and a separate `next_tet`

still carries a small TopoMT-specific redundancy.

## Native Correction

The native `_edge_facet_fnext()` now returns only one `EdgeFacetRecord`.

The owner tetrahedron of the next state is read from:

- `next_edge_facet.simplex_index`

inside `_fnext_walk_around_edge()`.

This makes the primitive closer to the historical semantics:

- `Fnext` yields the next combinatorial object
- and the ownership of that object is part of the object itself

## Why This Matters

Before this correction, the code was already structurally close, but it still
split one historical object into two return values.

That was operationally fine, but less faithful than necessary.

The new version:

- removes one more internal redundancy
- keeps the walk state centered on the explicit edge-facet object
- and makes the native `Fnext` step even closer to the object-level style of
  MKALF

## Structural Regression

`tests/test_castp_core.py` now checks `_edge_facet_fnext()` as a function that
returns only the next `EdgeFacetRecord`, with the owner tetrahedron encoded in
its `simplex_index`.

## Status

This is a fine-grained correction, but it removes one more remaining shortcut
from the native mouth-walk core.
