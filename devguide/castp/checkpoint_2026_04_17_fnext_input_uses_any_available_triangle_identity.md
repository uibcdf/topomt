"""Checkpoint for completing triangle identity before native Fnext clustering."""

# Checkpoint 2026-04-17: `Fnext` Input Uses Any Available Triangle Identity

## Purpose

This checkpoint records another fine structural correction in the native
`alf_init_mouths()` path.

The goal is to reduce the remaining reliance on atom-tuple fallback by making
the Fnext clustering input as triangle-indexed as the mesh already allows.

## Historical Reference

In MKALF, the mouth-walk path operates on explicit triangle / edge-facet
identities that belong to the combinatorial structure.

It does not conceptually keep mouth seeds in an "identity unknown" state when
that identity is already recoverable from the triangulation.

## Native Correction

The native canonicalization of `MouthFaceRecord` inputs now completes missing
`triangle_index` values through either of the mesh-level identity routes that
TopoMT may already expose:

- `get_face_index(simplex_index, face_index)`
- `get_face_index_from_atoms(face_atoms)`

So the Fnext clustering route now receives triangle-indexed records whenever
the mesh can resolve that identity by any available canonical path.

## Why This Matters

Before this correction, the input canonicalization only filled
`triangle_index` when the mesh exposed direct owner-local face indexing.

That was good, but still left a structural gap: some meshes already knew a
global face identity by atoms, and the clustering path still tolerated missing
triangle indices in those cases.

The new version:

- makes the Fnext input more consistently triangle-indexed
- reduces the need for later fallback to face-atom identity
- and pushes the native mouth path one step closer to explicit combinatorial
  identity throughout

## Structural Regression

`tests/test_castp_core.py` now includes a regression proving that
`cluster_mouth_faces()` populates missing `triangle_index` values both when the
mesh exposes owner-local face indexing and when it only exposes global face
identity by atoms.

## Status

This is another fine-grained correction, but it removes one more identity-level
shortcut from the native mouth path before the walk even begins.
