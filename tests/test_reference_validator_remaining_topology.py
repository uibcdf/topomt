"""Original shell/dumbbell receiving keeps exhaustive and named claims distinct."""

import hashlib
import json
from pathlib import Path

from devtools.reference_validator.model import Model, record_digest
from devtools.reference_validator.verify import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_remaining_topology_v1'


def _read(path):
    return json.loads(path.read_text())


def test_all_ten_original_models_and_receiving_bytes_are_bound():
    summary = _read(BASE / 'family_summary.json')
    assert len(summary['profiles']) == 10
    for row in summary['profiles']:
        for source in row['sources'].values():
            assert (
                hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest()
                == source['sha256']
            )
        protocol_path = ROOT / row['sources']['protocol']['path']
        protocol = _read(protocol_path)
        (case,) = protocol['cases']
        assert case['expected_components'] is case['expected_boundary_patches'] is None
        assert record_digest(case['model']) == row['model_sha256']
        assert _read(ROOT / row['sources']['model']['path']) == case['model']
        receipt = _read(ROOT / row['sources']['receipt']['path'])
        assert receipt['source_tree_modified'] is False
        assert (
            receipt['protocol_sha256']
            == hashlib.sha256(protocol_path.read_bytes()).hexdigest()
        )
        receiving = protocol_path.parent / 'receiving'
        for relative, digest in receipt['files'].items():
            assert (
                hashlib.sha256((receiving / relative).read_bytes()).hexdigest()
                == digest
            )
        proof = _read(ROOT / row['sources']['certificate']['path'])
        assert proof['model_sha256'] == row['model_sha256']
        assert len(proof['cells']) == len(case['model']['atoms'])
        for name, state in row['original_point_states_rechecked'].items():
            assert row['locations'][name]['point_state'] == state


def test_global_counts_preserve_extra_dumbbell_regions_and_anchor_scope():
    rows = _read(BASE / 'family_summary.json')['profiles']
    assert [(r['n_components'], r['n_boundary_patches']) for r in rows] == [
        (1, 13),
        (1, 0),
        (1, 0),
        (0, 0),
        (1, 1),
        (1, 0),
        (0, 0),
        (3, 2),
        (2, 0),
        (0, 0),
    ]
    first, second, empty = rows[-3:]
    assert (
        first['locations']['chamber_left']['region_id']
        == first['locations']['chamber_right']['region_id']
    )
    assert [r['boundary_patch_ids'] for r in first['region_boundary_incidence']] == [
        [],
        ['PATCH-1'],
        ['PATCH-2'],
    ]
    assert (
        second['locations']['chamber_left']['region_id']
        != second['locations']['chamber_right']['region_id']
    )
    assert empty['locations']['origin']['point_state'] == 'blocked'
    for row, connected in [(first, True), (second, False)]:
        anchors = _read(ROOT / row['sources']['anchors']['path'])
        (pair,) = anchors['pairs']
        assert pair['connected'] is connected
        if connected:
            model = Model.from_record(_read(ROOT / row['sources']['model']['path']))
            assert verify(model, pair['path_certificate'])['path_validated'] is True


def test_remaining_receiving_is_bounded_and_complete_without_native_fix_claims():
    summary = _read(BASE / 'family_summary.json')
    for row in summary['profiles']:
        execution = _read(ROOT / row['sources']['execution']['path'])
        receipt = _read(ROOT / row['sources']['receipt']['path'])
        checked = _read(ROOT / row['sources']['verification']['path'])
        proof = _read(ROOT / row['sources']['certificate']['path'])
        assert execution['exit_code'] == 0
        assert execution['stop_reason'] is None
        assert execution['receiving_status'] == 'completed'
        assert len(execution['cpu_affinity']) == 1
        assert execution['resource_policy']['address_space_limit_bytes'] == 2 * 1024**3
        assert execution['child_cpu_seconds'] < 600
        assert all(s['host']['safe'] for s in execution['host_samples'])
        assert checked['certificate_sha256'] == record_digest(proof)
        assert checked['topology_complete'] is True
        assert checked['per_region_volume_status'] == 'not_computed'
        assert receipt['native_dfnd_qualification'] == 'not_changed'
    assert summary['profile_totals']['wall_seconds'] == sum(
        r['elapsed_seconds'] for r in summary['profiles']
    )
