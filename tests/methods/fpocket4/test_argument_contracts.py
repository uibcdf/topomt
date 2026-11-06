"""Original fpocket inputs must be digested before molecular or file work."""

from pathlib import Path

import numpy as np
import pytest
from argdigest import UnknownArgumentError

from topomt._private.smonitor import ArgumentError
from topomt.third_party.fpocket import api, cli, files


def forbidden(*args, **kwargs):
    pytest.fail('Input work started before argument rejection.')


@pytest.mark.parametrize(
    ('name', 'value'),
    [
        ('selection', True),
        ('selection', [1.5]),
        ('selection', [[1]]),
        ('selection', [[1], [2, 3]]),
        ('selection', []),
        ('structure_indices', True),
        ('structure_indices', [0.0]),
        ('structure_indices', [[0]]),
        ('structure_indices', [0, 1]),
        ('structure_indices', -1),
        ('syntax', 1),
        ('syntax', 'unknown'),
        ('fpocket_cmd', ''),
        ('fpocket_cmd', 1),
        ('extra_args', '-m 3'),
        ('extra_args', ['-m', 3]),
        ('chemical_state', True),
        ('chemical_state', None),
        ('chemical_state', 0.5),
        ('chemical_state', 'structure'),
        ('skip_digestion', 1),
    ],
)
def test_cli_invalid_values_fail_before_source_work(name, value, monkeypatch):
    monkeypatch.setattr(cli, '_chemical_context', forbidden)
    with pytest.raises(ArgumentError, match=name):
        cli.get_topography(object(), **{name: value})


@pytest.mark.parametrize(
    ('name', 'value'),
    [
        ('pdb_file', None),
        ('pdb_file', []),
        ('output_dir', ''),
        ('output_dir', 1),
        ('provider_metadata', []),
        ('provider_metadata', {'selection': 'forged'}),
        ('provider_metadata', {'submitted_atom_indices': [999]}),
        ('submitted_atom_indices', [True]),
        ('submitted_atom_indices', [1.5]),
        ('submitted_atom_indices', [0, 0]),
        ('submitted_atom_indices', [-1]),
        ('chemical_state_context', {}),
        ('chemical_state_context', {'index': True}),
        ('chemical_state_context', []),
        ('chemical_state', True),
        ('backend', 'native'),
    ],
)
def test_files_invalid_values_fail_before_parsing(name, value, monkeypatch):
    monkeypatch.setattr(files, 'parse_fpocket_output', forbidden)
    options = {'pdb_file': 'input.pdb', 'output_dir': 'input_out', name: value}
    with pytest.raises(ArgumentError, match=name):
        files.load_topography(object(), **options)


@pytest.mark.parametrize('backend', ['cli', 'FiLeS'])
def test_api_rejects_unknown_keywords_before_delegation(backend, monkeypatch):
    monkeypatch.setattr(api, 'get_topography', forbidden)
    monkeypatch.setattr(api, 'load_topography', forbidden)
    with pytest.raises(UnknownArgumentError, match='strucuture_indices'):
        api.get_output(object(), backend=backend, strucuture_indices=0)


@pytest.mark.parametrize('route', [cli.get_topography, files.load_topography])
def test_closed_routes_reject_unknown_keywords_through_argdigest(route):
    options = {'strucuture_indices': 0}
    if route is files.load_topography:
        options.update(pdb_file='in.pdb', output_dir='out')
    with pytest.raises(UnknownArgumentError, match='strucuture_indices'):
        route(object(), **options)


@pytest.mark.parametrize('backend', [None, 1, True, 'native'])
def test_original_api_backend_is_digested_before_delegation(backend, monkeypatch):
    monkeypatch.setattr(api, 'get_topography', forbidden)
    monkeypatch.setattr(api, 'load_topography', forbidden)
    with pytest.raises(ArgumentError, match='backend'):
        api.get_output(object(), backend=backend)


def test_files_preserve_legacy_omission_and_normalize_explicit_map(monkeypatch):
    source, parsed, result = object(), object(), object()
    received = []
    monkeypatch.setattr(files, 'parse_fpocket_output', lambda *args: parsed)

    def build(molecular_system, fpocket_result, **options):
        assert molecular_system is source and fpocket_result is parsed
        received.append(options)
        return result

    monkeypatch.setattr(files, 'fpocket_result_to_topography', build)
    indices = np.array([3, 1])
    metadata = {'note': 'pilot'}
    assert (
        files.load_topography(
            source,
            pdb_file='in.pdb',
            output_dir=Path('out'),
            submitted_atom_indices=indices,
            provider_metadata=metadata,
        )
        is result
    )
    assert received[0]['chemical_state'] is None
    assert received[0]['chemical_state_context'] is None
    assert received[0]['provider_metadata'] is metadata
    assert list(received[0]['submitted_atom_indices']) == [3, 1]
    np.testing.assert_array_equal(indices, [3, 1])


def test_cli_digests_values_without_mutating_array_inputs(monkeypatch, tmp_path):
    source, result = object(), object()
    selection, frame = np.array([3, 1]), np.array([1])
    monkeypatch.setattr(cli, '_chemical_context', lambda *args: {})

    def prepare(molecular_system, **options):
        assert molecular_system is source
        assert (
            options['selection'] is selection and options['structure_indices'] is frame
        )
        assert options['syntax'] == 'MolSysMT' and options['chemical_state'] == 1
        return tmp_path / 'in.pdb', np.array([1, 3])

    def run(path, **options):
        assert options['fpocket_cmd'] == 'custom-fpocket'
        assert options['extra_args'] == ['-m', '3']
        return tmp_path / 'out'

    monkeypatch.setattr(cli, '_prepare_fpocket_input', prepare)
    monkeypatch.setattr(cli, 'run_fpocket', run)
    monkeypatch.setattr(cli.shutil, 'which', lambda cmd: None)

    def recover(*args, **options):
        assert options['skip_digestion'] is True
        return result

    monkeypatch.setattr(cli, 'load_fpocket_topography', recover)
    assert (
        cli.get_topography(
            source,
            selection=selection,
            structure_indices=frame,
            syntax='molsysmt',
            chemical_state=np.int64(1),
            fpocket_cmd='custom-fpocket',
            extra_args=('-m', '3'),
        )
        is result
    )
    np.testing.assert_array_equal(selection, [3, 1])
    np.testing.assert_array_equal(frame, [1])


@pytest.mark.parametrize(
    'function', [api.get_output, cli.get_topography, files.load_topography]
)
def test_original_routes_have_argdigest_plans(function):
    assert hasattr(function, 'digestion_plan')
