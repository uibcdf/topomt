"""Wide-tube receiving keeps source geometry, physical truth and native scope."""

import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

from devtools.reference_validator.model import Model, decode_point
from devtools.reference_validator.storage import read_record
from devtools.reference_validator.verify import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_power_cells_wide_v1'


def _profiles():
    spec = read_record(BASE / 'protocol.json')
    for row in spec['profiles']:
        path = ROOT / row['protocol']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['protocol_sha256']
        (case,) = read_record(path)['cases']
        yield row['probe_angstroms'], path.parent, case


def _receipt_bytes(base):
    receipt = read_record(base / 'receiving/receipt.json')
    execution = read_record(base / 'execution.json')
    assert receipt['source_tree_modified'] is False
    assert receipt['source_revision'] == execution['source_revision']
    assert (
        receipt['protocol_sha256']
        == hashlib.sha256((base / 'protocol.json').read_bytes()).hexdigest()
    )
    assert (
        execution['log_sha256']
        == hashlib.sha256((base / 'execution.log').read_bytes()).hexdigest()
    )
    for name, digest in receipt['files'].items():
        assert (
            hashlib.sha256((base / 'receiving' / name).read_bytes()).hexdigest()
            == digest
        )
    for name, digest in execution['files'].items():
        assert hashlib.sha256((base / name).read_bytes()).hexdigest() == digest
    return receipt, execution


def test_frozen_wide_inputs_and_every_receiving_file_retain_source_identity():
    rows = list(_profiles())
    assert [p for p, _, _ in rows] == [1.4, 2.5, 5.0]
    for _, base, case in rows:
        ref = case['reference_origin']
        archive = ROOT / ref['archive']
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == ref['archive_sha256']
        with zipfile.ZipFile(archive) as stream:
            raw = stream.read(ref['member'])
        assert hashlib.sha256(raw).hexdigest() == ref['member_sha256']
        assert json.loads(raw) == case['model']
        assert (
            read_record(base / 'receiving' / case['name'] / 'model.json')
            == case['model']
        )
        receipt, _ = _receipt_bytes(base)
        assert receipt['native_dfnd_qualification'] == 'not_changed'
        assert receipt['requested_precision_status'] == 'not_computed'


def test_complete_geometry_initialization_is_separate_from_profile_queries():
    base = BASE / 'initialization'
    receipt, execution = _receipt_bytes(base)
    result = read_record(base / 'receiving/wide_geometry_1_4/verification.json')
    assert result['topology_complete'] is True
    assert (result['n_components'], result['n_boundary_patches']) == (1, 2)
    assert (
        receipt['cases']['wide_geometry_1_4']['certificate_origin']['route']
        == 'constructed_here'
    )
    queries = read_record(base / 'receiving/wide_geometry_1_4/anchors.json')
    assert queries['points'] == {} and queries['pairs'] == []
    assert execution['resource_policy']['cpu_limit_seconds'] == 300
    assert execution['resource_policy']['wall_limit_seconds'] == 360


def test_each_profile_preserves_all_seventy_seven_complete_geometric_cells():
    source_folder = BASE / 'initialization/receiving/wide_geometry_1_4'
    source = read_record(source_folder / 'certificate.json')
    old_model = Model.from_record(read_record(source_folder / 'model.json'))
    assert len(old_model.atoms) == 77
    producer = read_record(BASE / 'initialization/receiving/receipt.json')[
        'source_revision'
    ]
    for probe, base, case in _profiles():
        folder = base / 'receiving' / case['name']
        new = read_record(folder / 'certificate.json')
        target = Model.from_record(read_record(folder / 'model.json'))
        assert len(new['cells']) == len(target.atoms) == 77
        assert new['model_sha256'] == target.digest
        for old, row in zip(source['cells'], new['cells']):
            for key in ['atom_id', 'support', 'vertices', 'edges']:
                assert old[key] == row[key]
        origin = read_record(base / 'receiving/receipt.json')['cases'][case['name']][
            'certificate_origin'
        ]
        if probe == 1.4:
            assert origin['route'] == 'saved_certificate'
            assert origin['producer_revision'] == producer
            assert new == source
        else:
            assert origin['route'] == 'reprobed_geometry'
            assert origin['geometry_producer_revision'] == producer
            assert new['model_sha256'] != source['model_sha256']


def test_profile_region_patch_and_axis_anchor_claims_keep_their_own_scopes():
    for probe, base, case in _profiles():
        folder = base / 'receiving' / case['name']
        result = read_record(folder / 'verification.json')
        queries = read_record(folder / 'anchors.json')
        model = Model.from_record(read_record(folder / 'model.json'))
        assert result['topology_complete'] is True
        assert result['per_region_volume_status'] == 'not_computed'
        if probe < 5:
            assert result['n_components'] == 1 and result['n_boundary_patches'] == 2
            assert queries['locations']['origin']['point_state'] == 'free'
            lower, upper = (queries['locations'][k] for k in ['lower', 'upper'])
            assert lower['region_id'] == upper['region_id']
            assert lower['boundary_patch_id'] != upper['boundary_patch_id']
            (pair,) = queries['pairs']
            assert pair['connected'] is True
            assert verify(model, pair['path_certificate'])['path_validated'] is True
        else:
            assert result['n_components'] == result['n_boundary_patches'] == 0
            assert result['volume_lower'] == result['volume_upper'] == ['0', '1']
            assert queries['locations']['origin']['point_state'] == 'blocked'
            assert queries['pairs'] == []
            atoms = {a.source_id: a for a in model.atoms}
            for cell in read_record(folder / 'certificate.json')['cells']:
                atom = atoms[cell['atom_id']]
                assert not cell['free_vertices']
                assert all(
                    sum((x - c) ** 2 for x, c in zip(decode_point(v), atom.center))
                    <= (atom.radius + model.probe) ** 2
                    for v in cell['vertices']
                )


def test_initialization_and_all_profiles_are_sequential_bounded_recorded_workers():
    stages = [(BASE / 'initialization', 300, 360)]
    stages.extend((base, 240, 300) for _, base, _ in _profiles())
    previous_end = None
    for base, cpu, wall in stages:
        execution = read_record(base / 'execution.json')
        assert execution['receiving_status'] == 'completed'
        assert execution['exit_code'] == 0 and execution['stop_reason'] is None
        assert len(execution['cpu_affinity']) == 1
        assert execution['resource_policy']['address_space_limit_bytes'] == 2 * 1024**3
        assert execution['resource_policy']['cpu_limit_seconds'] == cpu
        assert execution['resource_policy']['wall_limit_seconds'] == wall
        assert all(s['host']['safe'] for s in execution['host_samples'])
        start = datetime.fromisoformat(execution['recorded_at_utc']).timestamp()
        if previous_end is not None:
            assert start >= previous_end
        previous_end = start + execution['elapsed_seconds']


@pytest.mark.parametrize(
    'probe_folder,name,positive',
    [
        ('probe_2_5', 'original_wide_tube_2_5', True),
        ('probe_5_0', 'original_wide_tube_5_0', False),
    ],
)
def test_actual_wide_positive_and_negative_proofs_check_without_the_scientific_stack(
    probe_folder, name, positive
):
    folder = BASE / probe_folder / 'receiving' / name
    script = """
import sys,json,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CPU,(90,90))
for name in ['topomt','numpy','scipy','pyunitwizard','devtools.reference_validator.producer','devtools.reference_validator.power_cells','devtools.reference_validator.center_hull']:
 sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
model=Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
r=verify(model,json.loads(Path(sys.argv[2]).read_text()))
print(json.dumps({k:r[k] for k in ['model_sha256','certificate_sha256','topology_complete','n_components','n_boundary_patches','volume_lower','volume_upper']}))
"""
    run = subprocess.run(
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
        timeout=120,
    )
    result = json.loads(run.stdout)
    old = read_record(folder / 'verification.json')
    assert result['topology_complete'] is True
    for key in [
        'model_sha256',
        'certificate_sha256',
        'n_components',
        'n_boundary_patches',
    ]:
        assert result[key] == old[key]
    if positive:
        assert result['n_components'] == 1 and result['n_boundary_patches'] == 2
    else:
        assert result['n_components'] == result['n_boundary_patches'] == 0
        assert result['volume_lower'] == result['volume_upper'] == ['0', '1']


def test_family_summary_preserves_reference_faces_and_actual_execution_sources():
    summary = read_record(BASE / 'family_summary.json')
    facets = read_record(
        BASE / 'initialization/receiving/wide_geometry_1_4/model.json'
    )['domain']['certificate']['facets']
    assert [p['probe']['requested']['value'] for p in summary['profiles']] == [
        1.4,
        2.5,
        5.0,
    ]
    for row in summary['profiles']:
        for ref in row['sources'].values():
            assert (
                hashlib.sha256((ROOT / ref['path']).read_bytes()).hexdigest()
                == ref['sha256']
            )
        receipt = read_record(ROOT / row['sources']['receipt']['path'])
        (case,) = receipt['cases'].values()
        execution = read_record(ROOT / row['sources']['execution']['path'])
        checked = read_record(ROOT / row['sources']['verification']['path'])
        assert row['source_revision'] == receipt['source_revision']
        assert row['model_sha256'] == case['model_sha256']
        assert row['certificate_origin'] == case['certificate_origin']
        assert row['topology']['n_components'] == case['n_components']
        assert row['resources']['wall_seconds'] == execution['elapsed_seconds']
        assert row['resources']['cpu_seconds'] == execution['child_cpu_seconds']
        comparison = row['boundary_reference_comparison']
        if comparison is not None:
            for key in ['reference_verification', 'reference_certificate']:
                ref = comparison[key]
                assert (
                    hashlib.sha256((ROOT / ref['path']).read_bytes()).hexdigest()
                    == ref['sha256']
                )
            old = read_record(ROOT / comparison['reference_verification']['path'])
            current = sorted(
                [
                    sorted(
                        {
                            tuple(facets[s['domain_plane_index']]['source_ids'])
                            for s in p['face_supports']
                        }
                    )
                    for p in checked['boundary_patches']
                ]
            )
            prior = sorted(
                [
                    sorted(tuple(f) for f in part)
                    for part in old['components_faces_source_atom_indices']
                ]
            )
            assert current == prior
            assert [[list(face) for face in part] for part in current] == comparison[
                'opening_components_faces_source_ids'
            ]
            assert comparison['free_domain_face_count'] == sum(map(len, current))
            assert comparison['matches_earlier_partition'] is True
            assert comparison['free_wall_face_count'] == 0
    reuse = read_record(BASE / 'source_qualification_reuse.json')
    reference = reuse['reference_receipt']
    assert (
        hashlib.sha256((ROOT / reference['path']).read_bytes()).hexdigest()
        == reference['sha256']
    )
    assert (
        reuse['current_scientific_files_sha256']
        == read_record(ROOT / reference['path'])['source_files_sha256']
    )
    assert reuse['same_scientific_source_bytes'] is True
    for _, base, _ in _profiles():
        assert (
            read_record(base / 'receiving/receipt.json')['source_files_sha256']
            == reuse['current_scientific_files_sha256']
        )
