"""Five original parsers share offline save/recover workflows, without engines."""

import builtins
import hashlib
import json
import socket
import subprocess
import zipfile
from pathlib import Path
from urllib import request as url_request

import molsysmt as msm
import pytest

import topomt as tmt
from tests.methods.alphaspace2.test_saved_output import captured as alpha_cases
from tests.methods.castp.test_source_bound_output import (
    bind,
    same,
    snapshot,
)
from tests.methods.castp.test_source_bound_output import (
    binding_profile as castp_profile,
)
from tests.methods.fpocket4.test_saved_output import build_captured
from tests.methods.pycasta.test_input_context import (
    fake_original as pycasta_original,
)
from tests.methods.pycasta.test_input_context import (
    source as pycasta_source,
)
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun

# Pytest discovers these reused fixtures by name through getfixturevalue below.
__all__ = ['alpha_cases', 'castp_profile', 'pycasta_original', 'pycasta_source']

ROOT = Path(__file__).resolve().parents[1]


def _archived_pocketeer(folder):
    archive = ROOT / (
        'devguide/pocketeer/evidence/'
        'pocketeer_saved_output_public_receptor_20261106.zip'
    )
    with zipfile.ZipFile(archive) as files:
        manifest = json.loads(files.read('manifest.json'))
        for name in ('source.h5msm', 'original.zip'):
            member = 'structural-control/' + name
            data = files.read(member)
            assert len(data) == manifest[member]['bytes']
            assert hashlib.sha256(data).hexdigest() == manifest[member]['sha256']
            (folder / name).write_bytes(data)
    return {
        'provider': 'pocketeer',
        'source': msm.convert(folder / 'source.h5msm', to_form='molsysmt.MolSys'),
        'bundle': folder / 'original.zip',
        'binder': None,
    }


@pytest.fixture(
    params=[
        'fpocket',
        'pocketeer',
        'alphaspace2',
        'alphaspace2-bound',
        'pycasta',
        'castp',
    ]
)
def saved_case(request, tmp_path):
    """Reuse committed original bytes or small analytical original-format builders."""
    provider = request.param
    case = {'provider': provider, 'binder': None, 'bundle': tmp_path / 'original.zip'}
    if provider == 'fpocket':
        source, output, bundle, *_ = build_captured(tmp_path)
        case.update(source=source, bundle=bundle, original=output)
    elif provider == 'pocketeer':
        case = _archived_pocketeer(tmp_path)
    elif provider.startswith('alphaspace2'):
        tag = 'bound' if provider.endswith('-bound') else 'unbound'
        archived = request.getfixturevalue('alpha_cases')[tag]
        case.update(
            provider='alphaspace2',
            source=archived['source'],
            binder=archived['binder'],
            bundle=archived['bundle'],
        )
    elif provider == 'pycasta':
        source = request.getfixturevalue('pycasta_source')
        upstream_root, calls = request.getfixturevalue('pycasta_original')
        output = tmt.get_provider_output(
            source,
            method='pycasta',
            backend='library',
            selection=[5, 3, 2, 1, 0],
            structure_indices=1,
            chemical_state=1,
            upstream_root=upstream_root,
        )
        assert len(calls) == 1  # Existing fake worker; no original process executes.
        output.run.save(case['bundle'])
        case.update(source=source, original=output)
    else:
        source, mapping, _ = request.getfixturevalue('castp_profile')
        output = bind(source, mapping, ROOT / 'topomt/data/CASTp_3.0_server/2pk4.zip')
        output.run.save(case['bundle'])
        case.update(source=source, original=output)
    # Persist the exact full source, independently of the provider's selected PDB.
    case['source_file'] = tmp_path / 'full-source.h5msm'
    msm.convert(case['source'], to_form=str(case['source_file']))
    if case['binder'] is not None:
        case['binder_file'] = tmp_path / 'full-binder.h5msm'
        msm.convert(case['binder'], to_form=str(case['binder_file']))
    return case


def _forbid_execution(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Saved recovery attempted network or engine execution.')

    original_import = builtins.__import__
    engines = {'alphaspace2', 'mdtraj', 'pocketeer', 'pycasta', 'run_analysis'}

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name.split('.')[0] in engines:
            raise AssertionError('Saved recovery imported original engine: ' + name)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, '__import__', guarded_import)
    monkeypatch.setattr(socket, 'create_connection', forbidden)
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(socket.socket, 'connect_ex', forbidden)
    monkeypatch.setattr(url_request, 'urlopen', forbidden)
    monkeypatch.setattr(subprocess, 'run', forbidden)
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    # The existing pyCASTA builder isolates its worker in a local fake object.
    from topomt.third_party.pycasta import library

    monkeypatch.setattr(library.subprocess, 'run', forbidden)


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_public_save_and_self_describing_load_preserve_original_output(
    saved_case, tmp_path, monkeypatch, policy
):
    case = saved_case
    _forbid_execution(monkeypatch)
    files = [case['source_file'], case['bundle']]
    sources = [case['source']]
    if case['binder'] is not None:
        files.append(case['binder_file'])
        sources.append(case['binder'])
    before_files = {path: path.read_bytes() for path in files}
    before_sources = [snapshot(source) for source in sources]
    options = {'binder': case['binder']} if case['provider'] == 'alphaspace2' else {}
    with puw.context(standard_units=[*policy, 'radians']):
        active_units = puw.configure.report()['standard_units']
        reference = tmt.get_provider_output(
            case['source'],
            method=case['provider'],
            backend='files',
            bundle_file=case['bundle'],
            **options,
        )
        if 'original' in case:
            assert reference.run == case['original'].run
            same(reference.records, case['original'].records)
        path = tmp_path / 'public-save.zip'
        reference.save(path)
        restored = tmt.load_provider_output(
            path, molecular_system=case['source'], binder=case['binder']
        )
        assert type(restored) is type(reference)
        assert restored.run == reference.run == ProviderRun.load(path)
        assert restored.run == ProviderRun.load(case['bundle'])
        same(restored.records, reference.records)
        same(restored.input_coordinates, reference.input_coordinates)
        assert [record.source_id for record in restored.pockets] == [
            record.source_id for record in reference.pockets
        ]
        assert puw.configure.report()['standard_units'] == active_units
        # A second public save preserves the original acquisition, not a new files run.
        second = tmp_path / 'second-save.zip'
        restored.save(second)
        assert ProviderRun.load(second) == reference.run
        for source, before in zip(sources, before_sources, strict=True):
            same(snapshot(source), before)
    assert all(path.read_bytes() == before for path, before in before_files.items())
