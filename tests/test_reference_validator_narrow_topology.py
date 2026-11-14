"""Original narrow-tube topology receiving keeps geometry and exact proof scope."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from devtools.reference_validator.model import Model
from devtools.reference_validator.storage import read_record
from devtools.reference_validator.verify import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_power_cells_v3'
FOLDER = BASE / 'receiving/original_narrow_tube_1_4'


def test_repeat_preserves_the_complete_physical_model_and_frozen_earlier_attempt():
    spec = read_record(BASE / 'protocol.json')
    previous = ROOT / spec['previous_protocol']['path']
    assert (
        hashlib.sha256(previous.read_bytes()).hexdigest()
        == spec['previous_protocol']['sha256']
    )
    old = read_record(previous)
    for key, value in old['cases'][0].items():
        assert spec['cases'][0][key] == value
    assert spec['cases'][0]['model'] == read_record(FOLDER / 'model.json')
    model = Model.from_record(read_record(FOLDER / 'model.json'))
    assert len(model.atoms) == 81
    assert len(read_record(FOLDER / 'certificate.json')['cells']) == 81


def test_completed_receiving_binds_all_saved_files_without_changing_native_or_precision_claims():
    receipt = read_record(BASE / 'receiving/receipt.json')
    execution = read_record(BASE / 'execution.json')
    assert receipt['source_tree_modified'] is False
    assert receipt['source_revision'] == execution['source_revision']
    assert (
        hashlib.sha256((BASE / 'execution.log').read_bytes()).hexdigest()
        == execution['log_sha256']
    )
    assert (
        receipt['protocol_sha256']
        == hashlib.sha256((BASE / 'protocol.json').read_bytes()).hexdigest()
    )
    assert len(receipt['files']) == 5
    origin = receipt['cases']['original_narrow_tube_1_4']['certificate_origin']
    assert origin['route'] == 'saved_certificate'
    assert origin['producer_revision'] == 'fd3eeb7e6a5df99ad1781f63c090355fe497eaf1'
    assert (
        hashlib.sha256((ROOT / origin['path']).read_bytes()).hexdigest()
        == origin['sha256']
    )
    for name, digest in receipt['files'].items():
        assert (
            hashlib.sha256((BASE / 'receiving' / name).read_bytes()).hexdigest()
            == digest
        )
    for name, digest in execution['files'].items():
        assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == digest
    assert receipt['native_dfnd_qualification'] == 'not_changed'
    assert receipt['requested_precision_status'] == 'not_computed'


def test_retained_exact_anchor_connection_is_continuous_and_origin_can_be_blocked():
    model = Model.from_record(read_record(FOLDER / 'model.json'))
    queries = read_record(FOLDER / 'anchors.json')
    assert queries['locations']['origin']['point_state'] == 'blocked'
    a, b = (queries['locations'][k] for k in ['lower', 'upper'])
    assert a['point_state'] == b['point_state'] == 'free'
    assert a['region_id'] == b['region_id']
    (connection,) = queries['pairs']
    assert connection['connected'] is True
    assert verify(model, connection['path_certificate'])['path_validated'] is True


def test_repeat_records_bounded_one_cpu_phases_and_conservative_host_samples():
    execution = read_record(BASE / 'execution.json')
    assert execution['receiving_status'] == 'completed'
    assert execution['exit_code'] == 0 and execution['stop_reason'] is None
    assert len(execution['cpu_affinity']) == 1
    policy = execution['resource_policy']
    assert policy['address_space_limit_bytes'] == 2 * 1024**3
    assert policy['cpu_limit_seconds'] == 180 and policy['wall_limit_seconds'] == 240
    assert all(s['host']['safe'] for s in execution['host_samples'])
    phases = read_record(FOLDER / 'phases.json')
    assert list(phases) == [
        'model_receiving',
        'saved_certificate_reading',
        'saved_reading',
        'verification',
        'anchor_queries',
    ]
    assert all(
        p['wall_seconds'] >= 0 and p['cpu_seconds'] >= 0 for p in phases.values()
    )


def test_actual_narrow_certificate_is_independently_checkable_without_scientific_stack():
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
            str(FOLDER / 'model.json'),
            str(FOLDER / 'certificate.json'),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=40,
    )
    checked = json.loads(result.stdout)
    old = read_record(FOLDER / 'verification.json')
    assert checked['topology_complete'] is True
    assert checked['n_components'] == 1
    assert checked['n_boundary_patches'] == 2
    for key in ['n_components', 'regions', 'boundary_patches', 'nodes', 'edges']:
        assert checked[key] == old[key]
    assert checked['per_region_volume_status'] == 'not_computed'
