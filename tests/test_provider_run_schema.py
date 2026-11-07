"""Portable schema validation must survive deliberately rehashed bad manifests."""

import hashlib
import json
import zipfile

import pytest

from topomt.provider_output import ProviderRun


def seal(manifest):
    body = {key: value for key, value in manifest.items() if key != 'run_id'}
    encoded = json.dumps(body, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return {**body, 'run_id': hashlib.sha256(encoded.encode()).hexdigest()}


@pytest.fixture
def portable():
    artifacts = {
        'input/submitted.pdb': b'ATOM  original\n',
        'output/nested/result.bin': b'\x00\xff\n',
    }
    manifest = seal(
        {
            'schema_version': 1,
            'provider': 'castp',
            'backend': 'files',
            'metadata': {'selection': [4, 1], 'nested': {'available': True}},
            'artifacts': {
                name: hashlib.sha256(data).hexdigest()
                for name, data in artifacts.items()
            },
        }
    )
    return manifest, artifacts


def write_bundle(path, manifest, artifacts, *, raw_manifest=None):
    if raw_manifest is None:
        raw_manifest = json.dumps(
            manifest, sort_keys=True, separators=(',', ':'), allow_nan=False
        ).encode()
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('manifest.json', raw_manifest)
        for name, data in artifacts.items():
            archive.writestr(name, data)
    return path


@pytest.mark.parametrize(
    ('provider', 'backend'),
    [
        ('fpocket', 'cli'),
        ('pocketeer', 'library'),
        ('alphaspace2', 'library'),
        ('pycasta', 'library'),
        ('castp', 'files'),
        ('castp', 'server'),
    ],
)
def test_valid_capture_save_load_save_preserves_identity_and_bytes(
    tmp_path, provider, backend
):
    source = tmp_path / 'submitted.pdb'
    source.write_bytes(b'ATOM  original\n')
    output = tmp_path / 'output'
    (output / 'nested').mkdir(parents=True)
    (output / 'nested' / 'result.bin').write_bytes(b'\x00\xff\n')
    run = ProviderRun.capture(
        provider,
        backend,
        source,
        output,
        metadata={'selection': [4, 1], 'nested': {'available': True}},
    )
    first, second = tmp_path / 'first.zip', tmp_path / 'second.zip'
    run.save(first)
    restored = ProviderRun.load(first)
    restored.save(second)
    assert ProviderRun.load(second) == restored == run
    with zipfile.ZipFile(first) as left, zipfile.ZipFile(second) as right:
        assert {n: left.read(n) for n in left.namelist()} == {
            n: right.read(n) for n in right.namelist()
        }


@pytest.mark.parametrize('schema', [True, False, 1.0, '1', None, 0, 2, []])
def test_rehashed_manifest_requires_literal_integer_schema_one(
    portable, tmp_path, schema
):
    manifest, artifacts = portable
    manifest['schema_version'] = schema
    path = write_bundle(tmp_path / 'bad.zip', seal(manifest), artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize(
    'field',
    ['schema_version', 'provider', 'backend', 'metadata', 'artifacts', 'run_id'],
)
def test_manifest_requires_every_schema_field(portable, tmp_path, field):
    manifest, artifacts = portable
    del manifest[field]
    if field != 'run_id':
        manifest = seal(manifest)
    path = write_bundle(tmp_path / 'missing.zip', manifest, artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


def test_rehashed_extra_manifest_field_is_rejected_before_lossy_roundtrip(
    portable, tmp_path
):
    manifest, artifacts = portable
    manifest['unretained_extension'] = {'important': 'must not disappear'}
    path = write_bundle(tmp_path / 'extended.zip', seal(manifest), artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize('field', ['provider', 'backend'])
@pytest.mark.parametrize('value', [None, True, 1, [], {}, '', '   '])
def test_rehashed_manifest_requires_nonempty_provider_and_backend_strings(
    portable, tmp_path, field, value
):
    manifest, artifacts = portable
    manifest[field] = value
    path = write_bundle(tmp_path / 'bad.zip', seal(manifest), artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize('value', [None, False, 1, [], 'metadata'])
def test_rehashed_manifest_requires_metadata_object(portable, tmp_path, value):
    manifest, artifacts = portable
    manifest['metadata'] = value
    path = write_bundle(tmp_path / 'bad.zip', seal(manifest), artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize('value', [None, False, 1, [], 'artifacts'])
def test_rehashed_manifest_requires_artifact_checksum_object(portable, tmp_path, value):
    manifest, artifacts = portable
    manifest['artifacts'] = value
    path = write_bundle(tmp_path / 'bad.zip', seal(manifest), artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize('value', [None, True, 1, [], {}, 'bad', '0' * 63, 'G' * 64])
def test_rehashed_artifact_checksums_require_sha256_strings(portable, tmp_path, value):
    manifest, artifacts = portable
    manifest['artifacts']['output/nested/result.bin'] = value
    path = write_bundle(tmp_path / 'bad.zip', seal(manifest), artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize('value', [None, True, 1, [], {}, 'bad', '0' * 63, 'G' * 64])
def test_run_identity_requires_sha256_string(portable, tmp_path, value):
    manifest, artifacts = portable
    manifest['run_id'] = value
    path = write_bundle(tmp_path / 'bad.zip', manifest, artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize(
    'name',
    [
        'output//result.bin',
        'output/result.bin/',
        'output/./result.bin',
        'output/../result.bin',
        'output\\result.bin',
        '/output/result.bin',
        'other/result.bin',
    ],
)
def test_rehashed_manifest_rejects_noncanonical_artifact_identity(
    portable, tmp_path, name
):
    manifest, artifacts = portable
    old_name = 'output/nested/result.bin'
    artifacts[name] = artifacts.pop(old_name)
    manifest['artifacts'][name] = manifest['artifacts'].pop(old_name)
    path = write_bundle(tmp_path / 'alias.zip', seal(manifest), artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize('duplicate', ['provider', 'selection', 'artifact', 'run_id'])
def test_duplicate_json_keys_are_rejected_even_when_last_values_match_valid_id(
    portable, tmp_path, duplicate
):
    manifest, artifacts = portable
    raw = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
    if duplicate in {'provider', 'run_id'}:
        raw = '{' + json.dumps(duplicate) + ':"discarded",' + raw[1:]
    elif duplicate == 'selection':
        raw = raw.replace('"metadata":{', '"metadata":{"selection":"discarded",', 1)
    else:
        raw = raw.replace(
            '"artifacts":{',
            '"artifacts":{"output/nested/result.bin":"discarded",',
            1,
        )
    path = write_bundle(
        tmp_path / 'duplicate.zip', manifest, artifacts, raw_manifest=raw.encode()
    )
    with pytest.raises(ValueError, match='duplicate'):
        ProviderRun.load(path)


@pytest.mark.parametrize('value', [None, True, 1, [], 'manifest'])
def test_manifest_must_be_a_json_object(portable, tmp_path, value):
    _, artifacts = portable
    path = write_bundle(tmp_path / 'bad.zip', value, artifacts)
    with pytest.raises(ValueError):
        ProviderRun.load(path)


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('provider', None),
        ('provider', ''),
        ('backend', True),
        ('backend', '   '),
        ('metadata', []),
        ('metadata', False),
        ('metadata', 'invalid'),
    ],
)
def test_capture_rejects_invalid_portable_identity_types_before_reading_files(
    tmp_path, field, value
):
    options = {'provider': 'castp', 'backend': 'files', 'metadata': {}}
    options[field] = value
    with pytest.raises(ValueError):
        ProviderRun.capture(
            input_file=tmp_path / 'absent.pdb',
            output_dir=tmp_path / 'absent',
            **options,
        )
