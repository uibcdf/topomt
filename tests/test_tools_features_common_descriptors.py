"""Tests for common feature descriptors in topomt.tools.features."""

import numpy as np

from topomt.tools.features.common import (
    bounding_metrics,
    effective_center_radius,
)


def test_bounding_metrics_returns_expected_keys():

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

    metrics = bounding_metrics(points)

    assert set(metrics.keys()) == {'centroid', 'axes', 'lengths', 'elongation'}
    assert metrics['centroid'].shape == (3,)
    assert metrics['axes'].shape == (3, 3)
    assert metrics['lengths'].shape == (3,)
    assert metrics['elongation'] >= 1.0


def test_effective_center_radius_returns_centroid_and_distances():

    points = np.array(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
        ],
        dtype=float,
    )

    centroid, mean_radius, max_radius = effective_center_radius(points)

    assert np.allclose(centroid, np.zeros(3))
    assert mean_radius == 1.0
    assert max_radius == 1.0
