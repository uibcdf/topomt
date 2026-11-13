"""Exact model identity is independent of native DFND and decimal appearance."""

import copy
import json
import sys
from fractions import Fraction

import pytest

from devtools.reference_validator.model import (
    Atom,
    Box,
    Model,
    Tetrahedron,
    decode_scalar,
    encode_scalar,
    point,
    scalar,
)


def test_large_exact_scalars_round_trip_without_global_integer_policy_changes():
    original_limit = sys.get_int_max_str_digits()
    value = Fraction(10**5000 + 17, 10**5001 + 19)
    encoded = encode_scalar(value)
    assert len(encoded[0]) > 4300
    assert decode_scalar(json.loads(json.dumps(encoded))) == value
    assert sys.get_int_max_str_digits() == original_limit


def test_exact_scalar_codec_rejects_oversized_inputs_before_conversion():
    with pytest.raises(ValueError, match='codec budget'):
        decode_scalar(['1' + '0' * 20000, '1'])


def test_float_values_are_not_replaced_by_nearby_decimals():
    assert scalar(0.1) == Fraction(*(0.1).as_integer_ratio())
    assert scalar(0.1) != Fraction(1, 10)
    model = Model(
        (Atom(7, point((0, 0, 0)), scalar(0.1)),),
        scalar(0.2),
        Box(point((-1, -1, -1)), point((1, 1, 1))),
        'a' * 64,
    )
    assert model.atoms[0].radius + model.probe != scalar(0.1 + 0.2)
    record = json.loads(json.dumps(model.to_record()))
    restored = Model.from_record(record)
    assert restored == model
    assert restored.digest == model.digest
    for field, value in [
        ('length_unit', 'angstrom'),
        ('frame_index', -1),
        ('contact_policy', 'inclusive'),
    ]:
        bad = copy.deepcopy(record)
        bad[field] = value
        with pytest.raises(ValueError):
            Model.from_record(bad)


@pytest.mark.parametrize('value', [True, float('nan'), float('inf'), '0.1'])
def test_invalid_scalar_inputs_are_rejected(value):
    with pytest.raises((TypeError, ValueError)):
        scalar(value)


@pytest.mark.parametrize(
    'value', [['2', '4'], ['1', '0'], ['1', '-2'], ['01', '2'], [1, 2], ['0', '2']]
)
def test_serialized_rationals_must_be_canonical(value):
    with pytest.raises(ValueError):
        decode_scalar(value)


def test_model_digest_binds_atoms_probe_frame_domain_and_source():
    model = Model(
        (Atom(3, point((0, 0, 0)), scalar(1)),),
        scalar(0),
        Box(point((-2, -2, -2)), point((2, 2, 2))),
        'a' * 64,
    )
    for field, value in [
        ('probe', ['1', '1']),
        ('frame_index', 1),
        ('source_sha256', 'b' * 64),
    ]:
        record = model.to_record()
        record[field] = value
        assert Model.from_record(record).digest != model.digest
    record = model.to_record()
    record['atoms'][0]['source_id'] = 4
    assert Model.from_record(record).digest != model.digest
    record = model.to_record()
    record['domain']['upper'][0] = ['3', '1']
    assert Model.from_record(record).digest != model.digest


def test_negative_duplicate_and_degenerate_models_are_rejected():
    box = Box(point((-1, -1, -1)), point((1, 1, 1)))
    atom = Atom(0, point((0, 0, 0)), scalar(1))
    with pytest.raises(ValueError):
        Atom(0, point((0, 0, 0)), scalar(-1))
    with pytest.raises(ValueError):
        Model((atom, atom), scalar(0), box, 'a' * 64)
    with pytest.raises(ValueError):
        Model((atom,), scalar(-1), box, 'a' * 64)
    with pytest.raises(ValueError):
        Box(point((0, 0, 0)), point((0, 1, 1)))
    with pytest.raises(ValueError):
        Tetrahedron(tuple(point((i, 0, 0)) for i in range(4)))


def test_tetrahedron_encoding_and_unknown_fields():
    tet = Tetrahedron(
        tuple(point(x) for x in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)))
    )
    model = Model((), scalar(0), tet, 'a' * 64)
    assert Model.from_record(model.to_record()) == model
    record = model.to_record()
    record['topology_complete'] = True
    with pytest.raises(ValueError):
        Model.from_record(record)


def test_binary64_provenance_cannot_label_an_unrepresentable_rational():
    model = Model(
        (), Fraction(1, 3), Box(point((-1, -1, -1)), point((1, 1, 1))), 'a' * 64
    )
    record = model.to_record()
    record['interpretation'] = 'received_binary64_nm'
    with pytest.raises(ValueError, match='binary64'):
        Model.from_record(record)


def test_sphere_arrays_need_no_bonds_types_or_dfnd_results():
    domain = Box(point((-2, -2, -2)), point((2, 2, 2)))
    centers, radii = [[0, 0, 0]], [0.1]
    model = Model.from_spheres(centers, radii, 0.2, domain=domain)
    assert model.atoms[0].radius == scalar(0.1)
    assert model.probe == scalar(0.2)
    assert model.atoms[0].source_id == 0
    assert Model.from_record(model.to_record()) == model
    same_source = Model.from_spheres(centers, radii, 0.3, domain=domain)
    assert same_source.source_sha256 == model.source_sha256
    assert same_source.digest != model.digest
    centers[0][0], radii[0] = 10, 5
    assert model.atoms[0].center == point((0, 0, 0))
    assert model.atoms[0].radius == scalar(0.1)
    with pytest.raises(ValueError):
        Model.from_spheres([[0, 0, 0]], [], 0.2, domain=domain)
