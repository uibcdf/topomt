"""Checkpoint for native triangle indices analogous to `TrIndex`."""

# Checkpoint 2026-04-17: Native Triangle Indices

## Purpose

This checkpoint records a more substantial structural correction in the native
CASTp path.

The goal is to stop treating a face only as its atom triple and expose a global
triangle index analogous to historical `TrIndex`.

## Historical Motivation

MKALF builds mouths, unions, and reporting around triangle objects addressed by
their triangle index.

Even when the geometry is read through edge-facets, the underlying object is
not merely "the sorted tuple of the three atoms".

## Native Correction

Both `DelaunayMesh` and `WeightedDelaunayMesh` now expose:

- `get_face_index(simplex_index, face_index)`
- `get_face_index_from_atoms(face_atoms)`

These provide a native global face/triangle index layer built from unique face
triples.

`MouthFaceRecord` now carries `triangle_index` when the mesh provides it, and
the mouth clustering path uses that triangle index as the preferred identity
layer, falling back to atom triples only when necessary.

## Why This Matters

This is closer to MKALF in two ways:

1. mouth triangles now have an explicit global identity
2. the clustering path is less dependent on using atom triples as both
   geometry and identity

This does not claim that native triangle numbering matches historical MKALF
numbering. That is not the point. The point is to restore the same kind of
operational object: a globally indexed triangle.

## Structural Regression

`tests/test_castp_core.py` now includes regressions for:

- face-index roundtrip through `get_face_index()` / `get_face_index_from_atoms()`
- propagation of `triangle_index` into native mouth-face records

## Status

This does not fully close the remaining edge-facet combinatorics gap, but it is
one of the clearest remaining moves toward a truly `TrIndex`-like native path.
