"""show_dfn_graph: DFN flow-graph nodes/edges."""

from functools import wraps
from inspect import signature
from typing import Any

from topomt import pyunitwizard as puw

from ..geometry import dfn_graph_segments, tetrahedron_centers
from ._common import _resolve_topography
from .adapters import add_point_spheres, add_segments
from .result import (
    RenderResult,
    clear_previous_render_result,
    remember_render_result,
    render_result,
)

_DFN_NODE_PALETTE = {
    'wet_sealed': 0x14B8A6,
    'wet_open': 0x3B82F6,
    'wet_coast': 0x8B5CF6,
    'dry_sealed': 0x334155,
    'dry_open': 0x64748B,
    'dry_coast': 0xF97316,
}


def _show_dfn_graph_legacy(
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

    palette = dict(_DFN_NODE_PALETTE)
    if color_palette:
        palette.update(color_palette)

    state = {node['tetrahedron_id']: node for node in data.dfn.graph.nodes}

    def _is_node(tid: int) -> bool:
        node = state[tid]
        transit_role = node.get('transit_role')
        if transit_role is not None:
            return transit_role in {'resident_transit', 'transit_connector'}
        return (
            node['residence_state'] == 'resident' or node['n_permeable_contacts'] >= 1
        )

    node_ids = [
        tet['tetrahedron_id']
        for tet in mesh.tetrahedra
        if _is_node(tet['tetrahedron_id'])
    ]
    if not node_ids:
        return None
    node_geometry = tetrahedron_centers(topography, node_ids)
    colors = [palette.get(state[tid]['combined_class'], 0x888888) for tid in node_ids]

    edge_geometry, mouth_geometry = dfn_graph_segments(
        topography, node_ids, mouth_stub_angstrom=mouth_stub_angstrom
    )

    for tag in (
        tag_prefix,
        f'{tag_prefix}-node',
        f'{tag_prefix}-edges',
        f'{tag_prefix}-mouths',
    ):
        try:
            view.shapes.clear(tag=tag, skip_digestion=True)
        except Exception:
            pass

    node_layer = add_point_spheres(
        view,
        node_geometry,
        radius=puw.quantity(node_radius_nm, 'nm'),
        color=colors,
        alpha=node_alpha,
        tag=f'{tag_prefix}-node',
        layer_tag=f'{tag_prefix}-nodes',
        skip_digestion=skip_digestion,
    )
    edge_layer = None
    if edge_geometry.refs:
        edge_layer = add_segments(
            view,
            edge_geometry,
            radius=puw.quantity(edge_radius_nm, 'nm'),
            color=edge_color,
            tag=f'{tag_prefix}-edges',
            layer_tag=f'{tag_prefix}-edges',
            skip_digestion=skip_digestion,
        )
    mouth_layer = None
    if mouth_geometry.refs:
        mouth_layer = add_segments(
            view,
            mouth_geometry,
            radius=puw.quantity(edge_radius_nm, 'nm'),
            color=mouth_color,
            tag=f'{tag_prefix}-mouths',
            layer_tag=f'{tag_prefix}-mouths',
            skip_digestion=skip_digestion,
        )

    return {
        'nodes': node_layer,
        'node_geometry': node_geometry,
        'edges': edge_layer,
        'edge_geometry': edge_geometry,
        'mouths': mouth_layer,
        'mouth_geometry': mouth_geometry,
        'node_ids': tuple(node_ids),
        'n_nodes': len(node_ids),
        'n_edges': len(edge_geometry.refs),
        'n_mouths': len(mouth_geometry.refs),
    }


@wraps(_show_dfn_graph_legacy)
def show_dfn_graph(view, topography=None, **kwargs):
    """Render the DFN graph and return a uniform ``RenderResult``."""
    operation_key = f'graph:{kwargs.get("tag_prefix", "dfn-graph")}'
    clear_previous_render_result(view, operation_key)
    raw = _show_dfn_graph_legacy(view, topography, **kwargs)
    selected_ids = raw.get('node_ids', ()) if isinstance(raw, dict) else ()
    result = render_result('graph', raw, selected_ids=selected_ids)
    return remember_render_result(view, operation_key, result)


show_dfn_graph.__signature__ = signature(_show_dfn_graph_legacy).replace(
    return_annotation=RenderResult
)
show_dfn_graph.__annotations__['return'] = RenderResult
