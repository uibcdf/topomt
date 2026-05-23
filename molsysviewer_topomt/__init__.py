"""MolSysViewer addon for TopoMT — topography and pocket analysis."""

_in_getattr = False


def __getattr__(name: str):
    global _in_getattr
    if _in_getattr:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    if name in (
        "ADDON",
        "addon",
        "get_addon",
        "lifecycle",
        "on_enable",
        "on_disable",
        "on_context_action",
    ):
        _in_getattr = True
        try:
            import importlib
            addon_mod = importlib.import_module("molsysviewer_topomt.addon")
            globals()["addon"] = getattr(addon_mod, "addon")
            globals()["ADDON"] = getattr(addon_mod, "ADDON")
            globals()["get_addon"] = getattr(addon_mod, "get_addon")
            globals()["lifecycle"] = getattr(addon_mod, "lifecycle")
            globals()["on_enable"] = getattr(addon_mod, "on_enable")
            globals()["on_disable"] = getattr(addon_mod, "on_disable")
            globals()["on_context_action"] = getattr(addon_mod, "on_context_action")
            return getattr(addon_mod, name)
        finally:
            _in_getattr = False

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


from .integration import (
    attach_features,
    attach_pockets,
    attach_topography,
    new_view,
    register_with_molsysviewer,
    subset_topography,
    attach_dfnd_tetrahedra,
)
from .panels import TopoMTTopographyPanel, TopoMTPocketsPanel
from .payloads import feature_record_from_feature, topography_payload
from .render import render_topography_pockets, render_dfnd_tetrahedra
from .runtime import TopoMTAddonRuntime, ensure_runtime, record_event
from .standalone import build_topography_standalone0_html, launch_topography_standalone0

__all__ = [
    "ADDON",
    "addon",
    "get_addon",
    "lifecycle",
    "on_enable",
    "on_disable",
    "on_context_action",
    "register_with_molsysviewer",
    "subset_topography",
    "attach_features",
    "attach_pockets",
    "attach_topography",
    "attach_dfnd_tetrahedra",
    "new_view",
    "TopoMTTopographyPanel",
    "TopoMTPocketsPanel",
    "TopoMTAddonRuntime",
    "ensure_runtime",
    "record_event",
    "feature_record_from_feature",
    "topography_payload",
    "render_topography_pockets",
    "render_dfnd_tetrahedra",
    "build_topography_standalone0_html",
    "launch_topography_standalone0",
]
