"""Viewer-oriented payload adapters for current TopoMT objects."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np


def _tolist_or_none(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return list(value)
    return value


def feature_record_from_feature(feature: Any) -> dict[str, Any]:
    """Normalize a current TopoMT feature into a viewer-facing record."""
    record = {
        'feature_id': getattr(feature, 'feature_id', None),
        'feature_type': getattr(feature, 'feature_type', None),
        'shape_type': getattr(feature, 'shape_type', None),
        'source': getattr(feature, 'source', None),
        'source_id': getattr(feature, 'source_id', None),
        'atom_indices': _tolist_or_none(getattr(feature, 'atom_indices', None)) or [],
        'center': _tolist_or_none(getattr(feature, 'center', None)),
        'volume': getattr(feature, 'volume', None),
        'score': getattr(feature, 'score', None),
        'sphere_centers': _tolist_or_none(getattr(feature, 'alpha_sphere_centers', None)),
        'sphere_radii': _tolist_or_none(getattr(feature, 'alpha_sphere_radii', None)),
        'mouth_atom_indices': _tolist_or_none(getattr(feature, 'mouth_atom_indices', None)),
    }
    return record


def topography_payload(topography: Any) -> dict[str, Any]:
    """Normalize a TopoMT topography into a minimal addon payload."""
    if not isinstance(topography, Mapping):
        raise TypeError('topography_payload expects a Topography-like mapping of features.')

    features = [feature_record_from_feature(feature) for feature in topography.values()]
    by_type: dict[str, int] = {}
    for item in features:
        feature_type = item.get('feature_type')
        if not isinstance(feature_type, str):
            continue
        by_type[feature_type] = by_type.get(feature_type, 0) + 1

    return {
        'n_features': len(features),
        'feature_counts': by_type,
        'features': features,
    }
