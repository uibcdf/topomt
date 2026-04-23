# CASTp Checkpoint 2026-04-11: Canonical Vertex Materialization

## Purpose

This checkpoint records a focused canonicalization step in the native CASTp
implementation: replacing the previous boundary-face-based proxy for pocket
boundary atoms with a faithful MKALF-style vertex classification.

The objective of this step was **not** to change pocket topology or mouth
partitioning. It was to align the reported vertex sets with the historical
`iV/rV` semantics.

## Historical Rule

From the audited MKALF sources:

- vertex `mu1/mu2` values are induced from edge ranks in `spectrum.c`
- `alf_is_interior(ALF_VERTEX, rank, v)` is true iff:
  - the vertex is not on hull (`mu2 != 0`)
  - and `v_rank.mu2 <= rank`
- `alf_scan_pocket_v0()` and `alf_scan_pocket_v1()` both start from vertices of
  tetrahedra already belonging to the pocket
- regular pocket vertices (`rV`) are:
  - pocket vertices that are **not** interior at `rank2`
  - or pocket vertices touched by the peeling / outside set

This means that historical `rV` is **not** equivalent to "vertices appearing in
boundary faces".

## What Changed

### Geometry layer

File:

- [topomt/third_party/castp/core/castp_core/geometry.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/geometry.py)

Added canonical vertex-rank construction:

- `vertex_rho_ranks`
- `vertex_mu1_ranks`
- `vertex_mu2_ranks`

These are built from edge ranks following the historical `vertex_mus()` logic in
`spectrum.c`:

- unattached edge: vertex `mu1 <- min(edge.rho)`, `mu2 <- max(edge.mu2)`
- attached edge: vertex `mu1 <- min(edge.mu1)`, `mu2 <- max(edge.mu2)`
- hull triangles force incident vertex `mu2 = 0`

### Component assembly layer

File:

- [topomt/third_party/castp/core/castp_core/components.py](/home/diego/repos@uibcdf/topomt/topomt/third_party/castp/core/castp_core/components.py)

Added:

- `_vertex_is_interior_at()`
- `_component_regular_vertex_indices()`

Current behaviour for open features:

- `atom_indices`: all vertices of tetrahedra in the component
- `component_atom_indices`: same as above
- `boundary_atom_indices`: MKALF-like `rV` set, not boundary-face vertices

This is a canonical improvement over the previous proxy.

## Tests

Added regression:

- [tests/test_castp_core.py](/home/diego/repos@uibcdf/topomt/tests/test_castp_core.py)
  `::test_component_regular_vertex_indices_follow_mkalf_interior_and_touched_logic`

Existing short green battery remained green:

- `1stp`
- `1rop`
- `2lyz`
- `2pk4`

## Interpretation

This step improves faithfulness of reported pocket/channel vertex sets, but it
does **not** by itself resolve the residual `1ubq` atom `299` mismatch. That
residual still points to a local topological decision upstream of reporting.

## Next Step

Continue with the remaining known canonical gap:

- local audit of the `1ubq` face `(297, 300, 301)` between tetrahedra `2133`
  and `2134`, to determine whether the neighbour tetrahedron should enter the
  pocket according to canonical MKALF logic or whether this is already a
  CASTp-3.0-vs-MKALF divergence.
