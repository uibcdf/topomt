"""Derive a channel skeleton from DFND records.

A channel skeleton is a graph-derived geometric summary of a DFND channel. It is
used by ``molsysviewer_topomt`` to draw channel tubes and rings, but it is not a
collision-validated probe trajectory.

The current skeleton path is the shortest route by center-to-center distance in
the component's permeable resident graph between resident tetrahedra of its two
widest mouths. Gate metrics are therefore conditional to this shortest-distance
path; they are not the maximum capacity of the channel.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from depdigest import dep_digest


def _permeable_resident_graph(raw, resident_ids, tetra_by_id):
    """Build a resident graph with distance weights and gate metadata."""
    import networkx as nx

    graph = nx.Graph()
    graph.add_nodes_from(resident_ids)
    for face in raw['faces']:
        if not face.get('transit_edge', face.get('permeability_state') == 'permeable'):
            continue
        owner = face.get('owner_tetrahedron_id')
        neighbor = face.get('neighbor_tetrahedron_id')
        if owner in resident_ids and neighbor in resident_ids:
            ca = np.asarray(tetra_by_id[owner]['center'], dtype=float)
            cb = np.asarray(tetra_by_id[neighbor]['center'], dtype=float)
            graph.add_edge(
                owner,
                neighbor,
                weight=float(np.linalg.norm(ca - cb)),
                face_id=int(face['face_id']),
                gate_radius=float(face['R_gate']),
                gate_margin=float(face.get('gate_margin', face['R_gate'])),
            )
    return graph


def _mouth_resident_sets(component, external_links_by_id, resident_ids):
    """Resident tetrahedra per mouth, mouths ordered widest-first."""
    ranked = []
    for link_id in component.get('external_link_ids', []):
        link = external_links_by_id.get(link_id)
        if link is None:
            continue
        resident_overlap = sorted(t for t in link['tetrahedron_ids'] if t in resident_ids)
        if not resident_overlap:
            continue
        ranked.append((link.get('area_geometric', 0.0), link_id, resident_overlap))
    ranked.sort(reverse=True)  # widest mouth first
    return [(link_id, tetra_ids) for _area, link_id, tetra_ids in ranked]


@dep_digest('networkx')
def channel_skeleton(raw, component) -> dict[str, Any] | None:
    """Return the shortest-distance channel skeleton for a channel component.

    The two widest mouths are represented as virtual nodes connected to every
    incident resident tetrahedron, avoiding order-dependent endpoint selection.
    For a path with ``N`` tetrahedra, ``centers`` and ``station_radii`` have
    length ``N``. ``edge_gate_radii`` and ``edge_gate_margins`` have length
    ``N - 1`` and element ``i`` describes the transition
    ``tetra_path[i] -> tetra_path[i + 1]``.
    """
    import networkx as nx

    resident_ids = set(component.get('resident_tetrahedron_ids', []))
    if len(resident_ids) < 2:
        return None

    external_links_by_id = {e['external_link_id']: e for e in raw['external_links']}
    mouth_sets = _mouth_resident_sets(component, external_links_by_id, resident_ids)
    if len(mouth_sets) < 2:
        return None

    tetra_by_id = {t['tetrahedron_id']: t for t in raw['tetrahedra']}
    graph = _permeable_resident_graph(raw, resident_ids, tetra_by_id)

    (link_a, mouth_a_nodes), (link_b, mouth_b_nodes) = mouth_sets[0], mouth_sets[1]
    mouth_a = ('mouth', link_a)
    mouth_b = ('mouth', link_b)
    graph.add_node(mouth_a)
    graph.add_node(mouth_b)
    for node in mouth_a_nodes:
        graph.add_edge(mouth_a, node, weight=0.0)
    for node in mouth_b_nodes:
        graph.add_edge(mouth_b, node, weight=0.0)
    try:
        path_with_mouths = nx.shortest_path(graph, mouth_a, mouth_b, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None
    path = [node for node in path_with_mouths if not isinstance(node, tuple)]
    if len(path) < 2:
        return None

    centers = np.array([tetra_by_id[t]['center'] for t in path], dtype=float)
    station_radii = np.array(
        [tetra_by_id[t]['R_residence'] for t in path],
        dtype=float,
    )
    edge_records = [graph[path[index]][path[index + 1]] for index in range(len(path) - 1)]
    edge_gate_radii = np.array(
        [edge['gate_radius'] for edge in edge_records],
        dtype=float,
    )
    edge_gate_margins = np.array(
        [edge['gate_margin'] for edge in edge_records],
        dtype=float,
    )
    gate_bottleneck_edge_index = int(np.argmin(edge_gate_radii))

    return {
        'path_kind': 'shortest_distance',
        'tetra_path': list(path),
        'centers': centers,
        'station_radii': station_radii,
        'edge_gate_radii': edge_gate_radii,
        'edge_gate_margins': edge_gate_margins,
        'station_bottleneck_index': int(np.argmin(station_radii)),
        'gate_bottleneck_edge_index': gate_bottleneck_edge_index,
        'shortest_path_gate_radius_min': float(edge_gate_radii[gate_bottleneck_edge_index]),
        'shortest_path_gate_margin_min': float(edge_gate_margins[gate_bottleneck_edge_index]),
        'mouth_endpoints': [(link_a, path[0]), (link_b, path[-1])],
        'mouth_endpoint_policy': 'virtual_mouth_shortest_distance',
        'is_collision_validated': False,
    }
