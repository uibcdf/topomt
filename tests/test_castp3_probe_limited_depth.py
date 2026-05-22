"""Experimental probe-limited depth tests for the CASTp3 backend."""

from types import SimpleNamespace

import numpy as np

from topomt.third_party.castp3.core.castp_core import components as castp3_components
from topomt.third_party.castp3.core.castp_core import mouths as castp3_mouths
from topomt.third_party.castp3.core.castp_core.mouths import EdgeFacetRecord
from topomt.third_party.castp3._native_impl import _component_to_record


def test_castp3_default_beta_rank_uses_max_depth_not_probe_cutoff(monkeypatch):
    geometry = SimpleNamespace(
        base_rank=7,
        mesh=SimpleNamespace(n_simplices=0),
    )
    captured = {}

    monkeypatch.setattr(castp3_components, '_geometry_max_rank', lambda geometry: 42)
    monkeypatch.setattr(castp3_components, '_probe_rank', lambda geometry, probe_radius: 11)

    def fake_build_at_ranks(
        geometry,
        probe_radius,
        alpha_rank,
        beta_rank,
        probe_limited_depth=False,
        peripheral_atom_expansion_steps=0,
        alpha_boundary_face_epsilon_rank=0,
    ):
        captured['alpha_rank'] = alpha_rank
        captured['beta_rank'] = beta_rank
        captured['probe_limited_depth'] = probe_limited_depth
        captured['peripheral_atom_expansion_steps'] = peripheral_atom_expansion_steps
        captured['alpha_boundary_face_epsilon_rank'] = alpha_boundary_face_epsilon_rank
        return []

    monkeypatch.setattr(
        castp3_components,
        '_build_castp_feature_records_at_ranks',
        fake_build_at_ranks,
    )

    records = castp3_components.build_castp_feature_records(
        geometry,
        probe_radius=1.4,
    )

    assert records == []
    assert captured == {
        'alpha_rank': 7,
        'beta_rank': 42,
        'probe_limited_depth': False,
        'peripheral_atom_expansion_steps': 0,
        'alpha_boundary_face_epsilon_rank': 0,
    }
    assert geometry.base_rank == 7


def test_component_peripheral_atom_indices_expands_reporting_atoms_only():
    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [1, -1, -1, -1],
                [0, 2, -1, -1],
                [1, -1, -1, -1],
            ],
            dtype=int,
        ),
        simplex_atom_indices=np.asarray(
            [
                [0, 1, 2, 3],
                [2, 3, 4, 5],
                [4, 5, 6, 7],
            ],
            dtype=int,
        ),
    )

    atom_indices = castp3_components._component_peripheral_atom_indices(
        mesh,
        np.asarray([10, 11, 12, 13, 14, 15, 16, 17], dtype=int),
        [0],
        expansion_steps=1,
    )

    assert atom_indices == [12, 13, 14, 15]


def test_component_peripheral_atom_indices_excludes_other_active_pockets():
    mesh = SimpleNamespace(
        neighbors=np.asarray(
            [
                [1, -1, -1, -1],
                [0, 2, -1, -1],
                [1, -1, -1, -1],
            ],
            dtype=int,
        ),
        simplex_atom_indices=np.asarray(
            [
                [0, 1, 2, 3],
                [2, 3, 4, 5],
                [4, 5, 6, 7],
            ],
            dtype=int,
        ),
    )

    atom_indices = castp3_components._component_peripheral_atom_indices(
        mesh,
        np.asarray([10, 11, 12, 13, 14, 15, 16, 17], dtype=int),
        [0],
        expansion_steps=2,
        excluded_simplex_indices={1},
    )

    assert atom_indices == []


def test_probe_limited_depth_keeps_accessible_sink_inside_beta(monkeypatch):
    geometry = SimpleNamespace(
        mesh=SimpleNamespace(
            n_simplices=2,
            neighbors=np.asarray([[1, -1, -1, -1], [0, -1, -1, -1]], dtype=int),
        ),
        face_is_on_hull=np.zeros((2, 4), dtype=bool),
        simplex_rho_ranks=np.asarray([2, 3], dtype=int),
    )

    monkeypatch.setattr(
        castp3_components,
        '_hidden_triangle',
        lambda geometry, simplex_index, face_index, neighbor_index: int(face_index) == 0,
    )
    monkeypatch.setattr(
        castp3_components,
        '_triangle_is_attached',
        lambda geometry, simplex_index, face_index: False,
    )
    monkeypatch.setattr(
        castp3_components,
        '_iter_master_tetra_rho_indices',
        lambda geometry, descending, rank_start, rank_end: [1, 0],
    )

    depth = castp3_components._compute_probe_limited_pocket_depths(
        geometry,
        size_limit_rank=2,
    )

    assert depth.tolist() == [0, -1]


def test_probe_limited_fnext_walk_exits_when_leaving_retained_pocket(monkeypatch):
    start = EdgeFacetRecord(
        oriented_face_atoms=(0, 1, 2),
        face_atoms=(0, 1, 2),
        triangle_index=10,
        simplex_index=0,
    )
    exit_facet = EdgeFacetRecord(
        oriented_face_atoms=(0, 1, 3),
        face_atoms=(0, 1, 3),
        triangle_index=11,
        simplex_index=1,
    )

    monkeypatch.setattr(
        castp3_mouths,
        '_edge_facet_fnext',
        lambda edge_facet, mesh: exit_facet,
    )

    result = castp3_mouths._fnext_walk_around_edge(
        start,
        mesh=SimpleNamespace(),
        depth=np.asarray([0, 0], dtype=int),
        infinity_marker=99,
        pocket_simplex_indices={0},
    )

    assert result == exit_facet


def test_probe_limited_fnext_walk_cuts_cycles_by_state(monkeypatch):
    start = EdgeFacetRecord(
        oriented_face_atoms=(0, 1, 2),
        face_atoms=(0, 1, 2),
        triangle_index=10,
        simplex_index=0,
    )

    monkeypatch.setattr(
        castp3_mouths,
        '_edge_facet_fnext',
        lambda edge_facet, mesh: edge_facet,
    )

    result = castp3_mouths._fnext_walk_around_edge(
        start,
        mesh=SimpleNamespace(),
        depth=np.asarray([0], dtype=int),
        infinity_marker=99,
        pocket_simplex_indices={0},
    )

    assert result is None


def test_castp3_native_record_exports_server_aggregated_mouth():
    component = {
        'id': 7,
        'feature_type': 'branched_channel',
        'atom_indices': [1, 2, 3, 4, 5],
        'volume': 10.0,
        'area': 5.0,
        'n_mouths': 2,
        'mouths': [
            {
                'id': 1,
                'atom_indices': [1, 2, 3],
                'area': 2.0,
                'perimeter': 3.0,
                'faces': [(1, 2, 3)],
                'triangle_indices': [11],
            },
            {
                'id': 2,
                'atom_indices': [3, 4, 5],
                'area': 4.0,
                'perimeter': 7.0,
                'faces': [(3, 4, 5)],
                'triangle_indices': [13],
            },
        ],
    }

    record = _component_to_record(
        component,
        molsys=None,
        feature_type='branched_channel',
        component_index=7,
    )

    assert record['n_mouths'] == 2
    assert len(record['topological_mouths']) == 2
    assert record['mouths'] == [
        {
            'id': 1,
            'atom_indices': [1, 2, 3, 4, 5],
            'area': 6.0,
            'perimeter': 10.0,
            'faces': [(1, 2, 3), (3, 4, 5)],
            'triangle_indices': [11, 13],
        }
    ]
