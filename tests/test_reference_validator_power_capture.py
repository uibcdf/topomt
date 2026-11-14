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


def test_capture_keeps_the_received_model_when_construction_stops(
    tmp_path, monkeypatch
):
    import devtools.reference_validator.capture_power_cells as module

    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0})

    def stop(_):
        raise ValueError('Deliberate construction stop')

    monkeypatch.setattr(module, 'topology_certificate', stop)
    protocol = _protocol(tmp_path)
    output = tmp_path / 'receiving'
    with pytest.raises(ValueError, match='Deliberate construction stop'):
        module.capture(protocol, output)
    assert (
        read_record(output / 'two_barriers/model.json')
        == read_record(protocol)['cases'][0]['model']
    )
    assert not (output / 'receipt.json').exists()


def test_capture_reports_separate_construction_saved_check_and_query_costs(
    tmp_path, monkeypatch
):
    from devtools.reference_validator.capture_power_cells import capture

    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0})
    output = tmp_path / 'receiving'
    capture(_protocol(tmp_path), output)
    phases = read_record(output / 'two_barriers/phases.json')
    assert list(phases) == [
        'model_receiving',
        'construction',
        'saved_reading',
        'verification',
        'anchor_queries',
    ]
    assert all(
        p['wall_seconds'] >= 0 and p['cpu_seconds'] >= 0 for p in phases.values()
    )


def test_capture_can_recheck_a_saved_certificate_without_claiming_a_new_construction(
    tmp_path, monkeypatch
):
    import hashlib

    import devtools.reference_validator.capture_power_cells as module
    from devtools.reference_validator.power_cells import topology_certificate

    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0})
    protocol = _protocol(tmp_path)
    spec = read_record(protocol)
    cert = tmp_path / 'proof.json'
    cert.write_text(
        json.dumps(topology_certificate(Model.from_record(spec['cases'][0]['model'])))
    )
    spec['cases'][0]['saved_certificate'] = {
        'path': str(cert),
        'sha256': hashlib.sha256(cert.read_bytes()).hexdigest(),
        'producer_revision': 'a' * 40,
    }
    protocol.write_text(json.dumps(spec))

    def no_new_construction(_):
        raise AssertionError('Saved reading must not run the constructor')

    monkeypatch.setattr(module, 'topology_certificate', no_new_construction)
    output = tmp_path / 'receiving'
    module.capture(protocol, output)
    receipt = read_record(output / 'receipt.json')
    assert (
        receipt['cases']['two_barriers']['certificate_origin']['route']
        == 'saved_certificate'
    )
    assert (
        receipt['cases']['two_barriers']['certificate_origin']['producer_revision']
        == 'a' * 40
    )
    assert 'construction' not in read_record(output / 'two_barriers/phases.json')
    spec['cases'][0]['saved_certificate']['sha256'] = '0' * 64
    protocol.write_text(json.dumps(spec))
    with pytest.raises(ValueError, match='digest'):
        module.capture(protocol, tmp_path / 'rejected')


def test_capture_reuses_only_checked_geometry_for_a_changed_probe(
    tmp_path, monkeypatch
):
    import hashlib
    from dataclasses import replace
    from fractions import Fraction

    import devtools.reference_validator.capture_power_cells as module
    from devtools.reference_validator.power_cells import topology_certificate

    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0})
    protocol = _protocol(tmp_path)
    spec = read_record(protocol)
    source = Model.from_record(spec['cases'][0]['model'])
    source_path = tmp_path / 'source.json'
    source_path.write_text(json.dumps(source.to_record()))
    cert_path = tmp_path / 'proof.json'
    cert_path.write_text(json.dumps(topology_certificate(source)))
    row = spec['cases'][0]
    row['model'] = replace(source, probe=Fraction(1) - Fraction(1, 2**80)).to_record()
    row['expected_components'] = row['expected_boundary_patches'] = 1
    row['saved_geometry'] = {
        'model_path': str(source_path),
        'model_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'certificate_path': str(cert_path),
        'certificate_sha256': hashlib.sha256(cert_path.read_bytes()).hexdigest(),
        'producer_revision': 'a' * 40,
    }
    protocol.write_text(json.dumps(spec))

    def no_fresh_construction(_):
        raise AssertionError('Reuse must not rerun the cell constructor')

    monkeypatch.setattr(module, 'topology_certificate', no_fresh_construction)
    output = tmp_path / 'receiving'
    module.capture(protocol, output)
    checked = read_record(output / 'two_barriers/verification.json')
    assert checked['n_components'] == checked['n_boundary_patches'] == 1
    origin = read_record(output / 'receipt.json')['cases']['two_barriers'][
        'certificate_origin'
    ]
    assert origin['route'] == 'reprobed_geometry'
    assert origin['geometry_producer_revision'] == 'a' * 40
    assert 'certified_geometry_reprobe' in read_record(
        output / 'two_barriers/phases.json'
    )
    row['saved_geometry']['certificate_sha256'] = '0' * 64
    protocol.write_text(json.dumps(spec))
    with pytest.raises(ValueError, match='digest'):
        module.capture(protocol, tmp_path / 'rejected')


def test_capture_rejects_competing_saved_routes(tmp_path, monkeypatch):
    from devtools.reference_validator.capture_power_cells import capture

    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: {0})
    protocol = _protocol(tmp_path)
    spec = read_record(protocol)
    spec['cases'][0].update(saved_certificate={}, saved_geometry={})
    protocol.write_text(json.dumps(spec))
    with pytest.raises(ValueError, match='exclusive'):
        capture(protocol, tmp_path / 'receiving')
