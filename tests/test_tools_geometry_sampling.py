"""Tests for sampling-based geometry helpers in topomt.tools.geometry."""

import numpy as np
import pytest

from topomt.tools.geometry.sampling import union_volume_monte_carlo


def test_union_volume_monte_carlo_returns_zero_for_empty_input():

    volume = union_volume_monte_carlo(
        centers=np.zeros((0, 3), dtype=float),
        radii=np.zeros(0, dtype=float),
        n_samples=1000,
        rng=np.random.default_rng(123),
    )

    assert volume == 0.0


def test_union_volume_monte_carlo_estimates_single_sphere_volume():

    radius = 1.0
    expected = 4.0 * np.pi * radius**3 / 3.0

    volume = union_volume_monte_carlo(
        centers=np.array([[0.0, 0.0, 0.0]], dtype=float),
        radii=np.array([radius], dtype=float),
        n_samples=200000,
        rng=np.random.default_rng(123),
    )

    assert np.isclose(volume, expected, rtol=0.05)

def test_union_volume_monte_carlo_rejects_non_positive_sample_count():

    with pytest.raises(ValueError, match='n_samples must be a positive integer'):
        union_volume_monte_carlo(
            centers=np.array([[0.0, 0.0, 0.0]], dtype=float),
            radii=np.array([1.0], dtype=float),
            n_samples=0,
        )
