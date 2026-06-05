"""show_dfnd_components: typed components in multiple representations."""

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt.dfnd import families as fam
from topomt.dfnd.selectors import select_faces

from ._common import _dfnd_edge_meta, _resolve_topography

_TYPE_PALETTE = {
    fam.POCKET: 0x3B82F6,  # Blue
    fam.VOID: 0x10B981,  # Green
    fam.CHANNEL: 0xF59E0B,  # Amber
    fam.PERCOLATING: 0x8B5CF6,  # Purple
    fam.DRY_BANK: 0x64748B,  # Slate
}

_DISTINCT_PALETTE_LIST = [
    0x3B82F6,
    0x10B981,
    0xF59E0B,
    0x8B5CF6,
    0xEF4444,
    0x06B6D4,
    0xEC4899,
    0xF97316,
    0x14B8A6,
    0x64748B,
]


def _component_node_indices(comp, *, use_resident_nodes):
    """Tetrahedra to render for a component: the resident core by default, else all."""
    if use_resident_nodes and hasattr(comp, 'resident_node_indices'):
        return comp.resident_node_indices
    return comp.node_indices


def _component_spheres(comp, tetra_map, mesh, *, use_resident_nodes):
    """Alpha-sphere ``(centers, radii)`` arrays for a component's tetrahedra.

    Prefers the per-tetra record (``center`` / ``R_residence``) and falls back to
    the raw Delaunay alpha-spheres. Returns ``(None, None)`` when the component has
    no usable tetrahedra. Shared by the ``cloud`` and ``spheres`` representations.
    """
    centers_list = []
    radii_list = []
    for tid in _component_node_indices(comp, use_resident_nodes=use_resident_nodes):
        if tid not in tetra_map:
            continue
        t = tetra_map[tid]
        if 'center' in t and 'R_residence' in t:
            centers_list.append(t['center'])
            radii_list.append(t['R_residence'])
        else:
            centers_list.append(mesh.delaunay.alpha_sphere_centers[tid])
            radii_list.append(mesh.delaunay.alpha_sphere_radii[tid])
    if not centers_list:
        return None, None
    return np.array(centers_list, dtype=float), np.array(radii_list, dtype=float)


def show_dfnd_components(
    view,
    topography=None,
    *,
    show_wet: bool = True,
    show_dry: bool = False,
    representation: str = 'tetrahedra',
    interfaces_only: bool = False,
    component_ids: list[str] | None = None,
    component_types: tuple[str, ...] = fam.PRIMARY_WET_FAMILIES,
    color_mode: str = 'distinct',
    color_palette: dict[str, int] | None = None,
    alpha: float = 0.5,
    draw_faces: bool = True,
    draw_edges: bool = False,
    edge_radius_nm: float = 0.002,
    edge_color: int = 0x444444,
    use_resident_nodes: bool = True,
    tag_prefix: str = 'dfnd-comp',
    name: str = 'DFND Components',
    skip_digestion: bool = False,
    resolution: float | None = None,
    smoothing: float | None = None,
    iso_level: float | None = None,
) -> Any:
    """Render DFND components into the viewer using multiple representation modes.

    Parameters
    ----------
    view : molsysviewer.View
        The existing viewer instance.
    topography : Topography, optional
        A Topography registry. If None, resolves from view.topography.
    show_wet : bool, default True
        Render wet components (pockets, voids, channels).
    show_dry : bool, default False
        Render dry components (hydrophobic core, dry banks).
    representation : {'tetrahedra', 'cloud', 'spheres', 'surface', 'coast_faces', 'skeleton'}, default 'tetrahedra'
        - 'tetrahedra': Volumetric Delaunay tetrahedra.
        - 'cloud': Volumetric blob (iso-surface) from alpha-spheres.
        - 'spheres': Sphere cloud of empty space spheres.
        - 'surface': Molecular pocket surface based on lining atom indices.
        - 'coast_faces': Boundary faces touching between wet and dry sides.
        - 'skeleton': Simplification graph connecting barycenters.
    interfaces_only : bool, default False
        If True, only show components flagged as interfaces (wet_interfaces).
    component_ids : list of str, optional
        A list of specific component IDs to display (e.g. ['WET-1']).
        If None, all matching components are shown.
    component_types : tuple of str, default fam.PRIMARY_WET_FAMILIES (pocket/void/channel)
        Filter wet components by their feature type.
    color_mode : {'distinct', 'by_type'}, default 'distinct'
        - 'distinct': Color each component uniquely.
        - 'by_type': Color based on component type.
    color_palette : dict of str to int, optional
        Custom hex colors mapping from component ID or family.
    alpha : float, default 0.5
        Opacity of the component geometries.
    draw_faces : bool, default True
        For 'tetrahedra': draw solid face triangles.
    draw_edges : bool, default False
        For 'tetrahedra': draw wireframe edge cylinders.
    edge_radius_nm : float, default 0.002
        Radius in nanometers of edge cylinders.
    edge_color : int, default 0x444444
        Color of edge cylinders.
    use_resident_nodes : bool, default True
        For wet components: only render resident core tetrahedra.
    tag_prefix : str, default 'dfnd-comp'
        String prefix for naming rendering layers.
    name : str, default 'DFND Components'
        Visual name of the layer.
    skip_digestion : bool, default False
        Bypass ArgDigest argument verification.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')

    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')

    # Gather matching components
    selected_components = []

    if show_wet:
        for comp in dfnd_data.dfn.components.wet:
            if component_types and comp.family not in component_types:
                continue
            if component_ids is not None and comp.component_id not in component_ids:
                continue
            if interfaces_only and not getattr(comp, 'is_interface', False):
                continue
            selected_components.append(comp)

    if show_dry:
        for comp in dfnd_data.dfn.components.dry:
            if component_ids is not None and comp.component_id not in component_ids:
                continue
            if interfaces_only:
                continue
            selected_components.append(comp)

    if not selected_components:
        return None

    mesh = dfnd_data.mesh
    coords = np.asarray(mesh.atoms.coords, dtype=float)

    # Pre-build lookup map: tetrahedron_id -> record
    tetra_map = {
        t.get('tetrahedron_id', idx): t for idx, t in enumerate(mesh.tetrahedra)
    }

    # Clean previous rendering layers under tag_prefix
    for mode in ('', '-nodes', '-edges', '-mouths', '-faces'):
        try:
            view.shapes.clear(tag=f'{tag_prefix}{mode}', skip_digestion=True)
        except Exception:
            pass

    # Resolve color per component
    resolved_colors = {}
    for idx, comp in enumerate(selected_components):
        comp_id = comp.component_id
        if color_palette and comp_id in color_palette:
            color = color_palette[comp_id]
        elif color_palette and comp.family in color_palette:
            color = color_palette[comp.family]
        elif color_mode == 'by_type':
            color = _TYPE_PALETTE.get(comp.family, 0x888888)
        else:
            color = _DISTINCT_PALETTE_LIST[idx % len(_DISTINCT_PALETTE_LIST)]
        resolved_colors[comp_id] = color

    layers = []

    if representation == 'tetrahedra':
        atom_quads = []
        colors = []
        alphas = []
        labels = []
        selected_tetra_ids = set()
        tetra_to_color = {}

        for comp in selected_components:
            comp_id = comp.component_id
            color = resolved_colors[comp_id]
            t_indices = _component_node_indices(
                comp, use_resident_nodes=use_resident_nodes
            )
            if getattr(comp, 'volume', None) is not None:
                if puw.is_quantity(comp.volume):
                    vol_a = float(puw.get_value(comp.volume, to_unit='angstroms**3'))
                else:
                    vol_a = float(comp.volume)
            else:
                vol_a = 0.0

            for tid in t_indices:
                tet_rec = tetra_map.get(tid)
                if tet_rec is None:
                    continue
                quad = tet_rec.get('local_atom_indices')
                if not quad or len(quad) != 4:
                    continue
                atom_quads.append(quad)
                colors.append(color)
                alphas.append(alpha)
                selected_tetra_ids.add(tid)
                tetra_to_color[tid] = color
                lbl = (
                    f'Component: {comp_id} ({comp.family}) | '
                    f'Tetrahedron {tid} | Vol: {vol_a:.1f} Å³'
                )
                labels.append(lbl)

        if not atom_quads:
            return None

        # Build faces
        face_meta = []
        if draw_faces:
            for face in select_faces(
                topography, owner_tetrahedron_ids=selected_tetra_ids
            ):
                atoms = face.get('face_atoms_local')
                if not atoms or len(atoms) != 3:
                    continue
                neighbor = face.get('neighbor_tetrahedron_id', -1)
                permeability = face.get('permeability_state', 'unknown')
                owner_tid = face.get('owner_tetrahedron_id')
                color = tetra_to_color.get(owner_tid, 0x888888)
                face_meta.append(
                    {
                        'atoms': [int(atom) for atom in atoms],
                        'face_id': face.get('face_id'),
                        'permeability': permeability,
                        'owner_id': owner_tid,
                        'neighbor_id': 'OCEAN' if neighbor == -1 else neighbor,
                        'color': color,
                    }
                )

        layer = view.shapes.add_tetrahedra(
            atom_quads=atom_quads,
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
            exterior_only=True,
        )
        return layer


    elif representation == 'cloud':
        # Render a separate volumetric pocket blob layer per component
        for comp in selected_components:
            comp_id = comp.component_id
            centers, radii = _component_spheres(
                comp, tetra_map, mesh, use_resident_nodes=use_resident_nodes
            )
            if centers is None:
                continue

            tag = f'{tag_prefix}:{comp_id}'
            layer = view.shapes.add_pocket_blob(
                centers=puw.quantity(centers, 'angstroms'),
                radii=puw.quantity(radii, 'angstroms'),
                alpha=alpha,
                tag=tag,
                layer_tag=tag_prefix,
                name=f'{name} {comp_id}',
                resolution=resolution,
                smoothing=smoothing,
                iso_level=iso_level,
                skip_digestion=True,
            )
            layers.append(layer)
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'spheres':
        # Render spheres cloud representing empty space using bulk shape sets
        layers = []
        for comp in selected_components:
            comp_id = comp.component_id
            color = resolved_colors[comp_id]
            comp_centers, comp_radii = _component_spheres(
                comp, tetra_map, mesh, use_resident_nodes=use_resident_nodes
            )
            if comp_centers is None:
                continue

            tag = f'{tag_prefix}:{comp_id}'
            layer = view.shapes.add_set_alpha_spheres(
                centers=puw.quantity(comp_centers, 'angstroms'),
                radii=puw.quantity(comp_radii, 'angstroms'),
                color_alpha_spheres=color,
                alpha_alpha_spheres=alpha,
                tag=tag,
                layer_tag=tag_prefix,
                skip_digestion=True,
            )
            layers.append(layer)

        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'surface':
        # Render analytical lining surface using atoms
        for comp in selected_components:
            comp_id = comp.component_id
            color = resolved_colors[comp_id]
            atom_indices = getattr(comp, 'atom_indices', None)
            if not atom_indices:
                continue

            tag = f'{tag_prefix}:{comp_id}'
            layer = view.shapes.add_pocket_surface(
                atom_indices=atom_indices,
                color_map=[color, color],
                alpha=alpha,
                tag=tag,
                layer_tag=tag_prefix,
                skip_digestion=True,
            )
            layers.append(layer)
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'coast_faces':
        # Render shared contact coast faces between wet and dry
        face_by_id = {f['face_id']: f for f in mesh.faces}
        atom_triplets = []
        colors_list = []
        labels_list = []

        for comp in selected_components:
            comp_id = comp.component_id
            color = resolved_colors[comp_id]
            comp_coast_faces = [
                face
                for face in dfnd_data.dfn.components.coast_faces
                if face['wet_component_id'] == comp_id
                or face['dry_component_id'] == comp_id
            ]

            for face in comp_coast_faces:
                f_rec = face_by_id.get(face['face_id'])
                if f_rec is not None:
                    atoms_local = f_rec.get('face_atoms_local')
                    if atoms_local is not None:
                        atom_triplets.append([int(a) for a in atoms_local])
                        colors_list.append(color)
                        lbl = (
                            f'Coast Face {face["face_id"]} | '
                            f'Wet: {face["wet_component_id"]} | '
                            f'Dry: {face["dry_component_id"]} | '
                            f'Area: {face.get("area", 0.0):.2f} Å²'
                        )
                        labels_list.append(lbl)

        if not atom_triplets:
            return None

        layer = view.shapes.add_triangle_faces(
            atom_triplets=atom_triplets,
            colors=colors_list,
            alpha=alpha,
            labels=labels_list,
            tag=tag_prefix,
            layer_tag=tag_prefix,
            skip_digestion=True,
        )
        return layer

    elif representation == 'skeleton':
        # Render DFN graph simplified skeleton
        barycenter = {
            tet['tetrahedron_id']: coords[tet['local_atom_indices']].mean(axis=0)
            for tet in mesh.tetrahedra
        }
        selected_nodes = set()
        node_to_comp = {}
        for comp in selected_components:
            t_indices = _component_node_indices(
                comp, use_resident_nodes=use_resident_nodes
            )
            for tid in t_indices:
                selected_nodes.add(tid)
                node_to_comp[tid] = comp.component_id

        centers_list = [barycenter[tid].tolist() for tid in selected_nodes]
        colors_list = [resolved_colors[node_to_comp[tid]] for tid in selected_nodes]

        if not centers_list:
            return None

        node_layer = view.shapes.add_sphere(
            center=puw.quantity(np.asarray(centers_list), 'angstroms'),
            radius=puw.quantity(0.03, 'nm'),
            color=colors_list,
            alpha=alpha,
            tag=f'{tag_prefix}-nodes',
            layer_tag=f'{tag_prefix}-nodes',
            skip_digestion=True,
        )

        edge_pairs = []
        for face_state in dfnd_data.dfn.graph.faces:
            if face_state.get('permeability_state') != 'permeable':
                continue
            owner = face_state['owner_tetrahedron_id']
            neighbor = face_state['neighbor_tetrahedron_id']
            if (
                owner in selected_nodes
                and neighbor in selected_nodes
                and owner < neighbor
            ):
                edge_pairs.append(
                    [barycenter[owner].tolist(), barycenter[neighbor].tolist()]
                )

        edge_layer = None
        if edge_pairs:
            edge_layer = view.shapes.add_links(
                coordinate_pairs=puw.quantity(np.asarray(edge_pairs), 'angstroms'),
                radius=puw.quantity(0.015, 'nm'),
                color=0x3B82F6,
                tag=f'{tag_prefix}-edges',
                layer_tag=f'{tag_prefix}-edges',
                skip_digestion=True,
            )

        return {
            'nodes': node_layer,
            'edges': edge_layer,
            'n_nodes': len(centers_list),
            'n_edges': len(edge_pairs),
        }

