"""The retained storage capsule binds actual reader and byte-limit evidence."""

import hashlib
import json
import zipfile
from pathlib import Path

BASE = (
    Path(__file__).resolve().parents[1]
    / 'devguide/evidence/reference_validator_storage_v1'
)


def test_capsule_preserves_all_six_source_bound_scientific_storage_routes():
    manifest = json.loads((BASE / 'capsule_manifest.json').read_text())
    archive = BASE / 'receiving.zip'
    assert (
        hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    )
    with zipfile.ZipFile(archive) as saved:
        assert set(saved.namelist()) == set(manifest['members'])
        assert len(saved.namelist()) == len(set(saved.namelist()))
        for name, digest in manifest['members'].items():
            assert not name.startswith('/') and '..' not in Path(name).parts
            assert hashlib.sha256(saved.read(name)).hexdigest() == digest
        sources = json.loads((BASE / 'source.json').read_text())
        assert len(sources) == 51
        assert all(manifest['members'][n] == h for n, h in sources.items())
        cases = json.loads(saved.read('cases.json'))
        assert cases['record_ceiling_bytes'] == 16 * 1024**2
        assert {r['name'] for r in cases['cases']} == {
            'raw',
            'power',
            'parallel',
            'partition',
            'region',
            'edge',
        }
        for row in cases['cases']:
            for name, size in row['record_bytes'].items():
                assert len(saved.read(row['prefix'] + '/' + name)) == size
                assert size <= cases['record_ceiling_bytes']


def test_receiving_keeps_failed_baseline_and_successful_fresh_readers_distinct():
    before = json.loads((BASE / 'before.json').read_text())
    assert before['exit_code'] == 1
    assert '2 failed' in (BASE / 'before.log').read_text()
    readers = json.loads((BASE / 'fresh_readers.json').read_text())['readers']
    assert len(readers) == 6
    for row in readers:
        assert row['exit_code'] == 0 and row['site_packages'] is False
        assert row['producer_scientific_imports'] == 'blocked'
        assert row['name'] + ' independently checked' in row['output']
    for name in ['primary', 'integration', 'capsule']:
        record = json.loads((BASE / (name + '_execution.json')).read_text())
        assert record['exit_code'] == 0 and record['stop_reason'] is None
        assert len(record['cpu_affinity']) == 1
        assert record['address_space_bytes'] == 2 * 1024**3
        assert all(s['host']['safe'] for s in record['samples'])
