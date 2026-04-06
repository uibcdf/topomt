"""Tests for reusable tetrahedral discrete-flow helpers."""

import numpy as np

from topomt.delaunay_mesh import DelaunayMesh
from topomt.tools.tessellation import (
    ancestors_of_exterior,
    build_descending_flow_graph,
    build_open_neighbor_dict,
    flow_targets_to_sinks,
    group_by_flow_sink,
)


def test_flow_targets_to_sinks_descends_along_proxy():
    neighbor_dict = {
        0: [1],
        1: [0, 2],
        2: [1],
    }
    proxy_values = np.array([3.0, 2.0, 1.0], dtype=float)

    flow_target = flow_targets_to_sinks(proxy_values, neighbor_dict, tol_fraction=0.01)

    assert flow_target == {0: 2, 1: 2, 2: 2}


def test_group_by_flow_sink_preserves_connectivity():
    flow_target = {
        0: 1,
        1: 1,
        2: 3,
        3: 3,
    }
    neighbor_dict = {
        0: [1],
        1: [0],
        2: [3],
        3: [2],
    }

    components = group_by_flow_sink(flow_target, neighbor_dict)

    assert sorted(components.values()) == [[0, 1], [2, 3]]


def test_ancestors_of_exterior_walks_reverse_descending_graph():
    neighbor_dict = {
        0: [1],
        1: [0, 2],
        2: [1],
        3: [],
    }
    proxy_values = np.array([3.0, 2.0, 1.0, 5.0], dtype=float)

    _, reverse_graph = build_descending_flow_graph(proxy_values, neighbor_dict)
    ancestors = ancestors_of_exterior(reverse_graph, exterior_nodes=[2])

    assert ancestors == {0, 1, 2}


def test_build_open_neighbor_dict_filters_closed_faces():
    mesh = DelaunayMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 1.0, 1.0],
            ],
            dtype=float,
        )
    )

    face_radii = {}
    for simplex_faces in mesh.get_simplex_faces():
        for face in simplex_faces:
            face_radii.setdefault(tuple(int(atom_index) for atom_index in face), 2.0)

    open_mask = np.ones(mesh.n_simplices, dtype=bool)
    shared_face = tuple(
        sorted(set(mesh.simplices[0]).intersection(set(mesh.simplices[1])))
    )
    face_radii[shared_face] = 0.1

    neighbor_dict = build_open_neighbor_dict(mesh, open_mask, face_radii, probe_radius=1.4)

    assert neighbor_dict[0] == []
    assert neighbor_dict[1] == []


def test_build_open_neighbor_dict_supports_plain_face_adjacency():
    mesh = DelaunayMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 1.0, 1.0],
            ],
            dtype=float,
        )
    )

    open_mask = np.ones(mesh.n_simplices, dtype=bool)
    neighbor_dict = build_open_neighbor_dict(mesh, open_mask)

    assert neighbor_dict[0] == [1]
    assert neighbor_dict[1] == [0]
