"""Admit original Pocketeer arguments before dependency or molecular work."""

import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest
from argdigest import UnknownArgumentError

from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError
from topomt.third_party.pocketeer import api, library, native


def forbidden(*args, **kwargs):
    pytest.fail('Work started before argument admission.')


@pytest.mark.parametrize(
    ('name', 'value'),
    [
        ('molecular_system', None),
        ('selection', True),
        ('selection', []),
        ('selection', [1.5]),
        ('selection', [[1]]),
        ('selection', [[1], [2, 3]]),
        ('structure_indices', True),
        ('structure_indices', -1),
        ('structure_indices', []),
        ('structure_indices', [0, 1]),
        ('structure_indices', [0.0]),
        ('chemical_state', True),
        ('chemical_state', None),
        ('chemical_state', -1),
        ('chemical_state', 'structure'),
        ('syntax', 1),
        ('syntax', 'unknown'),
        ('upstream_root', 1),
        ('upstream_root', ''),
        ('upstream_root', 'bad\0path'),
        ('r_min', True),
        ('r_min', 0),
        ('r_min', -1),
        ('r_min', np.nan),
        ('r_min', np.inf),
        ('r_min', [3]),
        ('r_min', puw.quantity(1, 'ps')),
        ('r_max', 3),
        ('r_max', True),
        ('r_max', np.inf),
        ('polar_probe_radius', 0),
        ('polar_probe_radius', np.nan),
        ('sasa_threshold', 0),
        ('sasa_threshold', puw.quantity(1, 'nm')),
        ('merge_distance', -1),
        ('merge_distance', np.inf),
        ('min_spheres', True),
        ('min_spheres', 1.5),
        ('min_spheres', 0),
        ('ignore_hydrogens', 1),
        ('ignore_water', 'false'),
        ('ignore_hetero', None),
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
@pytest.mark.parametrize('option', ['r_mni', 'chemical_states'])
def test_unknown_options_are_rejected_by_argdigest(function, option, monkeypatch):
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    with pytest.raises(UnknownArgumentError, match=option):
        function(object(), **{option: 3})


@pytest.mark.parametrize('backend', [None, True, 1, 'native', 'files'])
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


def test_original_values_are_normalized_without_adding_unsupplied_options(
    monkeypatch, tmp_path
):
    pytest.importorskip('biotite')
    pytest.importorskip('pocketeer')
    pdb = tmp_path / 'input.pdb'
    pdb.write_text('ATOM      1  CA  ALA A   1       0.000   0.000   0.000\n')
    selection, frame = np.array([3, 1]), np.array([1])
    received = []

    def prepare(source, **options):
        assert (
            options['selection'] is selection and options['structure_indices'] is frame
        )
        return pdb, np.array([1, 3])

    class ReachedProvider(Exception):
        pass

    def find(array, **options):
        received.append(options)
        raise ReachedProvider

    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', prepare)
    monkeypatch.setattr(library, 'reference_chemical_context', lambda *a, **k: {})
    monkeypatch.setattr(
        library,
        'import_upstream_module',
        lambda *a, **k: SimpleNamespace(
            load_structure=lambda path: np.zeros(2), find_pockets=find
        ),
    )
    with pytest.raises(ReachedProvider):
        library.get_topography(
            object(),
            selection=selection,
            structure_indices=frame,
            r_min=puw.quantity(0.3, 'nm'),
            r_max=puw.quantity(600, 'pm'),
            sasa_threshold=puw.quantity(0.2, 'nm**2'),
            min_spheres=np.int64(5),
            merge_distance=0,
        )
    assert received == [
        {
            'r_min': pytest.approx(3),
            'r_max': pytest.approx(6),
            'sasa_threshold': pytest.approx(20),
            'min_spheres': 5,
            'merge_distance': 0,
        }
    ]
    np.testing.assert_array_equal(selection, [3, 1])
    np.testing.assert_array_equal(frame, [1])


def test_radius_range_compares_physical_values_before_input_work(monkeypatch):
    monkeypatch.setattr(library, 'prepare_wrapper_input_pdb', forbidden)
    with pytest.raises(ArgumentError, match='r_max'):
        library.get_topography(
            object(), r_min=puw.quantity(0.6, 'nm'), r_max=puw.quantity(5, 'angstroms')
        )


def test_exported_multiple_frames_fail_before_loading_provider(monkeypatch, tmp_path):
    pytest.importorskip('biotite')
    pytest.importorskip('pocketeer')
    pdb = tmp_path / 'frames.pdb'
    pdb.write_text(
        'MODEL        1\nATOM      1\nENDMDL\nMODEL        2\nATOM      1\nENDMDL\n'
    )
    monkeypatch.setattr(
        library, 'prepare_wrapper_input_pdb', lambda *a, **k: (pdb, np.array([0]))
    )
    monkeypatch.setattr(library, 'reference_chemical_context', lambda *a, **k: {})
    monkeypatch.setattr(library, 'import_upstream_module', forbidden)
    with pytest.raises(ValueError, match='exactly one'):
        library.get_topography(object(), structure_indices='all')


def test_argument_admission_does_not_import_optional_engine():
    script = """
import importlib.abc
import sys
from topomt._private.smonitor import ArgumentError
from topomt.third_party.pocketeer import library
assert 'pocketeer' not in sys.modules
attempts = []
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pocketeer', 'biotite'}:
            attempts.append(fullname)
            raise ModuleNotFoundError(name=fullname)
sys.meta_path.insert(0, Block())
try:
    library.get_topography(object(), r_min=0)
except ArgumentError:
    pass
else:
    raise AssertionError('Invalid radius was admitted')
assert not attempts
"""
    result = subprocess.run(
        [sys.executable, '-c', script],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('matching_origin', [False, True])
def test_distribution_version_requires_matching_provider_origin(
    monkeypatch, tmp_path, matching_origin
):
    from topomt.third_party import _common

    module = ModuleType('pocketeer')
    module.__file__ = str(
        tmp_path
        / ('installed' if matching_origin else 'source')
        / 'pocketeer/__init__.py'
    )
    installed = SimpleNamespace(
        version='0.4.0', locate_file=lambda name: tmp_path / 'installed' / name
    )
    monkeypatch.setattr(_common, 'distribution', lambda name: installed)
    assert _common.installed_provider_version(module) == (
        '0.4.0' if matching_origin else None
    )
