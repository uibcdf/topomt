"""Legacy original pyCASTA routing reaches provider admission before preparation."""

import warnings
from importlib import import_module

import numpy as np
import pytest

import topomt as tmt
from topomt._private.smonitor import ArgumentError
from topomt.third_party.pycasta import api


def test_original_legacy_route_preserves_source_context_before_topography(monkeypatch):
    dispatcher = import_module('topomt.get_topography')
    source = tmt.demo['TcTIM']['1tcd.pdb']
    selection = 'protein'
    frames = np.array([2])
    result = object()
    received = []

    def forbidden(*args, **kwargs):
        raise AssertionError('Topography prepared input before original admission.')

    def receive(value, **options):
        received.append((value, options))
        return result

    monkeypatch.setattr(dispatcher, 'Topography', forbidden)
    monkeypatch.setattr(api, 'get_topography', receive)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        assert (
            dispatcher.get_topography(
                source,
                method='pycasta',
                implementation='wrapper',
                selection=selection,
                structure_indices=frames,
                syntax='MDTraj',
                chemical_state=1,
            )
            is result
        )
    assert not any(
        type(item.message).__name__ == 'DigestNotDigestedWarning' for item in caught
    )
    value, options = received.pop()
    assert value == str(source)
    assert options.pop('selection') == selection
    np.testing.assert_array_equal(options.pop('structure_indices'), frames)
    assert options == {'backend': 'library', 'syntax': 'MDTraj', 'chemical_state': 1}


@pytest.mark.parametrize('chemical_state', [True, -1, 1.5, None])
def test_legacy_original_rejects_invalid_state_before_provider_or_preparation(
    chemical_state, monkeypatch
):
    dispatcher = import_module('topomt.get_topography')

    def forbidden(*args, **kwargs):
        pytest.fail('Invalid chemical state reached provider or preparation.')

    monkeypatch.setattr(dispatcher, 'Topography', forbidden)
    monkeypatch.setattr(api, 'get_topography', forbidden)
    with pytest.raises(ArgumentError, match='chemical_state'):
        dispatcher.get_topography(
            tmt.demo['TcTIM']['1tcd.pdb'],
            method='pycasta',
            implementation='wrapper',
            chemical_state=chemical_state,
        )
