"""Persistence and saved dispatch contracts without provider engines or network."""

import zipfile
from importlib import import_module
from inspect import Parameter, signature
from pathlib import Path

import pytest
from argdigest import UnknownArgumentError

import topomt as tmt
from topomt._private.smonitor import ArgumentError
from topomt.provider_output import ProviderRun
from topomt.third_party.output import ProviderOutput, ProviderRecord


@pytest.fixture
def captured(tmp_path):
    def create(provider='pocketeer', backend='library'):
        root = tmp_path / str(len(list(tmp_path.iterdir())))
        root.mkdir()
        pdb, results = root / 'submitted.pdb', root / 'results'
        pdb.write_bytes(b'REMARK Contract fixture; no molecular calculation.\n')
        results.mkdir()
        (results / 'original.txt').write_bytes(b'Original provider evidence.\n')
        run = ProviderRun.capture(
            provider, backend, pdb, results, metadata={'fixture_case': root.name}
        )
        kind = type('CapturedOutput', (ProviderOutput,), {'provider': provider})
        record = ProviderRecord(
            'consumer-only', 'pocket', run, _fields={'not_original': True}
        )
        output = kind(run, (record,), ((1.0, 2.0, 3.0),))
        bundle = root / 'original.zip'
        run.save(bundle)
        return output, bundle

    return create


@pytest.fixture
def loader():
    return import_module('topomt.load_provider_output')


def forbidden(*args, **kwargs):
    pytest.fail('Rejected persistence input reached dispatch or file loading.')


def test_public_loader_is_exported(loader):
    module = import_module('topomt.load_provider_output')
    assert tmt.load_provider_output is module.load_provider_output
    assert 'load_provider_output' in tmt.__all__
    assert (
        signature(tmt.load_provider_output).parameters['molecular_system'].default
        is Parameter.empty
    )
    assert tmt.load_provider_output.digestion_plan.contracts.resolve(
        'topomt.load_provider_output.load_provider_output'
    )


@pytest.mark.parametrize('as_string', [False, True])
def test_output_save_preserves_only_the_original_run(captured, tmp_path, as_string):
    output, _ = captured()
    before, records = output.run, output.records
    path = tmp_path / 'saved.zip'
    assert output.save(str(path) if as_string else path) is None
    assert ProviderRun.load(path) == before
    assert output.run is before and output.records == records
    with zipfile.ZipFile(path) as archive:
        assert set(archive.namelist()) == {
            'manifest.json',
            *(n for n, _ in before.artifacts),
        }
        assert b'not_original' not in archive.read('manifest.json')


@pytest.mark.parametrize('value', [None, True, 1, b'output.zip', '', '   ', []])
def test_save_path_is_admitted_before_persistence(captured, value, monkeypatch):
    output, _ = captured()
    monkeypatch.setattr(ProviderRun, 'save', forbidden)
    with pytest.raises(ArgumentError, match='path') as caught:
        output.save(value)
    assert caught.value.catalog_key == 'ArgumentError'


def test_saving_to_directory_is_a_filesystem_error(captured, tmp_path):
    output, _ = captured()
    with pytest.raises(OSError):
        output.save(tmp_path)


@pytest.mark.parametrize(
    ('provider', 'backend'),
    [
        ('fpocket', 'cli'),
        ('fpocket', 'wrapper'),
        ('fpocket', 'files'),
        ('pocketeer', 'library'),
        ('alphaspace2', 'library'),
        ('pycasta', 'library'),
        ('castp', 'files'),
    ],
)
def test_verified_identity_selects_only_saved_dispatch(
    captured, loader, monkeypatch, provider, backend
):
    output, path = captured(provider, backend)
    source, binder = object(), object() if provider == 'alphaspace2' else None
    received = []

    def recover(item, **kwargs):
        received.append((item, kwargs))
        return output

    monkeypatch.setattr(loader, 'get_provider_output', recover)
    assert (
        tmt.load_provider_output(path, molecular_system=source, binder=binder) is output
    )
    expected = {'method': provider, 'backend': 'files', 'bundle_file': path}
    if provider == 'alphaspace2':
        expected['binder'] = binder
    assert received == [(source, expected)]
    assert output.run.backend == backend


@pytest.mark.parametrize(
    ('provider', 'backend'),
    [
        ('unknown', 'library'),
        ('os.path', 'files'),
        ('castp', 'server'),
        ('pocketeer', 'files'),
        ('pycasta', 'native'),
    ],
)
def test_unreconstructable_runs_never_dispatch(
    captured, loader, monkeypatch, provider, backend
):
    _, path = captured(provider, backend)
    monkeypatch.setattr(loader, 'get_provider_output', forbidden)
    with pytest.raises(ValueError):
        tmt.load_provider_output(path, molecular_system=object())


def test_integrity_precedes_even_unknown_provider(captured, loader, monkeypatch):
    _, path = captured('unknown', 'native')
    with zipfile.ZipFile(path) as archive:
        payloads = {name: archive.read(name) for name in archive.namelist()}
    payloads['output/original.txt'] = b'Changed without updating checksums.'
    with zipfile.ZipFile(path, 'w') as archive:
        for name, data in payloads.items():
            archive.writestr(name, data)
    monkeypatch.setattr(loader, 'get_provider_output', forbidden)
    with pytest.raises(ValueError, match='(?i)checksum'):
        tmt.load_provider_output(path, molecular_system=object())


@pytest.mark.parametrize('provider', ['fpocket', 'pocketeer', 'pycasta', 'castp'])
def test_binder_is_exclusive_to_alphaspace2(captured, loader, monkeypatch, provider):
    backend = (
        'files'
        if provider == 'castp'
        else 'cli'
        if provider == 'fpocket'
        else 'library'
    )
    _, path = captured(provider, backend)
    monkeypatch.setattr(loader, 'get_provider_output', forbidden)
    with pytest.raises(ArgumentError, match='binder'):
        tmt.load_provider_output(path, molecular_system=object(), binder=object())


@pytest.mark.parametrize('value', [None, True, 1, b'bundle.zip', '', '   ', []])
def test_load_path_rejection_precedes_opening(loader, monkeypatch, value):
    monkeypatch.setattr(ProviderRun, 'load', forbidden)
    with pytest.raises(ArgumentError, match='bundle_file') as caught:
        tmt.load_provider_output(value, molecular_system=object())
    assert caught.value.catalog_key == 'ArgumentError'


def test_source_is_not_inferred_from_bundle(loader, monkeypatch):
    monkeypatch.setattr(ProviderRun, 'load', forbidden)
    with pytest.raises(ArgumentError, match='molecular_system'):
        tmt.load_provider_output(Path('unused.zip'), molecular_system=None)


@pytest.mark.parametrize(
    'key',
    [
        'method',
        'backend',
        'selection',
        'structure_indices',
        'chemical_state',
        'binder_selection',
        'skip_digestion',
    ],
)
def test_saved_execution_overrides_are_closed(loader, monkeypatch, key):
    monkeypatch.setattr(ProviderRun, 'load', forbidden)
    with pytest.raises(UnknownArgumentError, match=key):
        tmt.load_provider_output('unused.zip', molecular_system=object(), **{key: 0})


def test_recovery_cannot_return_a_changed_reread(captured, loader, monkeypatch):
    original, path = captured()
    changed, _ = captured()
    assert changed.run != original.run

    def recover(*args, **kwargs):
        changed.run.save(path)
        return changed

    monkeypatch.setattr(loader, 'get_provider_output', recover)
    with pytest.raises(ValueError, match='(?i)identity|run'):
        tmt.load_provider_output(path, molecular_system=object())
