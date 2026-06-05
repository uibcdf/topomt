"""show_dfn_graph: DFN flow-graph nodes/edges."""

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw

from ._common import _resolve_topography

_DFN_NODE_PALETTE = {
    'wet_sealed': 0x14B8A6,
    'wet_open': 0x3B82F6,
    'wet_coast': 0x8B5CF6,
    'dry_sealed': 0x334155,
    'dry_open': 0x64748B,
    'dry_coast': 0xF97316,
}


def show_dfn_graph(
    view,
    topography=None,
    *,
    color_palette: dict[str, int] | None = None,
    node_radius_nm: float = 0.03,
    node_alpha: float = 0.75,
    edge_radius_nm: float = 0.015,
    edge_color: int = 0x3B82F6,  # blue: permeable transit through a face
    mouth_color: int = 0xF59E0B,  # amber: external link (exterior access)
    mouth_stub_angstrom: float = 2.0,  # cylinder length beyond the boundary face
    tag_prefix: str = 'dfn-graph',
    skip_digestion: bool = False,
) -> dict[str, Any] | None:
    """Render the DFN as a graph (view-independent: spheres + cylinders).

    A sphere is placed at the barycentre of every tetrahedron that is a node:
    **resident OR with at least one permeable face** (so wet cells, dry transit
    connectors and dry_coast lining cells are all shown; only fully-sealed dry
    cells are omitted). Spheres are coloured by ``combined_class``. Permeable
    shared faces become blue cylinders between barycentres; permeable boundary
    faces become amber stubs along the outward normal (external links / mouths).

    Avoids the single-sided face artefacts of ``render_dfnd_tetrahedra``. See
    ``devguide/DFND/object_model.md`` and ``residence_transit_contract.md``.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError(
            'topography is required (pass it explicitly or attach via attach_topography(view, topography))'
        )
    data = getattr(topography, 'dfnd', None)
    if data is None:
        data = topography  # accept a DFNDData passed directly
    mesh = data.mesh
    coords = np.asarray(mesh.atoms.coords, dtype=float)

    palette = dict(_DFN_NODE_PALETTE)
    if color_palette:
        palette.update(color_palette)

    barycenter = {
        tet['tetrahedron_id']: coords[tet['local_atom_indices']].mean(axis=0)
        for tet in mesh.tetrahedra
    }
    state = {node['tetrahedron_id']: node for node in data.dfn.graph.nodes}

    def _is_node(tid: int) -> bool:
        s = state[tid]
        return s['residence_state'] == 'resident' or s['n_permeable_contacts'] >= 1

    node_ids = [
        tet['tetrahedron_id']
        for tet in mesh.tetrahedra
        if _is_node(tet['tetrahedron_id'])
    ]
    if not node_ids:
        return None
    node_set = set(node_ids)

    centers = [barycenter[tid].tolist() for tid in node_ids]
    colors = [palette.get(state[tid]['combined_class'], 0x888888) for tid in node_ids]

    edge_pairs: list[list[list[float]]] = []
    mouth_pairs: list[list[list[float]]] = []
    for face_state, face_geom in zip(data.dfn.graph.faces, mesh.faces):
        if face_state['permeability_state'] != 'permeable':
            continue
        owner = face_state['owner_tetrahedron_id']
        neighbor = face_state['neighbor_tetrahedron_id']
        if owner not in node_set:
            continue
        if neighbor >= 0:
            if (
                neighbor in node_set and owner < neighbor
            ):  # one cylinder per shared face
                edge_pairs.append(
                    [barycenter[owner].tolist(), barycenter[neighbor].tolist()]
                )
        else:  # boundary face -> mouth stub
            triangle = coords[face_geom['face_atoms_local']]
            normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
            length = np.linalg.norm(normal)
            if length < 1e-9:
                continue
            normal = normal / length
            origin = barycenter[owner]
            face_centroid = triangle.mean(axis=0)
            if np.dot(normal, face_centroid - origin) < 0:  # orient outward
                normal = -normal
            tip = face_centroid + normal * mouth_stub_angstrom
            mouth_pairs.append([origin.tolist(), tip.tolist()])

    try:
        view.shapes.clear(tag=tag_prefix, skip_digestion=True)
    except Exception:
        pass

    node_layer = view.shapes.add_sphere(
        center=puw.quantity(np.asarray(centers), 'angstroms'),
        radius=puw.quantity(node_radius_nm, 'nm'),
        color=colors,
        alpha=node_alpha,
        tag=f'{tag_prefix}-node',
        layer_tag=f'{tag_prefix}-nodes',
        skip_digestion=skip_digestion,
    )
    edge_layer = None
    if edge_pairs:
        edge_layer = view.shapes.add_links(
            coordinate_pairs=puw.quantity(np.asarray(edge_pairs), 'angstroms'),
            radius=puw.quantity(edge_radius_nm, 'nm'),
            color=edge_color,
            tag=f'{tag_prefix}-edges',
            layer_tag=f'{tag_prefix}-edges',
            skip_digestion=skip_digestion,
        )
    mouth_layer = None
    if mouth_pairs:
        mouth_layer = view.shapes.add_links(
            coordinate_pairs=puw.quantity(np.asarray(mouth_pairs), 'angstroms'),
            radius=puw.quantity(edge_radius_nm, 'nm'),
            color=mouth_color,
            tag=f'{tag_prefix}-mouths',
            layer_tag=f'{tag_prefix}-mouths',
            skip_digestion=skip_digestion,
        )

    return {
        'nodes': node_layer,
        'edges': edge_layer,
        'mouths': mouth_layer,
        'n_nodes': len(node_ids),
        'n_edges': len(edge_pairs),
        'n_mouths': len(mouth_pairs),
    }


