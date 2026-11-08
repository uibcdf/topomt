"""Reject new-provider options before optional engines or source IO."""

import importlib

import pytest
from argdigest import UnknownArgumentError

import topomt as tmt
from topomt._private.smonitor import ArgumentError


@pytest.mark.parametrize('method', ['pykvfinder', 'ghecom', 'caver', 'p2rank'])
@pytest.mark.parametrize(
    'options',
    [
        {'unknown_option': 1},
        {'workers': True},
        {'workers': 0},
        {'timeout': -1},
        {'backend': 'native'},
        {'backend': 'files', 'bundle_file': 'missing.zip', 'workers': 1},
    ],
)
def test_new_provider_admits_options_before_source_or_dependency(method, options):
    with pytest.raises((ArgumentError, UnknownArgumentError)):
        tmt.get_provider_output(object(), method=method, **options)


@pytest.mark.parametrize(
    'options',
    [
        {'probe_in': False},
        {'step': 0},
        {'probe_in': 5, 'probe_out': 4},
        {'volume_cutoff': -1},
        {'include_depth': 'yes'},
        {'max_grid_points': 0},
    ],
)
def test_pykvfinder_rejects_invalid_physical_protocol(options):
    with pytest.raises(ArgumentError):
        tmt.get_provider_output(object(), method='pykvfinder', **options)


def test_ghecom_rejects_unadmitted_morphological_mode():
    with pytest.raises(UnknownArgumentError):
        tmt.get_provider_output(object(), method='ghecom', mode='V')


@pytest.mark.parametrize('origin', [None, [1, 2], [0, 0, float('nan')], [True, 0, 0]])
def test_caver_requires_a_finite_quantity_origin(origin):
    with pytest.raises(ArgumentError):
        tmt.get_provider_output(object(), method='caver', origin=origin)


def test_custom_executable_is_the_one_checked_and_run(tmp_path, monkeypatch):
    module = importlib.import_module('topomt.third_party._execution')
    calls = []
    executable = tmp_path / 'selected engine'
    executable.write_text('#!/bin/sh\nprintf "selected"\n')
    executable.chmod(0o700)

    def check(name, **kwargs):
        calls.append(kwargs['executable'])

    monkeypatch.setattr(module, 'check_dependency', check)
    command = module.executable_command('ghecom', str(executable))
    module.run_command([command], tmp_path, timeout=3, workers=1)
    assert calls == [str(executable)]
    assert (tmp_path / 'stdout.txt').read_text() == 'selected'


@pytest.mark.parametrize('method', ['pykvfinder', 'ghecom', 'caver', 'p2rank'])
def test_new_provider_absence_precedes_source_conversion(method, monkeypatch):
    execution = importlib.import_module('topomt.third_party._execution')

    def forbidden(*args, **kwargs):
        pytest.fail('Missing engine reached molecular source conversion')

    monkeypatch.setattr(execution, 'reference_chemical_context', forbidden)
    runner = importlib.import_module(f'topomt.third_party.{method}.runner')

    def missing(options):
        raise execution.ProviderUnavailableError(
            provider=method, requirement='controlled absence'
        )

    monkeypatch.setattr(runner, 'ensure_available', missing)
    options = {}
    if method == 'caver':
        from topomt import pyunitwizard as puw

        options['origin'] = puw.quantity([0, 0, 0], 'nm')
    with pytest.raises(execution.ProviderUnavailableError, match='controlled absence'):
        tmt.get_provider_output(object(), method=method, **options)


@pytest.mark.parametrize(
    'name,fields',
    [
        (
            'ProviderExecutionError',
            {'provider': 'fixture', 'reason': 'controlled failure'},
        ),
        (
            'ProviderUnavailableError',
            {'provider': 'fixture', 'requirement': 'missing executable'},
        ),
    ],
)
def test_new_provider_diagnostics_survive_args_only_reconstruction(name, fields):
    module = importlib.import_module('topomt.third_party._execution')
    error = getattr(module, name)(**fields)
    assert type(error)(*error.args).args == error.args
