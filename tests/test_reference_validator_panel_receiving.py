"""The measured six-case report remains bound to complete saved evidence."""

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from devtools.reference_validator.model import record_digest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/content/benchlab/synthetic/artifacts/reference_validator_panel_v1'


def test_measured_panel_retains_six_cases_nineteen_profiles_and_honest_global_scope():
    protocol = json.loads((BASE / 'protocol.json').read_text())
    summary = json.loads((BASE / 'summary.json').read_text())
    receipt = json.loads((BASE / 'receiving_receipt.json').read_text())
    assert receipt['source_revision'] == '2b21cb2ee63093734ff71f1f70bd4ede7a53ebbb'
    assert summary['producer_source_revision'] == receipt['source_revision']
    assert summary['profile_count'] == 19 and summary['case_count'] == 6
    assert summary['full_validator_p5_qualified'] is False
    assert summary['proof_outcomes'] == {'accepted': 187, 'rejected_candidate': 118}
    assert (
        receipt['protocol_sha256']
        == hashlib.sha256((BASE / 'protocol.json').read_bytes()).hexdigest()
    )
    assert receipt['selected_cases'] == [row['name'] for row in protocol['cases']]
    assert receipt['execution_mode'] == 'local_sequential'
    assert len(receipt['parent_cpu_affinity']) == 1
    with zipfile.ZipFile(BASE / 'receiving.zip') as archive:
        manifest = json.loads(archive.read('MANIFEST.json'))
        assert manifest == json.loads((BASE / 'bundle_manifest.json').read_text())
        assert set(archive.namelist()) == set(manifest['files']) | {'MANIFEST.json'}
        for name, digest in manifest['files'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
        assert (
            archive.read('receiving/receipt.json')
            == (BASE / 'receiving_receipt.json').read_bytes()
        )
        for name, digest in receipt['files'].items():
            assert (
                hashlib.sha256(archive.read('receiving/' + name)).hexdigest() == digest
            )
        profiles = complete = 0
        for case in protocol['cases']:
            row = receipt['cases'][case['name']]
            assert row['status'] == 'completed'
            assert row['worker_wall_seconds'] > 0 and row['worker_cpu_seconds'] > 0
            assert row['peak_rss_kib_linux'] > 0
            assert row['cpu_limit_seconds'] == 180
            assert row['address_space_limit_bytes'] == 2 * 1024**3
            assert len(row['cpu_affinity']) == 1
            assert row['host_before']['safe'] and row['host_after']['safe']
            assert all(sample['safe'] for sample in row['host_samples'])
            assert row['worker_wall_seconds'] >= row['setup']['wall_seconds'] + sum(
                p['profile_wall_seconds'] for p in row['profiles']
            )
            assert [p['probe_angstroms'] for p in row['profiles']] == case[
                'probes_angstroms'
            ]
            for index, profile in enumerate(row['profiles']):
                profiles += 1
                model = json.loads(
                    archive.read(
                        f'receiving/cases/{case["name"]}/profile_{index}/model.json'
                    )
                )
                assert record_digest(model) == profile['model_sha256']
                assert len(model['atoms']) == case['n_atoms']
                assert model['source_sha256'] == case['input_sha256']
                assert model['domain']['kind'] == 'center_hull'
                centers = model['domain']['source']['centers']
                assert [(a['source_id'], a['center']) for a in model['atoms']] == [
                    (c['source_id'], c['point']) for c in centers
                ]
                assert profile['whole_hull']['n_components'] is None
                assert profile['whole_hull']['topology_complete'] is False
                part = profile['tetrahedron_partition']
                if part and part['topology_complete']:
                    complete += 1
                    assert (
                        case['name'] == 'regular_tetrahedron'
                        and profile['probe_angstroms'] == 1.7
                    )
                    assert part['n_components'] == 0 and part['volume_upper'] == [
                        '0',
                        '1',
                    ]
        assert profiles == 19 and complete == 1
    assert summary['summed_worker_cpu_seconds'] == sum(
        c['worker_cpu_seconds'] for c in receipt['cases'].values()
    )
    assert summary['maximum_worker_rss_kib_linux'] == max(
        c['peak_rss_kib_linux'] for c in receipt['cases'].values()
    )


@pytest.mark.parametrize(
    'case,index,model_name,certificate',
    [
        ('regular_tetrahedron', 2, 'tetrahedron_model.json', 'tetrahedron_partition'),
        ('straight_tube_narrow_dense', 1, 'model.json', 'bent_interior_reference'),
    ],
)
def test_downloaded_checker_replays_without_topomt_or_numerical_dependencies(
    tmp_path, case, index, model_name, certificate
):
    with zipfile.ZipFile(BASE / 'receiving.zip') as archive:
        archive.extractall(tmp_path)
    profile = tmp_path / 'receiving/cases' / case / f'profile_{index}'
    script = """
import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
for name in ['topomt','numpy','scipy','pyunitwizard','devtools.reference_validator.producer','devtools.reference_validator.center_hull','devtools.reference_validator.benchlab_panel']:
    sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
m=Model.from_record(json.loads(Path(sys.argv[2]).read_text()))
print(json.dumps(verify(m,json.loads(Path(sys.argv[3]).read_text()))))
"""
    result = subprocess.run(
        [
            sys.executable,
            '-I',
            '-c',
            script,
            str(tmp_path),
            str(profile / model_name),
            str(profile / 'queries' / f'{certificate}.certificate.json'),
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    checked = json.loads(result.stdout)
    if case == 'regular_tetrahedron':
        assert checked['topology_complete'] is True and checked['n_components'] == 0
    else:
        assert checked['path_validated'] is True
        assert checked['n_components'] is None and checked['topology_complete'] is False
