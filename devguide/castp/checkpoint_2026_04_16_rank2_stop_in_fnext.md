# Checkpoint 2026-04-16: `rank2` Stop Condition In `Fnext` Walk

## Decision

The native `Fnext` walk used for mouth clustering must stop not only at:

- the hull
- tetrahedra flowing to infinity

but also when the encountered tetrahedron does not belong to the `rank2` shape.

## Historical Reference

In `alf_init_mouths()` the walk continues while the current tetrahedron is in
the pocket structure. It stops when:

- there is no tetrahedron on the next side
- `depth[next_tet]` is infinity
- or `not alf_is_in_complex(ALF_TETRA, rank2, depth[next_tet])`

That third condition is part of the historical algorithm and cannot be dropped.

## Native Correction

The native `_fnext_walk_around_edge()` previously stopped only on:

- hull
- `depth[next_tet] == infinity_marker`

That was incomplete. The implementation now also stops when:

- the sink of `next_tet` has `rho_rank > rank2`

which is the Python equivalent of:

- `not alf_is_in_complex(ALF_TETRA, rank2, depth[next_tet])`

## Implication

This removes another concrete deviation in `alf_init_mouths()` semantics.
Without this stop condition, the walk could cross tetrahedra that were already
outside the historical pocket structure but still had finite depth.
