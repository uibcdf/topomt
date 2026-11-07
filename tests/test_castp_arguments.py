"""CASTp raw and saved admission precedes provider or file work."""

from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from argdigest import UnknownArgumentError

import topomt as tmt
from topomt._private.arg_digestion import arg_digest
from topomt._private.smonitor import ArgumentError


def boundary(kind):
    from topomt._private.arg_digestion.castp_arguments import (
        API_CALLER,
        FILES_CALLER,
        OPTIONS,
        ORIGINAL_PIPELINES,
        RECOVERY_CALLER,
    )

    seen = []
    if kind == 'api':

        def function(
            molecular_system=None, *, backend='server', skip_digestion=False, **kwargs
        ):
            seen.append((molecular_system, backend, kwargs))
            return seen[-1]

        caller = API_CALLER
        options = {**OPTIONS, 'argument_digestion': False, 'map': ORIGINAL_PIPELINES}
    elif kind == 'raw':

        def function(
            molecular_system=None,
            *,
            source_atom_indices=None,
            selection='all',
            structure_indices=0,
            syntax='MolSysMT',
            chemical_state='reference',
            skip_digestion=False,
            **rawkwargs,
        ):
            seen.append((molecular_system, source_atom_indices, rawkwargs))
            return seen[-1]

        caller, options = FILES_CALLER, OPTIONS
    else:

        def function(
            molecular_system, *, bundle_file, provider_server=None, skip_digestion=False
        ):
            seen.append((molecular_system, bundle_file, provider_server))
            return seen[-1]

        caller, options = RECOVERY_CALLER, OPTIONS
    function.__module__, function.__name__ = caller.rsplit('.', 1)
    function.__qualname__ = function.__name__
    return arg_digest(**options)(function), seen


@pytest.mark.parametrize(
    'backend', [None, True, 1, [], {}, '', 'native', 'library', 'unknown']
)
def test_invalid_original_route_is_rejected_before_body(backend):
    call, seen = boundary('api')
    with pytest.raises(ArgumentError, match='backend'):
        call(object(), backend=backend)
    assert not seen


@pytest.mark.parametrize(
    'value', [True, 1, np.array(1), [True], [1.0], [[1]], [1, -1], [1, 1], [1, False]]
)
def test_source_atom_map_rejects_noninteger_or_nonunique_axes(value):
    call, seen = boundary('raw')
    with pytest.raises(ArgumentError, match='source_atom_indices'):
        call(object(), source_atom_indices=value)
    assert not seen


@pytest.mark.parametrize('value', [None, [4, 1, 3], (4, 1, 3), np.array([4, 1, 3])])
def test_source_atom_map_preserves_declared_row_order(value):
    call, seen = boundary('raw')
    source = object()
    output = call(source, source_atom_indices=value, zip_file='original.zip')
    assert output[0] is source and output[1] is value
    assert output[2]['zip_file'] == Path('original.zip') and seen


@pytest.mark.parametrize('backend', ['files', 'FILES'])
@pytest.mark.parametrize(
    'name',
    [
        'source_atom_indices',
        'selection',
        'structure_indices',
        'syntax',
        'chemical_state',
        'zip_file',
        'dir_path',
        'poc_file',
        'pdb_file',
        'probe_radius',
        'provider_metadata',
    ],
)
def test_saved_route_rejects_raw_and_source_context_overrides(backend, name):
    call, seen = boundary('api')
    with pytest.raises(ArgumentError, match=name):
        call(object(), backend=backend, bundle_file='saved.zip', **{name: None})
    assert not seen


@pytest.mark.parametrize('kind', ['api', 'raw', 'saved'])
@pytest.mark.parametrize('value', [1, None, 'yes', []])
def test_bypass_requires_literal_boolean(kind, value):
    call, seen = boundary(kind)
    options = {'bundle_file': 'saved.zip'} if kind == 'saved' else {}
    with pytest.raises(ArgumentError, match='skip_digestion'):
        call(object(), skip_digestion=value, **options)
    assert not seen


@pytest.mark.parametrize('kind', ['api', 'saved'])
def test_saved_recovery_requires_source_before_body(kind):
    call, seen = boundary(kind)
    options = {'backend': 'files'} if kind == 'api' else {}
    with pytest.raises(ArgumentError, match='molecular_system'):
        call(None, bundle_file='saved.zip', **options)
    assert not seen


@pytest.mark.parametrize('value', [None, '', True, 1, 'bad\0path'])
def test_saved_bundle_path_is_validated_before_body(value):
    call, seen = boundary('saved')
    with pytest.raises(ArgumentError, match='bundle_file'):
        call(object(), bundle_file=value)
    assert not seen


@pytest.mark.parametrize('kind', ['api', 'saved'])
def test_saved_route_admits_source_bundle_and_server_identity(kind):
    call, seen = boundary(kind)
    source, bundle = object(), Path('saved.zip')
    if kind == 'api':
        output = call(
            source, backend='FILES', bundle_file=bundle, provider_server='castpfold'
        )
        assert output == (
            source,
            'files',
            {'bundle_file': bundle, 'provider_server': 'castpfold'},
        )
    else:
        output = call(source, bundle_file=str(bundle), provider_server='castpfold')
        assert output == (source, bundle, 'castpfold')
    assert seen


def test_raw_archive_source_is_optional_and_individual_options_remain_available():
    call, seen = boundary('raw')
    output = call(
        None,
        pocInfo_file='table.pocInfo',
        provider_server='castp3',
        provider_metadata={'declared': True},
    )
    assert output[0] is None and output[2]['pocInfo_file'] == Path('table.pocInfo')
    assert output[2]['provider_metadata'] == {'declared': True} and seen


@pytest.mark.parametrize('kind', ['api', 'raw'])
def test_private_capture_hooks_are_not_public_options(kind):
    call, seen = boundary(kind)
    options = {'backend': 'files'} if kind == 'api' else {}
    with pytest.raises(UnknownArgumentError, match='_provider_run'):
        call(None, _provider_run=object(), **options)
    assert not seen


def test_api_normalizes_only_backend_and_preserves_provider_values():
    call, _ = boundary('api')
    source, indices = object(), np.array([3, 1])
    output = call(
        source, backend='FILES', zip_file='original.zip', source_atom_indices=indices
    )
    assert output[0] is source and output[1] == 'files'
    assert output[2]['source_atom_indices'] is indices
    assert output[2]['zip_file'] == 'original.zip'


@pytest.mark.parametrize('backend', ['server', 'castpfold'])
def test_original_server_options_are_admitted_without_work(backend):
    call, seen = boundary('api')
    source = object()
    options = dict(
        server='castp3',
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
        probe_radius=1.4,
        email='N/A',
        wait=0,
        extra_wait=0,
        retries=0,
        timeout=30,
        output_zip_file='result.zip',
    )
    output = call(source, backend=backend, **options)
    assert output == (source, backend, options) and seen


@pytest.mark.parametrize('kind', ['api', 'raw', 'saved'])
def test_contract_plans_are_auditable(kind):
    call, _ = boundary(kind)
    assert hasattr(call, 'digestion_plan')


@pytest.mark.parametrize(
    'method,conflict', [('castp3', 'castpfold'), ('castpfold', 'castp3')]
)
def test_real_file_alias_conflict_precedes_provider_import(
    method, conflict, monkeypatch
):
    dispatch = import_module('topomt.get_provider_output')

    def forbidden(name):
        pytest.fail('Provider import preceded CASTp file-alias conflict admission.')

    monkeypatch.setattr(dispatch, 'import_module', forbidden)
    with pytest.raises(ValueError, match='[Ss]erver'):
        tmt.get_provider_output(
            method=method,
            backend='files',
            zip_file='not-opened.zip',
            provider_server=conflict,
        )


@pytest.mark.parametrize('method', ['castp3', 'castpfold'])
def test_real_file_alias_matching_server_reaches_provider_unchanged(
    method, monkeypatch
):
    dispatch = import_module('topomt.get_provider_output')
    received, result = [], object()

    def receive(source, **options):
        received.append((source, options))
        return result

    def provider(name):
        assert name == 'topomt.third_party.castp.api'
        return SimpleNamespace(get_output=receive)

    monkeypatch.setattr(dispatch, 'import_module', provider)
    assert (
        tmt.get_provider_output(
            method=method,
            backend='files',
            zip_file='not-opened.zip',
            provider_server=method,
        )
        is result
    )
    assert received == [
        (
            None,
            {
                'backend': 'files',
                'zip_file': 'not-opened.zip',
                'provider_server': method,
            },
        )
    ]


@pytest.mark.parametrize(
    'options',
    [
        {'selection': np.array([0, 1])},
        {'structure_indices': 1},
    ],
    ids=['selection-array', 'nonzero-frame'],
)
def test_actual_raw_leaf_refuses_unbound_selectors_before_file_io(tmp_path, options):
    from topomt.third_party.castp.files import load_output

    missing = tmp_path / 'not-opened.zip'
    assert not missing.exists()
    with pytest.raises(ValueError, match='CASTp source selectors require'):
        load_output(None, zip_file=missing, **options)


@pytest.mark.parametrize(
    'method,options',
    [
        ('castp3', {}),
        ('castp', {'server': 'castp3'}),
    ],
    ids=['castp3-alias-versus-fold-backend', 'explicit-castp3-versus-fold-backend'],
)
def test_real_original_routes_reject_conflicting_server_before_provider_import(
    method, options, monkeypatch
):
    dispatch = import_module('topomt.get_provider_output')

    def forbidden(name):
        pytest.fail(
            'Provider import preceded contradictory CASTp server-route admission.'
        )

    monkeypatch.setattr(dispatch, 'import_module', forbidden)
    with pytest.raises(ValueError):
        tmt.get_provider_output(object(), method=method, backend='castpfold', **options)
