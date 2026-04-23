# Checkpoint 2026-04-17: Canonical Reporting Partitions

## Summary

The native CASTp path now reports the canonical MKALF-style simplex partitions
explicitly instead of compressing them to atom sets plus mouths.

The native feature records produced by `build_castp_feature_records()` now
include:

- `iF`: interior pocket/void triangles
- `rF`: regular (mouth) pocket/void triangles
- `iE`: interior pocket/void edges
- `rE`: regular pocket/void edges
- `iV`: interior pocket/void vertices
- `rV`: regular pocket/void vertices

These are also preserved by `_native_impl.py` in the public native output.

## Historical Basis

This follows the historical MKALF reporting split used by:

- `alf_scan_pocket_f0()` / `alf_scan_pocket_f1()`
- `alf_scan_pocket_e0()` / `alf_scan_pocket_e1()`
- `alf_scan_pocket_v0()` / `alf_scan_pocket_v1()`
- `compute_edges_in_pocket()`
- `compute_vert_in_pocket()`

in `mkalf/voids.c`, and the ASCII printer in `mkalf/print_pocket.c`.

The native implementation now mirrors the historical criteria:

- `f0/f1`
  - triangle not in alpha complex at `rank1`
  - `f0`: opposite tetrahedron belongs to the current pocket
  - `f1`: opposite tetrahedron absent or outside the current pocket
- `e0/e1`
  - edge is in the pocket iff it is not in the alpha complex at `rank1`
  - `e0`: edge interior at `rank2` and not touched by peeling
  - `e1`: edge not interior at `rank2` or touched by peeling
- `v0/v1`
  - vertex is in the pocket iff it is not in the alpha complex at `rank1`
  - `v0`: vertex interior at `rank2` and not touched by peeling
  - `v1`: vertex not interior at `rank2` or touched by peeling

## Native Changes

The native code now includes explicit helpers for these partitions:

- `_component_face_partitions()`
- `_component_edge_partitions()`
- `_component_vertex_partitions()`

These are used when assembling both open features and voids.

The previous native `boundary_atom_indices` / `component_atom_indices`
reporting is still kept, but it is no longer the only explicit representation
of the canonical CAST/MKALF reporting split.

## Why This Matters

This closes one of the clear conceptual gaps identified in the reporting audit:
the native implementation can now expose the same main combinatorial reporting
layers that MKALF prints (`iF/rF/iE/rE/iV/rV`), instead of forcing all
comparisons through atom sets and mouth patches alone.

## Residual Reporting Gaps

This does **not** yet close all reporting gaps.

Still open:

- canonical CAST-style area reporting at the same public granularity
- any remaining output compression in `_native_impl.py`
- public exposure of any additional derived mouth geometry beyond area /
  perimeter / triangles
