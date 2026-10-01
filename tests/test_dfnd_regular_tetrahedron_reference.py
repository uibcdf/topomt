"""Independent regular-tetrahedron references for the public benchmark seed."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from pyunitwizard import QuantityRecord

from topomt import pyunitwizard as puw
from topomt.dfnd import DelaunayFlowNetwork, synthetic

EDGE = 5.3
ATOM_RADIUS = 1.7
REFERENCE_TOLERANCE = 1e-6  # angstroms; fixed before studying the solver
NOTEBOOK_DIR = Path(__file__).resolve().parents[1] / 'docs/content/showcase/dfnd'


@pytest.fixture
def network():
    system = synthetic.tetrahedron(edge=EDGE, atom_radius=ATOM_RADIUS)
    return DelaunayFlowNetwork.from_coordinates_and_radii(
        puw.quantity(system.coords, 'angstroms'),
        puw.quantity(system.radii, 'angstroms'),
        epsilon=puw.quantity(1e-6, 'angstroms'),
    )


def test_regular_tetrahedron_clearances_match_independent_circumradius_formulas(
    network,
):
    expected_residence = EDGE * np.sqrt(6) / 4 - ATOM_RADIUS
    expected_gate = EDGE / np.sqrt(3) - ATOM_RADIUS
    np.testing.assert_allclose(
        network.tetra_residence * 10,
        expected_residence,
        rtol=0,
        atol=REFERENCE_TOLERANCE,
    )
    np.testing.assert_allclose(
        network.face_r_gates_per_tet_face * 10,
        expected_gate,
        rtol=0,
        atol=REFERENCE_TOLERANCE,
    )
    assert expected_gate < 1.4 < expected_residence


@pytest.mark.parametrize(
    'probe, resident, contacts, family, links',
    [
        (1.2, True, 4, 'percolating', 1),
        (1.4, True, 0, 'void', 0),
        (1.7, False, 0, None, 0),
    ],
)
def test_regular_tetrahedron_separates_residence_from_face_transit(
    network, probe, resident, contacts, family, links
):
    result = network.get_topography(
        probe_radius=puw.quantity(probe, 'angstroms'), min_size=0
    )
    tetrahedron = result['raw']['tetrahedra'][0]
    assert (tetrahedron['residence_state'] == 'resident') is resident
    assert tetrahedron['n_permeable_contacts'] == contacts
    components = result['raw']['wet_components']
    if family is None:
        assert components == []
    else:
        assert len(components) == 1
        assert components[0]['family'] == family
        assert components[0]['n_external_links'] == links
    # No probe expansion or solvent subtraction: this is the finite cell's hull.
    np.testing.assert_allclose(
        tetrahedron['volume_topological'] * 1000, EDGE**3 / (6 * np.sqrt(2)), rtol=1e-12
    )


def test_regular_tetrahedron_reference_survives_rigid_motion(network):
    angle = 0.7
    rotation = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1],
        ]
    )
    moved = puw.get_value(
        puw.quantity(network.atom_coords, 'nm'), to_unit='angstroms'
    ) @ rotation.T + [17, -3, 8]
    other = DelaunayFlowNetwork.from_coordinates_and_radii(
        puw.quantity(moved, 'angstroms'), puw.quantity(network.atom_radii, 'nm')
    )
    np.testing.assert_allclose(
        other.tetra_residence,
        network.tetra_residence,
        rtol=0,
        atol=REFERENCE_TOLERANCE * 0.1,
    )
    np.testing.assert_allclose(
        other.face_r_gates_per_tet_face,
        network.face_r_gates_per_tet_face,
        rtol=0,
        atol=REFERENCE_TOLERANCE * 0.1,
    )


def test_public_tetrahedron_input_preserves_units_model_and_submitted_bytes():
    artifact_dir = NOTEBOOK_DIR / 'artifacts/regular_tetrahedron_v1'
    fixture = json.loads((artifact_dir / 'input.json').read_text())
    quantities = {
        field: QuantityRecord.from_dict(fixture[field]).to_quantity(
            field=field, unit='angstroms'
        )
        for field in ['coordinates', 'atom_radii', 'edge', 'anchor_probes']
    }
    coords = puw.get_value(quantities['coordinates'], to_unit='angstroms')
    radii = puw.get_value(quantities['atom_radii'], to_unit='angstroms')
    assert coords.shape == (4, 3)
    np.testing.assert_array_equal(radii, np.full(4, ATOM_RADIUS))
    for i in range(4):
        for j in range(i):
            assert np.linalg.norm(coords[i] - coords[j]) == pytest.approx(
                EDGE, rel=0, abs=REFERENCE_TOLERANCE
            )
    assert fixture['reference']['clearance_atol_angstroms'] == REFERENCE_TOLERANCE
    assert fixture['query']['min_size'] == 0
    assert (
        hashlib.sha256((artifact_dir / 'input.pdb').read_bytes()).hexdigest()
        == fixture['provider_input']['sha256']
    )


def test_public_tetrahedron_notebook_has_reviewed_report_and_executed_figures():
    notebook = json.loads((NOTEBOOK_DIR / 'regular_tetrahedron.ipynb').read_text())
    artifact_dir = NOTEBOOK_DIR / 'artifacts/regular_tetrahedron_v1'
    report = json.loads((artifact_dir / 'report.json').read_text())
    code_cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
    assert all(cell['execution_count'] is not None for cell in code_cells)
    outputs = [output for cell in code_cells for output in cell['outputs']]
    assert not any(output['output_type'] == 'error' for output in outputs)
    displayed_reports = [
        json.loads(''.join(output['data']['text/plain']))
        for cell in code_cells
        if 'topomt-reference-report' in cell.get('metadata', {}).get('tags', [])
        for output in cell['outputs']
        if 'text/plain' in output.get('data', {})
    ]
    assert displayed_reports == [report]
    assert sum('image/png' in output.get('data', {}) for output in outputs) == 2
    assert report['reference_checks'] == 'passed'
    assert (
        report['input_sha256']
        == hashlib.sha256((artifact_dir / 'input.json').read_bytes()).hexdigest()
    )
    expected_residence = EDGE * np.sqrt(6) / 4 - ATOM_RADIUS
    residence = QuantityRecord.from_dict(report['residence_clearance']).to_quantity(
        field='residence_clearance', unit='angstroms'
    )
    np.testing.assert_allclose(
        puw.get_value(residence, to_unit='angstroms'),
        expected_residence,
        rtol=0,
        atol=REFERENCE_TOLERANCE,
    )
    if report['provider']['status'] != 'completed':
        assert report['provider']['pocket_count'] is None
