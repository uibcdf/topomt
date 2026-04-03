import numpy as np

from topomt.tools.geometry.hulls import convex_hull_metrics
from topomt.tools.geometry.primitives import triangle_area
from topomt.tools.tessellation.mouths import mouth_area_from_faces
from topomt.tools.tessellation.representatives import representative_points_from_tetra
from topomt.tools.tessellation.tetrahedra import analytic_tetra_volume


def test_triangle_area_returns_expected_right_triangle_area():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )

    assert triangle_area(points) == 0.5


def test_analytic_tetra_volume_returns_expected_unit_tetrahedron_volume():

    tetra_positions = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

    volume = analytic_tetra_volume(tetra_positions, [[0, 1, 2, 3]])

    assert np.isclose(volume, 1.0 / 6.0)


def test_mouth_area_from_faces_sums_triangle_areas():

    atom_coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

    area = mouth_area_from_faces([(0, 1, 2), (0, 1, 3)], atom_coords)

    assert np.isclose(area, 1.0)


def test_representative_points_from_tetra_returns_group_centroids():

    tetra_positions = np.array(
        [
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            [
                [1.0, 1.0, 1.0],
                [2.0, 1.0, 1.0],
                [1.0, 2.0, 1.0],
                [1.0, 1.0, 2.0],
            ],
        ],
        dtype=float,
    )

    representatives = representative_points_from_tetra([[0], [1]], tetra_positions)

    assert len(representatives) == 2
    assert np.allclose(representatives[0], [0.25, 0.25, 0.25])
    assert np.allclose(representatives[1], [1.25, 1.25, 1.25])


def test_convex_hull_metrics_returns_volume_and_area():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

    volume, area = convex_hull_metrics(points)

    assert volume is not None
    assert area is not None
