import numpy as np
import pytest

from topomt.dfnd.core.solvent_volume import (
    tetrahedron_solvent_volume_estimate,
    tetrahedron_solvent_volume_estimate_batch,
    tetrahedron_volume,
)


def _unit_tetrahedron():
    return np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def test_tetrahedron_volume_unit_simplex():
    assert tetrahedron_volume(_unit_tetrahedron()) == pytest.approx(1.0 / 6.0)


def test_solvent_volume_estimate_is_full_volume_when_local_radii_are_zero():
    vertices = _unit_tetrahedron()
    result = tetrahedron_solvent_volume_estimate(
        vertices,
        np.zeros(4, dtype=float),
        resolution=4,
    )

    assert result.volume == pytest.approx(tetrahedron_volume(vertices))
    assert result.empty_fraction == pytest.approx(1.0)
    assert result.occupied_fraction == pytest.approx(0.0)
    assert result.n_samples > 0


def test_solvent_volume_estimate_is_zero_when_local_spheres_cover_tetrahedron():
    vertices = _unit_tetrahedron()
    result = tetrahedron_solvent_volume_estimate(
        vertices,
        np.full(4, 10.0, dtype=float),
        resolution=4,
    )

    assert result.volume == pytest.approx(0.0)
    assert result.empty_fraction == pytest.approx(0.0)
    assert result.occupied_fraction == pytest.approx(1.0)


def test_solvent_volume_estimate_is_bounded_for_intermediate_radii():
    vertices = _unit_tetrahedron()
    result = tetrahedron_solvent_volume_estimate(
        vertices,
        np.full(4, 0.2, dtype=float),
        resolution=6,
    )
    total_volume = tetrahedron_volume(vertices)

    assert 0.0 <= result.volume <= total_volume
    assert 0.0 <= result.empty_fraction <= 1.0
    assert 0.0 <= result.occupied_fraction <= 1.0
    assert result.empty_fraction + result.occupied_fraction == pytest.approx(1.0)


def test_solvent_volume_batch_matches_scalar_estimator():
    vertices = np.stack([_unit_tetrahedron(), 2.0 * _unit_tetrahedron()])
    radii = np.array(
        [
            [0.2, 0.2, 0.2, 0.2],
            [0.3, 0.3, 0.3, 0.3],
        ],
        dtype=float,
    )
    volumes, empty, occupied, n_samples = tetrahedron_solvent_volume_estimate_batch(
        vertices,
        radii,
        resolution=5,
    )

    for index in range(vertices.shape[0]):
        scalar = tetrahedron_solvent_volume_estimate(
            vertices[index],
            radii[index],
            resolution=5,
        )
        assert volumes[index] == pytest.approx(scalar.volume)
        assert empty[index] == pytest.approx(scalar.empty_fraction)
        assert occupied[index] == pytest.approx(scalar.occupied_fraction)
        assert n_samples[index] == scalar.n_samples
