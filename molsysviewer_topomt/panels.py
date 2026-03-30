"""Minimal panel entry points for the first TopoMT addon slice."""

from __future__ import annotations

from typing import Any

from .payloads import topography_payload


def topography_panel(view=None, topography=None, **kwargs) -> dict[str, Any]:
    """Return a minimal runtime snapshot for the main TopoMT panel."""
    payload = topography_payload(topography) if topography is not None else None
    return {
        'panel': 'topography',
        'addon': 'topomt',
        'has_view': view is not None,
        'payload': payload,
        'options': dict(kwargs),
    }


def pockets_panel(view=None, topography=None, **kwargs) -> dict[str, Any]:
    """Return a minimal runtime snapshot for the pocket panel."""
    payload = topography_payload(topography) if topography is not None else None
    return {
        'panel': 'pockets',
        'addon': 'topomt',
        'has_view': view is not None,
        'payload': payload,
        'options': dict(kwargs),
    }
