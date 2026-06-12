"""Tests for DFND record selectors."""

import types

from topomt.dfnd.selectors import (
    select_component_atom_indices,
    select_component_ids,
    select_component_tetrahedron_ids,
    select_components,
    select_face_atom_indices,
    select_face_ids,
    select_faces,
    select_tetrahedron_atom_indices,
    select_tetrahedron_ids,
    select_tetrahedron_indices,
)


def _raw_records():
    return {
        'tetrahedra': [
            {
                'tetrahedron_id': 10,
                'local_atom_indices': [0, 1, 2, 3],
                'residence_state': 'resident',
                'transit_role': 'core',
            },
            {
                'tetrahedron_id': 20,
                'local_atom_indices': [4, 5, 6, 7],
                'residence_state': 'non_resident',
                'transit_role': 'dry',
            },
            {
                'tetrahedron_id': 30,
                'local_atom_indices': [8, 9, 10, 11],
                'residence_state': 'non_resident',
                'transit_role': 'dry',
            },
        ],
        'faces': [
            {
                'face_id': 100,
                'owner_tetrahedron_id': 20,
                'neighbor_tetrahedron_id': 30,
                'face_atoms_local': [4, 5, 6],
                'permeability_state': 'permeable',
            },
            {
                'face_id': 100,
                'owner_tetrahedron_id': 30,
                'neighbor_tetrahedron_id': 20,
                'face_atoms_local': [4, 5, 6],
                'permeability_state': 'permeable',
            },
            {
                'face_id': 101,
                'owner_tetrahedron_id': 20,
                'neighbor_tetrahedron_id': 10,
                'face_atoms_local': [4, 5, 7],
                'permeability_state': 'non_permeable',
            },
            {
                'face_id': 102,
                'owner_tetrahedron_id': 10,
                'neighbor_tetrahedron_id': 20,
                'face_atoms_local': [0, 1, 2],
                'permeability_state': 'permeable',
            },
        ],
    }


def _dfnd_result():
    return {
        'raw': {
            **_raw_records(),
            'wet_components': [
                {
                    'id': 1,
                    'family': 'pocket',
                    'tetrahedron_ids': [10],
                    'atom_indices': [0, 1, 2, 3],
                    'flags': [],
                },
            ],
        },
        'dry': {
            'components': [
                {
                    'id': 1,
                    'tetrahedron_indices': [20],
                    'atom_indices': [4, 5, 6, 7],
                    'flags': ['exposed'],
                },
                {
                    'id': 2,
                    'tetrahedron_indices': [30],
                    'atom_indices': [8, 9, 10, 11],
                    'flags': [],
                },
            ],
        },
    }


def test_select_tetrahedra_by_state_returns_indices_ids_and_atoms():
    topography = types.SimpleNamespace(dfnd=types.SimpleNamespace(raw=_raw_records()))

    assert select_tetrahedron_indices(topography, residence_state='non_resident') == [
        1,
        2,
    ]
    assert select_tetrahedron_ids(topography, residence_state='non_resident') == [
        20,
        30,
    ]
    assert select_tetrahedron_atom_indices(
        topography,
        residence_state='non_resident',
    ) == [[4, 5, 6, 7], [8, 9, 10, 11]]
    assert select_tetrahedron_atom_indices(
        topography,
        residence_state='non_resident',
        tetrahedron_ids=[30],
    ) == [[8, 9, 10, 11]]


def test_select_faces_filters_by_owner_permeability_and_deduplicates_face_ids():
    wrapped_raw = {'raw': _raw_records()}
    dry_ids = select_tetrahedron_ids(wrapped_raw, residence_state='non_resident')

    faces = select_faces(
        wrapped_raw,
        owner_tetrahedron_ids=dry_ids,
        permeability_state='permeable',
    )

    assert [face['face_id'] for face in faces] == [100]
    assert select_face_ids(
        wrapped_raw,
        owner_tetrahedron_ids=dry_ids,
        permeability_state={'permeable', 'non_permeable'},
    ) == [100, 101]
    assert select_face_atom_indices(
        wrapped_raw,
        owner_tetrahedron_ids=dry_ids,
        permeability_state='permeable',
    ) == [[4, 5, 6]]


def test_select_components_returns_component_ids_tetrahedra_and_atoms():
    result = _dfnd_result()

    dry_components = select_components(result, side='dry')

    assert select_component_ids(result, side='dry') == ['DRY-1', 'DRY-2']
    assert [component['id'] for component in dry_components] == [1, 2]
    assert select_component_tetrahedron_ids(
        result,
        side='dry',
        component_ids='DRY-2',
    ) == [30]
    assert select_component_atom_indices(
        result,
        side='dry',
        component_ids=[1],
    ) == [4, 5, 6, 7]
    assert select_component_ids(
        result,
        side='wet',
        family='pocket',
    ) == ['WET-1']


def test_select_face_ids_fallback_preserves_original_raw_position_after_filtering():
    raw = _raw_records()
    raw['faces'][2].pop('face_id')

    assert select_face_ids(
        {'raw': raw},
        permeability_state='non_permeable',
    ) == [2]


def test_select_components_accepts_contextual_and_support_keys():
    result = _dfnd_result()
    wet = result['raw']['wet_components'][0]
    wet['component_key'] = 'component-wet-1'
    wet['support_key'] = 'support-wet-1'

    assert select_components(result, component_keys='component-wet-1') == [wet]
    assert select_components(result, support_keys='support-wet-1') == [wet]
