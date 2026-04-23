"""Checkpoint for explicit edge-facet records in the native Fnext path."""

# Checkpoint 2026-04-17: Explicit Edge-Facet Records

## Purpose

This checkpoint records another reduction of compression in the native mouth
walk.

The goal is to stop representing the primitive `Fnext` step as a loose tuple
and expose it as an explicit native edge-facet object.

## Historical Motivation

MKALF operates on edge-facets directly.

Even when the code later inspects triangle identity through `TrIndex(next)`,
the primitive combinatorial object is still the edge-facet, not just:

- an atom triple
- plus a neighboring tetrahedron index

## Native Correction

The native `_edge_facet_fnext()` now returns `EdgeFacetRecord` together with the
next tetrahedron index.

`EdgeFacetRecord` carries:

- `oriented_face_atoms`
- `face_atoms`
- `triangle_index`
- `simplex_index`

So the basic mouth-walk step now has a more explicit native analogue of the
historical object it is trying to model.

## Why This Matters

This is a structural fidelity improvement.

Before this change:

- the native walk had already recovered more triangle identity than before
- but the primitive step still returned an ad hoc tuple

Now the code names and preserves the actual object of the operation more
clearly, which makes further edge-facet tightening easier and less error-prone.

## Structural Regression

`tests/test_castp_core.py` now checks that `_edge_facet_fnext()` returns the
expected `EdgeFacetRecord` in a simple two-tetrahedron configuration.

## Status

This does not close the remaining edge-facet gap by itself, but it moves the
native path another step away from tuple-based reconstruction and closer to a
literal combinatorial implementation.
