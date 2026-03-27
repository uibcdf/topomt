"""
Unit to test the AlphaSpheres class
"""

import topomt as pom
import pytest
import numpy as np

def test_alphaspheres_original_points():

    points = ([[-1.,  2.,  0.],
               [ 0.,  2.,  1.],
               [ 1., -2.,  1.],
               [ 0.,  1.,  1.],
               [ 0.,  0.,  0.],
               [-1., -1.,  0.]])

    alphaspheres = pom.alpha_spheres.AlphaSpheres(points)

    assert np.allclose(points, alphaspheres.points)

    assert alphaspheres.n_points == 6

    assert alphaspheres.n_alpha_spheres == 4

    centers = ([[ 6.5 ,  1.5 , -0.5 ],
                [-0.25, -0.75,  1.75],
                [ 0.5 ,  1.5 , -0.5 ],
                [-1.5 ,  0.5 ,  0.5 ]])

    assert np.allclose(centers, alphaspheres.centers)

    radius_all = ([6.68954408, 1.92028644, 1.6583124 , 1.6583124 ])
    
    assert np.allclose(radius_all, alphaspheres.radii)

    volumes = ([0.16666667, 0.66666667, 0.16666667, 0.5])

    assert np.allclose(volumes, alphaspheres.get_volumes())

    points_of_alpha_sphere = ([[1, 2, 3, 4],
                               [2, 3, 4, 5],
                               [0, 1, 3, 4],
                               [0, 3, 4, 5]])

    assert np.allclose(points_of_alpha_sphere, alphaspheres.points_of_alpha_sphere)

    assert alphaspheres.get_neighbors() == {
        0: [1, 2],
        1: [0, 3],
        2: [0, 3],
        3: [1, 2],
    }

    merged_selected_point_indices = [0, 2, 3, 4, 5]

    assert np.allclose(merged_selected_point_indices, alphaspheres.get_points_of_alpha_spheres([1,3]))

    alphaspheres.remove_big_alpha_spheres(5.0)
    
    assert alphaspheres.n_alpha_spheres == 3

    remaining_no_big_radius = ([1.92028644, 1.6583124 , 1.6583124 ])
    
    assert np.allclose(remaining_no_big_radius, alphaspheres.radii)

    remaining_no_big_volumes = ([0.66666667, 0.16666667, 0.5])

    assert np.allclose(remaining_no_big_volumes, alphaspheres.get_volumes())
    assert alphaspheres.get_neighbors() == {0: [2], 1: [2], 2: [0, 1]}

    remaining_no_big_centers = ([[-0.25, -0.75,  1.75],
                                [ 0.5 ,  1.5 , -0.5 ],
                                [-1.5 ,  0.5 ,  0.5 ]])

    assert np.allclose(remaining_no_big_centers, alphaspheres.centers)

    alphaspheres.remove_small_alpha_spheres(1.66) 

    assert alphaspheres.n_alpha_spheres == 1

    remaining_no_small_radius = ([1.92028644])

    assert np.allclose(remaining_no_small_radius, alphaspheres.radii)

    remaining_no_small_volumes = ([0.66666667])

    assert np.allclose(remaining_no_small_volumes, alphaspheres.get_volumes())
    assert alphaspheres.get_neighbors() == {0: []}

    remaining_no_small_centers= ([[-0.25, -0.75,  1.75]])

    assert np.allclose(remaining_no_small_centers, alphaspheres.centers)


def test_alphaspheres_ambiguity_indicators_detect_near_cospherical_case():

    points = np.array([
        [1.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 0.0, -0.99],
    ])

    alphaspheres = pom.alpha_spheres.AlphaSpheres(points)

    indicators = alphaspheres.get_ambiguity_indicators(cospherical_tolerance=0.02)

    assert set(indicators.keys()) == {
        'volume',
        'normalized_volume',
        'min_edge',
        'max_edge',
        'radius_over_min_edge',
        'condition_number',
        'near_cospherical_count',
    }

    assert indicators['volume'].shape == (alphaspheres.n_alpha_spheres,)
    assert indicators['near_cospherical_count'].shape == (alphaspheres.n_alpha_spheres,)
    assert np.any(indicators['near_cospherical_count'] > 0)

    indices, returned_indicators = alphaspheres.get_potentially_ambiguous_alpha_spheres(
        cospherical_tolerance=0.02,
        minimum_near_cospherical_count=1,
        minimum_condition_number=None,
    )

    assert returned_indicators['near_cospherical_count'].shape == (
        alphaspheres.n_alpha_spheres,
    )
    assert indices.size > 0
    assert np.all(returned_indicators['near_cospherical_count'][indices] > 0)
