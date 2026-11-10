"""The portable reader stage receives real public findings and references."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = ROOT / 'docs/content/benchlab/synthetic'


def study_module():
    spec = importlib.util.spec_from_file_location(
        'public_study', SYNTHETIC / 'public_study.py'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    'case,probe,kind,mouths',
    [
        ('regular_tetrahedron', 1.2, 'percolating', 0),
        ('closed_shell', 0.2, 'void', 0),
        ('shell_with_opening', 1.4, 'pocket', 1),
    ],
)
def test_public_reader_keeps_native_physical_and_reference_observations_separate(
    case, probe, kind, mouths
):
    study = study_module()
    topo = study.receive(SYNTHETIC / case, probe)
    assert len(topo.get_features(by='type', value=kind)) == 1
    assert len(topo.get_features(by='type', value='mouth')) == mouths
    assert study.describe(topo)['physical_view_status'] == 'not_available'
    verified = study.reference(SYNTHETIC / case)
    if case == 'regular_tetrahedron':
        assert verified['opening_component_count'] == 4
    elif case == 'shell_with_opening':
        assert verified['opening_component_count'] == 1
    else:
        assert verified['conclusion'] == 'origin_free_and_enclosed'


def test_reader_suppression_retains_raw_geometry_and_support():
    study = study_module()
    directory = SYNTHETIC / 'shell_with_opening'
    before = study.receive(directory, 1.4)
    cutoff = before.dfnd.raw['wet_components'][0]['n_nodes'] + 1
    after = study.receive(directory, 1.4, min_size=cutoff)
    assert not after
    assert (
        before.dfnd.raw['parameters']['result_key']
        == after.dfnd.raw['parameters']['result_key']
    )
    assert (
        before.dfnd.raw['wet_components'][0]['support_key']
        == after.dfnd.raw['wet_components'][0]['support_key']
    )


@pytest.mark.parametrize(
    'case', ['regular_tetrahedron', 'closed_shell', 'shell_with_opening']
)
def test_actual_reader_notebook_inspects_support_without_inventing_neutral_support(
    case,
):
    study = study_module()
    directory = SYNTHETIC / case
    notebook = json.loads((directory / 'public_topography.ipynb').read_text())
    namespace = {'case_directory': directory, 'study': study}
    from IPython.display import Markdown, display

    namespace.update(Markdown=Markdown, display=display)
    exec(''.join(notebook['cells'][3]['source']), namespace)
    expected = 1 if case == 'shell_with_opening' else 0
    assert (
        len(namespace['topography'].get_features(by='type', value='mouth')) == expected
    )
    assert namespace['vertices'].shape[1:] == (4, 3)


def test_study_notebooks_never_shadow_a_retained_sphinx_page():
    sources = [
        path
        for path in SYNTHETIC.rglob('*')
        if path.suffix in ('.md', '.rst', '.ipynb')
    ]
    names = [path.with_suffix('') for path in sources]
    assert len(names) == len(set(names)), (
        'Two source formats shadow the same public document URL'
    )


def test_public_summary_rejects_an_uncomputed_container():
    study = study_module()
    with pytest.raises(ValueError, match='DFND'):
        study.describe(study.tmt.Topography())
