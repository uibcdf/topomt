"""Recover rich native supports through the real three-case public boundary."""

import pytest

from tests.test_benchlab_public_topography import public_result


@pytest.mark.parametrize(
    'case,probe',
    [
        ('regular_tetrahedron', 1.2),
        ('closed_shell', 0.2),
        ('shell_with_opening', 1.4),
        ('regular_tetrahedron', 1.7),
    ],
)
def test_public_audit_recovers_complete_supports_lining_and_depth_context(case, probe):
    from devtools.benchlab.public_contract import describe_public_contract

    topo = public_result(case, probe)[0]
    observed = describe_public_contract(topo)
    assert observed['node_inventory']['wet_nodes'] + observed['node_inventory'][
        'dry_nodes'
    ] == len(topo.dfnd.mesh.tetrahedra)
    assert observed['units'] == topo.dfnd.raw['units']
    assert observed['public_molecular_interface_validation'] == 'not_established'
    assert observed['versioned_public_topography_interchange'] == 'not_implemented'
    for wet in observed['wet_components']:
        assert set(wet['resident_node_indices']).isdisjoint(
            wet['connector_node_indices']
        )
        assert sorted(
            wet['resident_node_indices'] + wet['connector_node_indices']
        ) == sorted(wet['node_indices'])
        if not wet['native_external_link_ids']:
            assert wet['depth_reference'] == 'no_exterior_zero_convention'
        else:
            assert wet['depth_reference'] == 'native_exterior_graph_hops'


@pytest.mark.parametrize('damage', ['source_support', 'area', 'signature'])
def test_public_audit_rejects_corrupted_support_or_derived_observations(damage):
    from devtools.benchlab.public_contract import describe_public_contract

    topo = public_result('shell_with_opening', 1.4)[0]
    if damage == 'source_support':
        row = topo.dfnd.raw['tetrahedra'][0]
        row['atom_indices'][0] = row['atom_indices'][1]
    elif damage == 'area':
        topo.dfnd.dfn.components.coast_faces[0]['area'] *= 2
    else:
        feature = next(f for f in topo.values() if f.feature_type != 'mouth')
        feature.signature['n_mouths'] = 999
    with pytest.raises(ValueError):
        describe_public_contract(topo)
