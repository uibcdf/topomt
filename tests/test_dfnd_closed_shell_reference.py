"""Independent wall coverage and central-cavity reference for a sampled shell."""

import hashlib
import json
from pathlib import Path

import numpy as np
from pyunitwizard import QuantityRecord
from scipy.spatial import ConvexHull

from topomt import pyunitwizard as puw
from topomt.dfnd import DelaunayFlowNetwork

NOTEBOOK_DIR = Path(__file__).resolve().parents[1] / 'docs/content/showcase/dfnd'
ARTIFACT_DIR = NOTEBOOK_DIR / 'artifacts/closed_shell_v1'


def _input():
    fixture = json.loads((ARTIFACT_DIR / 'input.json').read_text())
    quantities = {
        field: QuantityRecord.from_dict(fixture[field]).to_quantity(
            field=field, unit='angstroms'
        )
        for field in ['coordinates', 'atom_radii', 'epsilon']
    }
    return fixture, quantities


def test_sampled_shell_has_independently_covered_boundary_and_free_center():
    fixture, quantities = _input()
    coords = puw.get_value(quantities['coordinates'], to_unit='angstroms')
    radii = puw.get_value(quantities['atom_radii'], to_unit='angstroms')
    hull = ConvexHull(coords)
    triangles = coords[hull.simplices]
    a = np.linalg.norm(triangles[:, 0] - triangles[:, 1], axis=1)
    b = np.linalg.norm(triangles[:, 1] - triangles[:, 2], axis=1)
    c = np.linalg.norm(triangles[:, 2] - triangles[:, 0], axis=1)
    areas = (
        np.linalg.norm(
            np.cross(
                triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
            ),
            axis=1,
        )
        / 2
    )
    face_cover_radii = a * b * c / (4 * areas)
    probe = fixture['reference']['certified_probe_angstroms']
    assert radii.min() + probe - face_cover_radii.max() > 0.1
    assert np.all(hull.equations[:, 3] < 0)
    assert np.min(np.linalg.norm(coords, axis=1) - radii) > probe
    # A negative coverage margin is inconclusive, rather than a proof of a leak.
    assert radii.min() + 0.2 - face_cover_radii.max() < 0


def test_dfnd_reports_a_sealed_component_containing_the_certified_center():
    fixture, quantities = _input()
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        quantities['coordinates'],
        quantities['atom_radii'],
        epsilon=quantities['epsilon'],
    )
    vertices = network.atom_coords[network.tetra_atoms]
    matrices = np.swapaxes(vertices[:, 1:] - vertices[:, :1], 1, 2)
    barycentric = np.linalg.solve(matrices, -vertices[:, 0, :, None])[:, :, 0]
    containing = np.flatnonzero(
        np.all(barycentric >= -1e-8, axis=1) & (np.sum(barycentric, axis=1) <= 1 + 1e-8)
    )
    assert len(containing) >= 1
    result = network.get_topography(
        probe_radius=puw.quantity(
            fixture['reference']['certified_probe_angstroms'], 'angstroms'
        ),
        **fixture['query'],
    )
    central_components = [
        component
        for component in result['raw']['wet_components']
        if set(map(int, containing)) & set(component['tetrahedron_ids'])
    ]
    assert len(central_components) == 1
    assert central_components[0]['family'] == 'void'
    assert central_components[0]['n_external_links'] == 0


def test_public_closed_shell_notebook_has_executed_reference_report():
    notebook = json.loads((NOTEBOOK_DIR / 'closed_shell.ipynb').read_text())
    report = json.loads((ARTIFACT_DIR / 'report.json').read_text())
    assert report['reference_checks'] == 'passed'
    assert (
        report['input_sha256']
        == hashlib.sha256((ARTIFACT_DIR / 'input.json').read_bytes()).hexdigest()
    )
    code_cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
    assert all(cell['execution_count'] is not None for cell in code_cells)
    outputs = [output for cell in code_cells for output in cell['outputs']]
    assert not any(output['output_type'] == 'error' for output in outputs)
    displayed = [
        json.loads(''.join(output['data']['text/plain']))
        for cell in code_cells
        if 'topomt-reference-report' in cell.get('metadata', {}).get('tags', [])
        for output in cell['outputs']
        if 'text/plain' in output.get('data', {})
    ]
    assert displayed == [report]
