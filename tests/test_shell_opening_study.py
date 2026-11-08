"""Independent geometric controls for the source-derived shell opening."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from tests.test_closed_shell_study import decode, geometry
from topomt import pyunitwizard as puw

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
