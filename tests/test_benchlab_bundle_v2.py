"""The current reader download includes its independently importable checkers."""

import importlib.util
import zipfile
from pathlib import Path

from devtools.benchlab.study_bundle import verify_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_current_bundle_retains_v1_and_supplies_current_reader_and_reference_tree(
    tmp_path,
):
    from devtools.benchlab.study_bundle_v2 import build_bundle

    target = tmp_path / 'study.zip'
    manifest = build_bundle(ROOT, target, '8' * 40)
    assert manifest['reader_revision'] == 2
    assert manifest['topomt_source_revision'] == '8' * 40
    for case in ('regular_tetrahedron', 'closed_shell', 'shell_with_opening'):
        base = f'docs/content/benchlab/synthetic/{case}'
        for filename in (
            'system.ipynb',
            'dfnd.ipynb',
            'public_topography.ipynb',
            'public_topography_v2.ipynb',
        ):
            assert f'{base}/{filename}' in manifest['files']
    for module in (
        'verify_small_probe_regions.py',
        'verify_small_probe_boundary.py',
        'verify_origin_access_bracket.py',
        'verify_volume_reference.py',
        'benchlab/public_contract.py',
        'benchlab/capture_volume.py',
    ):
        assert f'devtools/{module}' in manifest['files']
    assert 'topomt/_version.py' not in manifest['files']
    with zipfile.ZipFile(target) as archive:
        assert 'public_topography_v2.ipynb' in archive.read('README_STUDY.md').decode()
        archive.extractall(tmp_path / 'received')
    assert verify_manifest(tmp_path / 'received') == manifest
    module = tmp_path / 'received/docs/content/benchlab/synthetic/public_study_v2.py'
    spec = importlib.util.spec_from_file_location('received_current_study', module)
    assert spec is not None and spec.loader is not None
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    case = module.parent / 'closed_shell'
    verified = study.references(case)
    assert verified['small_probe']['opening_component_count'] == 13
    assert verified['access_bracket']['desired_width_met']


def test_volume_receiving_rejects_a_reference_from_another_protocol(tmp_path):
    import json

    import pytest

    helper = ROOT / 'docs/content/benchlab/synthetic/public_study_v2.py'
    spec = importlib.util.spec_from_file_location('current_study', helper)
    assert spec is not None and spec.loader is not None
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    folder = tmp_path / 'artifacts/volume_study_v1'
    folder.mkdir(parents=True)
    (folder / 'protocol.json').write_text(json.dumps({'domains': []}))
    (folder / 'independent_reference.json').write_text(
        json.dumps({'domains': [], 'protocol_sha256': '0' * 64})
    )
    with pytest.raises(ValueError, match='protocol'):
        study.volumes(tmp_path)


def test_current_notebooks_preserve_frozen_cell_sources_and_passed_outputs():
    import hashlib
    import json

    import nbformat

    base = ROOT / 'docs/content/benchlab/synthetic'
    for case in ('regular_tetrahedron', 'closed_shell', 'shell_with_opening'):
        directory = base / case
        notebook = nbformat.read(directory / 'public_topography_v2.ipynb', 4)
        protocol = json.loads(
            (directory / 'artifacts/reader_route_v2/protocol.json').read_text()
        )
        sources = [(cell.cell_type, cell.source) for cell in notebook.cells]
        assert (
            hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
            == protocol['code_and_markdown_sha256']
        )
        codes = [cell for cell in notebook.cells if cell.cell_type == 'code']
        assert all(cell.execution_count is not None for cell in codes)
        assert not any(
            output.output_type == 'error' for cell in codes for output in cell.outputs
        )
