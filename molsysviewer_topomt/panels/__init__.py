from .topography import TopoMTTopographyPanel
from .pockets import TopoMTPocketsPanel

# Keep legacy entry-point functions for any existing callers
from ..payloads import topography_payload as _topography_payload


def topography_panel(view=None, topography=None, **kwargs):
    payload = _topography_payload(topography) if topography is not None else None
    return {
        "panel": "topography",
        "addon": "topomt",
        "has_view": view is not None,
        "payload": payload,
        "options": dict(kwargs),
    }


def pockets_panel(view=None, topography=None, **kwargs):
    payload = _topography_payload(topography) if topography is not None else None
    return {
        "panel": "pockets",
        "addon": "topomt",
        "has_view": view is not None,
        "payload": payload,
        "options": dict(kwargs),
    }


__all__ = [
    "TopoMTTopographyPanel",
    "TopoMTPocketsPanel",
    "topography_panel",
    "pockets_panel",
]
