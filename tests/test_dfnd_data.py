"""Tests for the topography.dfnd container (DFNDData), incl. probe re-query."""

import types

import numpy as np
import pytest

from topomt import pyunitwizard as puw
from topomt.dfnd import synthetic as syn
from topomt.dfnd.data import DFNDData
from topomt.dfnd.graph import DelaunayFlowNetwork


def _argon_cube_arrays():
    h = 6.56 / np.sqrt(3.0) / 2.0  # body diagonal 2*(1.88+1.4); centre clearance ~1.4
    cube = np.array(
        [
            [sx * h, sy * h, sz * h]
            for sx in (-1.0, 1.0)
            for sy in (-1.0, 1.0)
            for sz in (-1.0, 1.0)
        ]
    )
    return cube, np.full(8, 1.88)


def _n_void(result):
    return sum(
        1
        for c in result['raw']['wet_components']
        if c['family'] == 'void' and c['n_resident_nodes'] >= 1
    )


def _data(coords, radii, probe_radius=1.4):
    network = DelaunayFlowNetwork.from_coordinates_and_radii(coords, radii, epsilon=1e-7)
    result = network.get_topography(probe_radius=probe_radius, min_size=0)
    return DFNDData(network, result)


def _significant_voids(data):
    return [c for c in data.dfn.components.wet if c.family == 'void' and c.size >= 5]


def test_raw_records_declare_nm_schema_and_units():
    coords, radii = _argon_cube_arrays()
    network = DelaunayFlowNetwork.from_coordinates_and_radii(coords, radii, epsilon=1e-7)
    result = network.get_topography(probe_radius=1.4, min_size=0)
    raw = result['raw']

    assert raw['schema_version'] == 'dfnd.raw.nm.v2'
    assert raw['units']['length'] == 'nm'
    assert raw['units']['area'] == 'nm**2'
    assert raw['units']['volume'] == 'nm**3'
    assert raw['parameters']['probe_radius'] == pytest.approx(0.14)


def test_get_tetrahedra_returns_raw_records_by_id():
    data = object.__new__(DFNDData)
    data.raw = {
        'tetrahedra': [
            {'tetrahedron_id': 10, 'residence_state': 'resident'},
            {'tetrahedron_id': 20, 'residence_state': 'non_resident'},
        ]
    }
    data._network = types.SimpleNamespace(molecular_system=None)

    assert data.get_tetrahedron(10)['residence_state'] == 'resident'
    assert data.get_tetrahedra([20]) == [
        {'tetrahedron_id': 20, 'residence_state': 'non_resident'}
    ]
    assert data.get_tetrahedra(residence_state='non_resident') == [
        {'tetrahedron_id': 20, 'residence_state': 'non_resident'}
    ]


def test_at_probe_reuses_the_mesh_and_recomputes_the_decomposition():
    # The dumbbell: one void at a small probe, two voids when the throat closes.
    coords, radii = syn.dumbbell(7.0, 12.5, 3.5, jitter=0.1, seed=0)
    data = _data(coords, radii, probe_radius=1.4)
    reprobed = data.at_probe(puw.quantity(2.2, 'angstroms'))

    # the expensive mesh is shared, not rebuilt
    assert reprobed.network is data.network
    assert reprobed.mesh.delaunay is data.mesh.delaunay
    assert len(reprobed.mesh.tetrahedra) == len(data.mesh.tetrahedra)

    # but the probe-dependent decomposition is recomputed
    assert reprobed.dfn.parameters['probe_radius'] == pytest.approx(0.22)
    assert len(_significant_voids(data)) == 1  # connected through the throat
    assert len(_significant_voids(reprobed)) == 2  # throat closed -> two chambers


def test_at_probe_inherits_query_options():
    coords, radii = syn.hollow_sphere(10.0, 3.5, jitter=0.1, seed=0)
    network = DelaunayFlowNetwork.from_coordinates_and_radii(coords, radii, epsilon=1e-7)
    result = network.get_topography(
        probe_radius=1.4, min_size=0, transit_policy='resident_only'
    )
    data = DFNDData(network, result)

    reprobed = data.at_probe(puw.quantity(1.2, 'angstroms'))
    assert reprobed.dfn.parameters['transit_policy'] == 'resident_only'  # inherited


def _dominant_wet(data):
    return max(data.dfn.components.wet, key=lambda c: c.size)


def test_pocket_has_topological_depth_and_mouth_motif():
    # Canonical wet motifs (domain_motifs.md S3): a pocket has a depth gradient
    # from its exterior boundary, depth regions, and one external_mouth motif.
    coords, radii = syn.hollow_sphere_with_opening(10.0, 3.5, 30.0, jitter=0.1, seed=0)
    pocket = _dominant_wet(_data(coords, radii))

    assert pocket.family == 'pocket'
    assert min(pocket.topological_depth.values()) == 0  # boundary at depth 0
    assert max(pocket.topological_depth.values()) > 0  # a real depth gradient
    assert pocket.depth_regions
    n_mouths = sum(1 for m in pocket.motifs if m['motif_type'] == 'external_mouth')
    assert n_mouths == pocket.n_mouths == 1
    assert len(pocket.motifs) == n_mouths + len(pocket.depth_regions)


def test_void_has_no_mouth_motif_and_flat_depth():
    # A sealed void has no exterior boundary -> no external_mouth, uniform depth.
    coords, radii = syn.hollow_sphere(10.0, 3.5, jitter=0.1, seed=0)
    void = _dominant_wet(_data(coords, radii))

    assert void.family == 'void'
    assert set(void.topological_depth.values()) == {0}
    assert all(m['motif_type'] != 'external_mouth' for m in void.motifs)


def test_dumbbell_throat_and_chamber_motifs():
    # Experimental capacity-persistence motifs: the connected dumbbell void has one
    # dominant throat (the neck) separating two chambers (the lobes).
    coords, radii = syn.dumbbell(7.0, 12.5, 3.5, jitter=0.1, seed=0)
    void = _dominant_wet(_data(coords, radii, probe_radius=1.4))

    assert void.family == 'void'
    assert len(void.throat_candidates) == 1
    assert len(void.chamber_candidates) == 2
    assert void.bottleneck is not None
    # the throat is passable at the 1.4 probe but seals before 2.2 (-> 2 voids there)
    assert 0.14 <= void.bottleneck['R_gate'] < 0.22
    assert void.bottleneck['persistence'] > 0.1


def test_simple_void_has_no_throat():
    # A single sphere void is one basin -> no throat/chamber candidates.
    coords, radii = syn.hollow_sphere(10.0, 3.5, jitter=0.1, seed=0)
    void = _dominant_wet(_data(coords, radii))

    assert void.throat_candidates == []
    assert void.chamber_candidates == []
    assert void.bottleneck is None


def test_residence_tolerance_widens_the_residence_threshold():
    # A probe just above the deepest clearance is not resident at tolerance 0, but
    # becomes resident once residence_tolerance exceeds the gap (generous policy).
    coords, radii = _argon_cube_arrays()
    network = DelaunayFlowNetwork.from_coordinates_and_radii(coords, radii, epsilon=1e-7)
    # tetra_residence is nm (internal); bump just above the deepest clearance.
    probe = puw.quantity(float(network.tetra_residence.max()) + 0.01, 'nm')

    strict = network.get_topography(probe_radius=probe, min_size=0)
    generous = network.get_topography(
        probe_radius=probe, min_size=0, residence_tolerance=puw.quantity(0.02, 'nm')
    )
    assert _n_void(strict) == 0
    assert _n_void(generous) >= 1
    assert generous['raw']['parameters']['residence_tolerance'] == pytest.approx(0.02)


def test_tolerances_recorded_and_inherited_by_at_probe():
    coords, radii = _argon_cube_arrays()
    network = DelaunayFlowNetwork.from_coordinates_and_radii(coords, radii, epsilon=1e-7)
    result = network.get_topography(
        probe_radius=1.45,
        min_size=0,
        residence_tolerance=0.1,
        permeability_tolerance=0.2,
    )
    data = DFNDData(network, result)

    assert data.dfn.parameters['residence_tolerance'] == pytest.approx(0.01)
    assert data.dfn.parameters['permeability_tolerance'] == pytest.approx(0.02)
    reprobed = data.at_probe(puw.quantity(1.4, 'angstroms'))  # tolerances inherited
    assert reprobed.dfn.parameters['residence_tolerance'] == pytest.approx(0.01)
    assert reprobed.dfn.parameters['permeability_tolerance'] == pytest.approx(0.02)


def test_wet_component_initializes_motif_descriptors():
    from topomt.dfnd.components import WetComponent

    component = WetComponent(component_id='WET-1', family='void')

    assert component.topological_depth == {}
    assert component.depth_regions == []
    assert component.throat_candidates == []
    assert component.chamber_candidates == []
    assert component.bottleneck is None


@pytest.mark.parametrize(
    'kwargs, message',
    [
        ({'probe_radius': -0.1}, 'probe_radius'),
        ({'residence_tolerance': -0.1}, 'residence_tolerance'),
        ({'permeability_tolerance': -0.1}, 'permeability_tolerance'),
        ({'min_size': -1}, 'min_size'),
        ({'min_size': 1.5}, 'min_size'),
        ({'min_size': True}, 'min_size'),
    ],
)
def test_get_topography_rejects_invalid_physical_query_parameters(kwargs, message):
    coords, radii = _argon_cube_arrays()
    network = DelaunayFlowNetwork.from_coordinates_and_radii(coords, radii, epsilon=1e-7)

    with pytest.raises(ValueError, match=message):
        network.get_topography(**kwargs)


def test_info_queries_original_molecular_system_with_global_atom_indices(monkeypatch):
    import molsysmt as msm

    calls = []

    def fake_get(system, *, selection, **kwargs):
        calls.append((system, list(selection), kwargs))
        if kwargs.get('atom_name'):
            return ['A10', 'A20', 'A30', 'A40']
        if kwargs.get('residue_name'):
            return ['RES'] * 4
        if kwargs.get('residue_id'):
            return [1] * 4
        raise AssertionError(kwargs)

    monkeypatch.setattr(msm, 'get', fake_get)
    data = object.__new__(DFNDData)
    data._network = types.SimpleNamespace(molecular_system='original-system')
    data.raw = {
        'tetrahedra': [
            {
                'tetrahedron_id': 7,
                'local_atom_indices': [0, 1, 2, 3],
                'atom_indices': [10, 20, 30, 40],
            }
        ]
    }

    data.info(7)

    assert calls
    assert all(system == 'original-system' for system, _selection, _kwargs in calls)
    assert all(selection == [10, 20, 30, 40] for _system, selection, _kwargs in calls)


def test_info_presents_raw_nm_lengths_and_volumes_as_angstroms(capsys):
    data = object.__new__(DFNDData)
    data._network = types.SimpleNamespace(molecular_system=None)
    data.raw = {
        'tetrahedra': [
            {
                'tetrahedron_id': 3,
                'atom_indices': [10, 20, 30, 40],
                'volume_topological': 1.5,
                'volume_solvent_estimate': 1.25,
                'R_residence': 0.215,
            }
        ]
    }

    data.info(3)

    output = capsys.readouterr().out
    assert 'Topological Vol  : 1500.0 Å³' in output
    assert 'Solvent Est. Vol : 1250.0 Å³' in output
    assert 'Clearance (R_res): 2.150 Å' in output


def test_info_uses_global_indices_after_hydrogen_exclusion(tmp_path, monkeypatch):
    import molsysmt as msm

    pdb = tmp_path / 'hydrogen_first.pdb'
    pdb.write_text(
        '\n'.join(
            [
                'ATOM      1  H1  GLY A   1       9.000   9.000   9.000  1.00  0.00           H',
                'ATOM      2  C1  GLY A   1       0.000   0.000   0.000  1.00  0.00           C',
                'ATOM      3  C2  GLY A   1       4.000   0.000   0.000  1.00  0.00           C',
                'ATOM      4  C3  GLY A   1       0.000   4.000   0.000  1.00  0.00           C',
                'ATOM      5  C4  GLY A   1       0.000   0.000   4.000  1.00  0.00           C',
                'END',
                '',
            ]
        )
    )
    network = DelaunayFlowNetwork(str(pdb), hydrogen_policy='exclude')
    result = network.get_topography()
    record = result['raw']['tetrahedra'][0]
    assert record['local_atom_indices'] == [0, 1, 2, 3]
    assert record['atom_indices'] == [1, 2, 3, 4]

    selections = []

    def fake_get(_system, *, selection, **kwargs):
        selections.append(list(selection))
        if kwargs.get('atom_name'):
            return ['C1', 'C2', 'C3', 'C4']
        if kwargs.get('residue_name'):
            return ['GLY'] * 4
        if kwargs.get('residue_id'):
            return [1] * 4
        raise AssertionError(kwargs)

    monkeypatch.setattr(msm, 'get', fake_get)
    DFNDData(network, result).info(record['tetrahedron_id'])

    assert selections and all(selection == [1, 2, 3, 4] for selection in selections)
