"""Workbench entry points for the initial TopoMT addon."""

from __future__ import annotations

from typing import Any

from .payloads import topography_payload


def topography_summary(view=None, topography=None, **kwargs) -> dict[str, Any]:
    """Return a small summary payload suitable for a future workbench section."""
    payload = topography_payload(topography) if topography is not None else {'n_features': 0, 'feature_counts': {}, 'features': []}
    return {
        'section': 'topography-summary',
        'addon': 'topomt',
        'has_view': view is not None,
        'summary': {
            'n_features': payload['n_features'],
            'feature_counts': payload['feature_counts'],
        },
        'options': dict(kwargs),
    }
