"""Explicit native query objects are admitted by the shared public dispatcher."""

import warnings

import pytest

from tests.test_benchlab_public_topography import molecular_input
from topomt import get_topography
from topomt import pyunitwizard as puw
from topomt._private.smonitor import ArgumentError
from topomt.dfnd.config import DFNDQuery


def test_valid_explicit_query_is_digested_and_preserves_the_canonical_result():
    system, selection, _, _, _ = molecular_input('regular_tetrahedron')
    normalized = float(puw.get_value(puw.quantity(1.2, 'angstroms'), to_unit='nm'))
    with warnings.catch_warnings(record=True) as received:
        warnings.simplefilter('always')
        topo = get_topography(
            system,
            method='dfnd',
            selection=selection,
            probe_radius=puw.quantity(1.2, 'angstroms'),
            query=DFNDQuery(probe_radius=normalized),
        )
    assert not any(
        type(w.message).__name__ == 'DigestNotDigestedWarning' for w in received
    )
    plain = get_topography(
        system,
        method='dfnd',
        selection=selection,
        probe_radius=puw.quantity(1.2, 'angstroms'),
        query=None,
    )
    assert topo.dfnd.raw['parameters']['query'] == plain.dfnd.raw['parameters']['query']
    assert (
        topo.dfnd.raw['parameters']['result_key']
        == plain.dfnd.raw['parameters']['result_key']
    )


@pytest.mark.parametrize('query', [{}, 'dfnd', 3.0, []])
def test_invalid_query_is_rejected_at_the_gateway_before_native_execution(
    query, monkeypatch
):
    import topomt.dfnd.api as api

    def forbidden(*args, **kwargs):
        raise AssertionError('Invalid query reached the native runner')

    monkeypatch.setattr(api, 'dfnd_to_topography', forbidden)
    system, selection, _, _, _ = molecular_input('regular_tetrahedron')
    with pytest.raises(ArgumentError, match='query'):
        get_topography(system, method='dfnd', selection=selection, query=query)


def test_public_gateway_preserves_inner_conflicting_query_diagnostics():
    system, selection, _, _, _ = molecular_input('regular_tetrahedron')
    with pytest.raises(ValueError, match='conflicts'):
        get_topography(
            system,
            method='dfnd',
            selection=selection,
            probe_radius=puw.quantity(1.3, 'angstroms'),
            query=DFNDQuery(probe_radius=0.12),
        )
