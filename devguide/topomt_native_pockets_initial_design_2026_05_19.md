# Superseded Native Pockets Note

Date: 2026-05-19

This note is superseded.

The project decision after further review is that DFND is the native TopoMT
pocket and topography method. TopoMT should not open a second native pocket
algorithm line unless a future design review identifies a concrete need that
DFND cannot satisfy.

The useful material from the previous native-method discussion should be read
as design pressure on DFND, not as a separate package proposal. In particular,
DFND should keep:

- explicit atom and radius policies;
- transparent diagnostics;
- continuous margins rather than hidden binary decisions;
- comparisons against CASTp, CASTpFold, fpocket, AlphaSpace2, Pocketeer, and
  other engines;
- clear separation between method semantics and validation references.

Current DFND references:

- devguide/DFND/Overview.md
- devguide/DFND/feature_definitions.md
- devguide/DFND/implementation_status.md
- devguide/DFND/Implementation_Route.md
- devguide/DFND/dynamic_topology.md

