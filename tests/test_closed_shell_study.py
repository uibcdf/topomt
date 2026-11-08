"""Independent controls and reviewed staged notebooks for the fixed shell."""

import ast
import base64
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from pyunitwizard import QuantityRecord
from scipy.spatial import ConvexHull

from topomt import pyunitwizard as puw

CASE = (
    Path(__file__).resolve().parents[1] / 'docs/content/benchlab/synthetic/closed_shell'
)
DATA = CASE / 'artifacts/native_study_v1'


def decode(record, field, unit):
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return np.asarray(puw.get_value(quantity, to_unit=unit))


def geometry(coords, radii, origin, direction):
    hull = ConvexHull(coords)
    triangles = coords[hull.simplices]
    a = np.linalg.norm(triangles[:, 0] - triangles[:, 1], axis=1)
    b = np.linalg.norm(triangles[:, 1] - triangles[:, 2], axis=1)
    c = np.linalg.norm(triangles[:, 2] - triangles[:, 0], axis=1)
    area = (
        np.linalg.norm(
            np.cross(
                triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
            ),
            axis=1,
        )
        / 2
    )
    delta = coords - origin
    projected = np.maximum(delta @ direction, 0)
    clearance = np.linalg.norm(delta - projected[:, None] * direction, axis=1) - radii
    return {
        'face_cover': a * b * c / (4 * area),
        'ray_clearance': clearance,
        'center_clearance': np.min(np.linalg.norm(delta, axis=1) - radii),
        'enclosing_radius': np.max(np.linalg.norm(delta, axis=1)),
        'origin_inside': np.all(
            hull.equations[:, :3] @ origin + hull.equations[:, 3] < 0
        ),
        'hull_volume': hull.volume,
    }


def inputs():
    fixture = json.loads((CASE / 'artifacts/closed_shell_v1/input.json').read_text())
    return (
        decode(fixture['coordinates'], 'coordinates', 'angstroms'),
        decode(fixture['atom_radii'], 'atom_radii', 'angstroms'),
    )


def test_closed_shell_protocol_preserves_input_and_historical_outputs():
    protocol = json.loads((DATA / 'protocol.json').read_text())
    for relative, expected in protocol['preserved_files'].items():
        assert hashlib.sha256((CASE / relative).read_bytes()).hexdigest() == expected
    assert not protocol['native_execution_before_reference']
    assert not protocol['provider_execution']
    assert [
        float(decode(e['probe_radius'], 'probe_radius', 'angstroms'))
        for e in protocol['experiments']
    ] == [0.05, 1.4, 5.0]
    assert (
        protocol['legacy_control']['expectation']
        == 'enclosure_unresolved_by_these_sufficient_bounds'
    )


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_closed_shell_reference_has_independent_open_enclosed_and_empty_controls(
    policy,
):
    reference = json.loads((DATA / 'system_reference.json').read_text())
    protocol = json.loads((DATA / 'protocol.json').read_text())
    with puw.context(standard_units=[*policy, 'radians']):
        coords, radii = inputs()
        origin = decode(protocol['origin'], 'origin', 'angstroms')
        direction = decode(
            protocol['escape_witness']['direction'], 'direction', 'dimensionless'
        )
        np.testing.assert_allclose(np.linalg.norm(direction), 1, rtol=0, atol=1e-14)
        observed = geometry(coords, radii, origin, direction)
        tolerance = float(
            decode(
                protocol['tolerances']['length_absolute'],
                'length_absolute',
                'angstroms',
            )
        )
        assert observed['origin_inside']
        assert observed['ray_clearance'].min() > 0.05 + tolerance
        assert radii.min() + 1.4 - observed['face_cover'].max() > tolerance
        assert observed['center_clearance'] > 1.4 + tolerance
        assert radii.min() + 5 - observed['enclosing_radius'] > tolerance
        assert radii.min() + 0.2 - observed['face_cover'].max() < 0
        actual = decode(
            reference['escape_witness']['per_atom_clearance'],
            'per_atom_clearance',
            'angstroms',
        )
        np.testing.assert_allclose(
            actual, observed['ray_clearance'], rtol=0, atol=1e-12
        )
        assert reference['reference_checks'] == 'passed'
        assert (
            reference['protocol_sha256']
            == hashlib.sha256((DATA / 'protocol.json').read_bytes()).hexdigest()
        )


def test_closed_shell_certificates_survive_rigid_motion():
    protocol = json.loads((DATA / 'protocol.json').read_text())
    coords, radii = inputs()
    origin = decode(protocol['origin'], 'origin', 'angstroms')
    direction = decode(
        protocol['escape_witness']['direction'], 'direction', 'dimensionless'
    )
    rotation = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    translation = np.array([3.0, -4.0, 5.0])
    before = geometry(coords, radii, origin, direction)
    after = geometry(
        coords @ rotation.T + translation,
        radii,
        origin @ rotation.T + translation,
        direction @ rotation.T,
    )
    for key in ('center_clearance', 'enclosing_radius', 'hull_volume'):
        np.testing.assert_allclose(before[key], after[key], rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(
        before['ray_clearance'], after['ray_clearance'], rtol=0, atol=1e-12
    )
    np.testing.assert_allclose(
        np.sort(before['face_cover']), np.sort(after['face_cover']), rtol=0, atol=1e-12
    )
    assert before['origin_inside'] and after['origin_inside']


def test_closed_shell_native_observations_match_the_certified_scope():
    report = json.loads((DATA / 'dfnd_observations.json').read_text())
    assert (
        report['reference_sha256']
        == hashlib.sha256((DATA / 'system_reference.json').read_bytes()).hexdigest()
    )
    assert report['reference_checks'] == 'passed'
    small, sealed, large = report['anchors']
    assert small['central_external_links'] > 0 and small['central_resident_nodes'] > 0
    assert sealed['central_family'] == 'void' and sealed['central_external_links'] == 0
    assert sealed['central_resident_nodes'] > 0
    assert large['raw_component_count'] == large['resident_node_count'] == 0
    assert (
        report['legacy_control']['reference_disposition']
        == 'enclosure_unresolved_by_these_sufficient_bounds'
    )
    assert len(report['sweep']) == 49
    for a, b in zip(report['sweep'], report['sweep'][1:]):
        assert set(b['resident_tetrahedron_ids']) <= set(a['resident_tetrahedron_ids'])
    control = report['reporting_control']
    assert control['geometry_unchanged'] and control['raw_central_component_retained']
    assert control['reported_component_count'] == 0
    assert 'provider_comparisons' not in report


def test_closed_shell_execution_receipt_matches_reviewed_notebooks_and_artifacts():
    receipt = json.loads((DATA / 'execution_receipt.json').read_text())
    for name, entry in receipt['notebooks'].items():
        assert (
            hashlib.sha256((CASE / f'{name}.ipynb').read_bytes()).hexdigest()
            == entry['sha256']
        )
    for name, expected in receipt['artifact_sha256'].items():
        assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == expected
    assert (
        receipt['limits']['os_cpu_affinity_count']
        == receipt['limits']['numerical_workers']
        == 1
    )
    with puw.context(standard_units=['pm', 'fs', 'radians']):
        report = json.loads((DATA / 'dfnd_observations.json').read_text())
        probes = [
            float(decode(entry['probe_radius'], 'probe_radius', 'angstroms'))
            for entry in report['anchors']
        ]
        np.testing.assert_allclose(probes, [0.05, 1.4, 5.0], rtol=0, atol=1e-14)
        volume = float(
            decode(
                report['anchors'][1]['central_solvent_volume_estimate'],
                'central_solvent_volume_estimate',
                'angstroms**3',
            )
        )
        assert np.isfinite(volume) and volume >= 0


@pytest.mark.parametrize(
    'name,tag,record,figures',
    [
        (
            'system',
            'topomt-closed-shell-reference',
            'system_reference.json',
            ['system_geometry.png', 'system_certificates.png'],
        ),
        (
            'dfnd',
            'topomt-closed-shell-native',
            'dfnd_observations.json',
            ['dfnd_probes.png', 'dfnd_sweep.png'],
        ),
    ],
)
def test_closed_shell_stages_have_reviewed_figures_and_no_provider_execution(
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
        tree = ast.parse(''.join(cell['source']))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not any(
                    alias.name.startswith(('subprocess', 'requests', 'urllib'))
                    for alias in node.names
                )
                if name == 'system':
                    assert not any(
                        alias.name.startswith('topomt') for alias in node.names
                    )
            if isinstance(node, ast.ImportFrom) and name == 'system':
                assert not (node.module or '').startswith('topomt')
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {
                    'get_provider_output',
                    'write_text',
                    'write_bytes',
                    'save',
                    'Popen',
                }
