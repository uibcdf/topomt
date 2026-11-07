"""Independent references and reviewed outputs for the split tetrahedron study."""

import ast
import base64
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from pyunitwizard import QuantityRecord

from topomt import pyunitwizard as puw

CASE = (
    Path(__file__).resolve().parents[1]
    / 'docs/content/benchlab/synthetic/regular_tetrahedron'
)
STUDY = CASE / 'artifacts/native_study_v1'
INPUT = CASE / 'artifacts/regular_tetrahedron_v1/input.json'


def _scalar(record: dict, field: str, unit: str) -> float:
    quantity = QuantityRecord.from_dict(record).to_quantity(field=field, unit=unit)
    return float(puw.get_value(quantity, to_unit=unit))


def test_system_study_freezes_independent_expectations_for_the_same_input():
    reference = json.loads((STUDY / 'system_reference.json').read_text())
    fixture = json.loads(INPUT.read_text())
    assert reference['input_sha256'] == hashlib.sha256(INPUT.read_bytes()).hexdigest()
    edge = _scalar(fixture['edge'], 'edge', 'angstroms')
    expected_residence = edge * np.sqrt(6) / 4 - 1.7
    expected_gate = edge / np.sqrt(3) - 1.7
    expected_volume = edge**3 / (6 * np.sqrt(2))
    for field, expected, unit in [
        ('residence_clearance', expected_residence, 'angstroms'),
        ('face_clearance', expected_gate, 'angstroms'),
        ('cell_hull_volume', expected_volume, 'angstroms**3'),
    ]:
        assert _scalar(reference['reference'][field], field, unit) == pytest.approx(
            expected, rel=1e-12, abs=1e-12
        )
    assert reference['reference_checks'] == 'passed'
    for experiment, probe in zip(
        reference['experiments'], [1.2, 1.4, 1.7], strict=True
    ):
        assert _scalar(experiment['probe_radius'], 'probe_radius', 'angstroms') == probe
        assert experiment['resident'] == (probe < expected_residence)
        assert experiment['permeable_faces'] == (4 if probe < expected_gate else 0)


def test_native_study_matches_reference_and_exposes_reporting_filters():
    reference_bytes = (STUDY / 'system_reference.json').read_bytes()
    reference = json.loads(reference_bytes)
    report = json.loads((STUDY / 'dfnd_observations.json').read_text())
    assert report['reference_sha256'] == hashlib.sha256(reference_bytes).hexdigest()
    assert report['input_sha256'] == reference['input_sha256']
    assert report['reference_checks'] == 'passed'
    assert len(report['sweep']) == 81
    for observed, expected, family, links in zip(
        report['anchors'],
        reference['experiments'],
        ['percolating', 'void', 'non_resident'],
        [1, 0, 0],
        strict=True,
    ):
        assert observed['resident'] == expected['resident']
        assert observed['permeable_faces'] == expected['permeable_faces']
        assert observed['family'] == family
        assert observed['external_links'] == links
        assert observed['raw_component_count'] == int(expected['resident'])
        assert sum(observed['reported_counts'].values()) == int(expected['resident'])
    control = report['reporting_control']
    assert control['min_size'] == 2
    assert control['raw_component_count'] == 1
    assert control['reported_component_count'] == 0
    assert control['geometry_unchanged']
    assert 'provider_comparisons' not in report


@pytest.mark.parametrize(
    'name,tag,artifact',
    [
        ('system', 'topomt-system-reference', 'system_reference.json'),
        ('dfnd', 'topomt-native-study', 'dfnd_observations.json'),
    ],
)
def test_study_notebooks_have_executed_figures_and_matching_reviewed_records(
    name, tag, artifact
):
    notebook = json.loads((CASE / f'{name}.ipynb').read_text())
    cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
    assert cells and all(cell['execution_count'] is not None for cell in cells)
    outputs = [output for cell in cells for output in cell['outputs']]
    assert not any(output['output_type'] == 'error' for output in outputs)
    assert sum('image/png' in output.get('data', {}) for output in outputs) >= 2
    figures = {
        'system': ['system_geometry.png', 'system_thresholds.png'],
        'dfnd': ['dfnd_probes.png', 'dfnd_sweep.png'],
    }[name]
    pngs = [o['data']['image/png'] for o in outputs if 'image/png' in o.get('data', {})]
    for image, filename in zip(pngs, figures, strict=True):
        assert base64.b64decode(''.join(image)) == (STUDY / filename).read_bytes()
    displayed = [
        json.loads(''.join(output['data']['text/plain']))
        for cell in cells
        if tag in cell.get('metadata', {}).get('tags', [])
        for output in cell['outputs']
        if 'text/plain' in output.get('data', {})
    ]
    assert displayed == [json.loads((STUDY / artifact).read_text())]
    for cell in cells:
        tree = ast.parse(''.join(cell['source']))
        imports = [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ] + [
            node.module or ''
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        ]
        assert not any(
            m.startswith(('requests', 'urllib', 'subprocess')) for m in imports
        )
        if name == 'system':
            assert not any(m.startswith('topomt') for m in imports)
