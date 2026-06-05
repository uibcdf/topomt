"""Shape-provider entry points for the first TopoMT addon slice."""

from __future__ import annotations

from typing import Any

from .payloads import topography_payload
from .render import show_topography_pockets


def pocket_blob_provider(view=None, topography=None, **kwargs) -> dict[str, Any]:
    """Render pockets when a view is available, otherwise expose the normalized payload."""
    payload = topography_payload(topography) if topography is not None else {'n_features': 0, 'feature_counts': {}, 'features': []}
    rendered = None
    if view is not None and topography is not None:
        rendered = show_topography_pockets(view, topography, **kwargs)
    return {
        'provider': 'topography-pocket-blob',
        'addon': 'topomt',
        'has_view': view is not None,
        'payload': payload,
        'rendered': rendered,
        'options': dict(kwargs),
    }
