import numpy as np

import topomt as tmt
from topomt.delaunay_mesh import DelaunayMesh


def test_delaunay_mesh_builds_minimal_single_simplex():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

    mesh = DelaunayMesh(points=points)

    assert mesh.n_points == 4
    assert mesh.simplices.shape == (1, 4)
    assert mesh.oriented_simplices.shape == (1, 4)
    assert mesh.neighbors.shape == (1, 4)
    assert mesh.alpha_sphere_centers.shape == (1, 3)
    assert mesh.alpha_sphere_radii.shape == (1,)
    assert mesh.alpha_sphere_atom_indices.shape == (1, 4)
    assert mesh.get_alpha_sphere_neighbors() == {0: []}
    assert mesh.get_alpha_sphere_neighbor_pairs().shape == (0,)


def test_delaunay_mesh_exposes_simplex_faces_and_boundary_faces():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

    mesh = DelaunayMesh(points=points)

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


def test_delaunay_mesh_alpha_sphere_radius_filter_returns_mask():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

    mesh = DelaunayMesh(points=points)
    mask = mesh.filter_alpha_spheres(min_radius=0.0, max_radius=10.0)

    assert mask.dtype == bool
    assert mask.shape == (1,)
    assert bool(mask[0]) is True


def test_get_delaunay_mesh_returns_mesh_for_demo_system():

    molecular_system = tmt.demo['HIV-1 Protease']['1HIV.pdb']
    mesh = tmt.get_delaunay_mesh(molecular_system)

    assert isinstance(mesh, DelaunayMesh)
    assert mesh.n_points > 0
    assert mesh.n_alpha_spheres > 0
