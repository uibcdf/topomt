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
        color = _FACE_PERMEABILITY_COLORS.get(permeability, 0x888888)
        if colors_by_tetrahedron:
            color = colors_by_tetrahedron.get(
                owner,
                colors_by_tetrahedron.get(neighbor, color),
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
                'color': color,
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


def _dfnd_face_label(face: dict[str, Any], fallback_face_id: int) -> str:
    face_id = face.get('face_id', fallback_face_id)
    owner = face.get('owner_tetrahedron_id', 'unknown')
    neighbor = face.get('neighbor_tetrahedron_id', 'unknown')
    neighbor_label = 'OCEAN' if neighbor == -1 else neighbor
    permeability = face.get('permeability_state', 'unknown')
    r_gate = face.get('R_gate')
    r_gate_label = _angstrom_label_from_nm(r_gate)
    return (
        f'Face id {face_id}: tetrahedra {owner}-{neighbor_label}; '
        f'permeability={permeability}; '
        f'R_gate={r_gate_label}'
    )
