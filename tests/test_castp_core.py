"""Tests for the internal CASTp implementation scaffold."""

import importlib

import numpy as np
import topomt as tmt
from types import SimpleNamespace

from topomt.delaunay_mesh import DelaunayMesh
from topomt.io.load_CASTp import load_CASTp
from topomt.methods.castp import castp
from topomt.methods.castp_core import components as castp_components
from topomt.methods.castp_core.components import _hidden_triangle
from topomt.methods.castp_core.geometry import (
    _castp_param_radii_for_labels,
    _protor_radii_for_labels,
    _weighted_face_size2_value,
    _weighted_hidden2,
)
from topomt.methods.castp_core.mouths import cluster_mouth_faces


def test_cluster_mouth_faces_splits_disconnected_openings():
    faces = [
        (0, 1, 2),
        (0, 2, 3),
        (10, 11, 12),
    ]

    clusters = cluster_mouth_faces(faces)

    assert len(clusters) == 2
    assert sorted(len(cluster) for cluster in clusters) == [1, 2]


def test_castp_delegates_to_castp_core(monkeypatch):
    castp_module = importlib.import_module('topomt.methods.castp')

    mesh = DelaunayMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        )
    )

    calls = {}

    class FakeGeometry:
        def __init__(self, mesh):
            self.mesh = mesh

    def fake_build_castp_geometry(molecular_system, selection, structure_indices, solvent_radius, radii_model):
        calls['geometry'] = (molecular_system, selection, structure_indices, solvent_radius, radii_model)
        return FakeGeometry(mesh)

    def fake_build_castp_feature_records(geometry, probe_radius):
        calls['components'] = (geometry, probe_radius)
        return [
            {
                'id': 1,
                'feature_type': 'pocket',
                'atom_indices': [1, 2, 3, 4],
                'center': np.array([0.1, 0.2, 0.3]),
                'volume': 2.5,
                'score': 2.5,
                'n_mouths': 1,
                'mouth_area': 1.25,
                'mouths': [],
                'tetrahedron_indices': [0],
            }
        ]

    monkeypatch.setattr(castp_module, 'build_castp_geometry', fake_build_castp_geometry)
    monkeypatch.setattr(castp_module, 'build_castp_feature_records', fake_build_castp_feature_records)

    feature_records, returned_mesh = castp(
        'fake-system',
        probe_radius=1.4,
        radii_model='protor',
    )

    assert calls['geometry'] == ('fake-system', 'molecule_type == "protein"', 0, 1.4, 'protor')
    assert calls['components'][0].mesh is mesh
    assert calls['components'][1] == 1.4
    assert returned_mesh is mesh
    assert len(feature_records) == 1
    assert feature_records[0]['feature_type'] == 'pocket'


def test_castp_defaults_to_protein_only_protor_geometry(monkeypatch):
    castp_module = importlib.import_module('topomt.methods.castp')

    mesh = DelaunayMesh(
        points=np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        )
    )

    calls = {}

    class FakeGeometry:
        def __init__(self, mesh):
            self.mesh = mesh

    def fake_build_castp_geometry(molecular_system, selection, structure_indices, solvent_radius, radii_model):
        calls['geometry'] = (molecular_system, selection, structure_indices, solvent_radius, radii_model)
        return FakeGeometry(mesh)

    def fake_build_castp_feature_records(geometry, probe_radius):
        return []

    monkeypatch.setattr(castp_module, 'build_castp_geometry', fake_build_castp_geometry)
    monkeypatch.setattr(castp_module, 'build_castp_feature_records', fake_build_castp_feature_records)

    castp('fake-system')

    assert calls['geometry'] == (
        'fake-system',
        'molecule_type == "protein"',
        0,
        1.4,
        'protor',
    )


def test_castp_param_radii_match_historical_table_and_defaults():
    radii = _castp_param_radii_for_labels(
        np.asarray(['ALA', 'ARG', 'SER', 'UNK', 'UNK'], dtype=object),
        np.asarray(['N', 'CZ', 'OG', 'XX', '1H'], dtype=object),
    )

    assert radii[0] == 1.625
    assert radii[1] == 1.125
    assert radii[2] == 1.535
    assert radii[3] == 1.8
    assert radii[4] == 1.2


def test_protor_radii_match_public_castpfold_table_and_fallbacks():
    radii = _protor_radii_for_labels(
        np.asarray(['ALA', 'GLY', 'SER', 'LYS', 'UNK', 'UNK'], dtype=object),
        np.asarray(['CA', 'CA', 'OG', 'NZ', 'XX', 'SD'], dtype=object),
        np.asarray(['C', 'C', 'O', 'N', 'C', 'S'], dtype=object),
        np.asarray([3, 3, 1, 1, 3, 2], dtype=int),
    )

    assert radii[0] == 1.88
    assert radii[1] == 1.88
    assert radii[2] == 1.46
    assert radii[3] == 1.64
    assert radii[4] == 1.88
    assert radii[5] == 1.77


def test_rank_driven_components_do_not_union_retained_tetrahedra_into_outside(monkeypatch):
    class FakeMesh:
        n_simplices = 2
        neighbors = np.asarray(
            [
                [1, -1, -1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        )
        simplex_atom_indices = np.asarray(
            [
                [0, 1, 2, 3],
                [1, 2, 3, 4],
            ],
            dtype=int,
        )

        @staticmethod
        def get_face_atoms(simplex_index, face_index):
            face_lookup = {
                (0, 0): (1, 2, 3),
                (1, 0): (1, 2, 3),
            }
            return face_lookup.get((int(simplex_index), int(face_index)), (0, 0, 0))

    geometry = SimpleNamespace(
        mesh=FakeMesh(),
        base_rank=1,
        simplex_rho_ranks=np.asarray([2, 2], dtype=int),
        face_rho_ranks=np.zeros((2, 4), dtype=int),
        face_mu1_ranks=np.full((2, 4), 2, dtype=int),
    )

    monkeypatch.setattr(
        castp_components,
        '_compute_pocket_depths',
        lambda geometry, empty_mask=None: np.asarray([2, 1], dtype=int),
    )

    components, blocked_nodes, depth = castp_components._build_rank_driven_components(
        geometry,
        np.asarray([True, True], dtype=bool),
        size_limit_rank=2,
    )

    assert depth.tolist() == [2, 1]
    assert blocked_nodes == {0}
    assert list(components.values()) == [[1]]


def test_build_castp_feature_records_uses_full_rank_window_for_component_assembly(monkeypatch):
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(),
        spectrum_values=np.asarray([0.0, 1.0, 2.0, 3.0], dtype=float),
    )

    calls = {}

    monkeypatch.setattr(
        castp_components,
        '_build_empty_simplex_mask',
        lambda geometry, probe_radius: np.asarray([True], dtype=bool),
    )
    monkeypatch.setattr(
        castp_components,
        '_probe_rank',
        lambda geometry, probe_radius: 2,
    )

    def fake_build_rank_driven_components(geometry, empty_mask, size_limit_rank):
        calls['assembly_rank'] = int(size_limit_rank)
        return {0: [0]}, set(), np.asarray([0], dtype=int)

    monkeypatch.setattr(
        castp_components,
        '_build_rank_driven_components',
        fake_build_rank_driven_components,
    )
    monkeypatch.setattr(
        castp_components,
        '_component_boundary_faces',
        lambda geometry, simplex_indices, blocked_nodes, depth, size_limit_rank: ([], []),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_atom_indices',
        lambda mesh, atom_indices_map, simplex_indices: [],
    )
    monkeypatch.setattr(
        castp_components,
        'component_center',
        lambda centers, simplex_indices: np.zeros(3, dtype=float),
    )
    monkeypatch.setattr(
        castp_components,
        'component_volume',
        lambda simplex_volumes, simplex_indices: 1.0,
    )
    monkeypatch.setattr(
        castp_components,
        'cluster_mouth_faces',
        lambda mouth_faces: [],
    )

    geometry.atom_indices_map = np.asarray([], dtype=int)
    geometry.atom_coordinates = np.zeros((0, 3), dtype=float)
    geometry.mesh.simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)
    geometry.mesh.simplex_centers = np.asarray([[0.0, 0.0, 0.0]], dtype=float)
    geometry.mesh.simplex_volumes = np.asarray([1.0], dtype=float)

    records = castp_components.build_castp_feature_records(geometry, probe_radius=1.4)

    assert calls['assembly_rank'] == 4
    assert len(records) == 1
    assert records[0]['feature_type'] == 'void'


def test_weighted_hidden2_matches_attached_vs_non_attached_triangle_cases():
    face_points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    face_weights = np.asarray([0.0, 0.0, 0.0], dtype=float)

    assert _weighted_hidden2(
        face_points,
        face_weights,
        np.asarray([0.5, 0.5, 0.1], dtype=float),
        0.0,
    ) > 0
    assert _weighted_hidden2(
        face_points,
        face_weights,
        np.asarray([0.0, 0.0, 1.0], dtype=float),
        0.0,
    ) == 0


def test_weighted_hidden2_reports_degenerate_case_separately():
    face_points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    face_weights = np.asarray([0.0, 0.0, 0.0], dtype=float)

    assert _weighted_hidden2(
        face_points,
        face_weights,
        np.asarray([0.0, 0.0, 0.0], dtype=float),
        0.0,
    ) == 2


def test_hidden_triangle_treats_degenerate_hidden2_as_not_hidden():
    class FakeMesh:
        simplex_atom_indices = np.asarray(
            [
                [0, 1, 2, 3],
                [0, 1, 2, 4],
            ],
            dtype=int,
        )
        weights = np.zeros(5, dtype=float)

        @staticmethod
        def get_face_atoms(simplex_index, face_index):
            return (0, 1, 2)

    geometry = SimpleNamespace(
        face_mu1_ranks=np.asarray([[2]], dtype=int),
        face_rho_ranks=np.asarray([[0]], dtype=int),
        simplex_rho_ranks=np.asarray([2, 2], dtype=int),
        mesh=FakeMesh(),
        atom_coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.0, 0.0],
            ],
            dtype=float,
        ),
    )

    assert _hidden_triangle(geometry, 0, 0, 1) is False


def test_castp_voids_match_oracle_for_1hiv():
    oracle_topography = load_CASTp(zip_file='topomt/data/CASTp_3.0_server/1hiv.zip')
    oracle_void_atoms = sorted(
        sorted(feature.atom_indices)
        for feature in oracle_topography.features.values()
        if feature.feature_type == 'void'
    )

    feature_records, _ = castp('topomt/data/HIV-1-Protease/CASTp_1hiv/1hiv.pdb')
    native_void_atoms = sorted(
        sorted(feature['atom_indices'])
        for feature in feature_records
        if feature['feature_type'] == 'void'
    )

    assert native_void_atoms == oracle_void_atoms


def test_castp_tcd_voids_include_oracle_34_and_40():
    oracle_topography = load_CASTp(zip_file='topomt/data/CASTp_3.0_server/1tcd.zip')
    target_voids = {
        feature.source_id: sorted(feature.atom_indices)
        for feature in oracle_topography.features.values()
        if feature.feature_type == 'void' and feature.source_id in {'Pocket 34', 'Pocket 40'}
    }

    feature_records, _ = castp('topomt/data/TcTIM/CASTp_1tcd/1tcd.pdb')
    native_voids = {
        tuple(sorted(feature['atom_indices']))
        for feature in feature_records
        if feature['feature_type'] == 'void'
    }

    assert tuple(target_voids['Pocket 34']) in native_voids
    assert tuple(target_voids['Pocket 40']) in native_voids


def test_weighted_face_size2_matches_unweighted_triangle_circumradius_squared():
    face_points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    face_weights = np.asarray([0.0, 0.0, 0.0], dtype=float)

    assert np.isclose(_weighted_face_size2_value(face_points, face_weights), 0.5)
