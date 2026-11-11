"""Independent dumbbell barriers certify sets, not native graph labels."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest
import pyunitwizard as puw

from devtools.verify_dumbbell_reference import (
    ReferenceIncomplete,
    build_simplex_cover,
    verify_simplex_cover,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'docs/content/benchlab/synthetic/dumbbell/artifacts/dumbbell_v1'


def toy_model():
    vertices = np.array(
        [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]]
    )
    return vertices, np.array([[0, 1, 2, 3]]), vertices.copy(), np.full(4, 0.3)


def test_external_simplex_cover_has_complete_bounded_all_atom_evidence():
    vertices, cells, centers, radii = toy_model()
    certificate = build_simplex_cover(
        vertices,
        cells,
        centers,
        radii,
        1.3,
        length_unit='angstroms',
        maximum_depth=12,
        maximum_nodes=10000,
    )
    result = verify_simplex_cover(
        vertices,
        cells,
        centers,
        radii,
        1.3,
        certificate,
        length_unit='angstroms',
        maximum_depth=12,
        maximum_nodes=10000,
    )
    assert result['visited_nodes'] > 1 and result['leaf_count'] > 1
    assert puw.get_value(result['minimum_coverage_margin'], to_unit='angstroms') > 1e-6


@pytest.mark.parametrize(
    'damage', ['missing_child', 'wrong_atom', 'changed_vertex', 'missing_root']
)
def test_simplex_cover_rejects_incomplete_or_false_witnesses(damage):
    vertices, cells, centers, radii = toy_model()
    certificate = build_simplex_cover(
        vertices,
        cells,
        centers,
        radii,
        1.3,
        length_unit='angstroms',
        maximum_depth=12,
        maximum_nodes=10000,
    )
    certificate = copy.deepcopy(certificate)
    if damage == 'missing_child':
        certificate['roots'][0]['children'].pop()
    elif damage == 'wrong_atom':
        node = certificate['roots'][0]
        while 'children' in node:
            node = node['children'][0]
        node['covering_atom_index'] = 999
    elif damage == 'changed_vertex':
        vertices[0] += 10
    else:
        certificate['roots'].pop()
    with pytest.raises(ValueError):
        verify_simplex_cover(
            vertices,
            cells,
            centers,
            radii,
            1.3,
            certificate,
            length_unit='angstroms',
            maximum_depth=12,
            maximum_nodes=10000,
        )


def test_cover_respects_explicit_units_and_rigid_motion():
    vertices, cells, centers, radii = toy_model()
    certificate = build_simplex_cover(
        vertices,
        cells,
        centers,
        radii,
        1.3,
        length_unit='angstroms',
        maximum_depth=12,
        maximum_nodes=10000,
    )
    rotation = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    shift = np.array([5.0, -7.0, 3.0])
    result = verify_simplex_cover(
        (vertices @ rotation + shift) / 10,
        cells,
        (centers @ rotation + shift) / 10,
        radii / 10,
        0.13,
        certificate,
        length_unit='nm',
        maximum_depth=12,
        maximum_nodes=10000,
    )
    assert puw.get_value(result['minimum_coverage_margin'], to_unit='angstroms') > 1e-6


def test_cover_refuses_unproved_geometry_and_work_overrun():
    vertices, cells, centers, radii = toy_model()
    with pytest.raises(ReferenceIncomplete, match='budget'):
        build_simplex_cover(
            vertices,
            cells,
            centers,
            radii,
            1.3,
            length_unit='angstroms',
            maximum_depth=12,
            maximum_nodes=1,
        )
    with pytest.raises(ReferenceIncomplete):
        build_simplex_cover(
            vertices,
            cells,
            centers[:1],
            radii[:1],
            0.01,
            length_unit='angstroms',
            maximum_depth=12,
            maximum_nodes=10000,
        )


def test_accepted_reference_replays_without_native_dfnd():
    from devtools.verify_dumbbell_reference import verify_reference

    result = verify_reference(
        ARTIFACTS / 'input.json',
        ARTIFACTS / 'protocol.json',
        json.loads((ARTIFACTS / 'reference_certificate.json').read_text()),
    )
    assert result['anchor_connection_1.4A'] == 'certified'
    assert result['anchor_enclosure_1.4A'] == 'certified'
    assert result['anchor_separation_2.2A'] == 'certified'
    assert result['finite_hull_exclusion_6A'] == 'certified'
    assert result['exact_global_free_component_count'] == 'not_established'


def test_reference_replay_respects_nondefault_application_units():
    from devtools.verify_dumbbell_reference import verify_reference

    with puw.context(standard_units=['pm', 'fs', 'radians']):
        observed = verify_reference(
            ARTIFACTS / 'input.json',
            ARTIFACTS / 'protocol.json',
            json.loads((ARTIFACTS / 'reference_certificate.json').read_text()),
        )
        clearance = puw.get_value(
            observed['connecting_axis_minimum_clearance'], to_unit='angstroms'
        )
        assert 1.43 < clearance < 1.44
        assert observed['anchor_separation_2.2A'] == 'certified'
