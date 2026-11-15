"""Frozen edge-volume receiving preserves inputs and runs without its producer."""

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
ARTIFACT = (
    ROOT / 'docs/content/benchlab/synthetic/artifacts/reference_validator_edge_v1'
)
EVIDENCE = ROOT / 'devguide/evidence/reference_validator_edge_volume_v1'


def test_saved_original_requests_models_and_all_region_bounds_are_preserved():
    index = json.loads((EVIDENCE / 'receiving_index.json').read_text())
    manifest = json.loads((ARTIFACT / 'bundle_manifest.json').read_text())
    archive = ARTIFACT / 'receiving.zip'
    assert (
        hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    )
    assert archive.stat().st_size == manifest['archive_bytes']
    assert len(index['originals']) == 19
    positive = regions = excluded = 0
    with zipfile.ZipFile(archive) as saved:
        assert len(saved.namelist()) == len(set(saved.namelist()))
        assert set(saved.namelist()) == set(manifest['members'])
        for name, digest in manifest['members'].items():
            assert hashlib.sha256(saved.read(name)).hexdigest() == digest
        internal = json.loads(saved.read('MANIFEST.json'))
        assert internal['members'] == {
            k: v for k, v in manifest['members'].items() if k != 'MANIFEST.json'
        }
        sources = json.loads((EVIDENCE / 'source_retry.json').read_text())
        assert len(sources) == 47
        assert all(
            manifest['members'][name] == digest for name, digest in sources.items()
        )
        for row in index['originals']:
            protocol_path = ROOT / row['original_protocol']
            assert (
                hashlib.sha256(protocol_path.read_bytes()).hexdigest()
                == row['original_protocol_sha256']
            )
            protocol = json.loads(protocol_path.read_text())
            assert json.loads(saved.read(row['model_member'])) == protocol['model']
            assert protocol['k'] == 24
            cert = json.loads(saved.read(row['certificate_member']))
            result = json.loads(saved.read(row['verification_member']))
            assert cert['model_sha256'] == result['model_sha256'] == row['model_sha256']
            assert record_digest(cert) == result['certificate_sha256']
            old = next((protocol_path.parent / 'receiving').rglob('certificate.json'))
            assert cert['request'] == json.loads(old.read_text())['request']
            previous = json.loads((old.parent / 'verification.json').read_text())
            request = VolumeRequest.from_record(cert['request'])
            assert request.relative == Fraction(1, 2**24)
            assert result['volume_unit'] == 'nm**3'
            assert result['verification_status'] == 'accepted'
            assert result['topology_complete'] is True
            assert result['precision_status'] == 'resolved'
            assert request.satisfied(
                decode_scalar(result['volume_lower']),
                decode_scalar(result['volume_upper']),
            )
            assert len(result['regions']) == row['n_components']
            assert len(result['regions']) == len(previous['regions'])
            old_regions = {r['region_id']: r for r in previous['regions']}
            assert (
                decode_scalar(previous['volume_lower'])
                <= decode_scalar(result['volume_lower'])
                <= decode_scalar(result['volume_upper'])
                <= decode_scalar(previous['volume_upper'])
            )
            for region in result['regions']:
                assert region['precision_status'] == 'resolved'
                assert request.satisfied(
                    decode_scalar(region['lower']), decode_scalar(region['upper'])
                )
                prior = old_regions[region['region_id']]
                assert (
                    decode_scalar(prior['lower'])
                    <= decode_scalar(region['lower'])
                    <= decode_scalar(region['upper'])
                    <= decode_scalar(prior['upper'])
                )
            if result['regions']:
                positive += 1
                regions += len(result['regions'])
            else:
                excluded += 1
                assert decode_scalar(result['volume_lower']) == 0
                assert decode_scalar(result['volume_upper']) == 0
    assert (positive, regions, excluded) == (13, 16, 6)


def test_saved_boundary_and_region_controls_meet_every_enabled_requirement():
    with zipfile.ZipFile(ARTIFACT / 'receiving.zip') as saved:
        paths = [
            n
            for n in saved.namelist()
            if n.startswith('controls/') and n.endswith('/certificate.json')
        ]
        assert sum(n.startswith('controls/boundary/') for n in paths) == 16
        assert sum(n.startswith('controls/region/') for n in paths) == 9
        for name in paths:
            cert = json.loads(saved.read(name))
            result = json.loads(saved.read(name.replace('certificate', 'verification')))
            req = VolumeRequest.from_record(cert['request'])
            assert result['precision_status'] == 'resolved'
            assert req.satisfied(
                decode_scalar(result['volume_lower']),
                decode_scalar(result['volume_upper']),
            )
            for region in result['regions']:
                assert req.satisfied(
                    decode_scalar(region['lower']), decode_scalar(region['upper'])
                )


def test_extracted_reader_reconstructs_results_without_producers_or_scientific_imports(
    tmp_path,
):
    with zipfile.ZipFile(ARTIFACT / 'receiving.zip') as saved:
        saved.extractall(tmp_path)
    code = """
import importlib.abc, json, pathlib, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        blocked = (
            'topomt', 'numpy', 'scipy', 'molsysmt', 'pyunitwizard', 'ackredit',
            'devtools.reference_validator.power_cells',
            'devtools.reference_validator.edge_volume',
            'devtools.reference_validator.boundary_volume',
            'devtools.reference_validator.region_volume',
            'devtools.reference_validator.producer',
            'devtools.reference_validator.parallel',
        )
        if any(fullname == n or fullname.startswith(n + '.') for n in blocked):
            raise ImportError('Producer/scientific dependency requested: ' + fullname)
sys.meta_path.insert(0, Block())
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
import devtools.reference_validator.verify.edge_volume as reader
assert pathlib.Path(reader.__file__).resolve().is_relative_to(pathlib.Path.cwd())
cases = [
    ('models/regular_tetrahedron/profile_1.json',
     'volumes/regular_tetrahedron/profile_1.json', 1),
    ('controls/boundary/near_corner_rational/k32/model.json',
     'controls/boundary/near_corner_rational/k32/certificate.json', 8),
    ('controls/region/asymmetric_three_regions/model.json',
     'controls/region/asymmetric_three_regions/certificate.json', 3),
]
for model, cert, count in cases:
    result = verify(Model.from_record(json.loads(pathlib.Path(model).read_text())),
                    json.loads(pathlib.Path(cert).read_text()))
    assert result['precision_status'] == 'resolved'
    assert len(result['regions']) == count
    assert all(r['precision_status'] == 'resolved' for r in result['regions'])
print(json.dumps({'fresh_results': 3, 'region_counts': [1, 8, 3]}))
"""
    env = {**os.environ, 'PYTHONPATH': str(tmp_path), 'PYTHONDONTWRITEBYTECODE': '1'}
    run = subprocess.run(
        [sys.executable, '-S', '-c', code],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=40,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert json.loads(run.stdout) == {'fresh_results': 3, 'region_counts': [1, 8, 3]}
