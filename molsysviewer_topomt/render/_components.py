"""show_dfnd_components: typed components in multiple representations."""

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt.dfnd import families as fam

from ..geometry import (
    EntityRef,
    RingGeometry,
    centerline_ring_geometry,
    component_alpha_sphere_geometry,
    component_centerline_geometry,
    component_residence_sphere_geometry,
    dfn_graph_segments,
    face_geometry,
    mouth_ring_geometry,
    probe_sphere_geometry,
    scaffold_geometry,
    tetrahedra_geometry,
    tetrahedron_centers,
)
from ..index_spaces import MOLECULAR_SYSTEM
from ..index_spaces import (
    atom_indices as indices_in_space,
)
from ._common import (
    _angstrom2_from_nm2,
    _angstrom3_from_nm3,
    _dfnd_edge_meta,
    _dfnd_face_meta,
    _resolve_topography,
)
from .adapters import (
    add_channel_tube,
    add_indexed_triangles,
    add_pocket_blob,
    add_point_spheres,
    add_rings,
    add_segments,
    add_sphere_set,
    add_tetrahedra,
    add_uniform_spheres,
)
from .result import (
    clear_previous_render_result,
    remember_render_result,
    render_result,
)

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
    fam.POCKET: _OKABE_ITO['blue'],  # 0x0072B2
    fam.VOID: _OKABE_ITO['sky_blue'],  # 0x56B4E9 (pocket = void + one mouth)
    fam.CHANNEL: _OKABE_ITO['orange'],  # 0xE69F00
    fam.PERCOLATING: _OKABE_ITO['reddish_purple'],  # 0xCC79A7
    fam.DRY_BANK: _OKABE_ITO['grey'],  # 0x999999
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
_HOLE_OPEN = _OKABE_ITO['bluish_green']  # R >= 1.5: admits water freely
_HOLE_TIGHT = _OKABE_ITO['orange']  # 1.15 <= R < 1.5: tight constriction
_HOLE_CLOSED = _OKABE_ITO['vermillion']  # R < 1.15: closed to water

# Affinity (physicochemical) colours for the 'affinity_spheres' druggability map,
# derived from molsysmt.physchem hydrophobicity (Eisenberg) + charge (pH7).
_AFFINITY_HYDROPHOBIC = _OKABE_ITO['orange']  # drug-favourable nonpolar
_AFFINITY_POLAR = _OKABE_ITO['sky_blue']  # polar / H-bonding
_AFFINITY_POSITIVE = _OKABE_ITO['blue']  # positively charged
_AFFINITY_NEGATIVE = _OKABE_ITO['vermillion']  # negatively charged
_AFFINITY_NEUTRAL = _OKABE_ITO['grey']  # unknown / dummy (e.g. DUM)

# Per-family default representation for representation='auto' (the per-family
# visual language). Channels become tubes; pockets/voids stay volumetric blobs
# until the 'envelope' mode (mouth caps) lands. See
# devguide/DFND/component_visualization_implementation.md.
_DEFAULT_REPRESENTATION_BY_FAMILY = {
    fam.CHANNEL: 'pipe',
    fam.POCKET: 'envelope',
    fam.VOID: 'envelope',
}
_AUTO_FALLBACK_REPRESENTATION = 'cloud'
_COMPONENT_REPRESENTATIONS = {
    'auto',
    'tetrahedra',
    'cloud',
    'envelope',
    'pipe',
    'rings',
    'residence_spheres',
    'alpha_spheres',
    'probe_centers',
    'surface',
    'contact_sheet',
    'scaffold',
    'affinity_spheres',
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


def _body_labels_from_dry(dry_components):
    """Map molecular-system atom indices to dry-body ids."""
    labels = {}
    ordered = sorted(
        dry_components,
        key=lambda c: len(getattr(c, 'atom_indices', []) or []),
        reverse=True,
    )
    for body_id, comp in enumerate(ordered):
        for atom in indices_in_space(
            getattr(comp, 'atom_indices', None), space=MOLECULAR_SYSTEM
        ):
            labels.setdefault(atom, body_id)
    return labels


def _rank_by_volume(components, top_n):
    """Keep the ``top_n`` components by solvent volume (largest first), the
    default-visibility-by-relevance rule. ``top_n=None`` keeps all.
    """
    if top_n is None or top_n >= len(components):
        return components
    return sorted(
        components,
        key=lambda c: getattr(c, 'volume_solvent_estimate', None) or 0.0,
        reverse=True,
    )[:top_n]


def _hole_clearance_color(radius):
    """HOLE traffic-light colour for a free radius (nm)."""
    radius_angstroms = radius * 10.0  # clearance radii are nm (DFND kernel units)
    if radius_angstroms < _WATER_RADIUS:
        return _HOLE_CLOSED
    if radius_angstroms < 1.5:
        return _HOLE_TIGHT
    return _HOLE_OPEN


def _atom_convexity(coords, radius=8.0):
    """Per-atom local convexity scalar: positive on ridges/protrusions, negative
    in valleys/pockets. For each atom, the displacement from the centroid of its
    neighbours within ``radius``, signed by whether it points outward (convex) or
    inward (concave) relative to the global centre.
    """
    coords = np.asarray(coords, dtype=float)
    n = len(coords)
    if n < 2:
        return np.zeros(n)
    from scipy.spatial import cKDTree

    global_center = coords.mean(axis=0)
    tree = cKDTree(coords)
    conv = np.zeros(n)
    for i in range(n):
        nbrs = [j for j in tree.query_ball_point(coords[i], radius) if j != i]
        if not nbrs:
            continue
        v = coords[i] - coords[nbrs].mean(axis=0)
        out = coords[i] - global_center
        out_norm = float(np.linalg.norm(out))
        sign = np.sign(float(np.dot(v, out))) if out_norm > 1e-9 else 1.0
        conv[i] = float(np.linalg.norm(v)) * (sign if sign != 0 else 1.0)
    return conv


def show_dfnd_legend(view, topography=None, *, families=None):
    """Show a colour legend for the DFND component families (Okabe-Ito palette)
    via ``view.scene.set_legend``. Defaults to the families present in the result,
    in canonical order. Returns the legend items.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')

    if families is None:
        present = {c.family for c in dfnd_data.dfn.components.wet}
        order = (fam.POCKET, fam.VOID, fam.CHANNEL, fam.PERCOLATING)
        families = [f for f in order if f in present]

    items = [
        {'label': str(f), 'color': _TYPE_PALETTE.get(f, 0x888888)} for f in families
    ]
    view.scene.set_legend(items)
    return items


def show_dfnd_pharmacophore(
    view,
    topography=None,
    *,
    component_ids=None,
    component_types=fam.PRIMARY_WET_FAMILIES,
    tag_prefix='dfnd-pharm',
):
    """Place an interaction-site glyph at each cavity's centre, typed by the
    dominant physicochemical character of its lining (positive/negative/
    hydrophobic/acceptor) via ``molsysmt.physchem`` + ``view.shapes.add_interaction_sites``
    — a pharmacophore/druggability map (see component_visualization.md §9). Skips
    components with no chemistry (dummy systems). Returns the layer, or ``None``.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')

    atom_kinds = _atom_pharmacophore_kinds(getattr(view, '_molsys', None))
    if atom_kinds is None:
        return None  # no chemistry (dummy system)

    from collections import Counter

    centers, kinds = [], []
    for comp in dfnd_data.dfn.components.wet:
        if component_types and comp.family not in component_types:
            continue
        if component_ids is not None and comp.component_id not in component_ids:
            continue
        if getattr(comp, 'center', None) is None:
            continue
        lining = []
        for atom in indices_in_space(
            getattr(comp, 'atom_indices', None), space=MOLECULAR_SYSTEM
        ):
            if 0 <= atom < len(atom_kinds) and atom_kinds[atom] is not None:
                lining.append(atom_kinds[atom])
        if not lining:
            continue
        centers.append(list(comp.center))
        kinds.append(Counter(lining).most_common(1)[0][0])

    if not centers:
        return None
    add_sites = getattr(
        getattr(view.shapes, 'interaction_sites', None),
        'add_interaction_sites',
        view.shapes.add_interaction_sites,
    )
    return add_sites(
        centers=puw.quantity(np.array(centers, dtype=float), 'angstroms'),
        kinds=kinds,
        tag=tag_prefix,
        layer_tag=tag_prefix,
        skip_digestion=True,
    )


def show_dfnd_convexity(view, topography=None, *, radius=0.8, palette='coolwarm'):
    """Colour the molecular surface by local convexity (ridges hot, valleys cold)
    via ``view.whole.set_color_by_values``. Convexity is computed per atom from the
    DFND coordinates; a convexity/protrusion heatmap (see
    devguide/DFND/component_visualization.md §7). Returns the per-atom values.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')

    coords = np.asarray(dfnd_data.mesh.atoms.coords, dtype=float)
    convexity = _atom_convexity(coords, radius=radius)
    index_map = np.asarray(
        getattr(dfnd_data.mesh.atoms, 'index_map', np.arange(len(coords)))
    )

    molsys = getattr(view, '_molsys', None)
    if molsys is not None:
        import molsysmt as msm

        n_atoms = int(msm.get(molsys, n_atoms=True))
        values = np.zeros(n_atoms)
        valid = index_map < n_atoms
        values[index_map[valid]] = convexity[valid]
    else:
        values = convexity  # assume DFND atom order == molecular-system order

    view.whole.set_color_by_values(values, element='atom', palette=palette)
    return values


def _affinity_color_for_scalars(hydrophobicity, charge):
    """Classify a residue's (hydrophobicity, charge) into an affinity colour."""
    if charge is not None and charge > 0.5:
        return _AFFINITY_POSITIVE
    if charge is not None and charge < -0.5:
        return _AFFINITY_NEGATIVE
    if hydrophobicity is None:
        return _AFFINITY_NEUTRAL
    return _AFFINITY_HYDROPHOBIC if hydrophobicity > 0 else _AFFINITY_POLAR


def _atom_affinity_colors(molsys):
    """Per-(molsys)atom affinity colour from ``molsysmt.physchem`` (hydrophobicity
    + charge by residue). Returns a list indexed by molsys atom index, or ``None``
    if the chemistry is unavailable (e.g. dummy-atom systems where physchem has no
    DUM entry — see molsysmt pending proposal physchem_support_dummy_atoms).
    """
    if molsys is None:
        return None
    try:
        import molsysmt as msm
        from molsysmt import physchem

        from topomt import pyunitwizard as _puw

        def _mags(q):
            try:
                return np.asarray(_puw.get_value(q), dtype=float)
            except Exception:
                return np.asarray(q, dtype=float)

        hydro = _mags(physchem.get_hydrophobicity(molsys, element='group'))
        charge = _mags(physchem.get_charge(molsys, element='group'))
        group_of_atom = np.asarray(
            msm.get(molsys, element='atom', group_index=True), dtype=int
        )
    except Exception:
        return None

    colors = []
    for g in group_of_atom:
        h = hydro[g] if 0 <= g < len(hydro) else None
        c = charge[g] if 0 <= g < len(charge) else None
        colors.append(_affinity_color_for_scalars(h, c))
    return colors


def _pharmacophore_kind_for_scalars(hydrophobicity, charge):
    """Classify a residue's (hydrophobicity, charge) into an interaction-site kind
    (positive / negative / hydrophobic / acceptor), or ``None`` if unknown."""
    if charge is not None and charge > 0.5:
        return 'positive'
    if charge is not None and charge < -0.5:
        return 'negative'
    if hydrophobicity is None:
        return None
    return 'hydrophobic' if hydrophobicity > 0 else 'acceptor'


def _atom_pharmacophore_kinds(molsys):
    """Per-(molsys)atom interaction-site kind from ``molsysmt.physchem``, or
    ``None`` if chemistry is unavailable (dummy systems). Mirrors
    ``_atom_affinity_colors`` but yields pharmacophore kinds."""
    if molsys is None:
        return None
    try:
        import molsysmt as msm
        from molsysmt import physchem

        from topomt import pyunitwizard as _puw

        def _mags(q):
            try:
                return np.asarray(_puw.get_value(q), dtype=float)
            except Exception:
                return np.asarray(q, dtype=float)

        hydro = _mags(physchem.get_hydrophobicity(molsys, element='group'))
        charge = _mags(physchem.get_charge(molsys, element='group'))
        group_of_atom = np.asarray(
            msm.get(molsys, element='atom', group_index=True), dtype=int
        )
    except Exception:
        return None

    kinds = []
    for g in group_of_atom:
        h = hydro[g] if 0 <= g < len(hydro) else None
        c = charge[g] if 0 <= g < len(charge) else None
        kinds.append(_pharmacophore_kind_for_scalars(h, c))
    return kinds


def _mouth_cap_face_ids(comp, raw):
    """Return canonical face IDs for a component mouth-cap cluster."""
    external_links = {e['external_link_id']: e for e in raw.get('external_links', [])}
    face_ids = []
    for link_id in getattr(comp, 'external_link_ids', None) or []:
        link = external_links.get(link_id)
        if link is not None:
            face_ids.extend(int(face_id) for face_id in link.get('face_ids', []))
    return face_ids


def carve_voids(
    view, topography=None, *, component_ids=None, component_types=(fam.VOID,), fade=0.85
):
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
        focus_atoms.update(
            indices_in_space(
                getattr(comp, 'atom_indices', None), space=MOLECULAR_SYSTEM
            )
        )

    if not focus_atoms:
        return None
    ordered = sorted(focus_atoms)
    view.focus_with_fade(ordered, fade=fade)
    return ordered


def show_dfnd_labels(
    view,
    topography=None,
    *,
    component_ids=None,
    component_types=fam.PRIMARY_WET_FAMILIES,
    tag_prefix='dfnd-label',
):
    """Label each component in the scene with its id, family, mouth count and
    solvent volume, anchored at its lining-atom centroid via ``view.annotations``.

    A scene legend per component (see
    devguide/DFND/component_visualization_implementation.md, Phase 5). Returns the
    created annotation layers, or ``None`` if no component matched.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')

    try:
        view.annotations.delete(tag_prefix, skip_digestion=True)
    except Exception:
        pass

    layers = []
    for comp in dfnd_data.dfn.components.wet:
        if component_types and comp.family not in component_types:
            continue
        if component_ids is not None and comp.component_id not in component_ids:
            continue
        atoms = indices_in_space(
            getattr(comp, 'atom_indices', None), space=MOLECULAR_SYSTEM
        )
        if not atoms:
            continue

        n_mouths = int(getattr(comp, 'n_mouths', 0) or 0)
        volume = getattr(comp, 'volume_solvent_estimate', None)
        parts = [str(comp.component_id), str(comp.family)]
        if n_mouths:
            parts.append(f'{n_mouths} mouth' + ('s' if n_mouths != 1 else ''))
        if volume:
            parts.append(f'{_angstrom3_from_nm3(volume):.0f} Å³')
        text = ' · '.join(parts)

        layer = view.annotations.add_annotation(
            text=text,
            kind='label',
            atom_indices=atoms,
            tag=f'{tag_prefix}:{comp.component_id}',
            layer_tag=tag_prefix,
            skip_digestion=True,
        )
        layers.append(layer)

    if not layers:
        return None
    return layers[0] if len(layers) == 1 else layers


def _render_dfnd_component_layers(
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
    face_color_mode: str = 'component',
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
          family's default mode (channel->pipe, pocket/void->envelope).
        - 'tetrahedra': Volumetric Delaunay tetrahedra.
        - 'cloud': Approximate iso-surface from residence spheres.
        - 'envelope': Volumetric blob plus a gate ring at each mouth (a void
          shows only the blob, a pocket adds its single mouth ring).
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
        - 'scaffold': Dry-core 'spine' — the minimum spanning tree of each dry
          component's atoms as thick cylinders.
        - 'affinity_spheres': Residence spheres coloured by the dominant
          physicochemical affinity of the lining (hydrophobic/polar/charged),
          from molsysmt.physchem; neutral for dummy systems.
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
    face_color_mode : {'component', 'permeability', 'role', 'gate_margin'}, default 'component'
        For 'tetrahedra': colour faces by component, permeability class, semantic
        role, or gate margin.
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
            res = _render_dfnd_component_layers(
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
                face_color_mode=face_color_mode,
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
        colors = []
        alphas = []
        labels = []
        selected_tetra_ids = set()
        selected_tetra_order = []
        tetra_to_color = {}
        tetra_to_component = {}

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
                colors.append(color)
                alphas.append(alpha)
                selected_tetra_ids.add(tid)
                selected_tetra_order.append(tid)
                tetra_to_color[tid] = color
                tetra_to_component[tid] = comp_id
                lbl = (
                    f'Component: {comp_id} ({comp.family}) | '
                    f'Tetrahedron {tid} | Vol: {vol_a:.1f} Å³'
                )
                labels.append(lbl)

        geometry = tetrahedra_geometry(topography, selected_tetra_order)
        if not geometry.atom_quads:
            return None

        face_meta = (
            _dfnd_face_meta(
                topography,
                selected_tetra_ids,
                colors_by_tetrahedron=tetra_to_color,
                components_by_tetrahedron=tetra_to_component,
                face_color_mode=face_color_mode,
            )
            if draw_faces
            else []
        )

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
            geometry = component_residence_sphere_geometry(
                topography, comp, use_resident_nodes=use_resident_nodes
            )
            if not geometry.centers:
                continue

            tag = f'{tag_prefix}:{comp_id}'
            layer = add_pocket_blob(
                view,
                geometry,
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

            path_geometry, bottleneck_index = (
                component_centerline_geometry(topography, comp)
                if comp.family == fam.CHANNEL and comp.raw_record is not None
                else (None, -1)
            )

            if path_geometry is None or not path_geometry.centers:
                geometry = component_residence_sphere_geometry(
                    topography, comp, use_resident_nodes=use_resident_nodes
                )
                if not geometry.centers:
                    continue
                layer = add_pocket_blob(
                    view,
                    geometry,
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

            tube = add_channel_tube(
                view,
                path_geometry,
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
            path_rings = centerline_ring_geometry(topography, comp)
            neck = bottleneck_index
            marker_geometry = RingGeometry(
                (path_rings.centers[neck],),
                (path_rings.normals[neck],),
                (path_rings.radii[neck],),
                path_rings.unit,
                (path_rings.refs[neck],),
            )
            marker = add_rings(
                view,
                marker_geometry,
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
        for comp in selected_components:
            comp_id = comp.component_id
            if comp.family != fam.CHANNEL or comp.raw_record is None:
                continue
            geometry = centerline_ring_geometry(topography, comp)
            if not geometry.centers:
                continue
            layer = add_rings(
                view,
                geometry,
                colors=[_hole_clearance_color(float(r)) for r in geometry.radii],
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

    elif representation == 'envelope':
        # Volumetric blob + a gate ring at each mouth: a void shows just the blob
        # (0 mouths), a pocket adds its single mouth ring, making them
        # distinguishable. See implementation plan (Phase 1).
        raw = dfnd_data.raw
        for comp in selected_components:
            comp_id = comp.component_id
            geometry = component_residence_sphere_geometry(
                topography, comp, use_resident_nodes=use_resident_nodes
            )
            if geometry.centers:
                layers.append(
                    add_pocket_blob(
                        view,
                        geometry,
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
                )

            mouth_geometry = mouth_ring_geometry(topography, comp)
            if mouth_geometry.centers:
                layers.append(
                    add_rings(
                        view,
                        mouth_geometry,
                        colors=[_MOUTH_ACCENT] * len(mouth_geometry.centers),
                        alpha=min(1.0, alpha + 0.3),
                        tag=f'{tag_prefix}:{comp_id}-mouths',
                        layer_tag=tag_prefix,
                        name=f'{name} {comp_id} mouths',
                        skip_digestion=True,
                    )
                )

            # Translucent portal cap over the canonical mouth face cluster.
            cap_geometry = face_geometry(
                topography, face_ids=_mouth_cap_face_ids(comp, raw)
            )
            if cap_geometry.atom_triplets:
                layers.append(
                    add_indexed_triangles(
                        view,
                        cap_geometry,
                        colors=[_MOUTH_ACCENT] * len(cap_geometry.atom_triplets),
                        alpha=min(0.4, alpha),
                        tag=f'{tag_prefix}:{comp_id}-cap',
                        layer_tag=tag_prefix,
                        skip_digestion=True,
                    )
                )

        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'scaffold':
        # Dry-core 'spine': the minimum spanning tree of each dry component's
        # atoms drawn as thick cylinders (the mechanical scaffold). See
        # devguide/DFND/component_visualization.md §7.
        for comp in dfnd_data.dfn.components.dry:
            comp_id = comp.component_id
            if component_ids is not None and comp_id not in component_ids:
                continue
            geometry = scaffold_geometry(topography, comp)
            if not geometry.refs:
                continue
            layers.append(
                add_segments(
                    view,
                    geometry,
                    radius=puw.quantity(0.4, 'angstroms'),
                    color=_TYPE_PALETTE[fam.DRY_BANK],
                    tag=f'{tag_prefix}:{comp_id}',
                    layer_tag=tag_prefix,
                    skip_digestion=True,
                )
            )

        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'affinity_spheres':
        # Residence spheres coloured by the dominant physicochemical affinity of
        # the component's lining (hydrophobic / polar / charged) — a druggability
        # map inside the cavity. Chemistry from molsysmt.physchem via the view's
        # molecular system; falls back to neutral for dummy systems (no DUM in
        # physchem). See component_visualization.md §9.
        molsys = getattr(view, '_molsys', None)
        atom_colors = _atom_affinity_colors(molsys)
        for comp in selected_components:
            comp_id = comp.component_id
            geometry = component_residence_sphere_geometry(
                topography, comp, use_resident_nodes=use_resident_nodes
            )
            if not geometry.centers:
                continue

            color = _AFFINITY_NEUTRAL
            if atom_colors is not None:
                from collections import Counter

                lining = []
                for atom in indices_in_space(
                    getattr(comp, 'atom_indices', None), space=MOLECULAR_SYSTEM
                ):
                    if 0 <= atom < len(atom_colors):
                        lining.append(atom_colors[atom])
                if lining:
                    color = Counter(lining).most_common(1)[0][0]

            layers.append(
                add_sphere_set(
                    view,
                    geometry,
                    color_alpha_spheres=color,
                    alpha_alpha_spheres=alpha,
                    tag=f'{tag_prefix}:{comp_id}',
                    layer_tag=tag_prefix,
                    skip_digestion=True,
                )
            )

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
                geometry = component_residence_sphere_geometry(
                    topography, comp, use_resident_nodes=use_resident_nodes
                )
            else:
                geometry = component_alpha_sphere_geometry(
                    topography, comp, use_resident_nodes=use_resident_nodes
                )
            if not geometry.centers:
                continue

            tag = f'{tag_prefix}:{comp_id}'
            layer = add_sphere_set(
                view,
                geometry,
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
        # parameters['probe_radius'] is in nm (DFND kernel units); residence
        # geometry is also nm, so the probe sphere radius stays in nm.
        if puw.is_quantity(probe_radius):
            probe_radius = float(puw.get_value(probe_radius, to_unit='nm'))
        else:
            probe_radius = float(probe_radius)

        for comp in selected_components:
            comp_id = comp.component_id
            color = resolved_colors[comp_id]
            residence_geometry = component_residence_sphere_geometry(
                topography, comp, use_resident_nodes=use_resident_nodes
            )
            geometry = probe_sphere_geometry(residence_geometry, probe_radius)
            if not geometry.centers:
                continue
            tag = f'{tag_prefix}:{comp_id}'
            layer = add_uniform_spheres(
                view,
                geometry,
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
            atom_indices = indices_in_space(
                getattr(comp, 'atom_indices', None), space=MOLECULAR_SYSTEM
            )
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
        body_labels = _body_labels_from_dry(list(dfnd_data.dfn.components.dry))
        for comp in selected_components:
            comp_id = comp.component_id
            atom_indices = indices_in_space(
                getattr(comp, 'atom_indices', None), space=MOLECULAR_SYSTEM
            )
            if not atom_indices:
                continue

            by_body = {}
            for atom in atom_indices:
                body = body_labels.get(int(atom), -1)
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
        # Render shared contact coast faces between wet and dry.
        color_by_face_id = {}
        label_by_face_id = {}

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
                face_id = int(face['face_id'])
                color_by_face_id.setdefault(face_id, color)
                label_by_face_id.setdefault(
                    face_id,
                    (
                        f'Coast Face {face_id} | '
                        f'Wet: {face["wet_component_id"]} | '
                        f'Dry: {face["dry_component_id"]} | '
                        f'Area: {_angstrom2_from_nm2(face.get("area", 0.0)):.2f} Å²'
                    ),
                )

        geometry = face_geometry(topography, face_ids=color_by_face_id)
        if not geometry.atom_triplets:
            return None

        return add_indexed_triangles(
            view,
            geometry,
            colors=[color_by_face_id[ref.entity_id] for ref in geometry.refs],
            alpha=alpha,
            labels=[label_by_face_id[ref.entity_id] for ref in geometry.refs],
            tag=tag_prefix,
            layer_tag=tag_prefix,
            skip_digestion=True,
        )

    elif representation == 'graph':
        # Render the component-filtered DFN connectivity graph.
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
        components_by_id = {comp.component_id: comp for comp in selected_components}
        component_refs = {
            tid: EntityRef(
                kind='tetrahedron',
                entity_id=tid,
                tetrahedron_ids=(tid,),
                support_key=getattr(
                    components_by_id[node_to_comp[tid]], 'support_key', None
                ),
                component_key=getattr(
                    components_by_id[node_to_comp[tid]], 'component_key', None
                ),
            )
            for tid in ordered_nodes
        }
        node_geometry = tetrahedron_centers(
            topography, ordered_nodes, component_refs=component_refs
        )
        colors_list = [resolved_colors[node_to_comp[tid]] for tid in ordered_nodes]

        if not node_geometry.coordinates:
            return None

        node_layer = add_point_spheres(
            view,
            node_geometry,
            radius=puw.quantity(0.03, 'nm'),
            color=colors_list,
            alpha=alpha,
            tag=f'{tag_prefix}-nodes',
            layer_tag=f'{tag_prefix}-nodes',
            skip_digestion=True,
        )

        edge_geometry, _mouth_geometry = dfn_graph_segments(
            topography, ordered_nodes, include_mouths=False
        )

        edge_layer = None
        if edge_geometry.refs:
            edge_layer = add_segments(
                view,
                edge_geometry,
                radius=puw.quantity(0.015, 'nm'),
                color=0x3B82F6,
                tag=f'{tag_prefix}-edges',
                layer_tag=f'{tag_prefix}-edges',
                skip_digestion=True,
            )

        return {
            'nodes': node_layer,
            'edges': edge_layer,
            'node_geometry': node_geometry,
            'edge_geometry': edge_geometry,
            'n_nodes': len(node_geometry.refs),
            'n_edges': len(edge_geometry.refs),
        }


def _selected_component_ids(topography, kwargs):
    data = getattr(topography, 'dfnd', None)
    if data is None:
        return tuple(kwargs.get('component_ids') or ())
    requested = kwargs.get('component_ids')
    requested = None if requested is None else set(requested)
    component_types = kwargs.get('component_types', fam.PRIMARY_WET_FAMILIES)
    interfaces_only = kwargs.get('interfaces_only', False)
    selected = []
    if kwargs.get('show_wet', True):
        for comp in data.dfn.components.wet:
            if component_types and comp.family not in component_types:
                continue
            if requested is not None and comp.component_id not in requested:
                continue
            if interfaces_only and not getattr(comp, 'is_interface', False):
                continue
            selected.append(comp.component_id)
    if kwargs.get('show_dry', False) and not interfaces_only:
        for comp in data.dfn.components.dry:
            if requested is None or comp.component_id in requested:
                selected.append(comp.component_id)
    return tuple(selected)


def show_dfnd_components(view, topography=None, **kwargs):
    """Render DFND components and return a uniform ``RenderResult``."""
    resolved = _resolve_topography(view, topography)
    representation = {'spheres': 'residence_spheres', 'skeleton': 'graph'}.get(
        kwargs.get('representation', 'tetrahedra'),
        kwargs.get('representation', 'tetrahedra'),
    )
    operation_key = f'components:{kwargs.get("tag_prefix", "dfnd-comp")}'
    clear_previous_render_result(view, operation_key)
    raw = _render_dfnd_component_layers(view, resolved, **kwargs)
    result = render_result(
        representation,
        raw,
        selected_ids=_selected_component_ids(resolved, kwargs),
    )
    return remember_render_result(view, operation_key, result)
