"""The frozen straight tube is received through the public molecular boundary."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'docs/content/benchlab/synthetic/cylinder_tube'


def study_module():
    path = CASE / 'study.py'
    spec = importlib.util.spec_from_file_location('tube_study', path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_tube_keeps_full_precision_argon_radii_and_source_mapping():
    study = study_module()
    topo = study.receive(CASE, 1.2)
    from topomt import pyunitwizard as puw

    fixture = study.read(CASE / 'artifacts/cylinder_tube_v1/input.json')
    coords = study.quantity(fixture['coordinates'], 'coordinates')
    np.testing.assert_allclose(
        puw.get_value(topo.input_context.coordinates, to_unit='angstroms'),
        puw.get_value(coords, to_unit='angstroms'),
        rtol=0,
        atol=1e-13,
    )
    np.testing.assert_allclose(
        puw.get_value(topo.input_context.radii, to_unit='angstroms'),
        1.88,
        rtol=0,
        atol=1e-14,
    )
    assert topo.input_context.atom_indices.tolist() == list(range(81))
    assert topo.dfnd.raw['parameters']['query']['probe_radius'] == pytest.approx(0.12)


@pytest.mark.parametrize('probe', [1.2, 1.4])
@pytest.mark.xfail(
    strict=True,
    reason='topomt#180: bounded physical arrangement exhausts its work on this tube',
)
def test_actual_public_physical_counts_match_the_independent_two_end_reference(probe):
    study = study_module()
    topo = study.receive(CASE, probe)
    physical = topo.dfnd.raw['boundary_connectivity']
    assert physical['status'] == 'resolved'
    assert physical['n_patches'] == 2
    observed = study.describe(topo)
    assert observed['public_molecular_interface_validation'] == 'not_established'
    assert observed['node_inventory']['total'] == len(topo.dfnd.mesh.tetrahedra)


@pytest.mark.xfail(
    strict=True,
    reason='topomt#181: local candidates persist in an independently covered hull',
)
def test_large_probe_is_empty_without_erasing_dry_support_or_input_context():
    study = study_module()
    topo = study.receive(CASE, 2.5)
    assert not topo
    assert topo.input_context is not None
    assert not topo.dfnd.dfn.components.wet
    assert topo.dfnd.dfn.components.dry
    assert topo.dfnd.raw['boundary_connectivity']['n_patches'] == 0


def test_unresolved_physical_receiving_preserves_support_and_unknown_counts():
    study = study_module()
    topo = study.receive(CASE, 1.4)
    observed = study.describe(topo)
    physical = topo.dfnd.raw['boundary_connectivity']
    if physical['status'] == 'unresolved':
        assert physical['n_patches'] is None
        assert physical['reason']
    assert observed['node_inventory']['total'] == 445
    assert (
        sum(observed['node_inventory'][key] for key in ('wet_nodes', 'dry_nodes'))
        == 445
    )
    assert observed['public_features']
    candidates = study.inspect_centerlines(topo)
    assert candidates
    for candidate in candidates:
        assert candidate['native_is_collision_validated'] is False
        assert candidate['length_unit'] == 'angstroms'
        assert candidate['all_segments_clear'] == (candidate['probe_margin'] > 1e-6)
