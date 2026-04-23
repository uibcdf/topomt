"""Checkpoint for explicit `Enext` on native edge-facet records."""

# Checkpoint 2026-04-17: Explicit `Enext` on Edge-Facets

## Purpose

This checkpoint records another fine-grained reduction of tuple-based
translation in the native mouth path.

The goal is to stop deriving the three initial outward mouth edge-facets from
tuple patterns alone and instead express `Enext` as an explicit operation on
the edge-facet object itself.

## Historical Motivation

In MKALF, the initial mouth edge-facets are built exactly as:

- `tri[0]`
- `tri[1] = Enext(tri[0])`
- `tri[2] = Enext(tri[1])`

That is not merely an ordering convention. It is the operational construction
used by the historical algorithm.

## Native Correction

The native code now exposes `_edge_facet_enext()` and uses it to build the
initial outward edge-facets for a mouth triangle.

So the native initialization path now follows the same explicit pattern:

- build `tri[0]`
- derive `tri[1]` with `Enext`
- derive `tri[2]` with `Enext` again

instead of only reconstructing the equivalent sequence from atom tuples.

## Why This Matters

This is another structural fidelity improvement.

Before this change, the initial edge-facets were already correct by content,
but their construction still relied on a derived tuple-level representation.

Now the same operation exists explicitly in the native combinatorial layer.

## Structural Regression

`tests/test_castp_core.py` now checks that `_edge_facet_enext()` rotates the
oriented vertices while preserving the rest of the edge-facet identity.

## Status

This does not close the remaining edge-facet semantics by itself, but it makes
the initialization of the mouth walk more literally aligned with the historical
algorithm.
