"""MolSysViewer addon for TopoMT — topography and pocket analysis."""

_in_getattr = False


def __getattr__(name: str):
    global _in_getattr
    if _in_getattr:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    if name in (
        'ADDON',
        'addon',
        'get_addon',
        'lifecycle',
        'on_enable',
        'on_disable',
        'on_context_action',
    ):
        _in_getattr = True
        try:
            import importlib

            addon_mod = importlib.import_module('molsysviewer_topomt.addon')
            globals()['addon'] = getattr(addon_mod, 'addon')
            globals()['ADDON'] = getattr(addon_mod, 'ADDON')
            globals()['get_addon'] = getattr(addon_mod, 'get_addon')
            globals()['lifecycle'] = getattr(addon_mod, 'lifecycle')
            globals()['on_enable'] = getattr(addon_mod, 'on_enable')
            globals()['on_disable'] = getattr(addon_mod, 'on_disable')
            globals()['on_context_action'] = getattr(addon_mod, 'on_context_action')
            return getattr(addon_mod, name)
        finally:
            _in_getattr = False

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


from .integration import (
    attach_dfnd_tetrahedra,
    attach_features,
    attach_pockets,
    attach_topography,
    clear_render_group,
    new_view,
    register_with_molsysviewer,
    subset_topography,
)
from .panels import TopoMTPocketsPanel, TopoMTTopographyPanel
from .payloads import feature_record_from_feature, topography_payload
from .render import (
    RenderResult,
    clear_feature_representations,
    hide_feature_representations,
    show_affinity,
    show_dfn_graph,
    show_dfnd_components,
    show_dfnd_convexity,
    show_dfnd_interface_cutaway,
    show_dfnd_legend,
    show_dfnd_peak_patches,
    show_dfnd_pharmacophore,
    show_dfnd_pocket_cutaway,
    show_dfnd_ridge_lines,
    show_dfnd_spikes,
    show_dfnd_tetrahedra,
    show_feature_representations,
    show_features,
    show_pharmacophore,
    show_topography_pockets,
)
from .runtime import TopoMTAddonRuntime, ensure_runtime, record_event
from .simplex_selection import simplex_selection_info
from .standalone import build_topography_standalone0_html, launch_topography_standalone0

__all__ = [
    'ADDON',
    'addon',
    'get_addon',
    'lifecycle',
    'on_enable',
    'on_disable',
    'on_context_action',
    'register_with_molsysviewer',
    'subset_topography',
    'attach_features',
    'attach_pockets',
    'attach_topography',
    'clear_render_group',
    'attach_dfnd_tetrahedra',
    'new_view',
    'TopoMTTopographyPanel',
    'TopoMTPocketsPanel',
    'TopoMTAddonRuntime',
    'ensure_runtime',
    'record_event',
    'feature_record_from_feature',
    'topography_payload',
    'RenderResult',
    'show_features',
    'clear_feature_representations',
    'hide_feature_representations',
    'show_feature_representations',
    'show_pharmacophore',
    'show_affinity',
    'show_topography_pockets',
    'show_dfnd_tetrahedra',
    'show_dfn_graph',
    'show_dfnd_components',
    'show_dfnd_convexity',
    'show_dfnd_interface_cutaway',
    'show_dfnd_legend',
    'show_dfnd_pocket_cutaway',
    'show_dfnd_peak_patches',
    'show_dfnd_pharmacophore',
    'show_dfnd_ridge_lines',
    'show_dfnd_spikes',
    'simplex_selection_info',
    'build_topography_standalone0_html',
    'launch_topography_standalone0',
]
