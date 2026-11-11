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
