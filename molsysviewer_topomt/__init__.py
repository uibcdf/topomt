"""MolSysViewer addon scaffold for TopoMT."""

from .addon import ADDON, addon, get_addon, lifecycle
from .integration import (
    attach_features,
    attach_pockets,
    attach_topography,
    build_view_with_topography,
    register_with_molsysviewer,
    subset_topography,
)
from .payloads import feature_record_from_feature, topography_payload
from .render import render_topography_pockets
from .standalone import build_topography_standalone0_html, launch_topography_standalone0

__all__ = [
    'ADDON',
    'addon',
    'get_addon',
    'lifecycle',
    'register_with_molsysviewer',
    'subset_topography',
    'attach_features',
    'attach_pockets',
    'attach_topography',
    'build_view_with_topography',
    'feature_record_from_feature',
    'topography_payload',
    'render_topography_pockets',
    'build_topography_standalone0_html',
    'launch_topography_standalone0',
]
