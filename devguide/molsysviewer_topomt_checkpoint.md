# MolSysViewer TopoMT Addon Checkpoint

## Why this became the current priority

We are pausing the previous engine-focused line of work in order to start a
first real `molsysviewer` integration for TopoMT.

This does not mean the engine work is finished.
It means the project now needs a visible ecosystem-facing entry point that can
be exercised by users and developers while the remaining native-method work
continues.

## What was already clarified before starting

The addon target is now constrained by the current MolSysViewer add-on
contract, not by older assumptions:

- package name:
  - `molsysviewer-topomt`
- import path:
  - `molsysviewer_topomt`
- required addon exports:
  - `addon`
  - `ADDON`
  - or `get_addon()`
- current contribution types that are safe to start with:
  - workspace
  - panels
  - workbench sections
  - context actions
  - shape providers
  - export helpers
  - lifecycle hooks

The normative references used for this checkpoint are:

- `../molsysviewer/docs/content/developer/addons.md`
- `../molsysviewer/standards/addons/IMPLEMENTATION_CONTRACT.md`
- `../molsysviewer/molsysviewer/addon_templates/minimal_topomt.py`

## First milestone we are implementing now

The first useful milestone is not full rendering fidelity.

The first milestone is:

1. an importable `molsysviewer_topomt` package inside this repository;
2. a valid `AddonSpec` with one workspace and a minimal but real addon surface;
3. a small lifecycle implementation that leaves visible runtime breadcrumbs on
   the `MolSysView` instance;
4. a TopoMT-to-viewer payload adapter that normalizes current `Topography`
   objects into a stable viewer-oriented record shape;
5. a first Python-side render helper that reuses existing MolSysViewer shapes
   for pocket blobs and fallback marker spheres;
6. convenience integration helpers that register the addon, attach a
   `Topography` to an existing view, or build a loaded view and immediately
   overlay the topography;
7. selection-oriented helpers that attach only chosen feature or pocket ids to
   an existing view without forcing callers to manually build a filtered
   `Topography`;
8. tests proving that registration, payload normalization, basic rendering
   helpers, and the convenience integration flow work.

This gives us a restartable integration point without pretending that full
viewer rendering is already solved.

## What this first milestone intentionally does not solve yet

The following are explicitly postponed to the next slice:

- rich frontend panels with custom runtime widgets;
- true pocket rendering through MolSysViewer shape APIs;
- synchronized selection/focus actions tied to rendered pockets;
- export-quality scene composition;
- dedicated AFND visualization support.

## Current implementation direction

The addon is being started conservatively:

- Python-side only;
- no custom frontend hooks yet;
- no new rendering protocol yet;
- reuse of existing `molsysviewer.shapes` primitives only;
- payload normalization first;
- addon registration first.

This matches the current recommendation in the MolSysViewer standards: validate
packaging, registration, lifecycle, workspace/panel plumbing, and only then
grow the rendering side.

## Standalone usefulness target

The addon should already be useful in the current MolSysViewer standalone host,
even before richer UI work exists.

The near-term practical target is:

- load a molecular system;
- compute or reuse a `Topography`;
- render pocket overlays into a `MolSysView`;
- export or launch a standalone host that already contains those overlays.

That path is now represented by the `molsysviewer_topomt.standalone` helper
layer, whose role is not to replace MolSysViewer's standalone host but to make
TopoMT usage short and explicit from this repository.

The intended public helpers are:

- `build_topography_standalone0_html(...)`
- `launch_topography_standalone0(...)`

Those helpers should:

- guarantee that `molsysviewer_topomt` is included in `addon_modules`;
- accept either an explicit `Topography` or a `method=...` request to compute
  one;
- optionally render only a chosen subset of feature ids.

## Pause checkpoint

If this work is resumed later, the practical starting point should be:

1. keep the current Python-side helpers as the stable usage baseline;
2. exercise them with one or more real documented examples from TopoMT demo
   systems;
3. only then decide which visible UI entry should exist first in the addon
   workspace, panel, or workbench layer.

At the moment, the most important thing already achieved is not UI richness but
having a real, restartable path that can:

- compute or accept a `Topography`;
- attach it to a `MolSysView`;
- export or launch a MolSysViewer standalone host with visible pocket
  overlays.

## Expected next slice after this checkpoint

Once the scaffold is in place, the next realistic step should be:

1. render pocket overlays from normalized payload records;
2. connect context actions to viewer focus/visibility operations;
3. expose a real TopoMT workbench section that reflects the active topography;
4. decide which helper logic belongs upstream in `molsysviewer`.

At this checkpoint, item 1 has started in a conservative Python-side way
through `molsysviewer_topomt.render.render_topography_pockets(...)`.
There is now also a first convenience orchestration layer in
`molsysviewer_topomt.integration`.

That integration layer now exposes:

- `register_with_molsysviewer(...)`
- `attach_topography(...)`
- `build_view_with_topography(...)`
- `attach_features(...)`
- `attach_pockets(...)`

One important implementation note is now known and should not be rediscovered
later:

- the current `BaseFeature.copy()` / `__deepcopy__()` path in TopoMT only
  preserves the base feature fields;
- render-relevant dynamic attributes such as `center`,
  `alpha_sphere_centers`, and `alpha_sphere_radii` are lost there;
- for the viewer subset helpers, we currently work around that by cloning the
  complete feature `__dict__` and then reattaching the clone to the subset
  `Topography`.

This workaround is local to the addon helper layer for now. If feature cloning
becomes a broader TopoMT need, the correct long-term fix belongs in the core
feature-copy semantics rather than in the viewer package.
