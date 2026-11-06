"""Public fpocket gateways validate routing without changing backend ownership."""

from types import SimpleNamespace

import pytest
from argdigest import UnknownArgumentError

from topomt._private.smonitor import ArgumentError
from topomt.third_party.fpocket import api, cli, files, native
from topomt.third_party.fpocket import topomt as variant


def forbidden(*args, **kwargs):
    pytest.fail('A backend was entered before routing admission.')


@pytest.mark.parametrize('function', [api.get_topography, api.get_pockets])
@pytest.mark.parametrize('backend', [None, True, 1, [], 'files', 'unknown'])
def test_invalid_gateway_backend_fails_before_delegation(
    function, backend, monkeypatch
):
    for module in (cli, native, variant):
        monkeypatch.setattr(module, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='backend'):
        function(object(), backend=backend)


@pytest.mark.parametrize('function', [api.get_topography, api.get_pockets])
@pytest.mark.parametrize(
    'backend,module',
    [('CLI', cli), ('Wrapper', cli), ('NATIVE', native), ('TopoMT', variant)],
)
def test_gateway_preserves_backend_and_owned_options(
    function, backend, module, monkeypatch
):
    source, option = object(), object()
    result = SimpleNamespace(get_features=lambda **kwargs: ['pocket'])

    def receive(molecular_system, **options):
        assert molecular_system is source
        assert options == {'backend_option': option}
        return result

    monkeypatch.setattr(module, 'get_topography', receive)
    actual = function(source, backend=backend, backend_option=option)
    assert actual is result if function is api.get_topography else actual == ['pocket']


def test_files_gateway_rejects_unknown_names_before_delegation(monkeypatch):
    monkeypatch.setattr(files, 'load_topography', forbidden)
    with pytest.raises(UnknownArgumentError, match='strucuture_indices'):
        api.load_topography(
            object(), pdb_file='in.pdb', output_dir='out', strucuture_indices=0
        )


@pytest.mark.parametrize(
    'function', [api.get_topography, api.get_pockets, api.load_topography]
)
def test_public_gateway_has_auditable_plan(function):
    assert hasattr(function, 'digestion_plan')


@pytest.mark.parametrize('function', [api.get_topography, api.get_pockets])
def test_gateway_rejects_nonboolean_bypass(function):
    with pytest.raises(ArgumentError, match='skip_digestion'):
        function(object(), skip_digestion=1)


def test_files_wrapper_preserves_values_for_owning_loader(monkeypatch):
    source, metadata, result = object(), {'note': 'pilot'}, object()

    def receive(molecular_system, *, pdb_file, output_dir, provider_metadata):
        assert molecular_system is source and provider_metadata is metadata
        assert pdb_file == 'in.pdb' and output_dir == 'out'
        return result

    monkeypatch.setattr(files, 'load_topography', receive)
    assert (
        api.load_topography(
            source, pdb_file='in.pdb', output_dir='out', provider_metadata=metadata
        )
        is result
    )


def test_output_rejects_nonboolean_bypass_before_delegation(monkeypatch):
    monkeypatch.setattr(api, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='skip_digestion'):
        api.get_output(object(), skip_digestion=1)


def test_output_internal_bypass_is_consumed_once(monkeypatch):
    from topomt.third_party import output

    result = object()

    def receive(source, *, backend, skip_digestion):
        assert backend == 'cli' and skip_digestion is True
        return result

    monkeypatch.setattr(api, 'get_topography', receive)
    monkeypatch.setattr(output, '_from_topography', lambda value, cls: value)
    assert api.get_output(object(), skip_digestion=True) is result
