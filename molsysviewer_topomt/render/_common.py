"""Shared helpers for the TopoMT viewer render package."""

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt.dfnd.selectors import select_faces

from ..geometry import edge_geometry, entity_ref_payload, face_geometry

DEFAULT_BLOB_ALPHA = 0.35
DEFAULT_MARKER_ALPHA = 0.55
DEFAULT_MARKER_COLOR = 0xD95F02
DEFAULT_MARKER_RADIUS_NM = 0.12


def _angstrom_from_nm(value):
    return float(value) * puw.conversion_factor('nm', 'angstroms')


def _angstrom2_from_nm2(value):
    return float(value) * puw.conversion_factor('nm', 'angstroms') ** 2


def _angstrom3_from_nm3(value):
    return float(value) * puw.conversion_factor('nm', 'angstroms') ** 3


def _angstrom_label_from_nm(value, digits=2):
    if isinstance(value, (int, float)):
        return f'{_angstrom_from_nm(value):.{digits}f} Å'
    return 'unknown'


_FACE_PERMEABILITY_COLORS = {
    'permeable': 0x93C5FD,
    'non_permeable': 0xE3C98A,
}

_FACE_ROLE_COLORS = {
    'transit_face': 0x0072B2,
    'blocked_face': 0xD55E00,
    'mouth_face': 0x009E73,
    'boundary_face': 0xCC79A7,
    'coast_face': 0xE69F00,
    'unknown_face': 0x888888,
}


def _raw_records(source: Any) -> dict[str, Any]:
    if getattr(source, 'dfnd', None) is not None:
        return source.dfnd.raw
    if isinstance(source, dict):
        return source.get('raw', source)
    raw = getattr(source, 'raw', None)
    return raw if isinstance(raw, dict) else {}


def _probe_radius_nm(raw: dict[str, Any]) -> float | None:
    parameters = raw.get('parameters', {})
    value = parameters.get('probe_radius')
    if value is None and isinstance(parameters.get('query'), dict):
        value = parameters['query'].get('probe_radius')
    if value is None:
        return None
    if puw.is_quantity(value):
        return float(puw.get_value(value, to_unit='nm'))
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _tetrahedron_side(record: dict[str, Any] | None) -> str:
    if not record:
        return 'unknown'
    combined_class = str(record.get('combined_class', ''))
    if combined_class.startswith('wet_'):
        return 'wet'
    if combined_class.startswith('dry_'):
        return 'dry'
    residence_state = str(record.get('residence_state', ''))
    if residence_state == 'resident':
        return 'wet'
    if residence_state == 'non_resident':
        return 'dry'
    return 'unknown'


def _face_role(face: dict[str, Any], owner_side: str, neighbor_side: str) -> str:
    permeability = face.get('permeability_state', 'unknown')
    neighbor = face.get('neighbor_tetrahedron_id', -1)
    if {owner_side, neighbor_side} == {'wet', 'dry'}:
        return 'coast_face'
    if neighbor == -1:
        if permeability == 'permeable':
            return 'mouth_face'
        return 'boundary_face'
    if permeability == 'permeable':
        return 'transit_face'
    if permeability == 'non_permeable':
        return 'blocked_face'
    return 'unknown_face'


def _gate_margin_color(gate_margin: float | None) -> int:
    if gate_margin is None:
        return 0x888888
    if gate_margin < 0.0:
        return 0xD55E00
    if gate_margin <= 0.02:
        return 0xE69F00
    return 0x0072B2


def _face_component_ids(
    face: dict[str, Any],
    owner: int | None,
    neighbor: int | None,
    components_by_tetrahedron: dict[int, str] | None,
) -> list[str]:
    component_ids = []
    for key in ('component_id', 'wet_component_id', 'dry_component_id'):
        value = face.get(key)
        if value is not None and value not in component_ids:
            component_ids.append(value)
    if components_by_tetrahedron:
        for tetrahedron_id in (owner, neighbor):
            value = components_by_tetrahedron.get(tetrahedron_id)
            if value is not None and value not in component_ids:
                component_ids.append(value)
    return component_ids


def face_semantics(
    topography,
    face: dict[str, Any],
    *,
    components_by_tetrahedron: dict[int, str] | None = None,
) -> dict[str, Any]:
    """Return viewer-facing semantic fields for a DFND face."""
    raw = _raw_records(topography)
    tetra_by_id = {
        record.get('tetrahedron_id', index): record
        for index, record in enumerate(raw.get('tetrahedra', ()))
    }
    owner = face.get('owner_tetrahedron_id')
    neighbor = face.get('neighbor_tetrahedron_id', -1)
    owner_record = tetra_by_id.get(owner)
    neighbor_record = tetra_by_id.get(neighbor) if neighbor != -1 else None
    owner_side = _tetrahedron_side(owner_record)
    neighbor_side = 'OCEAN' if neighbor == -1 else _tetrahedron_side(neighbor_record)

    probe_radius = _probe_radius_nm(raw)
    r_gate = face.get('R_gate')
    gate_margin = None
    if isinstance(r_gate, (int, float)) and probe_radius is not None:
        gate_margin = float(r_gate) - probe_radius

    role = _face_role(face, owner_side, neighbor_side)
    component_ids = _face_component_ids(
        face, owner, neighbor, components_by_tetrahedron
    )
    return {
        'role': role,
        'side_relation': f'{owner_side}-{neighbor_side}',
        'gate_margin': gate_margin,
        'component_ids': component_ids,
    }


def face_color_from_semantics(
    semantics: dict[str, Any],
    *,
    permeability: str,
    mode: str,
    fallback_color: int = 0x888888,
) -> int:
    """Resolve the face colour for a named semantic colouring mode."""
    if mode == 'component':
        return fallback_color
    if mode == 'permeability':
        return _FACE_PERMEABILITY_COLORS.get(permeability, 0x888888)
    if mode == 'role':
        return _FACE_ROLE_COLORS.get(semantics.get('role'), 0x888888)
    if mode == 'gate_margin':
        return _gate_margin_color(semantics.get('gate_margin'))
    raise ValueError(
        "face_color_mode must be one of 'component', 'permeability', 'role', or 'gate_margin'"
    )


def _resolve_topography(view, topography):
    """If ``topography`` is None, fall back to the one attached to the view via
    ``attach_topography`` (``view.topography`` or the add-on runtime). Lets callers
    omit it after attaching: ``show_dfnd_tetrahedra(view)``.
    """
    if topography is not None:
        return topography
    attached = getattr(view, 'topography', None)
    if attached is not None:
        return attached
    runtime = getattr(view, '_topomt_addon_runtime', None)
    return getattr(runtime, 'topography', None) if runtime is not None else None


def _dfnd_edge_meta(topography, tetrahedron_ids):
    """Per-edge metadata for the wireframe: keyed by the edge's LOCAL atom pair
    (the space ``atom_quads`` uses) so the frontend can label edges by ``edge_id``.
    """
    geometry = edge_geometry(topography, tetrahedron_ids)
    return [
        {
            'atoms': list(pair),
            'atom_index_space': geometry.atom_index_space,
            'edge_id': ref.entity_id,
            'entity_ref': entity_ref_payload(ref),
        }
        for pair, ref in zip(geometry.atom_pairs, geometry.refs, strict=True)
    ]


def _dfnd_face_meta(
    topography,
    tetrahedron_ids,
    *,
    permeability_states=None,
    colors_by_tetrahedron=None,
    components_by_tetrahedron=None,
    face_color_mode='permeability',
):
    """Build pickable DFND face metadata for faces touching selected tetrahedra."""
    geometry = face_geometry(
        topography, tetrahedron_ids, permeability_states=permeability_states
    )
    face_by_id = {
        face.get('face_id'): face
        for face in select_faces(topography, permeability_state=permeability_states)
    }
    face_meta = []

    for atoms, ref in zip(geometry.atom_triplets, geometry.refs, strict=True):
        face = face_by_id.get(ref.entity_id, {})
        owner = face.get('owner_tetrahedron_id')
        neighbor = face.get('neighbor_tetrahedron_id', -1)

        permeability = face.get('permeability_state', 'unknown')
        component_color = _FACE_PERMEABILITY_COLORS.get(permeability, 0x888888)
        if colors_by_tetrahedron:
            component_color = colors_by_tetrahedron.get(
                owner,
                colors_by_tetrahedron.get(neighbor, component_color),
            )
        semantics = face_semantics(
            topography,
            face,
            components_by_tetrahedron=components_by_tetrahedron,
        )
        color = face_color_from_semantics(
            semantics,
            permeability=permeability,
            mode=face_color_mode,
            fallback_color=component_color,
        )

        face_meta.append(
            {
                'atoms': list(atoms),
                'atom_index_space': geometry.atom_index_space,
                'face_id': ref.entity_id,
                'entity_ref': entity_ref_payload(ref),
                'permeability': permeability,
                'owner_id': owner,
                'neighbor_id': 'OCEAN' if neighbor == -1 else neighbor,
                'role': semantics['role'],
                'side_relation': semantics['side_relation'],
                'gate_margin': semantics['gate_margin'],
                'component_ids': semantics['component_ids'],
                'color': color,
                'label': _dfnd_face_label(face, ref.entity_id, semantics=semantics),
            }
        )

    return face_meta


def _dfnd_atom_coords(source: Any) -> np.ndarray | None:
    dfnd = getattr(source, 'dfnd', source)
    mesh = getattr(dfnd, 'mesh', None)
    atoms = getattr(mesh, 'atoms', None)
    coords = getattr(atoms, 'coords', None)
    if coords is None:
        return None
    coords_array = np.asarray(coords, dtype=float)
    if coords_array.ndim != 2 or coords_array.shape[1] != 3:
        return None
    return coords_array


def _dfnd_face_label(
    face: dict[str, Any],
    fallback_face_id: int,
    *,
    semantics: dict[str, Any] | None = None,
) -> str:
    face_id = face.get('face_id', fallback_face_id)
    owner = face.get('owner_tetrahedron_id', 'unknown')
    neighbor = face.get('neighbor_tetrahedron_id', 'unknown')
    neighbor_label = 'OCEAN' if neighbor == -1 else neighbor
    permeability = face.get('permeability_state', 'unknown')
    r_gate = face.get('R_gate')
    r_gate_label = _angstrom_label_from_nm(r_gate)
    parts = [
        f'Face id {face_id}: tetrahedra {owner}-{neighbor_label}',
        f'permeability={permeability}',
        f'R_gate={r_gate_label}',
    ]
    if semantics:
        parts.append(f'role={semantics.get("role", "unknown_face")}')
        gate_margin = semantics.get('gate_margin')
        if gate_margin is not None:
            parts.append(f'gate_margin={_angstrom_label_from_nm(gate_margin, digits=2)}')
        component_ids = semantics.get('component_ids') or []
        if component_ids:
            parts.append('components=' + ','.join(str(value) for value in component_ids))
    return '; '.join(parts)
