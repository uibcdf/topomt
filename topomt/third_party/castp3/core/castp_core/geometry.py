"""Canonical weighted geometry substrate for the native CASTp implementation."""

from dataclasses import dataclass
from functools import cmp_to_key
from functools import lru_cache
from pathlib import Path

import molsysmt as msm
import numpy as np

from topomt import pyunitwizard as puw
from topomt.weighted_delaunay_mesh import WeightedDelaunayMesh, _regular_triangulation_simplices
from .exact import ExactRatio, castp1_fixed_point_array, exact_determinant


_CASTP_PARAM_PATH = Path(__file__).resolve().parents[4] / 'data' / 'castp' / 'param.dat'
_CASTP_DEFAULT_HEAVY_RADIUS = 1.8
_CASTP_DEFAULT_HYDROGEN_RADIUS = 1.2
_CASTP1_FIXED_DECIMALS = 5
_PROTOR_FALLBACK_RADII = {
    'C': 1.88,
    'N': 1.64,
    'O': 1.42,
    'S': 1.77,
}
_PROTOR_RADII_BY_TYPE = {
    'C3H0': 1.61,
    'C3H1': 1.76,
    'C4H1': 1.88,
    'C4H2': 1.88,
    'C4H3': 1.88,
    'N3H0': 1.64,
    'N3H1': 1.64,
    'N3H2': 1.64,
    'N4H3': 1.64,
    'O1H0': 1.42,
    'O2H1': 1.46,
    'S2H0': 1.77,
    'S2H1': 1.77,
}
_PROTOR_PROTEIN_BACKBONE_TYPES = {
    'N': 'N3H1',
    'CA': 'C4H1',
    'C': 'C3H0',
    'O': 'O1H0',
    'OXT': 'O2H1',
}
_PROTOR_RESIDUE_NAME_ALIASES = {
    'HSD': 'HID',
    'HSE': 'HIE',
    'HSP': 'HIP',
}
_PROTOR_PROTEIN_HEAVY_ATOM_TYPES = {
    'ALA': {'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0', 'CB': 'C4H3'},
    'ARG': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C4H2', 'NE': 'N3H1', 'CZ': 'C3H0', 'NH1': 'N3H2', 'NH2': 'N3H2',
    },
    'ASN': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'OD1': 'O1H0', 'ND2': 'N3H2',
    },
    'ASP': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'OD1': 'O1H0', 'OD2': 'O1H0',
    },
    'ASH': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'OD1': 'O1H0', 'OD2': 'O2H1',
    },
    'CYS': {'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0', 'CB': 'C4H2', 'SG': 'S2H1'},
    'CYX': {'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0', 'CB': 'C4H2', 'SG': 'S2H0'},
    'GLN': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C3H0', 'OE1': 'O1H0', 'NE2': 'N3H2',
    },
    'GLU': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C3H0', 'OE1': 'O1H0', 'OE2': 'O1H0',
    },
    'GLH': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C3H0', 'OE1': 'O1H0', 'OE2': 'O2H1',
    },
    'GLY': {'N': 'N3H1', 'CA': 'C4H2', 'C': 'C3H0', 'O': 'O1H0'},
    'HIS': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'ND1': 'N3H0', 'CD2': 'C3H1', 'CE1': 'C3H1', 'NE2': 'N3H0',
    },
    'HID': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'ND1': 'N3H1', 'CD2': 'C3H1', 'CE1': 'C3H1', 'NE2': 'N3H0',
    },
    'HIE': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'ND1': 'N3H0', 'CD2': 'C3H1', 'CE1': 'C3H1', 'NE2': 'N3H1',
    },
    'HIP': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'ND1': 'N3H1', 'CD2': 'C3H1', 'CE1': 'C3H1', 'NE2': 'N3H1',
    },
    'ILE': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H1', 'CG1': 'C4H2', 'CG2': 'C4H3', 'CD1': 'C4H3',
    },
    'LEU': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C4H1', 'CD1': 'C4H3', 'CD2': 'C4H3',
    },
    'LYS': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C4H2', 'CE': 'C4H2', 'NZ': 'N4H3',
    },
    'LYN': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C4H2', 'CE': 'C4H2', 'NZ': 'N3H2',
    },
    'MET': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C4H2', 'SD': 'S2H0', 'CE': 'C4H3',
    },
    'PHE': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'CD1': 'C3H1', 'CD2': 'C3H1', 'CE1': 'C3H1', 'CE2': 'C3H1', 'CZ': 'C3H1',
    },
    'PRO': {'N': 'N3H0', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0', 'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C4H2'},
    'SER': {'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0', 'CB': 'C4H2', 'OG': 'O2H1'},
    'THR': {'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0', 'CB': 'C4H1', 'OG1': 'O2H1', 'CG2': 'C4H3'},
    'TRP': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'CD1': 'C3H1', 'CD2': 'C3H0', 'NE1': 'N3H1', 'CE2': 'C3H0',
        'CE3': 'C3H1', 'CZ2': 'C3H1', 'CZ3': 'C3H1', 'CH2': 'C3H1',
    },
    'TYR': {
        'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0',
        'CB': 'C4H2', 'CG': 'C3H0', 'CD1': 'C3H1', 'CD2': 'C3H1', 'CE1': 'C3H1', 'CE2': 'C3H1', 'CZ': 'C3H0', 'OH': 'O2H1',
    },
    'VAL': {'N': 'N3H1', 'CA': 'C4H1', 'C': 'C3H0', 'O': 'O1H0', 'CB': 'C4H1', 'CG1': 'C4H3', 'CG2': 'C4H3'},
}

ALF_BLANK = 0
ALF_VERTEX = 1
ALF_EDGE = 2
ALF_TRIANGLE = 3
ALF_TETRA = 4

ALF_RHO = 1
ALF_MU1 = 2
ALF_MU2 = 3


@dataclass(slots=True)
class CastpGeometry:
    """Shared weighted tetrahedral substrate used by the native CASTp path."""

    molecular_system: object
    selection: str
    structure_indices: int | list[int]
    solvent_radius: float
    radii_model: str
    atom_indices_map: np.ndarray
    atom_coordinates: np.ndarray
    atom_radii: np.ndarray
    mesh: WeightedDelaunayMesh
    simplex_regular_mask: np.ndarray
    spectrum_values: np.ndarray
    spectrum_ratios: tuple[ExactRatio, ...]
    spectrum_decimals: int
    base_rank: int
    simplex_rho_ranks: np.ndarray
    simplex_rank_sublists: dict[int, list[int]]
    master_entries: list['CastpMasterEntry']
    master_rank_offsets: dict[int, tuple[int, int]]
    face_rho_values: np.ndarray
    face_centers: np.ndarray
    face_rho_ranks: np.ndarray
    face_mu1_ranks: np.ndarray
    face_mu2_ranks: np.ndarray
    face_is_on_hull: np.ndarray
    face_records: list[tuple[int, int, tuple[int, int, int]]]
    edge_rho_ranks: dict[tuple[int, int], int]
    edge_mu1_ranks: dict[tuple[int, int], int]
    edge_mu2_ranks: dict[tuple[int, int], int]
    vertex_rho_ranks: np.ndarray
    vertex_mu1_ranks: np.ndarray
    vertex_mu2_ranks: np.ndarray


@dataclass(frozen=True, slots=True)
class CastpMasterEntry:
    """Python-level mirror of one MKALF master-list entry."""

    rank: int
    f_type: int
    r_type: int
    index: int
    is_attached: bool
    is_first: bool
    insertion_order: int = 0


@lru_cache(maxsize=1)
def _load_castp_param_radii() -> dict[tuple[str, str], float]:
    """Load CAST's historical PDB2ALF radii table."""

    param_radii = {}
    with _CASTP_PARAM_PATH.open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            fields = line.split()
            if len(fields) < 6:
                continue
            try:
                radius = float(fields[5])
            except ValueError:
                continue
            param_radii[(fields[0].strip(), fields[1].strip())] = radius

    if not param_radii:
        raise ValueError(f'CAST parameter file is empty or unreadable: {_CASTP_PARAM_PATH}')

    return param_radii


def _castp_param_radii_for_labels(
    group_names: np.ndarray,
    atom_names: np.ndarray,
) -> np.ndarray:
    """Return CAST PDB2ALF radii for the provided residue/atom labels."""

    param_radii = _load_castp_param_radii()
    radii = np.empty(len(group_names), dtype=float)

    for index, (group_name, atom_name) in enumerate(zip(group_names, atom_names)):
        residue_name = str(group_name).strip()
        atom_label = str(atom_name).strip()
        radius = param_radii.get((residue_name, atom_label))
        if radius is None:
            atom_is_hydrogen = atom_label.lstrip('0123456789').startswith('H')
            radius = _CASTP_DEFAULT_HYDROGEN_RADIUS if atom_is_hydrogen else _CASTP_DEFAULT_HEAVY_RADIUS
        radii[index] = float(radius)

    return radii


def _castp1_pdb2alf_radii_for_pdb_path(pdb_path: str | Path) -> np.ndarray:
    """Return base radii assigned by CASTp1's PDB2ALF PDB field policy."""

    param_radii = _load_castp_param_radii()
    radii = []

    with Path(pdb_path).open('r', encoding='utf-8') as handle:
        for raw_line in handle:
            if not (raw_line.startswith('ATOM') or raw_line.startswith('HETATM')):
                continue

            atom_label = raw_line[12:16].strip()
            residue_label = raw_line[17:21].strip()
            if residue_label == 'A':
                residue_label = 'ADE'
            elif residue_label == 'T':
                residue_label = 'THY'
            elif residue_label == 'G':
                residue_label = 'GUA'
            elif residue_label == 'C':
                residue_label = 'CYT'

            radius = param_radii.get((residue_label, atom_label))
            if radius is None:
                warning_key = raw_line[12:21].strip().replace(' ', '')
                atom_is_hydrogen = warning_key.lstrip('0123456789').startswith('H')
                radius = _CASTP_DEFAULT_HYDROGEN_RADIUS if atom_is_hydrogen else _CASTP_DEFAULT_HEAVY_RADIUS
            radii.append(float(radius))

    if not radii:
        raise ValueError(f'No ATOM/HETATM records found in PDB file: {pdb_path}')

    return np.asarray(radii, dtype=float)


def _path_like_or_none(value) -> Path | None:
    """Return a filesystem path when the molecular input is path-like."""

    if isinstance(value, Path):
        return value
    if isinstance(value, str):
        path = Path(value)
        if path.exists():
            return path
    return None


def _infer_protor_type_for_atom(
    residue_name: str,
    atom_name: str,
    atom_type: str,
    n_bonds: int,
) -> str | None:
    """Infer the CASTpFold ProtOr-like atom type for a heavy atom."""

    residue_name = str(residue_name).strip().upper()
    atom_name = str(atom_name).strip().upper()
    atom_type = str(atom_type).strip().upper()
    n_bonds = int(n_bonds)

    normalized_residue_name = _PROTOR_RESIDUE_NAME_ALIASES.get(residue_name, residue_name)
    residue_map = _PROTOR_PROTEIN_HEAVY_ATOM_TYPES.get(normalized_residue_name)
    if residue_map is not None and atom_name in residue_map:
        return residue_map[atom_name]

    if atom_name in _PROTOR_PROTEIN_BACKBONE_TYPES:
        if atom_name == 'N':
            return 'N3H0' if normalized_residue_name == 'PRO' else 'N3H1'
        if atom_name == 'CA':
            return 'C4H2' if normalized_residue_name == 'GLY' else 'C4H1'
        return _PROTOR_PROTEIN_BACKBONE_TYPES[atom_name]

    if atom_type == 'S':
        return 'S2H1' if n_bonds <= 1 else 'S2H0'

    return None


def _protor_radii_for_labels(
    group_names: np.ndarray,
    atom_names: np.ndarray,
    atom_types: np.ndarray,
    n_bonds: np.ndarray,
) -> np.ndarray:
    """Return CASTpFold ProtOr-like radii for heavy atoms."""

    radii = np.empty(len(group_names), dtype=float)

    for index, (group_name, atom_name, atom_type, atom_n_bonds) in enumerate(
        zip(group_names, atom_names, atom_types, n_bonds)
    ):
        protor_type = _infer_protor_type_for_atom(group_name, atom_name, atom_type, int(atom_n_bonds))
        if protor_type is not None:
            radii[index] = float(_PROTOR_RADII_BY_TYPE[protor_type])
            continue

        element = str(atom_type).strip().upper()
        radii[index] = float(_PROTOR_FALLBACK_RADII.get(element, _CASTP_DEFAULT_HEAVY_RADIUS))

    return radii


def _rank_of_ratio(spectrum_ratios: tuple[ExactRatio, ...], value_ratio: ExactRatio) -> int:
    """Return the 1-based MKALF-like rank of an exact threshold ratio."""

    if not spectrum_ratios:
        return 1

    left = 0
    right = len(spectrum_ratios)
    while left < right:
        middle = (left + right) // 2
        comparison = spectrum_ratios[middle].compare(value_ratio)
        if comparison <= 0:
            left = middle + 1
        else:
            right = middle
    if left <= 0:
        return 1
    if left >= len(spectrum_ratios):
        return int(len(spectrum_ratios))
    return int(left)


def _exact_threshold_ratio(value: float, decimals: int) -> ExactRatio:
    """Return the exact spectrum-threshold ratio on the native fixed grid."""

    scale = 10 ** int(decimals)
    scaled_value = int(round(float(value) * scale))
    return ExactRatio(scaled_value * scaled_value, 1)


def _rank_table_is_in_complex(rho_rank: int, mu1_rank: int, rank: int) -> bool:
    """Return `alf_is_in_complex` semantics for one historical rank-table row."""

    rho_rank = int(rho_rank)
    mu1_rank = int(mu1_rank)
    rank = int(rank)
    if rho_rank < 0:
        return False
    if rho_rank != 0:
        return bool(rho_rank <= rank)
    return bool(mu1_rank <= rank)


def _rank_table_is_interior(mu2_rank: int, rank: int) -> bool:
    """Return `alf_is_interior` semantics for a non-hull rank-table row."""

    mu2_rank = int(mu2_rank)
    rank = int(rank)
    if mu2_rank == 0:
        return False
    return bool(mu2_rank <= rank)


def _face_is_in_complex_at(geometry: CastpGeometry, simplex_index: int, face_index: int, rank: int) -> bool:
    """Return canonical `alf_is_in_complex(ALF_TRIANGLE, rank, ...)` semantics."""

    simplex_index = int(simplex_index)
    face_index = int(face_index)
    return _rank_table_is_in_complex(
        int(geometry.face_rho_ranks[simplex_index, face_index]),
        int(geometry.face_mu1_ranks[simplex_index, face_index]),
        int(rank),
    )


def _edge_is_in_complex_at(
    edge_rho_ranks: dict[tuple[int, int], int],
    edge_mu1_ranks: dict[tuple[int, int], int],
    edge: tuple[int, int],
    rank: int,
) -> bool:
    """Return canonical `alf_is_in_complex(ALF_EDGE, rank, ...)` semantics."""

    edge = tuple(sorted((int(edge[0]), int(edge[1]))))
    if edge not in edge_rho_ranks and edge not in edge_mu1_ranks:
        return False
    return _rank_table_is_in_complex(
        int(edge_rho_ranks.get(edge, 0)),
        int(edge_mu1_ranks.get(edge, 0)),
        int(rank),
    )


def _vertex_is_in_complex_at(geometry: CastpGeometry, vertex_index: int, rank: int) -> bool:
    """Return canonical `alf_is_in_complex(ALF_VERTEX, rank, ...)` semantics."""

    vertex_index = int(vertex_index)
    return _rank_table_is_in_complex(
        int(geometry.vertex_rho_ranks[vertex_index]),
        int(geometry.vertex_mu1_ranks[vertex_index]),
        int(rank),
    )


def _vertex_is_interior_at(geometry: CastpGeometry, vertex_index: int, rank: int) -> bool:
    """Return canonical `alf_is_interior(ALF_VERTEX, rank, ...)` semantics."""

    vertex_index = int(vertex_index)
    return _rank_table_is_interior(
        int(geometry.vertex_mu2_ranks[vertex_index]),
        int(rank),
    )


def _infer_decimal_places(values: np.ndarray, max_places: int = 6, tolerance: float = 1e-12) -> int:
    """Infer the smallest decimal grid that represents the values faithfully."""

    values_array = np.asarray(values, dtype=float)
    for decimals in range(max_places + 1):
        if np.allclose(values_array, np.round(values_array, decimals), atol=tolerance, rtol=0.0):
            return int(decimals)
    return int(max_places)


def _infer_weighted_decimal_places(points: np.ndarray, weights: np.ndarray) -> int:
    """Infer the fixed-point coordinate grid from coordinates and squared radii."""

    weights_array = np.asarray(weights, dtype=float)
    nonnegative_weights = weights_array[weights_array >= 0.0]
    if nonnegative_weights.size:
        radii = np.sqrt(nonnegative_weights)
        return max(_infer_decimal_places(points), _infer_decimal_places(radii))
    return _infer_decimal_places(points)


def _deduplicate_weighted_points(
    atom_coordinates: np.ndarray,
    atom_radii: np.ndarray,
    atom_indices_map: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Discard duplicate coordinates following DELCX's weighted input scan."""

    atom_coordinates = np.asarray(atom_coordinates, dtype=float)
    atom_radii = np.asarray(atom_radii, dtype=float)
    atom_indices_map = np.asarray(atom_indices_map, dtype=int)

    kept_positions: list[int] = []
    key_to_output_position: dict[tuple[float, float, float], int] = {}

    for atom_index, (point, radius) in enumerate(zip(atom_coordinates, atom_radii)):
        key = tuple(float(coordinate) for coordinate in point)
        output_position = key_to_output_position.get(key)
        if output_position is None:
            key_to_output_position[key] = len(kept_positions)
            kept_positions.append(int(atom_index))
            continue

        kept_atom_index = kept_positions[output_position]
        if float(radius) > float(atom_radii[kept_atom_index]):
            kept_positions[output_position] = int(atom_index)

    kept_positions_array = np.asarray(kept_positions, dtype=int)
    return (
        atom_coordinates[kept_positions_array],
        atom_radii[kept_positions_array],
        atom_indices_map[kept_positions_array],
    )


def _discard_redundant_weighted_points(
    atom_coordinates: np.ndarray,
    atom_radii: np.ndarray,
    atom_indices_map: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Discard regular-triangulation redundant vertices like DELCX."""

    atom_coordinates = np.asarray(atom_coordinates, dtype=float)
    atom_radii = np.asarray(atom_radii, dtype=float)
    atom_indices_map = np.asarray(atom_indices_map, dtype=int)

    if atom_coordinates.shape[0] <= 4:
        return atom_coordinates, atom_radii, atom_indices_map

    _oriented_simplices, sorted_simplices = _regular_triangulation_simplices(
        atom_coordinates,
        np.asarray(atom_radii * atom_radii, dtype=float),
    )
    used_positions = np.unique(np.asarray(sorted_simplices, dtype=int).reshape(-1))
    used_positions.sort()

    if used_positions.size == atom_coordinates.shape[0]:
        return atom_coordinates, atom_radii, atom_indices_map

    return (
        atom_coordinates[used_positions],
        atom_radii[used_positions],
        atom_indices_map[used_positions],
    )


def _face_rank_data(
    mesh: WeightedDelaunayMesh,
) -> tuple[np.ndarray, list[tuple[int, int, tuple[int, int, int]]]]:
    """Return face-level hull flags and canonical face records."""

    face_to_incident_simplices: dict[tuple[int, int, int], list[int]] = {}
    face_records: list[tuple[int, int, tuple[int, int, int]]] = []

    for simplex_index, simplex_neighbors in enumerate(mesh.neighbors):
        for face_index, neighbor in enumerate(simplex_neighbors):
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            face_to_incident_simplices.setdefault(face_atoms, []).append(int(simplex_index))
            face_records.append((int(simplex_index), int(face_index), face_atoms))

    face_is_on_hull_map: dict[tuple[int, int, int], bool] = {}

    for face_atoms, simplex_indices in face_to_incident_simplices.items():
        face_is_on_hull_map[face_atoms] = len(simplex_indices) == 1

    face_is_on_hull = np.zeros((mesh.n_simplices, 4), dtype=bool)

    for simplex_index, simplex_neighbors in enumerate(mesh.neighbors):
        for face_index, _neighbor in enumerate(simplex_neighbors):
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            face_is_on_hull[simplex_index, face_index] = face_is_on_hull_map[face_atoms]

    return face_is_on_hull, face_records


def _simplex_rank_sublists(simplex_rho_ranks: np.ndarray) -> dict[int, list[int]]:
    """Return tetrahedron rank sublists analogous to MKALF master sublists.

    MKALF stores a complete master list with all simplices and all rank-table
    events.  The pocket workflow later scans that structure rank by rank and
    reacts only to tetrahedron rho events.  This helper captures exactly that
    tetrahedron-facing view: for each rho rank, list the tetrahedra that enter
    at that rank.
    """

    result: dict[int, list[int]] = {}
    for simplex_index, simplex_rho_rank in enumerate(np.asarray(simplex_rho_ranks, dtype=int)):
        result.setdefault(int(simplex_rho_rank), []).append(int(simplex_index))
    return result


def _build_master_entries(
    simplex_rho_ranks: np.ndarray,
    face_rho_ranks: np.ndarray,
    face_mu1_ranks: np.ndarray,
    face_mu2_ranks: np.ndarray,
    edge_rho_ranks: dict[tuple[int, int], int],
    edge_mu1_ranks: dict[tuple[int, int], int],
    edge_mu2_ranks: dict[tuple[int, int], int],
    vertex_rho_ranks: np.ndarray,
    vertex_mu1_ranks: np.ndarray,
    vertex_mu2_ranks: np.ndarray,
    face_records: list[tuple[int, int, tuple[int, int, int]]],
) -> tuple[list[CastpMasterEntry], dict[int, tuple[int, int]], dict[int, list[int]]]:
    """Return a Python mirror of the historical MKALF master list."""

    rank_buckets: dict[int, list[CastpMasterEntry]] = {}
    insertion_order = 0

    def push(rank: int, f_type: int, r_type: int, index: int, is_attached: bool) -> None:
        nonlocal insertion_order
        if int(rank) <= 0:
            return
        insertion_order += 1
        # MKALF pushes master-list events to the head of the rank bucket
        # (`mheap_node[hn].nexti = auxi[r]; auxi[r] = hn`) before stable
        # sorting only by f_type in collect_master().
        rank_buckets.setdefault(int(rank), []).append(
            CastpMasterEntry(
                rank=int(rank),
                f_type=int(f_type),
                r_type=int(r_type),
                index=int(index),
                is_attached=bool(is_attached),
                is_first=bool(r_type == ALF_RHO or (r_type == ALF_MU1 and is_attached)),
                insertion_order=int(insertion_order),
            )
        )

    for simplex_index, simplex_rho_rank in enumerate(np.asarray(simplex_rho_ranks, dtype=int)):
        push(int(simplex_rho_rank), ALF_TETRA, ALF_RHO, int(simplex_index), False)

    face_id_by_atoms: dict[tuple[int, int, int], int] = {}
    face_rank_payloads: dict[int, tuple[int, int, int, bool]] = {}
    for simplex_index, face_index, face_atoms in face_records:
        face_id = face_id_by_atoms.setdefault(tuple(face_atoms), len(face_id_by_atoms))
        if face_id in face_rank_payloads:
            continue
        face_rho_rank = int(face_rho_ranks[int(simplex_index), int(face_index)])
        face_mu1_rank = int(face_mu1_ranks[int(simplex_index), int(face_index)])
        face_mu2_rank = int(face_mu2_ranks[int(simplex_index), int(face_index)])
        face_rank_payloads[face_id] = (
            face_rho_rank,
            face_mu1_rank,
            face_mu2_rank,
            face_rho_rank == 0,
        )

    for face_id, (face_rho_rank, face_mu1_rank, face_mu2_rank, is_attached) in face_rank_payloads.items():
        push(face_rho_rank, ALF_TRIANGLE, ALF_RHO, face_id, bool(is_attached))
        push(face_mu1_rank, ALF_TRIANGLE, ALF_MU1, face_id, bool(is_attached))
        push(face_mu2_rank, ALF_TRIANGLE, ALF_MU2, face_id, bool(is_attached))

    edge_id_by_atoms: dict[tuple[int, int], int] = {
        tuple(edge): edge_id for edge_id, edge in enumerate(sorted(edge_rho_ranks))
    }
    for edge_atoms, edge_id in edge_id_by_atoms.items():
        edge_rho_rank = int(edge_rho_ranks[edge_atoms])
        edge_mu1_rank = int(edge_mu1_ranks.get(edge_atoms, 0))
        edge_mu2_rank = int(edge_mu2_ranks.get(edge_atoms, 0))
        is_attached = edge_rho_rank == 0
        push(edge_rho_rank, ALF_EDGE, ALF_RHO, edge_id, bool(is_attached))
        push(edge_mu1_rank, ALF_EDGE, ALF_MU1, edge_id, bool(is_attached))
        push(edge_mu2_rank, ALF_EDGE, ALF_MU2, edge_id, bool(is_attached))

    for vertex_index in range(len(vertex_rho_ranks)):
        vertex_rho_rank = int(vertex_rho_ranks[vertex_index])
        vertex_mu1_rank = int(vertex_mu1_ranks[vertex_index])
        vertex_mu2_rank = int(vertex_mu2_ranks[vertex_index])
        is_attached = vertex_rho_rank == 0
        push(vertex_rho_rank, ALF_VERTEX, ALF_RHO, int(vertex_index), bool(is_attached))
        push(vertex_mu1_rank, ALF_VERTEX, ALF_MU1, int(vertex_index), bool(is_attached))
        push(vertex_mu2_rank, ALF_VERTEX, ALF_MU2, int(vertex_index), bool(is_attached))

    master_entries: list[CastpMasterEntry] = []
    master_rank_offsets: dict[int, tuple[int, int]] = {}
    simplex_rank_sublists: dict[int, list[int]] = {}

    for rank in sorted(rank_buckets):
        sublist = sorted(
            rank_buckets[rank],
            key=lambda entry: (entry.f_type, -entry.insertion_order),
        )
        start = len(master_entries)
        master_entries.extend(sublist)
        master_rank_offsets[int(rank)] = (int(start), int(len(master_entries)))
        tetra_sublist = [
            int(entry.index)
            for entry in sublist
            if entry.f_type == ALF_TETRA and entry.r_type == ALF_RHO
        ]
        if tetra_sublist:
            simplex_rank_sublists[int(rank)] = tetra_sublist

    return master_entries, master_rank_offsets, simplex_rank_sublists


def _weighted_face_center_and_power(
    face_points: np.ndarray,
    face_weights: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Return the weighted orthogonal center and power value of a triangle."""

    point_a = face_points[0]
    weight_a = float(face_weights[0])
    edge_ab = face_points[1] - point_a
    edge_ac = face_points[2] - point_a
    normal = np.cross(edge_ab, edge_ac)

    matrix = np.vstack(
        [
            2.0 * (face_points[1] - point_a),
            2.0 * (face_points[2] - point_a),
            normal,
        ]
    )
    vector = np.array(
        [
            np.dot(face_points[1], face_points[1]) - np.dot(point_a, point_a) - face_weights[1] + weight_a,
            np.dot(face_points[2], face_points[2]) - np.dot(point_a, point_a) - face_weights[2] + weight_a,
            np.dot(normal, point_a),
        ],
        dtype=float,
    )

    try:
        center = np.linalg.solve(matrix, vector)
    except np.linalg.LinAlgError:
        center = np.mean(face_points, axis=0)

    power_value = float(np.dot(center - point_a, center - point_a) - weight_a)
    return center, power_value


def _weighted_face_size2_value(
    face_points: np.ndarray,
    face_weights: np.ndarray,
) -> float:
    """Return the historical weighted ``size2`` value for a triangle."""

    triangle_rows = _homogeneous_lifted_rows(
        np.asarray(face_points, dtype=float),
        np.asarray(face_weights, dtype=float),
    )

    minor_120 = _minor_determinant(triangle_rows, (1, 2, 0))
    minor_130 = _minor_determinant(triangle_rows, (1, 3, 0))
    minor_140 = _minor_determinant(triangle_rows, (1, 4, 0))
    minor_230 = _minor_determinant(triangle_rows, (2, 3, 0))
    minor_240 = _minor_determinant(triangle_rows, (2, 4, 0))
    minor_340 = _minor_determinant(triangle_rows, (3, 4, 0))
    minor_123 = _minor_determinant(triangle_rows, (1, 2, 3))
    minor_124 = _minor_determinant(triangle_rows, (1, 2, 4))
    minor_134 = _minor_determinant(triangle_rows, (1, 3, 4))
    minor_234 = _minor_determinant(triangle_rows, (2, 3, 4))

    d0 = 4.0 * (minor_120 * minor_120 + minor_130 * minor_130 + minor_230 * minor_230)
    if np.isclose(d0, 0.0):
        return float('inf')

    d1 = -2.0 * (minor_130 * minor_340 + minor_120 * minor_240 - 2.0 * minor_123 * minor_230)
    d2 = 2.0 * (minor_120 * minor_140 - minor_230 * minor_340 - 2.0 * minor_123 * minor_130)
    d3 = 2.0 * (minor_230 * minor_240 + minor_130 * minor_140 + 2.0 * minor_123 * minor_120)
    d4 = -4.0 * (
        minor_120 * minor_124
        + minor_130 * minor_134
        + minor_230 * minor_234
        - 2.0 * minor_123 * minor_123
    )

    numerator = d1 * d1 + d2 * d2 + d3 * d3 - d0 * d4
    denominator = d0 * d0
    return float(numerator / denominator)


def _homogeneous_lifted_rows(points: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Return homogeneous lifted rows used by the historical weighted predicates."""

    points = np.asarray(points, dtype=float)
    weights = np.asarray(weights, dtype=float)
    lifted = np.sum(points * points, axis=1) - weights
    ones = np.ones((points.shape[0], 1), dtype=float)
    return np.concatenate((ones, points, lifted[:, None]), axis=1)


def _exact_minor_determinant(rows: np.ndarray, columns: tuple[int, ...]) -> int:
    """Return the exact determinant of the selected integer columns."""

    matrix = np.asarray(rows[:, columns], dtype=object)
    return exact_determinant(matrix)


def _fixed_point_lifted_rows(points: np.ndarray, radii: np.ndarray, decimals: int) -> np.ndarray:
    """Return exact fixed-point lifted rows compatible with historical predicates."""

    points_fixed = castp1_fixed_point_array(points, decimals)
    radii_fixed = castp1_fixed_point_array(radii, decimals)
    weights_fixed = radii_fixed * radii_fixed
    lifted = np.sum(points_fixed * points_fixed, axis=1) - weights_fixed
    ones = np.ones((points_fixed.shape[0], 1), dtype=object)
    return np.concatenate((ones, points_fixed, lifted[:, None]), axis=1)


def _fixed_point_lifted_rows_from_weights(
    points: np.ndarray,
    weights: np.ndarray,
    decimals: int,
) -> np.ndarray:
    """Return exact fixed-point lifted rows from point coordinates and weights."""

    points_fixed = castp1_fixed_point_array(points, decimals)
    radii = np.sqrt(np.asarray(weights, dtype=float))
    radii_fixed = castp1_fixed_point_array(radii, decimals)
    weights_fixed = radii_fixed * radii_fixed
    lifted = np.sum(points_fixed * points_fixed, axis=1) - weights_fixed
    ones = np.ones((points_fixed.shape[0], 1), dtype=object)
    return np.concatenate((ones, points_fixed, lifted[:, None]), axis=1)


def _exact_minor2(rows: np.ndarray, columns: tuple[int, int]) -> int:
    """Return an exact 2x2 minor."""

    return _exact_minor_determinant(rows, columns)


def _exact_minor3(rows: np.ndarray, columns: tuple[int, int, int]) -> int:
    """Return an exact 3x3 minor."""

    return _exact_minor_determinant(rows, columns)


def _exact_minor4(rows: np.ndarray, columns: tuple[int, int, int, int]) -> int:
    """Return an exact 4x4 minor."""

    return _exact_minor_determinant(rows, columns)


def _edge_rotation_order(edge_points: np.ndarray) -> tuple[int, int, int]:
    """Return the historical coordinate rotation used by `alf_w_hidden1`."""

    edge_points = np.asarray(edge_points, dtype=float)
    if not np.isclose(edge_points[0, 0], edge_points[1, 0]):
        return (1, 2, 3)
    if not np.isclose(edge_points[0, 1], edge_points[1, 1]):
        return (2, 3, 1)
    if not np.isclose(edge_points[0, 2], edge_points[1, 2]):
        return (3, 1, 2)
    raise ValueError('hidden1 requires two distinct edge endpoints')


def _simplex_exact_ratio(simplex_rows: np.ndarray) -> ExactRatio:
    """Return the exact weighted size3 ratio for a tetrahedron."""

    minor_4230 = _exact_minor_determinant(simplex_rows, (4, 2, 3, 0))
    minor_1430 = _exact_minor_determinant(simplex_rows, (1, 4, 3, 0))
    minor_1240 = _exact_minor_determinant(simplex_rows, (1, 2, 4, 0))
    minor_1230 = _exact_minor_determinant(simplex_rows, (1, 2, 3, 0))
    minor_1234 = _exact_minor_determinant(simplex_rows, (1, 2, 3, 4))

    numerator = (
        minor_4230 * minor_4230
        + minor_1430 * minor_1430
        + minor_1240 * minor_1240
        + 4 * minor_1230 * minor_1234
    )
    denominator = 4 * minor_1230 * minor_1230
    return ExactRatio(numerator, denominator)


def _face_exact_ratio(face_rows: np.ndarray) -> ExactRatio:
    """Return the exact weighted size2 ratio for a triangle."""

    minor_120 = _exact_minor_determinant(face_rows, (1, 2, 0))
    minor_130 = _exact_minor_determinant(face_rows, (1, 3, 0))
    minor_140 = _exact_minor_determinant(face_rows, (1, 4, 0))
    minor_230 = _exact_minor_determinant(face_rows, (2, 3, 0))
    minor_240 = _exact_minor_determinant(face_rows, (2, 4, 0))
    minor_340 = _exact_minor_determinant(face_rows, (3, 4, 0))
    minor_123 = _exact_minor_determinant(face_rows, (1, 2, 3))
    minor_124 = _exact_minor_determinant(face_rows, (1, 2, 4))
    minor_134 = _exact_minor_determinant(face_rows, (1, 3, 4))
    minor_234 = _exact_minor_determinant(face_rows, (2, 3, 4))

    d0 = 4 * (minor_120 * minor_120 + minor_130 * minor_130 + minor_230 * minor_230)
    numerator = (
        (-2 * (minor_130 * minor_340 + minor_120 * minor_240 - 2 * minor_123 * minor_230)) ** 2
        + (2 * (minor_120 * minor_140 - minor_230 * minor_340 - 2 * minor_123 * minor_130)) ** 2
        + (2 * (minor_230 * minor_240 + minor_130 * minor_140 + 2 * minor_123 * minor_120)) ** 2
        - d0
        * (
            -4
            * (
                minor_120 * minor_124
                + minor_130 * minor_134
                + minor_230 * minor_234
                - 2 * minor_123 * minor_123
            )
        )
    )
    denominator = d0 * d0
    return ExactRatio(numerator, denominator)


def _edge_exact_ratio(edge_points: np.ndarray, edge_radii: np.ndarray, decimals: int) -> ExactRatio:
    """Return the exact weighted size1 ratio for an edge."""

    edge_points_fixed = castp1_fixed_point_array(edge_points, decimals)
    edge_radii_fixed = castp1_fixed_point_array(edge_radii, decimals).reshape(-1)
    point_a = edge_points_fixed[0]
    point_b = edge_points_fixed[1]
    weight_a = int(edge_radii_fixed[0] * edge_radii_fixed[0])
    weight_b = int(edge_radii_fixed[1] * edge_radii_fixed[1])
    delta = point_b - point_a
    length2 = int(sum(component * component for component in delta))

    numerator = (length2 + weight_a - weight_b) ** 2 - 4 * length2 * weight_a
    denominator = 4 * length2
    return ExactRatio(numerator, denominator)


def _build_exact_rho_rank_tables(
    mesh: WeightedDelaunayMesh,
    atom_coordinates: np.ndarray,
    atom_radii: np.ndarray,
    simplex_rho_values: np.ndarray,
    face_rho_values: np.ndarray,
    edge_rho_map: dict[tuple[int, int], float],
    face_records: list[tuple[int, int, tuple[int, int, int]]],
) -> tuple[
    np.ndarray,
    np.ndarray,
    dict[tuple[int, int], int],
    np.ndarray,
    np.ndarray,
    tuple[ExactRatio, ...],
    int,
]:
    """Return exact rho ranks and the corresponding spectrum values."""

    decimals = _CASTP1_FIXED_DECIMALS
    lifted_rows = _fixed_point_lifted_rows(atom_coordinates, atom_radii, decimals)

    simplex_rho_ranks = np.zeros(mesh.n_simplices, dtype=int)
    face_rho_ranks = np.zeros((mesh.n_simplices, 4), dtype=int)
    edge_rho_ranks: dict[tuple[int, int], int] = {
        tuple(int(atom_index) for atom_index in edge): 0
        for edge in edge_rho_map
    }
    vertex_rho_states = np.zeros(atom_coordinates.shape[0], dtype=int)
    for edge_atom_indices in edge_rho_map:
        left, right = (int(atom_index) for atom_index in edge_atom_indices)
        if vertex_rho_states[left] >= 0:
            vertex_rho_states[left] = (
                -1
                if _weighted_hidden0(
                    atom_coordinates[left],
                    float(atom_radii[left] * atom_radii[left]),
                    atom_coordinates[right],
                    float(atom_radii[right] * atom_radii[right]),
                ) != 0
                else 1
            )
        if vertex_rho_states[right] >= 0:
            vertex_rho_states[right] = (
                -1
                if _weighted_hidden0(
                    atom_coordinates[right],
                    float(atom_radii[right] * atom_radii[right]),
                    atom_coordinates[left],
                    float(atom_radii[left] * atom_radii[left]),
                ) != 0
                else 1
            )

    vertex_rho_ranks = np.full(atom_coordinates.shape[0], -1, dtype=int)
    events: list[tuple[ExactRatio, float, str, object]] = []
    face_owners: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
    for simplex_index, face_index, face_atoms in face_records:
        face_owners.setdefault(face_atoms, []).append((int(simplex_index), int(face_index)))

    for simplex_index, simplex_atom_indices in enumerate(mesh.simplex_atom_indices):
        simplex_rows = lifted_rows[np.asarray(simplex_atom_indices, dtype=int)]
        events.append(
            (
                _simplex_exact_ratio(simplex_rows),
                float(simplex_rho_values[simplex_index]),
                'simplex',
                int(simplex_index),
            )
        )

    seen_faces: set[tuple[int, int, int]] = set()
    for simplex_index in range(mesh.n_simplices):
        for face_index in range(4):
            face_value = float(face_rho_values[simplex_index, face_index])
            if face_value == 0.0:
                continue
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            if face_atoms in seen_faces:
                continue
            seen_faces.add(face_atoms)
            face_atom_indices = np.asarray(face_atoms, dtype=int)
            face_rows = lifted_rows[face_atom_indices]
            events.append(
                (
                    _face_exact_ratio(face_rows),
                    face_value,
                    'face',
                    face_atoms,
                )
            )

    for edge_atom_indices, edge_value in edge_rho_map.items():
        if float(edge_value) == 0.0:
            continue
        edge_atom_indices_array = np.asarray(edge_atom_indices, dtype=int)
        events.append(
            (
                _edge_exact_ratio(
                    atom_coordinates[edge_atom_indices_array],
                    atom_radii[edge_atom_indices_array],
                    decimals,
                ),
                float(edge_value),
                'edge',
                tuple(int(atom_index) for atom_index in edge_atom_indices),
            )
        )

    for vertex_index, atom_radius in enumerate(np.asarray(atom_radii, dtype=float)):
        vertex_rho_state = int(vertex_rho_states[int(vertex_index)])
        if vertex_rho_state == -1:
            vertex_rho_ranks[int(vertex_index)] = 0
            continue
        if vertex_rho_state == 0:
            vertex_rho_ranks[int(vertex_index)] = -1
            continue
        scaled_radius = int(castp1_fixed_point_array(np.asarray([atom_radius]), decimals)[0])
        ratio = ExactRatio(-(scaled_radius * scaled_radius), 1)
        events.append((ratio, -float(atom_radius * atom_radius), 'vertex', int(vertex_index)))

    events.sort(key=cmp_to_key(lambda left, right: left[0].compare(right[0])))

    spectrum_values: list[float] = []
    spectrum_ratios: list[ExactRatio] = []
    current_ratio: ExactRatio | None = None
    current_rank = 0
    for ratio, float_value, kind, target in events:
        if current_ratio is None or current_ratio.compare(ratio) != 0:
            current_rank += 1
            spectrum_values.append(float(float_value))
            spectrum_ratios.append(ratio)
            current_ratio = ratio

        if kind == 'simplex':
            simplex_rho_ranks[int(target)] = int(current_rank)
        elif kind == 'face':
            for owner_simplex_index, owner_face_index in face_owners[tuple(target)]:
                face_rho_ranks[int(owner_simplex_index), int(owner_face_index)] = int(current_rank)
        elif kind == 'edge':
            edge_rho_ranks[tuple(target)] = int(current_rank)
        elif kind == 'vertex':
            vertex_rho_ranks[int(target)] = int(current_rank)

    return (
        simplex_rho_ranks,
        face_rho_ranks,
        edge_rho_ranks,
        vertex_rho_ranks,
        np.asarray(spectrum_values, dtype=float),
        tuple(spectrum_ratios),
        int(decimals),
    )


def _minor_determinant(rows: np.ndarray, columns: tuple[int, ...]) -> float:
    """Return the determinant of the selected columns."""

    matrix = np.asarray(rows[:, columns], dtype=float)
    return float(np.linalg.det(matrix))


def _weighted_hidden2(
    face_points: np.ndarray,
    face_weights: np.ndarray,
    probe_point: np.ndarray,
    probe_weight: float,
    epsilon: float = 1e-10,
) -> int:
    """Return the historical weighted attachment predicate for a triangle.

    This mirrors ``alf_w_hidden2`` from the original CAST code. The return
    value follows the original convention:

    - ``1``: attached / hidden
    - ``0``: not attached
    - ``2``: degenerate attachment, whose interpretation depends on context
    """

    all_points = np.vstack((np.asarray(face_points, dtype=float), np.asarray(probe_point, dtype=float)))
    all_weights = np.concatenate((np.asarray(face_weights, dtype=float), np.asarray([probe_weight], dtype=float)))
    decimals = _CASTP1_FIXED_DECIMALS
    rows = _fixed_point_lifted_rows_from_weights(all_points, all_weights, decimals)
    triangle_rows = rows[:3]

    minor_230 = _exact_minor3(triangle_rows, (2, 3, 0))
    minor_130 = _exact_minor3(triangle_rows, (1, 3, 0))
    minor_120 = _exact_minor3(triangle_rows, (1, 2, 0))
    minor_123 = _exact_minor3(triangle_rows, (1, 2, 3))

    expression = (
        _exact_minor4(rows, (2, 3, 4, 0)) * minor_230
        + _exact_minor4(rows, (1, 3, 4, 0)) * minor_130
        + _exact_minor4(rows, (1, 2, 4, 0)) * minor_120
        - 2 * _exact_minor4(rows, (1, 2, 3, 0)) * minor_123
    )

    if expression > 0:
        return 1
    if expression < 0:
        return 0
    return 2


def _weighted_hidden1(
    edge_points: np.ndarray,
    edge_weights: np.ndarray,
    probe_point: np.ndarray,
    probe_weight: float,
    epsilon: float = 1e-10,
) -> int:
    """Return the historical weighted attachment predicate for an edge."""

    del epsilon

    all_points = np.vstack((np.asarray(edge_points, dtype=float), np.asarray(probe_point, dtype=float)))
    all_weights = np.concatenate((np.asarray(edge_weights, dtype=float), np.asarray([probe_weight], dtype=float)))
    decimals = _CASTP1_FIXED_DECIMALS
    rows = _fixed_point_lifted_rows_from_weights(all_points, all_weights, decimals)
    edge_rows = rows[:2]
    coord1, coord2, coord3 = _edge_rotation_order(np.asarray(edge_points, dtype=float))

    result_0 = _exact_minor2(edge_rows, (coord1, 0))
    result_1 = _exact_minor2(edge_rows, (coord2, 0))
    result_2 = _exact_minor2(edge_rows, (coord3, 0))
    result_3 = _exact_minor2(edge_rows, (coord1, coord2))
    result_4 = _exact_minor2(edge_rows, (coord1, coord3))

    det_gamma = result_0 * (result_0 * result_0 + result_1 * result_1 + result_2 * result_2)

    det_lambda = (
        result_0 * _exact_minor3(rows, (coord1, 4, 0))
        + result_1 * _exact_minor3(rows, (coord2, 4, 0))
        + result_2 * _exact_minor3(rows, (coord3, 4, 0))
        - 2 * (
            result_4 * _exact_minor3(rows, (coord1, coord3, 0))
            + result_3 * _exact_minor3(rows, (coord1, coord2, 0))
        )
    )
    det_lambda = (
        result_0 * det_lambda
        + 2 * (result_3 * result_2 - result_4 * result_1) * _exact_minor3(rows, (coord2, coord3, 0))
    )

    expression = det_gamma * det_lambda

    if expression > 0:
        return 1
    if expression < 0:
        return 0
    return 2


def _weighted_hidden0(
    vertex_point: np.ndarray,
    vertex_weight: float,
    probe_point: np.ndarray,
    probe_weight: float,
) -> int:
    """Return the historical weighted attachment predicate for a vertex."""

    all_points = np.vstack((np.asarray(vertex_point, dtype=float), np.asarray(probe_point, dtype=float)))
    all_weights = np.asarray([float(vertex_weight), float(probe_weight)], dtype=float)
    decimals = _CASTP1_FIXED_DECIMALS
    points_fixed = castp1_fixed_point_array(all_points, decimals)
    radii_fixed = castp1_fixed_point_array(np.sqrt(all_weights), decimals)
    weights_fixed = radii_fixed * radii_fixed

    delta = points_fixed[1] - points_fixed[0]
    expression = int(sum(component * component for component in delta))
    expression += int(weights_fixed[0])
    expression -= int(weights_fixed[1])

    if expression < 0:
        return 1
    if expression > 0:
        return 0
    return 2


def _weighted_edge_center_and_power(
    edge_points: np.ndarray,
    edge_weights: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Return the weighted orthogonal center and power value of an edge."""

    point_a = np.asarray(edge_points[0], dtype=float)
    point_b = np.asarray(edge_points[1], dtype=float)
    weight_a = float(edge_weights[0])
    weight_b = float(edge_weights[1])
    direction = point_b - point_a
    squared_length = float(np.dot(direction, direction))

    if squared_length <= 0.0:
        center = 0.5 * (point_a + point_b)
        power_value = float(np.dot(center - point_a, center - point_a) - weight_a)
        return center, power_value

    lam = (squared_length + weight_a - weight_b) / (2.0 * squared_length)
    center = point_a + lam * direction
    power_value = float(np.dot(center - point_a, center - point_a) - weight_a)
    return center, power_value


def _edge_rho_map(
    mesh: WeightedDelaunayMesh,
    atom_coordinates: np.ndarray,
    atom_weights: np.ndarray,
) -> dict[tuple[int, int], float]:
    """Return {sorted_edge: rho_value} for every edge in the triangulation.

    Attached edges (the power-center of the edge lies inside at least one
    adjacent atom ball) get rho_value = 0.0, same as attached faces.
    Non-attached edges get their weighted circumradius² minus max-weight value.
    """

    edge_to_opposite_vertices: dict[tuple[int, int], set[int]] = {}

    for simplex_atom_indices in mesh.simplex_atom_indices:
        simplex_atom_indices = [int(atom_index) for atom_index in simplex_atom_indices]
        for first in range(4):
            for second in range(first + 1, 4):
                edge = tuple(sorted((simplex_atom_indices[first], simplex_atom_indices[second])))
                opposite_vertices = {
                    simplex_atom_indices[index]
                    for index in range(4)
                    if index not in (first, second)
                }
                edge_to_opposite_vertices.setdefault(edge, set()).update(opposite_vertices)

    result: dict[tuple[int, int], float] = {}
    for edge_atom_indices, opposite_vertices in edge_to_opposite_vertices.items():
        edge_atom_indices_array = np.asarray(edge_atom_indices, dtype=int)
        edge_points = atom_coordinates[edge_atom_indices_array]
        edge_weights = atom_weights[edge_atom_indices_array]
        attached = False
        for opposite_vertex in opposite_vertices:
            if _weighted_hidden1(
                edge_points,
                edge_weights,
                atom_coordinates[int(opposite_vertex)],
                float(atom_weights[int(opposite_vertex)]),
            ) != 0:
                attached = True
                break

        if attached:
            result[edge_atom_indices] = 0.0
        else:
            _edge_center, edge_power_value = _weighted_edge_center_and_power(edge_points, edge_weights)
            result[edge_atom_indices] = float(edge_power_value)

    return result


def _edge_mu_rank_maps(
    mesh: WeightedDelaunayMesh,
    face_rho_ranks: np.ndarray,
    face_mu1_ranks: np.ndarray,
    face_mu2_ranks: np.ndarray,
    face_is_on_hull: np.ndarray,
) -> tuple[dict[tuple[int, int], int], dict[tuple[int, int], int]]:
    """Return edge mu1/mu2 ranks induced by the historical face-to-edge rules."""

    edge_mu1_ranks: dict[tuple[int, int], int] = {}
    edge_mu2_ranks: dict[tuple[int, int], int] = {}

    hull_edges: set[tuple[int, int]] = set()

    for simplex_index in range(mesh.n_simplices):
        for face_index in range(4):
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            face_rho_rank = int(face_rho_ranks[simplex_index, face_index])
            face_mu1_rank = int(face_mu1_ranks[simplex_index, face_index])
            face_mu2_rank = int(face_mu2_ranks[simplex_index, face_index])

            face_edges = (
                tuple(sorted((face_atoms[0], face_atoms[1]))),
                tuple(sorted((face_atoms[0], face_atoms[2]))),
                tuple(sorted((face_atoms[1], face_atoms[2]))),
            )
            for edge in face_edges:
                candidate_mu1 = face_rho_rank if face_rho_rank != 0 else face_mu1_rank
                previous_mu1 = edge_mu1_ranks.get(edge)
                if previous_mu1 is None or candidate_mu1 < previous_mu1:
                    edge_mu1_ranks[edge] = int(candidate_mu1)

                previous_mu2 = edge_mu2_ranks.get(edge, 0)
                if int(face_mu2_rank) > int(previous_mu2):
                    edge_mu2_ranks[edge] = int(face_mu2_rank)

            if bool(face_is_on_hull[simplex_index, face_index]):
                for edge in face_edges:
                    hull_edges.add(edge)

    for edge in hull_edges:
        edge_mu2_ranks[edge] = 0

    return edge_mu1_ranks, edge_mu2_ranks


def _vertex_mu_rank_arrays(
    mesh: WeightedDelaunayMesh,
    edge_rho_ranks: dict[tuple[int, int], int],
    edge_mu1_ranks: dict[tuple[int, int], int],
    edge_mu2_ranks: dict[tuple[int, int], int],
    face_is_on_hull: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return vertex rho/mu1/mu2 ranks following the historical edge-to-vertex rules."""

    n_vertices = int(mesh.points.shape[0])
    vertex_rho_ranks = np.ones(n_vertices, dtype=int)
    vertex_mu1_ranks = np.zeros(n_vertices, dtype=int)
    vertex_mu2_ranks = np.zeros(n_vertices, dtype=int)

    for edge, edge_rho_rank in edge_rho_ranks.items():
        edge = tuple(int(atom_index) for atom_index in edge)
        edge_mu1_rank = int(edge_mu1_ranks.get(edge, 0))
        edge_mu2_rank = int(edge_mu2_ranks.get(edge, 0))
        candidate_mu1 = int(edge_rho_rank) if int(edge_rho_rank) != 0 else int(edge_mu1_rank)
        for vertex_index in edge:
            previous_mu1 = int(vertex_mu1_ranks[vertex_index])
            if previous_mu1 == 0 or (candidate_mu1 != 0 and candidate_mu1 < previous_mu1):
                vertex_mu1_ranks[vertex_index] = int(candidate_mu1)
            if edge_mu2_rank > int(vertex_mu2_ranks[vertex_index]):
                vertex_mu2_ranks[vertex_index] = int(edge_mu2_rank)

    for simplex_index in range(mesh.n_simplices):
        for face_index in range(4):
            if not bool(face_is_on_hull[simplex_index, face_index]):
                continue
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            for vertex_index in face_atoms:
                vertex_mu2_ranks[int(vertex_index)] = 0

    return vertex_rho_ranks, vertex_mu1_ranks, vertex_mu2_ranks


def _build_spectrum_values(*rho_value_arrays: np.ndarray) -> np.ndarray:
    """Return the historical spectrum support built from rho events only."""

    nonzero_values = []
    for values in rho_value_arrays:
        values_array = np.asarray(values, dtype=float).reshape(-1)
        if values_array.size == 0:
            continue
        filtered_values = values_array[np.abs(values_array) > 1e-12]
        if filtered_values.size:
            nonzero_values.append(filtered_values)

    if not nonzero_values:
        return np.asarray([0.0], dtype=float)

    return np.unique(np.concatenate(nonzero_values))


def _face_rho_data(
    mesh: WeightedDelaunayMesh,
    atom_coordinates: np.ndarray,
    atom_weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return face rho values, using 0.0 for attached triangles.

    Attachment criterion (matching ``spectrum_triangle`` in the C reference):
    a face is attached iff ``alf_hidden2(face, L) OR alf_hidden2(face, R)``,
    where L and R are the opposite vertices of the two adjacent tetrahedra.

    This is equivalent to asking: is the power-center of the face on the
    *inside* of the molecule with respect to at least one of its two flanking
    tetrahedra?  The criterion is strictly more permissive than ``size2 <= 0``:
    a face can have positive size2 and still be attached if either opposite
    vertex lies inside its power sphere.
    """

    face_rho_values = np.zeros((mesh.n_simplices, 4), dtype=float)
    face_centers = np.zeros((mesh.n_simplices, 4, 3), dtype=float)
    face_rho_map: dict[tuple[int, int, int], float] = {}
    face_center_map: dict[tuple[int, int, int], np.ndarray] = {}

    for simplex_index, simplex_neighbors in enumerate(mesh.neighbors):
        simplex_atoms = mesh.simplex_atom_indices[simplex_index]
        for face_index, neighbor in enumerate(simplex_neighbors):
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            if face_atoms in face_rho_map:
                face_rho_values[simplex_index, face_index] = face_rho_map[face_atoms]
                face_centers[simplex_index, face_index] = face_center_map[face_atoms]
                continue

            face_atom_indices = np.asarray(face_atoms, dtype=int)
            face_points = atom_coordinates[face_atom_indices]
            face_weights = atom_weights[face_atom_indices]
            face_center, _face_power_value = _weighted_face_center_and_power(face_points, face_weights)
            face_size2_value = _weighted_face_size2_value(face_points, face_weights)

            # Attachment criterion: hidden2(L) OR hidden2(R), where L is the
            # opposite vertex in the current simplex and R is the opposite vertex
            # in the neighbor simplex (if it exists).  This matches the C code:
            #   is_attached = alf_hidden2(i,j,k,L) or alf_hidden2(i,j,k,R)
            # in spectrum_triangle().
            opp_L = int(next(a for a in simplex_atoms if a not in face_atoms))
            is_attached = (
                _weighted_hidden2(
                    face_points, face_weights,
                    atom_coordinates[opp_L], float(atom_weights[opp_L]),
                ) != 0
            )
            if not is_attached and neighbor != -1:
                neighbor_atoms = mesh.simplex_atom_indices[int(neighbor)]
                opp_R = int(next(a for a in neighbor_atoms if a not in face_atoms))
                is_attached = (
                    _weighted_hidden2(
                        face_points, face_weights,
                        atom_coordinates[opp_R], float(atom_weights[opp_R]),
                    ) != 0
                )

            rho = 0.0 if is_attached else float(face_size2_value)
            face_rho_map[face_atoms] = rho
            face_center_map[face_atoms] = np.asarray(face_center, dtype=float)
            face_rho_values[simplex_index, face_index] = rho
            face_centers[simplex_index, face_index] = face_center_map[face_atoms]

    return face_rho_values, face_centers


def _point_in_tetrahedron(
    point: np.ndarray,
    tetrahedron_points: np.ndarray,
    epsilon: float = 1e-8,
) -> bool:
    """Return whether a point lies inside or on a tetrahedron."""

    point_a, point_b, point_c, point_d = tetrahedron_points
    matrix = np.column_stack((point_b - point_a, point_c - point_a, point_d - point_a))
    try:
        barycentric = np.linalg.solve(matrix, point - point_a)
    except np.linalg.LinAlgError:
        return False

    coordinate_u, coordinate_v, coordinate_w = barycentric
    coordinate_t = 1.0 - coordinate_u - coordinate_v - coordinate_w
    coordinates = np.array([coordinate_t, coordinate_u, coordinate_v, coordinate_w], dtype=float)
    return bool(np.all(coordinates >= -epsilon) and np.all(coordinates <= 1.0 + epsilon))


def build_castp_geometry(
    molecular_system,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    solvent_radius: float = 1.4,
    radii_model: str = 'castp_param',
    discard_redundant_vertices: bool = True,
    atom_radii_override: np.ndarray | None = None,
    alpha_boundary_epsilon_length: float = 0.0,
) -> CastpGeometry:
    """Build the weighted geometric substrate used by the native CASTp path."""

    molsys = msm.convert(molecular_system, to_form='molsysmt.MolSys', structure_indices=structure_indices)
    atom_indices = msm.select(molsys, selection=selection)

    atom_coordinates = puw.get_value(
        msm.get(molsys, selection=atom_indices, coordinates=True),
        to_unit='angstroms',
    )[0]
    atom_group_names = np.asarray(
        msm.get(molsys, selection=atom_indices, group_name=True),
        dtype=object,
    )
    atom_names = np.asarray(
        msm.get(molsys, selection=atom_indices, atom_name=True),
        dtype=object,
    )
    atom_types = np.asarray(
        msm.get(molsys, selection=atom_indices, atom_type=True),
        dtype=object,
    )
    atom_n_bonds = np.asarray(
        msm.get(molsys, selection=atom_indices, n_bonds=True),
        dtype=int,
    )
    if atom_radii_override is not None:
        atom_radii = np.asarray(atom_radii_override, dtype=float)
        if atom_radii.shape[0] != atom_coordinates.shape[0]:
            raise ValueError('atom_radii_override must match the selected atom count.')
    elif radii_model == 'castp1_pdb2alf':
        pdb_path = _path_like_or_none(molecular_system)
        if pdb_path is None:
            atom_radii = _castp_param_radii_for_labels(atom_group_names, atom_names)
        else:
            pdb_atom_radii = _castp1_pdb2alf_radii_for_pdb_path(pdb_path)
            if pdb_atom_radii.shape[0] == atom_coordinates.shape[0]:
                atom_radii = pdb_atom_radii
            elif pdb_atom_radii.shape[0] > int(np.max(atom_indices)):
                atom_radii = pdb_atom_radii[np.asarray(atom_indices, dtype=int)]
            else:
                raise ValueError(
                    'PDB2ALF radii count is incompatible with the selected atom indices.'
                )
        atom_radii = atom_radii + float(solvent_radius)
    elif radii_model == 'castp_param':
        atom_radii = _castp_param_radii_for_labels(atom_group_names, atom_names)
        atom_radii = atom_radii + float(solvent_radius)
    elif radii_model == 'protor':
        atom_radii = _protor_radii_for_labels(atom_group_names, atom_names, atom_types, atom_n_bonds)
        atom_radii = atom_radii + float(solvent_radius)
    else:
        raise ValueError(f'Unsupported CASTp radii model: {radii_model}')

    alpha_boundary_epsilon_length = float(alpha_boundary_epsilon_length)
    if alpha_boundary_epsilon_length < 0.0:
        raise ValueError('alpha_boundary_epsilon_length must be non-negative.')
    if alpha_boundary_epsilon_length:
        atom_radii = np.asarray(atom_radii, dtype=float) - alpha_boundary_epsilon_length
        if np.any(atom_radii <= 0.0):
            raise ValueError(
                'alpha_boundary_epsilon_length makes at least one effective radius '
                'non-positive.'
            )

    atom_coordinates, atom_radii, atom_indices = _deduplicate_weighted_points(
        atom_coordinates,
        atom_radii,
        np.asarray(atom_indices, dtype=int),
    )
    if bool(discard_redundant_vertices):
        atom_coordinates, atom_radii, atom_indices = _discard_redundant_weighted_points(
            atom_coordinates,
            atom_radii,
            atom_indices,
        )

    if atom_coordinates.shape[0] < 4:
        raise ValueError('Not enough atoms to build a CASTp weighted triangulation (min 4).')

    mesh = WeightedDelaunayMesh(
        points=atom_coordinates,
        weights=np.asarray(atom_radii * atom_radii, dtype=float),
        atom_radii=atom_radii,
    )

    simplex_regular_mask = np.zeros(mesh.n_simplices, dtype=bool)
    for simplex_index, simplex_atom_indices in enumerate(mesh.simplex_atom_indices):
        tetrahedron_points = atom_coordinates[simplex_atom_indices]
        simplex_regular_mask[simplex_index] = _point_in_tetrahedron(
            mesh.simplex_centers[simplex_index],
            tetrahedron_points,
        )

    face_rho_values, face_centers = _face_rho_data(mesh, atom_coordinates, np.asarray(mesh.weights, dtype=float))
    edge_rho_map = _edge_rho_map(mesh, atom_coordinates, np.asarray(mesh.weights, dtype=float))
    face_is_on_hull, face_records = _face_rank_data(mesh)
    (
        simplex_rho_ranks,
        face_rho_ranks,
        edge_rho_ranks,
        vertex_rho_ranks,
        spectrum_values,
        spectrum_ratios,
        spectrum_decimals,
    ) = _build_exact_rho_rank_tables(
        mesh,
        atom_coordinates,
        atom_radii,
        np.asarray(mesh.simplex_power_values, dtype=float),
        face_rho_values,
        edge_rho_map,
        face_records,
    )

    face_to_incident_simplex_ranks: dict[tuple[int, int, int], list[int]] = {}
    for simplex_index, face_index, face_atoms in face_records:
        face_to_incident_simplex_ranks.setdefault(face_atoms, []).append(
            int(simplex_rho_ranks[int(simplex_index)])
        )

    face_mu1_ranks = np.zeros((mesh.n_simplices, 4), dtype=int)
    face_mu2_ranks = np.zeros((mesh.n_simplices, 4), dtype=int)
    for simplex_index, face_index, face_atoms in face_records:
        incident_simplex_ranks = face_to_incident_simplex_ranks[face_atoms]
        face_mu1_ranks[int(simplex_index), int(face_index)] = int(min(incident_simplex_ranks))
        if not bool(face_is_on_hull[int(simplex_index), int(face_index)]):
            face_mu2_ranks[int(simplex_index), int(face_index)] = int(max(incident_simplex_ranks))

    base_rank = _rank_of_ratio(spectrum_ratios, ExactRatio(0, 1))
    edge_mu1_ranks, edge_mu2_ranks = _edge_mu_rank_maps(
        mesh,
        face_rho_ranks,
        face_mu1_ranks,
        face_mu2_ranks,
        face_is_on_hull,
    )
    _vertex_rho_ranks_unused, vertex_mu1_ranks, vertex_mu2_ranks = _vertex_mu_rank_arrays(
        mesh,
        edge_rho_ranks,
        edge_mu1_ranks,
        edge_mu2_ranks,
        face_is_on_hull,
    )
    master_entries, master_rank_offsets, simplex_rank_sublists = _build_master_entries(
        simplex_rho_ranks,
        face_rho_ranks,
        face_mu1_ranks,
        face_mu2_ranks,
        edge_rho_ranks,
        edge_mu1_ranks,
        edge_mu2_ranks,
        vertex_rho_ranks,
        vertex_mu1_ranks,
        vertex_mu2_ranks,
        face_records,
    )

    return CastpGeometry(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        solvent_radius=float(solvent_radius),
        radii_model=str(radii_model),
        atom_indices_map=np.asarray(atom_indices, dtype=int),
        atom_coordinates=np.asarray(atom_coordinates, dtype=float),
        atom_radii=np.asarray(atom_radii, dtype=float),
        mesh=mesh,
        simplex_regular_mask=np.asarray(simplex_regular_mask, dtype=bool),
        spectrum_values=np.asarray(spectrum_values, dtype=float),
        spectrum_ratios=tuple(spectrum_ratios),
        spectrum_decimals=int(spectrum_decimals),
        base_rank=int(base_rank),
        simplex_rho_ranks=np.asarray(simplex_rho_ranks, dtype=int),
        simplex_rank_sublists=dict(simplex_rank_sublists),
        master_entries=list(master_entries),
        master_rank_offsets=dict(master_rank_offsets),
        face_rho_values=np.asarray(face_rho_values, dtype=float),
        face_centers=np.asarray(face_centers, dtype=float),
        face_rho_ranks=np.asarray(face_rho_ranks, dtype=int),
        face_mu1_ranks=np.asarray(face_mu1_ranks, dtype=int),
        face_mu2_ranks=np.asarray(face_mu2_ranks, dtype=int),
        face_is_on_hull=np.asarray(face_is_on_hull, dtype=bool),
        face_records=list(face_records),
        edge_rho_ranks=edge_rho_ranks,
        edge_mu1_ranks=edge_mu1_ranks,
        edge_mu2_ranks=edge_mu2_ranks,
        vertex_rho_ranks=np.asarray(vertex_rho_ranks, dtype=int),
        vertex_mu1_ranks=np.asarray(vertex_mu1_ranks, dtype=int),
        vertex_mu2_ranks=np.asarray(vertex_mu2_ranks, dtype=int),
    )
