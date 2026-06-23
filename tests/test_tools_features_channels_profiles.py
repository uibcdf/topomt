"""Tests for channel profile helpers in topomt.tools.features."""

import math

import numpy as np
import pytest

from topomt.tools.features.channels import (
    cross_section_profile,
    min_cross_section_radius,
    shortest_path_length,
    thickness_profile,
)


def test_cross_section_profile_returns_expected_radial_maxima():

    centers = np.array(
        [
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.75, 2.0, 0.0],
            [0.75, -2.0, 0.0],
            [1.5, 0.0, 0.0],
        ],
        dtype=float,
    )

    bin_centers, radial_max = cross_section_profile(centers, axis=np.array([1.0, 0.0, 0.0]), n_bins=2)

    assert bin_centers.shape == (2,)
    assert np.allclose(radial_max, np.array([1.0, 2.0]))


def test_cross_section_profile_raises_with_zero_axis():

    centers = np.array([[0.0, 0.0, 0.0]], dtype=float)

    with pytest.raises(ValueError, match='Axis vector cannot be zero.'):
        cross_section_profile(centers, axis=np.zeros(3))


def test_min_cross_section_radius_returns_smallest_non_zero_radius():

    centers = np.array(
        [
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.75, 2.0, 0.0],
            [0.75, -2.0, 0.0],
            [1.5, 0.0, 0.0],
        ],
        dtype=float,
    )

    radius = min_cross_section_radius(centers, axis=np.array([1.0, 0.0, 0.0]), n_bins=2)

    assert radius == 1.0


def test_shortest_path_length_returns_graph_distance():

    centers = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    neighbor_pairs = [(0, 1), (1, 2)]

    distance = shortest_path_length(
        centers,
        neighbor_pairs=neighbor_pairs,
        start_indices=[0],
        end_indices=[2],
    )

    assert distance == 2.0


def test_shortest_path_length_returns_infinity_for_disconnected_graph():

    centers = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
        ],
        dtype=float,
    )

    distance = shortest_path_length(
        centers,
        neighbor_pairs=[(0, 1)],
        start_indices=[0],
        end_indices=[2],
    )

    assert math.isinf(distance)


def test_thickness_profile_averages_local_radii_per_bin():

    centers = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [1.5, 0.0, 0.0],
            [1.5, 4.0, 0.0],
            [3.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    neighbor_pairs = [(0, 1), (2, 3)]

    bin_centers, profile = thickness_profile(
        centers,
        axis=np.array([1.0, 0.0, 0.0]),
        neighbor_pairs=neighbor_pairs,
        n_bins=2,
    )

    assert bin_centers.shape == (2,)
    assert np.allclose(profile, np.array([1.0, 4.0 / 3.0]))

def test_cross_section_profile_rejects_empty_points():

    with pytest.raises(ValueError, match='centers must contain at least one point'):
        cross_section_profile(np.empty((0, 3)), axis=np.array([1.0, 0.0, 0.0]))


def test_cross_section_profile_includes_point_at_final_bin_edge():

    centers = np.array(
        [
            [0.0, 1.0, 0.0],
            [1.0, 3.0, 0.0],
        ],
        dtype=float,
    )

    _, radial_max = cross_section_profile(
        centers,
        axis=np.array([1.0, 0.0, 0.0]),
        axis_point=np.array([0.0, 0.0, 0.0]),
        n_bins=1,
    )

    assert radial_max == pytest.approx([3.0])


def test_thickness_profile_rejects_empty_points():

    with pytest.raises(ValueError, match='centers must contain at least one point'):
        thickness_profile(np.empty((0, 3)), axis=np.array([1.0, 0.0, 0.0]))

def test_cross_section_profile_is_translation_aware_by_default():
    centers = np.array(
        [
            [10.0, 1.0, 0.0],
            [10.0, -1.0, 0.0],
            [11.0, 2.0, 0.0],
            [11.0, -2.0, 0.0],
        ],
        dtype=float,
    )

    _, radial_max = cross_section_profile(
        centers, axis=np.array([1.0, 0.0, 0.0]), n_bins=2
    )

    assert radial_max == pytest.approx([1.0, 2.0])


def test_cross_section_profile_accepts_explicit_axis_point():
    centers = np.array(
        [
            [10.0, 1.0, 0.0],
            [10.0, -1.0, 0.0],
        ],
        dtype=float,
    )

    _, radial_max = cross_section_profile(
        centers,
        axis=np.array([1.0, 0.0, 0.0]),
        axis_point=np.array([10.0, 0.0, 0.0]),
        n_bins=1,
    )

    assert radial_max == pytest.approx([1.0])


def test_cross_section_profile_rejects_invalid_axis_point():
    centers = np.array([[0.0, 0.0, 0.0]], dtype=float)

    with pytest.raises(ValueError, match='axis_point must have shape'):
        cross_section_profile(
            centers,
            axis=np.array([1.0, 0.0, 0.0]),
            axis_point=np.array([0.0, 0.0]),
        )


def test_min_cross_section_radius_passes_axis_point():
    centers = np.array(
        [
            [10.0, 1.0, 0.0],
            [10.0, -1.0, 0.0],
            [11.0, 2.0, 0.0],
            [11.0, -2.0, 0.0],
        ],
        dtype=float,
    )

    radius = min_cross_section_radius(
        centers,
        axis=np.array([1.0, 0.0, 0.0]),
        axis_point=np.array([10.0, 0.0, 0.0]),
        n_bins=2,
    )

    assert radius == pytest.approx(1.0)


def test_shortest_path_length_rejects_out_of_range_indices():
    centers = np.array([[0.0, 0.0, 0.0]], dtype=float)

    with pytest.raises(ValueError, match='neighbor_pairs contains out-of-range indices'):
        shortest_path_length(
            centers,
            neighbor_pairs=[(0, 1)],
            start_indices=[0],
            end_indices=[0],
        )


def test_thickness_profile_rejects_out_of_range_neighbor_indices():
    centers = np.array([[0.0, 0.0, 0.0]], dtype=float)

    with pytest.raises(ValueError, match='neighbor_pairs contains out-of-range indices'):
        thickness_profile(
            centers,
            axis=np.array([1.0, 0.0, 0.0]),
            neighbor_pairs=[(0, 1)],
        )
