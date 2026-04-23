"""Checkpoint for preferring local-face identity over atom lookup."""

# Checkpoint 2026-04-17: Prefer Local Face Identity

## Purpose

This checkpoint records another fine-grained reduction of geometric
reconstruction in the native mouth path.

The goal is to prefer local tetrahedron-face identity whenever it is already
available, instead of recovering triangle identity from sorted atom triples.

## Historical Motivation

In MKALF, triangle identity is not normally recovered from geometry after the
fact when the local combinatorial object is already known.

The code advances from edge-facet and triangle objects directly.

## Native Correction

`_make_edge_facet()` now prefers:

- the local tetrahedron face
- and its direct `get_face_index(simplex_index, face_index)`

whenever the current `(a, b, c)` triangle is a face of the supplied simplex.

Only when that direct local route is unavailable does it fall back to
`get_face_index_from_atoms(...)`.

## Why This Matters

This is a small but real fidelity improvement.

Before this change, even the initial walk state could still recover triangle
identity from atoms in cases where the local simplex already gave enough
information to identify the face directly.

Now the native path prefers the more combinatorial route, and uses geometric
recovery only as a fallback.

## Structural Regression

`tests/test_castp_core.py` now checks that `_make_edge_facet()` prefers the
local face index and does not fall back to atom-based lookup when the simplex
face is already known.

## Status

This is another fine reduction of shortcuts. It does not change the public
result directly, but it makes the internal path more literal and less
reconstructive.
