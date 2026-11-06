"""Admit original AlphaSpace2 receptor/binder options before any input work."""

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from argdigest import UnknownArgumentError

from topomt._private.smonitor import ArgumentError
from topomt.third_party.alphaspace2 import api, library, native


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
        ('min_vertices', True),
        ('min_vertices', np.bool_(True)),
        ('min_vertices', 0),
        ('min_vertices', -1),
        ('min_vertices', 1.5),
        ('min_vertices', np.nan),
        ('min_vertices', np.inf),
        ('binder_selection', True),
        ('binder_selection', ''),
        ('binder_selection', []),
        ('binder_selection', [1.5]),
        ('binder_selection', [[1]]),
        ('binder_structure_indices', True),
        ('binder_structure_indices', -1),
        ('binder_structure_indices', []),
        ('binder_structure_indices', [0, 1]),
        ('binder_structure_indices', [0.0]),
        ('binder_syntax', 1),
        ('binder_syntax', 'unknown'),
        ('skip_digestion', 1),
    ],
)
def test_original_arguments_fail_before_input_work(name, value, monkeypatch):
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    source = None if name == 'molecular_system' else object()
    options = {} if name == 'molecular_system' else {name: value}
    with pytest.raises(ArgumentError, match=name):
        library.get_topography(source, **options)


@pytest.mark.parametrize('function', [api.get_output, library.get_topography])
@pytest.mark.parametrize(
    'option', ['min_verticies', 'binder_structures', 'chemical_state']
)
def test_unknown_options_are_rejected_by_argdigest(function, option, monkeypatch):
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    with pytest.raises(UnknownArgumentError, match=option):
        function(object(), **{option: 3})


@pytest.mark.parametrize('backend', [None, True, 1, 'native', 'cli', 'files'])
def test_original_route_is_admitted_before_delegation(backend, monkeypatch):
    monkeypatch.setattr(api, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='backend'):
        api.get_output(object(), backend=backend)


@pytest.mark.parametrize('function', [api.get_topography, api.get_pockets])
@pytest.mark.parametrize('backend', [None, True, 1, 'files'])
def test_gateway_route_is_admitted_before_delegation(function, backend, monkeypatch):
    monkeypatch.setattr(library, 'get_topography', forbidden)
    monkeypatch.setattr(native, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='backend'):
        function(object(), backend=backend)


@pytest.mark.parametrize(
    'function', [api.get_output, api.get_topography, api.get_pockets]
)
def test_gateway_bypass_is_a_literal_boolean(function, monkeypatch):
    monkeypatch.setattr(library, 'get_topography', forbidden)
    monkeypatch.setattr(native, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='skip_digestion'):
        function(object(), skip_digestion=1)


@pytest.mark.parametrize(
    'backend,module', [('LIBRARY', library), ('Wrapper', library), ('NATIVE', native)]
)
def test_gateway_preserves_options_and_native_default(backend, module, monkeypatch):
    source, option, result = object(), object(), object()

    def receive(value, **options):
        assert value is source and options == {'owned_option': option}
        return result

    monkeypatch.setattr(module, 'get_topography', receive)
    assert api.get_topography(source, backend=backend, owned_option=option) is result
    if module is native:
        assert api.get_topography(source, owned_option=option) is result


@pytest.mark.parametrize(
    'function',
    [api.get_output, api.get_topography, api.get_pockets, library.get_topography],
)
def test_original_boundaries_have_auditable_plans(function):
    assert hasattr(function, 'digestion_plan')


def test_original_values_preserve_molecular_inputs_and_index_axes(
    monkeypatch, tmp_path
):
    # Real optional dependencies satisfy availability; the probe isolates only
    # argument normalization and stops at the original engine's execution call.
    pytest.importorskip('mdtraj')
    pytest.importorskip('alphaspace2')

    pdb = tmp_path / 'input.pdb'
    pdb.write_text(
        'ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C\nEND\n'
    )
    source, binder = object(), object()
    selection, frame = np.array([3]), np.array([1])
    binder_selection, binder_frame = np.array([5]), np.array([2])
    preparations = []
    original_root = tmp_path / 'original'

    class ReachedProvider(Exception):
        pass

    def prepare(value, **options):
        preparations.append((value, options))
        return pdb, np.array([3 if value is source else 5])

    class Snapshot:
        def run(self, receptor, binder):
            assert receptor.n_atoms == binder.n_atoms == 1
            raise ReachedProvider

    def original(name, *, upstream_root):
        assert name == 'alphaspace2' and upstream_root == str(original_root.resolve())
        return SimpleNamespace(Snapshot=Snapshot)

    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', prepare)
    monkeypatch.setattr(library, 'import_upstream_module', original)
    monkeypatch.setattr(library, '_patch_alphaspace2_mdtraj_sasa', lambda *a: None)
    with pytest.raises(ReachedProvider):
        library.get_topography(
            source,
            selection=selection,
            structure_indices=frame,
            syntax='molsysmt',
            upstream_root=original_root,
            min_vertices=np.int64(2),
            binder=binder,
            binder_selection=binder_selection,
            binder_structure_indices=binder_frame,
            binder_syntax='molsysmt',
        )
    assert preparations[0][0] is source and preparations[1][0] is binder
    for (_, options), selected, structure in zip(
        preparations, (selection, binder_selection), (frame, binder_frame)
    ):
        assert (
            options['selection'] is selected
            and options['structure_indices'] is structure
        )
        assert options['syntax'] == 'MolSysMT'
    np.testing.assert_array_equal(selection, [3])
    np.testing.assert_array_equal(binder_selection, [5])


@pytest.mark.parametrize('field', ['min_vertices', 'binder_structure_indices'])
def test_argument_admission_does_not_import_optional_engines(field):
    script = """
import importlib.abc
import sys
from topomt._private.smonitor import ArgumentError
from topomt.third_party.alphaspace2 import library
assert 'alphaspace2' not in sys.modules and 'mdtraj' not in sys.modules
attempts=[]
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'alphaspace2','mdtraj'}:
            attempts.append(fullname)
            raise ModuleNotFoundError(name=fullname)
sys.meta_path.insert(0,Block())
try:
    library.get_topography(object(), **{sys.argv[1]: True})
except ArgumentError:
    pass
else:
    raise AssertionError('Invalid option admitted')
assert not attempts
"""
    result = subprocess.run(
        [sys.executable, '-c', script, field],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
