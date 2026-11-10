"""Execute the published DFND worked example against independent geometry."""

import importlib.util
import json
import re
import shutil
from math import sqrt
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from topomt import pyunitwizard as puw

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'docs/content/dfnd/examples/tetrahedron.py'
INPUT = ROOT / (
    'docs/content/benchlab/synthetic/regular_tetrahedron/'
    'artifacts/regular_tetrahedron_v1'
)


def example_module(filename='tetrahedron.py'):
    spec = importlib.util.spec_from_file_location(
        'dfnd_documentation_example', EXAMPLE.parent / filename
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('length_unit', ['nm', 'pm'])
def test_worked_tetrahedron_matches_independent_reference_and_public_result(
    length_unit,
):
    with puw.context(standard_units=[length_unit, 'ps', 'radians']):
        results = example_module().analyze_tetrahedron(INPUT)
        assert list(results) == [1.2, 1.4, 1.7]
        for probe, name in [(1.2, 'percolating'), (1.4, 'void')]:
            topo = results[probe]
            feature = next(iter(topo.get_features(by='type', value=name)))
            component = topo.dfnd.dfn.components[feature.component_id]
            assert feature.source_id == component.component_key
            assert feature.support_key == component.support_key
            assert not topo.get_features(by='type', value='mouth')
            np.testing.assert_allclose(
                [tet['R_residence'] for tet in topo.dfnd.raw['tetrahedra']],
                [(sqrt(6) * 5.3 / 4 - 1.7) / 10],
                rtol=0,
                atol=1e-12,
            )
            np.testing.assert_allclose(
                [face['R_gate'] for face in topo.dfnd.raw['faces']],
                (5.3 / sqrt(3) - 1.7) / 10,
                rtol=0,
                atol=1e-12,
            )
        assert results[1.2].dfnd.raw['wet_components'][0]['n_external_links'] == 1
        assert results[1.4].dfnd.raw['wet_components'][0]['n_external_links'] == 0
        assert not results[1.7].dfnd.raw['wet_components']
        assert not list(results[1.7].values())
        original = results[1.4]
        reprobed = original.dfnd.at_probe(puw.quantity(1.7, 'angstroms'))
        assert reprobed.network is original.dfnd.network
        assert original.get_features(by='type', value='void')
        assert not reprobed.dfn.components.wet
        assert original.input_context.atom_indices.tolist() == [0, 1, 2, 3]


def test_worked_example_rejects_a_changed_frozen_input(tmp_path):
    shutil.copyfile(INPUT / 'input.pdb', tmp_path / 'input.pdb')
    fixture = json.loads((INPUT / 'input.json').read_text())
    fixture['coordinates']['values'][0][0] += 0.01
    (tmp_path / 'input.json').write_text(json.dumps(fixture))
    with pytest.raises(ValueError, match='frozen input'):
        example_module().analyze_tetrahedron(tmp_path)


def test_documented_public_inspection_and_query_blocks_execute(tmp_path, monkeypatch):
    input_directory = tmp_path / 'tetrahedron_input'
    input_directory.mkdir()
    for filename in ('input.json', 'input.pdb'):
        shutil.copyfile(INPUT / filename, input_directory / filename)
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(EXAMPLE.parent))
    namespace: dict[str, Any] = {}
    for page in (
        'worked_tetrahedron.md',
        'results_and_provenance.md',
        'scale_and_dynamics.md',
        'numerics_and_reproducibility.md',
        'measurements.md',
    ):
        if page == 'numerics_and_reproducibility.md':
            namespace['molecular_system'] = namespace[
                'topography'
            ].input_context.recover_molecular_system()
        source = (EXAMPLE.parent.parent / page).read_text()
        blocks = re.findall(r'^```python\n(.*?)^```$', source, re.M | re.S)
        assert blocks, f'No executable public example in {page}'
        for code in blocks:
            exec(compile(code, page, 'exec'), namespace)
    assert namespace['topography'].get_features(by='type', value='void')
    assert namespace['source_atom_indices'] == [0, 1, 2, 3]
    assert not namespace['larger'].dfn.components.wet
    # A successful result can have unavailable descriptors: the reader must
    # recover None rather than inventing a zero mouth or a fitted shape.
    metrics = namespace['metrics']
    for name in ('mouth_radius', 'occlusion', 'elongation', 'funnel'):
        assert metrics[name] is None


def test_documented_shared_face_and_many_cell_centroid_execute(tmp_path, monkeypatch):
    source = (
        ROOT / 'docs/content/benchlab/synthetic/closed_shell/artifacts/closed_shell_v1'
    )
    inputs = tmp_path / 'shell_input'
    inputs.mkdir()
    for name in ('input.json', 'input.pdb'):
        shutil.copyfile(source / name, inputs / name)
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(EXAMPLE.parent))
    namespace: dict[str, Any] = {}
    page = EXAMPLE.parent.parent / 'network_and_decomposition.md'
    blocks = re.findall(r'^```python\n(.*?)^```$', page.read_text(), re.M | re.S)
    assert blocks, 'The shared-face explanation needs its executable example'
    for code in blocks:
        exec(compile(code, str(page), 'exec'), namespace)
    pair = namespace['face_pair']
    assert {tuple(sorted(face['atom_indices'])) for face in pair} == {(13, 23, 26)}
    assert {face['permeability_state'] for face in pair} == {
        'permeable',
        'non_permeable',
    }
    assert not any(face['transit_edge'] for face in pair)
    component = namespace['shell_component']
    assert len(component.node_indices) > 1
    aggregate = namespace['resident_aggregate']
    assert aggregate['component_key'] == component.component_key
    assert aggregate['tetrahedron_ids'] == component.resident_node_indices
    assert (
        aggregate['transit_connector_tetrahedron_ids']
        == component.transit_connector_node_indices
    )
    assert (
        sum(
            row['component_key'] == component.component_key
            for row in namespace['shell_topography'].dfnd.raw['residence_regions']
        )
        == 1
    )
    np.testing.assert_allclose(
        puw.get_value(namespace['shell_void'].center, to_unit='nm'),
        namespace['centroid_nm'],
        rtol=0,
        atol=1e-13,
    )


def test_closed_shell_example_rejects_a_changed_input(tmp_path):
    (tmp_path / 'input.json').write_text('{}')
    with pytest.raises(ValueError, match='frozen input'):
        example_module('closed_shell.py').analyze_closed_shell(tmp_path)
