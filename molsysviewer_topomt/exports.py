"""Export-helper placeholders for the initial TopoMT addon."""

from __future__ import annotations

from typing import Any

from .payloads import topography_payload


def export_topography_summary(view=None, topography=None, format='json', **kwargs) -> dict[str, Any]:
    """Return a normalized export record for future viewer exports."""
    payload = topography_payload(topography) if topography is not None else {'n_features': 0, 'feature_counts': {}, 'features': []}
    return {
        'helper': 'topography-summary-export',
        'addon': 'topomt',
        'format': format,
        'has_view': view is not None,
        'payload': payload,
        'options': dict(kwargs),
    }
