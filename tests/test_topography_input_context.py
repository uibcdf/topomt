"""Standalone input records validate retained evidence independently of DFND."""

import numpy as np
import pytest

from topomt import pyunitwizard as puw
from topomt.topography.input_context import InputContext


def _context(**overrides):
    values = dict(
        coordinates=puw.quantity([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], 'angstroms'),
        radii=puw.quantity([1.7, 1.7], 'angstroms'),
        atom_indices=np.array([8, 2]),
        selection='array',
        structure_index=None,
        selection_syntax='explicit_indices',
        hydrogen_policy='provided_atoms',
        radii_model='provided',
    )
    values.update(overrides)
    return InputContext(**values)


def test_quantity_context_converts_units_and_owns_protected_values():
    context = _context()
    np.testing.assert_allclose(
        puw.get_value(context.coordinates, to_unit='nm')[1], [0.1, 0.0, 0.0]
    )
    np.testing.assert_allclose(puw.get_value(context.radii, to_unit='nm'), [0.17, 0.17])
    assert context.local_atom_indices([], source_id=context.source_id) == []
    with pytest.raises(ValueError):
        puw.get_value(context.radii)[0] = 0.0
    with pytest.raises(AttributeError):
        context.source_id = 'another-source'


@pytest.mark.parametrize('indices', [[1, 1], [-1, 2], [1.5, 2.5], [[1, 2]]])
def test_context_rejects_ambiguous_source_atom_mapping(indices):
    with pytest.raises(ValueError, match='indices'):
        _context(atom_indices=np.asarray(indices))


@pytest.mark.parametrize(
    'overrides',
    [
        {'coordinates': np.zeros((2, 3))},
        {'radii': puw.quantity([1.7], 'angstroms')},
        {'radii': puw.quantity([1.7, -1.0], 'angstroms')},
        {'coordinates': puw.quantity([[np.nan, 0.0, 0.0], [0.0, 0.0, 0.0]], 'nm')},
        {'structure_index': True},
        {'structure_index': -1},
    ],
)
def test_context_rejects_inconsistent_geometry_and_frame_evidence(overrides):
    with pytest.raises(ValueError):
        _context(**overrides)
