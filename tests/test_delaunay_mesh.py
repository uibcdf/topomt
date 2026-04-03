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
    assert mesh.neighbors.shape == (1, 4)
    assert mesh.alpha_sphere_centers.shape == (1, 3)
    assert mesh.alpha_sphere_radii.shape == (1,)
    assert mesh.alpha_sphere_atom_indices.shape == (1, 4)
    assert mesh.get_alpha_sphere_neighbors() == {0: []}
    assert mesh.get_alpha_sphere_neighbor_pairs().shape == (0,)


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
