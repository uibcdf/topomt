"""show_topography_pockets: per-feature pocket markers/surfaces."""

import math
from typing import Any

from topomt import pyunitwizard as puw

from ..payloads import topography_payload
from ._common import (
    DEFAULT_BLOB_ALPHA,
    DEFAULT_MARKER_ALPHA,
    DEFAULT_MARKER_COLOR,
    DEFAULT_MARKER_RADIUS_NM,
    _resolve_topography,
)
from .result import RenderResult, clear_previous_render_result, remember_render_result


def _marker_radius_from_feature(feature_record: dict[str, Any]) -> float:
    volume = feature_record.get('volume')
    if isinstance(volume, (int, float)) and volume > 0:
        return max(
            DEFAULT_MARKER_RADIUS_NM,
            float(((3.0 * float(volume)) / (4.0 * math.pi)) ** (1.0 / 3.0)),
        )
    return DEFAULT_MARKER_RADIUS_NM


def show_topography_pockets(
    view,
    topography=None,
    *,
    feature_ids=None,
    tag_prefix: str = 'topomt-pocket',
    color_map: str = 'viridis',
    alpha: float = DEFAULT_BLOB_ALPHA,
    marker_color: int = DEFAULT_MARKER_COLOR,
    marker_alpha: float = DEFAULT_MARKER_ALPHA,
    skip_digestion: bool = False,
) -> RenderResult:
    """Render current TopoMT pocket features into an existing MolSysViewer view.

    Pockets with `sphere_centers` and `sphere_radii` are rendered as pocket blobs.
    Pockets that only expose a `center` fall back to a marker sphere.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError(
            'topography is required (pass it explicitly or attach via attach_topography(view, topography))'
        )
    operation_key = f'pockets:{tag_prefix}'
    clear_previous_render_result(view, operation_key)
    payload = topography_payload(topography)
    selected_ids = (
        None if feature_ids is None else {str(value) for value in feature_ids}
    )
    rendered: list[dict[str, Any]] = []

    for feature in payload['features']:
        if selected_ids is not None and feature.get('feature_id') not in selected_ids:
            continue
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
            rendered.append(
                {'feature_id': feature_id, 'tag': tag, 'mode': 'blob', 'layer': layer}
            )
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
            rendered.append(
                {'feature_id': feature_id, 'tag': tag, 'mode': 'marker', 'layer': layer}
            )

    return remember_render_result(
        view,
        operation_key,
        RenderResult(
            representation='pockets',
            selected_ids=tuple(item['feature_id'] for item in rendered),
            layers=tuple(item['layer'] for item in rendered),
            tags=tuple(item['tag'] for item in rendered),
            counts={'n_rendered': len(rendered)},
            details={'rendered': rendered, 'feature_counts': payload['feature_counts']},
        ),
    )
