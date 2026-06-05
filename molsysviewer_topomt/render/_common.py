"""Shared helpers for the TopoMT viewer render package."""

from typing import Any

import numpy as np

from topomt.dfnd.selectors import select_edges

DEFAULT_BLOB_ALPHA = 0.35
DEFAULT_MARKER_ALPHA = 0.55
DEFAULT_MARKER_COLOR = 0xD95F02
DEFAULT_MARKER_RADIUS_NM = 0.12


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
    return [
        {'atoms': list(edge['local_atom_indices']), 'edge_id': edge['edge_id']}
        for edge in select_edges(topography, tetrahedron_ids=tetrahedron_ids)
    ]


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
    if isinstance(r_gate, (int, float)):
        r_gate_label = f'{float(r_gate):.2f} Å'
    else:
        r_gate_label = 'unknown'
    return (
        f'Face id {face_id}: tetrahedra {owner}-{neighbor_label}; '
        f'permeability={permeability}; '
        f'R_gate={r_gate_label}'
    )
