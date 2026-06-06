"""show_dfnd_components: typed components in multiple representations."""

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt.dfnd import families as fam
from topomt.dfnd.centerline import channel_centerline

from ._common import _dfnd_edge_meta, _dfnd_face_meta, _resolve_topography

# Colour-blind-safe (Okabe-Ito) palette, per devguide/DFND/component_visualization.md
# §11. These eight hexes are a *generic* CVD-safe catalog that should ultimately
# live upstream in molsysviewer (see proposal_molsysviewer_improvement.md, D6);
# the family->colour *mapping* below is the DFND-specific part that stays here.
_OKABE_ITO = {
    'orange': 0xE69F00,
    'sky_blue': 0x56B4E9,
    'bluish_green': 0x009E73,
    'yellow': 0xF0E442,
    'blue': 0x0072B2,
    'vermillion': 0xD55E00,
    'reddish_purple': 0xCC79A7,
    'grey': 0x999999,
}

_TYPE_PALETTE = {
    fam.POCKET: _OKABE_ITO['blue'],          # 0x0072B2
    fam.VOID: _OKABE_ITO['sky_blue'],        # 0x56B4E9 (pocket = void + one mouth)
    fam.CHANNEL: _OKABE_ITO['orange'],       # 0xE69F00
    fam.PERCOLATING: _OKABE_ITO['reddish_purple'],  # 0xCC79A7
    fam.DRY_BANK: _OKABE_ITO['grey'],        # 0x999999
}

# Two-colour pair for the common bipartite interface; extend with the remaining
# hues for 3+-body junctions (yellow is reserved for the mouth/gate accent).
_INTERFACE_BODY_COLORS = [
    _OKABE_ITO['vermillion'],
    _OKABE_ITO['bluish_green'],
    _OKABE_ITO['blue'],
    _OKABE_ITO['orange'],
]

# Reserved high-contrast accent for mouths/gates (not used by any family).
_MOUTH_ACCENT = _OKABE_ITO['yellow']

# HOLE-style clearance colours for the 'rings' channel profile (CVD-safe traffic
# light). The 1.15 Å water radius is the key threshold (see
# devguide/DFND/component_visualization.md §6).
_WATER_RADIUS = 1.15
_HOLE_OPEN = _OKABE_ITO['bluish_green']   # R >= 1.5: admits water freely
_HOLE_TIGHT = _OKABE_ITO['orange']        # 1.15 <= R < 1.5: tight constriction
_HOLE_CLOSED = _OKABE_ITO['vermillion']   # R < 1.15: closed to water

# Per-family default representation for representation='auto' (the per-family
# visual language). Channels become tubes; pockets/voids stay volumetric blobs
# until the 'envelope' mode (mouth caps) lands. See
# devguide/DFND/component_visualization_implementation.md.
_DEFAULT_REPRESENTATION_BY_FAMILY = {
    fam.CHANNEL: 'pipe',
    fam.POCKET: 'cloud',
    fam.VOID: 'cloud',
}
_AUTO_FALLBACK_REPRESENTATION = 'cloud'
_COMPONENT_REPRESENTATIONS = {
    'auto',
    'tetrahedra',
    'cloud',
    'pipe',
    'rings',
    'residence_spheres',
    'alpha_spheres',
    'probe_centers',
    'surface',
    'contact_sheet',
    'coast_faces',
    'graph',
}

_DISTINCT_PALETTE_LIST = [
    _OKABE_ITO['blue'],
    _OKABE_ITO['orange'],
    _OKABE_ITO['bluish_green'],
    _OKABE_ITO['sky_blue'],
    _OKABE_ITO['vermillion'],
    _OKABE_ITO['reddish_purple'],
    _OKABE_ITO['yellow'],
    _OKABE_ITO['grey'],
]


def _component_node_indices(comp, *, use_resident_nodes):
    """Tetrahedra to render for a component: the resident core by default, else all."""
    if use_resident_nodes and hasattr(comp, 'resident_node_indices'):
        return comp.resident_node_indices
    return comp.node_indices


def _component_residence_spheres(comp, tetra_map, *, use_resident_nodes):
    """Return maximum-clearance residence spheres for a component."""
    centers_list = []
    radii_list = []
    for tid in _component_node_indices(comp, use_resident_nodes=use_resident_nodes):
        if tid not in tetra_map:
            continue
        t = tetra_map[tid]
        if 'center' in t and 'R_residence' in t:
            centers_list.append(t['center'])
            radii_list.append(t['R_residence'])
    if not centers_list:
        return None, None
    return np.array(centers_list, dtype=float), np.array(radii_list, dtype=float)


def _component_alpha_spheres(comp, mesh, *, use_resident_nodes):
    """Return geometric Delaunay circumspheres for a component."""
    tetrahedron_ids = list(
        _component_node_indices(comp, use_resident_nodes=use_resident_nodes)
    )
    if not tetrahedron_ids:
        return None, None
    centers = np.asarray(mesh.delaunay.alpha_sphere_centers, dtype=float)[
        tetrahedron_ids
    ]
    radii = np.asarray(mesh.delaunay.alpha_sphere_radii, dtype=float)[tetrahedron_ids]
    return centers, radii


def _body_labels_from_dry(dry_components, n_atoms):
    """Per-atom body id from the dry components (largest dry body wins shared
    atoms), mirroring ``interfaces.body_labels_from_dry_components`` but consuming
    the typed dry ``Component`` objects the renderer already holds. ``-1`` means
    no body. Used by the ``contact_sheet`` (interface) representation.
    """
    labels = np.full(int(n_atoms), -1, dtype=int)
    ordered = sorted(
        dry_components,
        key=lambda c: len(getattr(c, 'atom_indices', []) or []),
        reverse=True,
    )
    for body_id, comp in enumerate(ordered):
        for atom in getattr(comp, 'atom_indices', []) or []:
            if 0 <= atom < n_atoms and labels[atom] == -1:
                labels[atom] = body_id
    return labels


def _rank_by_volume(components, top_n):
    """Keep the ``top_n`` components by solvent volume (largest first), the
    default-visibility-by-relevance rule. ``top_n=None`` keeps all.
    """
    if top_n is None or top_n >= len(components):
        return components
    return sorted(
        components,
        key=lambda c: (getattr(c, 'volume_solvent_estimate', None) or 0.0),
        reverse=True,
    )[:top_n]


def _centerline_normals(centers):
    """Per-station tangent of an ordered centerline (the local axis a ring is
    drawn perpendicular to). Central difference inside, one-sided at the ends."""
    n = len(centers)
    normals = []
    for i in range(n):
        if i == 0:
            tangent = centers[1] - centers[0]
        elif i == n - 1:
            tangent = centers[-1] - centers[-2]
        else:
            tangent = centers[i + 1] - centers[i - 1]
        if not np.any(tangent):
            tangent = np.array([0.0, 0.0, 1.0])
        normals.append(tangent.tolist())
    return normals


def _hole_clearance_color(radius):
    """HOLE traffic-light colour for a free radius (Å)."""
    if radius < _WATER_RADIUS:
        return _HOLE_CLOSED
    if radius < 1.5:
        return _HOLE_TIGHT
    return _HOLE_OPEN


def carve_voids(view, topography=None, *, component_ids=None,
                component_types=(fam.VOID,), fade=0.85):
    """Expose buried components by fading the rest of the protein (void carving).

    Soft-focuses the molecular representation on the lining atoms of the selected
    components via ``view.focus_with_fade`` — everything outside fades to ``fade``
    transparency, so a buried void becomes visible without a clipping plane (see
    devguide/DFND/component_visualization_implementation.md, Phase 5). By default
    targets all voids. Call ``view.focus_with_fade('all')`` to clear.

    Returns the sorted lining atom indices kept opaque, or ``None`` if none match.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')

    focus_atoms: set[int] = set()
    for comp in dfnd_data.dfn.components.wet:
        if component_types and comp.family not in component_types:
            continue
        if component_ids is not None and comp.component_id not in component_ids:
            continue
        focus_atoms.update(int(a) for a in (getattr(comp, 'atom_indices', None) or []))

    if not focus_atoms:
        return None
    ordered = sorted(focus_atoms)
    view.focus_with_fade(ordered, fade=fade)
    return ordered


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
    radius_scale: float | None = None,
    top_n: int | None = None,
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
    representation : {'auto', 'tetrahedra', 'cloud', 'pipe', 'contact_sheet', 'residence_spheres', 'alpha_spheres', 'probe_centers', 'surface', 'coast_faces', 'graph'}, default 'tetrahedra'
        - 'auto': Per-family visual language — each component is drawn with its
          family's default mode (channel->pipe, pocket/void->cloud).
        - 'tetrahedra': Volumetric Delaunay tetrahedra.
        - 'cloud': Approximate iso-surface from residence spheres.
        - 'pipe': Channels as a variable-radius tube along their through-path
          (centerline + R_residence) with a bottleneck marker; non-channels fall
          back to a blob.
        - 'rings': HOLE-style clearance profile of a channel — a ring per
          centerline station coloured by free-radius threshold (green/amber/red).
        - 'residence_spheres': Maximum-clearance spheres inside resident tetrahedra.
        - 'alpha_spheres': Geometric Delaunay circumspheres for diagnostics.
        - 'probe_centers': Probe-sized spheres at maximum-clearance centers.
        - 'surface': Molecular pocket surface based on lining atom indices.
        - 'contact_sheet': Interface lining surface split by body (one colour per
          body), for wet components lined by two or more bodies.
        - 'coast_faces': Boundary faces touching between wet and dry sides.
        - 'graph': DFN connectivity graph connecting tetrahedron barycenters.
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
    radius_scale : float, optional
        For 'cloud': scales alpha-sphere radii before building the Gaussian field.
    top_n : int, optional
        If given, render only the ``top_n`` components by solvent volume
        (default-visibility-by-relevance); the rest are dropped from this call.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')

    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')

    representation = {
        'spheres': 'residence_spheres',
        'skeleton': 'graph',
    }.get(representation, representation)
    if representation not in _COMPONENT_REPRESENTATIONS:
        supported = ', '.join(sorted(_COMPONENT_REPRESENTATIONS))
        raise ValueError(
            f'Unknown representation {representation!r}. Supported: {supported}.'
        )

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

    selected_components = _rank_by_volume(selected_components, top_n)

    if representation == 'auto':
        # Per-family visual language: group the selection by each component's
        # default representation and delegate to the concrete mode per group, so a
        # void and a channel in the same call render differently. clear() is by
        # exact tag, so the groups do not clobber each other's layers.
        groups: dict[str, list[str]] = {}
        for comp in selected_components:
            # the interface axis is orthogonal to the mouth-topology family: an
            # interface (whatever its family) reads best as a body-split surface.
            if getattr(comp, 'is_interface', False):
                mode = 'contact_sheet'
            else:
                mode = _DEFAULT_REPRESENTATION_BY_FAMILY.get(
                    comp.family, _AUTO_FALLBACK_REPRESENTATION
                )
            groups.setdefault(mode, []).append(comp.component_id)
        results = []
        for mode, ids in groups.items():
            res = show_dfnd_components(
                view,
                topography,
                show_wet=show_wet,
                show_dry=show_dry,
                representation=mode,
                interfaces_only=interfaces_only,
                component_ids=ids,
                component_types=None,
                color_mode=color_mode,
                color_palette=color_palette,
                alpha=alpha,
                draw_faces=draw_faces,
                draw_edges=draw_edges,
                edge_radius_nm=edge_radius_nm,
                edge_color=edge_color,
                use_resident_nodes=use_resident_nodes,
                tag_prefix=tag_prefix,
                name=name,
                skip_digestion=skip_digestion,
                resolution=resolution,
                smoothing=smoothing,
                iso_level=iso_level,
                radius_scale=radius_scale,
            )
            if isinstance(res, list):
                results.extend(res)
            elif res is not None:
                results.append(res)
        if not results:
            return None
        return results[0] if len(results) == 1 else results

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

    for comp in selected_components:
        try:
            view.shapes.clear(
                tag=f'{tag_prefix}:{comp.component_id}', skip_digestion=True
            )
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

        face_meta = (
            _dfnd_face_meta(
                topography,
                selected_tetra_ids,
                colors_by_tetrahedron=tetra_to_color,
            )
            if draw_faces
            else []
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
        # Render a separate volumetric pocket blob layer per component. The
        # MolSysViewer blob defaults are broad for DFND residence spheres, so use
        # conservative defaults unless the caller provides explicit values.
        blob_resolution = 0.5 if resolution is None else resolution
        blob_smoothing = 0.5 if smoothing is None else smoothing
        blob_iso_level = 0.5 if iso_level is None else iso_level
        blob_radius_scale = 0.6 if radius_scale is None else radius_scale

        for comp in selected_components:
            comp_id = comp.component_id
            centers, radii = _component_residence_spheres(
                comp, tetra_map, use_resident_nodes=use_resident_nodes
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
                resolution=blob_resolution,
                smoothing=blob_smoothing,
                iso_level=blob_iso_level,
                radius_scale=blob_radius_scale,
                skip_digestion=True,
            )
            layers.append(layer)
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'pipe':
        # Channels as variable-radius tubes along their through-path (CAVER-style),
        # radius = local R_residence, with a bottleneck marker at the narrowest
        # station. Non-channels (or channels with no through-path) fall back to a
        # volumetric blob. See
        # devguide/DFND/component_visualization_implementation.md (Phase 2).
        raw = dfnd_data.raw
        for comp in selected_components:
            comp_id = comp.component_id
            color = resolved_colors[comp_id]

            centerline = None
            if comp.family == fam.CHANNEL and comp.raw_record is not None:
                centerline = channel_centerline(raw, comp.raw_record)

            if centerline is None:
                centers, radii = _component_residence_spheres(
                    comp, tetra_map, use_resident_nodes=use_resident_nodes
                )
                if centers is None:
                    continue
                layer = view.shapes.add_pocket_blob(
                    centers=puw.quantity(centers, 'angstroms'),
                    radii=puw.quantity(radii, 'angstroms'),
                    alpha=alpha,
                    tag=f'{tag_prefix}:{comp_id}',
                    layer_tag=tag_prefix,
                    name=f'{name} {comp_id}',
                    resolution=0.5 if resolution is None else resolution,
                    smoothing=0.5 if smoothing is None else smoothing,
                    iso_level=0.5 if iso_level is None else iso_level,
                    radius_scale=0.6 if radius_scale is None else radius_scale,
                    skip_digestion=True,
                )
                layers.append(layer)
                continue

            centers = centerline['centers']
            radii = centerline['radii']
            tube = view.shapes.add_channel_tube(
                centers=puw.quantity(centers, 'angstroms'),
                radii=puw.quantity(radii, 'angstroms'),
                color_map=[color, color],
                alpha=alpha,
                tag=f'{tag_prefix}:{comp_id}',
                layer_tag=tag_prefix,
                name=f'{name} {comp_id}',
                skip_digestion=True,
            )
            layers.append(tube)

            # Bottleneck ring: a flat ring at the narrowest station, perpendicular
            # to the local channel axis, radius = the free radius there. Drawn with
            # the dedicated molsysviewer ring shape in the reserved gate accent.
            neck = centerline['bottleneck_index']
            if neck == 0:
                tangent = centers[1] - centers[0]
            elif neck == len(centers) - 1:
                tangent = centers[-1] - centers[-2]
            else:
                tangent = centers[neck + 1] - centers[neck - 1]
            if not np.any(tangent):
                tangent = np.array([0.0, 0.0, 1.0])
            marker = view.shapes.add_rings(
                centers=puw.quantity(centers[neck:neck + 1], 'angstroms'),
                normals=[tangent.tolist()],
                radii=puw.quantity(radii[neck:neck + 1], 'angstroms'),
                colors=[_MOUTH_ACCENT],
                alpha=min(1.0, alpha + 0.3),
                tag=f'{tag_prefix}:{comp_id}-bottleneck',
                layer_tag=tag_prefix,
                skip_digestion=True,
            )
            layers.append(marker)

        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'rings':
        # HOLE-style clearance profile: one ring per centerline station,
        # perpendicular to the local channel axis, coloured by free-radius
        # threshold (green/amber/red). Channels only. See
        # devguide/DFND/component_visualization_implementation.md (Phase 4).
        raw = dfnd_data.raw
        for comp in selected_components:
            comp_id = comp.component_id
            if comp.family != fam.CHANNEL or comp.raw_record is None:
                continue
            centerline = channel_centerline(raw, comp.raw_record)
            if centerline is None:
                continue
            centers = centerline['centers']
            radii = centerline['radii']
            layer = view.shapes.add_rings(
                centers=puw.quantity(centers, 'angstroms'),
                normals=_centerline_normals(centers),
                radii=puw.quantity(radii, 'angstroms'),
                colors=[_hole_clearance_color(float(r)) for r in radii],
                alpha=alpha,
                tag=f'{tag_prefix}:{comp_id}',
                layer_tag=tag_prefix,
                name=f'{name} {comp_id}',
                skip_digestion=True,
            )
            layers.append(layer)

        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation in {'residence_spheres', 'alpha_spheres'}:
        # Residence spheres describe clearance; alpha-spheres describe geometry.
        layers = []
        for comp in selected_components:
            comp_id = comp.component_id
            color = resolved_colors[comp_id]
            if representation == 'residence_spheres':
                comp_centers, comp_radii = _component_residence_spheres(
                    comp, tetra_map, use_resident_nodes=use_resident_nodes
                )
            else:
                comp_centers, comp_radii = _component_alpha_spheres(
                    comp, mesh, use_resident_nodes=use_resident_nodes
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

    elif representation == 'probe_centers':
        parameters = getattr(dfnd_data.dfn, 'parameters', {})
        probe_radius = parameters.get('probe_radius')
        if probe_radius is None:
            raise ValueError(
                "DFND data must provide parameters['probe_radius'] for probe_centers"
            )
        if puw.is_quantity(probe_radius):
            probe_radius = float(puw.get_value(probe_radius, to_unit='angstroms'))
        else:
            probe_radius = float(probe_radius)

        for comp in selected_components:
            comp_id = comp.component_id
            color = resolved_colors[comp_id]
            centers, residence_radii = _component_residence_spheres(
                comp, tetra_map, use_resident_nodes=use_resident_nodes
            )
            if centers is None:
                continue
            valid_centers = residence_radii >= probe_radius
            centers = centers[valid_centers]
            if not len(centers):
                continue
            tag = f'{tag_prefix}:{comp_id}'
            layer = view.shapes.add_sphere(
                center=puw.quantity(centers, 'angstroms'),
                radius=puw.quantity(probe_radius, 'angstroms'),
                color=color,
                alpha=alpha,
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

    elif representation == 'contact_sheet':
        # Interface lining surface split by body: bicolor for two banks, one
        # colour per body for N-body junctions. Body labels are derived from the
        # dry network (the per-atom mapping the component only stores as counts).
        # See devguide/DFND/component_visualization_implementation.md (Phase 3).
        n_atoms = len(coords)
        body_labels = _body_labels_from_dry(
            list(dfnd_data.dfn.components.dry), n_atoms
        )
        for comp in selected_components:
            comp_id = comp.component_id
            atom_indices = getattr(comp, 'atom_indices', None)
            if not atom_indices:
                continue

            by_body = {}
            for atom in atom_indices:
                body = int(body_labels[atom]) if 0 <= atom < n_atoms else -1
                if body < 0:
                    continue
                by_body.setdefault(body, []).append(atom)

            if not by_body:
                # not a multi-body lining: single-colour fallback surface
                color = resolved_colors[comp_id]
                layers.append(
                    view.shapes.add_pocket_surface(
                        atom_indices=atom_indices,
                        color_map=[color, color],
                        alpha=alpha,
                        tag=f'{tag_prefix}:{comp_id}',
                        layer_tag=tag_prefix,
                        skip_digestion=True,
                    )
                )
                continue

            for body in sorted(by_body):
                body_color = _INTERFACE_BODY_COLORS[body % len(_INTERFACE_BODY_COLORS)]
                layers.append(
                    view.shapes.add_pocket_surface(
                        atom_indices=by_body[body],
                        color_map=[body_color, body_color],
                        alpha=alpha,
                        tag=f'{tag_prefix}:{comp_id}-body{body}',
                        layer_tag=tag_prefix,
                        skip_digestion=True,
                    )
                )

        if not layers:
            return None
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

    elif representation == 'graph':
        # Render the component-filtered DFN connectivity graph.
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

        ordered_nodes = sorted(selected_nodes)
        centers_list = [barycenter[tid].tolist() for tid in ordered_nodes]
        colors_list = [resolved_colors[node_to_comp[tid]] for tid in ordered_nodes]

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
