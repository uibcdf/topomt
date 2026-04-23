"""Checkpoint for record-based mouth identity in native clustering."""

# Checkpoint 2026-04-17: Record-Based Mouth Identity

## Purpose

This checkpoint records one more structural cleanup in the native mouth path.

The goal is to stop treating `face_atoms` as the identity of a mouth triangle
inside the clustering logic.

## Historical Motivation

In MKALF, mouth connectivity is built over triangle objects and edge-facets.

The triangle identity is not "the sorted atom tuple" as such. That tuple is a
geometric descriptor, but the operational object is the triangle record itself.

## Native Correction

The native code now performs mouth unions over explicit `MouthFaceRecord`
indices, using `face_atoms` only to detect geometric correspondence at the exit
of an `Fnext` walk.

This removes another indirect convention from the native implementation:

- identity is no longer assigned by a dictionary keyed only by `face_atoms`
- identity now belongs to the explicit mouth-seed record

## Why This Matters

This is again not a parity tweak but a fidelity cleanup.

Using `face_atoms` as both:

- geometry
- and identity

was a TopoMT shortcut. It worked often, but it was still a compressed
representation compared with the historical algorithm.

Keeping record identity explicit makes later edge-facet audits safer and more
literal.

## Structural Regression

`tests/test_castp_core.py` now includes a regression proving that
`cluster_mouth_faces()` accepts `MouthFaceRecord` directly as the primary mouth
seed representation.

## Status

This does not close the full `TrIndex` / edge-facet gap yet, but it removes one
more place where native bookkeeping still depended on a lossy shortcut.
