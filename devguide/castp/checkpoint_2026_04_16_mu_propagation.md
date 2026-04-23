# Checkpoint 2026-04-16: Canonical `mu1/mu2` Propagation

## Decision

The operational `mu1/mu2` path of the native CASTp implementation should follow
the historical MKALF rank propagation as literally as possible:

- triangles inherit `mu1/mu2` from incident tetrahedron rho ranks
- edges inherit from triangle rank tables
- vertices inherit from edge rank tables
- hull zeroing of `mu2` happens after the propagation sweep, not during it

## Historical Reference

In `spectrum.c`:

- `triangle_mus()` propagates from tetrahedron rho ranks to triangle `mu1/mu2`
- `edge_mus()` propagates from triangles to edges
- `vertex_mus()` propagates from edges to vertices
- for both edges and vertices, `mu2 = 0` on convex-hull entities is applied
  **after** the main propagation sweep

That ordering matters.

## Native Corrections

### 1. Operational path governed by rank propagation

The main `build_castp_geometry()` path no longer carries the extra value-based
edge/vertex `mu` propagation as part of the operational construction. The
runtime logic now depends on the rank-based propagation path.

### 2. Hull-edge `mu2` zeroing fixed

The native `_edge_mu_rank_maps()` and `_edge_mu_value_maps()` previously zeroed
`mu2` for hull edges *inside* the same loop that was still propagating triangle
contributions. That was non-canonical, because later non-hull faces could
overwrite the zero.

The implementation now follows the historical ordering:

1. propagate all triangle contributions
2. collect hull edges
3. zero their `mu2` afterwards

## Implication

This removes another genuine algorithmic deviation from MKALF. It also means
that any older observations involving hull-adjacent edges or vertices should be
treated as provisional if they were collected before this correction.
