from dataclasses import dataclass
from pathlib import Path
from typing import Any

import molsysmt as msm
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial import ConvexHull

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt._private.arg_digestion import arg_digest
from topomt._private.smonitor import signal
from topomt.delaunay_mesh import DelaunayMesh
from topomt.features import Pocket
from topomt.wrappers.fpocket.integration import get_topography_with_fpocket


ASPH_MIN_SIZE_NM = 0.34
ASPH_MAX_SIZE_NM = 0.62
CLUST_MAX_DIST_NM = 0.24
MIN_POCKET_ALPHA_SPHERES = 15
MIN_APOLAR_NEIGHBORS = 3
PRECISION_TOLERANCE_NM = 1.0e-4
MAX_BARYCENTER_DISTANCE_NM = 0.10
LARGE_ALPHA_RADIUS_NM = ASPH_MAX_SIZE_NM - 0.15

ELECTRONEGATIVITY_BY_ATOM_TYPE = {
    'H': 2.20,
    'B': 2.04,
    'C': 2.55,
    'N': 3.04,
    'O': 3.44,
    'F': 3.98,
    'P': 2.19,
    'S': 2.58,
    'CL': 3.16,
    'SE': 2.55,
    'BR': 2.96,
    'I': 2.66,
}

WATER_GROUP_NAMES = {'HOH', 'WAT', 'TIP'}
UPSTREAM_KEEP_HETATM_GROUP_NAMES = frozenset(
    Path(__file__).resolve().parents[1]
    .joinpath('data', 'fpocket4', 'upstream_keep_hetatm.txt')
    .read_text()
    .splitlines()
)
CANONICAL_POLYMER_GROUP_NAMES = frozenset(
    {
        'ALA', 'ARG', 'ASN', 'ASP', 'ASX', 'CYS', 'GLN', 'GLU', 'GLX', 'GLY',
        'HIS', 'HID', 'HIE', 'HIP', 'ILE', 'LEU', 'LYS', 'MET', 'PHE', 'PRO',
        'PYL', 'SEC', 'SER', 'THR', 'TRP', 'TYR', 'VAL',
        'A', 'C', 'G', 'U', 'I',
        'DA', 'DC', 'DG', 'DT', 'DI',
        'ADE', 'CYT', 'GUA', 'URI',
    }
)


@dataclass
class Fpocket4NativeState:
    atom_indices: np.ndarray
    coordinates_nm: np.ndarray
    atom_types: np.ndarray
    atom_radii_nm: np.ndarray
    atom_electronegativities: np.ndarray
    atom_b_factors: np.ndarray | None
    descriptor_occluder_coordinates_nm: np.ndarray
    descriptor_occluder_radii_nm: np.ndarray
    alpha_spheres: DelaunayMesh
    alpha_is_apolar: np.ndarray
    alpha_local_hydrophobic_density: np.ndarray
    pocket_alpha_index_list: list[list[int]]
    pocket_centers_nm: np.ndarray
    pocket_atom_index_list: list[list[int]]


@dataclass
class Fpocket4NativePocketDescriptor:
    alpha_indices: list[int]
    atom_indices: list[int]
    center_nm: np.ndarray
    n_alpha_spheres: int
    mean_alpha_sphere_radius_nm: float
    volume_nm3: float
    convex_hull_volume_nm3: float
    n_apolar_alpha_spheres: int
    apolar_alpha_sphere_ratio: float
    local_hydrophobic_density: float
    as_density_angstrom: float
    as_max_dst_angstrom: float
    score: float
    surf_pol_vdw14_angstrom2: float = 0.0
    surf_apol_vdw14_angstrom2: float = 0.0
    surf_pol_vdw22_angstrom2: float = 0.0
    surf_apol_vdw22_angstrom2: float = 0.0
    n_abpa: int = 0
    nas_norm: float = 0.0
    mean_loc_hyd_dens_norm: float = 0.0
    as_density_norm: float = 0.0
    as_max_dst_norm: float = 0.0
    druggability_score: float | None = None


def _get_upstream_like_bfactor_statistics(
    molecular_system,
    selection: str = 'all',
    syntax: str = 'MolSysMT',
    keep_water: bool = False,
    keep_ions: bool = False,
    keep_small_molecules: bool = False,
    include_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
    exclude_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
) -> tuple[float, float, float] | None:
    full_molsys, receptor, selected_atom_indices, _ = _build_selected_receptor(
        molecular_system=molecular_system,
        selection=selection,
        syntax=syntax,
    )
    keep_local_indices = _get_fpocket_native_keep_local_indices(
        receptor,
        drop_hydrogens=False,
        keep_water=keep_water,
        keep_ions=keep_ions,
        keep_small_molecules=keep_small_molecules,
        include_group_names=include_group_names,
        exclude_group_names=exclude_group_names,
    )
    if len(keep_local_indices) == 0:
        return None

    selected_b_factors = _get_selected_b_factors(full_molsys, selected_atom_indices)
    if selected_b_factors is None:
        return None

    kept_b_factors = selected_b_factors[np.asarray(keep_local_indices, dtype=int)]
    if kept_b_factors.size == 0:
        return None

    metadata = _get_receptor_atom_metadata(receptor)
    kept_atom_types = metadata['atom_types'][np.asarray(keep_local_indices, dtype=int)]
    heavy_atom_count = int(np.sum(np.char.upper(kept_atom_types.astype(str)) != 'H'))
    if heavy_atom_count <= 0:
        return None

    average_b_factor = 0.0
    min_b_factor = 0.0
    max_b_factor = 0.0
    for b_factor in kept_b_factors:
        b_factor_value = float(b_factor)
        average_b_factor += b_factor_value
        if b_factor_value < min_b_factor:
            min_b_factor = b_factor_value
        if b_factor_value > max_b_factor:
            max_b_factor = b_factor_value
    average_b_factor /= heavy_atom_count

    return average_b_factor, min_b_factor, max_b_factor


def _group_labels(labels: np.ndarray) -> list[list[int]]:
    groups = [[] for _ in range(int(np.max(labels)) + 1)]
    for index, label in enumerate(labels):
        groups[int(label)].append(index)
    return groups


def _normalize_structure_indices(structure_indices):
    if isinstance(structure_indices, np.ndarray):
        if structure_indices.ndim == 1 and structure_indices.size == 1:
            return int(structure_indices[0])
        return structure_indices.tolist()
    return structure_indices


def _build_selected_receptor(
    molecular_system,
    selection: str,
    syntax: str,
):
    full_molsys = msm.convert(
        molecular_system,
        to_form='molsysmt.MolSys',
    )
    selected_atom_indices = np.array(
        msm.select(full_molsys, selection=selection, syntax=syntax),
        dtype=int,
    )
    receptor = msm.convert(
        full_molsys,
        to_form='molsysmt.MolSys',
        selection=selected_atom_indices,
        syntax='MolSysMT',
    )
    selected_b_factors = _get_selected_b_factors(full_molsys, selected_atom_indices)
    return full_molsys, receptor, selected_atom_indices, selected_b_factors


def _get_receptor_atom_metadata(receptor) -> dict[str, np.ndarray]:
    raw_atom_types = np.array(
        msm.get(receptor, element='atom', atom_type=True),
        dtype=object,
    )
    atom_names = np.array(
        msm.get(receptor, element='atom', atom_name=True),
        dtype=object,
    )
    molecule_types = np.char.lower(
        np.array(
            msm.get(receptor, element='atom', molecule_type=True),
            dtype=object,
        ).astype(str)
    )
    group_names = np.char.upper(
        np.array(
            msm.get(receptor, element='atom', group_name=True),
            dtype=object,
        ).astype(str)
    )
    atom_types = np.char.upper(
        np.array(
            [
                _get_atom_element(atom_type, atom_name)
                for atom_type, atom_name in zip(raw_atom_types, atom_names)
            ],
            dtype=object,
        ).astype(str)
    )

    return {
        'raw_atom_types': raw_atom_types,
        'atom_names': atom_names,
        'atom_types': atom_types,
        'molecule_types': molecule_types,
        'group_names': group_names,
    }


def _prepare_receptor(
    molecular_system,
    selection: str,
    structure_indices: int | list[int],
    syntax: str,
    keep_water: bool = False,
    keep_ions: bool = False,
    keep_small_molecules: bool = False,
    include_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
    exclude_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
) -> tuple[object, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray | None]:
    _, receptor, selected_atom_indices, selected_b_factors = _build_selected_receptor(
        molecular_system=molecular_system,
        selection=selection,
        syntax=syntax,
    )

    keep_local_indices = _get_fpocket_native_keep_local_indices(
        receptor,
        drop_hydrogens=True,
        keep_water=keep_water,
        keep_ions=keep_ions,
        keep_small_molecules=keep_small_molecules,
        include_group_names=include_group_names,
        exclude_group_names=exclude_group_names,
    )

    filtered_receptor = msm.convert(
        receptor,
        to_form='molsysmt.MolSys',
        selection=keep_local_indices,
        syntax='MolSysMT',
    )
    filtered_atom_indices = selected_atom_indices[np.array(keep_local_indices, dtype=int)]
    coordinates = msm.get(
        molecular_system=filtered_receptor,
        coordinates=True,
        structure_indices=0 if structure_indices == 0 else structure_indices,
    )[0]
    coordinates_nm = np.asarray(puw.get_value(coordinates, to_unit='nm'))
    metadata = _get_receptor_atom_metadata(filtered_receptor)
    atom_types = metadata['atom_types']
    atom_radii_nm = _get_atomic_radii_nm(filtered_receptor, atom_types)
    atom_electronegativities = np.array(
        [_get_atom_electronegativity(atom_type) for atom_type in atom_types],
        dtype=float,
    )
    atom_b_factors = None
    if selected_b_factors is not None:
        atom_b_factors = selected_b_factors[np.array(keep_local_indices, dtype=int)]

    return (
        filtered_receptor,
        filtered_atom_indices,
        coordinates_nm,
        atom_types,
        atom_radii_nm,
        atom_electronegativities,
        atom_b_factors,
    )


def _get_fpocket_native_keep_local_indices(
    receptor,
    drop_hydrogens: bool = True,
    keep_water: bool = False,
    keep_ions: bool = False,
    keep_small_molecules: bool = False,
    include_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
    exclude_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
) -> np.ndarray:
    metadata = _get_receptor_atom_metadata(receptor)
    atom_types = metadata['atom_types']
    atom_names = metadata['atom_names']
    molecule_types = metadata['molecule_types']
    group_names = metadata['group_names']

    include_group_name_set = {
        str(group_name).strip().upper() for group_name in (include_group_names or [])
    }
    exclude_group_name_set = {
        str(group_name).strip().upper() for group_name in (exclude_group_names or [])
    }

    keep_mask = np.ones(len(atom_types), dtype=bool)
    keep_mask &= ~np.isin(group_names, list(exclude_group_name_set))

    for index, (atom_type, atom_name, group_name, molecule_type) in enumerate(
        zip(atom_types, atom_names, group_names, molecule_types)
    ):
        if not keep_mask[index]:
            continue

        if drop_hydrogens:
            if _is_excluded_as_hydrogen_for_fpocket(
                atom_type=atom_type,
                atom_name=atom_name,
                group_name=group_name,
            ):
                keep_mask[index] = False
                continue

        if group_name in include_group_name_set:
            continue

        if group_name in WATER_GROUP_NAMES:
            keep_mask[index] = keep_water
            continue

        if group_name in UPSTREAM_KEEP_HETATM_GROUP_NAMES:
            continue

        if group_name in CANONICAL_POLYMER_GROUP_NAMES:
            continue

        if molecule_type == 'water':
            keep_mask[index] = keep_water
            continue

        if molecule_type == 'ion':
            keep_mask[index] = keep_ions
            continue

        if molecule_type == 'small molecule':
            keep_mask[index] = keep_small_molecules
            continue

        keep_mask[index] = False

    return np.where(keep_mask)[0].astype(int)


def _is_excluded_as_hydrogen_for_fpocket(
    atom_type: str,
    atom_name,
    group_name: str,
) -> bool:
    normalized_atom_type = str(atom_type).strip().upper()
    if normalized_atom_type != 'H':
        return False

    if group_name in CANONICAL_POLYMER_GROUP_NAMES:
        return True

    if group_name not in UPSTREAM_KEEP_HETATM_GROUP_NAMES:
        return True

    if atom_name is None:
        return True

    normalized_name = str(atom_name).strip().upper()
    if not normalized_name:
        return True

    first_alpha_index = next(
        (index for index, char in enumerate(normalized_name) if char.isalpha()),
        None,
    )
    if first_alpha_index is not None:
        normalized_name = normalized_name[first_alpha_index:]
    else:
        normalized_name = ''

    if len(normalized_name) >= 2 and normalized_name[1].isalpha():
        return False

    return True


def _get_fpocket_descriptor_occluder_local_indices(receptor) -> np.ndarray:
    metadata = _get_receptor_atom_metadata(receptor)
    atom_types = metadata['atom_types']
    molecule_types = metadata['molecule_types']
    group_names = metadata['group_names']

    keep_mask = atom_types != 'H'
    keep_mask &= ~np.isin(group_names, list(WATER_GROUP_NAMES))
    keep_mask &= molecule_types != 'water'

    return np.where(keep_mask)[0].astype(int)


def _get_atom_element(atom_type, atom_name) -> str:
    if atom_type is not None and str(atom_type).strip() not in {'', 'None'}:
        normalized = str(atom_type).strip().upper()
        return normalized

    if atom_name is None:
        return 'X'

    stripped_name = str(atom_name).strip().upper()
    first_alpha_index = next(
        (index for index, char in enumerate(stripped_name) if char.isalpha()),
        None,
    )
    if first_alpha_index is not None:
        stripped_name = stripped_name[first_alpha_index:]
    else:
        stripped_name = ''

    name = ''.join(char for char in stripped_name if char.isalpha())
    if not name:
        return 'X'

    if name.startswith('H'):
        return 'H'

    return name[0]


def _get_atom_electronegativity(atom_type: str) -> float:
    if atom_type is None:
        return 3.5

    normalized = str(atom_type).strip().upper()
    return ELECTRONEGATIVITY_BY_ATOM_TYPE.get(normalized, 3.5)


def _get_atomic_radii_nm(receptor, atom_types: np.ndarray) -> np.ndarray:
    try:
        radii = msm.physchem.get_atomic_radius(
            receptor,
            element='atom',
            selection='all',
            definition='vdw',
            syntax='MolSysMT',
        )
        return np.asarray(puw.get_value(radii, to_unit='nm'), dtype=float)
    except Exception:
        from molsysmt.physchem.atoms.radius import vdw as vdw_radii

        fallback = []
        for atom_type in atom_types:
            key = str(atom_type).capitalize()
            radius_angstrom = vdw_radii.get(key, vdw_radii['C'])
            fallback.append(float(radius_angstrom) / 10.0)
        return np.asarray(fallback, dtype=float)


def _get_selected_b_factors(molecular_system, atom_indices: np.ndarray) -> np.ndarray | None:
    b_factors = msm.get(molecular_system, b_factor=True)
    if b_factors is None:
        return None

    b_factors_value = np.asarray(puw.get_value(b_factors), dtype=float)
    if b_factors_value.ndim == 2:
        if b_factors_value.shape[0] == 0:
            return None
        return b_factors_value[0, atom_indices]
    if b_factors_value.ndim == 1:
        return b_factors_value[atom_indices]

    return None


def _build_native_state(
    molecular_system,
    selection: str,
    structure_indices: int | list[int],
    syntax: str,
    keep_water: bool = False,
    keep_ions: bool = False,
    keep_small_molecules: bool = False,
    include_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
    exclude_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
    implementation: str = 'native',
) -> Fpocket4NativeState:
    receptor, atom_indices, coordinates_nm, atom_types, atom_radii_nm, atom_electronegativities, atom_b_factors = _prepare_receptor(
        # Returned data is already filtered to the heavy-atom receptor seen by
        # the native fpocket pipeline.
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        keep_water=keep_water,
        keep_ions=keep_ions,
        keep_small_molecules=keep_small_molecules,
        include_group_names=include_group_names,
        exclude_group_names=exclude_group_names,
    )
    descriptor_source = msm.convert(
        molecular_system,
        to_form='molsysmt.MolSys',
        selection=selection,
        syntax=syntax,
    )
    descriptor_keep_local_indices = _get_fpocket_descriptor_occluder_local_indices(
        descriptor_source
    )
    descriptor_occluder = msm.convert(
        descriptor_source,
        to_form='molsysmt.MolSys',
        selection=descriptor_keep_local_indices,
        syntax='MolSysMT',
    )
    descriptor_coordinates = msm.get(
        molecular_system=descriptor_occluder,
        coordinates=True,
        structure_indices=0 if structure_indices == 0 else structure_indices,
    )[0]
    descriptor_occluder_coordinates_nm = np.asarray(
        puw.get_value(descriptor_coordinates, to_unit='nm'),
        dtype=float,
    )
    descriptor_raw_atom_types = np.array(
        msm.get(descriptor_occluder, element='atom', atom_type=True),
        dtype=object,
    )
    descriptor_atom_names = np.array(
        msm.get(descriptor_occluder, element='atom', atom_name=True),
        dtype=object,
    )
    descriptor_atom_types = np.array(
        [
            _get_atom_element(atom_type, atom_name)
            for atom_type, atom_name in zip(descriptor_raw_atom_types, descriptor_atom_names)
        ],
        dtype=object,
    )
    descriptor_occluder_radii_nm = _get_atomic_radii_nm(
        descriptor_occluder,
        descriptor_atom_types,
    )

    alpha_spheres = DelaunayMesh(points=coordinates_nm)
    if implementation == 'native':
        min_alpha_radius_nm = ASPH_MIN_SIZE_NM - PRECISION_TOLERANCE_NM
        max_alpha_radius_nm = ASPH_MAX_SIZE_NM + PRECISION_TOLERANCE_NM
        upstream_bfactor_statistics = _get_upstream_like_bfactor_statistics(
            molecular_system,
            selection=selection,
            syntax=syntax,
            keep_water=keep_water,
            keep_ions=keep_ions,
            keep_small_molecules=keep_small_molecules,
            include_group_names=include_group_names,
            exclude_group_names=exclude_group_names,
        )
    else:
        min_alpha_radius_nm = ASPH_MIN_SIZE_NM
        max_alpha_radius_nm = ASPH_MAX_SIZE_NM
        upstream_bfactor_statistics = None

    alpha_spheres.keep_alpha_spheres(
        alpha_spheres.filter_alpha_spheres(
            min_radius=min_alpha_radius_nm,
            max_radius=max_alpha_radius_nm,
        )
    )
    _apply_fpocket_candidate_filter(
        alpha_spheres=alpha_spheres,
        coordinates_nm=coordinates_nm,
        atom_b_factors=atom_b_factors,
        upstream_bfactor_statistics=upstream_bfactor_statistics,
    )

    alpha_is_apolar = _classify_apolar_alpha_spheres(alpha_spheres, atom_electronegativities)
    alpha_local_hydrophobic_density = _compute_local_hydrophobic_density(
        alpha_spheres=alpha_spheres,
        alpha_is_apolar=alpha_is_apolar,
    )

    if alpha_spheres.n_alpha_spheres == 0:
        return Fpocket4NativeState(
            atom_indices=atom_indices,
            coordinates_nm=coordinates_nm,
            atom_types=atom_types,
            atom_radii_nm=atom_radii_nm,
            atom_electronegativities=atom_electronegativities,
            atom_b_factors=atom_b_factors,
            descriptor_occluder_coordinates_nm=descriptor_occluder_coordinates_nm,
            descriptor_occluder_radii_nm=descriptor_occluder_radii_nm,
            alpha_spheres=alpha_spheres,
            alpha_is_apolar=alpha_is_apolar,
            alpha_local_hydrophobic_density=alpha_local_hydrophobic_density,
            pocket_alpha_index_list=[],
            pocket_centers_nm=np.zeros((0, 3)),
            pocket_atom_index_list=[],
        )

    if alpha_spheres.n_alpha_spheres == 1:
        pocket_alpha_index_list = [[0]]
    else:
        linkage_matrix = linkage(alpha_spheres.centers, method='single', metric='euclidean')
        labels = fcluster(linkage_matrix, CLUST_MAX_DIST_NM, criterion='distance') - 1
        pocket_alpha_index_list = _group_labels(labels)

    pocket_alpha_index_list = [
        pocket_indices
        for pocket_indices in pocket_alpha_index_list
        if len(pocket_indices) >= MIN_POCKET_ALPHA_SPHERES
    ]

    pocket_centers_nm = np.array(
        [np.mean(alpha_spheres.centers[pocket_indices], axis=0) for pocket_indices in pocket_alpha_index_list],
        dtype=float,
    ) if pocket_alpha_index_list else np.zeros((0, 3))

    pocket_atom_index_list = [
        np.unique(atom_indices[alpha_spheres.points_of_alpha_sphere[pocket_indices]].reshape(-1)).astype(int).tolist()
        for pocket_indices in pocket_alpha_index_list
    ]

    return Fpocket4NativeState(
        atom_indices=atom_indices,
        coordinates_nm=coordinates_nm,
        atom_types=atom_types,
        atom_radii_nm=atom_radii_nm,
        atom_electronegativities=atom_electronegativities,
        atom_b_factors=atom_b_factors,
        descriptor_occluder_coordinates_nm=descriptor_occluder_coordinates_nm,
        descriptor_occluder_radii_nm=descriptor_occluder_radii_nm,
        alpha_spheres=alpha_spheres,
        alpha_is_apolar=alpha_is_apolar,
        alpha_local_hydrophobic_density=alpha_local_hydrophobic_density,
        pocket_alpha_index_list=pocket_alpha_index_list,
        pocket_centers_nm=pocket_centers_nm,
        pocket_atom_index_list=pocket_atom_index_list,
    )


def _apply_fpocket_candidate_filter(
    alpha_spheres: DelaunayMesh,
    coordinates_nm: np.ndarray,
    atom_b_factors: np.ndarray | None,
    upstream_bfactor_statistics: tuple[float, float, float] | None = None,
) -> None:
    if alpha_spheres.n_alpha_spheres == 0:
        return

    tetrahedron_points = coordinates_nm[alpha_spheres.points_of_alpha_sphere]
    distances = np.linalg.norm(
        tetrahedron_points - alpha_spheres.centers[:, None, :],
        axis=2,
    )
    first_distances = distances[:, [0]]
    equidistant_mask = np.all(
        np.abs(distances - first_distances) < PRECISION_TOLERANCE_NM,
        axis=1,
    )

    barycenters = np.mean(tetrahedron_points, axis=1)
    barycenter_distances = np.linalg.norm(alpha_spheres.centers - barycenters, axis=1)
    barycenter_mask = ~(
        (barycenter_distances > MAX_BARYCENTER_DISTANCE_NM)
        & (alpha_spheres.radii > LARGE_ALPHA_RADIUS_NM)
    )

    keep_mask = equidistant_mask & barycenter_mask

    if atom_b_factors is not None:
        tetra_b_factors = atom_b_factors[alpha_spheres.points_of_alpha_sphere]
        barycenter_b_factors = np.mean(tetra_b_factors, axis=1)
        if upstream_bfactor_statistics is None:
            average_b_factor = float(np.mean(atom_b_factors))
            max_b_factor = float(np.max(atom_b_factors))
            min_b_factor = float(np.min(atom_b_factors))
        else:
            average_b_factor, min_b_factor, max_b_factor = upstream_bfactor_statistics
        b_factor_std = np.std(tetra_b_factors, axis=1, ddof=1)
        b_factor_mask = ~(
            (
                (b_factor_std > average_b_factor)
                | (b_factor_std > ((max_b_factor - min_b_factor) / 4.0))
            )
            & (average_b_factor > 0.0)
            & ((barycenter_b_factors / average_b_factor) > 1.4)
        )
        keep_mask &= b_factor_mask

    if not np.all(keep_mask):
        alpha_spheres.remove_alpha_spheres(np.where(~keep_mask)[0])


def _classify_apolar_alpha_spheres(
    alpha_spheres: DelaunayMesh,
    atom_electronegativities: np.ndarray,
) -> np.ndarray:
    is_apolar_atom = atom_electronegativities < 2.8
    apolar_neighbor_counts = np.sum(is_apolar_atom[alpha_spheres.points_of_alpha_sphere], axis=1)
    return apolar_neighbor_counts >= MIN_APOLAR_NEIGHBORS


def _compute_local_hydrophobic_density(
    alpha_spheres: DelaunayMesh,
    alpha_is_apolar: np.ndarray,
) -> np.ndarray:
    local_density = np.zeros(alpha_spheres.n_alpha_spheres, dtype=float)
    if alpha_spheres.n_alpha_spheres == 0:
        return local_density

    centers = alpha_spheres.centers
    radii = alpha_spheres.radii
    for alpha_index in range(alpha_spheres.n_alpha_spheres):
        if not alpha_is_apolar[alpha_index]:
            continue
        distances = np.linalg.norm(centers - centers[alpha_index], axis=1)
        overlap = distances - (radii + radii[alpha_index])
        local_density[alpha_index] = float(np.sum((overlap <= 0.0) & alpha_is_apolar) - 1)

    return local_density


def _safe_convex_hull_volume(points: np.ndarray) -> float:
    if len(points) < 4:
        return 0.0
    try:
        return float(ConvexHull(points).volume)
    except Exception:
        return 0.0


_ASA_NSPIRAL = 100
_ASA_PROBE_14_NM = 0.14
_ASA_PROBE_22_NM = 0.22
_ASA_PADDING_NM = 0.10


def _get_points_on_sphere(n_points: int = _ASA_NSPIRAL) -> np.ndarray:
    points = np.empty((n_points, 3), dtype=float)
    increment = np.pi * (3.0 - np.sqrt(5.0))
    offset = 2.0 / float(n_points)
    for index in range(n_points):
        y_value = float(index) * offset - 1.0 + (offset / 2.0)
        radius = np.sqrt(max(0.0, 1.0 - y_value * y_value))
        phi = index * increment
        points[index, 0] = np.cos(phi) * radius
        points[index, 1] = y_value
        points[index, 2] = np.sin(phi) * radius
    return points


_ASA_SPHERE_POINTS = _get_points_on_sphere()


def _compute_pocket_local_hydrophobic_density(
    alpha_centers: np.ndarray,
    alpha_radii: np.ndarray,
    alpha_is_apolar: np.ndarray,
) -> float:
    if len(alpha_centers) == 0 or not np.any(alpha_is_apolar):
        return 0.0

    local_values = []
    for alpha_index in range(len(alpha_centers)):
        if not alpha_is_apolar[alpha_index]:
            continue

        distances = np.linalg.norm(alpha_centers - alpha_centers[alpha_index], axis=1)
        overlap = distances - (alpha_radii + alpha_radii[alpha_index])
        local_values.append(float(np.sum((overlap <= 0.0) & alpha_is_apolar) - 1))

    if len(local_values) == 0:
        return 0.0

    return float(np.mean(local_values))


def _compute_native_surface_descriptors(
    state: Fpocket4NativeState,
    alpha_indices_array: np.ndarray,
) -> tuple[float, float, float, float, int]:
    if alpha_indices_array.size == 0:
        return 0.0, 0.0, 0.0, 0.0, 0

    pocket_alpha_centers = state.alpha_spheres.centers[alpha_indices_array]
    pocket_alpha_radii = state.alpha_spheres.radii[alpha_indices_array]
    pocket_alpha_points = state.alpha_spheres.points_of_alpha_sphere[alpha_indices_array]
    unique_local_atom_indices = np.unique(pocket_alpha_points.reshape(-1))

    distances_to_centers = np.linalg.norm(
        state.descriptor_occluder_coordinates_nm[:, None, :] - pocket_alpha_centers[None, :, :],
        axis=2,
    )
    surrounding_mask = np.any(
        distances_to_centers < (pocket_alpha_radii[None, :] + _ASA_PADDING_NM),
        axis=1,
    )
    surrounding_indices = np.where(surrounding_mask)[0].astype(int)

    surf_pol_vdw14_angstrom2 = 0.0
    surf_apol_vdw14_angstrom2 = 0.0
    surf_pol_vdw22_angstrom2 = 0.0
    surf_apol_vdw22_angstrom2 = 0.0
    n_abpa = 0
    area14_by_atom = {}

    for local_atom_index in unique_local_atom_indices:
        atom_coordinate = state.coordinates_nm[local_atom_index]
        atom_radius_nm = state.atom_radii_nm[local_atom_index]
        atom_is_apolar = state.atom_electronegativities[local_atom_index] < 2.8
        contact_mask = np.any(pocket_alpha_points == local_atom_index, axis=1)
        atom_alpha_centers = pocket_alpha_centers[contact_mask]
        atom_alpha_radii = pocket_alpha_radii[contact_mask]

        probe14_points = atom_coordinate + _ASA_SPHERE_POINTS * (atom_radius_nm + _ASA_PROBE_14_NM)
        accessible14 = 0
        for point in probe14_points:
            if atom_alpha_centers.size == 0:
                vref_buried = True
            else:
                vref_buried = not np.any(
                    np.sum((point - atom_alpha_centers) ** 2, axis=1)
                    <= (atom_alpha_radii ** 2)
                )
            if vref_buried:
                continue

            buried = False
            for surrounding_index in surrounding_indices:
                surrounding_coordinate = state.descriptor_occluder_coordinates_nm[surrounding_index]
                surrounding_radius_nm = state.descriptor_occluder_radii_nm[surrounding_index]
                if np.sum((point - surrounding_coordinate) ** 2) < (
                    (surrounding_radius_nm + _ASA_PROBE_14_NM) ** 2
                ):
                    buried = True
                    break
            if not buried:
                accessible14 += 1

        area14_nm2 = (
            4.0
            * np.pi
            * (atom_radius_nm + _ASA_PROBE_14_NM) ** 2
            * (accessible14 / float(_ASA_NSPIRAL))
        )
        area14_angstrom2 = area14_nm2 * 100.0
        area14_by_atom[local_atom_index] = area14_angstrom2
        if atom_is_apolar:
            surf_apol_vdw14_angstrom2 += area14_angstrom2
        else:
            surf_pol_vdw14_angstrom2 += area14_angstrom2

        probe22_points = atom_coordinate + _ASA_SPHERE_POINTS * (atom_radius_nm + _ASA_PROBE_22_NM)
        accessible22 = 0
        for point in probe22_points:
            if atom_alpha_centers.size == 0:
                vref_buried = True
            else:
                vref_buried = not np.any(
                    np.sum((point - atom_alpha_centers) ** 2, axis=1)
                    <= (atom_alpha_radii ** 2)
                )
            if vref_buried:
                continue

            buried = False
            for surrounding_index in surrounding_indices:
                surrounding_coordinate = state.descriptor_occluder_coordinates_nm[surrounding_index]
                surrounding_radius_nm = state.descriptor_occluder_radii_nm[surrounding_index]
                if np.sum((point - surrounding_coordinate) ** 2) < (
                    (surrounding_radius_nm + _ASA_PROBE_22_NM) ** 2
                ):
                    buried = True
                    break
            if not buried:
                accessible22 += 1

        area22_nm2 = (
            4.0
            * np.pi
            * (atom_radius_nm + _ASA_PROBE_22_NM) ** 2
            * (accessible22 / float(_ASA_NSPIRAL))
        )
        area22_angstrom2 = area22_nm2 * 100.0
        if atom_is_apolar:
            surf_apol_vdw22_angstrom2 += area22_angstrom2
        else:
            if area22_angstrom2 < area14_angstrom2 and area14_angstrom2 <= 10.0:
                n_abpa += 1
            surf_pol_vdw22_angstrom2 += area22_angstrom2

    return (
        float(surf_pol_vdw14_angstrom2),
        float(surf_apol_vdw14_angstrom2),
        float(surf_pol_vdw22_angstrom2),
        float(surf_apol_vdw22_angstrom2),
        int(n_abpa),
    )


def _build_native_pocket_descriptor(
    state: Fpocket4NativeState,
    pocket_index: int,
) -> Fpocket4NativePocketDescriptor:
    alpha_indices = list(state.pocket_alpha_index_list[pocket_index])
    alpha_indices_array = np.asarray(alpha_indices, dtype=int)
    alpha_centers = state.alpha_spheres.centers[alpha_indices_array]
    alpha_radii = state.alpha_spheres.radii[alpha_indices_array]
    n_alpha_spheres = len(alpha_indices)
    volume_nm3 = float(np.sum(state.alpha_spheres.get_volumes()[alpha_indices_array]))
    mean_alpha_sphere_radius_nm = float(np.mean(alpha_radii))
    n_apolar_alpha_spheres = int(np.sum(state.alpha_is_apolar[alpha_indices_array]))
    apolar_alpha_sphere_ratio = (
        float(n_apolar_alpha_spheres / n_alpha_spheres) if n_alpha_spheres > 0 else 0.0
    )
    local_hydrophobic_density = _compute_pocket_local_hydrophobic_density(
        alpha_centers=alpha_centers,
        alpha_radii=alpha_radii,
        alpha_is_apolar=state.alpha_is_apolar[alpha_indices_array],
    )
    convex_hull_volume_nm3 = _safe_convex_hull_volume(alpha_centers)
    (
        surf_pol_vdw14_angstrom2,
        surf_apol_vdw14_angstrom2,
        surf_pol_vdw22_angstrom2,
        surf_apol_vdw22_angstrom2,
        n_abpa,
    ) = _compute_native_surface_descriptors(state, alpha_indices_array)

    if n_alpha_spheres > 1:
        pairwise_distances_nm = np.linalg.norm(
            alpha_centers[:, None, :] - alpha_centers[None, :, :],
            axis=2,
        )
        upper_triangle_nm = pairwise_distances_nm[np.triu_indices(n_alpha_spheres, 1)]
        as_density_angstrom = float(np.mean(upper_triangle_nm) * 10.0)
        as_max_dst_angstrom = float(np.max(upper_triangle_nm) * 10.0)
    else:
        as_density_angstrom = 0.0
        as_max_dst_angstrom = 0.0

    return Fpocket4NativePocketDescriptor(
        alpha_indices=alpha_indices,
        atom_indices=state.pocket_atom_index_list[pocket_index],
        center_nm=state.pocket_centers_nm[pocket_index],
        n_alpha_spheres=n_alpha_spheres,
        mean_alpha_sphere_radius_nm=mean_alpha_sphere_radius_nm,
        volume_nm3=volume_nm3,
        convex_hull_volume_nm3=convex_hull_volume_nm3,
        n_apolar_alpha_spheres=n_apolar_alpha_spheres,
        apolar_alpha_sphere_ratio=apolar_alpha_sphere_ratio,
        local_hydrophobic_density=local_hydrophobic_density,
        as_density_angstrom=as_density_angstrom,
        as_max_dst_angstrom=as_max_dst_angstrom,
        surf_pol_vdw14_angstrom2=surf_pol_vdw14_angstrom2,
        surf_apol_vdw14_angstrom2=surf_apol_vdw14_angstrom2,
        surf_pol_vdw22_angstrom2=surf_pol_vdw22_angstrom2,
        surf_apol_vdw22_angstrom2=surf_apol_vdw22_angstrom2,
        n_abpa=n_abpa,
        score=0.0,
    )


def _normalize_native_descriptors(
    descriptors: list[Fpocket4NativePocketDescriptor],
) -> None:
    if not descriptors:
        return

    if len(descriptors) == 1:
        descriptor = descriptors[0]
        descriptor.nas_norm = 0.0
        descriptor.mean_loc_hyd_dens_norm = 0.0
        descriptor.as_density_norm = 0.0
        descriptor.as_max_dst_norm = 0.0
        return

    nas_values = np.array([descriptor.n_alpha_spheres for descriptor in descriptors], dtype=float)
    mean_loc_hyd_dens_values = np.array(
        [descriptor.local_hydrophobic_density for descriptor in descriptors],
        dtype=float,
    )
    as_density_values = np.array(
        [descriptor.as_density_angstrom for descriptor in descriptors],
        dtype=float,
    )
    as_max_dst_values = np.array(
        [descriptor.as_max_dst_angstrom for descriptor in descriptors],
        dtype=float,
    )

    nas_min = float(np.min(nas_values))
    nas_max = float(np.max(nas_values))
    mean_loc_hyd_dens_min = float(np.min(mean_loc_hyd_dens_values))
    mean_loc_hyd_dens_max = float(np.max(mean_loc_hyd_dens_values))
    as_density_min = float(np.min(as_density_values))
    as_density_max = float(np.max(as_density_values))
    as_max_dst_min = float(np.min(as_max_dst_values))
    as_max_dst_max = float(np.max(as_max_dst_values))

    for descriptor in descriptors:
        if nas_max != nas_min:
            descriptor.nas_norm = (
                descriptor.n_alpha_spheres - nas_min
            ) / (nas_max - nas_min)
        if mean_loc_hyd_dens_max != mean_loc_hyd_dens_min:
            descriptor.mean_loc_hyd_dens_norm = (
                descriptor.local_hydrophobic_density - mean_loc_hyd_dens_min
            ) / (mean_loc_hyd_dens_max - mean_loc_hyd_dens_min)
        if as_density_max != as_density_min:
            descriptor.as_density_norm = (
                descriptor.as_density_angstrom - as_density_min
            ) / (as_density_max - as_density_min)
        if as_max_dst_max != as_max_dst_min:
            descriptor.as_max_dst_norm = (
                descriptor.as_max_dst_angstrom - as_max_dst_min
            ) / (as_max_dst_max - as_max_dst_min)


def _score_native_pocket(
    descriptor: Fpocket4NativePocketDescriptor,
) -> float:
    convex_hull_volume_angstrom3 = float((descriptor.convex_hull_volume_nm3 or 0.0) * 1000.0)
    return float(
        -0.03783394
        + 0.48461469 * descriptor.nas_norm
        + 0.09093926 * descriptor.as_density_angstrom
        + 0.0004155899 * convex_hull_volume_angstrom3
        - 0.003995233 * descriptor.surf_pol_vdw14_angstrom2
        - 0.004072336 * descriptor.surf_apol_vdw14_angstrom2
    )


def _drug_score_native_pocket(
    descriptor: Fpocket4NativePocketDescriptor,
) -> float:
    b0 = -9.5698768
    b1 = 7.479844
    b2 = 0.3696134

    return float(
        1.0
        / (
            1.0
            + np.exp(
                -(
                    b0
                    + b1 * descriptor.mean_loc_hyd_dens_norm
                    + b2 * descriptor.as_max_dst_angstrom
                    - 0.04671833 * descriptor.surf_pol_vdw22_angstrom2
                )
            )
        )
    )


def _keep_native_pocket(descriptor: Fpocket4NativePocketDescriptor) -> bool:
    if descriptor.n_alpha_spheres < MIN_POCKET_ALPHA_SPHERES:
        return False

    if descriptor.as_density_angstrom < 0.7:
        return False

    return True


def _native_topography_from_state(
    state: Fpocket4NativeState,
    molecular_system: Any = None,
    *,
    source: str = 'fpocket-native',
    source_prefix: str = 'fpocket-native',
) -> Topography:
    topography = Topography(molecular_system=molecular_system)

    descriptors = [
        _build_native_pocket_descriptor(state, pocket_index)
        for pocket_index in range(len(state.pocket_alpha_index_list))
    ]
    descriptors = [descriptor for descriptor in descriptors if _keep_native_pocket(descriptor)]
    _normalize_native_descriptors(descriptors)
    for descriptor in descriptors:
        descriptor.score = _score_native_pocket(descriptor)
        descriptor.druggability_score = _drug_score_native_pocket(descriptor)
    descriptors.sort(key=lambda descriptor: descriptor.score, reverse=True)

    for pocket_index, descriptor in enumerate(descriptors, start=1):
        alpha_indices_array = np.asarray(descriptor.alpha_indices, dtype=int)
        alpha_centers = state.alpha_spheres.centers[alpha_indices_array]
        alpha_radii = state.alpha_spheres.radii[alpha_indices_array]
        pocket = Pocket(
            atom_indices=descriptor.atom_indices,
            center=puw.quantity(descriptor.center_nm, 'nm'),
            volume=puw.quantity(descriptor.volume_nm3, 'nm**3'),
            convex_hull_volume=puw.quantity(descriptor.convex_hull_volume_nm3, 'nm**3'),
            score=descriptor.score,
            n_alpha_spheres=descriptor.n_alpha_spheres,
            mean_alpha_sphere_radius=puw.quantity(descriptor.mean_alpha_sphere_radius_nm, 'nm'),
            n_apolar_alpha_spheres=descriptor.n_apolar_alpha_spheres,
            apolar_alpha_sphere_ratio=descriptor.apolar_alpha_sphere_ratio,
            local_hydrophobic_density_score=descriptor.local_hydrophobic_density,
            as_density=descriptor.as_density_angstrom,
            as_max_dst=descriptor.as_max_dst_angstrom,
            druggability_score=descriptor.druggability_score,
            alpha_sphere_centers=puw.quantity(alpha_centers, 'nm'),
            alpha_sphere_radii=puw.quantity(alpha_radii, 'nm'),
            source=source,
            source_id=f'{source_prefix}:{pocket_index}',
        )
        topography.add_feature(pocket)

    return topography


@signal(tags=['method', 'fpocket4', 'native'])
@arg_digest()
def fpocket4(
    molecular_system,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    fpocket_cmd: str = 'fpocket',
    extra_args: list[str] | None = None,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
    implementation: str = 'wrapper',
    keep_water: bool = False,
    keep_ions: bool = False,
    keep_small_molecules: bool = False,
    include_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
    exclude_group_names: list[str] | tuple[str, ...] | set[str] | None = None,
):
    """
    Run either the wrapper-backed fpocket integration, the upstream-parity
    native implementation, or the TopoMT-corrected native variant.

    The default path remains the wrapper-backed integration because that is the
    only validated faithful route today. The native path targets upstream
    compatibility. The TopoMT path keeps the same implementation scaffold while
    allowing corrected semantics where TopoMT intentionally diverges from the
    original method.
    """

    structure_indices = _normalize_structure_indices(structure_indices)

    if implementation == 'wrapper':
        return get_topography_with_fpocket(
            molecular_system,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
            fpocket_cmd=fpocket_cmd,
            extra_args=extra_args,
        )

    if implementation not in {'native', 'topomt'}:
        raise ValueError("implementation must be 'wrapper', 'native' or 'topomt'")

    state = _build_native_state(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        keep_water=keep_water,
        keep_ions=keep_ions,
        keep_small_molecules=keep_small_molecules,
        include_group_names=include_group_names,
        exclude_group_names=exclude_group_names,
        implementation=implementation,
    )

    if implementation == 'native':
        return _native_topography_from_state(state, molecular_system=molecular_system)

    return _native_topography_from_state(
        state,
        molecular_system=molecular_system,
        source='fpocket-topomt',
        source_prefix='fpocket-topomt',
    )
