"""ArgDigest must admit the original-provider route before provider work."""

from importlib import import_module
from types import SimpleNamespace

import numpy as np
import pytest

import topomt as tmt
from topomt._private.smonitor import ArgumentError

dispatch = import_module('topomt.get_provider_output')


@pytest.fixture
def forbidden_provider(monkeypatch):
    def forbidden(name):
        pytest.fail(f'Provider imported before argument rejection: {name}')

    monkeypatch.setattr(dispatch, 'import_module', forbidden)


@pytest.mark.parametrize('method', [None, True, 1, [], {}, '', 'unknown', 'dfnd'])
def test_invalid_method_is_digested_before_provider_import(method, forbidden_provider):
    with pytest.raises(ArgumentError, match='method') as caught:
        tmt.get_provider_output(method=method)
    assert isinstance(caught.value, ValueError)


@pytest.mark.parametrize('backend', [True, 1, [], {}, 'native', 'topomt', 'unknown'])
def test_invalid_backend_is_digested_before_provider_import(
    backend, forbidden_provider
):
    with pytest.raises(ArgumentError, match='backend') as caught:
        tmt.get_provider_output(method='fpocket', backend=backend)
    assert isinstance(caught.value, ValueError)


@pytest.mark.parametrize(
    ('method', 'backend'),
    [('fpocket', 'library'), ('castp', 'cli'), ('pocketeer', 'cli')],
)
def test_incompatible_route_is_rejected_before_provider_import(
    method, backend, forbidden_provider
):
    with pytest.raises(ArgumentError, match='backend'):
        tmt.get_provider_output(method=method, backend=backend)


@pytest.mark.parametrize(
    ('method', 'backend', 'provider', 'expected', 'extra'),
    [
        ('FPOCKET4', None, 'fpocket', 'cli', {}),
        ('fpocket', 'WRAPPER', 'fpocket', 'wrapper', {}),
        ('fpocket', 'FILES', 'fpocket', 'files', {}),
        ('POCKETEER', None, 'pocketeer', 'library', {}),
        ('pocketeer', 'FILES', 'pocketeer', 'files', {}),
        ('alphaspace2', None, 'alphaspace2', 'library', {}),
        ('pycasta', None, 'pycasta', 'library', {}),
        ('pycasta', 'wrapper', 'pycasta', 'wrapper', {}),
        ('CASTP', None, 'castp', 'server', {}),
        ('CASTP3', None, 'castp', 'server', {'server': 'castp3'}),
        ('CASTPFOLD', 'FILES', 'castp', 'files', {'provider_server': 'castpfold'}),
        ('castp', 'castpfold', 'castp', 'castpfold', {}),
    ],
)
def test_dispatch_preserves_aliases_defaults_and_provider_owned_values(
    method, backend, provider, expected, extra, monkeypatch
):
    source = object()
    selection = np.array([1, 3])
    result = object()
    calls = []

    def receive(molecular_system, **kwargs):
        calls.append((molecular_system, kwargs))
        return result

    def load(name):
        assert name == f'topomt.third_party.{provider}.api'
        return SimpleNamespace(get_output=receive)

    monkeypatch.setattr(dispatch, 'import_module', load)
    assert (
        tmt.get_provider_output(
            source, method=method, backend=backend, selection=selection
        )
        is result
    )
    received_source, options = calls.pop()
    assert received_source is source
    assert options.pop('selection') is selection
    assert options == {'backend': expected, **extra}


def test_dispatch_has_auditable_argdigest_plan():
    assert hasattr(tmt.get_provider_output, 'digestion_plan')
    plan = tmt.get_provider_output.digestion_plan
    assert plan.contracts.resolve('topomt.get_provider_output.get_provider_output')


def test_castp_files_preserve_optional_source(monkeypatch):
    received = []
    monkeypatch.setattr(
        dispatch,
        'import_module',
        lambda name: SimpleNamespace(
            get_output=lambda source, **options: received.append((source, options))
        ),
    )
    tmt.get_provider_output(method='castp', backend='files', zip_file='result.zip')
    assert received == [(None, {'backend': 'files', 'zip_file': 'result.zip'})]


def test_invalid_method_precedes_backend_validation(forbidden_provider):
    with pytest.raises(ArgumentError, match='method'):
        tmt.get_provider_output(method=[], backend=[])


def test_dispatch_does_not_rewrite_provider_option_names(monkeypatch):
    received = []
    monkeypatch.setattr(
        dispatch,
        'import_module',
        lambda name: SimpleNamespace(
            get_output=lambda source, **options: received.append(options)
        ),
    )
    tmt.get_provider_output(method='pocketeer', engine='upstream', structure_index=1)
    assert received == [
        {'backend': 'library', 'engine': 'upstream', 'structure_index': 1}
    ]
