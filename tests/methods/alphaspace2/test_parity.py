import importlib
import sys
from pathlib import Path

import mdtraj as md
import numpy as np
import pytest

from topomt.third_party.alphaspace2.native import (
    _build_state,
    _compute_beta_scores,
    _contact_matrix,
    _grid_volume,
    _overlap_matrices,
    _prepare_receptor,
    alphaspace2,
)
from topomt._private.arg_digestion.argument.binder_coords import digest_binder_coords


UPSTREAM_PROTEASE_DATASET = (
    Path.home()
    / 'repos@others'
    / 'AlphaSpace2'
    / 'cookbooks'
    / 'DataSet'
    / 'Binding_Site_comparison'
    / 'protease'
)

UPSTREAM_CDK2_PDB_PATH = (
    Path.home()
    / 'repos@others'
    / 'AlphaSpace2'
    / 'cookbooks'
    / 'DataSet'
    / 'CDK2_Communities'
    / 'cdk2_prot.pdb'
)

UPSTREAM_CDK2_PDBQT_PATH = (
    Path.home()
    / 'repos@others'
    / 'AlphaSpace2'
    / 'cookbooks'
    / 'DataSet'
    / 'CDK2_Communities'
    / 'cdk2_prot.pdbqt'
)


def _import_upstream_alphaspace2():
    try:
        return importlib.import_module('alphaspace2')
    except ImportError:
        repo_path = Path.home() / 'repos@others' / 'AlphaSpace2'
        if not repo_path.exists():
            pytest.skip('AlphaSpace2 upstream repository not available for parity testing')
        sys.path.insert(0, str(repo_path))
        return importlib.import_module('alphaspace2')


def _patch_upstream_compatibility():
    import numpy as np
    from mdtraj.geometry import _geometry
    from mdtraj.geometry.sasa import _ATOMIC_RADII

    setattr(np, 'float', float)
    setattr(np, 'bool', np.bool_)
    setattr(np, 'in1d', np.isin)

    functions = importlib.import_module('alphaspace2.functions')

    def compat_get_sasa(protein_snapshot, cover_atom_coords=None):
        probe_radius = 0.14
        n_sphere_points = 960

        if cover_atom_coords is None:
            xyz = np.array(protein_snapshot.xyz, dtype=np.float32)
            atom_radii = [_ATOMIC_RADII[atom.element.symbol] for atom in protein_snapshot.topology.atoms]
        else:
            xyz = np.array(
                np.expand_dims(
                    np.concatenate((protein_snapshot.xyz[0], cover_atom_coords), axis=0),
                    axis=0,
                ),
                dtype=np.float32,
            )
            atom_radii = [_ATOMIC_RADII[atom.element.symbol] for atom in protein_snapshot.topology.atoms]
            atom_radii.extend([0.17] * (xyz.shape[1] - protein_snapshot.xyz.shape[1]))

        radii = np.array(atom_radii, np.float32) + probe_radius
        atom_mapping = np.arange(xyz.shape[1], dtype=np.int32)
        atom_selection_mask = np.ones(xyz.shape[1], dtype=np.int32)
        out = np.zeros((1, xyz.shape[1]), dtype=np.float32)
        _geometry._sasa(xyz, radii, int(n_sphere_points), atom_mapping, atom_selection_mask, out)
        return out[:, :protein_snapshot.xyz.shape[1]][0]

    functions.getSASA = compat_get_sasa


def _filtered_upstream_receptor(pdb_path: Path):
    receptor = md.load(str(pdb_path))
    keep_atom_indices = [
        atom.index
        for atom in receptor.topology.atoms
        if atom.element is None or atom.element.symbol != 'H'
    ]
    return receptor.atom_slice(keep_atom_indices)


def _native_pocket_scores_from_state(state) -> np.ndarray:
    beta_scores = np.asarray(state.beta_scores)

    if beta_scores.ndim == 2:
        beta_scalar_scores = np.min(beta_scores, axis=1)
    else:
        beta_scalar_scores = beta_scores.astype(float)

    return np.array(
        [
            float(np.sum(beta_scalar_scores[beta_indices])) if len(beta_indices) > 0 else 0.0
            for beta_indices in state.pocket_beta_index_list
        ],
        dtype=float,
    )


@pytest.mark.parametrize('pdb_name', ['1GG0.pdb', '3LKF.pdb'])
def test_alphaspace2_native_state_matches_upstream_snapshot(pdb_name):
    alphaspace2 = _import_upstream_alphaspace2()
    _patch_upstream_compatibility()

    pdb_path = Path('topomt/data/fpocket4/sample') / pdb_name

    receptor = _filtered_upstream_receptor(pdb_path)
    snapshot = alphaspace2.Snapshot()
    snapshot.run(receptor)

    state = _build_state(
        molecular_system=str(pdb_path),
        selection='all',
        structure_indices=0,
        min_radius_nm=0.32,
        max_radius_nm=0.54,
        cluster_cutoff_nm=0.47,
        beta_cluster_cutoff_nm=0.16,
        syntax='MolSysMT',
    )

    assert len(state.alpha_centers_nm) == len(snapshot._alpha_xyz)
    assert np.allclose(
        np.sort(state.alpha_radii_nm),
        np.sort(np.asarray(snapshot._alpha_radii) / 10.0),
        atol=1.5e-4,
    )
    assert np.isclose(
        np.sum(state.alpha_space_nm3),
        np.sum(np.asarray(snapshot._alpha_space) / 1000.0),
    )

    assert len(state.pocket_alpha_index_list) == len(list(snapshot.pockets))

    upstream_pocket_lining_sets = {
        tuple(sorted(np.unique(np.asarray(pocket.lining_atoms_idx, dtype=int).reshape(-1)).tolist()))
        for pocket in snapshot.pockets
    }
    native_pocket_lining_sets = {
        tuple(
            sorted(
                np.unique(state.alpha_lining_local_indices[alpha_indices].reshape(-1)).astype(int).tolist()
            )
        )
        for alpha_indices in state.pocket_alpha_index_list
    }

    assert native_pocket_lining_sets == upstream_pocket_lining_sets

    upstream_beta_group_sets = {
        tuple(sorted(np.asarray(beta_alpha_indices, dtype=int).tolist()))
        for beta_alpha_indices in snapshot._beta_alpha_index_list
    }
    native_beta_group_sets = {
        tuple(sorted(np.asarray(beta_alpha_indices, dtype=int).tolist()))
        for beta_alpha_indices in state.beta_alpha_index_list
    }

    assert len(state.beta_centers_nm) == len(snapshot._beta_xyz)
    assert upstream_beta_group_sets == native_beta_group_sets
    assert np.isclose(
        np.sum(state.beta_space_nm3),
        np.sum(np.asarray(snapshot._beta_space) / 1000.0),
    )
    assert np.allclose(np.asarray(snapshot._beta_scores), np.asarray(state.beta_scores))

    upstream_pocket_scores = np.array([float(pocket.score) for pocket in snapshot.pockets], dtype=float)
    native_pocket_scores = _native_pocket_scores_from_state(state)
    assert np.allclose(upstream_pocket_scores, native_pocket_scores)


def test_alphaspace2_native_grid_volume_matches_helper():
    state = _build_state(
        molecular_system='topomt/data/fpocket4/sample/1GG0.pdb',
        selection='all',
        structure_indices=0,
        min_radius_nm=0.32,
        max_radius_nm=0.54,
        cluster_cutoff_nm=0.47,
        beta_cluster_cutoff_nm=0.16,
        syntax='MolSysMT',
    )
    expected = np.array(
        [_grid_volume(state.alpha_centers_nm[indices]) for indices in state.pocket_alpha_index_list],
        dtype=float,
    )
    assert np.allclose(state.pocket_grid_volume_nm3, expected)


def test_alphaspace2_native_overlap_matrices_match_helper():
    state = _build_state(
        molecular_system='topomt/data/fpocket4/sample/1GG0.pdb',
        selection='all',
        structure_indices=0,
        min_radius_nm=0.32,
        max_radius_nm=0.54,
        cluster_cutoff_nm=0.47,
        beta_cluster_cutoff_nm=0.16,
        syntax='MolSysMT',
    )
    intersection, union = _overlap_matrices(state.pocket_alpha_index_list, len(state.alpha_centers_nm))
    assert np.allclose(state.pocket_overlap_intersection, intersection)
    assert np.allclose(state.pocket_overlap_union, union)


def test_alphaspace2_native_contact_matrix_matches_helper():
    binder = np.array([[0.35, 0.2, 0.15], [0.44, 0.79, 0.5]], dtype=float)
    _, _, _, _, state = alphaspace2(
        molecular_system='topomt/data/fpocket4/sample/1GG0.pdb',
        selection='all',
        structure_indices=0,
        binder_coords=binder,
        min_radius=0.32,
        max_radius=0.54,
        cluster_cutoff=0.47,
        beta_cluster_cutoff=0.16,
        syntax='MolSysMT',
        return_state=True,
    )
    expected = _contact_matrix(state.alpha_centers_nm, binder, 0.16)
    assert state.alpha_contact_matrix.shape == expected.shape
    assert np.array_equal(state.alpha_contact_matrix, expected)


def test_alphaspace2_pocket_connection_matrix_reflects_overlap():
    state = _build_state(
        molecular_system='topomt/data/fpocket4/sample/3LKF.pdb',
        selection='all',
        structure_indices=0,
        min_radius_nm=0.32,
        max_radius_nm=0.54,
        cluster_cutoff_nm=0.47,
        beta_cluster_cutoff_nm=0.16,
        syntax='MolSysMT',
    )
    overlap = _overlap_matrices(state.pocket_alpha_index_list, len(state.alpha_centers_nm))[0]
    assert np.array_equal(state.pocket_connection_matrix, overlap > 0)


def test_alphaspace2_beta_overlap_matches_helper():
    state = _build_state(
        molecular_system='topomt/data/fpocket4/sample/3LKF.pdb',
        selection='all',
        structure_indices=0,
        min_radius_nm=0.32,
        max_radius_nm=0.54,
        cluster_cutoff_nm=0.47,
        beta_cluster_cutoff_nm=0.16,
        syntax='MolSysMT',
    )
    intersection, union = _overlap_matrices(state.beta_alpha_index_list, len(state.alpha_centers_nm))
    assert np.allclose(state.beta_overlap_intersection, intersection)
    assert np.allclose(state.beta_overlap_union, union)


def test_alphaspace2_beta_probe_scores_match_helper():
    if not UPSTREAM_CDK2_PDB_PATH.exists() or not UPSTREAM_CDK2_PDBQT_PATH.exists():
        pytest.skip('AlphaSpace2 CDK2 Vina example not available for scoring comparison')

    receptor_data = _prepare_receptor(
        molecular_system=str(UPSTREAM_CDK2_PDB_PATH),
        selection='all',
        structure_indices=0,
        syntax='MolSysMT',
    )
    receptor, atom_indices, keep_local_indices = receptor_data

    state = _build_state(
        molecular_system=str(UPSTREAM_CDK2_PDB_PATH),
        selection='all',
        structure_indices=0,
        min_radius_nm=0.32,
        max_radius_nm=0.54,
        cluster_cutoff_nm=0.47,
        beta_cluster_cutoff_nm=0.16,
        syntax='MolSysMT',
        pdbqt_file=str(UPSTREAM_CDK2_PDBQT_PATH),
    )

    expected_probe_scores = _compute_beta_scores(
        receptor=receptor,
        keep_local_indices=keep_local_indices,
        coordinates_nm=state.coordinates_nm,
        beta_centers_nm=state.beta_centers_nm,
        pdbqt_file=str(UPSTREAM_CDK2_PDBQT_PATH),
    )

    assert np.allclose(state.beta_scores, expected_probe_scores)


@pytest.mark.parametrize(
    'pdb_path',
    [
        UPSTREAM_PROTEASE_DATASET / 'protein_1c70.pdb',
        UPSTREAM_PROTEASE_DATASET / 'protein_1hvi.pdb',
        UPSTREAM_PROTEASE_DATASET / 'protein_1pro.pdb',
    ],
    ids=['protein_1c70.pdb', 'protein_1hvi.pdb', 'protein_1pro.pdb'],
)
def test_alphaspace2_native_state_matches_upstream_snapshot_for_protease_examples(pdb_path):
    if not pdb_path.exists():
        pytest.skip(f'AlphaSpace2 protease example not available: {pdb_path.name}')

    alphaspace2 = _import_upstream_alphaspace2()
    _patch_upstream_compatibility()

    receptor = _filtered_upstream_receptor(pdb_path)
    snapshot = alphaspace2.Snapshot()
    snapshot.run(receptor)

    state = _build_state(
        molecular_system=str(pdb_path),
        selection='all',
        structure_indices=0,
        min_radius_nm=0.32,
        max_radius_nm=0.54,
        cluster_cutoff_nm=0.47,
        beta_cluster_cutoff_nm=0.16,
        syntax='MolSysMT',
    )

    assert len(state.alpha_centers_nm) == len(snapshot._alpha_xyz)
    assert np.allclose(
        np.sort(state.alpha_radii_nm),
        np.sort(np.asarray(snapshot._alpha_radii) / 10.0),
        atol=1.5e-4,
    )
    assert np.isclose(
        np.sum(state.alpha_space_nm3),
        np.sum(np.asarray(snapshot._alpha_space) / 1000.0),
    )

    assert len(state.pocket_alpha_index_list) == len(list(snapshot.pockets))

    upstream_pocket_lining_sets = {
        tuple(sorted(np.unique(np.asarray(pocket.lining_atoms_idx, dtype=int).reshape(-1)).tolist()))
        for pocket in snapshot.pockets
    }
    native_pocket_lining_sets = {
        tuple(
            sorted(
                np.unique(state.alpha_lining_local_indices[alpha_indices].reshape(-1)).astype(int).tolist()
            )
        )
        for alpha_indices in state.pocket_alpha_index_list
    }

    assert native_pocket_lining_sets == upstream_pocket_lining_sets

    upstream_beta_group_sets = {
        tuple(sorted(np.asarray(beta_alpha_indices, dtype=int).tolist()))
        for beta_alpha_indices in snapshot._beta_alpha_index_list
    }
    native_beta_group_sets = {
        tuple(sorted(np.asarray(beta_alpha_indices, dtype=int).tolist()))
        for beta_alpha_indices in state.beta_alpha_index_list
    }

    assert len(state.beta_centers_nm) == len(snapshot._beta_xyz)
    assert upstream_beta_group_sets == native_beta_group_sets
    assert np.isclose(
        np.sum(state.beta_space_nm3),
        np.sum(np.asarray(snapshot._beta_space) / 1000.0),
    )
    assert np.allclose(np.asarray(snapshot._beta_scores), np.asarray(state.beta_scores))

    upstream_pocket_scores = np.array([float(pocket.score) for pocket in snapshot.pockets], dtype=float)
    native_pocket_scores = _native_pocket_scores_from_state(state)
    assert np.allclose(upstream_pocket_scores, native_pocket_scores)


def test_alphaspace2_native_state_matches_upstream_snapshot_for_cdk2_vina_scores():
    if not UPSTREAM_CDK2_PDB_PATH.exists() or not UPSTREAM_CDK2_PDBQT_PATH.exists():
        pytest.skip('AlphaSpace2 CDK2 Vina example not available for parity testing')

    alphaspace2 = _import_upstream_alphaspace2()
    _patch_upstream_compatibility()

    receptor = _filtered_upstream_receptor(UPSTREAM_CDK2_PDB_PATH)
    alphaspace2.annotateVinaAtomTypes(receptor=receptor, pdbqt=str(UPSTREAM_CDK2_PDBQT_PATH))

    snapshot = alphaspace2.Snapshot()
    snapshot.run(receptor)

    state = _build_state(
        molecular_system=str(UPSTREAM_CDK2_PDB_PATH),
        selection='all',
        structure_indices=0,
        min_radius_nm=0.32,
        max_radius_nm=0.54,
        cluster_cutoff_nm=0.47,
        beta_cluster_cutoff_nm=0.16,
        syntax='MolSysMT',
        pdbqt_file=str(UPSTREAM_CDK2_PDBQT_PATH),
    )

    assert len(state.alpha_centers_nm) == len(snapshot._alpha_xyz)
    assert len(state.beta_centers_nm) == len(snapshot._beta_xyz)
    assert np.asarray(state.beta_scores).shape == np.asarray(snapshot._beta_scores).shape
    assert np.allclose(
        np.asarray(state.beta_scores),
        np.asarray(snapshot._beta_scores),
        atol=4.0e-3,
        rtol=0.0,
    )

    upstream_pocket_scores = np.array([float(pocket.score) for pocket in snapshot.pockets], dtype=float)
    native_pocket_scores = _native_pocket_scores_from_state(state)
    assert np.allclose(upstream_pocket_scores, native_pocket_scores, atol=5.0e-4, rtol=0.0)


def test_alphaspace2_native_state_matches_upstream_contact_flags():
    upstream_alphaspace2 = _import_upstream_alphaspace2()
    _patch_upstream_compatibility()

    pdb_path = Path('topomt/data/fpocket4/sample/1GG0.pdb')

    receptor = _filtered_upstream_receptor(pdb_path)
    snapshot = upstream_alphaspace2.Snapshot()
    snapshot.run(receptor)

    binder_coords_angstrom = np.asarray(snapshot._alpha_xyz[:1], dtype=float)
    snapshot.calculateContact(coords=binder_coords_angstrom)

    _, _, _, contacts, state = alphaspace2(
        molecular_system=str(pdb_path),
        selection='all',
        structure_indices=0,
        min_radius=0.32,
        max_radius=0.54,
        cluster_cutoff=0.47,
        beta_cluster_cutoff=0.16,
        syntax='MolSysMT',
        binder_coords=binder_coords_angstrom / 10.0,
        return_state=True,
    )

    assert np.array_equal(np.asarray(snapshot._alpha_contact, dtype=bool), np.asarray(contacts, dtype=bool))
    assert np.array_equal(np.asarray(snapshot._alpha_contact, dtype=bool), np.asarray(state.alpha_contact, dtype=bool))
    assert np.array_equal(np.asarray(snapshot._beta_contact, dtype=bool), np.asarray(state.beta_contact, dtype=bool))
    assert np.array_equal(np.asarray(snapshot._pocket_contact, dtype=bool), np.asarray(state.pocket_contact, dtype=bool))
def test_digest_binder_coords_accepts_array_like_shape_n_by_3():
    digested = digest_binder_coords([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]])

    assert isinstance(digested, np.ndarray)
    assert digested.shape == (2, 3)
