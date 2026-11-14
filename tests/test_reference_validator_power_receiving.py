"""Retained exact multi-ball receiving is source-bound and independently replayed."""

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from devtools.reference_validator.model import Model
from devtools.reference_validator.storage import read_record
from devtools.reference_validator.verify import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_power_cells_v1'


def test_retained_twenty_profiles_preserve_every_model_proof_and_receipt_byte():
    protocol = read_record(BASE / 'protocol.json')
    receipt = read_record(BASE / 'receiving/receipt.json')
    assert len(protocol['cases']) == len(receipt['cases']) == 20
    assert receipt['source_revision'] == 'bb308baddc52098f73f1fe9e8b5a185dc7aa7c21'
    assert receipt['source_tree_modified'] is False
    assert (
        receipt['protocol_sha256']
        == hashlib.sha256((BASE / 'protocol.json').read_bytes()).hexdigest()
    )
    assert len(receipt['files']) == 80
    for name, digest in receipt['files'].items():
        assert (
            hashlib.sha256((BASE / 'receiving' / name).read_bytes()).hexdigest()
            == digest
        )
    for row in protocol['cases']:
        folder = BASE / 'receiving' / row['name']
        model = Model.from_record(read_record(folder / 'model.json'))
        assert model.to_record() == row['model']
        checked = verify(model, read_record(folder / 'certificate.json'))
        old = read_record(folder / 'verification.json')
        assert checked['topology_complete'] is True
        for key in [
            'n_components',
            'n_boundary_patches',
            'regions',
            'boundary_patches',
            'nodes',
            'edges',
        ]:
            assert checked[key] == old[key]
        assert checked['per_region_volume_status'] == 'not_computed'
        assert checked['precision_status'] == 'not_requested'


def test_original_tetrahedron_is_the_same_saved_model_and_has_complete_one_one_zero_regions():
    protocol = read_record(BASE / 'protocol.json')
    outcomes = []
    for row in protocol['cases']:
        if not row['name'].startswith('original_tetra_'):
            continue
        origin = row['reference_origin']
        archive_path = ROOT / origin['archive']
        assert (
            hashlib.sha256(archive_path.read_bytes()).hexdigest()
            == origin['archive_sha256']
        )
        with zipfile.ZipFile(archive_path) as archive:
            raw = archive.read(origin['member'])
        assert hashlib.sha256(raw).hexdigest() == origin['member_sha256']
        assert json.loads(raw) == row['model']
        checked = read_record(BASE / 'receiving' / row['name'] / 'verification.json')
        outcomes.append((checked['n_components'], checked['n_boundary_patches']))
    assert outcomes == [(1, 4), (1, 0), (0, 0)]


def test_retained_execution_is_bounded_and_does_not_claim_requested_region_volume_precision():
    receipt = read_record(BASE / 'receiving/receipt.json')
    execution = read_record(BASE / 'execution.json')
    assert len(receipt['cpu_affinity']) == 1
    assert receipt['address_space_limit_bytes'] == 2 * 1024**3
    assert receipt['cpu_limit_seconds'] == execution['cpu_limit_seconds'] == 50
    assert execution['wall_limit_seconds'] == 60
    assert execution['exit_code'] == 0
    assert receipt['requested_precision_status'] == 'not_computed'
    assert receipt['native_dfnd_qualification'] == 'not_changed'
    assert (
        execution['receipt_sha256']
        == hashlib.sha256((BASE / 'receiving/receipt.json').read_bytes()).hexdigest()
    )


def test_original_saved_topology_is_replayable_without_producer_or_scientific_libraries():
    folder = BASE / 'receiving/original_tetra_1_2'
    script = """
import sys,json
from pathlib import Path
for name in ['topomt','numpy','scipy','pyunitwizard','devtools.reference_validator.producer','devtools.reference_validator.power_cells','devtools.reference_validator.center_hull']:
 sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
model=Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
print(json.dumps(verify(model,json.loads(Path(sys.argv[2]).read_text()))))
"""
    result = subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(folder / 'model.json'),
            str(folder / 'certificate.json'),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    checked = json.loads(result.stdout)
    assert (checked['n_components'], checked['n_boundary_patches']) == (1, 4)


def test_historical_narrow_attempt_preserves_unknown_instead_of_inventing_empty_topology():
    base = BASE / 'narrow_pilot'
    outcome = read_record(base / 'disposition.json')
    execution = read_record(base / 'execution.json')
    assert outcome['verification_status'] == 'unresolved_execution_stop'
    assert outcome['topology_complete'] is False
    assert outcome['n_components'] is outcome['n_boundary_patches'] is None
    assert outcome['completed_certificate'] is False
    assert execution['exit_code'] == outcome['observed_exit_code'] == -9
    for name in ['protocol', 'execution']:
        assert (
            outcome[f'{name}_sha256']
            == hashlib.sha256((base / f'{name}.json').read_bytes()).hexdigest()
        )
    assert not (base / 'receiving/receipt.json').exists()
    assert execution['cpu_limit_seconds'] == 50
    assert len(execution['cpu_affinity']) == 1
