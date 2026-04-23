"""Checkpoint for explicit mouth-face seed records."""

# Checkpoint 2026-04-17: Explicit Mouth-Face Records

## Purpose

This checkpoint records another reduction of internal compression in the native
mouth-building path.

The goal is to stop representing one mouth-triangle seed through three
position-coupled lists and instead treat it as one explicit entity.

## Historical Motivation

In MKALF, the operational object is the mouth triangle itself, addressed by its
triangle index and then traversed through edge-facets.

The historical code does not conceptually work with:

- a list of triangle atom tuples
- a parallel list of simplex owners
- a parallel list of face indices

It works with the triangle as a single primary object.

## Native Correction

The native code now uses `MouthFaceRecord` as the explicit seed record for one
regular mouth triangle.

Each record carries:

- `face_atoms`
- `simplex_index`
- `face_index`

So the clustering step can consume a less indirect representation of the mouth
seed, closer to the historical operational object.

## Why This Matters

This does not change the mathematical result by itself.

It matters because:

- it removes another local bookkeeping convention
- it makes the data flow easier to audit
- and it reduces the risk of future drift between face atoms, owner simplex,
  and face index

This is exactly the kind of structural cleanup required for a faithful native
reproduction of CASTp.

## Structural Regression

The structural test block now validates the same mouth path with explicit mouth
records in place.

## Status

This does not close the remaining `Fnext` / edge-facet gap, but it removes one
more indirect representation layer from the native implementation.
