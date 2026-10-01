---
summary: Adopt explicit Topography analysis context and spatial support.
issue: uibcdf/topomt#60
status: partial
opened: 2026-09-30
closed:
severity: high
verification: measured
area: [topography, dfnd, input]
guard: tests/test_dfnd_geometry_snapshot.py
normative: devguide/topography_conceptual_contract.md
blocked_by: []
supersedes: []
---

# Topography analysis context and spatial support adoption

## What

Adopt the public context/support contract decided in #59 while preserving
existing Mapping, feature imports and honest incomplete-provider results.
The governing requirements remain in #60 and the implementation route.

## How

The first native numeric ownership slice is implemented and measured in
[the snapshot checkpoint](../DFND/checkpoint_geometry_snapshots_2026_10_01.md).
Mutable coordinate/radius/map inputs cannot retarget an existing network;
cached arrays and public numerical views are protected, and probe queries share
their geometry. The guard above protects only that delivered slice.

The subsequent [input-context slice](../topography_input_context.md) retains
selected single-frame molecular input through MolSysMT, explicit source atom
maps, quantity-valued coordinates/radii and source occurrence namespaces.
`tests/test_dfnd_input_context.py` and `tests/test_topography_input_binding.py`
guard live input edits, historical recovery, copy/restoration, source rebinding
and native source/local label conversion. Standalone validation lives in
`tests/test_topography_input_context.py`. This delivery remains partial;
neutral support, complete method/source provenance and registry write migration
are not covered by these input guards.

## Why

Cached geometry, source identity and recoverable support must describe the
same input even if its live molecular system subsequently changes.

## What was refuted

Freezing configuration objects alone does not protect arrays. A NumPy read-only
flag on a mutable buffer can be re-enabled. Duplicating full geometry per probe
is unnecessary; exact support recovery does not imply exact physical volume.

## Scope and exclusions

This gate includes source/frame/selection/map context, snapshot ownership,
public mutation paths, neutral support/availability and native plus incomplete
provider examples. It excludes #61 participants, #62 occupancy, #63 provider
admission inventory and scientific precision/reference gates #75/#76.

## Acceptance criteria

Retain the complete issue acceptance criteria. Remaining work must define and
test concrete public types/schema, equal lining with distinct support, compatible
source mapping and frame recovery, Topography setter/registry migration, and
honest unavailable geometry operations. Native snapshot tests alone do not close
this public gate.
