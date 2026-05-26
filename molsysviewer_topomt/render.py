"""Python-side rendering helpers for the first TopoMT MolSysViewer addon slice."""

import math
from collections.abc import Iterable
from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt.dfnd.selectors import (
    select_component_tetrahedron_ids,
    select_faces,
    select_tetrahedra,
    select_tetrahedron_ids,
)

from .payloads import topography_payload

DEFAULT_BLOB_ALPHA = 0.35
DEFAULT_MARKER_ALPHA = 0.55
DEFAULT_MARKER_COLOR = 0xD95F02
DEFAULT_MARKER_RADIUS_NM = 0.12


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
    face_index = face.get('face_index', 'unknown')
    permeability = face.get('permeability_state', 'unknown')
    r_gate = face.get('R_gate')
    if isinstance(r_gate, (int, float)):
        r_gate_label = f'{float(r_gate):.2f} Å'
    else:
        r_gate_label = 'unknown'
    return (
        f'Face {face_id}: tetrahedra {owner}-{neighbor_label}; '
        f'owner_face_index={face_index}; '
        f'permeability={permeability}; '
        f'R_gate={r_gate_label}'
    )


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
    tetrahedra_indices: Iterable[int] | None = None,
    show_all_faces: bool = False,
    draw_faces: bool = True,
) -> Any:
    """Render DFND Delaunay tetrahedra into the viewer canvas.

    Delaunay tetrahedra are rendered as a custom triangle mesh color-coded by their
    DFND classification. Custom hover labels (tooltips) are attached for interactive
    diagnostics.

    With ``draw_faces=False`` only the tetrahedron *edges* are drawn (a wireframe
    of every selected tetrahedron, no coloured faces) as cylinders in
    ``edge_color`` — useful to see the Delaunay skeleton without the per-face
    colouring ambiguity. (Bump ``edge_radius_nm`` so the wireframe is visible,
    e.g. 0.02–0.05.)
    """
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
            f'Tetrahedron {tet.get("tetrahedron_id", idx)}: '
            f'combined_class={tet.get("combined_class", "unknown")}, '
            f'role={tet.get("transit_role", "unknown")}, '
            f'R_res={tet.get("R_residence", 0.0):.2f} Å'
        )
        labels.append(lbl)

    if not atom_quads:
        return None

    # Edges-only mode: the frontend skips the face triangles entirely
    # (draw_faces=False) and draws only the edge cylinders, so we force the
    # edges on and collect every face so all internal edges appear too.
    if not draw_faces:
        draw_edges = True
        show_all_faces = True

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
        draw_faces=draw_faces,
        draw_edges=draw_edges,
        edge_radius=puw.quantity(edge_radius_nm, 'nm'),
        edge_color=edge_color,
        tag=tag_prefix,
        layer_tag=tag_prefix,
        name=name,
        skip_digestion=skip_digestion,
        show_all_faces=show_all_faces,
        exterior_only=not show_all_faces,
    )

    return layer


# Node-class colors (combined_class), shared with render_dfnd_tetrahedra.
_DFN_NODE_PALETTE = {
    'wet_sealed': 0x14B8A6,
    'wet_open': 0x3B82F6,
    'wet_coast': 0x8B5CF6,
    'dry_sealed': 0x334155,
    'dry_open': 0x64748B,
    'dry_coast': 0xF97316,
}


def render_dfn_graph(
    view,
    topography,
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


def render_dfn_dry_components(
    view,
    topography,
    *,
    color: int = 0xFDE68A,  # pale yellow context body
    alpha: float = 0.15,
    draw_faces: bool = True,
    draw_edges: bool = False,
    draw_impermeable_faces: bool = True,
    draw_permeable_faces: bool = True,
    component_ids: str | int | Iterable[str | int] | None = None,
    edge_radius_nm: float = 0.002,
    edge_color: int = 0x444444,
    tag_prefix: str = 'dfn-dry',
    name: str = 'DFND Dry Components',
    skip_digestion: bool = False,
) -> Any:
    """Render the dry (non-resident) tetrahedra as a faint context body.

    Faces can be filtered by permeability. Edges are drawn as a separate
    wireframe layer so calls such as ``draw_faces=True, draw_edges=True,
    draw_impermeable_faces=False, draw_permeable_faces=True`` show the dry
    skeleton while filling only permeable dry faces.
    """
    dry_tetrahedron_ids = set(
        select_component_tetrahedron_ids(
            topography,
            side='dry',
            component_ids=component_ids,
        )
    )
    if component_ids is None and not dry_tetrahedron_ids:
        dry_tetrahedron_ids = set(
            select_tetrahedron_ids(topography, residence_state='non_resident')
        )

    dry_tetrahedra = select_tetrahedra(
        topography,
        tetrahedron_ids=dry_tetrahedron_ids,
        residence_state='non_resident',
    )
    atom_quads = []
    tetrahedron_labels = []
    for idx, tetrahedron in enumerate(dry_tetrahedra):
        atoms = tetrahedron.get('local_atom_indices')
        if not atoms or len(atoms) != 4:
            continue
        atom_quads.append([int(atom) for atom in atoms])
        tetrahedron_labels.append(
            f'Tetrahedron {tetrahedron.get("tetrahedron_id", idx)}: '
            f'combined_class={tetrahedron.get("combined_class", "unknown")}, '
            f'role={tetrahedron.get("transit_role", "unknown")}, '
            f'R_res={tetrahedron.get("R_residence", 0.0):.2f} Å'
        )
    if not atom_quads:
        return None
    allowed_permeability_states = set()
    if draw_impermeable_faces:
        allowed_permeability_states.add('non_permeable')
    if draw_permeable_faces:
        allowed_permeability_states.add('permeable')

    atom_coords = _dfnd_atom_coords(topography)
    face_triplets = []
    face_vertices = []
    face_labels = []
    if draw_faces and allowed_permeability_states:
        for face in select_faces(
            topography,
            owner_tetrahedron_ids=dry_tetrahedron_ids,
            permeability_state=allowed_permeability_states,
        ):
            atoms = face.get('face_atoms_local')
            if not atoms or len(atoms) != 3:
                continue
            atom_triplet = [int(atom) for atom in atoms]
            face_triplets.append(atom_triplet)
            if atom_coords is not None:
                face_vertices.append(atom_coords[atom_triplet].tolist())
            face_labels.append(_dfnd_face_label(face, len(face_triplets)))

    for tag in (tag_prefix, f'{tag_prefix}-edges', f'{tag_prefix}-faces'):
        try:
            view.shapes.clear(tag=tag, skip_digestion=True)
        except Exception:
            pass

    edge_layer = None
    if draw_edges:
        edge_layer = view.shapes.add_tetrahedra(
            atom_quads=atom_quads,
            colors=[color] * len(atom_quads),
            alphas=[alpha] * len(atom_quads),
            labels=tetrahedron_labels,
            draw_faces=False,
            draw_edges=True,
            edge_radius=puw.quantity(edge_radius_nm, 'nm'),
            edge_color=edge_color,
            tag=f'{tag_prefix}-edges',
            layer_tag=f'{tag_prefix}-edges',
            name=f'{name} Edges',
            skip_digestion=skip_digestion,
            show_all_faces=True,
            exterior_only=False,
        )

    face_layer = None
    if face_triplets:
        face_geometry = (
            {'vertices': puw.quantity(face_vertices, 'angstroms')}
            if face_vertices
            else {'atom_triplets': face_triplets}
        )
        face_layer = view.shapes.add_triangle_faces(
            **face_geometry,
            colors=[color] * len(face_triplets),
            alpha=alpha,
            labels=face_labels,
            draw_edges=False,
            tag=f'{tag_prefix}-faces',
            layer_tag=f'{tag_prefix}-faces',
            skip_digestion=skip_digestion,
        )

    if edge_layer is None:
        return face_layer
    if face_layer is None:
        return edge_layer
    return {
        'edges': edge_layer,
        'faces': face_layer,
        'n_tetrahedra': len(atom_quads),
        'n_faces': len(face_triplets),
    }
