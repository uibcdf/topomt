"""
Tests for the alpha-sphere-derived view exposed by DelaunayMesh.
"""

import numpy as np
import topomt as pom


def test_delaunay_mesh_alpha_view_original_points():

    points = ([[-1.,  2.,  0.],
               [ 0.,  2.,  1.],
               [ 1., -2.,  1.],
               [ 0.,  1.,  1.],
               [ 0.,  0.,  0.],
               [-1., -1.,  0.]])

    mesh = pom.DelaunayMesh(points)

    assert np.allclose(points, mesh.points)

    assert mesh.n_points == 6

    assert mesh.n_alpha_spheres == 4

    centers = ([[ 6.5 ,  1.5 , -0.5 ],
                [-0.25, -0.75,  1.75],
                [ 0.5 ,  1.5 , -0.5 ],
                [-1.5 ,  0.5 ,  0.5 ]])

    assert np.allclose(centers, mesh.centers)

    radius_all = ([6.68954408, 1.92028644, 1.6583124 , 1.6583124 ])
    assert np.allclose(radius_all, mesh.radii)

    volumes = ([0.16666667, 0.66666667, 0.16666667, 0.5])
    assert np.allclose(volumes, mesh.get_volumes())

    points_of_alpha_sphere = ([[1, 2, 3, 4],
                               [2, 3, 4, 5],
                               [0, 1, 3, 4],
                               [0, 3, 4, 5]])
    assert np.allclose(points_of_alpha_sphere, mesh.points_of_alpha_sphere)

    assert mesh.get_neighbors() == {
        0: [1, 2],
        1: [0, 3],
        2: [0, 3],
        3: [1, 2],
    }

    merged_selected_point_indices = [0, 2, 3, 4, 5]
    assert np.allclose(merged_selected_point_indices, mesh.get_points_of_alpha_spheres([1, 3]))


def test_delaunay_mesh_alpha_view_ambiguity_indicators_detect_near_cospherical_case():

    points = np.array([
        [1.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, -0.99],
    ])

    mesh = pom.DelaunayMesh(points)

    indicators = mesh.get_ambiguity_indicators(cospherical_tolerance=0.02)

    assert set(indicators.keys()) == {
        'volume',
        'normalized_volume',
        'min_edge',
        'max_edge',
        'radius_over_min_edge',
        'condition_number',
        'near_cospherical_count',
    }

    assert indicators['volume'].shape == (mesh.n_alpha_spheres,)
    assert indicators['near_cospherical_count'].shape == (mesh.n_alpha_spheres,)
    assert np.any(indicators['near_cospherical_count'] > 0)

    indices, returned_indicators = mesh.get_potentially_ambiguous_alpha_spheres(
        cospherical_tolerance=0.02,
        minimum_near_cospherical_count=1,
        minimum_condition_number=None,
    )

    assert returned_indicators['near_cospherical_count'].shape == (mesh.n_alpha_spheres,)
    assert indices.size > 0
    assert np.all(returned_indicators['near_cospherical_count'][indices] > 0)
