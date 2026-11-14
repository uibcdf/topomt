"""Power-cell receiving preserves proofs, anchors, provenance and old evidence."""

import json
import os

import pytest

from devtools.reference_validator.model import Box, Model, encode_point, point
from devtools.reference_validator.storage import read_record
from devtools.reference_validator.verify import verify


def _protocol(tmp_path):
    model = Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0)],
        [4, 4],
        1,
        domain=Box(point((-20, -3, -4)), point((20, 3, 4))),
    )
    spec = {
        'schema': 'topomt.reference-validator.power-cell-pilot/1',
        'length_unit': 'nm',
        'contact_policy': 'strict',
        'cases': [
            {
                'name': 'two_barriers',
                'model': model.to_record(),
                'expected_components': 3,
                'expected_boundary_patches': 3,
                'anchors': {
                    'left': encode_point(point((-15, 0, 0))),
                    'middle': encode_point(point((0, 0, 0))),
                    'also_left': encode_point(point((-14, 1, 0))),
                },
                'pairs': [['left', 'middle'], ['left', 'also_left']],
            }
        ],
    }
    path = tmp_path / 'protocol.json'
    path.write_text(json.dumps(spec))
    return path


def test_capture_saves_checks_and_binds_anchor_connection_and_separation(
    tmp_path, monkeypatch
):
    from devtools.reference_validator.capture_power_cells import capture

    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0})
    protocol = _protocol(tmp_path)
    output = tmp_path / 'receiving'
    capture(protocol, output)
    receipt = read_record(output / 'receipt.json')
    row = receipt['cases']['two_barriers']
    assert row['n_components'] == row['n_boundary_patches'] == 3
    assert row['per_region_volume_status'] == 'not_computed'
    folder = output / 'two_barriers'
    model = Model.from_record(read_record(folder / 'model.json'))
    assert verify(model, read_record(folder / 'certificate.json'))['topology_complete']
    queries = read_record(folder / 'anchors.json')
    assert queries['pairs'][0]['connected'] is False
    assert queries['pairs'][1]['connected'] is True
    assert verify(model, queries['pairs'][1]['path_certificate'])['path_validated']
    with pytest.raises(FileExistsError):
        capture(protocol, output)


def test_capture_does_not_replace_failed_expectation_with_a_physical_answer(
    tmp_path, monkeypatch
):
    from devtools.reference_validator.capture_power_cells import capture

    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0})
    protocol = _protocol(tmp_path)
    spec = read_record(protocol)
    spec['cases'][0]['expected_components'] = 1
    protocol.write_text(json.dumps(spec))
    output = tmp_path / 'receiving'
    with pytest.raises(ValueError, match='expectation'):
        capture(protocol, output)
    assert not (output / 'receipt.json').exists()


def test_capture_rejects_unbounded_parallel_envelope_before_creating_output(
    tmp_path, monkeypatch
):
    from devtools.reference_validator.capture_power_cells import capture

    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0, 1})
    with pytest.raises(ValueError, match='one CPU'):
        capture(_protocol(tmp_path), tmp_path / 'receiving')
    assert not (tmp_path / 'receiving').exists()
