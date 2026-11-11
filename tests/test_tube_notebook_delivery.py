"""The public tube study remains independently replayable and byte identified."""

import hashlib
import json
import zipfile
from pathlib import Path

import nbformat

from devtools.benchlab.study_bundle import verify_manifest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'docs/content/benchlab/synthetic/cylinder_tube'


def test_tube_notebooks_retain_the_frozen_sources_and_successful_outputs():
    folder = CASE / 'artifacts/cylinder_tube_v1'
    protocol = json.loads((folder / 'notebook_protocol.json').read_text())
    for name in ('system', 'dfnd'):
        notebook = nbformat.read(CASE / f'{name}.ipynb', 4)
        sources = [(cell.cell_type, cell.source) for cell in notebook.cells]
        assert (
            hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
            == protocol['notebooks'][name]
        )
        cells = [cell for cell in notebook.cells if cell.cell_type == 'code']
        assert all(cell.execution_count is not None for cell in cells)
        assert not any(
            output.output_type == 'error' for cell in cells for output in cell.outputs
        )
        assert any(
            '<table' in output.get('data', {}).get('text/html', '')
            for cell in cells
            for output in cell.outputs
        ), 'Generated tables must render semantically in Jupyter and Sphinx'


def test_downloaded_tube_references_replay_with_only_the_supplied_helper_tree(tmp_path):
    with zipfile.ZipFile(
        ROOT / 'docs/_static/benchlab/cylinder_tube_v1.zip'
    ) as archive:
        archive.extractall(tmp_path)
    manifest = verify_manifest(tmp_path)
    assert manifest['case'] == 'cylinder_tube'
    assert (
        manifest['topomt_source_revision'] == 'b07a20ed0ee1533cc16a0b6e30ace73c2ab09ac4'
    )
    assert len(manifest['entry_notebooks']) == 2
    import importlib.util

    helper = tmp_path / CASE.relative_to(ROOT) / 'study.py'
    spec = importlib.util.spec_from_file_location('received_tube_study', helper)
    assert spec is not None and spec.loader is not None
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    verified = study.references(helper.parent)
    assert verified['passage']['path_minimum_clearance_angstroms'] > 1.4 + 1e-6
    assert verified['passage']['model_reference']['exclusion']['2.5'][
        'strictly_covered'
    ]
    assert all(
        row['opening_component_count'] == 2 for row in verified['boundary'].values()
    )
