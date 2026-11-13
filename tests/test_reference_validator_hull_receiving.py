"""Retained original hulls bind source geometry without claiming free regions."""

import hashlib
import json
from pathlib import Path

import pytest

from devtools.reference_validator.hull_model import CenterSource
from devtools.reference_validator.model import decode_scalar, record_digest
from devtools.reference_validator.verify.center_hull import verify_hull

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_hulls_v1'
SAVED = BASE / 'local_receiving'


def _read(path):
    return json.loads(path.read_text())


def test_original_hull_receiving_is_complete_source_bound_and_locally_limited():
    protocol = _read(BASE / 'protocol.json')
    receipt = _read(SAVED / 'receipt.json')
    execution = _read(BASE / 'local_execution.json')
    selected = [row['name'] for row in protocol['original_inputs']]
    assert receipt['original_selection'] == selected
    assert set(receipt['originals']) == set(selected)
    assert receipt['source_revision'] == '9a276cd9827f4d84fc048d94e06ee6d043779106'
    assert (
        receipt['protocol_sha256']
        == hashlib.sha256((BASE / 'protocol.json').read_bytes()).hexdigest()
    )
    expected = {
        f'{category}/{name}/{kind}.json'
        for category in ['fixtures', 'clips', 'originals']
        for name in receipt[category]
        for kind in ['source', 'certificate', 'verification']
    } | {f'originals/{name}/result.json' for name in selected}
    assert set(receipt['files']) == expected
    assert {
        str(path.relative_to(SAVED)) for path in SAVED.rglob('*.json')
    } == expected | {'receipt.json'}
    for name, digest in receipt['files'].items():
        assert hashlib.sha256((SAVED / name).read_bytes()).hexdigest() == digest
    assert receipt['concurrency'] == 1
    assert len(receipt['cpu_affinity']) == 1
    assert receipt['address_space_limit_bytes'] == 2 * 1024**3
    assert receipt['slurm_allocation'] is None
    assert receipt['free_volume_status'] == 'not_computed'
    assert receipt['free_topology_status'] == 'not_computed'
    assert (
        execution['receipt_sha256']
        == hashlib.sha256((SAVED / 'receipt.json').read_bytes()).hexdigest()
    )
    assert execution['source_revision'] == receipt['source_revision']
    assert execution['protocol_sha256'] == receipt['protocol_sha256']
    assert execution['scheduler_used'] is False
    assert execution['external_limits']['per_case'] == protocol['per_case_resources']


@pytest.mark.parametrize(
    'name',
    [
        'regular_tetrahedron',
        'closed_shell',
        'shell_with_opening',
        'straight_tube_narrow_dense',
        'straight_tube_wide_sparse',
        'dumbbell',
    ],
)
def test_each_original_hull_retains_all_centers_and_separate_geometric_scope(name):
    protocol = _read(BASE / 'protocol.json')
    row = next(row for row in protocol['original_inputs'] if row['name'] == name)
    directory = SAVED / 'originals' / name
    source = CenterSource.from_record(_read(directory / 'source.json'))
    cert = _read(directory / 'certificate.json')
    checked = _read(directory / 'verification.json')
    result = _read(directory / 'result.json')
    assert result == _read(SAVED / 'receipt.json')['originals'][name]
    assert result['status'] == checked['verification_status'] == 'accepted'
    assert source.source_sha256 == row['input_sha256']
    assert (
        hashlib.sha256((ROOT / row['input']).read_bytes()).hexdigest()
        == (row['input_sha256'])
    )
    assert source.source_ids == tuple(range(row['n_atoms']))
    assert source.frame_index == 0
    assert source.interpretation == 'received_binary64_nm'
    assert result['n_centers'] == len(source.centers) == row['n_atoms']
    assert result['source_sha256'] == cert['source_sha256'] == source.digest
    assert result['certificate_sha256'] == record_digest(cert)
    assert result['verification_sha256'] == record_digest(checked)
    assert checked['hull_equality_status'] == 'resolved'
    assert checked['geometric_dimension'] == 3
    assert result['n_vertices'] == len(checked['vertices'])
    assert result['n_facets'] == len(checked['facets'])
    assert result['geometric_volume'] == checked['geometric_volume']
    assert decode_scalar(checked['geometric_volume']) > 0
    assert checked['volume_unit'] == result['volume_unit'] == 'nm**3'
    assert checked['length_unit'] == 'nm'
    assert checked['free_volume_status'] == 'not_computed'
    assert checked['free_topology_status'] == 'not_computed'
    assert result['slurm_allocation'] is None
    assert len(result['cpu_affinity']) == 1
    assert result['address_space_limit_bytes'] == 2 * 1024**3
    assert result['cpu_limit_seconds'] == 30
    assert result['elapsed_seconds'] < 40
    assert set(result['quantity_receiving']['dependency_versions']) == {
        'numpy',
        'pyunitwizard',
    }


@pytest.mark.parametrize('name', ['regular_tetrahedron', 'straight_tube_narrow_dense'])
def test_saved_original_hull_replay_matches_retained_geometric_receipt(name):
    # The original capture checked all six after saving. Keep this routine guard
    # small; replaying the two shells and dumbbell costs most of that full batch.
    directory = SAVED / 'originals' / name
    source = CenterSource.from_record(_read(directory / 'source.json'))
    checked = verify_hull(source, _read(directory / 'certificate.json'))
    original = _read(directory / 'verification.json')
    for key in [
        'vertices',
        'facets',
        'geometric_dimension',
        'geometric_volume',
        'hull_equality_status',
        'free_volume_status',
        'free_topology_status',
    ]:
        assert checked[key] == original[key]
