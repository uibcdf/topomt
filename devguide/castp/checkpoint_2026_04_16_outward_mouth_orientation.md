"""Checkpoint for explicit outward mouth-face orientation."""

# Checkpoint 2026-04-16: Outward Mouth Orientation

## Purpose

This checkpoint records one more step toward a literal `alf_init_mouths()`
implementation in the native CASTp path.

The goal is not parity by symptom, but removal of one more implicit TopoMT
convention in favor of explicit historical semantics.

## Historical Reference

In `voids.c`, `alf_init_mouths()` does not start the `Fnext` walk from an
arbitrary ordering of the mouth triangle atoms.

Instead, it first chooses:

- `tri[0] = EdFacet(t, 0)`
- `dp = depth[alf_tetra_index(tri[0])]`
- and if `dp == infinity` or `rho(dp) > rank2`, it replaces `tri[0]` with
  `Sym(tri[0])`

Only after that does it define:

- `tri[1] = Enext(tri[0])`
- `tri[2] = Enext(tri[1])`

So the starting orientation of the mouth triangle is explicitly tied to whether
the owning tetrahedron lies inside or outside the `rank2` shape.

## Native Correction

The native code now makes this step explicit through
`_mouth_face_outward_atoms()`.

That helper:

- starts from the oriented face order given by the tetrahedral mesh
- inspects the sink of the owning tetrahedron
- and reverses the triangle orientation when that sink is outside the `rank2`
  shape or equals the infinity marker

This is the Python analogue of choosing `tri[0]` or `Sym(tri[0])` before the
three oriented edge-facets are enumerated for the `Fnext` walk.

## Why This Matters

Without this step, the native code still relied on an implicit convention about
which local face order should seed the walk.

That is weaker than the historical algorithm, because MKALF decides the
starting edge-facet orientation from pocket ownership relative to `rank2`, not
from a generic mesh-facing convention.

Making this explicit reduces one more source of silent drift in mouth
construction.

## Structural Regression

`tests/test_castp_core.py` now includes a regression that checks:

- inward orientation is preserved when the owning sink remains inside `rank2`
- orientation flips when the sink lies outside `rank2`

This is a structural test, not a parity test.

## Status

This does not by itself prove full `alf_init_mouths()` equivalence, but it
removes another real non-canonical degree of freedom.

The remaining open front in this area is the literal edge-facet combinatorics
of `Fnext`, not the initial outward-vs-inward face choice.
