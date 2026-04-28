"""MolSysViewer addon for TopoMT — topography and pocket analysis."""

from .addon import ADDON, addon, get_addon, lifecycle
from .integration import (
    attach_features,
    attach_pockets,
    attach_topography,
    build_view_with_topography,
    register_with_molsysviewer,
    subset_topography,
)
from .panels import TopoMTTopographyPanel, TopoMTPocketsPanel
from .payloads import feature_record_from_feature, topography_payload
from .render import render_topography_pockets
from .runtime import TopoMTAddonRuntime, ensure_runtime, record_event
from .standalone import build_topography_standalone0_html, launch_topography_standalone0

__all__ = [
    "ADDON",
    "addon",
    "get_addon",
    "lifecycle",
    "register_with_molsysviewer",
    "subset_topography",
    "attach_features",
    "attach_pockets",
    "attach_topography",
    "build_view_with_topography",
    "TopoMTTopographyPanel",
    "TopoMTPocketsPanel",
    "TopoMTAddonRuntime",
    "ensure_runtime",
    "record_event",
    "feature_record_from_feature",
    "topography_payload",
    "render_topography_pockets",
    "build_topography_standalone0_html",
    "launch_topography_standalone0",
]
