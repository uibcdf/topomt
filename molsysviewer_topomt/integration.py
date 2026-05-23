from typing import Any
from .render import render_topography_pockets, render_dfnd_tetrahedra
from .runtime import ensure_runtime


def register_with_molsysviewer() -> None:
    """Register the TopoMT addon in the MolSysViewer host registry if needed."""
    import molsysviewer
    if not molsysviewer.addons.contains('topomt'):
        from .addon import get_addon, lifecycle
        molsysviewer.addons.register(get_addon(), lifecycle=lifecycle)


def subset_topography(topography, feature_ids) -> Any:
    """Build a TopoMT subset preserving the original molecular-system reference."""
    import topomt as tmt

    selected_ids = [feature_id for feature_id in feature_ids if feature_id in topography]
    subset = tmt.Topography(
        molecular_system=topography.molecular_system,
        selection=getattr(topography, 'selection', 'all'),
        structure_indices=getattr(topography, 'structure_indices', 0),
    )
    for feature_id in selected_ids:
        subset.add_feature(topography[feature_id].copy(deep=True))
    return subset


def attach_topography(
    view,
    topography,
    *,
    enable_addon: bool = True,
    render: bool = True,
    render_tetrahedra: bool = False,
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
    runtime.topography = topography
    if tag_prefix:
        runtime.tag_prefix = tag_prefix

    rendered = None
    if render:
        # Separate pocket kwargs and tetrahedra kwargs
        pocket_kwargs = {
            k: render_kwargs[k]
            for k in ['color_map', 'alpha', 'marker_color', 'marker_alpha']
            if k in render_kwargs
        }
        rendered = render_topography_pockets(
            view,
            topography,
            tag_prefix=tag_prefix,
            skip_digestion=True,
            **pocket_kwargs,
        )

    rendered_tetrahedra = None
    if render_tetrahedra:
        tetra_alpha = render_kwargs.get('tetra_alpha', render_kwargs.get('alpha', 0.4))
        rendered_tetrahedra = render_dfnd_tetrahedra(
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
        )

    return {
        'addon_enabled': 'topomt' in view.addons.enabled(skip_digestion=True),
        'rendered': rendered,
        'rendered_tetrahedra': rendered_tetrahedra,
        'tag_prefix': tag_prefix,
    }


def attach_features(
    view,
    topography,
    *,
    feature_ids,
    enable_addon: bool = True,
    render: bool = True,
    tag_prefix: str = 'topomt-pocket',
    skip_digestion: bool = False,
    **render_kwargs,
) -> dict[str, Any]:
    """Attach only a selected set of TopoMT features to an existing view."""
    selected_topography = subset_topography(topography, feature_ids)
    result = attach_topography(
        view,
        selected_topography,
        enable_addon=enable_addon,
        render=render,
        tag_prefix=tag_prefix,
        skip_digestion=True,
        **render_kwargs,
    )
    result['selected_feature_ids'] = list(feature_ids)
    return result


def attach_pockets(
    view,
    topography,
    *,
    pocket_ids,
    enable_addon: bool = True,
    render: bool = True,
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
        render=render,
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
) -> dict[str, Any]:
    """Render DFND tetrahedra programmatically into the viewer and enable topomt addon."""
    register_with_molsysviewer()
    if enable_addon:
        view.addons.enable('topomt')
        from .addon import lifecycle
        lifecycle.on_enable(view)

    # Note: store topography on runtime to allow UI synchronization / clear actions
    runtime = ensure_runtime(view)
    runtime.topography = topography

    layer = render_dfnd_tetrahedra(
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
    )

    return {
        'addon_enabled': 'topomt' in view.addons.enabled(skip_digestion=True),
        'layer': layer,
        'tag': layer.tag if layer else None,
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
    render: bool = True,
    render_tetrahedra: bool = False,
    skip_digestion: bool = False,
    **render_kwargs,
):
    if hasattr(topography, '_molsys'):
        molecular_system = topography._molsys
    else:
        raise ValueError("topography does not have a '_molsys' attribute.")

    register_with_molsysviewer()

    if feature_ids is not None:
        topography = subset_topography(topography, feature_ids)

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
        render=render,
        render_tetrahedra=render_tetrahedra,
        skip_digestion=True,
        **render_kwargs,
    )
    return view



