# MolSysViewer Addon Plan

## Objective

After the non-AFND core of TopoMT is stable, the next major integration target
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

This payload is designed around the current non-AFND priority, but it should
also be compatible with future AFND work. In particular, AFND may later need
viewer support for:

- channels;
- voids;
- mouths and gates;
- dry/wet network components.

For conceptual background on those richer semantics, see:

- [AFND/Overview.md](AFND/Overview.md)
- [AFND/Interpretation.md](AFND/Interpretation.md)
- [AFND/Technical_Design.md](AFND/Technical_Design.md)

## First implementation strategy

The first addon version should be conservative:

- separate addon package;
- Python-side integration first;
- reuse existing MolSysViewer shapes for pockets;
- avoid new frontend complexity unless strictly necessary.

## Short-term dependency on current work

Before starting the addon, TopoMT should complete:

- reliable atom-index mapping across engines;
- stable feature metadata for pockets;
- enough tests to trust engine outputs;
- a viewer-oriented normalization layer.

AFND should not block the first addon version. The addon should start from the
stable pocket-oriented payload and only later expand toward richer AFND-driven
representations if and when the AFND implementation becomes production-ready.

## Documentation dependency

This addon plan depends on the MolSysViewer developer documentation, especially:

- addon lifecycle and registration;
- layers and tags;
- payload protocols;
- existing pocket shape APIs.

That material should be revisited before implementation starts.
