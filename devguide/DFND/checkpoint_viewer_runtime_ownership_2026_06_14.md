# Viewer Runtime Ownership Checkpoint - 2026-06-14

## Decision

The TopoMT viewer runtime owns one canonical, complete source topography. Visual filtering is state associated with rendering; it never replaces the source analysis object.

- `runtime.topography` and `view.topography` reference the complete attached source.
- `runtime.active_feature_ids` is the current feature-render filter. `None` means all features.
- `runtime.render_groups` records emitted viewer objects for lifecycle management. It is not a second model of visibility.
- DFND and non-feature renders do not modify `active_feature_ids`.

This follows the same model-versus-view separation used by DFND query reporting and atom-index spaces.

## Render-group lifecycle

Render groups use stable keys of the form `<kind>:<tag_prefix>`, currently `features:<tag_prefix>` and `tetrahedra:<tag_prefix>`.

Creating a group replaces and clears only the previous group with the same key. Other groups remain intact. Attaching a different source topography clears all groups because their geometry and feature identities belong to the previous source.

Each group records its kind, tag prefix, applicable feature IDs, emitted tags, and layers. This registry is derived lifecycle state; the viewer tags remain the actual host objects.

## Feature filtering

`show_topography_pockets(..., feature_ids=...)` applies the filter directly while reading the complete source topography. `attach_features()`, `attach_pockets()`, and `new_view(feature_ids=...)` use this path and preserve the complete source in the runtime and view.

`subset_topography()` remains a public, explicit utility for callers that need an independent Topography object. It now starts from `Topography.copy(deep=True)` and removes unselected features, preserving retained relations and attached analysis state coherently. It is not used to implement viewer filtering.

## Behavior change and migration

Previously, `attach_features()`, `attach_pockets()`, and `new_view(feature_ids=...)` left `view.topography` and `runtime.topography` pointing to a partial Topography. They now point to the complete source.

Callers that intentionally need the previous partial-object behavior must create it explicitly:

```python
selected = molsysviewer_topomt.subset_topography(topography, feature_ids)
```

Use `runtime.active_feature_ids` to inspect the current feature filter.

## Verified invariants

- Re-filtering features replaces only `features:<tag_prefix>` and clears its previous tags.
- Feature filters never remove DFND data, unselected features, or relations from the attached source.
- `new_view(feature_ids=...)` renders only selected features while retaining the complete source.
- A semantic `subset_topography()` retains relations among selected features and an independent copy of attached DFND state; this is verified with a real DFND result.
- Panel render and clear actions use the same group lifecycle through `attach_topography()`, `attach_dfnd_tetrahedra()`, and `clear_render_group()`.
- Attaching all features resets `active_feature_ids` to `None` without clearing unrelated render groups.
