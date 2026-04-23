"""Checkpoint for explicit initial edge-facets on mouth triangles."""

# Checkpoint 2026-04-17: Explicit Initial Mouth Edge-Facets

## Purpose

This checkpoint records another reduction of tuple-based compression in the
native mouth path.

The goal is to stop representing the three outward initial edge-facets of a
mouth triangle as ad hoc `(edge, third_vertex)` tuples.

## Historical Motivation

In `alf_init_mouths()`, once the outward triangle has been chosen, the code
does not conceptually switch back to abstract edge/vertex pairs.

It immediately works with:

- `tri[0]`
- `tri[1] = Enext(tri[0])`
- `tri[2] = Enext(tri[1])`

That is already a sequence of explicit edge-facets.

## Native Correction

The native code now exposes those three initial outward edge-facets through
`_mouth_face_initial_edge_facets()`, which returns `EdgeFacetRecord` objects.

So the mouth path now has explicit edge-facets:

- at the initial mouth triangle
- in the primitive `Fnext` step
- and in the walk state

## Why This Matters

This is a structural fidelity step.

Before this change:

- the initial outward triangle was already correct
- but the three edge-facets were still encoded as tuple pairs

Now the walk is edge-facet based from the first step onward.

## Structural Regression

`tests/test_castp_core.py` now checks that the three initial outward
edge-facets are materialized as explicit `EdgeFacetRecord` objects.

## Status

This does not by itself prove full MKALF equivalence of the mouth layer, but it
removes another remaining tuple-based shortcut from the combinatorial path.
