# Checkpoint 2026-04-16: Master-List Layer

## Purpose

Record the introduction of a Python-level master-list layer aligned with the
historical MKALF `spectrum.c` / `ml.c` design.

## Change

`build_castp_geometry()` now materializes:

- `master_entries`
- `master_rank_offsets`

in addition to tetrahedron rank sublists.

This layer stores rank-grouped entries for:

- tetrahedron `rho`
- triangle `rho`, `mu1`, `mu2`
- edge `rho`, `mu1`, `mu2`
- vertex `rho`, `mu1`, `mu2`

and sorts each rank sublist by face type in the historical order:

- vertex
- edge
- triangle
- tetrahedron

## Why This Is Canonical

MKALF does not work from detached arrays of ranks alone. It builds:

- a spectrum
- rank tables
- and then a master list with per-rank sublists

Later workflows (`alf_find_voids`, `alf_init_pockets`, `compute_wrap_depths`,
etc.) scan that structure rank by rank.

Until now, the native path had only partial stand-ins for this:

- `spectrum_values`
- various rank arrays
- tetrahedron-only sublists

The new layer is still not a full `alf_ml_*` API, but it is a closer structural
match to the original design.

## Validation

Focused structural regressions passed:

- `tests/test_castp_core.py -k "build_master_entries or simplex_rank_sublists or rank_driven_components"`

## Consequence

This change does not by itself "fix" a red system. That is not the point of the
checkpoint.

The point is to reduce another structural difference with MKALF so later passes
can stop relying on implicit or ad hoc rank-group handling.

## Remaining Immediate Fronts

The highest-value canonical fronts now remaining above this layer are:

1. full spectrum / rank fidelity
2. attached simplex `mu1/mu2` fidelity
3. making more of the pocket / mouth workflow consume the master-list layer
   directly rather than only rank-derived helper structures
