"""Smoke tests for the isolated CASTp3 backend copy."""

from importlib import import_module


def test_castp3_backend_copy_imports_from_its_own_namespace():
    """The experimental CASTp3 copy should not resolve through the CASTp1 package."""

    module = import_module('topomt.third_party.castp3._native_impl')
    api_module = import_module('topomt.third_party.castp3.api')

    assert hasattr(module, 'castp')
    assert hasattr(api_module, 'get_topography')
    assert 'topomt/third_party/castp3/' in module.__file__
    assert 'topomt/third_party/castp3/' in api_module.__file__
