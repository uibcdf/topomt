"""Explicit source-engine gate; ordinary engine-free tests live separately."""

import hashlib
import importlib
import os
import subprocess
from pathlib import Path

import pytest

import topomt as tmt

SOURCE = Path(__file__).resolve().parents[2] / 'data/original_local/source.pdb'
ROOT = os.environ.get('TOPOMT_PYKVFINDER_ROOT')


@pytest.mark.skipif(
    ROOT is None,
    reason='Set TOPOMT_PYKVFINDER_ROOT for the designated original-source gate',
)
def test_original_library_agrees_with_public_output(tmp_path, monkeypatch):
    assert ROOT is not None
    root = Path(ROOT).resolve()
    assert (root / 'pyKVFinder/__init__.py').is_file(), (
        'Requested engine gate cannot skip a missing source'
    )
    monkeypatch.syspath_prepend(str(root))
    original = importlib.import_module('pyKVFinder')
    origin = original.__file__
    assert origin is not None
    module = Path(origin).resolve()
    assert module.is_relative_to(root), 'Requested original source is shadowed'
    result = tmt.get_provider_output(
        str(SOURCE), method='pykvfinder', upstream_root=root, step=1.0, workers=1
    )
    submitted, dictionary = tmp_path / 'input.pdb', tmp_path / 'vdw.dat'
    submitted.write_bytes(result.run.get_artifact('input/input.pdb'))
    dictionary.write_bytes(result.run.get_artifact('input/vdw.dat'))
    direct = original.run_workflow(
        str(submitted), vdw=str(dictionary), step=1.0, nthreads=1
    )
    assert direct is not None and len(result.cavities) == len(direct.volume) == 12
    assert result.pockets == ()
    assert result.run.metadata['version'] == original.__version__
    import tomlkit

    assert result.run.metadata['tomlkit_version'] == tomlkit.__version__
    assert (
        result.run.metadata['module']['sha256']
        == hashlib.sha256(module.read_bytes()).hexdigest()
    )
    for cavity in result.cavities:
        assert (
            cavity.measurements['volume'].original_value
            == direct.volume[cavity.source_id]
        )
        assert (
            cavity.measurements['area'].original_value == direct.area[cavity.source_id]
        )
        assert cavity.fields['RESIDUES'] == direct.residues[cavity.source_id]
    bundle = tmp_path / 'original.zip'
    result.save(bundle)

    def forbidden(*args, **kwargs):
        pytest.fail('Source-bound reconstruction attempted original execution')

    monkeypatch.setattr(subprocess, 'run', forbidden)
    restored = tmt.load_provider_output(bundle, molecular_system=str(SOURCE))
    assert restored.run == result.run
    assert [record.source_id for record in restored.cavities] == list(direct.volume)


@pytest.mark.skipif(
    ROOT is None,
    reason='Set TOPOMT_PYKVFINDER_ROOT for the designated original-source gate',
)
def test_original_library_valid_empty_is_recoverable(tmp_path):
    assert ROOT is not None
    result = tmt.get_provider_output(
        str(SOURCE),
        method='pykvfinder',
        upstream_root=ROOT,
        step=1.0,
        volume_cutoff=1e9,
        workers=1,
    )
    assert result.records == ()
    assert result.run.metadata['original_empty'] is True
    bundle = tmp_path / 'empty.zip'
    result.save(bundle)
    restored = tmt.load_provider_output(bundle, molecular_system=str(SOURCE))
    assert restored.records == () and restored.run == result.run
