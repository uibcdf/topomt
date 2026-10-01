---
summary: Preserve original PDB atom serials after the parser removes alternate locations.
issue: uibcdf/topomt#83
status: resolved
opened: 2026-10-01
closed: 2026-10-01
severity: medium
verification: reproduced
area: [castp, validation]
guard: tests/methods/castp/test_castp3_oracle_comparison.py::test_atom_id_lookup_respects_parser_alternate_location_removal
normative:
blocked_by: []
supersedes: []
---

# Oracle atom identity after alternate-location resolution

## What

The oracle harness mapped native atom indices onto raw PDB row positions.
MolSysMT can remove alternate locations before geometry construction, so later
indices refer to different serials. The pinned 1ROB archive has 1077 raw atom
rows but 1073 retained atoms. Retained index 66 is serial 68, not discarded 67;
the old mapping misidentified 1007 positions.

## How

A failing-first real-archive test reproduced the count/identity mismatch.
The shared mapping now obtains retained atom IDs from MolSysMT's public API,
verifies each against the exact archived PDB coordinates in angstroms and
rejects duplicate or inconsistent identity. Both offline comparison operations
and the expanded measurement fixture reuse it.

## Why

The faulty harness reported zero exact 1ROB memberships despite correct geometry.
The corrected run reproduces both closed voids and all eight SA/MS measures.

## What was refuted

The first eight-system run's apparent 1ROB geometry failure was a comparator
identity defect. Its stale result is replaced in the current measured artifact,
not treated as a native algorithm regression.

## Scope and exclusions

Offline comparison identity. Runtime geometry and radius defaults are unchanged.
Historical 38-system results were not rerun; counts for alternate-location inputs
must not be reused as verified measurements after this correction.

## Acceptance criteria

Real 1ROB retained IDs/coordinates and gapped-serial fixtures pass. Corrected
1ROB membership/measure evidence is pinned in the expanded panel and the
checkpoint explains the historical evidence limitation.
