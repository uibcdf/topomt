"""Analytic validation of the precise empty-volume integrator.

Each case has a closed-form answer; the integrator's rigorous error half-width
must bound the deviation, and the estimate must be accurate at a small
tolerance. Mirrors the metrics_contract.md validation battery (zero radius,
single sphere, overlapping spheres, convergence).
"""

import math

import numpy as np
import pytest

from topomt.dfnd.core.solvent_volume import (
    ball_tetrahedron_volume,
    region_empty_volume,
    region_empty_volume_exact,
    region_occupancy_grid,
    tetrahedron_empty_volume,
    tetrahedron_volume,
)

# A large regular tetrahedron; small balls placed near its centroid stay
# strictly interior, so analytic empty = vol(tet) - vol(union of balls).
_EDGE = 10.0
_TET = np.array(
    [
        [_EDGE / 2, 0.0, -_EDGE / (2 * math.sqrt(2))],
        [-_EDGE / 2, 0.0, -_EDGE / (2 * math.sqrt(2))],
        [0.0, _EDGE / 2, _EDGE / (2 * math.sqrt(2))],
        [0.0, -_EDGE / 2, _EDGE / (2 * math.sqrt(2))],
    ],
    dtype=float,
)
_CENTROID = _TET.mean(axis=0)
_TET_VOLUME = tetrahedron_volume(_TET)


def _ball_volume(r):
    return 4.0 / 3.0 * math.pi * r**3


def test_no_balls_is_full_tetrahedron():
    result = tetrahedron_empty_volume(_TET, np.empty((0, 3)), np.empty((0,)))
    assert result.volume == pytest.approx(_TET_VOLUME)
    assert result.error == 0.0


def test_single_ball_covering_tetrahedron_is_empty_zero():
    # one huge ball at the centroid contains all vertices -> fully occupied
    result = tetrahedron_empty_volume(_TET, _CENTROID[None, :], np.array([_EDGE]))
    assert result.volume == 0.0
    assert result.error == 0.0


def test_distant_ball_does_not_reduce_volume():
    far = _CENTROID + np.array([1000.0, 0.0, 0.0])
    result = tetrahedron_empty_volume(_TET, far[None, :], np.array([1.0]))
    assert result.volume == pytest.approx(_TET_VOLUME)
    assert result.error == 0.0


def test_single_interior_ball_matches_analytic_within_error():
    r = 1.0
    analytic = _TET_VOLUME - _ball_volume(r)
    result = tetrahedron_empty_volume(_TET, _CENTROID[None, :], np.array([r]))
    # accurate estimate with a small, honest statistical error bound
    assert abs(result.volume - analytic) < 0.02 * _TET_VOLUME
    assert 0.0 < result.error < 0.02 * _TET_VOLUME
    assert abs(result.volume - analytic) <= 3.0 * result.error


def test_overlapping_balls_subtract_union_not_sum():
    # two equal interior balls; overlap must NOT be subtracted twice
    r = 1.0
    d = 1.2  # centers distance < 2r -> they overlap
    c_a = _CENTROID + np.array([d / 2, 0.0, 0.0])
    c_b = _CENTROID - np.array([d / 2, 0.0, 0.0])
    # analytic lens (intersection) volume for two equal spheres, distance d (< 2r):
    lens = math.pi * (4 * r + d) * (2 * r - d) ** 2 / 12.0
    union = 2 * _ball_volume(r) - lens
    analytic = _TET_VOLUME - union

    result = tetrahedron_empty_volume(_TET, np.vstack([c_a, c_b]), np.array([r, r]))
    assert abs(result.volume - analytic) < 0.02 * _TET_VOLUME
    assert abs(result.volume - analytic) <= 3.0 * result.error
    # the naive (double-subtracted) value would be total - 2*ball: must differ
    double_subtracted = _TET_VOLUME - 2 * _ball_volume(r)
    assert result.volume > double_subtracted + lens / 2


def test_error_shrinks_with_more_samples():
    r = 1.5
    coarse = tetrahedron_empty_volume(
        _TET, _CENTROID[None, :], np.array([r]), n_samples=2000
    )
    fine = tetrahedron_empty_volume(
        _TET, _CENTROID[None, :], np.array([r]), n_samples=50000
    )
    assert fine.error < coarse.error
    analytic = _TET_VOLUME - _ball_volume(r)
    assert abs(fine.volume - analytic) <= 3.0 * fine.error


def test_region_volume_sums_tetrahedra_without_balls():
    far = _TET + np.array([100.0, 0.0, 0.0])
    region = np.stack([_TET, far])
    result = region_empty_volume(region, np.empty((0, 3)), np.empty((0,)))
    assert result.volume == pytest.approx(2.0 * _TET_VOLUME)
    assert result.error == 0.0


def test_region_volume_subtracts_ball_from_union():
    far = _TET + np.array([100.0, 0.0, 0.0])
    region = np.stack([_TET, far])
    r = 1.0
    result = region_empty_volume(region, _CENTROID[None, :], np.array([r]))
    analytic = 2.0 * _TET_VOLUME - _ball_volume(r)
    assert abs(result.volume - analytic) < 0.02 * (2.0 * _TET_VOLUME)


def test_occupancy_grid_volume_cross_checks_analytic():
    r = 1.0
    analytic = _TET_VOLUME - _ball_volume(r)
    result = region_occupancy_grid(
        _TET[None], _CENTROID[None, :], np.array([r]), spacing=0.3
    )
    # voxel volume agrees with the closed form within the discretization error
    assert abs(result.volume - analytic) < 0.05 * _TET_VOLUME
    # the grid is the 3D shape of the void
    assert result.grid.dtype == bool
    assert result.grid.sum() > 0
    assert result.spacing == 0.3


def test_occupancy_grid_no_balls_fills_region():
    result = region_occupancy_grid(
        _TET[None], np.empty((0, 3)), np.empty((0,)), spacing=0.3
    )
    assert abs(result.volume - _TET_VOLUME) < 0.05 * _TET_VOLUME


def test_occupancy_grid_agrees_with_monte_carlo():
    r = 1.2
    grid = region_occupancy_grid(
        _TET[None], _CENTROID[None, :], np.array([r]), spacing=0.25
    )
    mc = tetrahedron_empty_volume(_TET, _CENTROID[None, :], np.array([r]))
    assert abs(grid.volume - mc.volume) < 0.05 * _TET_VOLUME


def test_ball_tetrahedron_inside_is_ball_volume_exact():
    r = 1.0  # ball strictly inside the big tetrahedron
    v = ball_tetrahedron_volume(_TET, _CENTROID, r)
    assert abs(v - _ball_volume(r)) < 1e-6 * _TET_VOLUME


def test_ball_tetrahedron_covering_is_tetrahedron_volume_exact():
    v = ball_tetrahedron_volume(_TET, _CENTROID, 50.0)  # ball contains the tet
    assert abs(v - _TET_VOLUME) < 1e-6 * _TET_VOLUME


def test_ball_tetrahedron_partial_agrees_with_monte_carlo():
    vertex = _TET[0]
    r = 3.0  # ball at a vertex, partly outside the tet
    exact = ball_tetrahedron_volume(_TET, vertex, r, n_quad=48)
    empty = tetrahedron_empty_volume(_TET, vertex[None, :], np.array([r]))
    mc_ball_tet = _TET_VOLUME - empty.volume  # vol(ball ∩ tet) via MC
    assert abs(exact - mc_ball_tet) < 0.02 * _TET_VOLUME


def test_exact_single_interior_ball_matches_analytic():
    r = 1.0
    v = region_empty_volume_exact(_TET[None], _CENTROID[None, :], np.array([r]))
    assert abs(v - (_TET_VOLUME - _ball_volume(r))) < 1e-3 * _TET_VOLUME


def test_exact_overlapping_balls_subtract_union():
    r, d = 1.0, 1.2
    c_a = _CENTROID + np.array([d / 2, 0.0, 0.0])
    c_b = _CENTROID - np.array([d / 2, 0.0, 0.0])
    lens = math.pi * (4 * r + d) * (2 * r - d) ** 2 / 12.0
    union = 2 * _ball_volume(r) - lens
    v = region_empty_volume_exact(_TET[None], np.vstack([c_a, c_b]), np.array([r, r]))
    # exact handles the overlap (no double subtraction of the lens)
    assert abs(v - (_TET_VOLUME - union)) < 1e-3 * _TET_VOLUME


def test_exact_agrees_with_monte_carlo_on_overlapping_vertex_balls():
    atoms = np.vstack([_TET, _CENTROID])
    radii = np.array([3.0, 3.0, 3.0, 3.0, 1.5])  # heavily overlapping
    v_exact = region_empty_volume_exact(_TET[None], atoms, radii, n_quad=32)
    mc = region_empty_volume(_TET[None], atoms, radii, n_samples=300000)
    assert abs(v_exact - mc.volume) <= 2 * mc.error + 0.01 * _TET_VOLUME


def test_on_demand_component_solvent_volume_is_wired():
    from topomt import pyunitwizard as puw
    from topomt.dfnd import synthetic
    from topomt.dfnd.data import DFNDData
    from topomt.dfnd.graph import DelaunayFlowNetwork

    system = synthetic.hollow_sphere()
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        system.coords, system.radii
    )
    data = DFNDData(network, network.get_topography())
    wet = [
        c
        for c in data.dfn.components.values()
        if c.side == 'wet' and c.resident_node_indices
    ]
    assert wet, 'expected a wet component with residence'
    cid = wet[0].component_id

    volume, error = data.solvent_volume(cid, region='resident')
    v = puw.get_value(volume, to_unit='nm**3')
    assert v > 0.0
    assert puw.get_value(error, to_unit='nm**3') >= 0.0
    # transit region (resident + connectors) is never smaller than resident
    volume_t, _ = data.solvent_volume(cid, region='transit')
    assert puw.get_value(volume_t, to_unit='nm**3') >= v - 1e-9
    # a fixed seed is reproducible
    volume_again, _ = data.solvent_volume(cid, region='resident')
    assert puw.get_value(volume_again, to_unit='nm**3') == v

    # the on-demand occupancy grid (shape) is wired and roughly agrees with MC
    shape = data.occupancy_grid(cid, region='resident', spacing=0.05)
    assert shape['grid'] is not None and shape['grid'].dtype == bool
    assert shape['grid'].sum() > 0
    v_grid = puw.get_value(shape['volume'], to_unit='nm**3')
    assert abs(v_grid - v) < 0.3 * v
