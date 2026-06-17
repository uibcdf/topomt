"""show_dfnd_tetrahedra: Delaunay tetrahedra / face rendering."""

from collections.abc import Iterable
from functools import wraps
from inspect import signature
from typing import Any

from topomt import pyunitwizard as puw

from ..geometry import tetrahedra_geometry
from ._common import (
    _angstrom_label_from_nm,
    _dfnd_edge_meta,
    _dfnd_face_meta,
    _resolve_topography,
)
from .adapters import add_tetrahedra
from .result import (
    RenderResult,
    clear_previous_render_result,
    remember_render_result,
    render_result,
)


def _show_dfnd_tetrahedra_legacy(
    view,
    topography=None,
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
    tetrahedra_indices: Iterable[int] | None = None,
    exterior_only: bool = False,
    draw_faces: bool = True,
    permeable_faces: bool = True,
    non_permeable_faces: bool = True,
) -> Any:
    """Render DFND Delaunay tetrahedra into the viewer canvas.

    Faces are coloured by permeability and individually pickable. Hover labels
    carry the face id, both owning tetrahedra and permeability state.

    Face filters:
    - ``permeable_faces`` / ``non_permeable_faces``: hide one class of faces.
    - ``exterior_only=True``: keep only faces on the boundary of the selected
      tetrahedra set (faces shared by two selected tetrahedra are dropped).
      Default ``False`` -- show every unique face.

    With ``draw_faces=False`` only the tetrahedron *edges* are drawn (a wireframe
    of every selected tetrahedron, no coloured faces) as cylinders in
    ``edge_color``. Bump ``edge_radius_nm`` so the wireframe is visible
    (e.g. 0.02-0.05).
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError(
            'topography is required (pass it explicitly or attach via attach_topography(view, topography))'
        )
    if getattr(topography, 'dfnd', None) is not None:
        raw_records = topography.dfnd.raw
    elif isinstance(topography, dict):
        if 'raw' in topography:
            raw_records = topography['raw']
        else:
            raw_records = topography
    else:
        raise ValueError(
            'topography must be a Topography object or a dictionary from dfnd'
        )

    tetrahedra = raw_records.get('tetrahedra', [])
    if not tetrahedra:
        return None

    if tetrahedra_indices is not None:
        tetrahedra_indices_set = set(tetrahedra_indices)
        tetrahedra = [
            tet
            for idx, tet in enumerate(tetrahedra)
            if tet.get('tetrahedron_id', idx) in tetrahedra_indices_set
        ]
        if not tetrahedra:
            return None

    default_palettes = {
        'combined_class': {
            'wet_sealed': 0x14B8A6,  # Turquesa / Verde-Azul (isolated habitable cavity)
            'wet_open': 0x3B82F6,  # Celeste / Azul brillante (open habitable channel)
            'wet_coast': 0x8B5CF6,  # Púrpura / Violeta (boundary habitable water)
            'dry_sealed': 0x334155,  # Gris Pizarra Oscuro (core protein body background)
            'dry_open': 0x64748B,  # Gris Claro / Humo (dry non-habitable open areas)
            'dry_coast': 0xF97316,  # Naranja Coral / Salmón (contact active boundary lining)
        },
        'transit_role': {
            'resident_transit': 0x6366F1,  # Indigo
            'transit_connector': 0xF97316,  # Orange
            'terminal_contact': 0xF59E0B,  # Amber/Gold
            'non_transit': 0x475569,  # Slate/Steel
        },
        'residence_state': {
            'resident': 0x3B82F6,  # Electric Soft Blue
            'non_resident': 0x64748B,  # Soft Cool Slate
        },
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
        },
    }

    palette = default_palettes.get(
        color_mode, default_palettes['combined_class']
    ).copy()
    if color_palette:
        palette.update(color_palette)

    # Resolve alpha dictionary if not explicitly a single float
    if alpha is None:
        alpha_resolved = default_alphas.get(
            color_mode, default_alphas['combined_class']
        )
    elif isinstance(alpha, dict):
        alpha_resolved = alpha
    else:
        alpha_resolved = None  # Single float value to be used directly

    colors = []
    alphas = []
    labels = []
    selected_tetra_ids = set()
    selected_tetra_order = []

    for idx, tet in enumerate(tetrahedra):
        quad = tet.get('local_atom_indices')
        if not quad or len(quad) != 4:
            continue
        tetrahedron_id = tet.get('tetrahedron_id', idx)
        selected_tetra_ids.add(tetrahedron_id)
        selected_tetra_order.append(tetrahedron_id)

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
            f'Tetrahedron {tet.get("tetrahedron_id", idx)}: '
            f'combined_class={tet.get("combined_class", "unknown")}, '
            f'role={tet.get("transit_role", "unknown")}, '
            f'R_res={_angstrom_label_from_nm(tet.get("R_residence", 0.0))}'
        )
        labels.append(lbl)

    geometry = tetrahedra_geometry(topography, selected_tetra_order)
    if not geometry.atom_quads:
        return None

    # Disabling both permeability classes is the same as draw_faces=False.
    if not permeable_faces and not non_permeable_faces:
        draw_faces = False

    # Edges-only mode: the frontend skips face triangles and only draws the
    # edge cylinders.
    if not draw_faces:
        draw_edges = True

    # Faces are individually pickable (one group per unique face) and carry a face
    # label (id, permeability, both owning tetrahedra). The metadata is keyed by the
    # face's local atom-triple so the frontend can build the rich label and colour
    # each face by PERMEABILITY (the tetrahedron's own nature lives in the DFN graph
    # view, not the faces). Faces shared by two tetrahedra are a single pick group.
    # When the metadata only covers a subset of faces, the frontend treats it as a
    # visibility filter and hides faces not listed -- this is how permeable_faces /
    # non_permeable_faces actually take effect at render time.
    allowed_permeability = set()
    if permeable_faces:
        allowed_permeability.add('permeable')
    if non_permeable_faces:
        allowed_permeability.add('non_permeable')

    face_meta = []
    if draw_faces and allowed_permeability:
        face_meta = _dfnd_face_meta(
            topography,
            selected_tetra_ids,
            permeability_states=allowed_permeability,
        )

    # Clear existing tetrahedra layer if it exists to allow clean overwriting / re-runs
    try:
        view.shapes.clear(tag=tag_prefix, skip_digestion=True)
    except Exception:
        pass

    layer = add_tetrahedra(
        view,
        geometry,
        colors=colors,
        alphas=alphas,
        labels=labels,
        draw_faces=draw_faces,
        faces_pickable=draw_faces,
        face_meta=face_meta or None,
        draw_edges=draw_edges,
        edge_meta=(_dfnd_edge_meta(topography, selected_tetra_ids) or None)
        if draw_edges
        else None,
        edge_radius=puw.quantity(edge_radius_nm, 'nm'),
        edge_color=edge_color,
        tag=tag_prefix,
        layer_tag=tag_prefix,
        name=name,
        skip_digestion=skip_digestion,
        exterior_only=exterior_only,
    )

    return layer


# Node-class colors (combined_class), shared with render_dfnd_tetrahedra.


@wraps(_show_dfnd_tetrahedra_legacy)
def show_dfnd_tetrahedra(view, topography=None, **kwargs):
    """Render tetrahedra and return a uniform ``RenderResult``."""
    resolved = _resolve_topography(view, topography)
    operation_key = f'tetrahedra:{kwargs.get("tag_prefix", "dfnd-tetra")}'
    clear_previous_render_result(view, operation_key)
    raw = _show_dfnd_tetrahedra_legacy(view, resolved, **kwargs)
    selected_ids = kwargs.get('tetrahedra_indices')
    if selected_ids is None:
        if getattr(resolved, 'dfnd', None) is not None:
            records = resolved.dfnd.raw.get('tetrahedra', [])
        elif isinstance(resolved, dict):
            records = resolved.get('raw', resolved).get('tetrahedra', [])
        else:
            records = []
        selected_ids = tuple(
            record.get('tetrahedron_id', index)
            for index, record in enumerate(records)
            if len(record.get('local_atom_indices', ())) == 4
        )
    result = render_result('tetrahedra', raw, selected_ids=selected_ids)
    return remember_render_result(view, operation_key, result)


show_dfnd_tetrahedra.__signature__ = signature(_show_dfnd_tetrahedra_legacy).replace(
    return_annotation=RenderResult
)
show_dfnd_tetrahedra.__annotations__['return'] = RenderResult
