# Checkpoint 2026-04-16: Canonical Rank-Table Semantics

## Decision

The native CASTp core should not keep re-implementing local comparisons such as:

- `rho <= rank`
- `rho == 0 and mu1 <= rank`
- `mu2 <= rank`

in ad hoc ways across `components.py` and `mouths.py`.

These are not heuristics; they are the historical MKALF semantics of:

- `alf_is_in_complex`
- `alf_is_interior`

and should therefore be represented explicitly and reused.

## Historical Reference

In `lookup.c`, MKALF defines:

- `alf_is_in_complex(f_type, rank, i)` as:
  - `rho <= rank` if `rho != 0`
  - `mu1 <= rank` if `rho == 0`
- `alf_is_interior(f_type, rank, i)` for non-hull simplices as:
  - `mu2 <= rank`

This is true for vertices, edges, and triangles. Tetrahedra use `rho` only.

## Native Correction

The native core now exposes explicit canonical helpers in `geometry.py`:

- `_rank_table_is_in_complex(...)`
- `_rank_table_is_interior(...)`
- `_face_is_in_complex_at(...)`
- `_edge_is_in_complex_at(...)`
- `_vertex_is_in_complex_at(...)`
- `_vertex_is_interior_at(...)`

and `components.py` / `mouths.py` now use those helpers instead of duplicating
the comparisons locally.

## Implication

This does not by itself close all remaining CAST gaps, but it removes another
class of drift:

- different modules applying the same MKALF rank-table rule in slightly
  different ways.

That matters because rank-table semantics sit underneath:

- pocket union,
- mouth connectivity,
- boundary classification,
- and reporting of regular vs interior simplices.
