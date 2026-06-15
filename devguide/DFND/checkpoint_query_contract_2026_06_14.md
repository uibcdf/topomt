# DFND Checkpoint: Typed Mesh and Query Contract

**Date:** 2026-06-14  
**Status:** implemented and verified

## Problem

DFND previously represented one calculation through manually propagated argument
sets. `DFNDData.at_probe()` lost query fields, `sea_level` was recorded despite
having no effect, `min_size` changed wet and dry decomposition differently, and
component selectors interpreted several source shapes independently.

## Decision

DFND separates the cached substrate configuration from a reusable probe query:

- `DFNDMeshConfig`: selection, structure indices, hydrogen policy, radii model,
  and `epsilon`; changing any field requires rebuilding the substrate.
- `DFNDQuery`: probe radius, residence/permeability tolerances, transit policy,
  gate-intrusion policy, and dry adjacency; these fields can be changed while
  reusing the substrate.

Both objects are typed and frozen. Their `to_dict()` mappings feed the existing
identity canonicalization; DFND does not define another hashing scheme.

## Identity and Provenance

`substrate_key` includes the numerical atom substrate and `DFNDMeshConfig`.
`result_key` is derived from `substrate_key` and `DFNDQuery.to_dict()`. Reporting
filters do not affect result identity. Raw parameters preserve flat compatibility
fields and additionally expose `mesh_config`, `query`, `reporting`,
`substrate_key`, and `result_key`.

## Query and Reporting Behavior

- `DFNDData.at_probe()` uses validated query replacement and preserves every
  unspecified query field.
- `at_probe()` rejects mesh-configuration overrides.
- `min_size` is a compatibility/reporting filter, not a decomposition parameter.
  Wet and dry decompositions retain every component and mark
  `include_in_compatibility_view` symmetrically.
- Changing `min_size` does not change component support/context keys.
- `sea_level` was removed completely from DFND because it had no implemented
  scientific meaning and no external compatibility requirement.

## Public Compatibility

The established keyword facade remains supported. Advanced callers may pass
`mesh_config=DFNDMeshConfig(...)` and/or `query=DFNDQuery(...)`. Non-default
legacy arguments that contradict a supplied typed object raise instead of being
silently overwritten.

## Selector Contract

Component selectors normalize supported sources into one internal component
view with explicit wet/dry capabilities. Requesting a side absent from the source
raises an informative error instead of returning a misleading empty result.

## Verification

Tests cover frozen configuration, the mesh/query boundary, epsilon participation
in substrate identity, query-based result identity, reporting-independent
component identity, symmetric wet/dry reporting, full `at_probe()` inheritance,
mesh-override rejection, absence of `sea_level` from DFND APIs, query conflicts, normalized
selector capabilities, and face-selector filter forwarding.

## Remaining Related Work

- Replace the compatibility name `min_size` with an explicit reporting/promotion
  policy when the broader reporting contract is designed.
- Use mesh/query comparability explicitly when temporal matching is implemented.
