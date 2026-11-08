"""Protect the original-reader radius audit and its isolated name perturbation."""

import csv
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from pyunitwizard import QuantityRecord

from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun

CASE = (
    Path(__file__).resolve().parents[1]
    / 'docs/content/benchlab/synthetic/regular_tetrahedron'
)
AUDIT = CASE / 'artifacts/radius_audit_v1'


def decode(record, field, unit):
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return np.asarray(puw.get_value(quantity, to_unit=unit))


def test_radius_protocol_preserves_prior_evidence_and_only_changes_atom_name():
    protocol = json.loads((AUDIT / 'protocol.json').read_text())
    for relative, expected in protocol['preserved_files'].items():
        assert hashlib.sha256((CASE / relative).read_bytes()).hexdigest() == expected
    source = (CASE / protocol['source_file']).read_bytes().splitlines()
    aligned = (AUDIT / protocol['aligned_file']).read_bytes().splitlines()
    assert len(source) == len(aligned) == 5
    for original, variant in zip(source[:4], aligned[:4], strict=True):
        assert original[12:16] == b'C   ' and variant[12:16] == b' C  '
        assert original[:12] == variant[:12] and original[16:] == variant[16:]
    assert source[-1] == aligned[-1]
    assert protocol['workers'] == protocol['os_cpu_affinity_count'] == 1
    assert len(protocol['runs']) == 4


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_original_reader_assignments_reconstruct_without_engines(policy):
    report = json.loads((AUDIT / 'report.json').read_text())
    assert len(report['observations']) == 4
    expected = {
        'ghecom-original': 1.87,
        'ghecom-aligned': 1.87,
        'caver-original': 1.7,
        'caver-aligned': 1.7,
    }
    with puw.context(standard_units=[*policy, 'radians']):
        for entry in report['observations']:
            radius = decode(entry['radii'], 'atomic_radii', 'angstroms')
            assert radius.shape == (4,)
            np.testing.assert_allclose(
                radius, expected[entry['id']], rtol=0, atol=1e-12
            )
            path = AUDIT / entry['bundle']['file']
            assert (
                hashlib.sha256(path.read_bytes()).hexdigest()
                == entry['bundle']['sha256']
            )
            run = ProviderRun.load(path)
            assert run.run_id == entry['bundle']['run_id']
            assert run.metadata['operation'] == 'input_radius_audit'
            assert 'record_count' not in run.metadata
            if entry['method'] == 'ghecom':
                raw = run.get_artifact('output/assigned.pdb').decode()
                assert 'Occupancy [55-60] : Radius of the atom' in raw
                rows = [line for line in raw.splitlines() if line.startswith('ATOM  ')]
                assert len(rows) == 4
                np.testing.assert_allclose(
                    [float(line[54:60]) for line in rows], radius
                )
            else:
                text = run.get_artifact('output/stdout.txt').decode()
                start = text.index('serial\tname\telement\tradius_angstrom')
                rows = list(csv.DictReader(io.StringIO(text[start:]), delimiter='\t'))
                assert len(rows) == 4
                assert {row['element'] for row in rows} == {'C'}
                np.testing.assert_allclose(
                    [float(row['radius_angstrom']) for row in rows], radius
                )
            raw_input = run.get_artifact('input/input.pdb')
            assert hashlib.sha256(raw_input).hexdigest() == entry['input_sha256']
            xyz = decode(entry['coordinates'], 'coordinates', 'angstroms')
            reference = np.array(
                [
                    [1.874, 1.874, 1.874],
                    [1.874, -1.874, -1.874],
                    [-1.874, 1.874, -1.874],
                    [-1.874, -1.874, 1.874],
                ]
            )
            np.testing.assert_allclose(xyz, reference, rtol=0, atol=1e-12)


def test_radius_report_retains_definition_limits_and_independent_implications():
    report = json.loads((AUDIT / 'report.json').read_text())
    assert (
        report['scope']
        == 'Original input-radius assignment; no new pocket/channel interpretation'
    )
    assert (
        report['protocol_sha256']
        == hashlib.sha256((AUDIT / 'protocol.json').read_bytes()).hexdigest()
    )
    for entry in report['observations']:
        radius = decode(entry['radii'], 'atomic_radii', 'angstroms')[0]
        edge = np.linalg.norm([3.748, 3.748, 0])
        face = float(
            decode(
                entry['ball_model_implication']['face_clearance'],
                'face_clearance',
                'angstroms',
            )
        )
        assert face == pytest.approx(edge / np.sqrt(3) - radius, abs=1e-12)
        assert (
            entry['ball_model_implication']['meaning']
            == 'Independent equal-ball geometry, not an original detector prediction'
        )


def test_ghecom_audit_reads_provider_points_without_general_metadata_parsing(tmp_path):
    from devtools.benchlab.audit_tetrahedron_radii import _read_original

    # Analytical format control only; original detector evidence stays separate.
    text = 'REMARK  COMMENT NATOM_OF_RECEPTOR:4\nREMARK    Occupancy [55-60] : Radius of the atom\n'
    for line in (
        (CASE / 'artifacts/regular_tetrahedron_v1/input_atom.pdb')
        .read_text()
        .splitlines()
    ):
        if line.startswith('ATOM  '):
            text += line[:54] + '  1.87' + line[60:] + '\n'
    (tmp_path / 'assigned.pdb').write_text(text + 'END\n')
    radii, xyz = _read_original('ghecom', tmp_path)
    np.testing.assert_allclose(radii, [1.87] * 4)
    np.testing.assert_allclose(xyz[0], [1.874] * 3)


def test_effective_radius_changes_the_independent_probe_regimes():
    report = json.loads((AUDIT / 'report.json').read_text())
    by_id = {entry['id']: entry for entry in report['observations']}
    ghecom = by_id['ghecom-original']['ball_model_implication']
    caver = by_id['caver-original']['ball_model_implication']

    def face(entry):
        return float(decode(entry['face_clearance'], 'face_clearance', 'angstroms'))

    def residence(entry):
        return float(
            decode(entry['residence_clearance'], 'residence_clearance', 'angstroms')
        )

    assert face(ghecom) < 1.2 < residence(ghecom) < 1.4
    assert 1.2 < face(caver) < 1.4 < residence(caver) < 1.7


def test_radius_audit_receipt_covers_exact_originals_and_executed_driver():
    receipt = json.loads((AUDIT / 'receipt.json').read_text())
    for relative, expected in receipt['files'].items():
        assert hashlib.sha256((AUDIT / relative).read_bytes()).hexdigest() == expected
    driver = (
        Path(__file__).resolve().parents[1]
        / 'devtools/benchlab/audit_tetrahedron_radii.py'
    )
    assert (
        hashlib.sha256(driver.read_bytes()).hexdigest()
        == receipt['audit_driver_sha256']
    )
    assert len(receipt['files']) >= 30
    elapsed = float(
        decode(receipt['complete_run_wall_time'], 'elapsed_time', 'seconds')
    )
    assert 0 < elapsed < 60


def test_radius_audit_location_file_cannot_override_scientific_settings(
    tmp_path, monkeypatch
):
    from devtools.benchlab import audit_tetrahedron_radii as runner

    locations = tmp_path / 'tools.json'
    locations.write_text(json.dumps({'ghecom_cmd': '/not/executed', 'radius': 1.7}))
    output = tmp_path / 'new-audit'
    monkeypatch.setattr(
        sys, 'argv', ['audit', '--tools', str(locations), '--output', str(output)]
    )
    with pytest.raises(ValueError, match='location keys'):
        runner.main()
    assert not output.exists()
