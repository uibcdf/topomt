# MolSysViewer Addon Plan

## Objective

After the non-DFND core of TopoMT is stable, the next major integration target
is a MolSysViewer addon capable of rendering pockets and related topographic
features on molecular systems.

The intended package is:

- `molsysviewer-topomt`

The intended import path is:

- `molsysviewer_topomt`

## Why this should come after stabilization

The addon must consume stable feature contracts.

If TopoMT still changes the meaning of `atom_indices`, centers, volumes, or
feature typing, the addon will either break or prematurely freeze a weak API.

For that reason, the addon should follow, not lead, the stabilization of the
topography model.

## Rendering modes

The likely first rendering modes are:

### Surface mode

Use atom-driven surfaces when a feature is naturally associated with a set of
atoms.

Expected inputs:

- `atom_indices`
- optional `mouth_atom_indices`
- stable feature id and label metadata

### Blob mode

Use sphere-based rendering when a feature is better represented by alpha-sphere
or probe-sphere geometry.

Expected inputs:

- `centers`
- `radii`
- optional per-sphere values
- stable feature id and method metadata

## Minimum feature payload for visualization

TopoMT should aim to expose a minimal viewer-facing representation with these
fields whenever possible:

- `feature_id`
- `feature_type`
- `source`
- `source_id`
- `atom_indices`
- `center`
- `volume`
- `score`
- optional `mouth_atom_indices`
- optional `sphere_centers`
- optional `sphere_radii`

This payload does not need to be public yet, but it should guide internal
normalization work.

This payload is designed around the current non-DFND priority, but it should
also be compatible with future DFND work. In particular, DFND may later need
viewer support for:

- channels;
- voids;
- mouths and gates;
- dry/wet network components.

For conceptual background on those richer semantics, see:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/Interpretation.md](DFND/Interpretation.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md)

## First implementation strategy

The first addon version should be conservative:

- separate addon package;
- Python-side integration first;
- reuse existing MolSysViewer shapes for pockets;
- avoid new frontend complexity unless strictly necessary.

## Current checkpoint

This line of work has now started.

What currently exists:

- a local addon package scaffold:
  - `molsysviewer_topomt`
- a valid exported addon contract:
  - `addon`
  - `ADDON`
  - `get_addon()`
- a minimal lifecycle implementation for view-local runtime state;
- a first viewer-oriented payload adapter:
  - `molsysviewer_topomt.payloads.topography_payload(...)`
- a first Python-side rendering helper:
  - `molsysviewer_topomt.render.render_topography_pockets(...)`
- first convenience integration helpers:
  - `molsysviewer_topomt.register_with_molsysviewer(...)`
  - `molsysviewer_topomt.attach_topography(...)`
  - `molsysviewer_topomt.build_view_with_topography(...)`
  - `molsysviewer_topomt.attach_features(...)`
  - `molsysviewer_topomt.attach_pockets(...)`
- tests validating registration-level behavior and payload normalization.

What has already been clarified during implementation:

- selective rendering is useful enough to support from the Python helper layer
  now, before a richer panel UI exists;
- the current TopoMT feature copy semantics are not yet sufficient for that
  use case, because the generic copy path drops dynamic geometry attributes
  such as centers and alpha-sphere arrays;
- the addon currently works around that by cloning the full feature state when
  building filtered temporary topographies for rendering.

What still does not exist:

- real panel/workbench UI content;
- context actions wired to actual scene operations.
- richer rendering modes beyond the current blob/marker fallback.

For continuity details, see:

- [molsysviewer_topomt_checkpoint.md](molsysviewer_topomt_checkpoint.md)

## Short-term dependency on current work

Before starting the addon, TopoMT should complete:

- reliable atom-index mapping across engines;
- stable feature metadata for pockets;
- enough tests to trust engine outputs;
- a viewer-oriented normalization layer.

DFND should not block the first addon version. The addon should start from the
stable pocket-oriented payload and only later expand toward richer DFND-driven
representations if and when the DFND implementation becomes production-ready.

## Documentation dependency

This addon plan depends on the MolSysViewer developer documentation, especially:

- addon lifecycle and registration;
- layers and tags;
- payload protocols;
- existing pocket shape APIs.

That material should be revisited before implementation starts.
