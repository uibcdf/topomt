"""Tests for mesh-oriented geometry helpers."""

import numpy as np
import pytest

from topomt.tools.geometry.meshes import _mesh_volume_area, marching_cubes_union


def _unit_tetrahedron_mesh():
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    faces = np.array(
        [
            [0, 2, 1],
            [0, 1, 3],
            [0, 3, 2],
            [1, 2, 3],
        ],
        dtype=int,
    )
    return vertices, faces


def test_mesh_volume_area_uses_signed_sum_for_closed_mesh_volume():
    vertices, faces = _unit_tetrahedron_mesh()

    volume, area = _mesh_volume_area(vertices, faces)

    assert volume == pytest.approx(1.0 / 6.0)
    assert area > 0.0


def test_mesh_volume_area_does_not_sum_absolute_face_contributions():
    vertices, faces = _unit_tetrahedron_mesh()
    vertices = vertices + np.array([1.0, 1.0, 1.0])

    volume, _ = _mesh_volume_area(vertices, faces)

    assert volume == pytest.approx(1.0 / 6.0)


def test_mesh_volume_area_rejects_invalid_shapes():
    with pytest.raises(ValueError, match='vertices must have shape'):
        _mesh_volume_area(np.zeros((3,), dtype=float), np.zeros((0, 3), dtype=int))

    with pytest.raises(ValueError, match='faces must have shape'):
        _mesh_volume_area(np.zeros((4, 3), dtype=float), np.zeros((3,), dtype=int))


def test_mesh_volume_area_rejects_out_of_range_faces():
    vertices, _ = _unit_tetrahedron_mesh()

    with pytest.raises(ValueError, match='faces contain out-of-range vertex indices'):
        _mesh_volume_area(vertices, np.array([[0, 1, 4]], dtype=int))


def test_marching_cubes_union_rejects_non_positive_grid_spacing():
    with pytest.raises(ValueError, match='grid_spacing must be positive'):
        marching_cubes_union([[0.0, 0.0, 0.0]], [1.0], grid_spacing=0.0)
