"""show_dfnd_components: typed components in multiple representations."""

from typing import Any

import numpy as np

from topomt import pyunitwizard as puw
from topomt.dfnd import families as fam
from topomt.dfnd.selectors import select_faces

from ..geometry import (
    EntityRef,
    PointGeometry,
    RingGeometry,
    SegmentGeometry,
    SphereGeometry,
    centerline_ring_geometry,
    component_alpha_sphere_geometry,
    component_branch_geometries,
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
    _angstrom_from_nm,
    _dfnd_edge_meta,
    _dfnd_face_label,
    _dfnd_face_meta,
    _resolve_topography,
    face_color_from_semantics,
    face_semantics,
)
from .adapters import (
    add_channel_tube,
    add_indexed_triangles,
    add_pocket_blob,
    add_point_spheres,
    add_rings,
    add_scalar_isosurface,
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
_PIPE_STYLE_SOLID = 'solid'
_PIPE_STYLE_PROFILE = 'profile'
_PIPE_STYLE_SOLID_RINGS = 'solid_rings'
_PIPE_STYLE_LUMEN = 'lumen'
_PIPE_STYLE_RIBBON = 'ribbon'
_PIPE_STYLES = {
    _PIPE_STYLE_SOLID,
    _PIPE_STYLE_PROFILE,
    _PIPE_STYLE_SOLID_RINGS,
    _PIPE_STYLE_LUMEN,
    _PIPE_STYLE_RIBBON,
}
_CHANNEL_REPRESENTATION_ALIASES = {
    'channel_tube': ('tube', _PIPE_STYLE_SOLID),
    'channel_solid': ('tube', _PIPE_STYLE_SOLID),
    'channel_profile': ('tube', _PIPE_STYLE_PROFILE),
    'channel_lumen': ('tube', _PIPE_STYLE_LUMEN),
    'channel_tunnel': ('tube', _PIPE_STYLE_LUMEN),
    'channel_ribbon': ('tube', _PIPE_STYLE_RIBBON),
    'groove_ribbon': ('tube', _PIPE_STYLE_RIBBON),
    'channel_blob': ('cloud', None),
    'channel_wire_blob': ('wire_contour', None),
}

# Deprecated named modes -> grounded primitive (decision: the component renderer's
# vocabulary is grounded geometry, names live in the feature layer; see
# devguide/DFND/viewer_grounded_named_split.md). These collapse exact duplicates;
# the old names resolve to the grounded primitive (back-compat) before dispatch.
_REPRESENTATION_ALIASES = {
    'pipe': 'tube',  # variable-radius tube along the centerline (was the canonical name)
    'interface_links': 'links',  # segments between linked components (grounded)
    'pocket_depth_map': 'depth_map',  # depth field over the residence envelope
    'groove_depth_profile': 'depth_map',
    'groove_walls': 'lining_surface',  # component lining atoms as a surface
    'groove_width_profile': 'width_profile',  # HOLE width rings along the centerline
}
# Affinity (physicochemical) colours for the 'affinity_spheres' druggability map,
# derived from molsysmt.physchem hydrophobicity (Eisenberg) + charge (pH7).
_AFFINITY_HYDROPHOBIC = _OKABE_ITO['orange']  # drug-favourable nonpolar
_AFFINITY_POLAR = _OKABE_ITO['sky_blue']  # polar / H-bonding
_AFFINITY_POSITIVE = _OKABE_ITO['blue']  # positively charged
_AFFINITY_NEGATIVE = _OKABE_ITO['vermillion']  # negatively charged
_AFFINITY_NEUTRAL = _OKABE_ITO['grey']  # unknown / dummy (e.g. DUM)

_AUTO_FALLBACK_REPRESENTATION = 'cloud'

# --- Grounded, name-free component rendering -----------------------------------
# The component renderer keys on ``component.signature`` (the grounded topological
# handle: resident / exposed / n_mouths), NEVER on ``component.family`` -- so it
# survives the retirement of ``family`` from the kernel. Each wet component falls in
# one render *bucket*, derived from the signature; the bucket -- not a family name --
# drives the visual language (representation + colour). The buckets reproduce the
# legacy family mapping exactly (void=enclosed, pocket=mouthed, channel=through,
# percolating=through_open, every non-resident form=transient), so behaviour is
# preserved. See dfnd/components.py WetComponent.signature and
# devguide/DFND/component_visualization_implementation.md.


def _signature_of(component):
    sig = getattr(component, 'signature', None)
    return sig if isinstance(sig, dict) else None


def _render_bucket(component):
    """Grounded render bucket from the signature (resident/exposed/n_mouths). A
    non-wet component (no signature, e.g. a dry bank) is ``transient``."""
    sig = _signature_of(component)
    if sig is None or not sig.get('resident', False):
        return 'transient'
    if sig.get('exposed'):
        return 'through_open'  # percolating: resident but no enclosing wall
    n = int(sig.get('n_mouths', 0) or 0)
    if n >= 2:
        return 'through'  # >=2 mouths -> through passage (was channel)
    if n == 1:
        return 'mouthed'  # one mouth (was pocket)
    return 'enclosed'  # no mouth (was void)


# bucket -> visual language. Channels (through) read as tubes; mouthed/enclosed as
# volumetric blobs; through_open (percolating) + transient keep the auto fallback,
# matching the legacy per-family map (which omitted them).
_REPRESENTATION_BY_BUCKET = {
    'through': 'tube',
    'mouthed': 'envelope',
    'enclosed': 'envelope',
}
_COLOR_BY_BUCKET = {
    'through': _OKABE_ITO['orange'],  # was fam.CHANNEL
    'through_open': _OKABE_ITO['reddish_purple'],  # was fam.PERCOLATING
    'mouthed': _OKABE_ITO['blue'],  # was fam.POCKET
    'enclosed': _OKABE_ITO['sky_blue'],  # was fam.VOID
}
_BUCKET_LABEL = {
    'enclosed': 'enclosed cavity',
    'mouthed': 'one-mouth concavity',
    'through': 'through passage',
    'through_open': 'percolating',
    'transient': 'transient',
}

# Back-compat shim for the ``component_types`` / ``color_palette`` selectors, whose
# historical values are legacy family names. This table -- the only place still tied
# to those names -- maps a legacy selector to the grounded bucket(s) it covers, so a
# caller passing ``fam.PRIMARY_WET_FAMILIES`` keeps working without the renderer ever
# reading ``component.family``. New callers can pass grounded buckets directly.
_SELECTOR_BUCKETS = {
    fam.CHANNEL: {'through'},
    fam.PERCOLATING: {'through_open'},
    fam.POCKET: {'mouthed'},
    fam.VOID: {'enclosed'},
}


def _matches_component_types(component, component_types):
    """Whether ``component_types`` selects this component, decided from the grounded
    bucket (never from comp.family). Accepts grounded buckets or, for back-compat,
    legacy family-name selectors."""
    if not component_types:
        return True
    bucket = _render_bucket(component)
    for selector in component_types:
        if selector == bucket or bucket in _SELECTOR_BUCKETS.get(selector, ()):
            return True
    return False


def _representation_for(component):
    return _REPRESENTATION_BY_BUCKET.get(
        _render_bucket(component), _AUTO_FALLBACK_REPRESENTATION
    )


def _color_for(component):
    """Grounded by-type colour. A dry bank (no signature) keeps its structural
    DRY_BANK colour -- the dry side is outside the wet-family retirement."""
    if _signature_of(component) is None:
        return _TYPE_PALETTE.get(getattr(component, 'family', None), 0x888888)
    return _COLOR_BY_BUCKET.get(_render_bucket(component), 0x888888)


def _palette_color_override(color_palette, component):
    """A per-category colour override from ``color_palette``, by grounded bucket or
    (back-compat) by a legacy family-name key, without reading comp.family."""
    bucket = _render_bucket(component)
    if bucket in color_palette:
        return color_palette[bucket]
    for selector, buckets in _SELECTOR_BUCKETS.items():
        if bucket in buckets and selector in color_palette:
            return color_palette[selector]
    return None
_COMPONENT_REPRESENTATIONS = {
    'auto',
    'tetrahedra',
    'cloud',
    'envelope',
    'wire_contour',
    'clearance_map',
    'clearance_wire',
    'scalar_isosurface',
    'pocket_depth_map',
    # grounded primitives (deprecated named modes above resolve here)
    'depth_map',
    'lining_surface',
    'width_profile',
    'links',
    'shape_ellipsoids',
    'tube',
    'pipe',
    'channel_tube',
    'channel_solid',
    'channel_profile',
    'channel_lumen',
    'channel_tunnel',
    'channel_ribbon',
    'groove_ribbon',
    'groove_floor',
    'groove_walls',
    'groove_width_profile',
    'groove_depth_profile',
    'channel_blob',
    'channel_wire_blob',
    'rings',
    'mouth_rings',
    'bottleneck_rings',
    'residence_spheres',
    'alpha_spheres',
    'probe_centers',
    'surface',
    'contact_sheet',
    'scaffold',
    'affinity_spheres',
    'coast_faces',
    'dry_interface_faces',
    'dry_blocked_faces',
    'dry_depth_map',
    'dry_shell',
    'dry_cage',
    'semantic_faces',
    'permeable_faces',
    'impermeable_faces',
    'mouth_faces',
    'interface_faces',
    'interface_contact_faces',
    'interface_links',
    'interface_ribbon',
    'interface_lining_surface',
    'interface_surface',
    'mouth_stubs',
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
        present = {_render_bucket(c) for c in dfnd_data.dfn.components.wet}
        order = ('enclosed', 'mouthed', 'through', 'through_open')
        buckets = [b for b in order if b in present]
    else:
        # accept grounded buckets or (back-compat) legacy family-name selectors
        buckets = []
        for f in families:
            if f in _BUCKET_LABEL:
                buckets.append(f)
            else:
                buckets.extend(sorted(_SELECTOR_BUCKETS.get(f, ())))

    items = [
        {'label': _BUCKET_LABEL.get(b, str(b)), 'color': _COLOR_BY_BUCKET.get(b, 0x888888)}
        for b in buckets
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
        if not _matches_component_types(comp, component_types):
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



def show_dfnd_spikes(
    view,
    topography=None,
    *,
    radius=0.8,
    top_n=12,
    min_convexity=0.0,
    vector_length=0.25,
    palette='turbo',
    tag_prefix='dfnd-spikes',
):
    """Mark local convex protrusions with outward arrows.

    Convexity is computed from DFND atom coordinates. The final glyphs are
    rendered with MolSysViewer's generic displacement-vector primitive, so this
    function only decides which atoms are protrusion peaks and how long the
    outward marker should be. Coordinates and vectors are passed in nanometers.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')

    coords = np.asarray(dfnd_data.mesh.atoms.coords, dtype=float)
    if coords.size == 0:
        return None
    convexity = _atom_convexity(coords, radius=radius)
    selected = [
        int(index)
        for index in np.argsort(convexity)[::-1]
        if convexity[index] > float(min_convexity)
    ][: int(top_n)]
    if not selected:
        return None

    origins = coords[selected]
    center = coords.mean(axis=0)
    directions = origins - center
    lengths = np.linalg.norm(directions, axis=1)
    safe = lengths > 1e-12
    directions[~safe] = np.array([0.0, 0.0, 1.0])
    lengths[~safe] = 1.0
    directions = directions / lengths[:, None]

    selected_convexity = convexity[selected]
    max_convexity = float(np.max(selected_convexity)) if len(selected_convexity) else 1.0
    if max_convexity <= 0.0:
        scales = np.ones(len(selected))
    else:
        scales = np.clip(selected_convexity / max_convexity, 0.25, 1.0)
    vectors = directions * (float(vector_length) * scales)[:, None]

    index_map = np.asarray(
        getattr(dfnd_data.mesh.atoms, 'index_map', np.arange(len(coords)))
    )
    vector_shapes = getattr(view.shapes, 'vectors', None)
    add_vectors = (
        getattr(vector_shapes, 'add_displacement_vectors')
        if vector_shapes is not None
        else view.shapes.add_displacement_vectors
    )
    return add_vectors(
        origins=puw.quantity(origins, 'nm'),
        vectors=puw.quantity(vectors, 'nm'),
        atom_indices=[int(index_map[index]) for index in selected],
        color_by='norm',
        palette=palette,
        max_length=puw.quantity(vector_length, 'nm'),
        radius_scale=0.06,
        tag=tag_prefix,
        layer_tag=tag_prefix,
        skip_digestion=True,
    )


def _convex_peak_geometry(topography, *, radius=0.8, top_n=12, min_convexity=0.0):
    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')
    coords = np.asarray(dfnd_data.mesh.atoms.coords, dtype=float)
    if coords.size == 0:
        return PointGeometry((), 'nm', ())
    convexity = _atom_convexity(coords, radius=radius)
    selected = [
        int(index)
        for index in np.argsort(convexity)[::-1]
        if convexity[index] > float(min_convexity)
    ][: int(top_n)]
    index_map = np.asarray(
        getattr(dfnd_data.mesh.atoms, 'index_map', np.arange(len(coords)))
    )
    refs = tuple(
        EntityRef(
            kind='convex_peak',
            entity_id=int(index_map[index]),
            atom_indices=(int(index_map[index]),),
            metadata={'convexity': float(convexity[index])},
        )
        for index in selected
    )
    return PointGeometry(tuple(coords[selected]), 'nm', refs)


def show_dfnd_peak_patches(
    view,
    topography=None,
    *,
    radius=0.8,
    top_n=12,
    min_convexity=0.0,
    patch_radius=0.18,
    alpha=0.35,
    tag_prefix='dfnd-peak-patches',
):
    """Mark convex peak neighborhoods with translucent spherical patches."""
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    geometry = _convex_peak_geometry(
        topography, radius=radius, top_n=top_n, min_convexity=min_convexity
    )
    if not geometry.coordinates:
        return None
    return add_point_spheres(
        view,
        geometry,
        radius=puw.quantity(patch_radius, 'nm'),
        color=_OKABE_ITO['vermillion'],
        alpha=alpha,
        tag=tag_prefix,
        layer_tag=tag_prefix,
        skip_digestion=True,
    )


def show_dfnd_ridge_lines(
    view,
    topography=None,
    *,
    radius=0.8,
    top_n=12,
    min_convexity=0.0,
    line_radius=0.015,
    alpha=0.75,
    tag_prefix='dfnd-ridge-lines',
):
    """Connect convex peak markers into a diagnostic ridge-line scaffold."""
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    peaks = _convex_peak_geometry(
        topography, radius=radius, top_n=top_n, min_convexity=min_convexity
    )
    if len(peaks.coordinates) < 2:
        return None
    order = _ordered_interface_points(list(peaks.coordinates))
    starts = []
    ends = []
    refs = []
    for left, right in zip(order[:-1], order[1:], strict=True):
        starts.append(peaks.coordinates[left])
        ends.append(peaks.coordinates[right])
        refs.append(
            EntityRef(
                kind='ridge_line',
                entity_id=f'{peaks.refs[left].entity_id}-{peaks.refs[right].entity_id}',
                atom_indices=(
                    int(peaks.refs[left].entity_id),
                    int(peaks.refs[right].entity_id),
                ),
            )
        )
    geometry = SegmentGeometry(tuple(starts), tuple(ends), 'nm', tuple(refs))
    return add_segments(
        view,
        geometry,
        radius=puw.quantity(line_radius, 'nm'),
        color=_OKABE_ITO['vermillion'],
        alpha=alpha,
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



def _semantic_face_filters(representation: str):
    if representation == 'permeable_faces':
        return {'permeability': {'permeable'}, 'roles': None, 'color_mode': 'permeability'}
    if representation == 'impermeable_faces':
        return {
            'permeability': {'non_permeable'},
            'roles': None,
            'color_mode': 'permeability',
        }
    if representation == 'mouth_faces':
        return {'permeability': None, 'roles': {'mouth_face'}, 'color_mode': 'role'}
    if representation == 'interface_faces':
        return {'permeability': None, 'roles': {'coast_face'}, 'color_mode': 'role'}
    return {'permeability': None, 'roles': None, 'color_mode': 'role'}


def _component_face_payloads(topography, selected_components, representation: str):
    filters = _semantic_face_filters(representation)
    selected_tetrahedra = set()
    components_by_tetrahedron = {}
    for comp in selected_components:
        for tetrahedron_id in _component_node_indices(comp, use_resident_nodes=False):
            selected_tetrahedra.add(int(tetrahedron_id))
            components_by_tetrahedron[int(tetrahedron_id)] = comp.component_id

    color_by_face_id = {}
    label_by_face_id = {}
    for face in select_faces(topography, permeability_state=filters['permeability']):
        owner = int(face.get('owner_tetrahedron_id', -1))
        neighbor = int(face.get('neighbor_tetrahedron_id', -1))
        if owner not in selected_tetrahedra and neighbor not in selected_tetrahedra:
            continue
        semantics = face_semantics(
            topography,
            face,
            components_by_tetrahedron=components_by_tetrahedron,
        )
        if filters['roles'] is not None and semantics['role'] not in filters['roles']:
            continue
        permeability = face.get('permeability_state', 'unknown')
        face_id = int(face.get('face_id'))
        color_by_face_id[face_id] = face_color_from_semantics(
            semantics,
            permeability=permeability,
            mode=filters['color_mode'],
        )
        label_by_face_id[face_id] = _dfnd_face_label(
            face, face_id, semantics=semantics
        )
    return color_by_face_id, label_by_face_id




def _component_depth_values(component, geometry):
    depth_by_tetrahedron = getattr(component, 'topological_depth', {}) or {}
    return [
        float(depth_by_tetrahedron.get(int(ref.entity_id), 0))
        for ref in geometry.refs
    ]


def _interface_link_geometry(topography, selected_components) -> SegmentGeometry:
    selected_ids = {comp.component_id for comp in selected_components}
    relevant_faces = []
    tetrahedron_ids = set()
    for face in topography.dfnd.dfn.components.coast_faces:
        if (
            face.get('wet_component_id') not in selected_ids
            and face.get('dry_component_id') not in selected_ids
        ):
            continue
        wet_tetrahedron = int(face['wet_tetrahedron_id'])
        dry_tetrahedron = int(face['dry_tetrahedron_id'])
        relevant_faces.append((face, wet_tetrahedron, dry_tetrahedron))
        tetrahedron_ids.add(wet_tetrahedron)
        tetrahedron_ids.add(dry_tetrahedron)
    if not relevant_faces:
        return SegmentGeometry((), (), 'nm', ())

    centers = tetrahedron_centers(topography, sorted(tetrahedron_ids))
    center_by_id = {
        int(ref.entity_id): point
        for point, ref in zip(centers.coordinates, centers.refs, strict=True)
    }
    starts = []
    ends = []
    refs = []
    for face, wet_tetrahedron, dry_tetrahedron in relevant_faces:
        if wet_tetrahedron not in center_by_id or dry_tetrahedron not in center_by_id:
            continue
        starts.append(center_by_id[wet_tetrahedron])
        ends.append(center_by_id[dry_tetrahedron])
        refs.append(
            EntityRef(
                kind='interface_link',
                entity_id=face.get('face_id'),
                tetrahedron_ids=(wet_tetrahedron, dry_tetrahedron),
                component_key=None,
                metadata={
                    'wet_component_id': face.get('wet_component_id'),
                    'dry_component_id': face.get('dry_component_id'),
                    'face_id': face.get('face_id'),
                },
            )
        )
    return SegmentGeometry(tuple(starts), tuple(ends), 'nm', tuple(refs))



def _ordered_interface_points(points: list[tuple[float, float, float]]) -> list[int]:
    if len(points) <= 2:
        return list(range(len(points)))
    array = np.asarray(points, dtype=float)
    centered = array - array.mean(axis=0)
    try:
        _, _, vh = np.linalg.svd(centered, full_matrices=False)
    except np.linalg.LinAlgError:
        return list(range(len(points)))
    axis = vh[0]
    projection = centered @ axis
    return [int(index) for index in np.argsort(projection)]


def _interface_ribbon_geometries(topography, selected_components):
    selected_ids = {comp.component_id for comp in selected_components}
    component_faces = {}
    for face in topography.dfnd.dfn.components.coast_faces:
        wet_id = face.get('wet_component_id')
        dry_id = face.get('dry_component_id')
        for component_id in (wet_id, dry_id):
            if component_id in selected_ids:
                component_faces.setdefault(component_id, []).append(face)

    geometries = []
    for component_id, faces in component_faces.items():
        face_ids = [int(face['face_id']) for face in faces]
        face_geom = face_geometry(topography, face_ids=face_ids)
        if len(face_geom.coordinates) < 2:
            continue

        centers = []
        radii = []
        refs = []
        face_by_id = {int(face['face_id']): face for face in faces}
        for triplet, ref in zip(face_geom.coordinates, face_geom.refs, strict=True):
            face = face_by_id.get(int(ref.entity_id), {})
            centers.append(tuple(float(value) for value in np.mean(triplet, axis=0)))
            area = float(face.get('area', 0.0) or 0.0)
            radii.append(max(0.018, min(0.055, np.sqrt(max(area, 0.0)) * 0.18)))
            refs.append(
                EntityRef(
                    kind='interface_ribbon',
                    entity_id=ref.entity_id,
                    tetrahedron_ids=(
                        int(face.get('wet_tetrahedron_id', -1)),
                        int(face.get('dry_tetrahedron_id', -1)),
                    ),
                    component_key=None,
                    metadata={
                        'component_id': component_id,
                        'wet_component_id': face.get('wet_component_id'),
                        'dry_component_id': face.get('dry_component_id'),
                        'face_id': int(ref.entity_id),
                    },
                )
            )

        order = _ordered_interface_points(centers)
        geometries.append(
            (
                component_id,
                SphereGeometry(
                    tuple(centers[index] for index in order),
                    tuple(radii[index] for index in order),
                    'nm',
                    tuple(refs[index] for index in order),
                ),
            )
        )
    return geometries


def _lerp_color(color_a: int, color_b: int, fraction: float) -> int:
    fraction = max(0.0, min(1.0, float(fraction)))
    ar, ag, ab = (color_a >> 16) & 0xFF, (color_a >> 8) & 0xFF, color_a & 0xFF
    br, bg, bb = (color_b >> 16) & 0xFF, (color_b >> 8) & 0xFF, color_b & 0xFF
    rr = round(ar + (br - ar) * fraction)
    rg = round(ag + (bg - ag) * fraction)
    rb = round(ab + (bb - ab) * fraction)
    return (rr << 16) | (rg << 8) | rb


def _dry_depth_color(depth, max_depth) -> int:
    if depth is None:
        return _OKABE_ITO['grey']
    if not max_depth or max_depth <= 0:
        return _OKABE_ITO['yellow']
    return _lerp_color(_OKABE_ITO['yellow'], _OKABE_ITO['vermillion'], depth / max_depth)


def _dry_depth_by_tetrahedron(selected_components) -> dict[int, int]:
    depths = {}
    for comp in selected_components:
        if getattr(comp, 'side', None) != 'dry':
            continue
        raw = getattr(comp, 'raw_record', None) or {}
        for tetrahedron_id, depth in raw.get('face_depth_by_tetrahedron', {}).items():
            if depth is None:
                continue
            depths[int(tetrahedron_id)] = int(depth)
    return depths


def _dry_face_payloads(topography, selected_components, representation: str):
    selected_tetrahedra = {
        int(tetrahedron_id)
        for comp in selected_components
        if getattr(comp, 'side', None) == 'dry'
        for tetrahedron_id in _component_node_indices(comp, use_resident_nodes=False)
    }
    if not selected_tetrahedra:
        return {}, {}

    depth_by_tetrahedron = _dry_depth_by_tetrahedron(selected_components)
    max_depth = max(depth_by_tetrahedron.values(), default=0)
    color_by_face_id = {}
    label_by_face_id = {}

    if representation in {'dry_interface_faces', 'dry_shell'}:
        for face in getattr(topography.dfnd.dfn.components, 'coast_faces', []):
            dry_tetrahedron = int(face.get('dry_tetrahedron_id', -1))
            if dry_tetrahedron not in selected_tetrahedra:
                continue
            face_id = int(face['face_id'])
            color_by_face_id[face_id] = (
                _TYPE_PALETTE[fam.DRY_BANK]
                if representation == 'dry_shell'
                else _OKABE_ITO['orange']
            )
            label_by_face_id[face_id] = (
                f'Dry shell face {face_id} | '
                if representation == 'dry_shell'
                else f'Dry interface face {face_id} | '
            ) + (
                f'Wet: {face.get("wet_component_id")} | '
                f'Dry: {face.get("dry_component_id")} | '
                f'Area: {_angstrom2_from_nm2(face.get("area", 0.0)):.2f} Å²'
            )
        if representation == 'dry_interface_faces':
            return color_by_face_id, label_by_face_id

    for face in select_faces(topography, permeability_state='non_permeable'):
        owner = int(face.get('owner_tetrahedron_id', -1))
        neighbor = int(face.get('neighbor_tetrahedron_id', -1))
        if owner not in selected_tetrahedra and neighbor not in selected_tetrahedra:
            continue
        face_id = int(face['face_id'])
        dry_depths = [
            depth_by_tetrahedron[tetrahedron_id]
            for tetrahedron_id in (owner, neighbor)
            if tetrahedron_id in depth_by_tetrahedron
        ]
        depth = min(dry_depths) if dry_depths else None
        color_by_face_id[face_id] = (
            _dry_depth_color(depth, max_depth)
            if representation == 'dry_depth_map'
            else _TYPE_PALETTE[fam.DRY_BANK]
            if representation == 'dry_shell'
            else _OKABE_ITO['vermillion']
        )
        depth_label = 'unknown' if depth is None else str(depth)
        label_by_face_id[face_id] = (
            f'Dry face {face_id} | permeability=non_permeable | '
            f'face_depth={depth_label} | tetrahedra={owner},{neighbor}'
        )
    return color_by_face_id, label_by_face_id


def _component_shape_ellipsoid_payload(topography, component, *, use_resident_nodes=True):
    """Return one PCA ellipsoid payload for a component in nm coordinates.

    The ellipsoid is a visual summary of spatial orientation and elongation. It is
    not a DFND classification criterion: axes come from the covariance of
    residence centers when available, otherwise from alpha-sphere centers.
    """
    geometry = component_residence_sphere_geometry(
        topography, component, use_resident_nodes=use_resident_nodes
    )
    if len(geometry.centers) < 2:
        geometry = component_alpha_sphere_geometry(
            topography, component, use_resident_nodes=False
        )
    if len(geometry.centers) < 2:
        return None

    points = np.asarray(geometry.centers, dtype=float)
    center = points.mean(axis=0)
    centered = points - center
    covariance = np.cov(centered, rowvar=False)
    if covariance.shape != (3, 3) or not np.all(np.isfinite(covariance)):
        return None
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1]
    values = np.maximum(values[order], 1e-6)
    vectors = vectors[:, order].T

    # Convert nm axes to Angstrom because MolSysViewer currently serializes
    # ellipsoid centers through unit conversion but leaves eigenvalues as raw
    # Mol* wire lengths.
    axes_angstrom = tuple(float(np.sqrt(value) * 10.0) for value in values)
    anisotropy = 0.0
    if axes_angstrom[0] > 0.0:
        anisotropy = (axes_angstrom[0] - axes_angstrom[-1]) / axes_angstrom[0]
    return {
        'center': center,
        'eigenvalues': axes_angstrom,
        'eigenvectors': tuple(tuple(float(x) for x in row) for row in vectors),
        'anisotropy': float(anisotropy),
    }

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



def _components_matching(
    dfnd_data,
    *,
    component_ids=None,
    component_types=None,
    interfaces_only=False,
):
    requested = None if component_ids is None else set(component_ids)
    matches = []
    for comp in dfnd_data.dfn.components.wet:
        if requested is not None and comp.component_id not in requested:
            continue
        if not _matches_component_types(comp, component_types):
            continue
        if interfaces_only and not getattr(comp, 'is_interface', False):
            continue
        matches.append(comp)
    return matches


def _normal_from_points(points) -> tuple[float, float, float]:
    array = np.asarray(points, dtype=float)
    if len(array) < 2:
        return (1.0, 0.0, 0.0)
    centered = array - array.mean(axis=0)
    try:
        _, _, vh = np.linalg.svd(centered, full_matrices=False)
    except np.linalg.LinAlgError:
        return (1.0, 0.0, 0.0)
    normal = np.asarray(vh[0], dtype=float)
    norm = float(np.linalg.norm(normal))
    if norm < 1e-10:
        return (1.0, 0.0, 0.0)
    return tuple(float(value) for value in normal / norm)


def _component_cutaway_payload(topography, component, *, interface_normal=False):
    geometry = component_residence_sphere_geometry(
        topography, component, use_resident_nodes=True
    )
    if not geometry.centers:
        geometry = component_alpha_sphere_geometry(
            topography, component, use_resident_nodes=False
        )
    if not geometry.centers:
        return None

    points = np.asarray(geometry.centers, dtype=float)
    center = tuple(float(value) for value in points.mean(axis=0))
    normal = None
    if interface_normal:
        link_geometry = _interface_link_geometry(topography, [component])
        vectors = []
        for start, end in zip(link_geometry.starts, link_geometry.ends, strict=True):
            vector = np.asarray(end, dtype=float) - np.asarray(start, dtype=float)
            norm = float(np.linalg.norm(vector))
            if norm > 1e-10:
                vectors.append(vector / norm)
        if vectors:
            averaged = np.mean(np.asarray(vectors), axis=0)
            norm = float(np.linalg.norm(averaged))
            if norm > 1e-10:
                normal = tuple(float(value) for value in averaged / norm)
    if normal is None:
        normal = _normal_from_points(points)
    return center, normal


def _show_dfnd_cutaway(
    view,
    topography=None,
    *,
    component_ids=None,
    component_types=fam.PRIMARY_WET_FAMILIES,
    interfaces_only=False,
    invert=False,
    tag_prefix='dfnd-cutaway',
):
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')
    dfnd_data = getattr(topography, 'dfnd', None)
    if dfnd_data is None:
        raise ValueError('Topography has no DFND data attached')
    if not hasattr(view, 'scene') or not hasattr(view.scene, 'add_section'):
        raise TypeError('view must expose scene.add_section() for DFND cutaways')

    sections = []
    for comp in _components_matching(
        dfnd_data,
        component_ids=component_ids,
        component_types=component_types,
        interfaces_only=interfaces_only,
    ):
        payload = _component_cutaway_payload(
            topography, comp, interface_normal=interfaces_only
        )
        if payload is None:
            continue
        center, normal = payload
        tag = f'{tag_prefix}:{comp.component_id}'
        try:
            view.scene.remove_section(tag)
        except (AttributeError, KeyError):
            pass
        sections.append(
            view.scene.add_section(
                point=puw.quantity(center, 'nm'),
                normal=normal,
                invert=invert,
                tag=tag,
            )
        )
    if not sections:
        return None
    return sections[0] if len(sections) == 1 else sections


def show_dfnd_pocket_cutaway(
    view,
    topography=None,
    *,
    component_ids=None,
    component_types=fam.PRIMARY_WET_FAMILIES,
    invert=False,
    tag_prefix='dfnd-cutaway',
):
    """Add clipping sections through selected wet DFND components.

    This helper delegates the actual clipping plane to ``view.scene.add_section``.
    The initial plane is a diagnostic cut through the component centroid; it does
    not modify the DFND model or add a component representation.
    """
    return _show_dfnd_cutaway(
        view,
        topography,
        component_ids=component_ids,
        component_types=component_types,
        interfaces_only=False,
        invert=invert,
        tag_prefix=tag_prefix,
    )


def show_dfnd_interface_cutaway(
    view,
    topography=None,
    *,
    component_ids=None,
    component_types=fam.PRIMARY_WET_FAMILIES,
    invert=False,
    tag_prefix='dfnd-interface-cutaway',
):
    """Add clipping sections through selected DFND interface components.

    The normal is initialized from the mean wet-to-dry coast direction when coast
    faces are available, falling back to the component's principal geometric axis.
    """
    return _show_dfnd_cutaway(
        view,
        topography,
        component_ids=component_ids,
        component_types=component_types,
        interfaces_only=True,
        invert=invert,
        tag_prefix=tag_prefix,
    )

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
        if not _matches_component_types(comp, component_types):
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
        if not _matches_component_types(comp, component_types):
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
        parts = [str(comp.component_id), _BUCKET_LABEL.get(_render_bucket(comp), 'component')]
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
    draw_channel_branches: bool = True,
    pipe_style: str = _PIPE_STYLE_SOLID,
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
        - 'wire_contour': Wireframe iso-surface from residence spheres.
        - 'clearance_map': Volumetric envelope coloured by local R_residence.
        - 'scalar_isosurface': Domain-neutral gaussian isosurface of residence spheres.
        - 'pocket_depth_map': Envelope coloured by wet topological depth from mouths.
        - 'shape_ellipsoids': PCA ellipsoid per component for orientation/elongation.
        - 'clearance_wire': Wireframe envelope coloured by local R_residence.
        - 'pipe': Channels as a variable-radius tube along their through-path
          (centerline + R_residence) with a bottleneck marker; >2-mouth channels
          add secondary visual branches to the primary path; non-channels fall
          back to a blob.
        - 'channel_tube'/'channel_solid': Explicit channel-only aliases for
          a fixed-colour continuous tube.
        - 'channel_profile': Explicit channel-only diagnostic tube coloured by
          clearance profile.
        - 'channel_lumen'/'channel_tunnel': Explicit channel-only continuous
          lumen surface built from the channel path radii.
        - 'channel_ribbon'/'groove_ribbon': Flattened channel ribbon/cinta for
          reading direction and branching without implying a validated path.
        - 'groove_floor': Permeable component faces as a groove-floor diagnostic.
        - 'groove_walls': Component lining atoms as a groove-wall surface.
        - 'groove_width_profile': HOLE-style width rings along a groove/channel path.
        - 'groove_depth_profile': Residence envelope coloured by topological depth.
        - 'channel_blob': Explicit channel-only volumetric blob.
        - 'channel_wire_blob': Explicit channel-only wireframe blob.
        - 'mouth_rings': Aperture rings at external links.
        - 'bottleneck_rings': Neck markers for channel shortest-distance skeletons.
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
        - 'dry_interface_faces': Dry-side wet/dry coast faces.
        - 'dry_blocked_faces': Non-permeable faces touching selected dry banks.
        - 'dry_depth_map': Dry faces coloured by face-depth from interface.
        - 'dry_shell': Semitransparent shell of selected dry-bank boundary faces.
        - 'dry_cage': Edge-only tetrahedral cage of selected dry banks.
        - 'interface_ribbon': Flattened tube through interface face centroids.
        - 'semantic_faces': DFND faces touching selected components, coloured by semantic role.
        - 'permeable_faces': Permeable DFND faces touching selected components.
        - 'impermeable_faces': Non-permeable DFND faces touching selected components.
        - 'mouth_faces': Permeable boundary faces opening to OCEAN.
        - 'interface_faces': Wet-dry coast/interface faces.
        - 'mouth_stubs': Short outward links through external permeable faces.
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
    draw_channel_branches : bool, default True
        For 'pipe': draw shortest-distance secondary branches from extra mouths
        to the primary two-mouth path. These are visual topology cues, not
        validated trajectories or max-capacity paths.
    pipe_style : {'solid', 'profile', 'solid_rings', 'lumen', 'ribbon'}, default 'solid'
        Visual style for 'pipe':
        - 'solid': fixed-colour, near-opaque channel tube with a bottleneck marker.
        - 'profile': diagnostic tube coloured by the station clearance profile.
        - 'solid_rings': solid tube plus HOLE-style clearance rings.
        - 'lumen': continuous channel-lumen surface from the path radii.
        - 'ribbon': flattened smooth tube/cinta for reading channel orientation.
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

    requested_representation = representation
    representation = {
        'spheres': 'residence_spheres',
        'skeleton': 'graph',
        'interface_contact_faces': 'interface_faces',
        'interface_lining_surface': 'contact_sheet',
        'interface_surface': 'contact_sheet',
    }.get(representation, representation)
    # resolve deprecated named modes to their grounded primitive (back-compat)
    representation = _REPRESENTATION_ALIASES.get(representation, representation)
    channel_alias = representation in _CHANNEL_REPRESENTATION_ALIASES
    if channel_alias:
        representation, alias_pipe_style = _CHANNEL_REPRESENTATION_ALIASES[representation]
        if alias_pipe_style is not None:
            pipe_style = alias_pipe_style
        if component_types == fam.PRIMARY_WET_FAMILIES:
            component_types = (fam.CHANNEL,)
    if representation not in _COMPONENT_REPRESENTATIONS:
        supported = ', '.join(sorted(_COMPONENT_REPRESENTATIONS))
        raise ValueError(
            f'Unknown representation {representation!r}. Supported: {supported}.'
        )

    if requested_representation in {'interface_lining_surface', 'interface_surface'}:
        show_wet = True
        show_dry = False
        interfaces_only = True
    if requested_representation in {
        'dry_interface_faces',
        'dry_blocked_faces',
        'dry_depth_map',
        'dry_shell',
        'dry_cage',
    }:
        show_wet = False
        show_dry = True
        component_types = None
        interfaces_only = False

    # Gather matching components
    selected_components = []

    if show_wet:
        for comp in dfnd_data.dfn.components.wet:
            if not _matches_component_types(comp, component_types):
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
                mode = _representation_for(comp)
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
                draw_channel_branches=draw_channel_branches,
                pipe_style=pipe_style,
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
    if representation == 'tube':
        pipe_style = pipe_style.lower()
        if pipe_style not in _PIPE_STYLES:
            supported = ', '.join(sorted(_PIPE_STYLES))
            raise ValueError(
                f'Unknown pipe_style {pipe_style!r}. Supported: {supported}.'
            )
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
        palette_override = (
            _palette_color_override(color_palette, comp) if color_palette else None
        )
        if color_palette and comp_id in color_palette:
            color = color_palette[comp_id]
        elif palette_override is not None:
            color = palette_override
        elif color_mode == 'by_type':
            color = _color_for(comp)
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
                    f'Component: {comp_id} ({_BUCKET_LABEL.get(_render_bucket(comp), "component")}) | '
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

    elif representation == 'wire_contour':
        # Wireframe isosurface from the same DFND residence spheres as 'cloud'.
        # The scientific scalar field is unchanged; only the final MolSysViewer
        # visual is switched to marching-cubes lines.
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
                name=f'{name} {comp_id} wire contour',
                resolution=blob_resolution,
                smoothing=blob_smoothing,
                iso_level=blob_iso_level,
                radius_scale=blob_radius_scale,
                wireframe=True,
                skip_digestion=True,
            )
            layers.append(layer)
        return layers[0] if len(layers) == 1 else layers

    elif representation in {
        'cloud',
        'clearance_map',
        'clearance_wire',
        'scalar_isosurface',
        'depth_map',
    }:
        # Render a separate volumetric envelope per component. The clearance
        # variants use the same scalar field but pass R_residence as a per-sphere
        # value so MolSysViewer colours the surface by local probe clearance.
        blob_resolution = 0.5 if resolution is None else resolution
        blob_smoothing = 0.5 if smoothing is None else smoothing
        blob_iso_level = 0.5 if iso_level is None else iso_level
        blob_radius_scale = 0.6 if radius_scale is None else radius_scale
        clearance = representation in {'clearance_map', 'clearance_wire', 'scalar_isosurface'}

        for comp in selected_components:
            comp_id = comp.component_id
            geometry = component_residence_sphere_geometry(
                topography, comp, use_resident_nodes=use_resident_nodes
            )
            if not geometry.centers:
                continue

            tag = f'{tag_prefix}:{comp_id}'
            surface_adapter = (
                add_scalar_isosurface
                if representation == 'scalar_isosurface'
                else add_pocket_blob
            )
            layer = surface_adapter(
                view,
                geometry,
                alpha=alpha,
                tag=tag,
                layer_tag=tag_prefix,
                name=f'{name} {comp_id}'
                + (' clearance' if clearance else ' depth' if representation == 'depth_map' else ''),
                resolution=blob_resolution,
                smoothing=blob_smoothing,
                iso_level=blob_iso_level,
                radius_scale=blob_radius_scale,
                values=(
                    [_angstrom_from_nm(radius) for radius in geometry.radii]
                    if clearance
                    else _component_depth_values(comp, geometry)
                    if representation == 'depth_map'
                    else None
                ),
                color_map='turbo' if clearance or representation == 'depth_map' else None,
                wireframe=representation == 'clearance_wire',
                skip_digestion=True,
            )
            layers.append(layer)
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'tube':
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
                if _render_bucket(comp) == 'through' and comp.raw_record is not None
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

            solid_pipe = pipe_style in {_PIPE_STYLE_SOLID, _PIPE_STYLE_SOLID_RINGS}
            lumen_pipe = pipe_style == _PIPE_STYLE_LUMEN
            ribbon_pipe = pipe_style == _PIPE_STYLE_RIBBON
            tube_alpha = max(alpha, 0.85) if solid_pipe else alpha
            tube_colors = (
                [color]
                if solid_pipe or lumen_pipe or ribbon_pipe
                else [_hole_clearance_color(float(r)) for r in path_geometry.radii]
            )
            tube = add_channel_tube(
                view,
                path_geometry,
                color_by='segment',
                colors=tube_colors,
                alpha=max(alpha, 0.55) if lumen_pipe else tube_alpha,
                radial_segments=24 if solid_pipe or ribbon_pipe else 16,
                smoothing_subdivisions=2 if solid_pipe or ribbon_pipe else 0,
                tube_style='surface'
                if lumen_pipe
                else 'smooth'
                if solid_pipe or ribbon_pipe
                else 'segments',
                surface_resolution=0.5 if lumen_pipe and resolution is None else resolution,
                surface_smoothing=0.75 if lumen_pipe and smoothing is None else smoothing,
                surface_iso_level=0.5 if lumen_pipe and iso_level is None else iso_level,
                surface_radius_scale=0.85 if lumen_pipe and radius_scale is None else radius_scale,
                tube_aspect_ratio=0.22 if ribbon_pipe else None,
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
                alpha=min(1.0, max(alpha, 0.75)),
                tag=f'{tag_prefix}:{comp_id}-bottleneck',
                layer_tag=tag_prefix,
                skip_digestion=True,
            )
            layers.append(marker)

            if pipe_style == _PIPE_STYLE_SOLID_RINGS:
                profile = add_rings(
                    view,
                    path_rings,
                    colors=[_hole_clearance_color(float(r)) for r in path_rings.radii],
                    alpha=min(1.0, max(alpha, 0.45)),
                    tag=f'{tag_prefix}:{comp_id}-profile-rings',
                    layer_tag=tag_prefix,
                    name=f'{name} {comp_id} clearance profile',
                    skip_digestion=True,
                )
                layers.append(profile)

            if draw_channel_branches:
                for branch_index, branch_geometry in enumerate(
                    component_branch_geometries(topography, comp), start=1
                ):
                    if not branch_geometry.centers:
                        continue
                    branch_colors = (
                        [color]
                        if solid_pipe or lumen_pipe or ribbon_pipe
                        else [
                            _hole_clearance_color(float(r))
                            for r in branch_geometry.radii
                        ]
                    )
                    branch = add_channel_tube(
                        view,
                        branch_geometry,
                        color_by='segment',
                        colors=branch_colors,
                        alpha=max(0.25, min(0.45, alpha * 0.65)),
                        radial_segments=18 if solid_pipe or ribbon_pipe else 12,
                        smoothing_subdivisions=1 if solid_pipe or ribbon_pipe else 0,
                        tube_style='surface'
                        if lumen_pipe
                        else 'smooth'
                        if solid_pipe or ribbon_pipe
                        else 'segments',
                        surface_resolution=0.5 if lumen_pipe and resolution is None else resolution,
                        surface_smoothing=0.75 if lumen_pipe and smoothing is None else smoothing,
                        surface_iso_level=0.5 if lumen_pipe and iso_level is None else iso_level,
                        surface_radius_scale=0.85 if lumen_pipe and radius_scale is None else radius_scale,
                        tube_aspect_ratio=0.22 if ribbon_pipe else None,
                        tag=f'{tag_prefix}:{comp_id}-branch-{branch_index}',
                        layer_tag=tag_prefix,
                        name=f'{name} {comp_id} branch {branch_index}',
                        skip_digestion=True,
                    )
                    layers.append(branch)

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
            if _render_bucket(comp) != 'through' or comp.raw_record is None:
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


    elif representation == 'mouth_rings':
        for comp in selected_components:
            comp_id = comp.component_id
            geometry = mouth_ring_geometry(topography, comp)
            if not geometry.centers:
                continue
            layers.append(
                add_rings(
                    view,
                    geometry,
                    colors=[_MOUTH_ACCENT] * len(geometry.centers),
                    alpha=min(1.0, max(alpha, 0.75)),
                    tag=f'{tag_prefix}:{comp_id}',
                    layer_tag=tag_prefix,
                    name=f'{name} {comp_id} mouths',
                    skip_digestion=True,
                )
            )

        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'bottleneck_rings':
        for comp in selected_components:
            comp_id = comp.component_id
            if _render_bucket(comp) != 'through' or comp.raw_record is None:
                continue
            path_geometry, bottleneck_index = component_centerline_geometry(
                topography, comp
            )
            if not path_geometry.centers or bottleneck_index < 0:
                continue
            path_rings = centerline_ring_geometry(topography, comp)
            geometry = RingGeometry(
                (path_rings.centers[bottleneck_index],),
                (path_rings.normals[bottleneck_index],),
                (path_rings.radii[bottleneck_index],),
                path_rings.unit,
                (path_rings.refs[bottleneck_index],),
            )
            layers.append(
                add_rings(
                    view,
                    geometry,
                    colors=[_MOUTH_ACCENT],
                    alpha=min(1.0, max(alpha, 0.8)),
                    tag=f'{tag_prefix}:{comp_id}',
                    layer_tag=tag_prefix,
                    name=f'{name} {comp_id} bottleneck',
                    skip_digestion=True,
                )
            )

        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'shape_ellipsoids':
        centers = []
        eigenvalues = []
        eigenvectors = []
        values = []
        colors = []
        for comp in selected_components:
            payload = _component_shape_ellipsoid_payload(
                topography, comp, use_resident_nodes=use_resident_nodes
            )
            if payload is None:
                continue
            centers.append(payload['center'])
            eigenvalues.append(payload['eigenvalues'])
            eigenvectors.append(payload['eigenvectors'])
            values.append(payload['anisotropy'])
            colors.append(resolved_colors[comp.component_id])

        if not centers:
            return None
        return view.shapes.add_anisotropy_ellipsoids(
            centers=puw.quantity(np.asarray(centers), 'nm'),
            eigenvalues=eigenvalues,
            eigenvectors=eigenvectors,
            values=values,
            colors=colors,
            color_by='anisotropy',
            palette='turbo',
            alpha=alpha,
            scale=2.0,
            max_eccentricity=6.0,
            tag=tag_prefix,
            layer_tag=tag_prefix,
            name=f'{name} shape ellipsoids',
            skip_digestion=True,
        )

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

    elif representation == 'mouth_stubs':
        selected_nodes = set()
        for comp in selected_components:
            selected_nodes.update(
                _component_node_indices(comp, use_resident_nodes=use_resident_nodes)
            )
        _edge_geometry, mouth_geometry = dfn_graph_segments(
            topography, sorted(selected_nodes), include_mouths=True
        )
        if not mouth_geometry.refs:
            return None
        return add_segments(
            view,
            mouth_geometry,
            radius=puw.quantity(0.02, 'nm'),
            color=_MOUTH_ACCENT,
            tag=tag_prefix,
            layer_tag=tag_prefix,
            skip_digestion=True,
        )

    elif representation in {
        'semantic_faces',
        'permeable_faces',
        'impermeable_faces',
        'mouth_faces',
        'interface_faces',
    }:
        color_by_face_id, label_by_face_id = _component_face_payloads(
            topography, selected_components, representation
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



    elif representation == 'links':
        geometry = _interface_link_geometry(topography, selected_components)
        if not geometry.refs:
            return None
        return add_segments(
            view,
            geometry,
            radius=puw.quantity(0.012, 'nm'),
            color=_OKABE_ITO['orange'],
            alpha=min(1.0, max(alpha, 0.65)),
            tag=tag_prefix,
            layer_tag=tag_prefix,
            skip_digestion=True,
        )

    elif representation == 'interface_ribbon':
        for comp_id, geometry in _interface_ribbon_geometries(
            topography, selected_components
        ):
            if len(geometry.centers) < 2:
                continue
            layers.append(
                add_channel_tube(
                    view,
                    geometry,
                    color_by='segment',
                    colors=[_OKABE_ITO['orange']],
                    alpha=min(1.0, max(alpha, 0.6)),
                    radial_segments=18,
                    smoothing_subdivisions=1,
                    tube_style='smooth',
                    tube_aspect_ratio=0.18,
                    tag=f'{tag_prefix}:{comp_id}',
                    layer_tag=tag_prefix,
                    name=f'{name} {comp_id} interface ribbon',
                    skip_digestion=True,
                )
            )
        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'groove_floor':
        color_by_face_id, label_by_face_id = _component_face_payloads(
            topography, selected_components, 'permeable_faces'
        )
        geometry = face_geometry(topography, face_ids=color_by_face_id)
        if not geometry.atom_triplets:
            return None
        return add_indexed_triangles(
            view,
            geometry,
            colors=[_OKABE_ITO['sky_blue'] for _ in geometry.refs],
            alpha=alpha,
            labels=[label_by_face_id[ref.entity_id] for ref in geometry.refs],
            tag=tag_prefix,
            layer_tag=tag_prefix,
            skip_digestion=True,
        )

    elif representation == 'lining_surface':
        for comp in selected_components:
            atom_indices = indices_in_space(
                getattr(comp, 'atom_indices', None), space=MOLECULAR_SYSTEM
            )
            if not atom_indices:
                continue
            layers.append(
                view.shapes.add_pocket_surface(
                    atom_indices=atom_indices,
                    color_map=[_OKABE_ITO['sky_blue'], _OKABE_ITO['sky_blue']],
                    alpha=alpha,
                    tag=f'{tag_prefix}:{comp.component_id}',
                    layer_tag=tag_prefix,
                    skip_digestion=True,
                )
            )
        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'width_profile':
        for comp in selected_components:
            if _render_bucket(comp) != 'through' or comp.raw_record is None:
                continue
            geometry = centerline_ring_geometry(topography, comp)
            if not geometry.centers:
                continue
            layers.append(
                add_rings(
                    view,
                    geometry,
                    colors=[_hole_clearance_color(float(r)) for r in geometry.radii],
                    alpha=alpha,
                    tag=f'{tag_prefix}:{comp.component_id}',
                    layer_tag=tag_prefix,
                    name=f'{name} {comp.component_id} groove width profile',
                    skip_digestion=True,
                )
            )
        if not layers:
            return None
        return layers[0] if len(layers) == 1 else layers

    elif representation == 'dry_cage':
        selected_tetra_ids = []
        for comp in selected_components:
            if getattr(comp, 'side', None) != 'dry':
                continue
            selected_tetra_ids.extend(
                _component_node_indices(comp, use_resident_nodes=False)
            )
        selected_tetra_ids = sorted({int(value) for value in selected_tetra_ids})
        geometry = tetrahedra_geometry(topography, selected_tetra_ids)
        if not geometry.atom_quads:
            return None
        return add_tetrahedra(
            view,
            geometry,
            colors=[_TYPE_PALETTE[fam.DRY_BANK]] * len(geometry.atom_quads),
            alphas=[0.0] * len(geometry.atom_quads),
            labels=[f'Dry cage tetrahedron {ref.entity_id}' for ref in geometry.refs],
            draw_faces=False,
            draw_edges=True,
            edge_meta=_dfnd_edge_meta(topography, selected_tetra_ids) or None,
            edge_radius=puw.quantity(max(edge_radius_nm, 0.006), 'nm'),
            edge_color=_TYPE_PALETTE[fam.DRY_BANK],
            tag=tag_prefix,
            layer_tag=tag_prefix,
            name=f'{name} dry cage',
            skip_digestion=True,
            exterior_only=True,
        )

    elif representation in {
        'dry_interface_faces',
        'dry_blocked_faces',
        'dry_depth_map',
        'dry_shell',
    }:
        color_by_face_id, label_by_face_id = _dry_face_payloads(
            topography, selected_components, representation
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
            if not _matches_component_types(comp, component_types):
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
