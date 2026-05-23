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


def render_dfnd_tetrahedra(
    view,
    topography,
    *,
    color_mode: str = 'combined_class',
    color_palette: dict[str, int] | None = None,
    alpha: float | dict[str, float] | None = None,
    draw_edges: bool = True,
    edge_radius_nm: float = 0.002,
    edge_color: int = 0x444444,
    tag_prefix: str = 'dfnd-tetra',
    name: str = 'DFND Tetrahedra',
    skip_digestion: bool = False,
) -> Any:
    """Render DFND Delaunay tetrahedra into the viewer canvas.

    Delaunay tetrahedra are rendered as a custom triangle mesh color-coded by their
    DFND classification. Custom hover labels (tooltips) are attached for interactive
    diagnostics.
    """
    if getattr(topography, 'dfnd', None) is not None:
        raw_records = topography.dfnd.raw
    elif isinstance(topography, dict):
        if 'raw' in topography:
            raw_records = topography['raw']
        else:
            raw_records = topography
    else:
        raise ValueError("topography must be a Topography object or a dictionary from dfnd")

    tetrahedra = raw_records.get('tetrahedra', [])
    if not tetrahedra:
        return None

    default_palettes = {
        'combined_class': {
            'wet_sealed': 0x14B8A6,    # Turquesa / Verde-Azul (isolated habitable cavity)
            'wet_open': 0x3B82F6,      # Celeste / Azul brillante (open habitable channel)
            'wet_coast': 0x8B5CF6,     # Púrpura / Violeta (boundary habitable water)
            'dry_sealed': 0x334155,    # Gris Pizarra Oscuro (core protein body background)
            'dry_open': 0x64748B,      # Gris Claro / Humo (dry non-habitable open areas)
            'dry_coast': 0xF97316,     # Naranja Coral / Salmón (contact active boundary lining)
        },
        'transit_role': {
            'resident_transit': 0x6366F1,     # Indigo
            'transit_connector': 0xF97316,    # Orange
            'terminal_contact': 0xF59E0B,     # Amber/Gold
            'non_transit': 0x475569,          # Slate/Steel
        },
        'residence_state': {
            'resident': 0x3B82F6,      # Electric Soft Blue
            'non_resident': 0x64748B,  # Soft Cool Slate
        }
    }

    default_alphas = {
        'combined_class': {
            'wet_sealed': 0.5,
            'wet_open': 0.5,
            'wet_coast': 0.5,
            'dry_sealed': 0.05,
            'dry_open': 0.1,
            'dry_coast': 0.4,
        },
        'transit_role': {
            'resident_transit': 0.5,
            'transit_connector': 0.5,
            'terminal_contact': 0.4,
            'non_transit': 0.05,
        },
        'residence_state': {
            'resident': 0.5,
            'non_resident': 0.1,
        }
    }

    palette = default_palettes.get(color_mode, default_palettes['combined_class']).copy()
    if color_palette:
        palette.update(color_palette)

    # Resolve alpha dictionary if not explicitly a single float
    if alpha is None:
        alpha_resolved = default_alphas.get(color_mode, default_alphas['combined_class'])
    elif isinstance(alpha, dict):
        alpha_resolved = alpha
    else:
        alpha_resolved = None  # Single float value to be used directly

    atom_quads = []
    colors = []
    alphas = []
    labels = []

    for idx, tet in enumerate(tetrahedra):
        quad = tet.get('local_atom_indices')
        if not quad or len(quad) != 4:
            continue
        atom_quads.append(quad)

        # Retrieve value based on selected color mode
        if color_mode == 'combined_class':
            val = tet.get('combined_class', '')
        elif color_mode == 'transit_role':
            val = tet.get('transit_role', '')
        elif color_mode == 'residence_state':
            val = tet.get('residence_state', '')
        else:
            val = tet.get('combined_class', '')

        # Resolve color from palette
        color = palette.get(val, 0x888888)  # Fallback to grey
        colors.append(color)

        # Resolve alpha
        if alpha_resolved is not None:
            alphas.append(alpha_resolved.get(val, 0.4))
        else:
            alphas.append(alpha)

        # Generate descriptive hover label
        lbl = (
            f"Tetrahedron {tet.get('tetrahedron_id', idx)}: "
            f"combined_class={tet.get('combined_class', 'unknown')}, "
            f"role={tet.get('transit_role', 'unknown')}, "
            f"R_res={tet.get('R_residence', 0.0):.2f} Å"
        )
        labels.append(lbl)

    if not atom_quads:
        return None

    # Clear existing tetrahedra layer if it exists to allow clean overwriting / re-runs
    try:
        view.shapes.clear(tag=tag_prefix, skip_digestion=True)
    except Exception:
        pass

    # Call view.shapes.add_tetrahedra directly
    layer = view.shapes.add_tetrahedra(
        atom_quads=atom_quads,
        colors=colors,
        alphas=alphas,
        labels=labels,
        draw_edges=draw_edges,
        edge_radius=puw.quantity(edge_radius_nm, 'nm'),
        edge_color=edge_color,
        tag=tag_prefix,
        layer_tag=tag_prefix,
        name=name,
        skip_digestion=skip_digestion,
    )

    return layer

