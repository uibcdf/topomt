"""Threshold margins, fixed-policy nesting and mapped numerical observables."""

import copy
from dataclasses import replace
from math import sqrt

import numpy as np
import pytest

from devtools.verify_volume_reference import regular_vertex_sector_volume
from tests.test_benchlab_public_topography import load_case, public_result, values
from topomt import pyunitwizard as puw
from topomt.dfnd.config import DFNDQuery
from topomt.dfnd.data import DFNDData
from topomt.dfnd.graph import DelaunayFlowNetwork


def frozen_network(mode='identity'):
    _, fixture, _ = load_case('regular_tetrahedron')
    coords = values(fixture['coordinates'], 'coordinates', 'nm')
    radii = values(fixture['atom_radii'], 'atom_radii', 'nm')
    epsilon = float(values(fixture['epsilon'], 'epsilon', 'nm'))
    mapping = np.arange(4)
    scale = 1.0
    if mode == 'rotation':
        theta = 0.413
        rotation = np.array(
            [
                [np.cos(theta), -np.sin(theta), 0.0],
                [np.sin(theta), np.cos(theta), 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        coords = coords @ rotation.T + np.array([2.5, -7.2, 1.1]) / 10
    elif mode == 'permutation':
        order = [2, 0, 3, 1]
        coords, radii, mapping = coords[order], radii[order], mapping[order]
    elif mode == 'similarity':
        scale = 3.0
        coords, radii, epsilon = coords * scale, radii * scale, epsilon * scale
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        puw.quantity(coords, 'nm'),
        puw.quantity(radii, 'nm'),
        atom_indices=mapping,
        epsilon=puw.quantity(epsilon, 'nm'),
    )
    return network, scale


@pytest.mark.parametrize('capacity', ['gate', 'residence'])
def test_below_at_above_analytic_threshold_preserves_marginality(capacity):
    network, _ = frozen_network()
    radius = 5.3 / sqrt(3) - 1.7 if capacity == 'gate' else sqrt(6) * 5.3 / 4 - 1.7
    for offset in (-1e-4, 0.0, 1e-4):
        query = DFNDQuery(probe_radius=(radius + offset) / 10)
        raw = network.get_topography(query=query, min_size=0)['raw']
        cell = raw['tetrahedra'][0]
        if offset == 0:
            assert 'marginal' in cell['flags']
            if capacity == 'gate':
                assert all('marginal' in face['flags'] for face in raw['faces'])
        elif capacity == 'gate':
            assert all(
                (face['permeability_state'] == 'permeable') == (offset < 0)
                for face in raw['faces']
            )
        else:
            assert (cell['residence_state'] == 'resident') == (offset < 0)
        physical = raw['boundary_connectivity']
        if physical['status'] == 'resolved':
            expected = 4 if capacity == 'gate' and offset < 0 else 0
            assert physical['n_patches'] == expected
        else:
            assert physical['status'] == 'unresolved'
            assert physical['n_patches'] is None and physical['reason']


@pytest.mark.parametrize('policy', ['with_connectors', 'resident_only'])
def test_fixed_model_primitive_availability_is_nested_without_count_constraints(policy):
    network, _ = frozen_network()
    previous = None
    for probe in (0.05, 0.2, 1.2, 1.4, 1.7, 3.0, 5.0):
        states = network._compute_query_states(
            probe / 10, 0.0, 0.0, policy, 'flag_only'
        )
        current = (states.resident, states.face_permeable, states.finite_transit)
        if previous is not None:
            for lower, higher in zip(previous, current, strict=True):
                assert np.all(~higher | lower)
        previous = tuple(mask.copy() for mask in current)


def test_cached_shell_query_matches_fresh_source_support_and_preserves_history():
    original = public_result('closed_shell', 1.4)[0].dfnd
    before = copy.deepcopy(original.raw)
    reused = original.at_probe(puw.quantity(0.2, 'angstroms'))
    fresh = public_result('closed_shell', 0.2)[0].dfnd
    assert reused.network is original.network
    assert original.raw == before
    assert reused.dfn.query == fresh.dfn.query

    def partition(data):
        return {
            (c.side, frozenset(tuple(sorted(tet)) for tet in c.tetrahedron_support))
            for c in data.dfn.components.values()
        }

    assert partition(reused) == partition(fresh)
    for field in ('status', 'n_patches'):
        assert (
            reused.raw['boundary_connectivity'][field]
            == fresh.raw['boundary_connectivity'][field]
        )


@pytest.mark.parametrize('mode', ['identity', 'rotation', 'permutation', 'similarity'])
@pytest.mark.parametrize('units', [['nm', 'ps', 'radians'], ['pm', 'fs', 'radians']])
def test_mapped_volume_and_physical_observables_keep_units_and_declared_accuracy(
    mode, units
):
    with puw.context(standard_units=units):
        network, scale = frozen_network(mode)
        query = replace(
            DFNDQuery(), probe_radius=0.12 * scale, boundary_tolerance=1e-7 * scale
        )
        data = DFNDData(network, network.get_topography(query=query, min_size=0))
        component = data.dfn.components.wet[0]
        physical = data.raw['boundary_connectivity']
        assert physical['status'] == 'resolved' and physical['n_patches'] == 4
        assert sorted(component.tetrahedron_support[0]) == [0, 1, 2, 3]
        assert network.epsilon == pytest.approx(1e-7 * scale)
        reference = regular_vertex_sector_volume(
            network.atom_coords, network.atom_radii
        )
        measured = data.solvent_volume_measurement(
            component.component_id, method='quadrature', n_quad=12, max_order=96
        )
        volume = float(puw.get_value(measured['volume'], to_unit='nm**3'))
        assert (
            abs(volume - reference['empty_volume'])
            <= 1e-4 * reference['carrier_volume']
        )
        if measured['status'] == 'converged':
            assert measured['error_kind'] == 'successive_order_difference'
        else:
            assert measured['status'] == 'unresolved' and measured['error'] is None
        sampling = data.solvent_volume_measurement(
            component.component_id, n_samples=4096
        )
        low, high = [
            float(puw.get_value(v, to_unit='nm**3')) for v in sampling['interval']
        ]
        assert low <= reference['empty_volume'] <= high
        assert float(puw.get_value(sampling['error'], to_unit='nm**3')) > 0
