"""Source profiles and original-field comparisons are reusable developer tools."""

from dataclasses import replace
from pathlib import Path

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from devtools.provider_handoff import (
    chemical_state_context,
    pocket_outputs_agree,
    prepare_reference_source,
)
from tests.methods.fpocket4.test_chemical_context import _with_states
from tests.methods.fpocket4.test_input_preparation import _pdb_frame
from topomt import pyunitwizard as puw


@pytest.fixture
def small_source(tmp_path):
    path = tmp_path / 'seed.pdb'
    path.write_text(_pdb_frame() + 'END\n')
    return msm.convert(path, to_form='molsysmt.MolSys')


@pytest.mark.parametrize('inventory', ['absent', 'empty', 'two'])
def test_source_profile_rejects_missing_or_multiple_states(small_source, inventory):
    source = _with_states(small_source, inventory=inventory)
    with pytest.raises(ValueError, match='chemical state'):
        prepare_reference_source(source)


def test_source_profile_distinguishes_absent_and_empty_states(small_source):
    assert (
        chemical_state_context(_with_states(small_source, inventory='absent'))['count']
        is None
    )
    assert (
        chemical_state_context(_with_states(small_source, inventory='empty'))['count']
        == 0
    )


def test_source_profile_requires_auxiliary_atoms(small_source):
    with pytest.raises(ValueError, match='nonconsecutive'):
        prepare_reference_source(small_source)


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_source_profile_preserves_source_and_declares_only_one_new_frame(policy):
    path = Path(tmt.__file__).parent / 'data/CASTp_3.0_server/3ptb.pdb'
    seed = msm.convert(path, to_form='molsysmt.MolSys')
    before = puw.get_value(msm.get(seed, coordinates=True), to_unit='nm').copy()
    with puw.context(standard_units=[*policy, 'radians']):
        source, selection = prepare_reference_source(seed)
        assert np.any(np.diff(selection) > 1)
        assert chemical_state_context(source) == {'count': 1, 'reference_index': 0}
        coordinates = puw.get_value(msm.get(source, coordinates=True), to_unit='nm')
        assert coordinates.shape[0] == 2
        np.testing.assert_allclose(
            coordinates[1] - coordinates[0],
            np.broadcast_to([0.3, -0.2, 0.1], coordinates[0].shape),
            rtol=0,
            atol=1e-12,
        )
    np.testing.assert_array_equal(
        puw.get_value(msm.get(seed, coordinates=True), to_unit='nm'), before
    )


@pytest.fixture(scope='module')
def original_output():
    root = Path(tmt.__file__).parent / 'data/fpocket4/sample'
    return tmt.get_provider_output(
        root / '3LKF.pdb',
        method='fpocket',
        backend='files',
        pdb_file=root / '3LKF.pdb',
        output_dir=root / '3LKF_out',
    )


@pytest.mark.parametrize(
    'change', ['membership', 'geometry', 'measurement', 'order', 'empty']
)
def test_comparison_rejects_changed_scientific_records(original_output, change):
    first, *others = original_output.records
    if change == 'membership':
        first = replace(first, atom_indices=first.atom_indices[1:])
    elif change == 'geometry':
        geometry, *rest = first._geometries
        points = np.asarray(geometry.points_nm) + [0.01, 0, 0]
        first = replace(
            first,
            _geometries=(replace(geometry, points_nm=tuple(map(tuple, points))), *rest),
        )
    elif change == 'measurement':
        attributes = first.fields
        value = attributes['external_measurements']['score']
        attributes['external_measurements']['score'] = replace(
            value,
            original_value=value.original_value + 1,
        )
        first = replace(first, _fields=attributes)
    if change == 'order':
        records = tuple(reversed(original_output.records))
    elif change == 'empty':
        records = ()
    else:
        records = (first, *others)
    changed = replace(original_output, records=records)
    assert not pocket_outputs_agree(changed, original_output)


def test_comparison_accepts_only_physical_roundoff(original_output):
    first, *others = original_output.records
    geometry, *rest = first._geometries
    points = np.asarray(geometry.points_nm) + [1e-14, 0, 0]
    changed = replace(
        first,
        _geometries=(replace(geometry, points_nm=tuple(map(tuple, points))), *rest),
    )
    assert pocket_outputs_agree(
        replace(original_output, records=(changed, *others)), original_output
    )


def test_comparison_preserves_undefined_original_measurements(original_output):
    first, *others = original_output.records

    def with_value(value):
        attributes = first.fields
        score = attributes['external_measurements']['score']
        attributes['external_measurements']['score'] = replace(
            score, original_value=value
        )
        record = replace(first, _fields=attributes)
        return replace(original_output, records=(record, *others))

    left, right = with_value(float('nan')), with_value(float('nan'))
    assert pocket_outputs_agree(left, right)
    assert not pocket_outputs_agree(left, with_value(0.0))
    assert not pocket_outputs_agree(left, with_value(float('inf')))
    assert not pocket_outputs_agree(with_value(float('inf')), with_value(float('-inf')))
