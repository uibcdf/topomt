# Development Status

TopoMT is currently in an intermediate development stage.

The project already has:

- a coherent `Topography` and `Feature` model;
- a unified top-level entry point through `get_topography()`;
- multiple integrated detection engines;
- initial ecosystem integration with MolSysSuite packages;
- an internal `devguide/` that now reflects the real project structure.

What it does not yet have is a fully consolidated release-quality surface.

## Current priority

The current priority is the non-DFND stabilization path:

- `pocketeer`
- `alphaspace2`
- `fpocket4`
- `pocket_geometry`
- `pycasta`

This work includes:

- reliable atom-index handling;
- normalized engine outputs;
- stronger tests;
- preparation for future MolSysViewer integration.

## DFND

DFND remains part of the project vision, but it is currently a postponed track.

Its design material is richer than most other historical developer documents,
but it is not the current execution priority.

## Practical interpretation

TopoMT is already useful for development and research prototyping, but it
should still be treated as an actively consolidating library rather than a
fully stabilized toolkit.
