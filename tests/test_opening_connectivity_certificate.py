"""Independent boundary connectivity on the unchanged opened-shell input."""

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from devtools.verify_closed_shell_wall_cover import verify_triangle_cover
from devtools.verify_opening_connectivity import first_betti, verify_certificate
from tests.test_benchlab_public_topography import public_result
from topomt import pyunitwizard as puw

CASE = (
    Path(__file__).resolve().parents[1]
    / 'docs/content/benchlab/synthetic/shell_with_opening'
)
DATA = CASE / 'artifacts/opening_connectivity_v1'


def certificate():
    return json.loads((DATA / 'certificate.json').read_text())


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_opening_has_one_connected_free_boundary_patch_with_an_origin_path(policy):
    with puw.context(standard_units=[*policy, 'radians']):
        result = verify_certificate(
            CASE / 'artifacts/shell_with_opening_v1/input.json',
            DATA / 'protocol.json',
            certificate(),
        )
    assert result['verification'] == 'passed'
    assert result['opening_component_count'] == result['nerve']['beta_1'] == 1
    assert result['covered_hull_face_count'] == 127
    assert result['cover_leaf_count'] == 193
    assert result['origin_connected_to_opening']
    assert result['face_parent_atom_indices'] == [6, 7, 8]
    assert result['nerve']['vertices'] == 14


def test_missing_intersection_record_cannot_certify_connectivity():
    broken = certificate()
    broken['intersections'].pop()
    with pytest.raises(ValueError, match='complete'):
        verify_certificate(
            CASE / 'artifacts/shell_with_opening_v1/input.json',
            DATA / 'protocol.json',
            broken,
        )


def test_false_positive_intersection_witness_is_rejected():
    from pyunitwizard import QuantityRecord

    broken = certificate()
    record = next(record for record in broken['intersections'] if record['nonempty'])
    record['barycentric_weights'] = QuantityRecord.from_quantity(
        puw.quantity([0.0, 0.0, 1.0], 'dimensionless'), field='barycentric_weights'
    ).to_dict()
    with pytest.raises(ValueError, match='intersection witness'):
        verify_certificate(
            CASE / 'artifacts/shell_with_opening_v1/input.json',
            DATA / 'protocol.json',
            broken,
        )


def test_invalid_negative_separation_witness_is_rejected():
    from pyunitwizard import QuantityRecord

    broken = certificate()
    record = next(
        record for record in broken['intersections'] if not record['nonempty']
    )
    record['direction'] = QuantityRecord.from_quantity(
        puw.quantity([0.0, 0.0, 0.0], 'dimensionless'), field='direction'
    ).to_dict()
    with pytest.raises(ValueError, match='direction'):
        verify_certificate(
            CASE / 'artifacts/shell_with_opening_v1/input.json',
            DATA / 'protocol.json',
            broken,
        )


def test_missing_wall_piece_cannot_exclude_another_opening():
    broken = copy.deepcopy(certificate())
    broken['wall_cover']['leaves'].pop()
    with pytest.raises(ValueError, match='partition'):
        verify_certificate(
            CASE / 'artifacts/shell_with_opening_v1/input.json',
            DATA / 'protocol.json',
            broken,
        )


def test_first_homology_distinguishes_one_two_and_filled_cycles():
    assert first_betti([0, 1, 2], [(0, 1), (0, 2), (1, 2)], [])['beta_1'] == 1
    assert first_betti([0, 1, 2], [(0, 1), (0, 2), (1, 2)], [(0, 1, 2)])['beta_1'] == 0
    assert (
        first_betti(
            list(range(6)), [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5)], []
        )['beta_1']
        == 2
    )
    with pytest.raises(ValueError, match='edge'):
        first_betti([0, 1, 2], [(0, 1)], [(0, 1, 2)])


def test_certificate_survives_a_rigid_motion_without_changing_the_nerve(tmp_path):
    from pyunitwizard import QuantityRecord

    fixture = json.loads(
        (CASE / 'artifacts/shell_with_opening_v1/input.json').read_text()
    )
    protocol = json.loads((DATA / 'protocol.json').read_text())
    moved = copy.deepcopy(certificate())
    rotation = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    shift = np.array([3.0, -4.0, 5.0])

    def vector(record, field, unit):
        quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
        return np.asarray(puw.get_value(quantity, to_unit=unit))

    def qrecord(data, field, unit):
        return QuantityRecord.from_quantity(
            puw.quantity(data, unit), field=field
        ).to_dict()

    coords = vector(fixture['coordinates'], 'coordinates', 'angstroms')
    fixture['coordinates'] = qrecord(
        coords @ rotation.T + shift, 'coordinates', 'angstroms'
    )
    origin = vector(protocol['origin'], 'origin', 'angstroms')
    axis = vector(protocol['axis'], 'axis', 'dimensionless')
    protocol['origin'] = qrecord(origin @ rotation.T + shift, 'origin', 'angstroms')
    protocol['axis'] = qrecord(axis @ rotation.T, 'axis', 'dimensionless')
    fixture['derivation']['origin'] = protocol['origin']
    fixture['derivation']['axis'] = protocol['axis']
    for record in moved['intersections']:
        if not record['nonempty']:
            direction = vector(record['direction'], 'direction', 'dimensionless')
            record['direction'] = qrecord(
                direction @ rotation.T, 'direction', 'dimensionless'
            )
    input_file = tmp_path / 'input.json'
    input_file.write_text(json.dumps(fixture))
    moved['input_sha256'] = protocol['input_sha256'] = hashlib.sha256(
        input_file.read_bytes()
    ).hexdigest()
    protocol_file = tmp_path / 'protocol.json'
    protocol_file.write_text(json.dumps(protocol))
    moved['protocol_sha256'] = hashlib.sha256(protocol_file.read_bytes()).hexdigest()
    verified = verify_certificate(input_file, protocol_file, moved)
    assert verified['opening_component_count'] == 1
    assert verified['origin_connected_to_opening']


def test_partial_wall_cover_has_an_explicit_length_unit_contract():
    from pyunitwizard import QuantityRecord

    fixture = json.loads(
        (CASE / 'artifacts/shell_with_opening_v1/input.json').read_text()
    )
    cert = certificate()

    def nm(record, field):
        quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit='nm')
        return np.asarray(puw.get_value(quantity, to_unit='nm'))

    coverage = verify_triangle_cover(
        nm(fixture['coordinates'], 'coordinates'),
        nm(fixture['atom_radii'], 'atom_radii'),
        np.array(cert['wall_cover']['hull_faces']),
        cert['wall_cover']['leaves'],
        0.14,
        1e-7,
        length_unit='nm',
        maximum_depth=8,
        maximum_nodes=20000,
    )
    assert coverage['leaf_count'] == 193


def test_source_atom_permutation_preserves_the_boundary_certificate(tmp_path):
    from pyunitwizard import QuantityRecord

    fixture = json.loads(
        (CASE / 'artifacts/shell_with_opening_v1/input.json').read_text()
    )
    protocol = json.loads((DATA / 'protocol.json').read_text())
    permuted = certificate()
    order = np.arange(66)[::-1]
    inverse = np.argsort(order)
    for field in ('coordinates', 'atom_radii'):
        quantity = QuantityRecord.from_dict(fixture[field]).to_quantity(
            field=field, unit='angstroms'
        )
        data = np.asarray(puw.get_value(quantity, to_unit='angstroms'))[order]
        fixture[field] = QuantityRecord.from_quantity(
            puw.quantity(data, 'angstroms'), field=field
        ).to_dict()
    fixture['derivation']['parent_atom_indices'] = np.asarray(
        fixture['derivation']['parent_atom_indices']
    )[order].tolist()
    cover = permuted['wall_cover']
    cover['hull_faces'] = inverse[np.array(cover['hull_faces'])].tolist()
    for leaf in cover['leaves']:
        leaf['covering_atom_index'] = int(inverse[leaf['covering_atom_index']])
    input_file = tmp_path / 'input.json'
    input_file.write_text(json.dumps(fixture))
    permuted['input_sha256'] = protocol['input_sha256'] = hashlib.sha256(
        input_file.read_bytes()
    ).hexdigest()
    protocol_file = tmp_path / 'protocol.json'
    protocol_file.write_text(json.dumps(protocol))
    permuted['protocol_sha256'] = hashlib.sha256(protocol_file.read_bytes()).hexdigest()
    result = verify_certificate(input_file, protocol_file, permuted)
    assert result['opening_component_count'] == 1
    assert result['origin_connected_to_opening']


def test_reference_matches_the_existing_public_mouth_on_the_declared_face():
    result = verify_certificate(
        CASE / 'artifacts/shell_with_opening_v1/input.json',
        DATA / 'protocol.json',
        certificate(),
    )
    topo, _, _ = public_result('shell_with_opening', 1.4)
    mouths = topo.get_features(by='type', value='mouth')
    assert len(mouths) == result['opening_component_count']
    mouth = next(iter(mouths))
    parent = next(iter(topo.parents_of(mouth.feature_id)))
    assert parent.feature_type == 'pocket'
    faces = np.asarray(mouth.faces)
    assert (
        np.sort(topo.input_context.atom_indices[faces][0]).tolist()
        == result['face_parent_atom_indices']
    )


def test_reference_receipt_preserves_prior_evidence_and_versioned_artifacts():
    root = CASE.parents[1]
    protocol = json.loads((DATA / 'protocol.json').read_text())
    for relative, digest in protocol['preserved_files'].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
    receipt = json.loads((DATA / 'execution_receipt.json').read_text())
    for name, digest in receipt['artifact_sha256'].items():
        assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == digest
    assert set(receipt['verifier_source_sha256']) == {
        'devtools/verify_closed_shell_wall_cover.py',
        'devtools/verify_opening_connectivity.py',
    }
    receiving = json.loads((DATA / 'native_correspondence.json').read_text())
    assert receiving['checks'] == 'passed'
    assert receiving['reference_opening_count'] == receiving['public_mouth_count'] == 1


@pytest.mark.parametrize('tolerance', [float('nan'), -1.0])
def test_cover_checker_rejects_unsafe_safety_tolerances(tolerance):
    from pyunitwizard import QuantityRecord

    fixture = json.loads(
        (CASE / 'artifacts/shell_with_opening_v1/input.json').read_text()
    )
    cert = certificate()

    def values(record, field):
        quantity = QuantityRecord.from_dict(record).to_quantity(
            field=field, unit='angstroms'
        )
        return np.asarray(puw.get_value(quantity, to_unit='angstroms'))

    with pytest.raises(ValueError, match='tolerance'):
        verify_triangle_cover(
            values(fixture['coordinates'], 'coordinates'),
            values(fixture['atom_radii'], 'atom_radii'),
            np.array(cert['wall_cover']['hull_faces']),
            cert['wall_cover']['leaves'],
            1.4,
            tolerance,
            length_unit='angstroms',
            maximum_depth=8,
            maximum_nodes=20000,
        )
