"""Tests for mouth descriptor helpers in topomt.tools.features."""

import numpy as np

from topomt.tools.features.mouths import mouth_area_on_plane


def test_mouth_area_on_plane_returns_projected_square_area():

    mouth_points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )

    area = mouth_area_on_plane(
        mouth_points,
        plane_point=np.array([0.0, 0.0, 0.0]),
        plane_normal=np.array([0.0, 0.0, 1.0]),
    )

    assert area == 1.0


def test_mouth_area_on_plane_returns_zero_with_fewer_than_three_points():

    mouth_points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=float,
    )

    area = mouth_area_on_plane(
        mouth_points,
        plane_point=np.zeros(3),
        plane_normal=np.array([0.0, 0.0, 1.0]),
    )

    assert area == 0.0


def test_mouth_area_on_plane_returns_zero_with_degenerate_normal():

    mouth_points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        dtype=float,
    )

    area = mouth_area_on_plane(
        mouth_points,
        plane_point=np.zeros(3),
        plane_normal=np.zeros(3),
    )

    assert area == 0.0
