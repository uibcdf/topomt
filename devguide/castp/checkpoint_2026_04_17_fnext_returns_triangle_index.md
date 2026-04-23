"""Checkpoint for `Fnext` exits carrying native triangle indices."""

# Checkpoint 2026-04-17: `Fnext` Returns Triangle Indices

## Purpose

This checkpoint records another step toward a more literal MKALF-like mouth
path.

The goal is to make the native `Fnext` walk return triangle identity directly,
instead of reducing the exit only to a sorted atom triple.

## Historical Motivation

In MKALF, the mouth walk exits on a triangle object that is immediately tested
through `TrIndex(next)`.

The exit is not conceptually "just the set of its three atoms". The operational
object is the triangle itself.

## Native Correction

The native `_fnext_walk_around_edge()` now returns `FnextWalkExit`, which
contains:

- `face_atoms`
- `triangle_index`
- `simplex_index`

When the mesh provides global face indices, the walk therefore carries the
native analogue of `TrIndex(next)` directly.

The clustering step now prefers that `triangle_index` to identify the exit
mouth triangle, falling back to atom triples only when no triangle index is
available.

## Additional Fix

This pass also corrected a real regression in the Fnext clustering path:

- the walk must start from `record.simplex_index`
- not from an implicit `start_tet` symbol left over from a previous refactor

## Why This Matters

This is a real fidelity improvement.

Before this change:

- the mouth path already had explicit seed records and native triangle indices
- but the walk itself still collapsed the exit triangle back to an atom tuple

Now the walk and the clustering logic speak more consistently in terms of the
same operational object.

## Structural Regression

`tests/test_castp_core.py` now includes regressions proving:

- `Fnext` exits carry `triangle_index` when the mesh can provide it
- the clustering path prefers `triangle_index` identity on the Fnext route

## Status

This does not yet prove a fully literal edge-facet combinatorics layer, but it
removes another important place where the native implementation still collapsed
triangle identity too early.
