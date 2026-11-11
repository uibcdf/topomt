"""The fixed dumbbell reaches native/public supports without invented counts."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'docs/content/benchlab/synthetic/dumbbell'
ARTIFACTS = CASE / 'artifacts/dumbbell_v1'


def study_module():
    spec = importlib.util.spec_from_file_location('dumbbell_study', CASE / 'study.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dumbbell_reader_import_does_not_import_topomt():
    subprocess.run(
        [
            sys.executable,
            '-c',
            "import sys; import study; assert 'topomt' not in sys.modules",
        ],
        cwd=CASE,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize('probe, expected_components', [(1.4, 1), (2.2, 2)])
def test_named_anchors_reach_the_connected_and_separated_native_support(
    probe, expected_components
):
    study = study_module()
    topo = study.receive(CASE, probe)
    protocol = study.read(ARTIFACTS / 'protocol.json')
    anchors = study.quantity(protocol['anchors'], 'anchors')
    rows = study.inspect_anchors(topo, anchors)
    keys = {key for row in rows for key in row['wet_component_keys']}
    assert len(keys) == expected_components
    assert all(row['cell_hits'] for row in rows)
    assert all(row['physical_clearance_angstroms'] > probe + 1e-6 for row in rows)
    assert all(hit['side'] == 'wet' for row in rows for hit in row['cell_hits'])
    assert topo.input_context.atom_indices.tolist() == list(range(94))
    import pyunitwizard as puw

    np.testing.assert_allclose(
        puw.get_value(topo.input_context.radii, to_unit='angstroms'),
        1.88,
        rtol=0,
        atol=1e-14,
    )


def test_dumbbell_hierarchy_retains_support_and_actual_public_parent():
    study = study_module()
    topo = study.receive(CASE, 1.4)
    observed = study.inspect_hierarchy(topo)
    assert any(row['throats'] and row['chambers'] for row in observed['components'])
    assert observed['public_motif_keys_match_native']
    assert observed['standalone_chamber_children_promoted'] is False


def test_named_lobes_are_recoverable_in_the_actual_native_hierarchy():
    study = study_module()
    topo = study.receive(CASE, 1.4)
    anchors = study.quantity(
        study.read(ARTIFACTS / 'protocol.json')['anchors'], 'anchors'
    )
    points = study.inspect_anchors(topo, anchors)
    hierarchy = study.inspect_hierarchy(topo)
    parent = next(
        c
        for c in hierarchy['components']
        if c['component_key'] == points[0]['wet_component_keys'][0]
    )
    selected = []
    for point in points:
        cells = {h['tetrahedron_id'] for h in point['cell_hits']}
        matches = [
            c['motif_key'] for c in parent['chambers'] if cells & set(c['node_ids'])
        ]
        assert len(matches) == 1
        selected.append(matches[0])
    assert len(set(selected)) == 2
    assert any(set(t['child_chamber_keys']) == set(selected) for t in parent['throats'])


@pytest.mark.xfail(strict=True, reason='#180: bounded physical arrangement exhausted')
def test_excluded_dumbbell_hull_has_a_resolved_zero_physical_patch_count():
    topo = study_module().receive(CASE, 6.0)
    physical = topo.dfnd.raw['boundary_connectivity']
    assert physical['status'] == 'resolved'
    assert physical['n_patches'] == 0


def test_actual_dumbbell_anchor_mapping_respects_application_units():
    import pyunitwizard as puw

    study = study_module()
    with puw.context(standard_units=['pm', 'fs', 'radians']):
        topo = study.receive(CASE, 1.4)
        anchors = study.quantity(
            study.read(ARTIFACTS / 'protocol.json')['anchors'], 'anchors'
        )
        observed = study.inspect_anchors(topo, anchors)
        assert observed[0]['wet_component_keys'] == observed[1]['wet_component_keys']
        np.testing.assert_allclose(
            [r['physical_clearance_angstroms'] for r in observed],
            [4.9720422604301, 4.886156410738181],
            rtol=0,
            atol=1e-12,
        )


def test_excluded_dumbbell_retains_complete_dry_support_and_empty_public_result():
    topo = study_module().receive(CASE, 6.0)
    assert not topo.dfnd.dfn.components.wet
    assert len(topo) == 0
    observed = study_module().describe(topo)
    nodes = observed['node_inventory']
    assert nodes['wet_nodes'] == 0 and nodes['dry_nodes'] == nodes['total'] > 0
    assert topo.input_context.atom_indices.tolist() == list(range(94))
    assert topo.attribution['producer'] and topo.attribution['references']


def test_current_dumbbell_notebook_code_cells_parse_before_execution():
    import ast

    import nbformat

    for name in ('system', 'dfnd'):
        notebook = nbformat.read(CASE / f'{name}.ipynb', 4)
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type == 'code':
                ast.parse(cell.source, filename=f'{name}.ipynb cell {index}')


def test_reviewed_dumbbell_readers_bind_sources_and_have_successful_outputs():
    import hashlib
    import json

    import nbformat

    protocol = study_module().read(ARTIFACTS / 'reader_protocol.json')
    assert protocol['reader_revision'] == 2
    assert (
        hashlib.sha256(
            (ARTIFACTS / 'native_observations.json').read_bytes()
        ).hexdigest()
        == protocol['native_observations_sha256']
    )
    for name in ('system', 'dfnd'):
        notebook = nbformat.read(CASE / f'{name}.ipynb', 4)
        source = [(cell.cell_type, cell.source) for cell in notebook.cells]
        assert (
            hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()
            == protocol['notebooks'][name]
        )
        cells = [cell for cell in notebook.cells if cell.cell_type == 'code']
        assert all(cell.execution_count is not None for cell in cells)
        assert not any(o.output_type == 'error' for c in cells for o in c.outputs)
        html = [
            o.get('data', {}).get('text/html', '') for c in cells for o in c.outputs
        ]
        assert sum('<table' in output for output in html) >= 3
        assert all('hide-input' in c.metadata['tags'] for c in cells)


def test_complete_dumbbell_download_preserves_manifest_and_executable_case(tmp_path):
    import zipfile

    from devtools.benchlab.study_bundle import verify_manifest

    with zipfile.ZipFile(ROOT / 'docs/_static/benchlab/dumbbell_v1.zip') as archive:
        archive.extractall(tmp_path)
    manifest = verify_manifest(tmp_path)
    assert manifest['case'] == 'dumbbell'
    assert (
        manifest['topomt_source_revision']
        == study_module().read(ARTIFACTS / 'reader_protocol.json')[
            'topomt_source_revision'
        ]
    )
    for path in [
        'devtools/benchlab/ball_study.py',
        'devtools/verify_dumbbell_reference.py',
        'devtools/verify_tube_passage.py',
    ]:
        assert path in manifest['files']
    for name in ('system', 'dfnd'):
        path = str((CASE / f'{name}.ipynb').relative_to(ROOT))
        assert path in manifest['entry_notebooks']
        assert (tmp_path / path).read_bytes() == (ROOT / path).read_bytes()
