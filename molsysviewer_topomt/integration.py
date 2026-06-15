from collections.abc import Iterable
from typing import Any

from .render import show_dfnd_tetrahedra, show_topography_pockets
from .runtime import ensure_runtime


def register_with_molsysviewer() -> None:
    """Register the TopoMT addon in the MolSysViewer host registry if needed."""
    import molsysviewer

    if not molsysviewer.addons.contains('topomt'):
        from .addon import get_addon, lifecycle

        molsysviewer.addons.register(get_addon(), lifecycle=lifecycle)


def subset_topography(topography, feature_ids) -> Any:
    """Return an independent semantic subset of a Topography.

    This public utility preserves analysis state and relations among retained
    features. Viewer filtering does not use it; the viewer keeps the complete
    source topography attached.
    """
    selected_ids = {
        feature_id for feature_id in feature_ids if feature_id in topography
    }
    subset = topography.copy(deep=True)
    for feature_id in list(subset):
        if feature_id not in selected_ids:
            subset.remove_feature(feature_id)
    return subset


def _render_group_key(kind: str, tag_prefix: str) -> str:
    return f'{kind}:{tag_prefix}'


def _clear_render_group(view, runtime, group_key: str) -> bool:
    previous = runtime.render_groups.pop(group_key, None)
    if previous is None:
        return False
    for tag in previous.get('tags', ()):
        view.shapes.clear(tag=tag, skip_digestion=True)
    return True


def clear_render_group(view, kind: str, tag_prefix: str) -> bool:
    """Clear one stable TopoMT render group and synchronize runtime state."""
    if kind not in {'features', 'tetrahedra'}:
        raise ValueError("kind must be 'features' or 'tetrahedra'")
    runtime = ensure_runtime(view)
    cleared = _clear_render_group(view, runtime, _render_group_key(kind, tag_prefix))
    if kind == 'features':
        runtime.active_feature_ids = ()
    return cleared


def _clear_all_render_groups(view, runtime) -> None:
    for group_key in list(runtime.render_groups):
        _clear_render_group(view, runtime, group_key)


def _attach_source(view, runtime, topography) -> None:
    if runtime.topography is not None and runtime.topography is not topography:
        _clear_all_render_groups(view, runtime)
        runtime.active_feature_ids = None
    runtime.topography = topography
    view.topography = topography


def _record_feature_render_group(runtime, tag_prefix, feature_ids, rendered) -> str:
    group_key = _render_group_key('features', tag_prefix)
    records = [] if rendered is None else rendered.get('rendered', [])
    runtime.render_groups[group_key] = {
        'kind': 'features',
        'tag_prefix': tag_prefix,
        'feature_ids': feature_ids,
        'tags': tuple(record['tag'] for record in records if record.get('tag')),
        'layers': tuple(record['layer'] for record in records if record.get('layer')),
    }
    return group_key


def _record_tetrahedra_render_group(runtime, tag_prefix, rendered) -> str:
    group_key = _render_group_key('tetrahedra', tag_prefix)
    layers = tuple(getattr(rendered, 'layers', ()) or ())
    tags = tuple(getattr(rendered, 'tags', ()) or ())
    runtime.render_groups[group_key] = {
        'kind': 'tetrahedra',
        'tag_prefix': tag_prefix,
        'feature_ids': None,
        'tags': tags,
        'layers': layers,
    }
    return group_key


def attach_topography(
    view,
    topography,
    *,
    enable_addon: bool = True,
    show: bool = True,
    show_tetrahedra: bool = False,
    tag_prefix: str = 'topomt-pocket',
    tetra_tag_prefix: str = 'dfnd-tetra',
    skip_digestion: bool = False,
    **render_kwargs,
) -> dict[str, Any]:
    """Attach a TopoMT topography to an existing MolSysViewer view."""
    register_with_molsysviewer()
    if enable_addon:
        view.addons.enable('topomt')
        from .addon import lifecycle

        lifecycle.on_enable(view)

    runtime = ensure_runtime(view)
    _attach_source(view, runtime, topography)
    runtime.active_feature_ids = None
    if tag_prefix:
        runtime.tag_prefix = tag_prefix

    feature_group_key = _render_group_key('features', tag_prefix)
    _clear_render_group(view, runtime, feature_group_key)
    rendered = None
    if show:
        # Separate pocket kwargs and tetrahedra kwargs
        pocket_kwargs = {
            k: render_kwargs[k]
            for k in ['color_map', 'alpha', 'marker_color', 'marker_alpha']
            if k in render_kwargs
        }
        rendered = show_topography_pockets(
            view,
            topography,
            feature_ids=None,
            tag_prefix=tag_prefix,
            skip_digestion=True,
            **pocket_kwargs,
        )
    feature_group_key = _record_feature_render_group(
        runtime, tag_prefix, None, rendered
    )

    rendered_tetrahedra = None
    if show_tetrahedra:
        _clear_render_group(
            view, runtime, _render_group_key('tetrahedra', tetra_tag_prefix)
        )
        tetra_alpha = render_kwargs.get('tetra_alpha', render_kwargs.get('alpha', 0.4))
        rendered_tetrahedra = show_dfnd_tetrahedra(
            view,
            topography,
            color_mode=render_kwargs.get('color_mode', 'combined_class'),
            color_palette=render_kwargs.get('color_palette'),
            alpha=tetra_alpha,
            draw_edges=render_kwargs.get('draw_edges', True),
            edge_radius_nm=render_kwargs.get('edge_radius_nm', 0.002),
            edge_color=render_kwargs.get('edge_color', 0x444444),
            tag_prefix=tetra_tag_prefix,
            name=render_kwargs.get('tetra_name', 'DFND Tetrahedra'),
            skip_digestion=True,
            tetrahedra_indices=render_kwargs.get('tetrahedra_indices'),
            exterior_only=render_kwargs.get('exterior_only', False),
        )
        _record_tetrahedra_render_group(runtime, tetra_tag_prefix, rendered_tetrahedra)

    return {
        'addon_enabled': 'topomt' in view.addons.enabled(skip_digestion=True),
        'rendered': rendered,
        'rendered_tetrahedra': rendered_tetrahedra,
        'tag_prefix': tag_prefix,
        'render_group_key': feature_group_key,
    }


def attach_features(
    view,
    topography,
    *,
    feature_ids,
    enable_addon: bool = True,
    show: bool = True,
    tag_prefix: str = 'topomt-pocket',
    skip_digestion: bool = False,
    **render_kwargs,
) -> dict[str, Any]:
    """Attach a complete source and render only the selected features."""
    register_with_molsysviewer()
    if enable_addon:
        view.addons.enable('topomt')
        from .addon import lifecycle

        lifecycle.on_enable(view)

    runtime = ensure_runtime(view)
    _attach_source(view, runtime, topography)
    selected_ids = tuple(
        feature_id for feature_id in feature_ids if feature_id in topography
    )
    runtime.active_feature_ids = selected_ids
    if tag_prefix:
        runtime.tag_prefix = tag_prefix

    group_key = _render_group_key('features', tag_prefix)
    _clear_render_group(view, runtime, group_key)
    rendered = None
    if show:
        pocket_kwargs = {
            key: render_kwargs[key]
            for key in ['color_map', 'alpha', 'marker_color', 'marker_alpha']
            if key in render_kwargs
        }
        rendered = show_topography_pockets(
            view,
            topography,
            feature_ids=selected_ids,
            tag_prefix=tag_prefix,
            skip_digestion=True,
            **pocket_kwargs,
        )
    group_key = _record_feature_render_group(
        runtime, tag_prefix, selected_ids, rendered
    )
    return {
        'addon_enabled': 'topomt' in view.addons.enabled(skip_digestion=True),
        'rendered': rendered,
        'tag_prefix': tag_prefix,
        'selected_feature_ids': list(selected_ids),
        'render_group_key': group_key,
    }


def attach_pockets(
    view,
    topography,
    *,
    pocket_ids,
    enable_addon: bool = True,
    show: bool = True,
    tag_prefix: str = 'topomt-pocket',
    skip_digestion: bool = False,
    **render_kwargs,
) -> dict[str, Any]:
    """Attach only selected pocket features to an existing view."""
    return attach_features(
        view,
        topography,
        feature_ids=pocket_ids,
        enable_addon=enable_addon,
        show=show,
        tag_prefix=tag_prefix,
        skip_digestion=True,
        **render_kwargs,
    )


def attach_dfnd_tetrahedra(
    view,
    topography,
    *,
    enable_addon: bool = True,
    color_mode: str = 'combined_class',
    color_palette: dict[str, int] | None = None,
    alpha: float | dict[str, float] = 0.4,
    draw_edges: bool = True,
    edge_radius_nm: float = 0.002,
    edge_color: int = 0x444444,
    tag_prefix: str = 'dfnd-tetra',
    name: str = 'DFND Tetrahedra',
    skip_digestion: bool = False,
    tetrahedra_indices: Iterable[int] | None = None,
    exterior_only: bool = False,
) -> dict[str, Any]:
    """Render DFND tetrahedra programmatically into the viewer and enable topomt addon."""
    register_with_molsysviewer()
    if enable_addon:
        view.addons.enable('topomt')
        from .addon import lifecycle

        lifecycle.on_enable(view)

    runtime = ensure_runtime(view)
    _attach_source(view, runtime, topography)
    group_key = _render_group_key('tetrahedra', tag_prefix)
    _clear_render_group(view, runtime, group_key)

    layer = show_dfnd_tetrahedra(
        view,
        topography,
        color_mode=color_mode,
        color_palette=color_palette,
        alpha=alpha,
        draw_edges=draw_edges,
        edge_radius_nm=edge_radius_nm,
        edge_color=edge_color,
        tag_prefix=tag_prefix,
        name=name,
        skip_digestion=skip_digestion,
        tetrahedra_indices=tetrahedra_indices,
        exterior_only=exterior_only,
    )

    group_key = _record_tetrahedra_render_group(runtime, tag_prefix, layer)

    return {
        'addon_enabled': 'topomt' in view.addons.enabled(skip_digestion=True),
        'layer': layer,
        'tag': layer.tag if layer else None,
        'render_group_key': group_key,
    }


def new_view(
    topography,
    *,
    feature_ids=None,
    selection='all',
    structure_indices='all',
    syntax='MolSysMT',
    load_mode='selection',
    view=None,
    enable_addon: bool = True,
    # --- Pocket/feature display ---
    show: bool = True,
    # --- Tetrahedra display ---
    show_tetrahedra: bool = False,
    # --- Tetrahedra options (forwarded to show_dfnd_tetrahedra) ---
    color_mode: str = 'combined_class',
    color_palette: dict[str, int] | None = None,
    alpha: float | dict[str, float] | None = None,
    draw_edges: bool = True,
    edge_radius_nm: float = 0.002,
    edge_color: int = 0x444444,
    exterior_only: bool = False,
    tetrahedra_indices: Iterable[int] | None = None,
    tetra_name: str = 'DFND Tetrahedra',
    skip_digestion: bool = False,
    **render_kwargs,
):
    # Prefer the *original* molecular system the user attached to the topography
    # (``topography.molecular_system``); fall back to the internal ``_molsys``
    # copy. For PDB-derived inputs the copy can fail to render correctly while the
    # original loads fine -- this is also what ``msm.view(molecular_system)`` uses.
    molecular_system = getattr(topography, 'molecular_system', None)
    if molecular_system is None:
        if hasattr(topography, '_molsys'):
            molecular_system = topography._molsys
        else:
            raise ValueError('topography does not expose a molecular_system.')

    register_with_molsysviewer()

    import molsysviewer

    view = molsysviewer.new_view(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        load_mode=load_mode,
        view=view,
        skip_digestion=True,
    )
    attach_topography(
        view,
        topography,
        enable_addon=enable_addon,
        show=show if feature_ids is None else False,
        show_tetrahedra=show_tetrahedra,
        skip_digestion=True,
        color_mode=color_mode,
        color_palette=color_palette,
        alpha=alpha,
        draw_edges=draw_edges,
        edge_radius_nm=edge_radius_nm,
        edge_color=edge_color,
        exterior_only=exterior_only,
        tetrahedra_indices=tetrahedra_indices,
        tetra_name=tetra_name,
        **render_kwargs,
    )
    if feature_ids is not None:
        attach_features(
            view,
            topography,
            feature_ids=feature_ids,
            enable_addon=False,
            show=show,
            skip_digestion=True,
            alpha=alpha,
            **render_kwargs,
        )
    return view
