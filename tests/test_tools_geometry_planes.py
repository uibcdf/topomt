"""Tests for plane-based geometry helpers in topomt.tools.geometry."""

import numpy as np

from topomt.tools.geometry.planes import clip_mesh_with_plane


def test_clip_mesh_with_plane_returns_square_area_and_perimeter():

    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    faces = np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
        ],
        dtype=int,
    )

    polygon, area, perimeter = clip_mesh_with_plane(
        vertices,
        faces,
        plane_point=np.zeros(3),
        plane_normal=np.array([0.0, 0.0, 1.0]),
    )

    assert polygon.shape == (4, 3)
    assert area == 1.0
    assert perimeter == 4.0


def test_clip_mesh_with_plane_returns_empty_for_zero_normal():

    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    faces = np.array([[0, 1, 2]], dtype=int)

    polygon, area, perimeter = clip_mesh_with_plane(
        vertices,
        faces,
        plane_point=np.zeros(3),
        plane_normal=np.zeros(3),
    )

    assert polygon.shape == (0, 3)
    assert area == 0.0
    assert perimeter == 0.0
