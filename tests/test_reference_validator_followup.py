"""Additive receiving, restricted precision and a portable saved-proof capsule."""

import hashlib
import json
import os
import subprocess
import sys
import zipfile
from fractions import Fraction
from pathlib import Path

from devtools.reference_validator.model import decode_scalar, record_digest
from devtools.reference_validator.volume_request import VolumeRequest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_boundary_volume_v1'
CAPSULE = (
    ROOT / 'docs/content/benchlab/synthetic/artifacts/reference_validator_followup_v1'
)


def _read(path):
    return json.loads(path.read_text())


def test_all_sixteen_clipped_controls_pass_total_and_every_tiny_region_request():
    jobs = _read(BASE / 'plan.json')['jobs']
    assert len(jobs) == 16
    for job in jobs:
        protocol = ROOT / job['protocol']
        assert hashlib.sha256(protocol.read_bytes()).hexdigest() == job['sha256']
        spec = _read(protocol)
        folder = protocol.parent
        receipt = _read(folder / 'receiving/receipt.json')
        execution = _read(folder / 'execution.json')
        result = _read(folder / 'receiving/leaves_1/verification.json')
        cert = _read(folder / 'receiving/leaves_1/certificate.json')
        assert execution['exit_code'] == 0 and execution['stop_reason'] is None
        assert len(execution['cpu_affinity']) == 1
        assert execution['resource_policy']['address_space_limit_bytes'] == 2 * 1024**3
        assert all(s['host']['safe'] for s in execution['host_samples'])
        assert result['certificate_sha256'] == record_digest(cert)
        assert result['precision_status'] == 'resolved'
        request = VolumeRequest.from_record(receipt['request'])
        assert request.relative == Fraction(1, 2 ** spec['k'])
        assert request.satisfied(
            decode_scalar(result['volume_lower']), decode_scalar(result['volume_upper'])
        )
        assert len(result['regions']) == 8
        independent = spec['independent_region_bounds_nm3']
        lower, upper = map(decode_scalar, [independent['lower'], independent['upper']])
        for row in result['regions']:
            lo, hi = map(decode_scalar, [row['lower'], row['upper']])
            assert lower <= lo <= hi <= upper
            assert request.satisfied(lo, hi)
        for relative, digest in execution['files'].items():
            assert (
                hashlib.sha256((folder / relative).read_bytes()).hexdigest() == digest
            )
        assert (
            hashlib.sha256((folder / 'execution.log').read_bytes()).hexdigest()
            == execution['log_sha256']
        )


def test_capsule_binds_all_payloads_and_preserves_original_numerical_models():
    manifest = _read(CAPSULE / 'bundle_manifest.json')
    archive = CAPSULE / 'receiving.zip'
    assert (
        hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    )
    with zipfile.ZipFile(archive) as stream:
        assert set(stream.namelist()) == set(manifest['members'])
        for name, digest in manifest['members'].items():
            assert not name.startswith('/') and '..' not in Path(name).parts
            assert hashlib.sha256(stream.read(name)).hexdigest() == digest
        inside = json.loads(stream.read('MANIFEST.json'))
        assert inside['manifest_excludes_itself'] is True
        assert inside['members'] == {
            k: v for k, v in manifest['members'].items() if k != 'MANIFEST.json'
        }
        qualification = _read(BASE / 'source_qualification.json')
        for name, digest in qualification['source_files'].items():
            assert hashlib.sha256(stream.read(name)).hexdigest() == digest
        original = _read(
            ROOT / 'devguide/evidence/reference_validator_region_volume_v1/plan.json'
        )['jobs']
        for job in original:
            if job['category'] != 'original':
                continue
            spec = _read(ROOT / job['protocol'])
            key = job['name'].removeprefix('original/')
            assert json.loads(stream.read('models/' + key + '.json')) == spec['model']
            assert (
                stream.read('topology/' + key + '.json')
                == (ROOT / spec['topology_path']).read_bytes()
            )


def test_extracted_capsule_checks_original_and_tiny_proofs_without_scientific_stack(
    tmp_path,
):
    with zipfile.ZipFile(CAPSULE / 'receiving.zip') as stream:
        stream.extractall(tmp_path)
    script = """
import json,sys
from pathlib import Path
for name in ['topomt','numpy','scipy','pyunitwizard','ackredit','devtools.reference_validator.power_cells','devtools.reference_validator.region_volume','devtools.reference_validator.producer']:
 sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
import devtools.reference_validator.verify as checker
assert Path(checker.__file__).resolve().is_relative_to(Path.cwd())
def check(model_path,proof_path):
 model=Model.from_record(json.loads(Path(model_path).read_text()))
 return verify(model,json.loads(Path(proof_path).read_text()))
assert check('models/regular_tetrahedron/profile_1.json','topology/regular_tetrahedron/profile_1.json')['n_components']==1
assert check('models/regular_tetrahedron/profile_1.json','volumes/regular_tetrahedron/profile_1.json')['precision_status']=='unresolved'
tiny=check('controls/near_corner_rational/k32/model.json','controls/near_corner_rational/k32/certificate.json')
assert tiny['precision_status']=='resolved' and len(tiny['regions'])==8
native=check('native/straight_tube_wide_sparse/native_model.json','native/straight_tube_wide_sparse/reference_certificate.json')
assert native['n_components']==0 and native['topology_complete']
"""
    environment = dict(os.environ, PYTHONPATH=str(tmp_path))
    subprocess.run(
        [sys.executable, '-c', script],
        cwd=tmp_path,
        env=environment,
        check=True,
        timeout=100,
    )
