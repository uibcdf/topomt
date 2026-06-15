# Viewer RenderResult Contract Checkpoint - 2026-06-14

## Decision

The primary TopoMT render operations return one structurally immutable `RenderResult` contract:

- `show_topography_pockets()`;
- `show_dfnd_tetrahedra()`;
- `show_dfn_graph()`;
- `show_dfnd_components()` for every representation.

`RenderResult` contains:

- `representation`: canonical representation name;
- `selected_ids`: selected feature, tetrahedron, graph-node, or component IDs;
- `layers`: all emitted MolSysViewer layers;
- `tags`: exact owned scene-object tags;
- `counts`: read-only integer result counts, always including `n_layers` and `n_selected`;
- `warnings`: non-fatal render warnings;
- `details`: representation-specific metadata;
- `primary_layer` and `is_empty` convenience properties.

An empty render returns `RenderResult(is_empty=True)` rather than `None`. Its boolean value is false.

## Compatibility

`RenderResult` implements `Mapping`. Existing dictionary-style access remains valid, including graph counts and pocket-render records:

```python
result['n_nodes']
result['rendered']
```

Unknown attribute access delegates to `primary_layer`, preserving common single-layer uses such as `result.tag`. Callers that require the actual host layer should use `result.primary_layer`; callers handling every emitted object should use `result.layers`.

The existing public call signatures are preserved; their return annotation now declares `RenderResult`.

The explicit behavior change is that empty primary renders no longer return `None`. Use `if not result` or `result.is_empty`.

## Render lifecycle

Direct component and pocket renders remember their previous `RenderResult` by stable operation key and clear the exact recorded tags before replacement. This fixes derived-tag collisions without maintaining fragile suffix lists.

Component operation keys use `components:<tag_prefix>`. Pocket operation keys use `pockets:<tag_prefix>`. Existing tetrahedron and graph renderers already clear their complete known tag sets before rendering.

The runtime-level `render_groups` from WP-07 remains responsible for attached/integration operations. Direct-render result ownership and runtime groups are complementary: both use exact emitted tags, while only runtime groups describe attached application state.

## Verified invariants

- Every primary renderer returns `RenderResult`, including empty renders and batched host-layer returns.
- Mapping access and primary-layer attribute compatibility work.
- Every one of the 15 component representations renders twice under the same tag prefix without collisions.
- Derived tags such as mouth rings, bottlenecks, and contact-sheet body surfaces are replaced correctly.
- Graph, tetrahedron, and pocket renderers render repeatedly without collisions; an empty replacement clears prior geometry.
- `RenderResult.layers` and runtime render groups contain actual MolSysViewer layers, not nested result objects.
