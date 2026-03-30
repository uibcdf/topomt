"""Convenience integration helpers between TopoMT and MolSysViewer."""

import copy
from typing import Any

import molsysviewer

from .addon import get_addon, lifecycle
from .render import render_topography_pockets


def _clone_feature_preserving_state(feature):
    """Clone a TopoMT feature preserving dynamic render-relevant attributes."""
    cloned_feature = feature.__class__.__new__(feature.__class__)
    cloned_feature.__dict__ = copy.deepcopy(feature.__dict__)
    cloned_feature._topography = None
    return cloned_feature


def register_with_molsysviewer() -> None:
    """Register the TopoMT addon in the MolSysViewer host registry if needed."""
    if not molsysviewer.addons.contains('topomt'):
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
        subset.add_feature(_clone_feature_preserving_state(topography[feature_id]))
    return subset


def attach_topography(
    view,
    topography,
    *,
    enable_addon: bool = True,
    render: bool = True,
    tag_prefix: str = 'topomt-pocket',
    skip_digestion: bool = False,
    **render_kwargs,
) -> dict[str, Any]:
    """Attach a TopoMT topography to an existing MolSysViewer view."""
    register_with_molsysviewer()
    if enable_addon:
        view.addons.enable('topomt')
        lifecycle.on_enable(view)

    rendered = None
    if render:
        rendered = render_topography_pockets(
            view,
            topography,
            tag_prefix=tag_prefix,
            skip_digestion=True,
            **render_kwargs,
        )

    return {
        'addon_enabled': 'topomt' in view.addons.enabled(skip_digestion=True),
        'rendered': rendered,
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


def build_view_with_topography(
    molecular_system,
    topography,
    *,
    selection='all',
    structure_indices='all',
    syntax='MolSysMT',
    load_mode='selection',
    view=None,
    enable_addon: bool = True,
    render: bool = True,
    skip_digestion: bool = False,
    **render_kwargs,
):
    """Create or reuse a view, load a molecular system, and overlay a TopoMT topography."""
    register_with_molsysviewer()
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
        skip_digestion=True,
        **render_kwargs,
    )
    return view
