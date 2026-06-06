"""Derive a channel centerline (ordered stations + free radii) from DFND records.

Pure geometry on the raw topography: no viewer dependency, unit-testable. Used by
the ``molsysviewer_topomt`` ``pipe`` representation (``add_channel_tube``) to draw
a channel as a variable-radius tube along its through-path, and equally usable as
a HOLE-style channel *profile* for analysis. See
``devguide/DFND/component_visualization_implementation.md`` (Phase 2).

The through-path is the shortest route (weighted by inter-center distance) in the
component's *permeable* resident graph between resident tetrahedra of its two
widest mouths. Returns ``None`` for anything that is not a genuine through-channel
(fewer than two resident mouths, or no connecting path).
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _permeable_resident_graph(raw, resident_ids, tetra_by_id):
    """``networkx.Graph`` over ``resident_ids`` with one edge per shared *permeable*
    face, weighted by the distance between residence centers (so the path is the
    geometrically shortest route a probe can take, not the fewest hops)."""
    import networkx as nx

    graph = nx.Graph()
    graph.add_nodes_from(resident_ids)
    for face in raw['faces']:
        if face.get('permeability_state') != 'permeable':
            continue
        owner = face.get('owner_tetrahedron_id')
        neighbor = face.get('neighbor_tetrahedron_id')
        if owner in resident_ids and neighbor in resident_ids:
            ca = np.asarray(tetra_by_id[owner]['center'], dtype=float)
            cb = np.asarray(tetra_by_id[neighbor]['center'], dtype=float)
            graph.add_edge(owner, neighbor, weight=float(np.linalg.norm(ca - cb)))
    return graph


def _mouth_endpoints(component, external_links_by_id, resident_ids):
    """One resident endpoint tetra per mouth, mouths ordered widest-first.

    Returns ``[(external_link_id, endpoint_tetra_id), ...]``; mouths with no
    resident tetra are skipped.
    """
    ranked = []
    for link_id in component.get('external_link_ids', []):
        link = external_links_by_id.get(link_id)
        if link is None:
            continue
        resident_overlap = [t for t in link['tetrahedron_ids'] if t in resident_ids]
        if not resident_overlap:
            continue
        ranked.append((link.get('area_geometric', 0.0), link_id, resident_overlap[0]))
    ranked.sort(reverse=True)  # widest mouth first
    return [(link_id, tetra_id) for _area, link_id, tetra_id in ranked]


def channel_centerline(raw, component) -> dict[str, Any] | None:
    """Ordered centerline stations + free radii for a channel ``component``.

    Parameters
    ----------
    raw : dict
        A DFND ``raw`` topography (``get_topography(...)['raw']``) with
        ``faces``, ``tetrahedra`` and ``external_links``.
    component : dict
        One ``raw['wet_components']`` record (its ``resident_tetrahedron_ids``
        and ``external_link_ids`` are used).

    Returns
    -------
    dict or None
        ``None`` when there is no through-path. Otherwise:

        - ``tetra_path``: tetrahedron ids from one mouth to the other;
        - ``centers``: ``(N, 3)`` residence centers along the path;
        - ``radii``: ``(N,)`` ``R_residence`` per station (the free radius);
        - ``bottleneck_index``: index of the narrowest station;
        - ``mouth_endpoints``: the two ``(link_id, tetra_id)`` mouths used.
    """
    import networkx as nx

    resident_ids = set(component.get('resident_tetrahedron_ids', []))
    if len(resident_ids) < 2:
        return None

    external_links_by_id = {e['external_link_id']: e for e in raw['external_links']}
    endpoints = _mouth_endpoints(component, external_links_by_id, resident_ids)
    if len(endpoints) < 2:
        return None  # not a through-channel: needs two resident mouths

    tetra_by_id = {t['tetrahedron_id']: t for t in raw['tetrahedra']}
    graph = _permeable_resident_graph(raw, resident_ids, tetra_by_id)

    (link_a, node_a), (link_b, node_b) = endpoints[0], endpoints[1]
    try:
        path = nx.shortest_path(graph, node_a, node_b, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None
    if len(path) < 2:
        return None

    centers = np.array([tetra_by_id[t]['center'] for t in path], dtype=float)
    radii = np.array([tetra_by_id[t]['R_residence'] for t in path], dtype=float)
    return {
        'tetra_path': list(path),
        'centers': centers,
        'radii': radii,
        'bottleneck_index': int(np.argmin(radii)),
        'mouth_endpoints': [(link_a, node_a), (link_b, node_b)],
    }
