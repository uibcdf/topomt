"""Tests for the internal CASTp implementation scaffold."""

import importlib
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pytest
import topomt as tmt
from types import SimpleNamespace

from topomt.delaunay_mesh import DelaunayMesh
from topomt.io.load_CASTp import load_CASTp
from topomt.third_party.castp._native_impl import castp
from topomt.third_party.castp.core.castp_core import (
    build_castp_geometry,
    components as castp_components,
)
from topomt.third_party.castp.core.castp_core.components import (
    ALF_POC_BURIED,
    ALF_POC_MOUTH,
    ALF_POC_RANK,
    ALF_POC_TETRA,
    ALF_POC_UNION_SAME,
    ALF_POC_UNION_TWO,
    _component_edge_partitions,
    _component_face_partitions,
    _build_rank_driven_components,
    _build_void_components,
    _compute_pocket_depths,
    _iter_master_tetra_rho_indices,
    castp1_pocket_metric_signatures,
    _component_regular_vertex_indices,
    _component_vertex_partitions,
    _geometry_max_rank,
    _handle_tetra_pocket,
    _handle_tetra_seq,
    _hidden_triangle,
    _probe_rank,
)
from topomt.third_party.castp.core.castp_core.exact import (
    ExactRatio,
    castp1_fixed_point_array,
    castp1_fixed_point_int,
    exact_determinant,
    fixed_point_array,
    fixed_point_int,
)
from topomt.third_party.castp.core.castp_core.geometry import (
    ALF_EDGE,
    ALF_MU1,
    ALF_RHO,
    ALF_TETRA,
    ALF_TRIANGLE,
    ALF_VERTEX,
    CastpMasterEntry,
    _build_exact_rho_rank_tables,
    _build_master_entries,
    _simplex_rank_sublists,
    _build_spectrum_values,
    _castp1_pdb2alf_radii_for_pdb_path,
    _castp_param_radii_for_labels,
    _deduplicate_weighted_points,
    _discard_redundant_weighted_points,
    _exact_threshold_ratio,
    _edge_exact_ratio,
    _edge_mu_rank_maps,
    _edge_is_in_complex_at,
    _face_exact_ratio,
    _fixed_point_lifted_rows,
    _protor_radii_for_labels,
    _infer_weighted_decimal_places,
    _rank_of_ratio,
    _rank_table_is_in_complex,
    _rank_table_is_interior,
    _simplex_exact_ratio,
    _vertex_mu_rank_arrays,
    _weighted_edge_center_and_power,
    _weighted_face_center_and_power,
    _weighted_hidden0,
    _weighted_hidden1,
    _weighted_face_size2_value,
    _weighted_hidden2,
)
from topomt.third_party.castp.core.castp_core.mouths import (
    EdgeFacetRecord,
    MouthFaceRecord,
    _edge_facet_enext,
    _edge_facet_fnext,
    _make_edge_facet,
    _mouth_face_initial_edge_facets,
    _mouth_face_edge_facets,
    _mouth_face_outward_atoms,
    _fnext_walk_around_edge,
    cluster_mouth_faces,
)
from topomt.third_party.castp.core.castp_core.volbl import (
    VolblMetricContext,
    envelope_measurements,
    fringe_measurements_cx,
    shape_volume,
    space_filling_measurements,
    volbl_measurements,
    voids_measurements,
)
from topomt.weighted_delaunay_mesh import WeightedDelaunayMesh
from topomt.third_party.castp.core.castp_core.metrics import component_area, mouth_perimeter


def _extract_castp_server_pdb(zip_path: str | Path, tmp_dir: str) -> str:
    """Extract the PDB payload from a CASTp server ZIP and return its path."""

    with zipfile.ZipFile(zip_path) as archive:
        pdb_name = next(name for name in archive.namelist() if name.lower().endswith('.pdb'))
        archive.extract(pdb_name, path=tmp_dir)
    return f'{tmp_dir}/{pdb_name}'


def _feature_atom_sets(topography_or_records) -> dict[str, set[tuple[int, ...]]]:
    """Return comparable feature-atom sets keyed by feature type."""

    result = {}

    if hasattr(topography_or_records, 'features'):
        for feature in topography_or_records.features.values():
            if feature.feature_type == 'mouth':
                continue
            result.setdefault(feature.feature_type, set()).add(tuple(sorted(feature.atom_indices)))
        return result

    for feature in topography_or_records:
        result.setdefault(feature['feature_type'], set()).add(tuple(sorted(feature['atom_indices'])))
    return result


def _tetra_rho_master(rank_to_tetrahedra: dict[int, list[int]]):
    """Return a minimal tetra-rho master-list fixture."""

    entries = []
    offsets = {}
    for rank in sorted(rank_to_tetrahedra):
        start = len(entries)
        for simplex_index in rank_to_tetrahedra[rank]:
            entries.append(
                SimpleNamespace(
                    rank=int(rank),
                    f_type=ALF_TETRA,
                    r_type=ALF_RHO,
                    index=int(simplex_index),
                )
            )
        offsets[int(rank)] = (start, len(entries))
    return entries, offsets


CASTP1_ORACLE_CASES = [
    '1crn',
    '1rop',
    '2pk4',
    '1pht',
    '1ubq',
    '1stp',
    '1lyz',
    '2lyz',
    '1mbn',
]


CASTP1_VOLBL_ORACLE_TOTALS = {
    '1crn': {
        'Vsf_sa': 8806.427,
        'Vsf_ms': 5076.477,
        'Vtv_sa': 0.0,
        'Vtv_ms': 0.0,
        'Vtiv': 0.0,
        'Vof_sa': 6054.747,
        'Vof_ms': 2324.796,
        'Vsh': 2751.681,
        'Asf_sa': 3013.097,
        'Asf_ms': 2331.009,
        'Atv_sa': 0.0,
        'Atv_ms': 0.0,
        'Aof_sa': 3013.097,
        'Aof_ms': 2331.009,
        'Lsf': 1372.335,
        'Ltv': 0.0,
        'Lof': 1372.335,
        'Csf': 458,
        'Ctv': 0,
        'Cof': 458,
        'void_count': 0,
    },
    '2pk4': {
        'Vsf_sa': 20654.25,
        'Vsf_ms': 12394.57,
        'Vtv_sa': 0.000304,
        'Vtv_ms': 13.94116,
        'Vtiv': 10.91916,
        'Vof_sa': 12455.52,
        'Vof_ms': 4209.772,
        'Vsh': 8187.817,
        'Asf_sa': 6558.904,
        'Asf_ms': 5394.201,
        'Atv_sa': 0.042880,
        'Atv_ms': 28.38051,
        'Aof_sa': 6558.861,
        'Aof_ms': 5365.820,
        'Lsf': 2759.121,
        'Ltv': 1.236587,
        'Lof': 2757.885,
        'Csf': 858,
        'Ctv': 4,
        'Cof': 854,
        'void_count': 1,
    },
}


def _parse_castp1_feature_file(
    path: Path,
) -> list[dict[str, set[tuple[int, ...]]]]:
    """Parse a CASTp 1.0 `.poc` or `.voids` structural feature file."""

    fields = ['iT', 'iF', 'rF', 'iE', 'rE', 'iV', 'rV']
    components = []
    current = None

    with path.open() as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('**'):
                if current is not None:
                    components.append(current)
                current = {field: [] for field in fields}
                continue
            if current is None:
                continue
            parts = line.split()
            field = parts[0]
            if field in current:
                current[field].append(
                    tuple(sorted(int(value) for value in parts[1:]))
                )

    if current is not None:
        components.append(current)

    return [
        {field: set(values) for field, values in component.items()}
        for component in components
    ]


def _castp1_oracle_paths(
    case_id: str,
) -> tuple[int, int | None, Path | None, Path | None]:
    """Return explicit CASTp 1.0 ranks and oracle paths for one local case."""

    case_dir = Path('sandbox/castp_oracle_runs') / case_id
    poc_path = next(case_dir.glob(f'{case_id}.*.*.poc'), None)
    voids_path = next(case_dir.glob(f'{case_id}.*.voids'), None)

    if poc_path is not None:
        _stem, alpha_rank, beta_rank = poc_path.stem.split('.')
        return int(alpha_rank), int(beta_rank), poc_path, voids_path

    if voids_path is not None:
        _stem, alpha_rank = voids_path.stem.split('.')
        return int(alpha_rank), None, poc_path, voids_path

    raise FileNotFoundError(f'No CASTp 1.0 oracle files found for {case_id}')


def _castp1_component_key(
    component: dict[str, set[tuple[int, ...]]],
) -> frozenset[tuple[int, ...]]:
    """Return the component identity used by CASTp 1.0 structural files."""

    return frozenset(component['iT'])


def _native_castp1_component_sets(
    geometry,
    record,
) -> dict[str, set[tuple[int, ...]]]:
    """Return native feature fields in CASTp 1.0 one-based atom numbering."""

    mesh = geometry.mesh
    atom_map = geometry.atom_indices_map
    component = {
        'iT': {
            tuple(
                sorted(
                    int(atom_map[atom_index]) + 1
                    for atom_index in mesh.simplex_atom_indices[int(simplex_index)]
                )
            )
            for simplex_index in record.get('iT', [])
        },
    }

    for field in ['iF', 'rF']:
        component[field] = {
            tuple(sorted(int(atom_index) + 1 for atom_index in face))
            for face in record.get(field, [])
        }

    for field in ['iE', 'rE']:
        component[field] = {
            tuple(sorted(int(atom_index) + 1 for atom_index in edge))
            for edge in record.get(field, [])
        }

    for field in ['iV', 'rV']:
        component[field] = {
            (int(atom_index) + 1,)
            for atom_index in record.get(field, [])
        }

    return component


def _assert_castp1_components_match(
    native_components,
    oracle_components,
    case_id,
    label,
):
    """Assert exact CASTp 1.0 component and field parity."""

    native_by_key = {
        _castp1_component_key(component): component
        for component in native_components
    }
    oracle_by_key = {
        _castp1_component_key(component): component
        for component in oracle_components
    }

    assert native_by_key.keys() == oracle_by_key.keys(), (
        case_id,
        label,
        {
            'native_only': [
                sorted(key)
                for key in native_by_key.keys() - oracle_by_key.keys()
            ],
            'oracle_only': [
                sorted(key)
                for key in oracle_by_key.keys() - native_by_key.keys()
            ],
        },
    )

    for key in oracle_by_key:
        native_component = native_by_key[key]
        oracle_component = oracle_by_key[key]
        for field in ['iF', 'rF', 'iE', 'rE', 'iV', 'rV']:
            assert native_component[field] == oracle_component[field], (
                case_id,
                label,
                field,
                {
                    'native_only': sorted(
                        native_component[field] - oracle_component[field]
                    ),
                    'oracle_only': sorted(
                        oracle_component[field] - native_component[field]
                    ),
                },
            )


def test_cluster_mouth_faces_splits_disconnected_openings():
    faces = [
        (0, 1, 2),
        (0, 2, 3),
        (10, 11, 12),
    ]

    # (0,1,2) and (0,2,3) share edge (0,2) → 2 clusters
    clusters = cluster_mouth_faces(faces)
    assert len(clusters) == 2
    assert sorted(len(cluster) for cluster in clusters) == [1, 2]

    # edge_rho_ranks / rank1 are accepted but not yet used as a filter
    clusters_with_ranks = cluster_mouth_faces(faces, edge_rho_ranks={(0, 2): 1}, rank1=1)
    assert len(clusters_with_ranks) == 2


def test_cluster_mouth_faces_accepts_mouth_face_records():
    faces = [
        MouthFaceRecord(face_atoms=(0, 1, 2), simplex_index=0, face_index=0),
        MouthFaceRecord(face_atoms=(0, 2, 3), simplex_index=1, face_index=1),
        MouthFaceRecord(face_atoms=(10, 11, 12), simplex_index=2, face_index=2),
    ]

    clusters = cluster_mouth_faces(faces)

    assert len(clusters) == 2
    assert sorted(len(cluster) for cluster in clusters) == [1, 2]


def test_cluster_mouth_faces_rejects_tuple_faces_in_canonical_fnext_path():
    faces = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    with pytest.raises(ValueError, match='MouthFaceRecord inputs'):
        cluster_mouth_faces(
            faces,
            mesh=object(),
            depth=np.asarray([0, 1], dtype=int),
            infinity_marker=2,
        )


def test_make_edge_facet_prefers_local_face_index_over_atom_lookup():
    class FakeMesh:
        simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)

        @staticmethod
        def get_face_index(simplex_index, face_index):
            lookup = {
                (0, 3): 55,
            }
            return lookup[(int(simplex_index), int(face_index))]

        @staticmethod
        def get_face_index_from_atoms(face_atoms):
            raise AssertionError('Should not fall back to atom-based triangle lookup for a local face')

    edge_facet = _make_edge_facet(0, 1, 2, 0, FakeMesh())

    assert edge_facet == EdgeFacetRecord(
        oriented_face_atoms=(0, 1, 2),
        face_atoms=(0, 1, 2),
        triangle_index=55,
        simplex_index=0,
    )


def test_delaunay_mesh_face_indices_roundtrip_through_face_atoms():
    mesh = DelaunayMesh(
        points=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        )
    )

    face_indices = {
        mesh.get_face_index(0, face_index)
        for face_index in range(4)
    }

    assert len(face_indices) == 4
    for face_index in range(4):
        face_atoms = mesh.get_face_atoms(0, face_index)
        assert mesh.get_face_index_from_atoms(face_atoms) == mesh.get_face_index(0, face_index)
        assert mesh.get_face_owner_indices(0, face_index) == (0, -1)


def test_castp_delegates_to_castp_core(monkeypatch):
    castp_module = importlib.import_module('topomt.third_party.castp._native_impl')

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

    def fake_build_castp_feature_records(geometry, probe_radius, alpha_rank=None, beta_rank=None):
        calls['components'] = (geometry, probe_radius, alpha_rank, beta_rank)
        return [
            {
                'id': 1,
                'feature_type': 'pocket',
                'atom_indices': [1, 2, 3, 4],
                'iF': [(1, 2, 3)],
                'rF': [(1, 2, 4)],
                'iE': [(1, 2)],
                'rE': [(1, 4)],
                'iV': [2],
                'rV': [1, 4],
                'center': np.array([0.1, 0.2, 0.3]),
                'area': 9.75,
                'volume': 2.5,
                'score': 2.5,
                'n_mouths': 1,
                'mouth_area': 1.25,
                'mouth_perimeter': 4.5,
                'mouths': [
                    {
                        'id': 1,
                        'atom_indices': [1, 2],
                        'area': 1.25,
                        'perimeter': 4.5,
                        'faces': [(0, 1, 2)],
                        'triangle_indices': [17],
                    }
                ],
                'iT': [0],
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

    assert calls['geometry'] == ('fake-system', 'all', 0, 1.4, 'protor')
    assert calls['components'][0].mesh is mesh
    assert calls['components'][1:] == (1.4, None, None)
    assert returned_mesh is mesh
    assert len(feature_records) == 1
    assert feature_records[0]['feature_type'] == 'pocket'
    assert feature_records[0]['iT'] == [0]
    assert feature_records[0]['tetrahedron_indices'] == [0]
    assert feature_records[0]['area'] == 9.75
    assert feature_records[0]['mouth_perimeter'] == 4.5
    assert feature_records[0]['mouths'][0]['perimeter'] == 4.5
    assert feature_records[0]['mouths'][0]['triangle_indices'] == [17]
    assert feature_records[0]['iF'] == [(1, 2, 3)]
    assert feature_records[0]['rF'] == [(1, 2, 4)]
    assert feature_records[0]['iE'] == [(1, 2)]
    assert feature_records[0]['rE'] == [(1, 4)]
    assert feature_records[0]['iV'] == [2]
    assert feature_records[0]['rV'] == [1, 4]


def test_castp_defaults_to_all_atoms_and_historical_param_radii(monkeypatch):
    castp_module = importlib.import_module('topomt.third_party.castp._native_impl')

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

    def fake_build_castp_feature_records(geometry, probe_radius, alpha_rank=None, beta_rank=None):
        return []

    monkeypatch.setattr(castp_module, 'build_castp_geometry', fake_build_castp_geometry)
    monkeypatch.setattr(castp_module, 'build_castp_feature_records', fake_build_castp_feature_records)

    castp('fake-system')

    assert calls['geometry'] == (
        'fake-system',
        'all',
        0,
        1.4,
        'castp_param',
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


def test_castp1_pdb2alf_radii_parse_pdb_fixed_fields_and_defaults(tmp_path):
    pdb_path = tmp_path / 'input.pdb'
    pdb_path.write_text(
        '\n'.join(
            [
                'ATOM      1  N   THR A   1      17.047  14.099   3.625  1.00 13.79           N  ',
                'ATOM      2  OG1 THR A   1      19.334  12.829   4.463  1.00 15.06           O  ',
                'ATOM      3  N1    A A   2      20.000  12.000   4.000  1.00 15.06           N  ',
                'ATOM      4  XX  UNK A   3      21.000  12.000   4.000  1.00 15.06           C  ',
                'ATOM      5 1H   UNK A   3      22.000  12.000   4.000  1.00 15.06           H  ',
                '',
            ]
        ),
        encoding='utf-8',
    )

    radii = _castp1_pdb2alf_radii_for_pdb_path(pdb_path)

    assert radii.tolist() == [1.625, 1.535, 1.625, 1.8, 1.2]


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


def test_build_spectrum_values_uses_only_rho_events():
    spectrum_values = _build_spectrum_values(
        np.asarray([-3.5, -2.8], dtype=float),
        np.asarray([[0.0, -2.5, 0.0, 0.0]], dtype=float),
        np.asarray([-4.0], dtype=float),
        np.asarray([-5.0, -1.0], dtype=float),
    )

    assert np.all(np.diff(spectrum_values) > 0.0)
    assert tuple(spectrum_values.tolist()) == (-5.0, -4.0, -3.5, -2.8, -2.5, -1.0)
    assert 0.0 not in spectrum_values


def test_simplex_rank_sublists_group_tetrahedra_by_rank():
    sublists = _simplex_rank_sublists(np.asarray([3, 1, 3, 2, 2], dtype=int))

    assert sublists == {
        1: [1],
        2: [3, 4],
        3: [0, 2],
    }


def test_build_master_entries_groups_and_sorts_rank_sublists():
    master_entries, master_rank_offsets, simplex_rank_sublists = _build_master_entries(
        simplex_rho_ranks=np.asarray([3, 1], dtype=int),
        face_rho_ranks=np.asarray([[0], [2]], dtype=int),
        face_mu1_ranks=np.asarray([[3], [2]], dtype=int),
        face_mu2_ranks=np.asarray([[0], [3]], dtype=int),
        edge_rho_ranks={(0, 1): 0, (0, 2): 2},
        edge_mu1_ranks={(0, 1): 3, (0, 2): 2},
        edge_mu2_ranks={(0, 1): 0, (0, 2): 3},
        vertex_rho_ranks=np.asarray([1, 1, 1], dtype=int),
        vertex_mu1_ranks=np.asarray([2, 2, 2], dtype=int),
        vertex_mu2_ranks=np.asarray([0, 3, 3], dtype=int),
        face_records=[(0, 0, (0, 1, 2)), (1, 0, (0, 1, 3))],
    )

    assert simplex_rank_sublists == {
        1: [1],
        3: [0],
    }
    assert master_rank_offsets[1] == (0, 4)
    rank1_entries = master_entries[slice(*master_rank_offsets[1])]
    assert [entry.f_type for entry in rank1_entries] == [ALF_VERTEX, ALF_VERTEX, ALF_VERTEX, ALF_TETRA]
    assert [entry.index for entry in rank1_entries[:3]] == [2, 1, 0]
    assert rank1_entries[-1].r_type == ALF_RHO

    rank3_entries = master_entries[slice(*master_rank_offsets[3])]
    assert any(entry.f_type == ALF_TRIANGLE and entry.r_type == ALF_MU1 for entry in rank3_entries)
    assert any(entry.f_type == ALF_EDGE and entry.r_type == ALF_MU1 for entry in rank3_entries)
    assert any(entry.f_type == ALF_TETRA and entry.r_type == ALF_RHO for entry in rank3_entries)


def test_iter_master_tetra_rho_indices_uses_master_list_order():
    geometry = SimpleNamespace(
        master_entries=[
            SimpleNamespace(rank=1, f_type=ALF_VERTEX, r_type=ALF_RHO, index=10),
            SimpleNamespace(rank=1, f_type=ALF_TETRA, r_type=ALF_RHO, index=1),
            SimpleNamespace(rank=2, f_type=ALF_EDGE, r_type=ALF_RHO, index=20),
            SimpleNamespace(rank=2, f_type=ALF_TETRA, r_type=ALF_RHO, index=2),
            SimpleNamespace(rank=3, f_type=ALF_TETRA, r_type=ALF_RHO, index=3),
        ],
        master_rank_offsets={
            1: (0, 2),
            2: (2, 4),
            3: (4, 5),
        },
        simplex_rank_sublists={1: [99], 2: [98], 3: [97]},
    )

    ascending = list(
        _iter_master_tetra_rho_indices(
            geometry,
            descending=False,
            rank_start=1,
            rank_end=3,
        )
    )
    descending = list(
        _iter_master_tetra_rho_indices(
            geometry,
            descending=True,
            rank_start=1,
            rank_end=3,
        )
    )

    assert ascending == [1, 2, 3]
    assert descending == [3, 2, 1]


def test_exact_ratio_compare_preserves_exact_ordering():
    assert ExactRatio(1, 2).compare(ExactRatio(2, 4)) == 0
    assert ExactRatio(1, 3).compare(ExactRatio(1, 2)) == -1
    assert ExactRatio(5, 7).compare(ExactRatio(3, 5)) == 1


def test_rank_of_ratio_uses_exact_threshold_ordering():
    spectrum_ratios = (
        ExactRatio(-9, 1),
        ExactRatio(-4, 1),
        ExactRatio(0, 1),
        ExactRatio(9, 4),
    )

    assert _rank_of_ratio(spectrum_ratios, ExactRatio(0, 1)) == 3
    assert _rank_of_ratio(spectrum_ratios, ExactRatio(1, 1)) == 3
    assert _rank_of_ratio(spectrum_ratios, ExactRatio(9, 4)) == 4


def test_exact_threshold_ratio_uses_native_fixed_grid():
    assert _exact_threshold_ratio(1.4, 1).compare(ExactRatio(196, 1)) == 0
    assert _exact_threshold_ratio(1.4, 3).compare(ExactRatio(1960000, 1)) == 0


def test_geometry_max_rank_uses_global_spectrum_plus_final_infinity_rank():
    geometry = SimpleNamespace(
        spectrum_ratios=(
            ExactRatio(-4, 1),
            ExactRatio(0, 1),
            ExactRatio(4, 1),
            ExactRatio(9, 1),
        ),
        spectrum_values=np.asarray([-4.0, 0.0, 4.0, 9.0], dtype=float),
        simplex_rho_ranks=np.asarray([1, 2], dtype=int),
        base_rank=2,
    )

    assert _geometry_max_rank(geometry) == 5


def test_fixed_point_helpers_follow_decimal_grid():
    assert fixed_point_int(27.34, 5) == 2734000
    assert fixed_point_int(3.04, 5) == 304000

    values = fixed_point_array(np.asarray([[27.34, 24.43, 2.614]], dtype=float), 5)
    assert values.tolist() == [[2734000, 2443000, 261400]]


def test_castp1_fixed_point_helpers_follow_lia_ffpload_floor_semantics():
    assert castp1_fixed_point_int(10.547, 5) == 1054700
    assert castp1_fixed_point_int(9.229, 5) == 922899

    values = castp1_fixed_point_array(
        np.asarray([[10.547, 16.150, 35.059], [9.229, 15.623, 34.806]]),
        5,
    )

    assert values.tolist() == [
        [1054700, 1614999, 3505899],
        [922899, 1562300, 3480599],
    ]


def test_weighted_decimal_places_include_radius_precision_from_squared_weights():
    points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    radii = np.asarray([1.77, 1.40], dtype=float)
    weights = radii * radii

    assert _infer_weighted_decimal_places(points, weights) == 2


def test_mouth_perimeter_uses_only_boundary_edges():
    atom_coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    faces = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    assert np.isclose(mouth_perimeter(atom_coordinates, faces), 4.0)


def test_component_area_sums_boundary_triangle_areas():
    atom_coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    faces = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    assert np.isclose(component_area(atom_coordinates, faces), 1.0)


def test_exact_determinant_matches_small_integer_example():
    matrix = np.asarray(
        [
            [1, 2, 3],
            [0, 4, 5],
            [1, 0, 6],
        ],
        dtype=object,
    )

    assert exact_determinant(matrix) == 22


def test_rank_table_is_in_complex_matches_historical_lookup_semantics():
    assert _rank_table_is_in_complex(-1, 0, 99) is False
    assert _rank_table_is_in_complex(4, 9, 3) is False
    assert _rank_table_is_in_complex(4, 9, 4) is True
    assert _rank_table_is_in_complex(0, 6, 5) is False
    assert _rank_table_is_in_complex(0, 6, 6) is True


def test_rank_table_is_interior_and_edge_membership_match_historical_lookup_semantics():
    assert _rank_table_is_interior(0, 10) is False
    assert _rank_table_is_interior(7, 6) is False
    assert _rank_table_is_interior(7, 7) is True

    edge_rho_ranks = {(1, 3): 0, (2, 4): 5}
    edge_mu1_ranks = {(1, 3): 8, (2, 4): 0}

    assert _edge_is_in_complex_at(edge_rho_ranks, edge_mu1_ranks, (8, 9), 10) is False
    assert _edge_is_in_complex_at(edge_rho_ranks, edge_mu1_ranks, (1, 3), 7) is False
    assert _edge_is_in_complex_at(edge_rho_ranks, edge_mu1_ranks, (1, 3), 8) is True
    assert _edge_is_in_complex_at(edge_rho_ranks, edge_mu1_ranks, (2, 4), 4) is False
    assert _edge_is_in_complex_at(edge_rho_ranks, edge_mu1_ranks, (2, 4), 5) is True


def test_edge_mu_rank_maps_follow_historical_attached_vs_unattached_rules():
    class FakeMesh:
        n_simplices = 1
        simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)

        @staticmethod
        def get_face_atoms(simplex_index, face_index):
            lookup = {
                (0, 0): (1, 2, 3),
                (0, 1): (0, 2, 3),
                (0, 2): (0, 1, 3),
                (0, 3): (0, 1, 2),
            }
            return lookup[(int(simplex_index), int(face_index))]

    face_rho_ranks = np.asarray([[0, 7, 0, 5]], dtype=int)
    face_mu1_ranks = np.asarray([[9, 7, 8, 5]], dtype=int)
    face_mu2_ranks = np.asarray([[12, 11, 10, 6]], dtype=int)
    face_is_on_hull = np.asarray([[False, False, True, False]], dtype=bool)

    edge_mu1_ranks, edge_mu2_ranks = _edge_mu_rank_maps(
        FakeMesh(),
        face_rho_ranks,
        face_mu1_ranks,
        face_mu2_ranks,
        face_is_on_hull,
    )

    assert edge_mu1_ranks[(1, 2)] == 5
    assert edge_mu1_ranks[(0, 2)] == 5
    assert edge_mu1_ranks[(0, 1)] == 5
    assert edge_mu2_ranks[(0, 1)] == 0
    assert edge_mu2_ranks[(0, 2)] == 11


def test_vertex_mu_rank_arrays_follow_historical_attached_vs_unattached_rules():
    class FakeMesh:
        points = np.zeros((4, 3), dtype=float)
        n_simplices = 1
        simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)

        @staticmethod
        def get_face_atoms(simplex_index, face_index):
            lookup = {
                (0, 0): (1, 2, 3),
                (0, 1): (0, 2, 3),
                (0, 2): (0, 1, 3),
                (0, 3): (0, 1, 2),
            }
            return lookup[(int(simplex_index), int(face_index))]

    edge_rho_ranks = {
        (0, 1): 4,
        (0, 2): 0,
        (0, 3): 6,
        (1, 2): 5,
        (1, 3): 0,
        (2, 3): 7,
    }
    edge_mu1_ranks = {
        (0, 1): 4,
        (0, 2): 9,
        (0, 3): 6,
        (1, 2): 5,
        (1, 3): 8,
        (2, 3): 7,
    }
    edge_mu2_ranks = {
        (0, 1): 10,
        (0, 2): 12,
        (0, 3): 11,
        (1, 2): 9,
        (1, 3): 13,
        (2, 3): 14,
    }
    face_is_on_hull = np.asarray([[False, False, True, False]], dtype=bool)

    vertex_rho_ranks, vertex_mu1_ranks, vertex_mu2_ranks = _vertex_mu_rank_arrays(
        FakeMesh(),
        edge_rho_ranks,
        edge_mu1_ranks,
        edge_mu2_ranks,
        face_is_on_hull,
    )

    assert vertex_rho_ranks.tolist() == [1, 1, 1, 1]
    assert vertex_mu1_ranks.tolist() == [4, 4, 5, 6]
    assert vertex_mu2_ranks.tolist() == [0, 0, 14, 0]


def test_rank_driven_components_do_not_union_retained_tetrahedra_into_outside(monkeypatch):
    master_entries, master_rank_offsets = _tetra_rho_master({2: [0, 1]})

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
        master_entries=master_entries,
        master_rank_offsets=master_rank_offsets,
        simplex_rank_sublists={2: [0, 1]},
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
        size_limit_rank=2,
    )

    assert depth.tolist() == [2, 1]
    assert blocked_nodes == {0}
    assert list(components.values()) == [[1]]


def test_compute_pocket_depths_follows_max_rho_sink_semantics(monkeypatch):
    master_entries, master_rank_offsets = _tetra_rho_master({2: [0], 3: [2], 4: [1]})

    geometry = SimpleNamespace(
        mesh=SimpleNamespace(
            n_simplices=3,
            neighbors=np.asarray(
                [
                    [1, -1, -1, -1],
                    [2, -1, -1, -1],
                    [-1, -1, -1, -1],
                ],
                dtype=int,
            ),
        ),
        face_is_on_hull=np.zeros((3, 4), dtype=bool),
        simplex_rho_ranks=np.asarray([2, 4, 3], dtype=int),
        master_entries=master_entries,
        master_rank_offsets=master_rank_offsets,
        simplex_rank_sublists={2: [0], 3: [2], 4: [1]},
    )

    monkeypatch.setattr(
        castp_components,
        '_triangle_is_attached',
        lambda geometry, simplex_index, face_index: False,
    )
    monkeypatch.setattr(
        castp_components,
        '_hidden_triangle',
        lambda geometry, simplex_index, face_index, neighbor_index: face_index == 0,
    )

    depth = _compute_pocket_depths(geometry)

    assert depth.tolist() == [1, 1, 2]


def test_build_void_components_scans_master_list_like_alf_find_voids():
    mesh = SimpleNamespace(
        n_simplices=3,
        neighbors=np.asarray(
            [
                [1, -1, -1, -1],
                [0, -1, -1, -1],
                [-1, -1, -1, -1],
            ],
            dtype=int,
        ),
    )
    master_entries = [
        SimpleNamespace(
            rank=2,
            f_type=ALF_TRIANGLE,
            r_type=ALF_RHO,
            index=0,
            is_first=True,
        ),
        SimpleNamespace(
            rank=3,
            f_type=ALF_TETRA,
            r_type=ALF_RHO,
            index=0,
            is_first=True,
        ),
        SimpleNamespace(
            rank=3,
            f_type=ALF_TETRA,
            r_type=ALF_RHO,
            index=1,
            is_first=True,
        ),
    ]
    geometry = SimpleNamespace(
        mesh=mesh,
        base_rank=1,
        simplex_rho_ranks=np.asarray([3, 3, 1], dtype=int),
        master_entries=master_entries,
        master_rank_offsets={
            2: (0, 1),
            3: (1, 3),
        },
        face_records=[
            (0, 0, (1, 2, 3)),
            (1, 0, (1, 2, 3)),
        ],
    )

    components, blocked_nodes = _build_void_components(
        geometry,
        empty_mask=np.asarray([False, False, False], dtype=bool),
    )

    assert list(components.values()) == [[0, 1]]
    assert blocked_nodes == {-1}


def test_component_boundary_faces_use_regular_triangle_selection_per_pocket(monkeypatch):
    class FakeMesh:
        neighbors = np.asarray([[1, -1, -1, -1]], dtype=int)

        @staticmethod
        def get_face_atoms(simplex_index, face_index):
            lookup = {
                (0, 0): (1, 2, 3),
                (0, 1): (0, 2, 3),
                (0, 2): (0, 1, 3),
                (0, 3): (0, 1, 2),
            }
            return lookup[(int(simplex_index), int(face_index))]

        @staticmethod
        def get_face_index(simplex_index, face_index):
            return 17 + int(face_index)

    geometry = SimpleNamespace(
        mesh=FakeMesh(),
        base_rank=1,
        face_rho_ranks=np.asarray([[0, 2, 2, 2]], dtype=int),
        face_mu1_ranks=np.asarray([[3, 2, 2, 2]], dtype=int),
        simplex_rho_ranks=np.asarray([2, 2], dtype=int),
    )

    monkeypatch.setattr(
        castp_components,
        '_triangle_in_complex_at',
        lambda geometry, simplex_index, face_index, rank: face_index != 0,
    )

    boundary_faces, mouth_faces = castp_components._component_boundary_faces(
        geometry,
        simplex_indices=[0],
        blocked_nodes=set(),
        depth=np.asarray([0, 0], dtype=int),
        size_limit_rank=2,
        rank1=1,
    )

    assert boundary_faces == [(1, 2, 3)]
    assert mouth_faces == [
        MouthFaceRecord(
            face_atoms=(1, 2, 3),
            simplex_index=0,
            face_index=0,
            triangle_index=17,
        )
    ]


def test_component_boundary_faces_do_not_make_mouths_between_active_pockets(monkeypatch):
    class FakeMesh:
        neighbors = np.asarray([[1, -1, -1, -1]], dtype=int)

        @staticmethod
        def get_face_atoms(simplex_index, face_index):
            lookup = {
                (0, 0): (1, 2, 3),
                (0, 1): (0, 2, 3),
                (0, 2): (0, 1, 3),
                (0, 3): (0, 1, 2),
            }
            return lookup[(int(simplex_index), int(face_index))]

        @staticmethod
        def get_face_index(simplex_index, face_index):
            return 17 + int(face_index)

    geometry = SimpleNamespace(
        mesh=FakeMesh(),
        base_rank=1,
        face_rho_ranks=np.asarray([[0, 2, 2, 2]], dtype=int),
        face_mu1_ranks=np.asarray([[3, 2, 2, 2]], dtype=int),
        simplex_rho_ranks=np.asarray([2, 2], dtype=int),
    )

    monkeypatch.setattr(
        castp_components,
        '_triangle_in_complex_at',
        lambda geometry, simplex_index, face_index, rank: face_index != 0,
    )

    boundary_faces, mouth_faces = castp_components._component_boundary_faces(
        geometry,
        simplex_indices=[0],
        blocked_nodes=set(),
        depth=np.asarray([0, 1], dtype=int),
        size_limit_rank=2,
        rank1=1,
        active_pocket_nodes={0, 1},
    )

    assert boundary_faces == []
    assert mouth_faces == []


def test_fnext_walk_stops_when_neighbor_sink_is_outside_rank2():
    class FakeMesh:
        simplex_atom_indices = np.asarray(
            [
                [0, 1, 2, 3],
                [0, 1, 3, 4],
            ],
            dtype=int,
        )
        neighbors = np.asarray(
            [
                [-1, -1, 1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        )

        @staticmethod
        def get_face_index(simplex_index, face_index):
            lookup = {
                (1, 3): 12,
                (0, 2): 12,
            }
            return lookup[(int(simplex_index), int(face_index))]

    result = _fnext_walk_around_edge(
        EdgeFacetRecord(
            oriented_face_atoms=(0, 3, 2),
            face_atoms=(0, 2, 3),
            triangle_index=20,
            simplex_index=0,
        ),
        FakeMesh(),
        depth=np.asarray([0, 1], dtype=int),
        infinity_marker=2,
        simplex_rho_ranks=np.asarray([2, 7], dtype=int),
        rank2=5,
    )

    assert result == EdgeFacetRecord(
        oriented_face_atoms=(0, 3, 1),
        face_atoms=(0, 1, 3),
        triangle_index=12,
        simplex_index=1,
    )


def test_cluster_mouth_faces_fnext_prefers_triangle_index_identity():
    class FakeMesh:
        simplex_atom_indices = np.asarray(
            [
                [0, 1, 2, 3],
                [0, 1, 3, 4],
            ],
            dtype=int,
        )
        neighbors = np.asarray(
            [
                [-1, -1, 1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        )

        @staticmethod
        def get_oriented_face_atoms(simplex_index, face_index):
            lookup = {
                (0, 2): (0, 3, 2),
                (1, 2): (0, 4, 3),
            }
            return lookup[(int(simplex_index), int(face_index))]

        @staticmethod
        def get_face_index(simplex_index, face_index):
            lookup = {
                (0, 1): 20,
                (0, 2): 20,
                (1, 1): 21,
                (1, 2): 21,
                (1, 3): 21,
            }
            return lookup[(int(simplex_index), int(face_index))]

    faces = [
        MouthFaceRecord(face_atoms=(0, 2, 3), simplex_index=0, face_index=2, triangle_index=20),
        MouthFaceRecord(face_atoms=(0, 1, 3), simplex_index=1, face_index=2, triangle_index=21),
    ]

    clusters = cluster_mouth_faces(
        faces,
        edge_rho_ranks={
            (0, 1): 1,
            (0, 2): 1,
            (0, 3): 0,
            (1, 3): 1,
            (2, 3): 1,
            (3, 4): 1,
        },
        edge_mu1_ranks={(0, 3): 8},
        rank1=5,
        mesh=FakeMesh(),
        depth=np.asarray([0, 1], dtype=int),
        infinity_marker=2,
        simplex_rho_ranks=np.asarray([2, 7], dtype=int),
        rank2=5,
    )

    assert len(clusters) == 1
    assert sorted(record.face_atoms for record in clusters[0]) == [(0, 1, 3), (0, 2, 3)]
    assert all(isinstance(record, MouthFaceRecord) for record in clusters[0])


def test_cluster_mouth_faces_populates_triangle_index_before_fnext_clustering():
    class FakeMesh:
        simplex_atom_indices = np.asarray(
            [
                [0, 1, 2, 3],
                [0, 1, 3, 4],
            ],
            dtype=int,
        )
        neighbors = np.asarray(
            [
                [-1, -1, 1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        )

        @staticmethod
        def get_oriented_face_atoms(simplex_index, face_index):
            lookup = {
                (0, 2): (0, 3, 2),
                (1, 2): (0, 4, 3),
            }
            return lookup[(int(simplex_index), int(face_index))]

        @staticmethod
        def get_face_index(simplex_index, face_index):
            lookup = {
                (0, 1): 20,
                (0, 2): 20,
                (1, 2): 21,
                (1, 1): 21,
                (1, 3): 21,
            }
            return lookup[(int(simplex_index), int(face_index))]

    faces = [
        MouthFaceRecord(face_atoms=(0, 2, 3), simplex_index=0, face_index=2, triangle_index=None),
        MouthFaceRecord(face_atoms=(0, 1, 3), simplex_index=1, face_index=2, triangle_index=None),
    ]

    clusters = cluster_mouth_faces(
        faces,
        edge_rho_ranks={
            (0, 1): 1,
            (0, 2): 1,
            (0, 3): 0,
            (1, 3): 1,
            (2, 3): 1,
            (3, 4): 1,
        },
        edge_mu1_ranks={(0, 3): 8},
        rank1=5,
        mesh=FakeMesh(),
        depth=np.asarray([0, 1], dtype=int),
        infinity_marker=2,
        simplex_rho_ranks=np.asarray([2, 7], dtype=int),
        rank2=5,
    )

    assert len(clusters) == 1
    assert sorted(record.triangle_index for record in clusters[0]) == [20, 21]


def test_cluster_mouth_faces_requires_explicit_triangle_identity_in_canonical_fnext_path():
    class FakeMesh:
        simplex_atom_indices = np.asarray(
            [
                [0, 1, 2, 3],
                [0, 1, 3, 4],
            ],
            dtype=int,
        )
        neighbors = np.asarray(
            [
                [-1, -1, 1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        )

        @staticmethod
        def get_oriented_face_atoms(simplex_index, face_index):
            lookup = {
                (0, 2): (0, 3, 2),
                (1, 2): (0, 4, 3),
            }
            return lookup[(int(simplex_index), int(face_index))]

    faces = [
        MouthFaceRecord(face_atoms=(0, 2, 3), simplex_index=0, face_index=2, triangle_index=None),
        MouthFaceRecord(face_atoms=(0, 1, 3), simplex_index=1, face_index=2, triangle_index=None),
    ]

    with pytest.raises(ValueError, match='explicit triangle identity'):
        cluster_mouth_faces(
            faces,
            edge_rho_ranks={(0, 3): 0},
            edge_mu1_ranks={(0, 3): 8},
            rank1=5,
            mesh=FakeMesh(),
            depth=np.asarray([0, 1], dtype=int),
            infinity_marker=2,
            simplex_rho_ranks=np.asarray([2, 7], dtype=int),
            rank2=5,
        )


def test_mouth_face_outward_atoms_flips_orientation_when_sink_is_outside_rank2():
    class FakeMesh:
        @staticmethod
        def get_oriented_face_atoms(simplex_index, face_index):
            assert int(simplex_index) == 0
            assert int(face_index) == 2
            return (10, 11, 12)

    inward = _mouth_face_outward_atoms(
        0,
        2,
        FakeMesh(),
        depth=np.asarray([0], dtype=int),
        infinity_marker=1,
        simplex_rho_ranks=np.asarray([4], dtype=int),
        rank2=5,
    )
    outward = _mouth_face_outward_atoms(
        0,
        2,
        FakeMesh(),
        depth=np.asarray([0], dtype=int),
        infinity_marker=1,
        simplex_rho_ranks=np.asarray([6], dtype=int),
        rank2=5,
    )

    assert inward == (10, 11, 12)
    assert outward == (10, 12, 11)


def test_mouth_face_edge_facets_follow_historical_enext_order():
    edge_facets = _mouth_face_edge_facets((10, 11, 12))

    assert edge_facets == (
        ((10, 11), 12),
        ((11, 12), 10),
        ((12, 10), 11),
    )


def test_edge_facet_enext_rotates_oriented_vertices_and_preserves_identity():
    edge_facet = EdgeFacetRecord(
        oriented_face_atoms=(10, 11, 12),
        face_atoms=(10, 11, 12),
        triangle_index=70,
        simplex_index=5,
    )

    next_edge_facet = _edge_facet_enext(edge_facet)

    assert next_edge_facet == EdgeFacetRecord(
        oriented_face_atoms=(11, 12, 10),
        face_atoms=(10, 11, 12),
        triangle_index=70,
        simplex_index=5,
    )


def test_mouth_face_initial_edge_facets_build_explicit_edge_facet_records():
    class FakeMesh:
        simplex_atom_indices = np.asarray([[9, 10, 11, 12]], dtype=int)

        @staticmethod
        def get_oriented_face_atoms(simplex_index, face_index):
            assert int(simplex_index) == 0
            assert int(face_index) == 2
            return (10, 11, 12)

        @staticmethod
        def get_face_index(simplex_index, face_index):
            lookup = {
                (0, 0): 70,
            }
            return lookup[(int(simplex_index), int(face_index))]

    edge_facets = _mouth_face_initial_edge_facets(
        0,
        2,
        FakeMesh(),
        depth=np.asarray([0], dtype=int),
        infinity_marker=1,
        simplex_rho_ranks=np.asarray([4], dtype=int),
        rank2=5,
    )

    assert edge_facets == (
        EdgeFacetRecord(oriented_face_atoms=(10, 11, 12), face_atoms=(10, 11, 12), triangle_index=70, simplex_index=0),
        EdgeFacetRecord(oriented_face_atoms=(11, 12, 10), face_atoms=(10, 11, 12), triangle_index=70, simplex_index=0),
        EdgeFacetRecord(oriented_face_atoms=(12, 10, 11), face_atoms=(10, 11, 12), triangle_index=70, simplex_index=0),
    )


def test_edge_facet_fnext_returns_next_triangle_around_same_edge():
    class FakeMesh:
        simplex_atom_indices = np.asarray(
            [
                [0, 1, 2, 3],
                [0, 1, 3, 4],
            ],
            dtype=int,
        )
        neighbors = np.asarray(
            [
                [-1, -1, 1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        )

        @staticmethod
        def get_face_index(simplex_index, face_index):
            lookup = {
                (1, 3): 45,
                (0, 2): 44,
            }
            return lookup[(int(simplex_index), int(face_index))]

    start_edge_facet = EdgeFacetRecord(
        oriented_face_atoms=(0, 3, 2),
        face_atoms=(0, 2, 3),
        triangle_index=20,
        simplex_index=0,
    )

    next_edge_facet = _edge_facet_fnext(start_edge_facet, FakeMesh())

    assert next_edge_facet == EdgeFacetRecord(
        oriented_face_atoms=(0, 3, 1),
        face_atoms=(0, 1, 3),
        triangle_index=45,
        simplex_index=1,
    )


def test_build_castp_feature_records_uses_canonical_base_rank_for_component_assembly(monkeypatch):
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(),
        spectrum_values=np.asarray([0.0, 1.0, 2.0, 3.0], dtype=float),
        spectrum_ratios=(
            ExactRatio(0, 1),
            ExactRatio(1, 1),
            ExactRatio(2, 1),
            ExactRatio(3, 1),
        ),
        spectrum_decimals=1,
        base_rank=1,
        edge_rho_ranks={},
        simplex_rho_ranks=np.asarray([2], dtype=int),
    )

    calls = {}

    monkeypatch.setattr(
        castp_components,
        '_build_empty_simplex_mask',
        lambda geometry, probe_radius: np.asarray([True], dtype=bool),
    )
    def fake_build_rank_driven_components(geometry, size_limit_rank, rank1=None):
        calls['assembly_rank'] = int(size_limit_rank)
        calls['rank1'] = rank1
        return {0: [0]}, set(), np.asarray([0], dtype=int)

    monkeypatch.setattr(
        castp_components,
        '_build_rank_driven_components',
        fake_build_rank_driven_components,
    )
    monkeypatch.setattr(
        castp_components,
        '_build_void_components',
        lambda geometry, empty_mask: ({}, {0}),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_boundary_faces',
        lambda geometry, simplex_indices, blocked_nodes, depth, size_limit_rank, rank1=None, active_pocket_nodes=None: (
            [],
            [],
        ),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_atom_indices',
        lambda mesh, atom_indices_map, simplex_indices: [],
    )
    monkeypatch.setattr(
        castp_components,
        '_component_regular_vertex_indices',
        lambda geometry, simplex_indices, touched_simplex_indices, rank2: [],
    )
    monkeypatch.setattr(
        castp_components,
        '_component_face_partitions',
        lambda geometry, simplex_indices, rank1, active_pocket_nodes=None: ([], []),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_edge_partitions',
        lambda geometry, simplex_indices, touched_simplex_indices, rank1, rank2: ([], []),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_vertex_partitions',
        lambda geometry, simplex_indices, touched_simplex_indices, rank1, rank2: ([], []),
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
        'component_area',
        lambda coordinates, faces: 0.0,
    )
    monkeypatch.setattr(
        castp_components,
        'cluster_mouth_faces',
        lambda mouth_faces, edge_rho_ranks=None, edge_mu1_ranks=None, rank1=0, **kwargs: [],
    )

    geometry.atom_indices_map = np.asarray([10, 11, 12, 13], dtype=int)
    geometry.atom_coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    geometry.mesh.simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)
    geometry.mesh.simplex_centers = np.asarray([[0.0, 0.0, 0.0]], dtype=float)
    geometry.mesh.simplex_volumes = np.asarray([1.0], dtype=float)
    geometry.mesh.n_simplices = 1

    records = castp_components.build_castp_feature_records(geometry, probe_radius=1.4)

    assert calls['assembly_rank'] == 4
    assert calls['rank1'] == 1
    assert len(records) == 1
    assert records[0]['feature_type'] == 'pocket'
    assert records[0]['n_mouths'] == 0


def test_build_castp_feature_records_uses_probe_rank_as_beta(monkeypatch):
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(),
        spectrum_values=np.asarray([0.0, 1.0, 4.0, 9.0], dtype=float),
        spectrum_ratios=(
            ExactRatio(0, 1),
            ExactRatio(1, 1),
            ExactRatio(4, 1),
            ExactRatio(9, 1),
        ),
        spectrum_decimals=1,
        base_rank=1,
        edge_rho_ranks={},
        simplex_rho_ranks=np.asarray([2], dtype=int),
    )

    calls = {}

    monkeypatch.setattr(
        castp_components,
        '_build_empty_simplex_mask',
        lambda geometry, probe_radius: np.asarray([True], dtype=bool),
    )
    monkeypatch.setattr(
        castp_components,
        '_build_void_components',
        lambda geometry, empty_mask: ({}, set()),
    )

    def fake_build_rank_driven_components(geometry, size_limit_rank, rank1=None):
        calls['assembly_rank'] = int(size_limit_rank)
        calls['rank1'] = int(rank1)
        return {0: [0]}, set(), np.asarray([0], dtype=int)

    def fake_component_boundary_faces(
        geometry,
        simplex_indices,
        blocked_nodes,
        depth,
        size_limit_rank,
        rank1=None,
        active_pocket_nodes=None,
    ):
        calls['boundary_rank2'] = int(size_limit_rank)
        calls['boundary_rank1'] = int(rank1)
        return (
            [(0, 1, 2)],
            [MouthFaceRecord(face_atoms=(0, 1, 2), simplex_index=0, face_index=0)],
        )

    def fake_component_regular_vertex_indices(geometry, simplex_indices, touched_simplex_indices, rank2):
        calls['regular_vertex_rank2'] = int(rank2)
        return []

    monkeypatch.setattr(
        castp_components,
        '_build_rank_driven_components',
        fake_build_rank_driven_components,
    )
    monkeypatch.setattr(
        castp_components,
        '_component_boundary_faces',
        fake_component_boundary_faces,
    )
    monkeypatch.setattr(
        castp_components,
        '_component_regular_vertex_indices',
        fake_component_regular_vertex_indices,
    )
    monkeypatch.setattr(
        castp_components,
        '_component_face_partitions',
        lambda geometry, simplex_indices, rank1, active_pocket_nodes=None: (
            [],
            [(10, 11, 12)],
        ),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_edge_partitions',
        lambda geometry, simplex_indices, touched_simplex_indices, rank1, rank2: ([], []),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_vertex_partitions',
        lambda geometry, simplex_indices, touched_simplex_indices, rank1, rank2: ([], []),
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
        'component_area',
        lambda coordinates, faces: 7.0,
    )
    monkeypatch.setattr(
        castp_components,
        'mouth_area',
        lambda coordinates, faces: 1.0,
    )
    monkeypatch.setattr(
        castp_components,
        'cluster_mouth_faces',
        lambda mouth_faces, edge_rho_ranks=None, edge_mu1_ranks=None, rank1=0, **kwargs: [[(0, 1, 2)]],
    )

    geometry.atom_indices_map = np.asarray([10, 11, 12, 13], dtype=int)
    geometry.atom_coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    geometry.mesh.simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)
    geometry.mesh.simplex_centers = np.asarray([[0.0, 0.0, 0.0]], dtype=float)
    geometry.mesh.simplex_volumes = np.asarray([1.0], dtype=float)
    geometry.mesh.n_simplices = 1

    records = castp_components.build_castp_feature_records(geometry, probe_radius=1.4)

    assert calls['assembly_rank'] == 4
    assert calls['rank1'] == 1
    assert calls['boundary_rank2'] == 4
    assert calls['boundary_rank1'] == 1
    assert calls['regular_vertex_rank2'] == 4
    assert len(records) == 1
    assert records[0]['area'] == 7.0


def test_build_castp_feature_records_accepts_explicit_castp_ranks(monkeypatch):
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(),
        spectrum_values=np.asarray([0.0, 1.0], dtype=float),
        spectrum_ratios=(ExactRatio(0, 1), ExactRatio(1, 1)),
        spectrum_decimals=1,
        base_rank=1,
        edge_rho_ranks={},
        simplex_rho_ranks=np.asarray([2], dtype=int),
        atom_indices_map=np.asarray([10, 11, 12, 13], dtype=int),
        atom_coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        ),
    )
    geometry.mesh.simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)
    geometry.mesh.simplex_centers = np.asarray([[0.0, 0.0, 0.0]], dtype=float)
    geometry.mesh.simplex_volumes = np.asarray([1.0], dtype=float)
    geometry.mesh.n_simplices = 1

    calls = {}

    monkeypatch.setattr(castp_components, '_probe_rank', lambda geometry, probe_radius: (_ for _ in ()).throw(AssertionError))
    monkeypatch.setattr(
        castp_components,
        '_build_empty_simplex_mask',
        lambda geometry, probe_radius: np.asarray([True], dtype=bool),
    )
    monkeypatch.setattr(
        castp_components,
        '_build_void_components',
        lambda geometry, empty_mask: ({}, set()),
    )

    def fake_build_rank_driven_components(geometry, size_limit_rank, rank1=None):
        calls['rank1'] = int(rank1)
        calls['rank2'] = int(size_limit_rank)
        return {}, set(), np.asarray([0], dtype=int)

    monkeypatch.setattr(
        castp_components,
        '_build_rank_driven_components',
        fake_build_rank_driven_components,
    )

    records = castp_components.build_castp_feature_records(
        geometry,
        probe_radius=1.4,
        alpha_rank=14676,
        beta_rank=15044,
    )

    assert records == []
    assert calls == {'rank1': 14676, 'rank2': 15044}
    assert geometry.base_rank == 1


def test_build_castp_feature_records_classifies_branched_channels(monkeypatch):
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(),
        spectrum_values=np.asarray([0.0, 1.0], dtype=float),
        spectrum_ratios=(
            ExactRatio(0, 1),
            ExactRatio(1, 1),
        ),
        spectrum_decimals=1,
        base_rank=1,
        edge_rho_ranks={},
        simplex_rho_ranks=np.asarray([2], dtype=int),
        atom_indices_map=np.asarray([10, 11, 12, 13], dtype=int),
        atom_coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        ),
    )

    monkeypatch.setattr(
        castp_components,
        '_build_empty_simplex_mask',
        lambda geometry, probe_radius: np.asarray([True], dtype=bool),
    )
    monkeypatch.setattr(
        castp_components,
        '_build_void_components',
        lambda geometry, empty_mask: ({}, {0}),
    )
    monkeypatch.setattr(
        castp_components,
        '_build_rank_driven_components',
        lambda geometry, size_limit_rank, rank1=None: ({0: [0]}, set(), np.asarray([0], dtype=int)),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_boundary_faces',
        lambda geometry, simplex_indices, blocked_nodes, depth, size_limit_rank, rank1=None, active_pocket_nodes=None: (
            [(0, 1, 2), (0, 1, 3), (0, 2, 3)],
            [
                MouthFaceRecord(face_atoms=(0, 1, 2), simplex_index=0, face_index=0),
                MouthFaceRecord(face_atoms=(0, 1, 3), simplex_index=0, face_index=1),
                MouthFaceRecord(face_atoms=(0, 2, 3), simplex_index=0, face_index=2),
            ],
        ),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_atom_indices',
        lambda mesh, atom_indices_map, simplex_indices: [10, 11, 12, 13],
    )
    monkeypatch.setattr(
        castp_components,
        '_component_regular_vertex_indices',
        lambda geometry, simplex_indices, touched_simplex_indices, rank2: [10, 11, 12],
    )
    monkeypatch.setattr(
        castp_components,
        '_component_face_partitions',
        lambda geometry, simplex_indices, rank1, active_pocket_nodes=None: (
            [(10, 11, 12)],
            [(10, 11, 13)],
        ),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_edge_partitions',
        lambda geometry, simplex_indices, touched_simplex_indices, rank1, rank2: (
            [(10, 11)],
            [(10, 13)],
        ),
    )
    monkeypatch.setattr(
        castp_components,
        '_component_vertex_partitions',
        lambda geometry, simplex_indices, touched_simplex_indices, rank1, rank2: (
            [11],
            [10, 12],
        ),
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
        'component_area',
        lambda coordinates, faces: 42.0,
    )
    monkeypatch.setattr(
        castp_components,
        'mouth_area',
        lambda coordinates, faces: float(len(faces)),
    )
    monkeypatch.setattr(
        castp_components,
        'mouth_perimeter',
        lambda coordinates, faces: float(len(faces) * 10.0),
    )
    monkeypatch.setattr(
        castp_components,
        'cluster_mouth_faces',
        lambda mouth_faces, edge_rho_ranks=None, edge_mu1_ranks=None, rank1=0, **kwargs: [
            [MouthFaceRecord(face_atoms=(0, 1, 2), simplex_index=0, face_index=0, triangle_index=30)],
            [MouthFaceRecord(face_atoms=(0, 1, 3), simplex_index=0, face_index=1, triangle_index=31)],
            [MouthFaceRecord(face_atoms=(0, 2, 3), simplex_index=0, face_index=2, triangle_index=32)],
        ],
    )

    geometry.mesh.simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)
    geometry.mesh.simplex_centers = np.asarray([[0.0, 0.0, 0.0]], dtype=float)
    geometry.mesh.simplex_volumes = np.asarray([1.0], dtype=float)
    geometry.mesh.n_simplices = 1

    records = castp_components.build_castp_feature_records(geometry, probe_radius=1.4)

    assert len(records) == 1
    assert records[0]['feature_type'] == 'branched_channel'
    assert records[0]['type'] == 'BranchedChannel'
    assert records[0]['n_mouths'] == 3
    assert records[0]['area'] == 42.0
    assert records[0]['mouth_perimeter'] == 30.0
    assert records[0]['mouths'][0]['triangle_indices'] == [30]
    assert records[0]['mouths'][0]['perimeter'] == 10.0
    assert records[0]['iF'] == [(10, 11, 12)]
    assert records[0]['rF'] == [(10, 11, 13)]
    assert records[0]['iE'] == [(10, 11)]
    assert records[0]['rE'] == [(10, 13)]
    assert records[0]['iV'] == [11]
    assert records[0]['rV'] == [10, 12]


def test_probe_rank_prefers_exact_ratios_over_float_spectrum_values():
    geometry = SimpleNamespace(
        spectrum_values=np.asarray([0.0, 100.0, 200.0], dtype=float),
        spectrum_ratios=(
            ExactRatio(0, 1),
            ExactRatio(100, 1),
            ExactRatio(196, 1),
        ),
        spectrum_decimals=1,
    )

    assert _probe_rank(geometry, probe_radius=1.4) == 3


def test_probe_rank_requires_exact_rank_support():
    geometry = SimpleNamespace(
        spectrum_values=np.asarray([0.0, 1.0, 4.0], dtype=float),
    )

    with pytest.raises(ValueError, match='exact spectrum_ratios'):
        _probe_rank(geometry, probe_radius=1.4)


def test_component_regular_vertex_indices_follow_mkalf_interior_and_touched_logic():
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(
            simplex_atom_indices=np.asarray(
                [
                    [0, 1, 2, 3],
                    [1, 3, 4, 5],
                ],
                dtype=int,
            )
        ),
        atom_indices_map=np.asarray([100, 101, 102, 103, 104, 105], dtype=int),
        base_rank=1,
        vertex_rho_ranks=np.asarray([0, 0, 0, 0, 0, 0], dtype=int),
        vertex_mu1_ranks=np.asarray([5, 5, 5, 5, 5, 5], dtype=int),
        vertex_mu2_ranks=np.asarray([2, 5, 0, 7, 6, 9], dtype=int),
    )

    regular_vertices = _component_regular_vertex_indices(
        geometry,
        simplex_indices=[0],
        touched_simplex_indices={1},
        rank2=8,
    )

    # component vertices = {0,1,2,3}
    # v0: interior (mu2=2) and not touched -> not regular
    # v1: interior (mu2=5) but touched via simplex 1 -> regular
    # v2: hull (mu2=0) -> regular
    # v3: interior (mu2=7) and touched via simplex 1 -> regular
    assert regular_vertices == [101, 102, 103]


def test_component_vertex_partitions_follow_mkalf_interior_and_touched_logic():
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(
            simplex_atom_indices=np.asarray(
                [
                    [0, 1, 2, 3],
                    [1, 3, 4, 5],
                ],
                dtype=int,
            )
        ),
        atom_indices_map=np.asarray([100, 101, 102, 103, 104, 105], dtype=int),
        vertex_rho_ranks=np.asarray([0, 0, 0, 0, 0, 0], dtype=int),
        vertex_mu1_ranks=np.asarray([5, 5, 5, 5, 5, 5], dtype=int),
        vertex_mu2_ranks=np.asarray([2, 5, 0, 7, 6, 9], dtype=int),
    )

    interior_vertices, regular_vertices = _component_vertex_partitions(
        geometry,
        simplex_indices=[0],
        touched_simplex_indices={1},
        rank1=1,
        rank2=8,
    )

    assert interior_vertices == [100]
    assert regular_vertices == [101, 102, 103]


def test_component_edge_partitions_follow_mkalf_interior_and_touched_logic():
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(
            simplex_atom_indices=np.asarray(
                [
                    [0, 1, 2, 3],
                    [1, 3, 4, 5],
                ],
                dtype=int,
            )
        ),
        atom_indices_map=np.asarray([100, 101, 102, 103, 104, 105], dtype=int),
        edge_rho_ranks={
            (0, 1): 0,
            (0, 2): 0,
            (1, 3): 0,
            (0, 3): 1,
            (1, 2): 1,
            (2, 3): 1,
        },
        edge_mu1_ranks={
            (0, 1): 5,
            (0, 2): 5,
            (1, 3): 5,
        },
        edge_mu2_ranks={
            (0, 1): 2,
            (0, 2): 0,
            (1, 3): 5,
        },
    )

    interior_edges, regular_edges = _component_edge_partitions(
        geometry,
        simplex_indices=[0],
        touched_simplex_indices={1},
        rank1=1,
        rank2=8,
    )

    assert interior_edges == [(100, 101)]
    assert regular_edges == [(100, 102), (101, 103)]


def test_component_face_partitions_follow_mkalf_interior_and_regular_logic():
    face_by_owner = {
        (0, 0): (1, 2, 3),
        (0, 1): (0, 3, 2),
        (0, 2): (0, 1, 3),
        (0, 3): (0, 2, 1),
        (1, 0): (1, 2, 4),
        (1, 1): (0, 4, 2),
        (1, 2): (0, 1, 4),
        (1, 3): (0, 2, 1),
    }
    face_index_by_owner = {
        (0, 0): 10,
        (0, 1): 11,
        (0, 2): 12,
        (0, 3): 13,
        (1, 0): 14,
        (1, 1): 15,
        (1, 2): 16,
        (1, 3): 13,
    }
    neighbor_by_owner = {
        (0, 0): -1,
        (0, 1): -1,
        (0, 2): -1,
        (0, 3): 1,
        (1, 0): -1,
        (1, 1): -1,
        (1, 2): -1,
        (1, 3): 0,
    }

    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [-1, -1, -1, 1],
                [-1, -1, -1, 0],
            ],
            dtype=int,
        ),
        get_face_atoms=lambda simplex_index, face_index: face_by_owner[(int(simplex_index), int(face_index))],
        get_face_index=lambda simplex_index, face_index: face_index_by_owner[(int(simplex_index), int(face_index))],
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        atom_indices_map=np.asarray([10, 11, 12, 13, 14], dtype=int),
        face_rho_ranks=np.zeros((2, 4), dtype=int),
        face_mu1_ranks=np.full((2, 4), 5, dtype=int),
    )

    interior_faces, regular_faces = _component_face_partitions(
        geometry,
        simplex_indices=[0, 1],
        rank1=1,
    )

    assert interior_faces == [
        (10, 11, 12),
        (10, 11, 13),
        (10, 11, 14),
        (10, 12, 13),
        (10, 12, 14),
        (11, 12, 13),
        (11, 12, 14),
    ]
    assert regular_faces == [
        (10, 11, 13),
        (10, 11, 14),
        (10, 12, 13),
        (10, 12, 14),
        (11, 12, 13),
        (11, 12, 14),
    ]


def test_component_face_partitions_treat_faces_to_other_pockets_as_interior():
    face_by_owner = {
        (0, 0): (1, 2, 3),
    }
    mesh = SimpleNamespace(
        neighbors=np.asarray([[1, -1, -1, -1]], dtype=int),
        get_face_atoms=lambda simplex_index, face_index: face_by_owner[
            (int(simplex_index), int(face_index))
        ],
        get_face_index=lambda simplex_index, face_index: 10 + int(face_index),
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        atom_indices_map=np.asarray([10, 11, 12, 13], dtype=int),
        face_rho_ranks=np.asarray([[0, 1, 1, 1]], dtype=int),
        face_mu1_ranks=np.full((1, 4), 5, dtype=int),
    )

    interior_faces, regular_faces = _component_face_partitions(
        geometry,
        simplex_indices=[0],
        rank1=1,
        active_pocket_nodes={0, 1},
    )

    assert interior_faces == [(11, 12, 13)]
    assert regular_faces == []


def test_handle_tetra_seq_emits_canonical_pocket_events():
    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [-1, -1, -1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        ),
        get_face_index=lambda simplex_index, face_index: 10 * int(simplex_index) + int(face_index),
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        face_rho_ranks=np.asarray(
            [
                [2, 1, 1, 1],
                [2, 1, 1, 1],
            ],
            dtype=int,
        ),
        face_mu1_ranks=np.zeros((2, 4), dtype=int),
    )

    events = []
    parents = {-1: -1, 0: 0}
    sizes = {-1: 1, 0: 1}

    _handle_tetra_seq(
        geometry,
        simplex_index=1,
        rank1=1,
        parents=parents,
        sizes=sizes,
        exterior=-1,
        event_hook=lambda index, event_type: events.append((int(index), int(event_type))),
    )

    assert events[0] == (1, ALF_POC_TETRA)
    assert (10, ALF_POC_UNION_TWO) in events
    assert (11, ALF_POC_BURIED) in events
    assert (12, ALF_POC_BURIED) in events
    assert (13, ALF_POC_BURIED) in events

    events_same = []
    parents_same = {-1: -1, 0: 0, 1: 0}
    sizes_same = {-1: 1, 0: 2}
    _handle_tetra_seq(
        geometry,
        simplex_index=1,
        rank1=1,
        parents=parents_same,
        sizes=sizes_same,
        exterior=-1,
        event_hook=lambda index, event_type: events_same.append((int(index), int(event_type))),
    )
    assert (10, ALF_POC_UNION_SAME) in events_same


def test_handle_tetra_seq_unions_through_face_owner_indices():
    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [-1, -1, -1, -1],
                [-1, -1, -1, -1],
                [-1, -1, -1, -1],
            ],
            dtype=int,
        ),
        get_face_index=lambda simplex_index, face_index: 20 + int(face_index),
        get_face_owner_indices=lambda simplex_index, face_index: (7, 3) if int(face_index) == 0 else (int(simplex_index), -1),
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        face_rho_ranks=np.asarray(
            [
                [1, 1, 1, 1],
                [2, 1, 1, 1],
                [1, 1, 1, 1],
            ],
            dtype=int,
        ),
        face_mu1_ranks=np.zeros((3, 4), dtype=int),
    )

    events = []
    parents = {-1: -1, 7: 7, 3: 3, 1: 1}
    sizes = {-1: 1, 7: 1, 3: 2, 1: 1}

    _handle_tetra_seq(
        geometry,
        simplex_index=1,
        rank1=1,
        parents=parents,
        sizes=sizes,
        exterior=-1,
        event_hook=lambda index, event_type: events.append((int(index), int(event_type))),
    )

    assert (20, ALF_POC_UNION_TWO) in events
    assert parents[7] == 3


def test_handle_tetra_seq_uses_canonical_edge_facet_owner_order_for_union():
    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [1, -1, -1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        ),
        get_face_index=lambda simplex_index, face_index: 30 + int(face_index),
        get_face_owner_indices=lambda simplex_index, face_index: (int(simplex_index), int(mesh.neighbors[int(simplex_index), int(face_index)])),
        get_face_atoms=lambda simplex_index, face_index: {
            (0, 0): (1, 2, 3),
            (1, 0): (1, 2, 3),
            (1, 1): (0, 2, 3),
            (1, 2): (0, 1, 3),
            (1, 3): (0, 1, 2),
        }.get((int(simplex_index), int(face_index)), (0, 0, 0)),
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        face_records=[
            (0, 0, (1, 2, 3)),
            (1, 0, (1, 2, 3)),
        ],
        face_rho_ranks=np.asarray(
            [
                [2, 1, 1, 1],
                [2, 1, 1, 1],
            ],
            dtype=int,
        ),
        face_mu1_ranks=np.zeros((2, 4), dtype=int),
    )

    parents = {-1: -1, 0: 0}
    sizes = {-1: 1, 0: 1}
    events = []

    _handle_tetra_seq(
        geometry,
        simplex_index=1,
        rank1=1,
        parents=parents,
        sizes=sizes,
        exterior=-1,
        event_hook=lambda index, event_type: events.append((int(index), int(event_type))),
    )

    assert (30, ALF_POC_UNION_TWO) in events
    assert parents[1] == 0


def test_handle_tetra_pocket_unions_current_tetrahedron_with_processed_neighbor():
    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [-1, -1, -1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        ),
        get_face_owner_indices=lambda simplex_index, face_index: (7, 3),
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        face_rho_ranks=np.asarray(
            [
                [1, 1, 1, 1],
                [2, 1, 1, 1],
            ],
            dtype=int,
        ),
        face_mu1_ranks=np.zeros((2, 4), dtype=int),
    )

    parents = {-1: -1, 0: 0}
    sizes = {-1: 1, 0: 1}

    _handle_tetra_pocket(
        geometry,
        simplex_index=1,
        rank1=1,
        parents=parents,
        sizes=sizes,
        exterior=-1,
    )

    assert parents[0] == 1


def test_build_rank_driven_components_emits_rank_and_mouth_events_without_monkeypatch():
    master_entries, master_rank_offsets = _tetra_rho_master({2: [0]})

    mesh = SimpleNamespace(
        neighbors=np.asarray([[-1, -1, -1, -1]], dtype=int),
        n_simplices=1,
        get_face_index=lambda simplex_index, face_index: 100 + int(face_index),
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        base_rank=1,
        simplex_rho_ranks=np.asarray([2], dtype=int),
        master_entries=master_entries,
        master_rank_offsets=master_rank_offsets,
        simplex_rank_sublists={2: [0]},
        face_is_on_hull=np.asarray([[True, True, True, True]], dtype=bool),
        face_rho_ranks=np.asarray([[2, 2, 2, 2]], dtype=int),
        face_mu1_ranks=np.zeros((1, 4), dtype=int),
    )

    events = []
    components, blocked_nodes, depth = _build_rank_driven_components(
        geometry,
        size_limit_rank=2,
        rank1=1,
        event_hook=lambda index, event_type: events.append((int(index), int(event_type))),
    )

    assert components == {0: [0]}
    assert blocked_nodes == set()
    assert depth.tolist() == [0]
    assert events[0] == (0, ALF_POC_TETRA)
    assert events.count((100, ALF_POC_MOUTH)) == 1
    assert events.count((101, ALF_POC_MOUTH)) == 1
    assert events.count((102, ALF_POC_MOUTH)) == 1
    assert events.count((103, ALF_POC_MOUTH)) == 1
    assert events[-1] == (0, ALF_POC_RANK)


def test_castp1_pocket_metric_signatures_follow_mkalf_event_updates():
    master_entries, master_rank_offsets = _tetra_rho_master({2: [0]})

    class FakeMesh:
        n_simplices = 1
        neighbors = np.asarray([[-1, -1, -1, -1]], dtype=int)
        simplex_atom_indices = np.asarray([[0, 1, 2, 3]], dtype=int)
        simplex_volumes = np.asarray([1.0 / 6.0], dtype=float)

        @staticmethod
        def get_face_index(simplex_index, face_index):
            return 100 + int(face_index)

        @staticmethod
        def get_face_atoms(simplex_index, face_index):
            faces = {
                0: (1, 2, 3),
                1: (0, 3, 2),
                2: (0, 1, 3),
                3: (0, 2, 1),
            }
            return faces[int(face_index)]

    geometry = SimpleNamespace(
        mesh=FakeMesh(),
        base_rank=1,
        simplex_rho_ranks=np.asarray([2], dtype=int),
        master_entries=master_entries,
        master_rank_offsets=master_rank_offsets,
        simplex_rank_sublists={2: [0]},
        face_is_on_hull=np.asarray([[True, True, True, True]], dtype=bool),
        face_rho_ranks=np.asarray([[2, 2, 2, 2]], dtype=int),
        face_mu1_ranks=np.zeros((1, 4), dtype=int),
        atom_coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        ),
    )

    signatures = castp1_pocket_metric_signatures(
        geometry,
        alpha_rank=1,
        beta_rank=2,
    )

    assert signatures['final']['num_pockets'] == 1
    assert signatures['final']['num_tetra'] == 1
    assert signatures['final']['num_buried_triangles'] == 0
    assert signatures['final']['max_tetra'] == 1
    expected_mouth_area = component_area(
        geometry.atom_coordinates,
        [
            (1, 2, 3),
            (0, 3, 2),
            (0, 1, 3),
            (0, 2, 1),
        ],
    )
    assert signatures['final']['pocket_volume'] == pytest.approx(1.0 / 6.0)
    assert signatures['final']['buried_area'] == 0.0
    assert signatures['final']['mouth_area'] == pytest.approx(expected_mouth_area)
    assert signatures['final']['mouth_triangles'] == 4
    assert signatures['final']['max_pocket_volume'] == pytest.approx(1.0 / 6.0)


def test_castp1_pocket_metric_signatures_track_union_maxima():
    master_entries, master_rank_offsets = _tetra_rho_master({2: [0, 1]})

    face_by_owner = {
        (0, 0): (1, 2, 3),
        (0, 1): (0, 3, 2),
        (0, 2): (0, 1, 3),
        (0, 3): (0, 2, 1),
        (1, 0): (1, 2, 4),
        (1, 1): (0, 4, 2),
        (1, 2): (0, 1, 4),
        (1, 3): (0, 2, 1),
    }
    face_index_by_owner = {
        (0, 0): 10,
        (0, 1): 11,
        (0, 2): 12,
        (0, 3): 13,
        (1, 0): 14,
        (1, 1): 15,
        (1, 2): 16,
        (1, 3): 13,
    }
    neighbor_by_owner = {
        (0, 0): -1,
        (0, 1): -1,
        (0, 2): -1,
        (0, 3): 1,
        (1, 0): -1,
        (1, 1): -1,
        (1, 2): -1,
        (1, 3): 0,
    }

    mesh = SimpleNamespace(
        n_simplices=2,
        neighbors=np.asarray(
            [
                [-1, -1, -1, 1],
                [-1, -1, -1, 0],
            ],
            dtype=int,
        ),
        simplex_atom_indices=np.asarray(
            [
                [0, 1, 2, 3],
                [0, 1, 2, 4],
            ],
            dtype=int,
        ),
        simplex_volumes=np.asarray([2.0, 3.0], dtype=float),
        get_face_atoms=lambda simplex_index, face_index: face_by_owner[
            (int(simplex_index), int(face_index))
        ],
        get_face_index=lambda simplex_index, face_index: face_index_by_owner[
            (int(simplex_index), int(face_index))
        ],
        get_face_owner_indices=lambda simplex_index, face_index: (
            int(simplex_index),
            int(neighbor_by_owner[(int(simplex_index), int(face_index))]),
        ),
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        base_rank=1,
        simplex_rho_ranks=np.asarray([2, 2], dtype=int),
        master_entries=master_entries,
        master_rank_offsets=master_rank_offsets,
        simplex_rank_sublists={2: [0, 1]},
        face_is_on_hull=np.asarray(
            [
                [True, True, True, False],
                [True, True, True, False],
            ],
            dtype=bool,
        ),
        face_rho_ranks=np.full((2, 4), 2, dtype=int),
        face_mu1_ranks=np.zeros((2, 4), dtype=int),
        atom_coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.0, 0.0, -1.0],
            ],
            dtype=float,
        ),
    )

    signatures = castp1_pocket_metric_signatures(
        geometry,
        alpha_rank=1,
        beta_rank=2,
    )

    assert signatures['final']['num_pockets'] == 1
    assert signatures['final']['num_tetra'] == 2
    assert signatures['final']['max_tetra'] == 2
    assert signatures['final']['pocket_volume'] == pytest.approx(5.0)
    assert signatures['final']['max_pocket_volume'] == pytest.approx(5.0)
    assert signatures['final']['mouth_triangles'] == 6


def test_volbl_metric_context_matches_basic_ball_formulas():
    context = VolblMetricContext(
        coordinates=np.asarray([[0.0, 0.0, 0.0]], dtype=float),
        radii=np.asarray([2.0], dtype=float),
        solvent_radius=0.0,
    )

    assert context.ball_area(0) == pytest.approx(16.0 * np.pi)
    assert context.ball_volume(0) == pytest.approx((32.0 / 3.0) * np.pi)


def test_volbl_metric_context_ball_radius_uses_alpha_not_solvent_radius():
    context = VolblMetricContext(
        coordinates=np.asarray([[0.0, 0.0, 0.0]], dtype=float),
        radii=np.asarray([2.0], dtype=float),
        solvent_radius=1.4,
        alpha=0.0,
    )

    assert context.ball_radius(0) == pytest.approx(2.0)

    context = VolblMetricContext(
        coordinates=np.asarray([[0.0, 0.0, 0.0]], dtype=float),
        radii=np.asarray([2.0], dtype=float),
        solvent_radius=1.4,
        alpha=3.0,
    )

    assert context.ball_radius(0) == pytest.approx(np.sqrt(13.0))


def test_volbl_metric_context_matches_equal_sphere_cap_formulas():
    context = VolblMetricContext(
        coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
            ],
            dtype=float,
        ),
        radii=np.asarray([1.0, 1.0], dtype=float),
        solvent_radius=0.0,
    )

    assert context.cap_height(0, 1) == pytest.approx(0.5)
    assert context.disk_radius(0, 1) == pytest.approx(np.sqrt(0.75))
    assert context.cap_area(0, 1) == pytest.approx(np.pi)
    assert context.cap_volume(0, 1) == pytest.approx((5.0 / 24.0) * np.pi)
    assert context.ball2_area(0, 1) == pytest.approx(2.0 * np.pi)
    assert context.ball2_volume(0, 1) == pytest.approx((5.0 / 12.0) * np.pi)


def test_volbl_metric_context_shell_shrinks_accessible_area_to_molecular_surface():
    context = VolblMetricContext(
        coordinates=np.asarray([[0.0, 0.0, 0.0]], dtype=float),
        radii=np.asarray([2.0], dtype=float),
        solvent_radius=0.5,
    )

    shell = context.shell(0, area=8.0)

    assert shell.area == pytest.approx(8.0 * 1.5 * 1.5 / 4.0)
    assert shell.volume == pytest.approx((8.0 * 2.0 - shell.area * 1.5) / 3.0)


def test_volbl_metric_context_regular_tetrahedron_solid_angle_identity():
    context = VolblMetricContext(
        coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        ),
        radii=np.ones(4, dtype=float),
        solvent_radius=0.0,
    )

    assert context.tetrahedron_volume(0, 1, 2, 3) == pytest.approx(1.0 / 6.0)
    assert context.sector_volume(0, 1, 2, 3) == pytest.approx(
        context.angle_solid(0, 1, 2, 3) * context.ball_volume(0)
    )
    assert context.wedge_area(0, 1, 2, 3) == pytest.approx(
        context.angle_dihedral(
            context.vector(0),
            context.vector(1),
            context.vector(2),
            context.vector(3),
        )
        * context.ball2_area(0, 1)
    )


def test_volbl_metric_context_intermediate_primitives_are_finite_and_composed():
    context = VolblMetricContext(
        coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        ),
        radii=np.full(4, 2.0, dtype=float),
        solvent_radius=0.0,
    )

    values = [
        context.segment_height(0, 1, 2),
        context.segment_angle(0, 1, 2),
        context.segment_area(0, 1, 2),
        context.segment2_angle(0, 1, 2, 3),
        context.segment2_area(0, 1, 2, 3),
        context.cap2_area(0, 1, 2),
        context.cap2_volume(0, 1, 2),
        context.cap3_area(0, 1, 2, 3),
        context.cap3_volume(0, 1, 2, 3),
        context.ball3_area(0, 1, 2),
        context.ball3_volume(0, 1, 2),
        context.ball4_area(0, 1, 2, 3),
        context.ball4_volume(0, 1, 2, 3),
    ]

    assert all(np.isfinite(value) for value in values)
    assert context.ball3_volume(0, 1, 2) == pytest.approx(
        context.cap2_volume(0, 1, 2)
        + context.cap2_volume(1, 0, 2)
        + context.cap2_volume(2, 0, 1)
    )
    assert context.ball4_area(0, 1, 2, 3) == pytest.approx(
        context.cap3_area(0, 1, 2, 3)
        + context.cap3_area(1, 0, 2, 3)
        + context.cap3_area(2, 0, 1, 3)
        + context.cap3_area(3, 0, 1, 2)
    )
    assert context.pawn_volume(0, 1, 2) == pytest.approx(
        0.5 * context.ball3_volume(0, 1, 2)
    )


def test_volbl_metric_context_patch_and_torus_are_finite():
    context = VolblMetricContext(
        coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        ),
        radii=np.full(4, 2.0, dtype=float),
        solvent_radius=0.5,
    )

    patch = context.patch(0, 1, 2)
    torus = context.torus(0, 1)

    assert np.isfinite(
        [
            patch.area,
            patch.volume,
            patch.area_1,
            patch.volume_1,
            torus.area_1,
            torus.area_2,
            torus.volume_1,
            torus.volume_2,
            torus.volume_mod_1,
            torus.volume_mod_2,
        ]
    ).all()
    assert patch.area == pytest.approx(patch.area_1 + patch.area_2 + patch.area_3)
    assert patch.volume == pytest.approx(
        patch.volume_1 + patch.volume_2 + patch.volume_3
    )


def test_space_filling_measurements_single_vertex_matches_volbl_block():
    geometry = SimpleNamespace(
        atom_coordinates=np.asarray([[0.0, 0.0, 0.0]], dtype=float),
        atom_radii=np.asarray([2.0], dtype=float),
        solvent_radius=0.0,
        edge_rho_ranks={},
        face_records=[],
        mesh=SimpleNamespace(simplex_atom_indices=np.empty((0, 4), dtype=int)),
        master_entries=[
            CastpMasterEntry(
                rank=1,
                f_type=ALF_VERTEX,
                r_type=ALF_RHO,
                index=0,
                is_attached=False,
                is_first=True,
            )
        ],
        master_rank_offsets={1: (0, 1)},
    )
    context = VolblMetricContext(
        coordinates=geometry.atom_coordinates,
        radii=geometry.atom_radii,
        solvent_radius=0.0,
    )

    measurements = space_filling_measurements(geometry, input_rank=1)

    assert measurements.volume_sa == pytest.approx(context.ball_volume(0))
    assert measurements.volume_ms == pytest.approx(context.ball_volume(0))
    assert measurements.area_sa == pytest.approx(context.ball_area(0))
    assert measurements.area_ms == pytest.approx(context.ball_area(0))
    assert measurements.length == pytest.approx(0.0)
    assert measurements.corners == 0


def test_space_filling_measurements_edge_matches_volbl_inclusion_exclusion():
    coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    radii = np.asarray([1.0, 1.0], dtype=float)
    geometry = SimpleNamespace(
        atom_coordinates=coordinates,
        atom_radii=radii,
        solvent_radius=0.0,
        edge_rho_ranks={(0, 1): 2},
        face_records=[],
        mesh=SimpleNamespace(simplex_atom_indices=np.empty((0, 4), dtype=int)),
        master_entries=[
            CastpMasterEntry(
                rank=1,
                f_type=ALF_VERTEX,
                r_type=ALF_RHO,
                index=0,
                is_attached=False,
                is_first=True,
            ),
            CastpMasterEntry(
                rank=1,
                f_type=ALF_VERTEX,
                r_type=ALF_RHO,
                index=1,
                is_attached=False,
                is_first=True,
            ),
            CastpMasterEntry(
                rank=2,
                f_type=ALF_EDGE,
                r_type=ALF_RHO,
                index=0,
                is_attached=False,
                is_first=True,
            ),
        ],
        master_rank_offsets={1: (0, 2), 2: (2, 3)},
    )
    context = VolblMetricContext(
        coordinates=coordinates,
        radii=radii,
        solvent_radius=0.0,
    )

    measurements = space_filling_measurements(geometry, input_rank=2)

    expected_volume = (
        context.ball_volume(0)
        + context.ball_volume(1)
        - context.cap_volume(0, 1)
        - context.cap_volume(1, 0)
    )
    expected_area = (
        context.ball_area(0)
        + context.ball_area(1)
        - context.cap_area(0, 1)
        - context.cap_area(1, 0)
    )
    assert measurements.volume_sa == pytest.approx(expected_volume)
    assert measurements.volume_ms == pytest.approx(expected_volume)
    assert measurements.area_sa == pytest.approx(expected_area)
    assert measurements.area_ms == pytest.approx(expected_area)
    assert measurements.length == pytest.approx(context.ball2_length(0, 1))
    assert measurements.corners == 0


def test_voids_measurements_single_void_keeps_initial_tetra_volume_without_boundary_terms():
    coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    radii = np.full(4, 2.0, dtype=float)
    mesh = SimpleNamespace(
        n_simplices=1,
        simplex_atom_indices=np.asarray([[0, 1, 2, 3]], dtype=int),
        neighbors=np.asarray([[-1, -1, -1, -1]], dtype=int),
    )
    geometry = SimpleNamespace(
        atom_coordinates=coordinates,
        atom_radii=radii,
        solvent_radius=0.0,
        mesh=mesh,
        base_rank=1,
        spectrum_values=np.asarray([0.0, 1.0], dtype=float),
        simplex_rho_ranks=np.asarray([2], dtype=int),
        master_entries=[
            CastpMasterEntry(
                rank=2,
                f_type=ALF_TETRA,
                r_type=ALF_RHO,
                index=0,
                is_attached=False,
                is_first=True,
            )
        ],
        master_rank_offsets={2: (0, 1)},
        face_records=[
            (0, 0, (1, 2, 3)),
            (0, 1, (0, 2, 3)),
            (0, 2, (0, 1, 3)),
            (0, 3, (0, 1, 2)),
        ],
        face_rho_ranks=np.full((1, 4), 2, dtype=int),
        face_mu1_ranks=np.full((1, 4), 2, dtype=int),
        face_mu2_ranks=np.full((1, 4), 0, dtype=int),
        edge_rho_ranks={
            (0, 1): 2,
            (0, 2): 2,
            (0, 3): 2,
            (1, 2): 2,
            (1, 3): 2,
            (2, 3): 2,
        },
        edge_mu1_ranks={},
        edge_mu2_ranks={},
        vertex_rho_ranks=np.full(4, 2, dtype=int),
        vertex_mu1_ranks=np.full(4, 2, dtype=int),
        vertex_mu2_ranks=np.zeros(4, dtype=int),
    )
    context = VolblMetricContext(
        coordinates=coordinates,
        radii=radii,
        solvent_radius=0.0,
    )

    measurements = voids_measurements(geometry, input_rank=1)

    assert len(measurements.voids) == 1
    assert measurements.total_volume_sa == pytest.approx(
        context.tetrahedron_volume(0, 1, 2, 3)
    )
    assert measurements.total_volume_ms == pytest.approx(
        context.tetrahedron_volume(0, 1, 2, 3)
    )
    assert measurements.total_area_sa == pytest.approx(0.0)
    assert measurements.total_area_ms == pytest.approx(0.0)
    assert measurements.total_length == pytest.approx(0.0)
    assert measurements.total_corners == 0


def test_shape_volume_and_envelope_use_same_tetra_volume_contract():
    coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    radii = np.full(4, 2.0, dtype=float)
    mesh = SimpleNamespace(
        n_simplices=1,
        simplex_atom_indices=np.asarray([[0, 1, 2, 3]], dtype=int),
        neighbors=np.asarray([[-1, -1, -1, -1]], dtype=int),
    )
    geometry = SimpleNamespace(
        atom_coordinates=coordinates,
        atom_radii=radii,
        solvent_radius=0.0,
        mesh=mesh,
        base_rank=1,
        spectrum_values=np.asarray([0.0, 1.0], dtype=float),
        simplex_rho_ranks=np.asarray([2], dtype=int),
        master_entries=[
            CastpMasterEntry(
                rank=2,
                f_type=ALF_TETRA,
                r_type=ALF_RHO,
                index=0,
                is_attached=False,
                is_first=True,
            )
        ],
        master_rank_offsets={2: (0, 1)},
        face_records=[
            (0, 0, (1, 2, 3)),
            (0, 1, (0, 2, 3)),
            (0, 2, (0, 1, 3)),
            (0, 3, (0, 1, 2)),
        ],
        face_rho_ranks=np.full((1, 4), 2, dtype=int),
        face_mu1_ranks=np.full((1, 4), 2, dtype=int),
        face_mu2_ranks=np.full((1, 4), 0, dtype=int),
        edge_rho_ranks={
            (0, 1): 2,
            (0, 2): 2,
            (0, 3): 2,
            (1, 2): 2,
            (1, 3): 2,
            (2, 3): 2,
        },
        edge_mu1_ranks={},
        edge_mu2_ranks={},
        vertex_rho_ranks=np.full(4, 2, dtype=int),
        vertex_mu1_ranks=np.full(4, 2, dtype=int),
        vertex_mu2_ranks=np.zeros(4, dtype=int),
    )
    context = VolblMetricContext(
        coordinates=coordinates,
        radii=radii,
        solvent_radius=0.0,
    )
    expected_volume = context.tetrahedron_volume(0, 1, 2, 3)

    envelope = envelope_measurements(geometry, input_rank=1)

    assert shape_volume(geometry, input_rank=1) == pytest.approx(0.0)
    assert shape_volume(geometry, input_rank=2) == pytest.approx(expected_volume)
    assert envelope.shape_volume == pytest.approx(0.0)
    assert envelope.shape_volume_ms == pytest.approx(0.0)
    assert envelope.voids.total_volume_sa == pytest.approx(expected_volume)


@pytest.mark.parametrize('case_id', sorted(CASTP1_VOLBL_ORACLE_TOTALS))
def test_native_volbl_matches_local_castp1_oracle_totals(case_id):
    oracle_root = Path('sandbox/castp_oracle_runs')
    if not oracle_root.exists():
        pytest.skip('local CASTp 1.0 oracle runs are not available')

    case_dir = oracle_root / case_id
    pdb_path = case_dir / f'{case_id}.pdb'
    if not pdb_path.exists():
        pytest.skip(f'local CASTp 1.0 oracle PDB is not available for {case_id}')

    geometry = build_castp_geometry(pdb_path, radii_model='castp_param')
    rank0 = _rank_of_ratio(tuple(geometry.spectrum_ratios), ExactRatio(0, 1))
    measurements = volbl_measurements(geometry, rank0)
    space_filling = measurements.space_filling
    voids = measurements.voids
    fringe = measurements.fringe
    shape = measurements.shape_volume
    expected = CASTP1_VOLBL_ORACLE_TOTALS[case_id]

    observed = {
        'Vsf_sa': space_filling.volume_sa,
        'Vsf_ms': space_filling.volume_ms,
        'Vtv_sa': voids.total_volume_sa,
        'Vtv_ms': voids.total_volume_ms,
        'Vtiv': sum(item.initial_volume for item in voids.voids),
        'Vof_sa': fringe.volume_sa,
        'Vof_ms': fringe.volume_ms,
        'Vsh': shape,
        'Asf_sa': space_filling.area_sa,
        'Asf_ms': space_filling.area_ms,
        'Atv_sa': voids.total_area_sa,
        'Atv_ms': voids.total_area_ms,
        'Aof_sa': fringe.area_sa,
        'Aof_ms': fringe.area_ms,
        'Lsf': space_filling.length,
        'Ltv': voids.total_length,
        'Lof': fringe.length,
        'Csf': space_filling.corners,
        'Ctv': voids.total_corners,
        'Cof': fringe.corners,
        'void_count': len(voids.voids),
    }

    for key, expected_value in expected.items():
        if key.startswith('C') or key == 'void_count':
            assert observed[key] == expected_value
        else:
            assert observed[key] == pytest.approx(expected_value, abs=1.0e-2)


def test_build_rank_driven_components_drains_delayed_tetrahedra_as_lifo_stack():
    master_entries, master_rank_offsets = _tetra_rho_master({2: [1, 2], 3: [0]})

    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [1, 2, -1, -1],
                [0, -1, -1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        ),
        n_simplices=3,
        get_face_index=lambda simplex_index, face_index: 100 + 10 * int(simplex_index) + int(face_index),
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        base_rank=1,
        simplex_rho_ranks=np.asarray([3, 2, 2], dtype=int),
        master_entries=master_entries,
        master_rank_offsets=master_rank_offsets,
        simplex_rank_sublists={2: [1, 2], 3: [0]},
        face_is_on_hull=np.asarray(
            [
                [False, False, True, True],
                [False, True, True, True],
                [False, True, True, True],
            ],
            dtype=bool,
        ),
        face_rho_ranks=np.asarray(
            [
                [0, 0, 3, 3],
                [0, 2, 2, 2],
                [0, 2, 2, 2],
            ],
            dtype=int,
        ),
        face_mu1_ranks=np.asarray(
            [
                [2, 2, 0, 0],
                [2, 0, 0, 0],
                [2, 0, 0, 0],
            ],
            dtype=int,
        ),
        atom_coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        ),
    )
    geometry.mesh.weights = np.zeros(4, dtype=float)
    geometry.mesh.simplex_atom_indices = np.asarray(
        [
            [0, 1, 2, 3],
            [0, 1, 2, 3],
            [0, 1, 2, 3],
        ],
        dtype=int,
    )

    events = []
    components, blocked_nodes, depth = _build_rank_driven_components(
        geometry,
        size_limit_rank=3,
        rank1=1,
        event_hook=lambda index, event_type: events.append((int(index), int(event_type))),
    )

    tetra_event_order = [index for index, event_type in events if event_type == ALF_POC_TETRA]

    assert components == {0: [0, 1, 2]}
    assert blocked_nodes == set()
    assert depth.tolist() == [0, 0, 0]
    assert tetra_event_order == [2, 1, 0]


def test_build_rank_driven_components_event_sequence_delays_same_rank_non_sink_tetrahedra():
    master_entries, master_rank_offsets = _tetra_rho_master({2: [1, 2, 0]})

    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [1, 2, -1, -1],
                [0, -1, -1, -1],
                [0, -1, -1, -1],
            ],
            dtype=int,
        ),
        n_simplices=3,
        get_face_index=lambda simplex_index, face_index: 200 + 10 * int(simplex_index) + int(face_index),
        get_face_owner_indices=lambda simplex_index, face_index: (
            (int(simplex_index), int(mesh.neighbors[int(simplex_index), int(face_index)]))
            if int(mesh.neighbors[int(simplex_index), int(face_index)]) != -1
            else (int(simplex_index), -1)
        ),
        get_face_atoms=lambda simplex_index, face_index: {
            (0, 0): (1, 2, 3),
            (0, 1): (0, 2, 3),
            (0, 2): (0, 1, 3),
            (0, 3): (0, 1, 2),
            (1, 0): (1, 2, 3),
            (1, 1): (0, 2, 3),
            (1, 2): (0, 1, 3),
            (1, 3): (0, 1, 2),
            (2, 0): (0, 2, 3),
            (2, 1): (1, 2, 3),
            (2, 2): (0, 1, 3),
            (2, 3): (0, 1, 2),
        }[(int(simplex_index), int(face_index))],
    )
    geometry = SimpleNamespace(
        mesh=mesh,
        base_rank=1,
        simplex_rho_ranks=np.asarray([2, 2, 2], dtype=int),
        master_entries=master_entries,
        master_rank_offsets=master_rank_offsets,
        simplex_rank_sublists={2: [1, 2, 0]},
        face_is_on_hull=np.asarray(
            [
                [False, False, True, True],
                [False, True, True, True],
                [False, True, True, True],
            ],
            dtype=bool,
        ),
        face_rho_ranks=np.asarray(
            [
                [0, 0, 2, 2],
                [0, 2, 2, 2],
                [0, 2, 2, 2],
            ],
            dtype=int,
        ),
        face_mu1_ranks=np.asarray(
            [
                [2, 2, 0, 0],
                [2, 0, 0, 0],
                [2, 0, 0, 0],
            ],
            dtype=int,
        ),
        atom_coordinates=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=float,
        ),
    )
    geometry.mesh.weights = np.zeros(4, dtype=float)
    geometry.mesh.simplex_atom_indices = np.asarray(
        [
            [0, 1, 2, 3],
            [0, 1, 2, 3],
            [0, 1, 2, 3],
        ],
        dtype=int,
    )

    events = []
    components, blocked_nodes, depth = _build_rank_driven_components(
        geometry,
        size_limit_rank=2,
        rank1=1,
        event_hook=lambda index, event_type: events.append((int(index), int(event_type))),
    )

    tetra_event_order = [index for index, event_type in events if event_type == ALF_POC_TETRA]

    assert components == {0: [0, 1, 2]}
    assert blocked_nodes == set()
    assert depth.tolist() == [0, 0, 2]
    assert tetra_event_order == [2, 1, 0]


def test_weighted_delaunay_mesh_preserves_oriented_tetrahedra():
    points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    mesh = WeightedDelaunayMesh(points=points, weights=np.zeros(4, dtype=float))

    sorted_simplex = tuple(int(atom_index) for atom_index in mesh.simplices[0])
    oriented_simplex = tuple(int(atom_index) for atom_index in mesh.oriented_simplices[0])

    tetrahedron_points = points[list(oriented_simplex)]
    orientation = np.linalg.det(
        np.vstack(
            (
                tetrahedron_points[1] - tetrahedron_points[0],
                tetrahedron_points[2] - tetrahedron_points[0],
                tetrahedron_points[3] - tetrahedron_points[0],
            )
        )
    )

    assert sorted_simplex == (0, 1, 2, 3)
    assert orientation > 0.0
    assert tuple(sorted(oriented_simplex)) == sorted_simplex
    assert mesh.get_face_atoms(0, 0) == tuple(sorted(oriented_simplex[index] for index in (1, 2, 3)))


def test_weighted_delaunay_mesh_returns_outward_oriented_faces():
    points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    mesh = WeightedDelaunayMesh(points=points, weights=np.zeros(4, dtype=float))

    assert mesh.get_oriented_face_atoms(0, 0) == (
        int(mesh.oriented_simplices[0, 1]),
        int(mesh.oriented_simplices[0, 2]),
        int(mesh.oriented_simplices[0, 3]),
    )
    assert mesh.get_oriented_face_atoms(0, 1) == (
        int(mesh.oriented_simplices[0, 0]),
        int(mesh.oriented_simplices[0, 3]),
        int(mesh.oriented_simplices[0, 2]),
    )


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
        np.asarray([1.0, 1.0, 0.0], dtype=float),
        0.0,
    ) == 2


def test_weighted_hidden1_matches_attached_vs_non_attached_edge_cases():
    edge_points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    edge_weights = np.asarray([0.0, 0.0], dtype=float)

    assert _weighted_hidden1(
        edge_points,
        edge_weights,
        np.asarray([0.5, 0.1, 0.0], dtype=float),
        0.0,
    ) > 0
    assert _weighted_hidden1(
        edge_points,
        edge_weights,
        np.asarray([0.5, 0.5, 0.0], dtype=float),
        0.0,
    ) == 2
    assert _weighted_hidden1(
        edge_points,
        edge_weights,
        np.asarray([0.5, 1.0, 0.0], dtype=float),
        0.0,
    ) == 0


def test_weighted_hidden1_matches_castp1_lia_ffpload_regression_for_1lyz_edge():
    edge_points = np.asarray(
        [
            [10.547, 16.150, 35.059],
            [9.229, 15.623, 34.806],
        ],
        dtype=float,
    )
    edge_radii = np.asarray([3.025, 3.300], dtype=float)
    probe_point = np.asarray([10.547, 17.139, 35.754], dtype=float)
    probe_radius = 3.275

    assert _weighted_hidden1(
        edge_points,
        edge_radii * edge_radii,
        probe_point,
        probe_radius * probe_radius,
    ) == 0


def test_weighted_hidden0_matches_vertex_attachment_semantics():
    vertex_point = np.asarray([0.0, 0.0, 0.0], dtype=float)

    assert _weighted_hidden0(
        vertex_point,
        1.0,
        np.asarray([0.0, 0.0, 0.0], dtype=float),
        4.0,
    ) == 1
    assert _weighted_hidden0(
        vertex_point,
        0.0,
        np.asarray([1.0, 0.0, 0.0], dtype=float),
        1.0,
    ) == 2
    assert _weighted_hidden0(
        vertex_point,
        1.0,
        np.asarray([1.0, 0.0, 0.0], dtype=float),
        1.0,
    ) == 0


def test_deduplicate_weighted_points_keeps_largest_radius_for_duplicate_coordinates():
    atom_coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    atom_radii = np.asarray([1.0, 1.5, 2.0, 1.0, 1.5], dtype=float)
    atom_indices_map = np.asarray([10, 11, 12, 13, 14], dtype=int)

    kept_coordinates, kept_radii, kept_indices = _deduplicate_weighted_points(
        atom_coordinates,
        atom_radii,
        atom_indices_map,
    )

    assert kept_coordinates.tolist() == [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [2.0, 0.0, 0.0],
    ]
    assert kept_radii.tolist() == [2.0, 1.5, 1.0]
    assert kept_indices.tolist() == [12, 11, 13]


def test_discard_redundant_weighted_points_removes_hidden_vertex_from_regular_triangulation():
    atom_coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.25, 0.25, 0.25],
        ],
        dtype=float,
    )
    atom_radii = np.asarray([1.0, 1.0, 1.0, 1.0, 0.0], dtype=float)
    atom_indices_map = np.asarray([10, 11, 12, 13, 14], dtype=int)

    kept_coordinates, kept_radii, kept_indices = _discard_redundant_weighted_points(
        atom_coordinates,
        atom_radii,
        atom_indices_map,
    )

    assert kept_coordinates.tolist() == atom_coordinates[:4].tolist()
    assert kept_radii.tolist() == [1.0, 1.0, 1.0, 1.0]
    assert kept_indices.tolist() == [10, 11, 12, 13]


def test_exact_rho_rank_tables_classify_attached_and_redundant_vertices_like_mkalf():
    mesh = SimpleNamespace(
        n_simplices=0,
        simplex_atom_indices=np.empty((0, 4), dtype=int),
    )
    atom_coordinates = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [4.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    atom_radii = np.asarray([1.0, 2.0, 1.0], dtype=float)

    (
        _simplex_rho_ranks,
        _face_rho_ranks,
        _edge_rho_ranks,
        vertex_rho_ranks,
        _spectrum_values,
        _spectrum_ratios,
        _spectrum_decimals,
    ) = _build_exact_rho_rank_tables(
        mesh,
        atom_coordinates,
        atom_radii,
        np.asarray([], dtype=float),
        np.zeros((0, 4), dtype=float),
        {(0, 1): 0.0},
        [],
    )

    assert vertex_rho_ranks.tolist() == [0, 1, -1]


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


@pytest.mark.parametrize('case_id', CASTP1_ORACLE_CASES)
def test_native_castp1_matches_local_mkalf_structural_outputs(case_id):
    oracle_root = Path('sandbox/castp_oracle_runs')
    if not oracle_root.exists():
        pytest.skip('local CASTp 1.0 oracle runs are not available')

    alpha_rank, beta_rank, poc_path, voids_path = _castp1_oracle_paths(case_id)
    case_dir = oracle_root / case_id
    geometry = build_castp_geometry(
        case_dir / f'{case_id}.pdb',
        radii_model='castp_param',
    )
    records = castp_components.build_castp_feature_records(
        geometry,
        probe_radius=1.4,
        alpha_rank=alpha_rank,
        beta_rank=beta_rank,
    )

    native_poc_components = [
        _native_castp1_component_sets(geometry, record)
        for record in records
        if record['feature_type'] != 'void'
    ]
    native_void_components = [
        _native_castp1_component_sets(geometry, record)
        for record in records
        if record['feature_type'] == 'void'
    ]

    oracle_poc_components = _parse_castp1_feature_file(poc_path) if poc_path is not None else []
    oracle_void_components = (
        _parse_castp1_feature_file(voids_path)
        if voids_path is not None
        else []
    )

    _assert_castp1_components_match(
        native_poc_components,
        oracle_poc_components,
        case_id,
        'poc',
    )
    _assert_castp1_components_match(
        native_void_components,
        oracle_void_components,
        case_id,
        'voids',
    )


@pytest.mark.xfail(reason='CASTP 3.0 server parity is a later phase; current native target is CASTp1.')
def test_castp_voids_parity_1hiv():
    # 1HIV oracle: 3 voids.  The native implementation recovers all 3 exactly.
    oracle_topography = load_CASTp(zip_file='topomt/data/CASTp_3.0_server/1hiv.zip')
    oracle_void_atoms = {
        tuple(sorted(feature.atom_indices))
        for feature in oracle_topography.features.values()
        if feature.feature_type == 'void'
    }

    feature_records, _ = castp('topomt/data/HIV-1-Protease/CASTp_1hiv/1hiv.pdb')
    native_void_atoms = {
        tuple(sorted(feature['atom_indices']))
        for feature in feature_records
        if feature['feature_type'] == 'void'
    }

    # All three oracle voids must be present exactly.
    assert tuple(sorted([67, 86, 180, 624])) in native_void_atoms                                         # VOI-1
    assert tuple(sorted([480, 499, 561, 578, 679, 680])) in native_void_atoms                             # VOI-2
    assert tuple(sorted([866, 882, 914, 915, 917, 1008, 1009, 1035, 1389, 1391])) in native_void_atoms    # VOI-3

    # No spurious voids beyond the oracle set.
    assert native_void_atoms <= oracle_void_atoms

    # Document parity status: 3/3.
    recovered = len(native_void_atoms & oracle_void_atoms)
    assert recovered == 3, f'Expected 3/3 oracle voids; got {recovered}'


@pytest.mark.xfail(reason='CASTP 3.0 server parity is a later phase; current native target is CASTp1.')
def test_castp_voids_parity_1tcd():
    # 1TCD oracle: 36 voids.  The native implementation recovers 35/36 exactly.
    # VOI-11 ([488, 695, 696, 790, 851]) is the one remaining residual: our
    # native finds the same tetrahedra but with one fewer lining atom (851),
    # because the corrected attachment criterion makes one boundary face attached.
    oracle_topography = load_CASTp(zip_file='topomt/data/CASTp_3.0_server/1tcd.zip')
    oracle_void_atoms = {
        feature.source_id: tuple(sorted(feature.atom_indices))
        for feature in oracle_topography.features.values()
        if feature.feature_type == 'void'
    }

    feature_records, _ = castp('topomt/data/TcTIM/CASTp_1tcd/1tcd.pdb')
    native_voids = {
        tuple(sorted(feature['atom_indices']))
        for feature in feature_records
        if feature['feature_type'] == 'void'
    }

    # A stable sample of recovered oracle voids (triangulation-independent).
    # Keys are source_ids from the CASTp server (Pocket numbering).
    recovered_sample = [
        'Pocket 25',  # [49, 50, 52, 53, ...]   (VOI-1)
        'Pocket 55',  # [67, 73, 95, 139, ...]   (VOI-3)
        'Pocket 65',  # [467, 670, 674, 676, ...] (VOI-9)
        'Pocket 50',  # [492, 493, 494, ...]      (VOI-12)
        'Pocket 66',  # [553, 1972, ...]           (VOI-13)
        'Pocket 47',  # [1966, 1983, 1986, ...]   (VOI-23)
    ]
    for void_id in recovered_sample:
        assert oracle_void_atoms[void_id] in native_voids, (
            f'{void_id} should be recovered but is not present in native voids'
        )

    # Overall parity: 35 of 36 expected.
    recovered = sum(1 for atoms in oracle_void_atoms.values() if atoms in native_voids)
    assert recovered == 35, f'Expected 35/36 oracle voids; got {recovered}'


@pytest.mark.xfail(reason='CASTP 3.0 server parity is a later phase; current native target is CASTp1.')
def test_castp_recovers_branched_channel_for_1a4j_pocket_2():
    oracle_topography = load_CASTp(zip_file='topomt/data/CASTp_3.0_server/1a4j.zip')
    oracle_feature = next(
        feature
        for feature in oracle_topography.features.values()
        if feature.source_id == 'Pocket 2'
    )

    with tempfile.TemporaryDirectory() as tmp:
        feature_records, _ = castp(_extract_castp_server_pdb('topomt/data/CASTp_3.0_server/1a4j.zip', tmp))
    native_feature = next(
        feature
        for feature in feature_records
        if tuple(sorted(feature['atom_indices'])) == tuple(sorted(oracle_feature.atom_indices))
    )

    assert oracle_feature.feature_type == 'branched_channel'
    assert native_feature['feature_type'] == 'branched_channel'
    assert native_feature['n_mouths'] == 3


@pytest.mark.xfail(reason='CASTP 3.0 server parity is a later phase; current native target is CASTp1.')
def test_castp_recovers_channel_for_1stp_pocket_7():
    oracle_topography = load_CASTp(zip_file='topomt/data/CASTp_3.0_server/1stp.zip')
    oracle_feature = next(
        feature
        for feature in oracle_topography.features.values()
        if feature.source_id == 'Pocket 7'
    )

    with tempfile.TemporaryDirectory() as tmp:
        feature_records, _ = castp(_extract_castp_server_pdb('topomt/data/CASTp_3.0_server/1stp.zip', tmp))
    native_feature = next(
        feature
        for feature in feature_records
        if tuple(sorted(feature['atom_indices'])) == tuple(sorted(oracle_feature.atom_indices))
    )

    assert oracle_feature.feature_type == 'channel'
    assert oracle_feature.n_mouths == 2
    assert native_feature['feature_type'] == 'channel'
    assert native_feature['n_mouths'] == 2


@pytest.mark.xfail(reason='CASTP 3.0 server parity is a later phase; current native target is CASTp1.')
def test_castp_short_green_battery_exact_feature_parity():
    cases = ['1stp', '1rop', '2lyz', '2pk4']

    for pdb_id in cases:
        zip_path = f'topomt/data/CASTp_3.0_server/{pdb_id}.zip'
        oracle_topography = load_CASTp(zip_file=zip_path)
        with tempfile.TemporaryDirectory() as tmp:
            feature_records, _ = castp(_extract_castp_server_pdb(zip_path, tmp))

        oracle_sets = _feature_atom_sets(oracle_topography)
        native_sets = _feature_atom_sets(feature_records)

        assert native_sets.get('pocket', set()) == oracle_sets.get('pocket', set()), pdb_id
        assert native_sets.get('channel', set()) == oracle_sets.get('channel', set()), pdb_id
        assert native_sets.get('branched_channel', set()) == oracle_sets.get('branched_channel', set()), pdb_id
        assert native_sets.get('void', set()) == oracle_sets.get('void', set()), pdb_id


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


def test_exact_size1_ratio_matches_weighted_edge_power_value():
    edge_points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    edge_radii = np.asarray([1.0, 0.5], dtype=float)

    _edge_center, edge_power_value = _weighted_edge_center_and_power(
        edge_points,
        edge_radii * edge_radii,
    )
    ratio = _edge_exact_ratio(edge_points, edge_radii, decimals=1)

    assert np.isclose(ratio.numerator / ratio.denominator / 100.0, edge_power_value)


def test_exact_size2_ratio_matches_weighted_face_power_value():
    face_points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
        ],
        dtype=float,
    )
    face_radii = np.asarray([1.0, 0.5, 0.5], dtype=float)

    _face_center, face_power_value = _weighted_face_center_and_power(
        face_points,
        face_radii * face_radii,
    )
    rows = _fixed_point_lifted_rows(face_points, face_radii, decimals=1)
    ratio = _face_exact_ratio(rows)

    assert np.isclose(ratio.numerator / ratio.denominator / 100.0, face_power_value)


def test_exact_size3_ratio_matches_weighted_tetrahedron_power_value():
    tetra_points = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 2.0],
        ],
        dtype=float,
    )
    tetra_radii = np.asarray([1.0, 0.5, 0.5, 0.5], dtype=float)
    mesh = WeightedDelaunayMesh(
        points=tetra_points,
        weights=tetra_radii * tetra_radii,
        atom_radii=tetra_radii,
    )

    rows = _fixed_point_lifted_rows(tetra_points, tetra_radii, decimals=1)
    ratio = _simplex_exact_ratio(rows)

    assert np.isclose(ratio.numerator / ratio.denominator / 100.0, mesh.simplex_power_values[0])
