"""Separate local residence from native wet/dry component membership."""

import numpy as np
import pytest

from tests.test_benchlab_public_topography import public_result
from topomt.dfnd.data import Graph


@pytest.fixture(scope='module')
def closed_shell():
    return public_result('closed_shell', 0.2)[0].dfnd


def test_actual_nonresident_connectors_belong_to_wet_component_neighbors(closed_shell):
    data = closed_shell
    wet = next(c for c in data.dfn.components.wet if c.transit_connector_node_indices)
    connector = wet.transit_connector_node_indices[0]
    node = data.mesh.neighbors(connector)[0]
    graph = data.dfn.graph
    assert connector in graph.neighbors(node, side='dry')
    assert connector in graph.neighbors(node, component_side='wet')
    assert connector not in graph.neighbors(node, component_side='dry')
    assert connector in graph.neighbors(node, side='dry', component_side='wet')


def test_component_side_queries_match_complete_native_membership(closed_shell):
    data = closed_shell
    graph = data.dfn.graph
    wet = {node for c in data.dfn.components.wet for node in c.node_indices}
    dry = {node for c in data.dfn.components.dry for node in c.node_indices}
    for node in range(len(data.mesh.tetrahedra)):
        all_neighbors = set(graph.neighbors(node))
        wet_neighbors = set(graph.neighbors(node, component_side='wet'))
        dry_neighbors = set(graph.neighbors(node, component_side='dry'))
        assert wet_neighbors == all_neighbors & wet
        assert dry_neighbors == all_neighbors & dry
        assert wet_neighbors.isdisjoint(dry_neighbors)
        assert wet_neighbors | dry_neighbors == all_neighbors
        for neighbor in all_neighbors:
            assert node in graph.neighbors(
                neighbor, component_side='wet' if node in wet else 'dry'
            )


def test_component_lookup_does_not_rescan_all_node_records(closed_shell):
    import copy

    class NoIteration(list):
        def __iter__(self):
            raise AssertionError('Repeated neighbor queries must not rescan all nodes')

    graph = copy.copy(closed_shell.dfn.graph)
    graph.nodes = NoIteration(graph.nodes)
    assert isinstance(graph.neighbors(0, component_side='wet'), list)


def test_missing_legacy_transit_roles_are_unavailable_for_component_filtering():
    graph = Graph(
        {
            'tetrahedra': [
                {'tetrahedron_id': 0, 'residence_state': 'resident'},
                {'tetrahedron_id': 1, 'residence_state': 'non_resident'},
            ],
            'faces': [],
            'external_links': [],
        },
        adjacency=np.array([[1, -1, -1, -1], [0, -1, -1, -1]]),
    )
    assert graph.neighbors(0, side='dry') == [1]
    with pytest.raises(RuntimeError, match='role|context'):
        graph.neighbors(0, component_side='dry')


def test_invalid_component_side_is_not_an_empty_query(closed_shell):
    with pytest.raises(ValueError, match='component_side'):
        closed_shell.dfn.graph.neighbors(0, component_side='unknown')


def test_selecting_saved_neighbors_adds_no_fresh_calculation_credit(closed_shell):
    ackredit = pytest.importorskip('ackredit')

    with ackredit.session('read native adjacency'):
        closed_shell.dfn.graph.neighbors(0, component_side='wet')
        closed_shell.dfn.graph.neighbors(0, side='dry', component_side='wet')
        assert not ackredit.get_attribution().to_dict()['items']


def test_disabling_connectors_moves_their_native_side_to_banks(closed_shell):
    from topomt import pyunitwizard as puw

    data = closed_shell.at_probe(
        puw.quantity(0.2, 'angstroms'), transit_policy='resident_only'
    )
    graph = data.dfn.graph
    wet = {node for c in data.dfn.components.wet for node in c.node_indices}
    for node in range(len(data.mesh.tetrahedra)):
        expected = [neighbor for neighbor in graph.neighbors(node) if neighbor in wet]
        assert graph.neighbors(node, component_side='wet') == expected
        assert graph.neighbors(node, component_side='wet') == graph.neighbors(
            node, side='wet'
        )
