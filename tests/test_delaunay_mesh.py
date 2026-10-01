import numpy as np
import pytest

import topomt as tmt
from topomt.delaunay_mesh import DelaunayMesh


def test_frozen_mesh_keeps_owned_geometry_and_rejects_destructive_operations():
    points = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )
    mesh = DelaunayMesh(points=points)
    assert mesh.freeze() is mesh
    points[:] *= 2
    assert mesh.simplex_volumes[0] == pytest.approx(1 / 6)
    assert mesh.points[1, 0] == 1
    with pytest.raises(ValueError, match='read-only'):
        mesh.points[1, 0] = 2
    with pytest.raises(ValueError):
        mesh.points.setflags(write=True)
    with pytest.raises(AttributeError, match='read-only'):
        mesh.points = points
    with pytest.raises(AttributeError, match='read-only'):
        mesh.remove_alpha_spheres([0])
    assert mesh.n_simplices == 1
    assert mesh.get_simplex_faces().shape == (1, 4, 3)


def test_frozen_mesh_neighbor_lookup_cannot_modify_its_cached_adjacency():
    mesh = DelaunayMesh(
        points=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        )
    )
    mesh.freeze()
    mesh.get_alpha_sphere_neighbors()[0].append(100)
    assert mesh.get_alpha_sphere_neighbors() == {0: []}


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
    oriented_simplex = tuple(
        int(atom_index) for atom_index in mesh.oriented_simplices[0]
    )
    assert mesh.get_face_atoms(0, 2) == tuple(
        sorted(oriented_simplex[index] for index in (0, 1, 3))
    )  # face opposite oriented vertex 2

    boundary_faces = mesh.get_boundary_face_records()
    assert len(boundary_faces) == 4
    assert {record[2] for record in boundary_faces} == expected_faces


def test_delaunay_mesh_exposes_simplex_view_aliases():

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

    assert mesh.n_simplices == mesh.n_alpha_spheres
    assert np.array_equal(mesh.simplex_atom_indices, mesh.alpha_sphere_atom_indices)
    assert np.allclose(mesh.simplex_centers, mesh.alpha_sphere_centers)
    assert np.allclose(mesh.simplex_radii, mesh.alpha_sphere_radii)
    assert np.allclose(mesh.simplex_volumes, mesh.alpha_sphere_volumes)
    assert mesh.get_simplex_neighbors() == mesh.get_alpha_sphere_neighbors()
    assert np.array_equal(
        mesh.get_simplex_neighbor_pairs(),
        mesh.get_alpha_sphere_neighbor_pairs(),
    )


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


def test_delaunay_mesh_keep_alpha_spheres_accepts_boolean_mask():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
        ],
        dtype=float,
    )

    mesh = DelaunayMesh(points=points)
    initial_count = mesh.n_alpha_spheres
    assert initial_count > 1

    mask = np.zeros(initial_count, dtype=bool)
    mask[0] = True
    mesh.keep_alpha_spheres(mask)

    assert mesh.n_alpha_spheres == 1
    assert mesh.n_simplices == 1
    assert mesh.alpha_sphere_centers.shape == (1, 3)
    assert mesh.simplices.shape == (1, 4)
    assert mesh.oriented_simplices.shape == (1, 4)


def test_get_delaunay_mesh_returns_mesh_for_demo_system():

    molecular_system = tmt.demo['HIV-1 Protease']['1HIV.pdb']
    mesh = tmt.get_delaunay_mesh(molecular_system)

    assert isinstance(mesh, DelaunayMesh)
    assert mesh.n_points > 0
    assert mesh.n_alpha_spheres > 0
