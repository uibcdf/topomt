"""Mapped support, continuous paths and honest availability for #151."""

import copy
from dataclasses import replace

import numpy as np
import pytest

from tests.test_benchlab_public_topography import load_case, public_result, values
from topomt import pyunitwizard as puw
from topomt.dfnd.config import DFNDQuery
from topomt.dfnd.core import physical_boundary as physical
from topomt.dfnd.data import DFNDData
from topomt.dfnd.graph import DelaunayFlowNetwork


def network(coords=None, radii=None, atom_indices=None):
    _, fixture, _ = load_case('regular_tetrahedron')
    if coords is None:
        coords = values(fixture['coordinates'], 'coordinates', 'angstroms')
    if radii is None:
        radii = values(fixture['atom_radii'], 'atom_radii', 'angstroms')
    return DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, radii, atom_indices=atom_indices
    )


def test_patches_have_recoverable_clipped_support_and_whole_segment_evidence():
    topo = public_result('regular_tetrahedron', 1.2)[0]
    record = topo.dfnd.raw['boundary_connectivity']
    assert topo.dfnd.dfn.boundary_connectivity is record
    centers = np.asarray(record['surface']['coordinates'])
    expanded = (
        np.asarray(record['surface']['atomic_radii']) + record['query']['probe_radius']
    )
    paths = record['component_associations']['records']
    assert len(paths) == 4
    for patch in record['patches']:
        for selector in patch['support']['face_regions']:
            face = record['surface']['faces'][selector['face_index']]
            region = face['regions'][selector['region_index']]
            assert region['cells']
            point = np.asarray(region['witness'])
            assert (
                np.min(np.linalg.norm(centers - point, axis=1) - expanded)
                > record['query']['tolerance']
            )
    for association in paths:
        assert association['status'] == 'resolved'
        path = association['path']
        start, end = np.asarray(path['start']), np.asarray(path['attachment'])
        assert (
            physical.segment_clearance(start, end, centers, expanded)
            > record['query']['tolerance']
        )
        direction = np.asarray(path['exterior_ray_direction'])
        assert np.min((end - centers) @ direction) >= -1e-14
        assert path['carrier_cover'][0]['t_interval'][0] == 0.0
        assert path['carrier_cover'][-1]['t_interval'][1] == 1.0
    # Every seam is blocked in this analytic control; adjacency alone cannot glue.
    assert len(record['surface']['seams']) == 6
    assert not any(seam['free_t_intervals'] for seam in record['surface']['seams'])


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_physical_unit_contract_survives_application_standardization(policy):
    with puw.context(standard_units=[*policy, 'radians']):
        topo = public_result('shell_with_opening', 1.4)[0]
        record = topo.dfnd.raw['boundary_connectivity']
        assert record['status'] == 'resolved' and record['n_patches'] == 1
        assert record['units'] == {'length': 'nm', 'coordinates': 'nm'}
        assert record['query']['probe_radius'] == pytest.approx(0.14)
        assert (
            record['surface']['source_atom_indices']
            == topo.input_context.atom_indices.tolist()
        )


@pytest.mark.parametrize('mode', ['rotation', 'permutation', 'similarity'])
def test_physical_support_corresponds_under_mapped_geometric_changes(mode):
    original = network()
    coords = original.atom_coords * 10
    radii = original.atom_radii * 10
    mapping = original.atom_indices_map.copy()
    query = DFNDQuery(probe_radius=0.12)
    reference = original.get_topography(query=query)['raw']['boundary_connectivity']
    if mode == 'rotation':
        theta = 0.413
        rotation = np.array(
            [
                [np.cos(theta), -np.sin(theta), 0.0],
                [np.sin(theta), np.cos(theta), 0.0],
                [0.0, 0.0, 1.0],
            ]
        )
        coords = coords @ rotation.T + [2.5, -7.2, 1.1]
    elif mode == 'permutation':
        order = [2, 0, 3, 1]
        coords, radii, mapping = coords[order], radii[order], mapping[order]
    else:
        coords, radii = coords * 3, radii * 3
        query = replace(
            query,
            probe_radius=query.probe_radius * 3,
            boundary_tolerance=query.boundary_tolerance * 3,
        )
    changed = network(coords, radii, mapping).get_topography(query=query)['raw'][
        'boundary_connectivity'
    ]
    assert changed['status'] == 'resolved' and changed['n_patches'] == 4

    def support(record):
        return {
            tuple(sorted(patch['support']['carrier_faces_source_atom_indices'][0]))
            for patch in record['patches']
        }

    assert support(changed) == support(reference)
    assert all(
        item['status'] == 'resolved'
        for item in changed['component_associations']['records']
    )


def test_reporting_and_reprobe_reuse_preserve_physical_geometry():
    native = network()
    result = native.get_topography(query=DFNDQuery(probe_radius=0.12))
    filtered = native.get_topography(query=DFNDQuery(probe_radius=0.12), min_size=100)
    assert (
        filtered['raw']['boundary_connectivity']
        == result['raw']['boundary_connectivity']
    )
    assert not filtered['wet']['percolatings']
    reused = DFNDData(native, result).at_probe(puw.quantity(1.4, 'angstroms'))
    fresh = network().get_topography(
        query=DFNDQuery(probe_radius=puw.quantity(1.4, 'angstroms'))
    )
    assert reused.raw['boundary_connectivity'] == fresh['raw']['boundary_connectivity']
    assert reused.raw['boundary_connectivity']['n_patches'] == 0


@pytest.mark.parametrize(
    'option',
    [
        {'physical_boundary': False},
        {'boundary_max_faces': 1},
        {'boundary_max_atoms': 3},
        {'boundary_max_events': 1},
    ],
)
def test_unavailable_or_incomplete_is_never_a_computed_zero(option):
    result = network().get_topography(query=DFNDQuery(probe_radius=0.12, **option))
    record = result['raw']['boundary_connectivity']
    assert record['status'] == (
        'not_computed' if option.get('physical_boundary') is False else 'unresolved'
    )
    assert record['n_patches'] is None and record['patches'] == []
    assert record['reason']
    typed = DFNDData(network(), result)
    assert (
        typed.dfn.components.wet[0].boundary['physical_openings']['n_patches'] is None
    )


def test_missing_seam_and_incomplete_face_inventory_cannot_return_a_count(monkeypatch):
    native = network()
    faces = native.mesh.get_boundary_face_records()
    monkeypatch.setattr(
        type(native.mesh), 'get_boundary_face_records', lambda self: faces[:-1]
    )
    record = native.get_topography(query=DFNDQuery(probe_radius=0.12))['raw'][
        'boundary_connectivity'
    ]
    assert record['status'] == 'unresolved' and record['n_patches'] is None
    assert 'inventory' in record['reason']
    monkeypatch.setattr(
        type(native.mesh), 'get_boundary_face_records', lambda self: faces
    )
    function = physical.decompose_face

    def incomplete(*args, **kwargs):
        result = function(*args, **kwargs)
        result['inventory_complete'] = False
        return result

    monkeypatch.setattr(physical, 'decompose_face', incomplete)
    record = native.get_topography(query=DFNDQuery(probe_radius=0.12))['raw'][
        'boundary_connectivity'
    ]
    assert record['status'] == 'unresolved' and record['n_patches'] is None


def test_failed_path_search_does_not_erase_resolved_global_patches(monkeypatch):
    monkeypatch.setattr(physical, '_carrier_cover', lambda *args: None)
    result = network().get_topography(query=DFNDQuery(probe_radius=0.12))
    record = result['raw']['boundary_connectivity']
    assert record['status'] == 'resolved' and record['n_patches'] == 4
    assert record['component_associations']['status'] == 'unresolved'
    view = (
        DFNDData(network(), result).dfn.components.wet[0].boundary['physical_openings']
    )
    assert view['status'] == 'unresolved' and view['n_patches'] is None


def test_nested_physical_records_copy_deeply_without_retargeting_snapshots():
    topo = public_result('shell_with_opening', 1.4)[0]
    shallow, deep = topo.copy(deep=False), topo.copy(deep=True)
    assert shallow.dfnd is not topo.dfnd
    assert shallow.dfnd.raw is topo.dfnd.raw
    assert deep.dfnd is not topo.dfnd
    before = copy.deepcopy(topo.dfnd.raw['boundary_connectivity'])
    deep.dfnd.raw['boundary_connectivity']['query']['probe_radius'] = 99.0
    assert topo.dfnd.raw['boundary_connectivity'] == before
    assert not topo.dfnd.network.atom_coords.flags.writeable


def test_false_patch_witness_cannot_be_accepted_as_resolved(monkeypatch):
    function = physical.decompose_face

    def false_witness(triangle, *args, **kwargs):
        result = function(triangle, *args, **kwargs)
        if result['status'] == 'resolved' and result['regions']:
            result['regions'][0]['witness'] = triangle[0].tolist()
        return result

    monkeypatch.setattr(physical, 'decompose_face', false_witness)
    record = network().get_topography(query=DFNDQuery(probe_radius=0.12))['raw'][
        'boundary_connectivity'
    ]
    assert record['status'] == 'unresolved' and record['n_patches'] is None
    assert 'witness' in record['reason']


def test_path_budget_preserves_global_count_and_partial_availability():
    result = network().get_topography(
        query=DFNDQuery(probe_radius=0.12, boundary_max_path_tests=1)
    )
    record = result['raw']['boundary_connectivity']
    assert record['status'] == 'resolved' and record['n_patches'] == 4
    assert record['work']['path_tests'] == 1
    assert record['component_associations']['status'] == 'unresolved'
    view = (
        DFNDData(network(), result).dfn.components.wet[0].boundary['physical_openings']
    )
    assert view['status'] == 'unresolved' and view['n_patches'] is None


def test_patch_occurrences_do_not_depend_on_hull_face_enumeration(monkeypatch):
    native = network()
    query = DFNDQuery(probe_radius=0.12)
    reference = native.get_topography(query=query)['raw']['boundary_connectivity']
    faces = native.mesh.get_boundary_face_records()
    monkeypatch.setattr(
        type(native.mesh),
        'get_boundary_face_records',
        lambda self: list(reversed(faces)),
    )
    changed = native.get_topography(query=query)['raw']['boundary_connectivity']

    def supports(record):
        return {
            tuple(
                sorted(patch['support']['carrier_faces_source_atom_indices'][0])
            ): patch['patch_id']
            for patch in record['patches']
        }

    assert supports(changed) == supports(reference)
