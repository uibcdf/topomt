"""Checkpoint for keeping triangle identity through native mouth clusters."""

# Checkpoint 2026-04-17: Clusters Keep Triangle Identity

## Purpose

This checkpoint records another structural step toward a more literal MKALF
mouth path.

The goal is to avoid collapsing mouth clusters to raw atom triples too early.

## Historical Motivation

In MKALF, the mouth-building logic does not reduce the clustered mouth
structure to atom triples immediately after union operations.

The operational objects remain triangles and edge-facets for longer than that.

## Native Correction

When `cluster_mouth_faces()` receives `MouthFaceRecord`, the Fnext path now
returns clusters of `MouthFaceRecord`, not clusters of atom triples.

The conversion back to pure face triples now happens later, at the point where
the public feature record is serialized:

- face atoms are still used for geometry and area
- triangle identity is retained through clustering

The serialized mouth records now also expose `triangle_indices` when available.

## Why This Matters

This is another reduction of internal compression.

Before this change:

- the walk already knew triangle identity
- but the cluster result still collapsed that identity immediately

Now the clustering phase preserves the triangle object as long as possible, in
closer agreement with the operational structure of the historical algorithm.

## Structural Regression

`tests/test_castp_core.py` now checks that:

- the Fnext clustering path returns `MouthFaceRecord`
- `build_castp_feature_records()` serializes those clusters while preserving
  `triangle_indices`

## Status

This does not close the whole remaining edge-facet gap, but it removes another
place where the native code discarded triangle identity too early.
