"""Contract tests for DFND mesh/query configuration and reporting filters."""

import inspect
from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from topomt import pyunitwizard as puw
from topomt.dfnd.config import DFNDMeshConfig, DFNDQuery
from topomt.dfnd.data import DFNDData
from topomt.dfnd.graph import DelaunayFlowNetwork


def _network():
    coordinates = np.array(
        [
            [0.0, 0.0, 0.0],
            [4.0, 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 4.0],
            [8.0, 0.0, 0.0],
            [8.0, 4.0, 0.0],
            [8.0, 0.0, 4.0],
            [8.0, 4.0, 4.0],
        ],
        dtype=float,
    )
    return DelaunayFlowNetwork.from_coordinates_and_radii(
        coordinates,
        np.full(len(coordinates), 1.5),
        epsilon=1e-7,
    )


def test_mesh_config_and_query_are_frozen_and_keep_epsilon_on_the_mesh_side():
    network = _network()

    assert isinstance(network.mesh_config, DFNDMeshConfig)
    assert network.mesh_config.epsilon == pytest.approx(1e-8)
    assert 'epsilon' not in DFNDQuery().to_dict()
    with pytest.raises(FrozenInstanceError):
        network.mesh_config.epsilon = 1e-6


def test_typed_configs_accept_quantities_and_normalize_to_nm():
    query = DFNDQuery(
        probe_radius=puw.quantity(1.4, 'angstroms'),
        residence_tolerance=puw.quantity(0.1, 'angstroms'),
        permeability_tolerance=puw.quantity(0.2, 'angstroms'),
    )
    mesh_config = DFNDMeshConfig(epsilon=puw.quantity(1e-6, 'angstroms'))

    assert query.probe_radius == pytest.approx(0.14)
    assert query.residence_tolerance == pytest.approx(0.01)
    assert query.permeability_tolerance == pytest.approx(0.02)
    assert mesh_config.epsilon == pytest.approx(1e-7)



def test_public_length_float_compatibility_warns_and_interprets_angstroms():
    from topomt.dfnd.api import _public_length_to_nm

    with pytest.warns(FutureWarning, match='bare float'):
        assert _public_length_to_nm('probe_radius', 1.4) == pytest.approx(0.14)
    with pytest.warns(FutureWarning, match='bare float'):
        assert _public_length_to_nm('residence_tolerance', 0.1) == pytest.approx(0.01)
    assert _public_length_to_nm(
        'permeability_tolerance', puw.quantity(0.2, 'angstroms')
    ) == pytest.approx(0.02)

def test_query_drives_result_identity_but_reporting_min_size_does_not():
    network = _network()
    query = DFNDQuery(probe_radius=0.14, dry_adjacency='vertex')

    unfiltered = network.get_topography(query=query, min_size=0)
    filtered = network.get_topography(query=query, min_size=1000)

    assert (
        unfiltered['raw']['parameters']['result_key']
        == filtered['raw']['parameters']['result_key']
    )
    assert unfiltered['raw']['parameters']['query'] == query.to_dict()
    assert filtered['raw']['parameters']['reporting']['min_size'] == 1000
    assert [item['component_key'] for item in unfiltered['dry']['components']] == [
        item['component_key'] for item in filtered['dry']['components']
    ]
    assert len(filtered['dry']['components']) == len(unfiltered['dry']['components'])


def test_at_probe_preserves_every_unspecified_query_and_reporting_option():
    network = _network()
    result = network.get_topography(
        query=DFNDQuery(
            probe_radius=puw.quantity(1.4, 'angstroms'),
            residence_tolerance=puw.quantity(0.1, 'angstroms'),
            permeability_tolerance=puw.quantity(0.2, 'angstroms'),
            transit_policy='resident_only',
            gate_intrusion_policy='block_suspect',
            dry_adjacency='vertex',
        ),
        min_size=7,
    )

    reprobed = DFNDData(network, result).at_probe(puw.quantity(1.2, 'angstroms'))

    assert reprobed.dfn.parameters['query'] == {
        **result['raw']['parameters']['query'],
        'probe_radius': pytest.approx(0.12),  # 1.2 angstroms -> nm
    }
    assert reprobed.dfn.parameters['reporting']['min_size'] == 7



def test_at_probe_warns_for_legacy_bare_float_probe_radius():
    network = _network()
    data = DFNDData(network, network.get_topography())

    with pytest.warns(FutureWarning, match='bare float'):
        reprobed = data.at_probe(1.2)

    assert reprobed.dfn.parameters['query']['probe_radius'] == pytest.approx(0.12)

def test_at_probe_rejects_mesh_configuration_overrides():
    network = _network()
    data = DFNDData(network, network.get_topography())

    with pytest.raises(ValueError, match='mesh configuration'):
        data.at_probe(1.2, epsilon=1e-5)


def test_sea_level_is_absent_from_dfnd_public_signatures():
    from topomt.dfnd.api import dfnd, dfnd_to_topography

    assert 'sea_level' not in inspect.signature(dfnd).parameters
    assert 'sea_level' not in inspect.signature(dfnd_to_topography).parameters
    assert (
        'sea_level'
        not in inspect.signature(DelaunayFlowNetwork.get_topography).parameters
    )


def test_network_rejects_non_default_arguments_that_conflict_with_query():
    network = _network()

    with pytest.raises(ValueError, match='query conflicts'):
        network.get_topography(query=DFNDQuery(probe_radius=0.20), probe_radius=1.5)


def test_epsilon_is_part_of_substrate_and_result_identity():
    first = _network()
    second = DelaunayFlowNetwork.from_coordinates_and_radii(
        first.atom_coords, first.atom_radii, epsilon=1e-5
    )

    assert first.substrate_key != second.substrate_key
    assert (
        first.get_topography()['raw']['parameters']['result_key']
        != second.get_topography()['raw']['parameters']['result_key']
    )


def test_min_size_marks_wet_and_dry_without_changing_decomposition():
    network = _network()
    unfiltered = network.get_topography(min_size=0)
    filtered = network.get_topography(min_size=1000)

    for side, key in (('raw', 'wet_components'), ('dry', 'components')):
        first = unfiltered[side][key]
        second = filtered[side][key]
        assert [item['component_key'] for item in first] == [
            item['component_key'] for item in second
        ]
        assert all(item['include_in_compatibility_view'] for item in first)
        assert not any(item['include_in_compatibility_view'] for item in second)


def test_mesh_config_freezes_mutable_sequence_inputs():
    selection = [1, 2, 3]
    config = DFNDMeshConfig(selection=selection, structure_indices=[0, 1])
    selection.append(4)

    assert config.selection == (1, 2, 3)
    assert config.structure_indices == (0, 1)
