import numpy as np

from topomt.dfnd.components import build_components
from topomt.dfnd.graph import DelaunayFlowNetwork
from topomt.dfnd.identity import (
    component_key,
    component_sort_key,
    external_link_key,
    external_link_support_key,
    motif_key,
    result_key,
    substrate_key,
    support_key,
)


def _regular_tetrahedron_network(atom_indices=None):
    coordinates = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )
    radii = np.full(4, 1.7, dtype=float)
    return DelaunayFlowNetwork.from_arrays(
        coordinates,
        radii,
        atom_indices=atom_indices,
    )


def test_support_key_uses_atom_defined_tetrahedra_not_node_order():
    support_a = [(9, 4, 7, 2), (8, 5, 7, 2)]
    support_b = [(2, 7, 5, 8), (7, 2, 9, 4)]

    assert support_key(support_a) == support_key(support_b)
    assert support_key(support_a) != support_key([(9, 4, 7, 3), (8, 5, 7, 2)])


def test_external_link_support_uses_atom_defined_faces_not_face_order():
    faces_a = [(9, 4, 7), (8, 5, 7)]
    faces_b = [(7, 5, 8), (4, 9, 7)]

    assert external_link_support_key(faces_a) == external_link_support_key(faces_b)
    assert external_link_support_key(faces_a) != external_link_support_key(
        [(9, 4, 6), (8, 5, 7)]
    )


def test_substructure_contextual_keys_include_parent_component_and_type():
    support = external_link_support_key([(4, 7, 9)])

    assert external_link_key('component-a', support) != external_link_key(
        'component-b', support
    )
    assert motif_key('component-a', 'external_mouth', support) != motif_key(
        'component-a', 'throat_candidate', support
    )


def test_result_and_component_keys_are_contextual_but_support_key_is_not():
    support = support_key([(2, 4, 7, 9)])
    substrate = substrate_key(
        {'atom_indices': [2, 4, 7, 9], 'coordinates': [[0.0, 0.0, 0.0]]}
    )
    low_probe = result_key({'substrate_key': substrate}, {'probe_radius': 1.4})
    high_probe = result_key({'substrate_key': substrate}, {'probe_radius': 2.0})

    assert low_probe != high_probe
    assert component_key(low_probe, 'wet', support) != component_key(
        high_probe, 'wet', support
    )
    assert component_key(low_probe, 'wet', support) != component_key(
        low_probe, 'dry', support
    )


def test_component_sort_key_uses_support_key_to_break_equal_node_counts():
    first = {'n_nodes': 3, 'support_key': 'aaa', 'graph_label': 99}
    second = {'n_nodes': 3, 'support_key': 'bbb', 'graph_label': 0}

    assert sorted([second, first], key=component_sort_key) == [first, second]


def test_raw_and_typed_components_expose_static_identity_contract():
    network = _regular_tetrahedron_network(atom_indices=[10, 20, 30, 40])
    result = network.get_topography(probe_radius=1.4, min_size=0)

    raw_component = result['raw']['wet_components'][0]
    assert raw_component['component_index'] == 0
    assert raw_component['node_count_rank'] == 1
    assert raw_component['size_rank'] == raw_component['node_count_rank']
    assert raw_component['support_key']
    assert raw_component['component_key']
    assert result['raw']['parameters']['substrate_key'] == network.substrate_key
    assert result['raw']['parameters']['result_key']

    component = build_components(result, network).wet[0]
    assert component.node_count_rank == raw_component['node_count_rank']
    assert all(
        motif['parent_component_key'] == component.component_key
        for motif in component.motifs
    )
    assert all(motif['motif_support_key'] for motif in component.motifs)
    assert all(motif['motif_key'] for motif in component.motifs)
    assert len({motif['motif_key'] for motif in component.motifs}) == len(
        component.motifs
    )
    assert component.external_link_keys == [
        link['external_link_key'] for link in result['raw']['external_links']
    ]
    for motifs in (
        component.depth_regions,
        component.throat_candidates,
        component.chamber_candidates,
    ):
        assert all(
            motif['parent_component_key'] == component.component_key for motif in motifs
        )
    if component.bottleneck is not None:
        assert component.bottleneck['parent_component_key'] == component.component_key
    assert component.size_rank == component.node_count_rank
    assert component.support_key == raw_component['support_key']
    assert component.component_key == raw_component['component_key']

    dry_result = network.get_topography(probe_radius=10.0, min_size=0)
    raw_dry_component = dry_result['dry']['components'][0]
    dry_component = build_components(dry_result, network).dry[0]
    assert raw_dry_component['node_count_rank'] == 1
    assert raw_dry_component['size_rank'] == raw_dry_component['node_count_rank']
    assert dry_component.support_key == raw_dry_component['support_key']
    assert dry_component.component_key == raw_dry_component['component_key']
    assert dry_component.motif_keys == raw_dry_component['motif_keys']


def test_support_key_survives_probe_change_while_component_key_changes():
    network = _regular_tetrahedron_network(atom_indices=[10, 20, 30, 40])
    low_probe = network.get_topography(probe_radius=1.0, min_size=0)
    high_probe = network.get_topography(probe_radius=1.4, min_size=0)

    low_component = low_probe['raw']['wet_components'][0]
    high_component = high_probe['raw']['wet_components'][0]

    assert low_component['support_key'] == high_component['support_key']
    assert low_component['component_key'] != high_component['component_key']


def test_component_relations_carry_contextual_component_keys():
    network = _regular_tetrahedron_network(atom_indices=[10, 20, 30, 40])
    wet_result = network.get_topography(probe_radius=1.4, min_size=0)
    wet_component = wet_result['raw']['wet_components'][0]

    for region in wet_result['raw']['residence_regions']:
        assert region['component_key'] == wet_component['component_key']
    for link in wet_result['raw']['external_links']:
        assert link['component_key'] == wet_component['component_key']
        assert link['external_link_support_key']
        assert link['external_link_key']
        assert link['R_gate_min'] <= link['R_gate_mean'] <= link['R_gate_max']
    assert len(
        {link['external_link_key'] for link in wet_result['raw']['external_links']}
    ) == len(wet_result['raw']['external_links'])

    dry_result = network.get_topography(probe_radius=10.0, min_size=0)
    dry_by_id = {
        component['id']: component for component in dry_result['dry']['components']
    }
    for interface in dry_result['dry']['interfaces']:
        assert (
            interface['dry_component_key']
            == dry_by_id[interface['dry_component_id']]['component_key']
        )
        target_id = interface['target_dry_component_id']
        assert interface['target_dry_component_key'] == (
            dry_by_id[target_id]['component_key'] if target_id is not None else None
        )
    for motif in dry_result['dry']['motifs']:
        assert (
            motif['dry_component_key']
            == dry_by_id[motif['dry_component_id']]['component_key']
        )
        assert motif['motif_support_key']
        assert motif['motif_key']
    assert len({motif['motif_key'] for motif in dry_result['dry']['motifs']}) == len(
        dry_result['dry']['motifs']
    )
