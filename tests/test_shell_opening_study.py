"""Independent geometric controls for the source-derived shell opening."""

import ast
import base64
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial import ConvexHull

from tests.test_closed_shell_study import decode, geometry
from topomt import pyunitwizard as puw
from topomt.dfnd import DelaunayFlowNetwork

CASE = (
    Path(__file__).resolve().parents[1]
    / 'docs/content/benchlab/synthetic/shell_with_opening'
)
DATA = CASE / 'artifacts/shell_with_opening_v1'
PARENT = CASE.parent / 'closed_shell'


def inputs():
    fixture = json.loads((DATA / 'input.json').read_text())
    protocol = json.loads((DATA / 'protocol.json').read_text())
    parent = json.loads((PARENT / protocol['parent_input_file']).read_text())
    return fixture, protocol, parent


def test_opening_is_an_exact_identifiable_subset_of_the_frozen_parent():
    fixture, protocol, parent = inputs()
    for relative, digest in protocol['parent_preserved_files'].items():
        assert hashlib.sha256((PARENT / relative).read_bytes()).hexdigest() == digest
    assert (
        hashlib.sha256((DATA / 'input.json').read_bytes()).hexdigest()
        == protocol['input_sha256']
    )
    assert (
        hashlib.sha256((DATA / 'input.pdb').read_bytes()).hexdigest()
        == protocol['pdb_sha256']
    )
    assert protocol['reference_before_new_native_execution']
    assert not protocol['provider_execution']
    derivation = fixture['derivation']
    kept = derivation['parent_atom_indices']
    removed = derivation['removed_parent_atom_indices']
    assert kept == list(range(6, 72)) and removed == list(range(6))
    coordinates = decode(parent['coordinates'], 'coordinates', 'angstroms')
    radii = decode(parent['atom_radii'], 'atom_radii', 'angstroms')
    np.testing.assert_array_equal(
        decode(fixture['coordinates'], 'coordinates', 'angstroms'), coordinates[kept]
    )
    np.testing.assert_array_equal(
        decode(fixture['atom_radii'], 'atom_radii', 'angstroms'), radii[kept]
    )
    origin = decode(derivation['origin'], 'origin', 'angstroms')
    axis = decode(derivation['axis'], 'axis', 'dimensionless')
    angle = float(decode(derivation['half_angle'], 'half_angle', 'radians'))
    delta = coordinates - origin
    mask = (delta @ axis) / np.linalg.norm(delta, axis=1) > np.cos(angle)
    assert np.flatnonzero(mask).tolist() == removed
    parent_lines = (
        (PARENT / 'artifacts/closed_shell_v1/input.pdb').read_text().splitlines()
    )
    child_lines = (DATA / 'input.pdb').read_text().splitlines()
    assert child_lines == [parent_lines[index] for index in kept] + ['END']
    assert [int(line[6:11]) for line in child_lines[:-1]] == [i + 1 for i in kept]
    assert fixture['probe_sweep'] == parent['probe_sweep']


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_opening_has_independent_access_enclosure_and_exclusion_controls(policy):
    fixture, protocol, parent = inputs()
    with puw.context(standard_units=[*policy, 'radians']):
        coords = decode(fixture['coordinates'], 'coordinates', 'angstroms')
        radii = decode(fixture['atom_radii'], 'atom_radii', 'angstroms')
        origin = decode(protocol['origin'], 'origin', 'angstroms')
        axis = decode(fixture['derivation']['axis'], 'axis', 'dimensionless')
        original = decode(parent['coordinates'], 'coordinates', 'angstroms')
        original_radii = decode(parent['atom_radii'], 'atom_radii', 'angstroms')
        observed = geometry(coords, radii, origin, axis)
        negative = geometry(original, original_radii, origin, axis)
        angle = float(
            decode(fixture['derivation']['half_angle'], 'half_angle', 'radians')
        )
        cap_bound = np.linalg.norm(original - origin, axis=1).min() * np.sin(angle)
        cap_bound -= radii.max()
        assert observed['origin_inside'] and negative['origin_inside']
        assert observed['ray_clearance'].min() > cap_bound > 1.4 + 1e-6
        assert negative['ray_clearance'].min() < 1.4
        assert original_radii.min() + 1.4 - negative['face_cover'].max() > 1e-6
        assert radii.min() + 3.0 - observed['face_cover'].max() > 1e-6
        assert observed['center_clearance'] > 3.0 + 1e-6
        assert radii.min() + 5.0 - observed['enclosing_radius'] > 1e-6


def test_opening_derivation_and_certificates_survive_rigid_motion():
    fixture, protocol, _ = inputs()
    coords = decode(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = decode(fixture['atom_radii'], 'atom_radii', 'angstroms')
    origin = decode(protocol['origin'], 'origin', 'angstroms')
    axis = decode(fixture['derivation']['axis'], 'axis', 'dimensionless')
    rotation = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    translation = np.array([3.0, -4.0, 5.0])
    before = geometry(coords, radii, origin, axis)
    transformed = coords @ rotation.T + translation
    transformed_origin = origin @ rotation.T + translation
    transformed_axis = axis @ rotation.T
    after = geometry(transformed, radii, transformed_origin, transformed_axis)
    np.testing.assert_allclose(
        before['ray_clearance'], after['ray_clearance'], rtol=0, atol=1e-12
    )
    np.testing.assert_allclose(
        np.sort(before['face_cover']), np.sort(after['face_cover']), rtol=0, atol=1e-12
    )
    before_angles = (coords - origin) @ axis / np.linalg.norm(coords - origin, axis=1)
    after_angles = (transformed - transformed_origin) @ transformed_axis
    after_angles /= np.linalg.norm(transformed - transformed_origin, axis=1)
    np.testing.assert_allclose(before_angles, after_angles, rtol=0, atol=1e-14)
    assert before['origin_inside'] and after['origin_inside']


def test_opening_reference_reproduces_the_independent_geometry():
    fixture, protocol, parent = inputs()
    reference = json.loads((DATA / 'system_reference.json').read_text())
    assert reference['reference_checks'] == 'passed'
    assert (
        reference['protocol_sha256']
        == hashlib.sha256((DATA / 'protocol.json').read_bytes()).hexdigest()
    )
    assert reference['input_sha256'] == protocol['input_sha256']
    coordinates = decode(fixture['coordinates'], 'coordinates', 'angstroms')
    radii = decode(fixture['atom_radii'], 'atom_radii', 'angstroms')
    origin = decode(protocol['origin'], 'origin', 'angstroms')
    axis = decode(fixture['derivation']['axis'], 'axis', 'dimensionless')
    independent = geometry(coordinates, radii, origin, axis)
    np.testing.assert_allclose(
        decode(
            reference['escape_witness']['per_atom_clearance'],
            'per_atom_clearance',
            'angstroms',
        ),
        independent['ray_clearance'],
        rtol=0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        decode(
            reference['certificates']['maximum_face_cover_radius'],
            'maximum_face_cover_radius',
            'angstroms',
        ),
        independent['face_cover'].max(),
        rtol=0,
        atol=1e-12,
    )
    assert [
        float(decode(e['probe_radius'], 'probe_radius', 'angstroms'))
        for e in reference['experiments']
    ] == [1.4, 3.0, 5.0]
    kept = fixture['derivation']['parent_atom_indices']
    contact = reference['contact_reference']
    assert set(map(tuple, contact['new_child_hull_faces_parent_ids'])).isdisjoint(
        map(tuple, contact['unchanged_child_hull_faces_parent_ids'])
    )
    all_face_atoms = {
        atom
        for face in contact['new_child_hull_faces_parent_ids']
        + contact['unchanged_child_hull_faces_parent_ids']
        for atom in face
    }
    assert all_face_atoms <= set(kept)
    parent_coords = decode(parent['coordinates'], 'coordinates', 'angstroms')
    parent_faces = {tuple(sorted(face)) for face in ConvexHull(parent_coords).simplices}
    child_faces = {
        tuple(sorted(np.asarray(kept)[face]))
        for face in ConvexHull(coordinates).simplices
    }
    assert (
        set(map(tuple, contact['new_child_hull_faces_parent_ids']))
        == child_faces - parent_faces
    )
    assert (
        set(map(tuple, contact['unchanged_child_hull_faces_parent_ids']))
        == child_faces & parent_faces
    )
    np.testing.assert_array_equal(
        decode(fixture['coordinates'], 'coordinates', 'angstroms'),
        decode(parent['coordinates'], 'coordinates', 'angstroms')[kept],
    )


def test_opening_observations_preserve_the_certified_scope_and_parent_faces():
    report = json.loads((DATA / 'dfnd_observations.json').read_text())
    reference = json.loads((DATA / 'system_reference.json').read_text())
    assert (
        report['reference_sha256']
        == hashlib.sha256((DATA / 'system_reference.json').read_bytes()).hexdigest()
    )
    assert report['reference_checks'] == 'passed'
    parent = report['parent_control']
    assert parent['central_family'] == 'void' and parent['central_external_links'] == 0
    opened, sealed, excluded = report['anchors']
    assert opened['central_resident_nodes'] > 0 and opened['central_external_links'] > 0
    assert (
        sealed['central_resident_nodes'] > 0 and sealed['central_external_links'] == 0
    )
    assert sealed['central_family'] == 'void'
    assert excluded['resident_node_count'] == excluded['raw_component_count'] == 0
    new_faces = set(
        map(tuple, reference['contact_reference']['new_child_hull_faces_parent_ids'])
    )
    for link in report['contact_analysis']['links']:
        assert link['faces_parent_ids']
        assert set(map(tuple, link['faces_parent_ids'])) <= new_faces
        assert set(link['atom_indices']) <= set(range(6, 72))
        gate = float(decode(link['R_gate_min'], 'R_gate_min', 'angstroms'))
        assert gate >= 1.4 - 1e-6
        assert (
            float(decode(link['area_geometric'], 'area_geometric', 'angstroms**2')) > 0
        )
    assert len(report['contact_analysis']['links']) == opened['central_external_links']
    assert len(report['sweep']) == 49
    dispositions = set()
    for row in report['sweep']:
        dispositions.add(row['reference_disposition'])
        assert row['reference_check'] in ('passed', 'unresolved')
    assert 'unresolved_by_sufficient_bounds' in dispositions
    for before, after in zip(report['sweep'], report['sweep'][1:]):
        assert set(after['resident_tetrahedron_ids']) <= set(
            before['resident_tetrahedron_ids']
        )
    control = report['reporting_control']
    assert control['geometry_unchanged'] and control['raw_central_component_retained']
    assert control['min_size'] == opened['central_nodes'] + 1
    assert not control['central_in_compatibility_view']


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_live_opening_controls_and_parent_identity_under_explicit_units(policy):
    fixture, protocol, parent = inputs()
    with puw.context(standard_units=[*policy, 'radians']):

        def quantity(record, field):
            return puw.quantity(decode(record, field, 'angstroms'), 'angstroms')

        query = {
            key: quantity(value, key) if isinstance(value, dict) else value
            for key, value in protocol['query'].items()
        }
        for source, probes, mapping in [
            (parent, [1.4], np.arange(72)),
            (
                fixture,
                [1.4, 3.0, 5.0],
                np.array(fixture['derivation']['parent_atom_indices']),
            ),
        ]:
            network = DelaunayFlowNetwork.from_coordinates_and_radii(
                quantity(source['coordinates'], 'coordinates'),
                quantity(source['atom_radii'], 'atom_radii'),
                atom_indices=mapping,
                epsilon=quantity(source['epsilon'], 'epsilon'),
            )
            origin = decode(protocol['origin'], 'origin', 'nm')
            vertices = network.atom_coords[network.tetra_atoms]
            matrices = np.swapaxes(vertices[:, 1:] - vertices[:, :1], 1, 2)
            bary = np.linalg.solve(matrices, (origin - vertices[:, 0])[:, :, None])[
                :, :, 0
            ]
            containing = set(
                np.flatnonzero(
                    np.all(bary >= -1e-8, axis=1) & (bary.sum(axis=1) <= 1 + 1e-8)
                )
            )
            assert containing
            for probe in probes:
                raw = network.get_topography(
                    probe_radius=puw.quantity(probe, 'angstroms'), **query
                )['raw']
                for cell in raw['tetrahedra']:
                    assert (
                        cell['atom_indices']
                        == mapping[cell['local_atom_indices']].tolist()
                    )
                central = [
                    c
                    for c in raw['wet_components']
                    if containing & set(c['tetrahedron_ids'])
                ]
                if probe == 5:
                    assert not raw['wet_components']
                    assert not any(
                        t['residence_state'] == 'resident' for t in raw['tetrahedra']
                    )
                else:
                    assert len(central) == 1 and central[0]['n_resident_nodes'] > 0
                    if source is fixture and probe == 1.4:
                        assert central[0]['n_external_links'] > 0
                        reference = json.loads(
                            (DATA / 'system_reference.json').read_text()
                        )
                        new_faces = set(
                            map(
                                tuple,
                                reference['contact_reference'][
                                    'new_child_hull_faces_parent_ids'
                                ],
                            )
                        )
                        for link in raw['external_links']:
                            if (
                                link['external_link_id']
                                not in central[0]['external_link_ids']
                            ):
                                continue
                            faces = {
                                tuple(sorted(mapping[face])) for face in link['faces']
                            }
                            assert faces and faces <= new_faces
                            assert set(link['atom_indices']) == {
                                atom for face in faces for atom in face
                            }
                    else:
                        assert (
                            central[0]['n_external_links'] == 0
                            and central[0]['family'] == 'void'
                        )


@pytest.mark.parametrize(
    'name,tag,record,figures',
    [
        (
            'system',
            'topomt-shell-opening-reference',
            'system_reference.json',
            ['system_geometry.png', 'system_certificates.png'],
        ),
        (
            'dfnd',
            'topomt-shell-opening-native',
            'dfnd_observations.json',
            ['dfnd_contacts.png', 'dfnd_sweep.png'],
        ),
    ],
)
def test_opening_notebooks_display_reviewed_records_without_writing_or_providers(
    name, tag, record, figures
):
    notebook = json.loads((CASE / f'{name}.ipynb').read_text())
    cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
    assert cells and all(cell['execution_count'] is not None for cell in cells)
    outputs = [output for cell in cells for output in cell['outputs']]
    assert not any(output['output_type'] == 'error' for output in outputs)
    pngs = [
        output['data']['image/png']
        for output in outputs
        if 'image/png' in output.get('data', {})
    ]
    assert len(pngs) == len(figures)
    for png, figure in zip(pngs, figures, strict=True):
        assert base64.b64decode(''.join(png)) == (DATA / figure).read_bytes()
    displayed = [
        json.loads(''.join(output['data']['text/plain']))
        for cell in cells
        if tag in cell.get('metadata', {}).get('tags', [])
        for output in cell['outputs']
        if 'text/plain' in output.get('data', {})
    ]
    assert displayed == [json.loads((DATA / record).read_text())]
    for cell in cells:
        for node in ast.walk(ast.parse(''.join(cell['source']))):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = (
                    [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or '']
                )
                assert not any(
                    module.startswith(('subprocess', 'requests', 'urllib'))
                    for module in modules
                )
                if name == 'system':
                    assert not any(module.startswith('topomt') for module in modules)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in (
                    'write_text',
                    'write_bytes',
                    'savefig',
                    'to_file',
                )


def test_opening_receipt_matches_reviewed_notebooks_and_artifacts():
    receipt = json.loads((DATA / 'execution_receipt.json').read_text())
    for name, entry in receipt['notebooks'].items():
        assert (
            hashlib.sha256((CASE / f'{name}.ipynb').read_bytes()).hexdigest()
            == entry['sha256']
        )
    for name, digest in receipt['artifact_sha256'].items():
        assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == digest
    assert (
        receipt['limits']['os_cpu_affinity_count']
        == receipt['limits']['numerical_workers']
        == 1
    )
