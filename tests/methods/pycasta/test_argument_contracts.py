"""Admit original pyCASTA options before dependency, input or recovery work."""

import subprocess
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest
from argdigest import UnknownArgumentError
from depdigest.core import decorator as dependency_decorator

from topomt._private.smonitor import ArgumentError
from topomt.third_party.pycasta import api, library, native


def forbidden(*args, **kwargs):
    pytest.fail('Work started before argument admission.')


@pytest.mark.parametrize(
    ('name', 'value'),
    [
        ('molecular_system', None),
        ('selection', True),
        ('selection', ''),
        ('selection', []),
        ('selection', [1.5]),
        ('selection', [[1]]),
        ('selection', [[1], [2, 3]]),
        ('structure_indices', True),
        ('structure_indices', -1),
        ('structure_indices', []),
        ('structure_indices', [0, 1]),
        ('structure_indices', [0.0]),
        ('syntax', 1),
        ('syntax', 'unknown'),
        ('upstream_root', 1),
        ('upstream_root', ''),
        ('upstream_root', 'bad\0path'),
        ('chemical_state', True),
        ('chemical_state', None),
        ('chemical_state', -1),
        ('chemical_state', 'structure'),
        ('skip_digestion', 1),
    ],
)
def test_original_arguments_fail_before_dependency_or_input_work(
    name, value, monkeypatch
):
    monkeypatch.setattr(dependency_decorator, 'check_dependency', forbidden)
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    source = None if name == 'molecular_system' else object()
    options = {} if name == 'molecular_system' else {name: value}
    with pytest.raises(ArgumentError, match=name):
        library.get_topography(source, **options)


@pytest.mark.parametrize('option', ['chemical_states', 'alpha', 'bundle_file'])
def test_library_rejects_unowned_options_before_dependency_work(option, monkeypatch):
    monkeypatch.setattr(dependency_decorator, 'check_dependency', forbidden)
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    with pytest.raises(UnknownArgumentError, match=option):
        library.get_topography(object(), **{option: 3})


@pytest.mark.parametrize(
    'function', [api.get_output, api.get_topography, api.get_pockets]
)
@pytest.mark.parametrize('backend', [None, True, 1, [], {}, '', 'cli', 'unknown'])
def test_invalid_routes_fail_before_delegation(function, backend, monkeypatch):
    monkeypatch.setattr(library, 'get_topography', forbidden)
    monkeypatch.setattr(native, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='backend'):
        function(object(), backend=backend)


@pytest.mark.parametrize('backend', ['native', 'topomt'])
def test_original_output_refuses_local_routes(backend, monkeypatch):
    monkeypatch.setattr(api, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='backend'):
        api.get_output(object(), backend=backend)


@pytest.mark.parametrize('function', [api.get_topography, api.get_pockets])
def test_legacy_topography_gateway_does_not_add_saved_backend(function, monkeypatch):
    monkeypatch.setattr(library, 'get_topography', forbidden)
    monkeypatch.setattr(native, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='backend'):
        function(object(), backend='files', bundle_file='run.zip')


@pytest.mark.parametrize(
    'function', [api.get_output, api.get_topography, api.get_pockets]
)
def test_gateway_bypass_requires_literal_boolean(function, monkeypatch):
    monkeypatch.setattr(library, 'get_topography', forbidden)
    monkeypatch.setattr(native, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='skip_digestion'):
        function(object(), skip_digestion=1)


@pytest.mark.parametrize(
    'function', [api.get_output, api.get_topography, api.get_pockets]
)
@pytest.mark.parametrize('backend', ['library', 'Wrapper'])
@pytest.mark.parametrize('option', ['chemical_states', 'alpha', 'bundle_file'])
def test_original_routes_reject_unowned_options_before_delegation(
    function, backend, option, monkeypatch
):
    monkeypatch.setattr(library, 'get_topography', forbidden)
    with pytest.raises(UnknownArgumentError, match=option):
        function(object(), backend=backend, **{option: 3})


@pytest.mark.parametrize(
    'option',
    ['selection', 'structure_indices', 'syntax', 'upstream_root', 'chemical_state'],
)
@pytest.mark.parametrize('backend', ['files', 'FILES'])
def test_saved_route_rejects_runtime_overrides_before_reader_import(
    option, backend, monkeypatch
):
    reader = ModuleType('topomt.third_party.pycasta.files')
    reader.load_output = forbidden
    monkeypatch.setitem(sys.modules, reader.__name__, reader)
    with pytest.raises(UnknownArgumentError, match=option):
        api.get_output(
            object(), backend=backend, bundle_file='run.zip', **{option: None}
        )


def test_saved_route_requires_bundle_before_reader_import(monkeypatch):
    reader = ModuleType('topomt.third_party.pycasta.files')
    reader.load_output = forbidden
    monkeypatch.setitem(sys.modules, reader.__name__, reader)
    with pytest.raises(ArgumentError, match='bundle_file'):
        api.get_output(object(), backend='files')


def test_saved_route_preserves_source_and_bundle(monkeypatch, tmp_path):
    source, result = object(), object()
    bundle = tmp_path / 'saved.zip'
    reader = ModuleType('topomt.third_party.pycasta.files')

    def load(value, **options):
        assert value is source and options == {'bundle_file': bundle}
        return result

    reader.load_output = load
    monkeypatch.setitem(sys.modules, reader.__name__, reader)
    assert api.get_output(source, backend='FILES', bundle_file=bundle) is result


@pytest.mark.parametrize('backend', ['library', 'Wrapper'])
def test_gateway_preserves_original_molecular_values(backend, monkeypatch, tmp_path):
    source, result = object(), object()
    selection, frame = np.array([3, 1]), np.array([2])
    root = tmp_path / 'original'

    def receive(value, **options):
        assert value is source
        assert options['selection'] is selection
        assert options['structure_indices'] is frame
        assert options['upstream_root'] is root
        assert options['syntax'] == 'molsysmt'
        assert options['chemical_state'] == 1
        assert set(options) == {
            'selection',
            'structure_indices',
            'syntax',
            'upstream_root',
            'chemical_state',
        }
        return result

    monkeypatch.setattr(library, 'get_topography', receive)
    assert (
        api.get_topography(
            source,
            backend=backend,
            selection=selection,
            structure_indices=frame,
            syntax='molsysmt',
            upstream_root=root,
            chemical_state=1,
        )
        is result
    )
    np.testing.assert_array_equal(selection, [3, 1])
    np.testing.assert_array_equal(frame, [2])


def test_native_gateway_retains_owned_options_and_default(monkeypatch):
    source, option, result = object(), object(), object()

    def receive(value, **options):
        assert value is source and options == {'owned_option': option}
        return result

    monkeypatch.setattr(native, 'get_topography', receive)
    assert api.get_topography(source, owned_option=option) is result
    assert api.get_topography(source, backend='NATIVE', owned_option=option) is result


@pytest.mark.parametrize(
    'function',
    [api.get_output, api.get_topography, api.get_pockets, library.get_topography],
)
def test_original_boundaries_have_auditable_plans(function):
    assert hasattr(function, 'digestion_plan')


def test_invalid_admission_does_not_probe_original_engine():
    script = """
import importlib.abc
import sys
from topomt._private.smonitor import ArgumentError
from topomt.third_party.pycasta import library
assert 'pycasta' not in sys.modules
attempts=[]
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] == 'pycasta':
            attempts.append(fullname)
            raise AssertionError('Original engine was probed')
sys.meta_path.insert(0, Block())
try:
    library.get_topography(object(), structure_indices=[0, 1])
except ArgumentError:
    pass
else:
    raise AssertionError('Invalid frame axis was admitted')
assert not attempts
"""
    result = subprocess.run(
        [sys.executable, '-B', '-c', script],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
