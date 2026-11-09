"""Independent tetrahedron boundary patches versus native face grouping."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from pyunitwizard import QuantityRecord

from devtools.verify_tetrahedron_boundary import verify_certificate
from tests.test_benchlab_public_topography import public_result
from topomt import pyunitwizard as puw

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'docs/content/benchlab/synthetic/regular_tetrahedron'
DATA = CASE / 'artifacts/boundary_connectivity_v1'
INPUT = CASE / 'artifacts/regular_tetrahedron_v1/input.json'


def load(name):
    return json.loads((DATA / name).read_text())


def q(value, field, unit='angstroms'):
    return QuantityRecord.from_quantity(
        puw.quantity(value, unit), field=field
    ).to_dict()


def values(record, field, unit='angstroms'):
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return np.asarray(puw.get_value(quantity, to_unit=unit))


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_four_disconnected_boundary_patches_all_reach_the_origin(policy):
    with puw.context(standard_units=[*policy, 'radians']):
        result = verify_certificate(
            INPUT, DATA / 'protocol.json', load('certificate.json')
        )
    assert result == load('verification.json')
    assert result['opening_component_count'] == 4
    assert result['blocked_edge_count'] == 6
    assert result['origin_connected_patch_count'] == 4
    assert [face['nerve']['beta_1'] for face in result['faces']] == [1] * 4
    assert result['sealed_control']['opening_component_count'] == 0
    assert not result['excluded_control']['has_free_finite_hull_point']


@pytest.mark.parametrize(
    'damage', ['face', 'edge', 'intersection', 'positive', 'negative']
)
def test_incomplete_or_false_boundary_witnesses_are_rejected(damage):
    cert = load('certificate.json')
    if damage in {'face', 'edge'}:
        cert[{'face': 'faces', 'edge': 'blocked_edges'}[damage]].pop()
    elif damage == 'intersection':
        cert['faces'][0]['intersections'].pop()
    elif damage == 'positive':
        record = cert['faces'][0]['intersections'][0]
        record['barycentric_weights'] = q(
            [0, 1, 0], 'barycentric_weights', 'dimensionless'
        )
    else:
        record = next(r for r in cert['faces'][0]['intersections'] if not r['nonempty'])
        record['direction'] = q([0, 0, 0], 'direction', 'dimensionless')
    with pytest.raises(ValueError):
        verify_certificate(INPUT, DATA / 'protocol.json', cert)


def test_reference_survives_rigid_motion_and_atom_permutation(tmp_path):
    fixture, protocol, cert = (
        json.loads(INPUT.read_text()),
        load('protocol.json'),
        load('certificate.json'),
    )
    rotation = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    shift = np.array([4.0, -7.0, 2.0])
    permutation = [2, 0, 3, 1]
    coords = values(fixture['coordinates'], 'coordinates')
    fixture['coordinates'] = q(
        (coords @ rotation.T + shift)[permutation] / 10, 'coordinates', 'nm'
    )
    fixture['atom_radii'] = q(
        values(fixture['atom_radii'], 'atom_radii')[permutation] / 10,
        'atom_radii',
        'nm',
    )
    protocol['atom_indices'] = permutation
    for field in ['probe_radii', 'length_absolute']:
        protocol[field] = q(values(protocol[field], field) / 10, field, 'nm')
    for face in cert['faces']:
        for record in face['intersections']:
            if not record['nonempty']:
                record['direction'] = q(
                    values(record['direction'], 'direction', 'dimensionless')
                    @ rotation.T,
                    'direction',
                    'dimensionless',
                )
    input_file, protocol_file = tmp_path / 'input.json', tmp_path / 'protocol.json'
    input_file.write_text(json.dumps(fixture))
    cert['input_sha256'] = protocol['input_sha256'] = hashlib.sha256(
        input_file.read_bytes()
    ).hexdigest()
    protocol_file.write_text(json.dumps(protocol))
    cert['protocol_sha256'] = hashlib.sha256(protocol_file.read_bytes()).hexdigest()
    result = verify_certificate(input_file, protocol_file, cert)
    assert (
        result['opening_component_count'] == result['origin_connected_patch_count'] == 4
    )
    assert result['blocked_edge_count'] == 6


def test_physical_patch_count_is_distinct_from_current_public_receiving():
    topo, _, _ = public_result('regular_tetrahedron', 1.2)
    assert len(topo.get_features(by='type', value='percolating')) == 1
    assert len(topo.get_features(by='type', value='mouth')) == 0
    assert topo.dfnd.raw['wet_components'][0]['n_external_links'] == 1
    assert topo.dfnd.raw['wet_components'][0]['n_wall_faces'] == 0
    result = load('native_correspondence.json')
    assert result['native_external_link_count'] == 1
    assert len(result['native_face_clusters_source_atom_indices'][0]) == 4
    assert len(topo.dfnd.raw['external_links']) == 1
    assert len(topo.dfnd.raw['external_links'][0]['faces']) == 4
    assert result['independent_boundary_patch_count'] == 4
    assert result['public_mouth_count'] == len(
        topo.get_features(by='type', value='mouth')
    )
    assert result['disposition'] == 'distinct_observables_physical_refinement_pending'


def test_prior_scientific_bytes_are_preserved():
    for relative, digest in load('protocol.json')[
        'preserved_scientific_sha256'
    ].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize('unit,scale', [('nm', 0.1), ('pm', 100.0)])
def test_shared_convex_intersection_checker_requires_explicit_units(unit, scale):
    from devtools.verify_opening_connectivity import verify_convex_intersections

    fixture = json.loads(INPUT.read_text())
    coords = values(fixture['coordinates'], 'coordinates')
    face = load('certificate.json')['faces'][0]
    result = verify_convex_intersections(
        coords * scale,
        list(range(4)),
        coords[face['atom_indices']] * scale,
        2.9 * scale,
        1e-6 * scale,
        face['intersections'],
        8,
        length_unit=unit,
    )
    assert result['nerve']['beta_1'] == 1
    margin = values(
        result['minimum_intersection_decision_margin'],
        'minimum_intersection_decision_margin',
    )
    assert float(margin) > 0.15
    with pytest.raises(ValueError, match='tolerance'):
        verify_convex_intersections(
            coords,
            list(range(4)),
            coords[face['atom_indices']],
            2.9,
            float('nan'),
            face['intersections'],
            8,
            length_unit='angstroms',
        )


def test_shared_checker_preserves_historical_shell_verification():
    from devtools.verify_opening_connectivity import verify_certificate as verify_shell

    case = CASE.parent / 'shell_with_opening'
    data = case / 'artifacts/opening_connectivity_v1'
    result = verify_shell(
        case / 'artifacts/shell_with_opening_v1/input.json',
        data / 'protocol.json',
        json.loads((data / 'certificate.json').read_text()),
    )
    assert result == json.loads((data / 'verification.json').read_text())
