"""Context-action placeholders for the initial TopoMT addon."""

from __future__ import annotations


def focus_topography_feature(view=None, payload=None):
    """Return a normalized description of the requested action."""
    return {
        'action': 'focus-topography-feature',
        'has_view': view is not None,
        'payload': {} if payload is None else dict(payload),
    }
