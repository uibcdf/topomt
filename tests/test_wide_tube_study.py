"""The wide tube uses independent references and exact public input receiving."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'docs/content/benchlab/synthetic/straight_tube_wide_sparse'
ARTIFACTS = CASE / 'artifacts/straight_tube_wide_sparse_v1'


def study_module():
    spec = importlib.util.spec_from_file_location('wide_study', CASE / 'study.py')
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_shared_tube_reader_import_does_not_import_topomt():
    subprocess.run(
        [
            sys.executable,
            '-c',
            'import sys; import devtools.benchlab.tube_study; '
            "assert 'topomt' not in sys.modules",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_wide_reference_separates_matched_passage_and_finite_exclusion():
    from devtools.verify_tube_passage import verify_reference

    certificate = json.loads((ARTIFACTS / 'reference_certificate.json').read_text())
    result = verify_reference(
        ARTIFACTS / 'input.json', ARTIFACTS / 'protocol.json', certificate
    )
    assert result['path_minimum_clearance_angstroms'] > 2.5 + 1e-6
    assert result['model_reference']['exclusion']['5.0']['strictly_covered']
    assert [row['end_to_end_path'] for row in result['controls'][:2]] == [
        'certified'
    ] * 2


@pytest.mark.parametrize('probe', [1.4, 2.5])
def test_wide_boundary_reference_has_two_ends_and_no_free_side_wall(probe):
    from devtools.verify_tube_boundary import verify_boundary

    result = verify_boundary(
        ARTIFACTS / 'input.json',
        ARTIFACTS / f'boundary_{probe:g}A_protocol.json',
        json.loads((ARTIFACTS / f'boundary_{probe:g}A_certificate.json').read_text()),
    )
    assert result['opening_component_count'] == 2
    assert sorted(result['component_end_labels']) == ['negative_z', 'positive_z']
    assert (
        result['covered_wall_faces'] + result['end_faces']
        == result['complete_hull_faces']
    )


@pytest.mark.parametrize('probe', [1.4, 2.5, 5.0])
def test_wide_public_receiving_preserves_the_full_model_and_native_support(probe):
    study = study_module()
    topo = study.receive(CASE, probe)
    import pyunitwizard as puw

    fixture = study.read(ARTIFACTS / 'input.json')
    expected = study.quantity(fixture['coordinates'], 'coordinates')
    np.testing.assert_allclose(
        puw.get_value(topo.input_context.coordinates, to_unit='angstroms'),
        puw.get_value(expected, to_unit='angstroms'),
        rtol=0,
        atol=1e-13,
    )
    np.testing.assert_allclose(
        puw.get_value(topo.input_context.radii, to_unit='angstroms'),
        1.88,
        rtol=0,
        atol=1e-14,
    )
    assert topo.input_context.atom_indices.tolist() == list(range(77))
    observed = study.describe(topo)
    inventory = observed['node_inventory']
    assert inventory['wet_nodes'] + inventory['dry_nodes'] == inventory['total']
    assert inventory['total'] == len(topo.dfnd.mesh.tetrahedra)
    physical = topo.dfnd.raw['boundary_connectivity']
    if physical['status'] == 'unresolved':
        assert physical['n_patches'] is None and physical['reason']
    for candidate in study.inspect_centerlines(topo):
        assert candidate['native_is_collision_validated'] is False
        assert candidate['all_segments_clear'] == (candidate['probe_margin'] > 1e-6)


@pytest.mark.parametrize(
    'probe, expected',
    [
        (1.4, 2),
        pytest.param(
            2.5,
            2,
            marks=pytest.mark.xfail(
                strict=True,
                reason='#184: critical-section ordering within numerical margin',
            ),
        ),
        pytest.param(
            5.0,
            0,
            marks=pytest.mark.xfail(
                strict=True, reason='#180: bounded physical arrangement exhausted'
            ),
        ),
    ],
)
def test_wide_physical_boundary_matches_the_independent_reference(probe, expected):
    topo = study_module().receive(CASE, probe)
    physical = topo.dfnd.raw['boundary_connectivity']
    assert physical['status'] == 'resolved'
    assert physical['n_patches'] == expected
