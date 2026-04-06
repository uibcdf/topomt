import numpy as np

import topomt as tmt
from topomt.weighted_delaunay_mesh import WeightedDelaunayMesh


def test_weighted_delaunay_mesh_builds_minimal_single_simplex():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    weights = np.array([0.0, 0.0, 0.0, 0.0], dtype=float)

    mesh = WeightedDelaunayMesh(points=points, weights=weights)

    assert mesh.n_points == 4
    assert np.allclose(mesh.weights, weights)
    assert mesh.simplices.shape == (1, 4)
    assert mesh.oriented_simplices.shape == (1, 4)
    assert mesh.neighbors.shape == (1, 4)
    assert mesh.simplex_atom_indices.shape == (1, 4)
    assert mesh.simplex_centers.shape == (1, 3)
    assert mesh.simplex_power_values.shape == (1,)
    assert mesh.get_simplex_neighbors() == {0: []}
    assert mesh.get_simplex_neighbor_pairs().shape == (0, 2)


def test_weighted_delaunay_mesh_exposes_simplex_faces_and_boundary_faces():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    weights = np.array([0.0, 0.2, 0.1, 0.0], dtype=float)

    mesh = WeightedDelaunayMesh(points=points, weights=weights)

    simplex_faces = mesh.get_simplex_faces()
    assert simplex_faces.shape == (1, 4, 3)
    expected_faces = {
        (0, 1, 2),
        (0, 1, 3),
        (0, 2, 3),
        (1, 2, 3),
    }
    assert {tuple(face) for face in simplex_faces[0]} == expected_faces
    assert mesh.get_face_atoms(0, 2) == (0, 2, 3)

    boundary_faces = mesh.get_boundary_face_records()
    assert len(boundary_faces) == 4
    assert {record[2] for record in boundary_faces} == expected_faces


def test_topomt_exports_weighted_delaunay_mesh():

    assert tmt.WeightedDelaunayMesh is WeightedDelaunayMesh
