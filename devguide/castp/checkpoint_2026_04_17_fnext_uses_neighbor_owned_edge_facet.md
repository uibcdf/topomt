"""Checkpoint for neighbor-owned edge-facets in the native `Fnext` step."""

# Checkpoint 2026-04-17: `Fnext` Uses Neighbor-Owned Edge-Facets

## Purpose

This checkpoint records a small but real structural correction in the native
`alf_init_mouths()` path.

The goal is to remove one more local shortcut from the `Fnext` step:
the next edge-facet should be materialized as an edge-facet of the neighboring
tetrahedron, not as a manually reconstructed tuple that only happens to carry
the same atoms.

## Historical Reference

In MKALF, `Fnext` operates on the current edge-facet and returns the next
edge-facet in the rotation.

That next object is not conceptually "the same current triangle with a patched
owner"; it is the next oriented triangle state in the neighboring tetrahedron.
So the ownership of the returned state matters as part of the combinatorial
semantics.

## Native Correction

The native `_edge_facet_fnext()` no longer takes detached scalars
`(a, b, c, simplex_index)`.

It now takes one explicit `EdgeFacetRecord` and returns the next
`EdgeFacetRecord`.

When the walk stays inside the triangulation, the returned record is now built
through `_make_edge_facet(..., next_simplex_index, mesh)`, so its
`triangle_index` and local identity are recovered from the neighboring
tetrahedron itself.

The hull exit path still carries the current shared triangle identity, but the
non-hull path now follows the owner-local combinatorics more literally.

## Why This Matters

Before this correction, the native implementation already walked around the
correct geometric edge, but the next state still carried one subtle shortcut:
it was reconstructed by hand from atoms plus a patched neighbor index.

That was close in behavior, but not as faithful in structure.

The new version:

- keeps `Fnext` expressed as a transition between explicit edge-facet records
- prefers owner-local triangle identity over detached reconstruction
- and makes the walk easier to audit against MKALF's object-level semantics

## Structural Regression

`tests/test_castp_core.py` now checks that `_edge_facet_fnext()` returns the
next edge-facet with triangle identity resolved from the neighboring tetrahedron
rather than from the current one.

## Status

This does not finish the edge-facet audit, but it removes one more fine-grained
TopoMT shortcut from the mouth-walk core.
