"""Python-side rendering helpers for the first TopoMT MolSysViewer addon slice."""

import math
from typing import Any

from topomt import pyunitwizard as puw

from .payloads import topography_payload

DEFAULT_BLOB_ALPHA = 0.35
DEFAULT_MARKER_ALPHA = 0.55
DEFAULT_MARKER_COLOR = 0xD95F02
DEFAULT_MARKER_RADIUS_NM = 0.12


def _marker_radius_from_feature(feature_record: dict[str, Any]) -> float:
    volume = feature_record.get('volume')
    if isinstance(volume, (int, float)) and volume > 0:
        return max(
            DEFAULT_MARKER_RADIUS_NM,
            float(((3.0 * float(volume)) / (4.0 * math.pi)) ** (1.0 / 3.0)),
        )
    return DEFAULT_MARKER_RADIUS_NM


def render_topography_pockets(
    view,
    topography,
    *,
    tag_prefix: str = 'topomt-pocket',
    color_map: str = 'viridis',
    alpha: float = DEFAULT_BLOB_ALPHA,
    marker_color: int = DEFAULT_MARKER_COLOR,
    marker_alpha: float = DEFAULT_MARKER_ALPHA,
    skip_digestion: bool = False,
) -> dict[str, Any]:
    """Render current TopoMT pocket features into an existing MolSysViewer view.

    Pockets with `sphere_centers` and `sphere_radii` are rendered as pocket blobs.
    Pockets that only expose a `center` fall back to a marker sphere.
    """
    payload = topography_payload(topography)
    rendered: list[dict[str, Any]] = []

    for feature in payload['features']:
        if feature.get('feature_type') != 'pocket':
            continue

        feature_id = feature.get('feature_id') or f'{tag_prefix}-unknown'
        tag = f'{tag_prefix}:{feature_id}'
        sphere_centers = feature.get('sphere_centers')
        sphere_radii = feature.get('sphere_radii')
        center = feature.get('center')

        if sphere_centers and sphere_radii:
            n_spheres = len(sphere_centers)
            score = feature.get('score')
            values = None
            if isinstance(score, (int, float)):
                values = [float(score)] * n_spheres
            layer = view.shapes.add_pocket_blob(
                centers=puw.quantity(sphere_centers, 'nm'),
                radii=puw.quantity(sphere_radii, 'nm'),
                values=values,
                color_map=color_map,
                alpha=alpha,
                tag=tag,
                name=str(feature_id),
                skip_digestion=True,
            )
            rendered.append({'feature_id': feature_id, 'tag': tag, 'mode': 'blob', 'layer': layer})
            continue

        if center is not None:
            layer = view.shapes.add_sphere(
                center=puw.quantity(center, 'nm'),
                radius=puw.quantity(_marker_radius_from_feature(feature), 'nm'),
                color=marker_color,
                alpha=marker_alpha,
                tag=tag,
                skip_digestion=True,
            )
            rendered.append({'feature_id': feature_id, 'tag': tag, 'mode': 'marker', 'layer': layer})

    return {
        'n_rendered': len(rendered),
        'rendered': rendered,
        'feature_counts': payload['feature_counts'],
    }
