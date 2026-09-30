"""Optional engines fail at their boundary without disabling other backends."""

import importlib
import subprocess
import sys
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import SimpleNamespace

import depdigest.core.decorator as dependency_decorator
import numpy as np
import pytest

from topomt._private.smonitor import LibraryNotFoundError

PROVIDERS = ('pocketeer', 'alphaspace2', 'pycasta')


def test_external_input_rejects_empty_selection_before_writing(monkeypatch, tmp_path):
    from topomt.third_party import _common

    def convert(*args, to_form, **kwargs):
        assert to_form == 'molsysmt.MolSys'
        return object()

    monkeypatch.setattr(_common.msm, 'convert', convert)
    monkeypatch.setattr(_common.msm, 'select', lambda *args, **kwargs: [])
    with pytest.raises(ValueError, match='empty atom selection'):
        _common.prepare_wrapper_input_pdb(None, tmpdir=tmp_path)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('frame_index', [0, 1])
def test_external_input_selects_one_pdb_frame_without_optional_engines(
    tmp_path, frame_index
):
    from topomt.third_party._common import prepare_wrapper_input_pdb

    source = Path('topomt/data/fpocket4/sample/1GG0.pdb')
    first = [
        line for line in source.read_text().splitlines() if line.startswith('ATOM  ')
    ][:4]
    second = [f'{line[:30]}{float(line[30:38]) + 10:8.3f}{line[38:]}' for line in first]
    trajectory = tmp_path / 'trajectory.pdb'
    trajectory.write_text(
        'MODEL        1\n' + '\n'.join(first) + '\nENDMDL\n'
        'MODEL        2\n' + '\n'.join(second) + '\nENDMDL\nEND\n'
    )
    submitted_dir = tmp_path / 'submitted'
    submitted_dir.mkdir()
    submitted, indices = prepare_wrapper_input_pdb(
        str(trajectory),
        tmpdir=submitted_dir,
        structure_indices=np.array([frame_index]),
    )
    atoms = [
        line for line in submitted.read_text().splitlines() if line.startswith('ATOM  ')
    ]
    assert indices.tolist() == [0, 1, 2, 3]
    assert len(atoms) == 4
    expected = first if frame_index == 0 else second
    assert [float(line[30:38]) for line in atoms] == pytest.approx(
        [float(line[30:38]) for line in expected]
    )


@pytest.mark.parametrize('provider', PROVIDERS)
def test_original_engines_are_soft_dependencies(provider):
    from topomt._depdigest import LIBRARIES

    assert LIBRARIES[provider] == {'type': 'soft', 'pypi': provider, 'conda': None}


@pytest.mark.parametrize('provider', PROVIDERS)
def test_missing_engine_fails_before_input_conversion(monkeypatch, provider):
    library = importlib.import_module(f'topomt.third_party.{provider}.library')

    def check(module_name, **kwargs):
        if module_name == provider:
            raise LibraryNotFoundError(library=provider)

    monkeypatch.setattr(dependency_decorator, 'check_dependency', check)
    with pytest.raises(LibraryNotFoundError) as caught:
        library.get_topography(None)

    assert caught.value.code == 'LibraryNotFoundError'
    assert provider in str(caught.value)
    assert f'pip install {provider}' in str(caught.value)


@pytest.mark.parametrize('provider', PROVIDERS)
def test_source_checkout_does_not_require_installed_provider(monkeypatch, provider):
    library = importlib.import_module(f'topomt.third_party.{provider}.library')
    checked = []

    def check(module_name, **kwargs):
        checked.append(module_name)
        assert module_name != provider

    def stop_at_input(*args, **kwargs):
        raise RuntimeError('input boundary reached')

    monkeypatch.setattr(dependency_decorator, 'check_dependency', check)
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', stop_at_input)
    with pytest.raises(RuntimeError, match='input boundary reached'):
        library.get_topography(None, upstream_root='/explicit/source')


def test_import_topomt_does_not_import_original_engines():
    code = """
import importlib.abc
import sys

class BlockEngines(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pocketeer', 'alphaspace2', 'pycasta'}:
            raise AssertionError(f'Eager engine import: {fullname}')

sys.meta_path.insert(0, BlockEngines())
import topomt
assert not {'pocketeer', 'alphaspace2', 'pycasta'} & set(sys.modules)
"""
    result = subprocess.run(
        [sys.executable, '-c', code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize('collect_only', [True, False])
def test_provider_tests_do_not_require_optional_engines(collect_only):
    code = """
import importlib.abc
import sys
import pytest

class MissingEngines(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'mdtraj', 'alphaspace2', 'pocketeer', 'pycasta'}:
            raise ModuleNotFoundError(f'No module named {fullname!r}', name=fullname)

sys.meta_path.insert(0, MissingEngines())
"""
    if collect_only:
        nodes = [
            '--collect-only',
            'tests/methods/alphaspace2',
            'tests/methods/pocketeer',
            'tests/methods/pycasta',
            'tests/methods/test_installed_engines.py',
        ]
    else:
        nodes = [
            'tests/methods/pycasta/test_provider_pycasta.py::test_pycasta_atom_mapping_skips_interleaved_hetatm',
            'tests/methods/pycasta/test_provider_pycasta.py::test_pycasta_atom_mapping_rejects_coordinate_mismatch',
            'tests/methods/alphaspace2/test_parity.py::test_digest_binder_coords_accepts_array_like_shape_n_by_3',
            'tests/methods/alphaspace2/test_wrapper_alphaspace2.py::test_alphaspace2_wrapper_smoke_on_demo_system',
            'tests/methods/alphaspace2/test_parity.py::test_alphaspace2_native_grid_volume_matches_helper',
        ]
    arguments = ['-o', 'addopts=--doctest-modules', '-q', *nodes]
    code += f'raise SystemExit(pytest.main({arguments!r}))\n'
    result = subprocess.run(
        [sys.executable, '-c', code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    if not collect_only:
        assert '3 passed, 2 skipped' in result.stdout


def test_upstream_import_preserves_missing_transitive_dependency(monkeypatch):
    from topomt.third_party import _common

    original = ModuleNotFoundError("No module named 'internal_dependency'")
    original.name = 'internal_dependency'

    def broken_import(name):
        raise original

    monkeypatch.setattr(_common, 'import_module', broken_import)
    with pytest.raises(ModuleNotFoundError) as caught:
        _common.import_upstream_module('pocketeer', upstream_root='/source')
    assert caught.value is original


def test_source_import_restores_search_path(tmp_path):
    from topomt.third_party._common import import_upstream_module

    (tmp_path / 'topomt_test_engine.py').write_text('value = 42\n')
    before = sys.path.copy()
    try:
        module = import_upstream_module('topomt_test_engine', upstream_root=tmp_path)
        assert module.value == 42
        assert sys.path == before
    finally:
        sys.modules.pop('topomt_test_engine', None)


def test_pycasta_resolves_installed_namespace_without_importing_scripts(
    monkeypatch, tmp_path
):
    from topomt.third_party.pycasta import library

    package_root = tmp_path / 'pycasta'
    package_root.mkdir()
    (package_root / 'run_analysis.py').write_text(
        'raise AssertionError("parent import")'
    )
    spec = ModuleSpec('pycasta', loader=None, is_package=True)
    spec.submodule_search_locations = [str(package_root)]
    monkeypatch.setattr(library, 'find_spec', lambda name: spec)

    assert library._get_source_root(None) == package_root


def test_fpocket_missing_executable_has_installation_hint(tmp_path):
    from topomt.third_party.fpocket.runner import FpocketError, run_fpocket

    missing = str(tmp_path / 'missing_fpocket')
    with pytest.raises(FpocketError) as caught:
        run_fpocket(tmp_path / 'input.pdb', fpocket_cmd=missing)
    assert caught.value.code == 'ExecutableNotFoundError'
    assert caught.value.extra['executable'] == missing
    assert 'conda install -c conda-forge fpocket' in str(caught.value)


def test_library_exception_accepts_args_reconstruction():
    error = LibraryNotFoundError(library='pocketeer')
    rebuilt = type(error)(*error.args)
    assert rebuilt.args == error.args


def test_catalog_codes_render_dependency_diagnostics():
    from smonitor import resolve

    from topomt._private.smonitor import CATALOG, CODES

    for group in ('exceptions', 'warnings'):
        for entry in CATALOG[group].values():
            assert entry['code'] in CODES
    text, hint = resolve(code='LibraryNotFoundError', extra={'library': 'pocketeer'})
    assert 'pocketeer' in text
    assert 'pip install pocketeer' in hint


def test_alphaspace2_unbound_contacts_leave_geometry_unchanged():
    from topomt.third_party.alphaspace2.library import _initialize_unbound_contacts

    coordinates = np.asarray([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    snapshot = SimpleNamespace(
        _alpha_xyz=coordinates,
        _alpha_contact=None,
        _beta_alpha_index_list=[[0], [1]],
        _beta_contact=None,
        _pocket_alpha_index_list=[[0, 1]],
        _pocket_contact=None,
    )
    assert _initialize_unbound_contacts(snapshot) is True
    assert snapshot._alpha_xyz is coordinates
    assert snapshot._alpha_contact.tolist() == [False, False]
    assert snapshot._beta_contact.tolist() == [False, False]
    assert snapshot._pocket_contact.tolist() == [False]
    snapshot._alpha_contact[0] = True
    assert _initialize_unbound_contacts(snapshot) is False
    assert snapshot._alpha_contact[0]
