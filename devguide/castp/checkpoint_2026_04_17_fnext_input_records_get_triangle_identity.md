"""Checkpoint for populating triangle identity before native Fnext clustering."""

# Checkpoint 2026-04-17: `Fnext` Input Records Get Triangle Identity Up Front

## Purpose

This checkpoint records another fine structural correction in the native
`alf_init_mouths()` path.

The goal is to remove one more fallback from the `Fnext` clustering route:
when the mesh already knows the global identity of a mouth triangle, the
corresponding `MouthFaceRecord` should carry that identity before clustering
starts.

## Historical Reference

In MKALF, the mouth-walk path operates on triangle / edge-facet identities that
already belong to the combinatorial structure.

The clustering logic does not begin with an identity-less triangle and only
later try to recover it from geometry.

So leaving `triangle_index = None` on records that already come from a known
mesh face is still a small TopoMT-specific shortcut.

## Native Correction

The native `cluster_mouth_faces()` now canonicalizes its `MouthFaceRecord`
inputs before entering `_cluster_mouth_faces_fnext()`.

If a record arrives with:

- `triangle_index is None`

but the mesh exposes:

- `get_face_index(simplex_index, face_index)`

then the record is upgraded immediately to a record with canonical triangle
identity.

This means the Fnext clustering path now receives triangle-indexed mouth seeds
whenever the mesh already knows that identity.

## Why This Matters

Before this correction, the code already preferred triangle identity when it
was present, but it still tolerated missing triangle indices and therefore
needed to keep a stronger fallback to face-atom identity than the canonical
path really wants.

The new version:

- strengthens the canonical entry state of the Fnext clustering route
- reduces identity loss before the walk even begins
- and makes triangle-index matching the default behavior whenever the mesh can
  support it

## Structural Regression

`tests/test_castp_core.py` now includes a regression proving that
`cluster_mouth_faces()` populates missing `triangle_index` values before Fnext
clustering when the mesh can provide global face identity.

## Status

This is another fine-grained correction, but it removes one more identity-level
shortcut from the native mouth path.
