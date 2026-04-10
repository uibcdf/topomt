"""Native AlphaSpace2 reimplementation work in progress."""

from dataclasses import dataclass
from importlib.resources import files

import molsysmt as msm
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt._private.smonitor import signal
from topomt.delaunay_mesh import DelaunayMesh
from topomt._private.arg_digestion.argument.binder_coords import digest_binder_coords
from topomt.features import Pocket


@dataclass
class AlphaSpace2State:
    """Internal state for the native AlphaSpace2 reimplementation."""

    atom_indices: np.ndarray
    coordinates_nm: np.ndarray
    alpha_centers_nm: np.ndarray
    alpha_radii_nm: np.ndarray
    alpha_lining_local_indices: np.ndarray
    alpha_lining_atom_indices: np.ndarray
    alpha_space_nm3: np.ndarray
    alpha_nonpolar_ratio: np.ndarray
    pocket_alpha_index_list: list[list[int]]
    pocket_centers_nm: np.ndarray
    pocket_space_nm3: np.ndarray
    beta_alpha_index_list: list[list[int]]
    pocket_beta_index_list: list[list[int]]
    beta_centers_nm: np.ndarray
    beta_space_nm3: np.ndarray
    beta_scores: np.ndarray
    alpha_contact: np.ndarray
    beta_contact: np.ndarray
    pocket_contact: np.ndarray
    alpha_contact_matrix: np.ndarray
    pocket_grid_volume_nm3: np.ndarray
    pocket_overlap_intersection: np.ndarray
    pocket_overlap_union: np.ndarray
    pocket_connection_matrix: np.ndarray
    beta_overlap_intersection: np.ndarray
    beta_overlap_union: np.ndarray


POLAR_TYPES = np.array(['OA', 'OS', 'N', 'NS', 'NA', 'S', 'SA'], dtype=object)
ALIPHATIC_TYPES = {'C', 'A'}
PROBE_ELEMENTS = ['C', 'Br', 'F', 'Cl', 'I', 'OA', 'SA', 'N', 'P']
COFACTOR_MATCH_DICT = {
    'C': 'C',
    'N': 'N',
    'P': 'P',
    'O': 'OA',
    'S': 'SA',
    'F': 'F',
    'CL': 'Cl',
    'BR': 'Br',
    'I': 'I',
}

_VINA_SCORING_DATA = None


def _get_atom_element(atom_type, atom_name) -> str:
    normalized_atom_type = '' if atom_type is None else str(atom_type).strip().upper()
    if normalized_atom_type and normalized_atom_type not in {'NONE', 'NAN'}:
        if len(normalized_atom_type) >= 2 and normalized_atom_type[1].islower():
            return normalized_atom_type[0].upper() + normalized_atom_type[1].lower()
        return normalized_atom_type[0]

    if atom_name is None:
        return ''

    stripped_name = ''.join(character for character in str(atom_name).strip() if character.isalpha())
    if not stripped_name:
        return ''

    if len(stripped_name) >= 2 and stripped_name[1].islower():
        return stripped_name[0].upper() + stripped_name[1].lower()

    return stripped_name[0].upper()


def _load_vina_scoring_data():
    global _VINA_SCORING_DATA

    if _VINA_SCORING_DATA is not None:
        return _VINA_SCORING_DATA

    data_dir = files('topomt').joinpath('data', 'alphaspace2')

    hp_types_dict: dict[str, dict[str, tuple[str, str]]] = {}
    for line in data_dir.joinpath('hp_types_dict.dat').read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        residue_name, atom_name, for_acc, for_don = [item.strip() for item in stripped.split(',')]
        hp_types_dict.setdefault(residue_name, {})[atom_name] = (for_acc, for_don)

    typing_pdb_dict: dict[str, dict[str, str]] = {}
    for line in data_dir.joinpath('typing_from_pdb.dat').read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        residue_name, atom_name, atom_type = [item.strip() for item in stripped.split(',')]
        typing_pdb_dict.setdefault(residue_name, {})[atom_name] = atom_type

    autodock_types_dict: dict[str, tuple[float, bool]] = {}
    for line in data_dir.joinpath('autodock_atom_type_info.dat').read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        items = [item.strip() for item in stripped.split(',')]
        atom_type = items[0]
        autodock_types_dict[atom_type] = (float(items[1]) / 2.0, bool(int(items[7])))

    vina_terms: list[float] = []
    for line in data_dir.joinpath('vina_params.dat').read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('term'):
            continue
        _, weight, _ = [item.strip() for item in stripped.split(',', 2)]
        vina_terms.append(float(weight))

    _VINA_SCORING_DATA = (
        hp_types_dict,
        typing_pdb_dict,
        autodock_types_dict,
        np.array(vina_terms, dtype=np.float32),
    )
    return _VINA_SCORING_DATA


def _group_labels(labels: np.ndarray) -> list[list[int]]:
    groups = [[] for _ in range(int(np.max(labels)) + 1)]
    for index, label in enumerate(labels):
        groups[int(label)].append(index)
    return groups


def _prepare_receptor(
    molecular_system,
    selection: str,
    structure_indices: int,
    syntax: str,
) -> tuple[object, np.ndarray, np.ndarray]:
    full_molsys = msm.convert(
        molecular_system,
        to_form='molsysmt.MolSys',
        structure_indices=structure_indices,
    )
    selected_atom_indices = np.array(
        msm.select(full_molsys, selection=selection, syntax=syntax),
        dtype=int,
    )

    receptor = msm.convert(
        molecular_system,
        to_form='molsysmt.MolSys',
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )

    keep_local_indices = msm.select(
        molecular_system=receptor,
        selection='atom_type not in ["H"]',
        syntax='MolSysMT',
    )

    filtered_receptor = msm.convert(
        receptor,
        to_form='molsysmt.MolSys',
        selection=keep_local_indices,
        syntax='MolSysMT',
    )
    keep_local_indices = np.array(keep_local_indices, dtype=int)
    filtered_atom_indices = selected_atom_indices[keep_local_indices]

    return filtered_receptor, filtered_atom_indices, keep_local_indices


def _compute_alpha_layer(
    receptor,
    atom_indices: np.ndarray,
    structure_indices: int,
    min_radius_nm: float,
    max_radius_nm: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    coordinates = msm.get(
        molecular_system=receptor,
        coordinates=True,
        structure_indices=0 if structure_indices == 0 else structure_indices,
    )[0]
    coordinates_nm = np.asarray(puw.get_value(coordinates, to_unit='nm'), dtype=float)
    mesh = DelaunayMesh(points=coordinates_nm)
    mesh.keep_alpha_spheres(
        mesh.filter_alpha_spheres(
            min_radius=min_radius_nm,
            max_radius=max_radius_nm,
        )
    )

    alpha_lining_local = mesh.points_of_alpha_sphere
    alpha_lining_atom_indices = atom_indices[alpha_lining_local]
    alpha_centers_nm = mesh.centers
    alpha_radii_nm = mesh.radii
    alpha_space_nm3 = mesh.get_volumes()

    sasa = msm.physchem.get_sasa(receptor, element='atom', engine='mdtraj')
    atom_sasa_nm2 = np.asarray(puw.get_value(sasa, to_unit='nm**2'))[0]
    atom_types = receptor.topology.atoms['atom_type'].to_numpy()
    is_nonpolar = np.array([atom_type not in ['O', 'N', 'S'] for atom_type in atom_types], dtype=float)
    alpha_nonpolar_ratio = (
        (atom_sasa_nm2 * is_nonpolar)[alpha_lining_local].sum(axis=1)
        / (atom_sasa_nm2[alpha_lining_local].sum(axis=1) + 1e-12)
    )

    return (
        coordinates_nm,
        alpha_centers_nm,
        alpha_radii_nm,
        alpha_lining_local,
        alpha_lining_atom_indices,
        alpha_space_nm3,
        alpha_nonpolar_ratio,
    )


def _cluster_pockets(alpha_centers_nm: np.ndarray, alpha_space_nm3: np.ndarray, cluster_cutoff_nm: float):
    if len(alpha_centers_nm) == 0:
        return [], np.zeros((0, 3)), np.zeros(0)

    if len(alpha_centers_nm) == 1:
        pocket_alpha_index_list = [[0]]
    else:
        linkage_matrix = linkage(alpha_centers_nm, method='average')
        labels = fcluster(linkage_matrix, cluster_cutoff_nm, criterion='distance') - 1
        pocket_alpha_index_list = _group_labels(labels)

    pocket_centers_nm = np.array(
        [np.mean(alpha_centers_nm[indices], axis=0) for indices in pocket_alpha_index_list],
        dtype=float,
    )
    pocket_space_nm3 = np.array(
        [np.sum(alpha_space_nm3[indices]) for indices in pocket_alpha_index_list],
        dtype=float,
    )

    return pocket_alpha_index_list, pocket_centers_nm, pocket_space_nm3


def _cluster_betas(
    alpha_centers_nm: np.ndarray,
    alpha_space_nm3: np.ndarray,
    pocket_alpha_index_list: list[list[int]],
    beta_cluster_cutoff_nm: float,
):
    beta_alpha_index_list: list[list[int]] = []
    pocket_beta_index_list: list[list[int]] = []

    for pocket_indices in pocket_alpha_index_list:
        pocket_alpha_centers = alpha_centers_nm[pocket_indices]
        pocket_alpha_indices = np.array(pocket_indices, dtype=int)

        if len(pocket_alpha_indices) == 0:
            pocket_beta_index_list.append([])
            continue

        if len(pocket_alpha_indices) == 1:
            grouped_alpha_indices = [[int(pocket_alpha_indices[0])]]
        else:
            linkage_matrix = linkage(pocket_alpha_centers, method='complete')
            labels = fcluster(linkage_matrix, beta_cluster_cutoff_nm, criterion='distance') - 1
            grouped_local = _group_labels(labels)
            grouped_alpha_indices = [
                [int(pocket_alpha_indices[local_idx]) for local_idx in group]
                for group in grouped_local
            ]

        offset = len(beta_alpha_index_list)
        pocket_beta_index_list.append([offset + index for index in range(len(grouped_alpha_indices))])
        beta_alpha_index_list.extend(grouped_alpha_indices)

    if len(beta_alpha_index_list) == 0:
        return beta_alpha_index_list, pocket_beta_index_list, np.zeros((0, 3)), np.zeros(0), np.zeros(0)

    beta_centers_nm = np.array(
        [np.mean(alpha_centers_nm[indices], axis=0) for indices in beta_alpha_index_list],
        dtype=float,
    )
    beta_space_nm3 = np.array(
        [np.sum(alpha_space_nm3[indices]) for indices in beta_alpha_index_list],
        dtype=float,
    )
    beta_scores = np.zeros(len(beta_alpha_index_list), dtype=float)

    return beta_alpha_index_list, pocket_beta_index_list, beta_centers_nm, beta_space_nm3, beta_scores


def _grid_volume(coord_list: np.ndarray, threshold_nm: float = 0.16, resolution_nm: float = 0.05) -> float:
    if coord_list.size == 0:
        return 0.0
    min_coord = np.min(coord_list, axis=0) - threshold_nm
    max_coord = np.max(coord_list, axis=0) + threshold_nm
    grid_axes = [
        np.arange(start=min_coord[i], stop=max_coord[i] + resolution_nm, step=resolution_nm)
        for i in range(3)
    ]
    mesh = np.array(np.meshgrid(*grid_axes)).transpose().reshape(-1, 3)
    contact = np.linalg.norm(
        mesh[:, None, :] - coord_list[None, :, :], axis=2
    ) < threshold_nm
    contact_voxel = np.any(contact, axis=1)
    return float(np.count_nonzero(contact_voxel) * (resolution_nm ** 3))


def _overlap_matrices(groups: list[list[int]], total_space: int) -> tuple[np.ndarray, np.ndarray]:
    if len(groups) == 0:
        return np.zeros((0, 0), dtype=float), np.zeros((0, 0), dtype=float)
    incidence = np.zeros((len(groups), total_space), dtype=int)
    for idx, indices in enumerate(groups):
        incidence[idx, indices] = 1
    intersection = incidence @ incidence.T
    union = np.zeros_like(intersection)
    for i in range(union.shape[0]):
        for j in range(union.shape[1]):
            union[i, j] = np.count_nonzero(incidence[i] + incidence[j])
    return intersection.astype(float), union.astype(float)


def _connection_matrix(intersection_matrix: np.ndarray) -> np.ndarray:
    if intersection_matrix.size == 0:
        return np.zeros_like(intersection_matrix, dtype=bool)
    return intersection_matrix > 0

def _read_pdbqt_adv_atom_types(pdbqt_file: str) -> np.ndarray:
    adv_atom_types: list[str] = []
    with open(pdbqt_file, 'r', encoding='utf-8') as file_handle:
        for line in file_handle:
            if line.startswith('ATOM'):
                adv_atom_types.append(line[77:79].strip())

    return np.array(adv_atom_types, dtype=object)


def _get_filtered_adv_atom_types(
    receptor,
    keep_local_indices: np.ndarray,
    adv_atom_types: np.ndarray | list[str] | tuple[str, ...] | None = None,
    pdbqt_file: str | None = None,
) -> np.ndarray | None:
    raw_adv_atom_types = adv_atom_types
    if raw_adv_atom_types is None and pdbqt_file is not None:
        raw_adv_atom_types = _read_pdbqt_adv_atom_types(pdbqt_file)

    if raw_adv_atom_types is None:
        return None

    raw_adv_atom_types = np.array(raw_adv_atom_types, dtype=object)
    atom_count = len(msm.get(receptor, element='atom', atom_name=True))

    if len(raw_adv_atom_types) == atom_count:
        return raw_adv_atom_types[keep_local_indices].astype(str)

    if len(raw_adv_atom_types) == len(keep_local_indices):
        return raw_adv_atom_types.astype(str)

    raise ValueError(
        'adv_atom_types must align either with the selected receptor atoms before hydrogen filtering '
        'or with the filtered heavy-atom receptor.'
    )


def _prepare_vina_typing(
    coordinates_a: np.ndarray,
    atom_names: np.ndarray,
    residue_names: np.ndarray,
    elements: np.ndarray,
    adv_atom_types: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    prot_types = np.array([str(value).strip() for value in adv_atom_types], dtype=object)
    hp_type = np.full(len(prot_types), 'UNK', dtype=object)
    don_type = np.full(len(prot_types), 'UNK', dtype=object)
    acc_type = np.full(len(prot_types), 'UNK', dtype=object)

    tree = cKDTree(coordinates_a)

    for index in np.where(hp_type == 'UNK')[0]:
        neighbor_indices = np.array(tree.query_ball_point(coordinates_a[index], 2.0), dtype=int)
        neighbor_indices = neighbor_indices[neighbor_indices != index]
        if prot_types[index] not in POLAR_TYPES:
            hp_type[index] = 'NNP' if np.any(np.isin(prot_types[neighbor_indices], POLAR_TYPES)) else 'NP'
        else:
            hp_type[index] = 'XXX'

    for index in np.where(don_type == 'UNK')[0]:
        neighbor_indices = np.array(tree.query_ball_point(coordinates_a[index], 2.0), dtype=int)
        neighbor_indices = neighbor_indices[neighbor_indices != index]
        if prot_types[index] in {'N', 'NS', 'NA'}:
            don_type[index] = 'NPP' if len(neighbor_indices) > 2 else 'P'
        else:
            don_type[index] = 'XXX'

    for index in np.where(acc_type == 'UNK')[0]:
        if prot_types[index] in {'OA', 'OS', 'SA', 'S'}:
            acc_type[index] = 'P'
        else:
            acc_type[index] = 'XXX'

    return prot_types, hp_type, acc_type, don_type


def _get_probe_scores(
    prot_coord_a: np.ndarray,
    prot_types: np.ndarray,
    hp_type: np.ndarray,
    don_type: np.ndarray,
    acc_type: np.ndarray,
    probe_coords_a: np.ndarray,
) -> np.ndarray:
    _, _, autodock_types_dict, vina_terms = _load_vina_scoring_data()

    def _nonpolar_interp(distance: float) -> float:
        if distance < 0.5:
            return 1.0
        if distance > 1.5:
            return 0.0
        return 1.5 - distance

    def _polar_interp(distance: float) -> float:
        if distance < -0.7:
            return 1.0
        if distance >= 0.0:
            return 0.0
        return -distance / 0.7

    probe_prot_dist = cdist(probe_coords_a, prot_coord_a)
    probe_scores = np.zeros((probe_coords_a.shape[0], len(PROBE_ELEMENTS)), dtype=np.float32)

    for probe_index in range(probe_coords_a.shape[0]):
        distance_mask = probe_prot_dist[probe_index] <= 8.0
        temp_dist = probe_prot_dist[probe_index][distance_mask]
        temp_type = prot_types[distance_mask]
        np_type = hp_type[distance_mask] == 'NP'
        polar_donor_type = don_type[distance_mask] == 'P'
        polar_acceptor_type = acc_type[distance_mask] == 'P'
        dist_radii = np.array([autodock_types_dict[str(atom_type)][0] for atom_type in temp_type], dtype=float)

        for element_index, probe_element in enumerate(PROBE_ELEMENTS):
            probe_dist = autodock_types_dict[str(probe_element)][0]
            processed_dist = temp_dist - dist_radii - probe_dist
            gauss1 = float(np.sum(np.exp(-(processed_dist / 0.5) ** 2)))
            gauss2 = float(np.sum(np.exp(-((processed_dist - 3.0) / 2.0) ** 2)))
            repulsion = float(np.sum([distance**2 if distance < 0.0 else 0.0 for distance in processed_dist]))

            if probe_element in {'C', 'Br', 'Cl', 'F', 'I'}:
                hydrophobic = float(np.sum([_nonpolar_interp(distance) for distance in processed_dist[np_type]]))
                hydrogen = 0.0
            elif probe_element in {'OA', 'SA'}:
                hydrophobic = 0.0
                hydrogen = float(
                    np.sum([_polar_interp(distance) for distance in processed_dist[polar_donor_type]])
                )
            elif probe_element in {'N', 'P'}:
                hydrophobic = 0.0
                hydrogen = float(
                    np.sum([_polar_interp(distance) for distance in processed_dist[polar_acceptor_type]])
                )
            else:
                raise ValueError(f'Unsupported probe element {probe_element!r}.')

            terms = np.array([gauss1, gauss2, repulsion, hydrophobic, hydrogen], dtype=np.float32)
            probe_scores[probe_index][element_index] = float(np.sum(terms * vina_terms))

    return probe_scores


def _compute_beta_scores(
    receptor,
    keep_local_indices: np.ndarray,
    coordinates_nm: np.ndarray,
    beta_centers_nm: np.ndarray,
    adv_atom_types: np.ndarray | list[str] | tuple[str, ...] | None = None,
    pdbqt_file: str | None = None,
) -> np.ndarray:
    if len(beta_centers_nm) == 0:
        return np.zeros(0, dtype=float)

    filtered_adv_atom_types = _get_filtered_adv_atom_types(
        receptor=receptor,
        keep_local_indices=keep_local_indices,
        adv_atom_types=adv_atom_types,
        pdbqt_file=pdbqt_file,
    )
    if filtered_adv_atom_types is None:
        return np.zeros(len(beta_centers_nm), dtype=float)

    atom_names = np.array(msm.get(receptor, element='atom', atom_name=True), dtype=object)[keep_local_indices]
    residue_names = np.array(msm.get(receptor, element='atom', group_name=True), dtype=object)[keep_local_indices]
    raw_atom_types = np.array(msm.get(receptor, element='atom', atom_type=True), dtype=object)[keep_local_indices]
    elements = np.array(
        [_get_atom_element(atom_type, atom_name) for atom_type, atom_name in zip(raw_atom_types, atom_names)],
        dtype=object,
    )

    prot_types, hp_type, acc_type, don_type = _prepare_vina_typing(
        coordinates_a=coordinates_nm * 10.0,
        atom_names=atom_names,
        residue_names=residue_names,
        elements=elements,
        adv_atom_types=filtered_adv_atom_types,
    )

    return _get_probe_scores(
        prot_coord_a=coordinates_nm * 10.0,
        prot_types=prot_types,
        hp_type=hp_type,
        don_type=don_type,
        acc_type=acc_type,
        probe_coords_a=beta_centers_nm * 10.0,
    )


def _get_beta_scalar_scores(beta_scores: np.ndarray) -> np.ndarray:
    beta_scores = np.asarray(beta_scores)

    if beta_scores.ndim == 2:
        return np.min(beta_scores, axis=1)

    return beta_scores.astype(float)


def _contact_matrix(alpha_centers_nm: np.ndarray, binder_coords_nm: np.ndarray | None, cutoff_nm: float) -> np.ndarray:
    if binder_coords_nm is None or len(binder_coords_nm) == 0:
        return np.zeros((len(alpha_centers_nm), 0), dtype=bool)
    dist = cdist(alpha_centers_nm, binder_coords_nm)
    return dist <= cutoff_nm


def _compute_contact_masks(
    alpha_centers_nm: np.ndarray,
    beta_alpha_index_list: list[list[int]],
    pocket_alpha_index_list: list[list[int]],
    binder_coords_nm: np.ndarray | None,
    cutoff_nm: float = 0.16,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if binder_coords_nm is None or len(binder_coords_nm) == 0:
        alpha_contact = np.zeros(len(alpha_centers_nm), dtype=bool)
    else:
        binder_coords_nm = np.asarray(binder_coords_nm, dtype=float)
        binder_tree = cKDTree(binder_coords_nm)
        alpha_contact = np.array(
            [len(binder_tree.query_ball_point(center, r=cutoff_nm)) > 0 for center in alpha_centers_nm],
            dtype=bool,
        )

    beta_contact = np.array(
        [np.any(alpha_contact[alpha_indices]) for alpha_indices in beta_alpha_index_list],
        dtype=bool,
    )
    pocket_contact = np.array(
        [np.any(alpha_contact[alpha_indices]) for alpha_indices in pocket_alpha_index_list],
        dtype=bool,
    )

    contact_matrix = _contact_matrix(alpha_centers_nm, binder_coords_nm, cutoff_nm)
    return alpha_contact, beta_contact, pocket_contact, contact_matrix


def _build_state(
    molecular_system,
    selection: str,
    structure_indices: int,
    min_radius_nm: float,
    max_radius_nm: float,
    cluster_cutoff_nm: float,
    beta_cluster_cutoff_nm: float,
    syntax: str,
    adv_atom_types: np.ndarray | list[str] | tuple[str, ...] | None = None,
    pdbqt_file: str | None = None,
) -> AlphaSpace2State:
    receptor, atom_indices, keep_local_indices = _prepare_receptor(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )

    (
        coordinates_nm,
        alpha_centers_nm,
        alpha_radii_nm,
        alpha_lining_local_indices,
        alpha_lining_atom_indices,
        alpha_space_nm3,
        alpha_nonpolar_ratio,
    ) = _compute_alpha_layer(
        receptor=receptor,
        atom_indices=atom_indices,
        structure_indices=structure_indices,
        min_radius_nm=min_radius_nm,
        max_radius_nm=max_radius_nm,
    )

    pocket_alpha_index_list, pocket_centers_nm, pocket_space_nm3 = _cluster_pockets(
        alpha_centers_nm=alpha_centers_nm,
        alpha_space_nm3=alpha_space_nm3,
        cluster_cutoff_nm=cluster_cutoff_nm,
    )
    (
        beta_alpha_index_list,
        pocket_beta_index_list,
        beta_centers_nm,
        beta_space_nm3,
        _beta_scores,
    ) = _cluster_betas(
        alpha_centers_nm=alpha_centers_nm,
        alpha_space_nm3=alpha_space_nm3,
        pocket_alpha_index_list=pocket_alpha_index_list,
        beta_cluster_cutoff_nm=beta_cluster_cutoff_nm,
    )
    beta_scores = _compute_beta_scores(
        receptor=receptor,
        keep_local_indices=keep_local_indices,
        coordinates_nm=coordinates_nm,
        beta_centers_nm=beta_centers_nm,
        adv_atom_types=adv_atom_types,
        pdbqt_file=pdbqt_file,
    )

    pocket_grid_volume_nm3 = np.array(
        [_grid_volume(alpha_centers_nm[indices]) for indices in pocket_alpha_index_list],
        dtype=float,
    )
    pocket_overlap_intersection, pocket_overlap_union = _overlap_matrices(
        pocket_alpha_index_list,
        total_space=len(alpha_centers_nm),
    )
    pocket_connection_matrix = _connection_matrix(pocket_overlap_intersection)

    beta_overlap_intersection, beta_overlap_union = _overlap_matrices(
        beta_alpha_index_list,
        total_space=len(alpha_centers_nm),
    )

    return AlphaSpace2State(
        atom_indices=atom_indices,
        coordinates_nm=coordinates_nm,
        alpha_centers_nm=alpha_centers_nm,
        alpha_radii_nm=alpha_radii_nm,
        alpha_lining_local_indices=alpha_lining_local_indices,
        alpha_lining_atom_indices=alpha_lining_atom_indices,
        alpha_space_nm3=alpha_space_nm3,
        alpha_nonpolar_ratio=alpha_nonpolar_ratio,
        pocket_alpha_index_list=pocket_alpha_index_list,
        pocket_centers_nm=pocket_centers_nm,
        pocket_space_nm3=pocket_space_nm3,
        beta_alpha_index_list=beta_alpha_index_list,
        pocket_beta_index_list=pocket_beta_index_list,
        beta_centers_nm=beta_centers_nm,
        beta_space_nm3=beta_space_nm3,
        beta_scores=beta_scores,
        alpha_contact=np.zeros(len(alpha_centers_nm), dtype=bool),
        beta_contact=np.zeros(len(beta_alpha_index_list), dtype=bool),
        pocket_contact=np.zeros(len(pocket_alpha_index_list), dtype=bool),
        alpha_contact_matrix=np.zeros((len(alpha_centers_nm), 0), dtype=bool),
        pocket_grid_volume_nm3=pocket_grid_volume_nm3,
        pocket_overlap_intersection=pocket_overlap_intersection,
        pocket_overlap_union=pocket_overlap_union,
        pocket_connection_matrix=pocket_connection_matrix,
        beta_overlap_intersection=beta_overlap_intersection,
        beta_overlap_union=beta_overlap_union,
    )


def _state_to_pocket_records(state: AlphaSpace2State) -> list[dict[str, object]]:
    pocket_records: list[dict[str, object]] = []
    beta_scalar_scores = _get_beta_scalar_scores(state.beta_scores)

    for pocket_index, alpha_indices in enumerate(state.pocket_alpha_index_list):
        lining_atom_indices = np.unique(state.alpha_lining_atom_indices[alpha_indices].reshape(-1))
        beta_indices = state.pocket_beta_index_list[pocket_index]
        pocket_score = float(np.sum(beta_scalar_scores[beta_indices])) if beta_indices else 0.0

        pocket_records.append(
            {
                'pocket_index': pocket_index,
                'atom_indices': lining_atom_indices.astype(int).tolist(),
                'center': state.pocket_centers_nm[pocket_index],
                'volume': float(state.pocket_space_nm3[pocket_index]),
                'score': pocket_score,
                'nonpolar_volume': float(
                    np.sum(
                        state.alpha_space_nm3[alpha_indices]
                        * state.alpha_nonpolar_ratio[alpha_indices]
                    )
                ),
                'alpha_sphere_centers': state.alpha_centers_nm[alpha_indices],
                'alpha_sphere_radii': state.alpha_radii_nm[alpha_indices],
                'beta_centers': state.beta_centers_nm[beta_indices] if beta_indices else np.zeros((0, 3)),
                'beta_scores': beta_scalar_scores[beta_indices] if beta_indices else np.zeros(0),
                'beta_probe_scores': state.beta_scores[beta_indices] if beta_indices else np.zeros((0, 9)),
                'is_contact': bool(state.pocket_contact[pocket_index]),
                'grid_volume_nm3': float(state.pocket_grid_volume_nm3[pocket_index]),
                'overlap_intersection_counts': state.pocket_overlap_intersection[pocket_index].copy(),
                'overlap_union_counts': state.pocket_overlap_union[pocket_index].copy(),
            }
        )

    return pocket_records


@signal(tags=['method', 'alphaspace2', 'native'])
def alphaspace2(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    min_radius: float = 0.32,
    max_radius: float = 0.54,
    cluster_cutoff: float = 0.47,
    beta_cluster_cutoff: float = 0.16,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
    return_atom_indices: bool = False,
    return_state: bool = False,
    return_pocket_records: bool = False,
    binder_coords=None,
    adv_atom_types: np.ndarray | list[str] | tuple[str, ...] | None = None,
    pdbqt_file: str | None = None,
):
    """Detect pockets with the native AlphaSpace2 reimplementation."""

    if puw.is_quantity(min_radius):
        min_radius_nm = float(puw.get_value(min_radius, to_unit='nm'))
    else:
        min_radius_nm = float(min_radius)

    if puw.is_quantity(max_radius):
        max_radius_nm = float(puw.get_value(max_radius, to_unit='nm'))
    else:
        max_radius_nm = float(max_radius)

    if puw.is_quantity(cluster_cutoff):
        cluster_cutoff_nm = float(puw.get_value(cluster_cutoff, to_unit='nm'))
    else:
        cluster_cutoff_nm = float(cluster_cutoff)

    if puw.is_quantity(beta_cluster_cutoff):
        beta_cluster_cutoff_nm = float(puw.get_value(beta_cluster_cutoff, to_unit='nm'))
    else:
        beta_cluster_cutoff_nm = float(beta_cluster_cutoff)

    binder_coords = digest_binder_coords(
        binder_coords,
        caller='topomt.third_party.alphaspace2.native.alphaspace2',
    )
    binder_coords_nm = None
    if binder_coords is not None:
        if puw.is_quantity(binder_coords):
            binder_coords_nm = np.asarray(puw.get_value(binder_coords, to_unit='nm'), dtype=float)
        else:
            binder_coords_nm = np.asarray(binder_coords, dtype=float)

    state = _build_state(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        min_radius_nm=min_radius_nm,
        max_radius_nm=max_radius_nm,
        cluster_cutoff_nm=cluster_cutoff_nm,
        beta_cluster_cutoff_nm=beta_cluster_cutoff_nm,
        syntax=syntax,
        adv_atom_types=adv_atom_types,
        pdbqt_file=pdbqt_file,
    )
    state.alpha_contact, state.beta_contact, state.pocket_contact, state.alpha_contact_matrix = _compute_contact_masks(
        alpha_centers_nm=state.alpha_centers_nm,
        beta_alpha_index_list=state.beta_alpha_index_list,
        pocket_alpha_index_list=state.pocket_alpha_index_list,
        binder_coords_nm=binder_coords_nm,
        cutoff_nm=0.16,
    )

    if return_pocket_records:
        pocket_records = _state_to_pocket_records(state)
        outputs: list[object] = [pocket_records]
        if return_atom_indices:
            outputs.append(state.atom_indices.tolist())
        if return_state:
            outputs.append(state)
        if len(outputs) == 1:
            return outputs[0]
        return tuple(outputs)

    clusters = [list(indices) for indices in state.pocket_alpha_index_list]
    contacts = state.alpha_contact

    if return_atom_indices:
        outputs = [clusters, state.alpha_centers_nm, state.alpha_radii_nm, contacts, state.atom_indices.tolist()]
        if return_state:
            outputs.append(state)
        return tuple(outputs)

    if return_state:
        return clusters, state.alpha_centers_nm, state.alpha_radii_nm, contacts, state

    return clusters, state.alpha_centers_nm, state.alpha_radii_nm, contacts


def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    min_vertices: int = 20,
    **kwargs,
) -> Topography:
    """Run the local AlphaSpace2 implementation and return a Topography."""

    topography = Topography(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
    )

    result = alphaspace2(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        return_atom_indices=True,
        return_state=True,
        **kwargs,
    )

    if len(result) == 6:
        clusters, vertices, radii, contacts, atom_indices, state = result
    else:
        clusters, vertices, radii, contacts, atom_indices = result
        state = None

    if state is not None:
        pocket_records = _state_to_pocket_records(state)
        for pocket_record in pocket_records:
            if len(pocket_record['alpha_sphere_centers']) < min_vertices:
                continue

            topography.add_feature(
                Pocket(
                    atom_indices=pocket_record['atom_indices'],
                    center=puw.quantity(pocket_record['center'], 'nm'),
                    volume=puw.quantity(pocket_record['volume'], 'nm**3'),
                    score=pocket_record['score'],
                    source='alphaspace2',
                    source_id=f"alphaspace2:{pocket_record['pocket_index']}",
                    alpha_sphere_centers=puw.quantity(
                        pocket_record['alpha_sphere_centers'],
                        'nm',
                    ),
                    alpha_sphere_radii=puw.quantity(
                        pocket_record['alpha_sphere_radii'],
                        'nm',
                    ),
                    beta_centers=puw.quantity(pocket_record['beta_centers'], 'nm'),
                    beta_scores=pocket_record['beta_scores'],
                    nonpolar_volume=puw.quantity(
                        pocket_record['nonpolar_volume'],
                        'nm**3',
                    ),
                    is_contact=pocket_record['is_contact'],
                )
            )

        return topography

    atom_coords = msm.get(molecular_system, selection=atom_indices, coordinates=True)[0]
    atom_coords = puw.get_value(atom_coords, to_unit='nm')
    tree = cKDTree(atom_coords)

    for index, cluster in enumerate(clusters):
        if len(cluster) < min_vertices:
            continue

        cluster_vertices = vertices[cluster]
        cluster_radii = radii[cluster]
        centroid = np.mean(cluster_vertices, axis=0) if len(cluster_vertices) > 0 else None

        involved_atoms = set()
        for vertex, radius in zip(cluster_vertices, cluster_radii):
            near_atoms = tree.query_ball_point(vertex, radius + 0.02)
            involved_atoms.update(atom_indices[atom_index] for atom_index in near_atoms)

        if not involved_atoms:
            continue

        topography.add_feature(
            Pocket(
                atom_indices=sorted(involved_atoms),
                center=centroid,
                source='alphaspace2',
                source_id=f'alphaspace2:{index}',
            )
        )

    return topography
