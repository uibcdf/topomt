"""Independent Cartesian integration and justified tetrahedral sector controls."""

import math

import numpy as np
import pytest


def test_cartesian_membership_counts_union_once_and_keeps_nonlocal_obstacles():
    from devtools.verify_volume_reference import free_at_probes, inside_union

    cell = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )
    points = np.array([[0.1, 0.1, 0.1], [0.5, 0.5, 0.5], [0.2, 0.2, 0.2]])
    assert inside_union(points, np.array([cell, cell])).tolist() == [True, False, True]
    bare, expanded = free_at_probes(
        points, np.array([[0.2, 0.2, 0.2]]), np.array([0.05]), 0.15
    )
    assert bare.tolist() == [True, True, False]
    assert expanded.tolist() == [False, True, False]


def test_vertex_sectors_require_disjoint_untruncated_regular_ball_intersections():
    from devtools.verify_volume_reference import regular_vertex_sector_volume

    vertices = np.array(
        [[1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, -1.0, 1.0]]
    )
    edge = math.sqrt(8)
    result = regular_vertex_sector_volume(vertices, np.full(4, 0.5))
    omega = 3 * math.acos(1 / 3) - math.pi
    assert result['empty_volume'] == pytest.approx(
        edge**3 / (6 * math.sqrt(2)) - 4 * omega * 0.5**3 / 3
    )
    with pytest.raises(ValueError, match='overlap'):
        regular_vertex_sector_volume(vertices, np.full(4, 1.5))


def test_hoeffding_interval_retains_finite_endpoint_width_and_explicit_confidence():
    from devtools.verify_volume_reference import hoeffding_interval

    low, high, width = hoeffding_interval(0, 1024, 2.0, 0.999, 1.0)
    assert low == 0 and high > 0 and width > 0
    expected = 2 * math.sqrt(math.log(2 / (1 - 0.999)) / (2 * 1024))
    assert width == pytest.approx(expected)
    assert high <= 1.0


def test_cartesian_reference_checks_analytic_empty_support_without_topomt_sampler():
    from devtools.verify_volume_reference import integrate_domain

    cell = np.array(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    )
    result = integrate_domain(
        cell[None],
        np.empty((0, 3)),
        np.empty(0),
        0.2,
        n_samples=8192,
        seed=82371,
        confidence=0.999,
        batch_size=1024,
    )
    assert result['carrier_volume'] == pytest.approx(1 / 6)
    for key in ('bare_empty', 'probe_center'):
        interval = result[key]['interval']
        assert interval[0] <= 1 / 6 <= interval[1]
