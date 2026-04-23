# Checkpoint 2026-04-16: Literal `f1` Seed Selection

## Decision

The native mouth-seed selection should follow the historical `alf_scan_pocket_f1()`
rule as literally as possible:

- triangle not in the alpha complex at `rank1`
- opposite tetrahedron either absent (hull) or not in the current pocket set

and it should not add extra filtering through local depth or beta-side checks
at the seed-selection stage.

## Historical Reference

In `voids.c`, `alf_scan_pocket_f1()` uses:

- `not alf_is_in_complex(ALF_TRIANGLE, p_rank1, triangle)`
- and then checks whether the opposite tetrahedron is missing or not in the
  current pocket union-find set.

That is the seed layer used by `alf_init_mouths()`.

## Native Correction

`_component_boundary_faces()` was still mixing seed selection with additional
logic based on:

- `blocked_nodes`
- `depth`
- `size_limit_rank`

That made the seed layer less literal than the historical `f1` scan.

The implementation now treats `mouth_faces` as regular pocket triangles in the
historical sense:

- outside the alpha complex at `rank1`
- and facing either the hull or a tetrahedron outside the current pocket

## Implication

This does not yet close the whole mouth pipeline, but it removes another place
where the native code was applying a more indirect rule than MKALF.
