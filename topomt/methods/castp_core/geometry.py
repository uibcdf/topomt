"""Canonical weighted geometry substrate for the native CASTp implementation."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import molsysmt as msm
import numpy as np

from topomt import pyunitwizard as puw
from topomt.weighted_delaunay_mesh import WeightedDelaunayMesh


_CASTP_PARAM_PATH = Path(__file__).resolve().parents[2] / 'data' / 'castp' / 'param.dat'
_CASTP_DEFAULT_HEAVY_RADIUS = 1.8
_CASTP_DEFAULT_HYDROGEN_RADIUS = 1.2
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
_PROTOR_STANDARD_PROTEIN_TYPES = {
    'ALA': {'CB': 'C4H3'},
    'ARG': {'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C4H2', 'NE': 'N3H1', 'CZ': 'C3H0', 'NH1': 'N3H2', 'NH2': 'N3H2'},
    'ASN': {'CB': 'C4H2', 'CG': 'C3H0', 'OD1': 'O1H0', 'ND2': 'N3H2'},
    'ASP': {'CB': 'C4H2', 'CG': 'C3H0', 'OD1': 'O1H0', 'OD2': 'O1H0'},
    'CYS': {'CB': 'C4H2'},
    'GLN': {'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C3H0', 'OE1': 'O1H0', 'NE2': 'N3H2'},
    'GLU': {'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C3H0', 'OE1': 'O1H0', 'OE2': 'O1H0'},
    'GLY': {},
    'HIS': {'CB': 'C4H2', 'CG': 'C3H0', 'ND1': 'N3H0', 'CD2': 'C3H1', 'CE1': 'C3H1', 'NE2': 'N3H0'},
    'HID': {'CB': 'C4H2', 'CG': 'C3H0', 'ND1': 'N3H1', 'CD2': 'C3H1', 'CE1': 'C3H1', 'NE2': 'N3H0'},
    'HIE': {'CB': 'C4H2', 'CG': 'C3H0', 'ND1': 'N3H0', 'CD2': 'C3H1', 'CE1': 'C3H1', 'NE2': 'N3H1'},
    'HIP': {'CB': 'C4H2', 'CG': 'C3H0', 'ND1': 'N3H1', 'CD2': 'C3H1', 'CE1': 'C3H1', 'NE2': 'N3H1'},
    'ILE': {'CB': 'C4H1', 'CG1': 'C4H2', 'CG2': 'C4H3', 'CD1': 'C4H3'},
    'LEU': {'CB': 'C4H2', 'CG': 'C4H1', 'CD1': 'C4H3', 'CD2': 'C4H3'},
    'LYS': {'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C4H2', 'CE': 'C4H2', 'NZ': 'N4H3'},
    'MET': {'CB': 'C4H2', 'CG': 'C4H2', 'SD': 'S2H0', 'CE': 'C4H3'},
    'PHE': {'CB': 'C4H2', 'CG': 'C3H0', 'CD1': 'C3H1', 'CD2': 'C3H1', 'CE1': 'C3H1', 'CE2': 'C3H1', 'CZ': 'C3H1'},
    'PRO': {'CB': 'C4H2', 'CG': 'C4H2', 'CD': 'C4H2'},
    'SER': {'CB': 'C4H2', 'OG': 'O2H1'},
    'THR': {'CB': 'C4H1', 'OG1': 'O2H1', 'CG2': 'C4H3'},
    'TRP': {'CB': 'C4H2', 'CG': 'C3H0', 'CD1': 'C3H1', 'CD2': 'C3H0', 'NE1': 'N3H1', 'CE2': 'C3H0', 'CE3': 'C3H1', 'CZ2': 'C3H1', 'CZ3': 'C3H1', 'CH2': 'C3H1'},
    'TYR': {'CB': 'C4H2', 'CG': 'C3H0', 'CD1': 'C3H1', 'CD2': 'C3H1', 'CE1': 'C3H1', 'CE2': 'C3H1', 'CZ': 'C3H0', 'OH': 'O2H1'},
    'VAL': {'CB': 'C4H1', 'CG1': 'C4H3', 'CG2': 'C4H3'},
}


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
    base_rank: int
    simplex_rho_values: np.ndarray
    simplex_rho_ranks: np.ndarray
    face_rho_values: np.ndarray
    face_centers: np.ndarray
    face_rho_ranks: np.ndarray
    face_mu1_values: np.ndarray
    face_mu1_ranks: np.ndarray
    face_mu2_values: np.ndarray
    face_mu2_ranks: np.ndarray
    face_is_on_hull: np.ndarray
    face_records: list[tuple[int, int, tuple[int, int, int]]]


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

    if atom_name == 'N':
        if residue_name == 'PRO':
            return 'N3H0'
        if n_bonds <= 1:
            return 'N3H2'
        if n_bonds == 2:
            return 'N3H1'
        return 'N3H0'

    if atom_name == 'CA':
        return 'C4H2' if residue_name == 'GLY' else 'C4H1'
    if atom_name == 'C':
        return 'C3H0'
    if atom_name == 'O':
        return 'O1H0'
    if atom_name == 'OXT':
        return 'O2H1'

    residue_map = _PROTOR_STANDARD_PROTEIN_TYPES.get(residue_name)
    if residue_map is not None and atom_name in residue_map:
        mapped_type = residue_map[atom_name]
        if atom_name == 'SG':
            return 'S2H1' if n_bonds <= 1 else 'S2H0'
        return mapped_type

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


def _rank_from_values(values: np.ndarray) -> np.ndarray:
    """Return 1-based ranks for strictly increasing unique values."""

    unique_values = np.unique(np.asarray(values, dtype=float))
    value_to_rank = {float(value): rank for rank, value in enumerate(unique_values, start=1)}
    return np.asarray([value_to_rank[float(value)] for value in values], dtype=int)


def _rank_of_value(spectrum_values: np.ndarray, value: float) -> int:
    """Return the 1-based MKALF-like rank of a threshold value."""

    spectrum_values = np.asarray(spectrum_values, dtype=float)
    if spectrum_values.size == 0:
        return 1
    if value <= float(spectrum_values[0]):
        return 1
    if value >= float(spectrum_values[-1]):
        return int(spectrum_values.size)
    return int(np.searchsorted(spectrum_values, value, side='right'))


def _face_rank_data(mesh: WeightedDelaunayMesh) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[tuple[int, int, tuple[int, int, int]]]]:
    """Return face-level mu values and hull flags induced by simplex rho values."""

    face_to_incident_simplices: dict[tuple[int, int, int], list[int]] = {}
    face_records: list[tuple[int, int, tuple[int, int, int]]] = []

    for simplex_index, simplex_neighbors in enumerate(mesh.neighbors):
        for face_index, neighbor in enumerate(simplex_neighbors):
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            face_to_incident_simplices.setdefault(face_atoms, []).append(int(simplex_index))
            face_records.append((int(simplex_index), int(face_index), face_atoms))

    face_mu1_map: dict[tuple[int, int, int], float] = {}
    face_mu2_map: dict[tuple[int, int, int], float] = {}
    face_is_on_hull_map: dict[tuple[int, int, int], bool] = {}
    simplex_rho_values = np.asarray(mesh.radii, dtype=float)

    for face_atoms, simplex_indices in face_to_incident_simplices.items():
        incident_rho_values = simplex_rho_values[np.asarray(simplex_indices, dtype=int)]
        face_mu1_map[face_atoms] = float(np.min(incident_rho_values))
        face_mu2_map[face_atoms] = 0.0 if len(simplex_indices) == 1 else float(np.max(incident_rho_values))
        face_is_on_hull_map[face_atoms] = len(simplex_indices) == 1

    face_mu1_values = np.empty((mesh.n_simplices, 4), dtype=float)
    face_mu2_values = np.empty((mesh.n_simplices, 4), dtype=float)
    face_is_on_hull = np.zeros((mesh.n_simplices, 4), dtype=bool)

    for simplex_index, simplex_neighbors in enumerate(mesh.neighbors):
        for face_index, _neighbor in enumerate(simplex_neighbors):
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            face_mu1_values[simplex_index, face_index] = face_mu1_map[face_atoms]
            face_mu2_values[simplex_index, face_index] = face_mu2_map[face_atoms]
            face_is_on_hull[simplex_index, face_index] = face_is_on_hull_map[face_atoms]

    return face_mu1_values, face_mu2_values, face_is_on_hull, face_records


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

    rows = _homogeneous_lifted_rows(
        np.vstack((np.asarray(face_points, dtype=float), np.asarray(probe_point, dtype=float))),
        np.concatenate((np.asarray(face_weights, dtype=float), np.asarray([probe_weight], dtype=float))),
    )
    triangle_rows = rows[:3]

    minor_230 = _minor_determinant(triangle_rows, (2, 3, 0))
    minor_130 = _minor_determinant(triangle_rows, (1, 3, 0))
    minor_120 = _minor_determinant(triangle_rows, (1, 2, 0))
    minor_123 = _minor_determinant(triangle_rows, (1, 2, 3))

    expression = (
        _minor_determinant(rows, (2, 3, 4, 0)) * minor_230
        + _minor_determinant(rows, (1, 3, 4, 0)) * minor_130
        + _minor_determinant(rows, (1, 2, 4, 0)) * minor_120
        - 2.0 * _minor_determinant(rows, (1, 2, 3, 0)) * minor_123
    )

    if expression > epsilon:
        return 1
    if expression < -epsilon:
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


def _edge_rho_values(
    mesh: WeightedDelaunayMesh,
    atom_coordinates: np.ndarray,
    atom_weights: np.ndarray,
) -> np.ndarray:
    """Return weighted rho values for non-attached edges."""

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

    rho_values = []
    for edge_atom_indices, opposite_vertices in edge_to_opposite_vertices.items():
        edge_atom_indices_array = np.asarray(edge_atom_indices, dtype=int)
        edge_points = atom_coordinates[edge_atom_indices_array]
        edge_weights = atom_weights[edge_atom_indices_array]
        edge_center, edge_power_value = _weighted_edge_center_and_power(edge_points, edge_weights)

        attached = False
        for opposite_vertex in opposite_vertices:
            opposite_power = float(
                np.dot(
                    edge_center - atom_coordinates[int(opposite_vertex)],
                    edge_center - atom_coordinates[int(opposite_vertex)],
                )
                - atom_weights[int(opposite_vertex)]
            )
            if opposite_power < 0.0 or np.isclose(opposite_power, 0.0):
                attached = True
                break

        if not attached and not np.isclose(edge_power_value, 0.0):
            rho_values.append(float(edge_power_value))

    return np.asarray(rho_values, dtype=float)


def _face_rho_data(
    mesh: WeightedDelaunayMesh,
    atom_coordinates: np.ndarray,
    atom_weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return face rho values, using 0.0 for attached triangles."""

    face_rho_values = np.zeros((mesh.n_simplices, 4), dtype=float)
    face_centers = np.zeros((mesh.n_simplices, 4, 3), dtype=float)
    face_rho_map: dict[tuple[int, int, int], float] = {}
    face_center_map: dict[tuple[int, int, int], np.ndarray] = {}

    for simplex_index, simplex_neighbors in enumerate(mesh.neighbors):
        simplex_atom_indices = mesh.simplex_atom_indices[simplex_index]
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

            attached = False
            opposite_atom_index = next(
                int(atom_index)
                for atom_index in simplex_atom_indices
                if int(atom_index) not in face_atom_indices
            )
            opposite_hidden = _weighted_hidden2(
                face_points,
                face_weights,
                atom_coordinates[opposite_atom_index],
                atom_weights[opposite_atom_index],
            )
            if opposite_hidden:
                attached = True

            if neighbor != -1:
                neighbor_atom_indices = mesh.simplex_atom_indices[int(neighbor)]
                neighbor_extra_atom = next(
                    int(atom_index)
                    for atom_index in neighbor_atom_indices
                    if int(atom_index) not in face_atom_indices
                )
                neighbor_hidden = _weighted_hidden2(
                    face_points,
                    face_weights,
                    atom_coordinates[neighbor_extra_atom],
                    atom_weights[neighbor_extra_atom],
                )
                if neighbor_hidden:
                    attached = True

            face_rho_map[face_atoms] = 0.0 if attached else float(face_size2_value)
            face_center_map[face_atoms] = np.asarray(face_center, dtype=float)
            face_rho_values[simplex_index, face_index] = face_rho_map[face_atoms]
            face_centers[simplex_index, face_index] = face_center_map[face_atoms]

    for simplex_index, simplex_neighbors in enumerate(mesh.neighbors):
        for face_index, _neighbor in enumerate(simplex_neighbors):
            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            face_rho_values[simplex_index, face_index] = face_rho_map[face_atoms]
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
    selection: str = 'molecule_type == "protein"',
    structure_indices: int | list[int] = 0,
    solvent_radius: float = 1.4,
    radii_model: str = 'protor',
) -> CastpGeometry:
    """Build the weighted geometric substrate used by the native CASTp path."""

    molsys = msm.convert(molecular_system, to_form='molsysmt.MolSys', structure_indices=structure_indices)
    atom_indices_selection = msm.select(molsys, selection=selection)
    atom_indices_heavy = msm.select(molsys, selection='atom_type != "H"', mask=atom_indices_selection)

    atom_coordinates = puw.get_value(
        msm.get(molsys, selection=atom_indices_heavy, coordinates=True),
        to_unit='angstroms',
    )[0]
    atom_group_names = np.asarray(
        msm.get(molsys, selection=atom_indices_heavy, group_name=True),
        dtype=object,
    )
    atom_names = np.asarray(
        msm.get(molsys, selection=atom_indices_heavy, atom_name=True),
        dtype=object,
    )
    atom_types = np.asarray(
        msm.get(molsys, selection=atom_indices_heavy, atom_type=True),
        dtype=object,
    )
    atom_n_bonds = np.asarray(
        msm.get(molsys, selection=atom_indices_heavy, n_bonds=True),
        dtype=int,
    )
    if radii_model == 'castp_param':
        atom_radii = _castp_param_radii_for_labels(atom_group_names, atom_names)
    elif radii_model == 'protor':
        atom_radii = _protor_radii_for_labels(atom_group_names, atom_names, atom_types, atom_n_bonds)
    else:
        raise ValueError(f'Unsupported CASTp radii model: {radii_model}')
    atom_radii = atom_radii + float(solvent_radius)

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
    simplex_rho_values = np.asarray(mesh.simplex_power_values, dtype=float)
    edge_rho_values = _edge_rho_values(mesh, atom_coordinates, np.asarray(mesh.weights, dtype=float))
    vertex_rho_values = -np.asarray(mesh.weights, dtype=float)
    rho_spectrum_source = np.concatenate(
        (
            simplex_rho_values[np.abs(simplex_rho_values) > 1e-12],
            face_rho_values[np.abs(face_rho_values) > 1e-12].reshape(-1),
            edge_rho_values[np.abs(edge_rho_values) > 1e-12],
            vertex_rho_values[np.abs(vertex_rho_values) > 1e-12],
        )
    )
    spectrum_values = np.unique(np.asarray(rho_spectrum_source, dtype=float))
    if spectrum_values.size == 0:
        spectrum_values = np.asarray([0.0], dtype=float)

    simplex_rho_ranks = np.asarray(
        [_rank_of_value(spectrum_values, float(value)) for value in simplex_rho_values],
        dtype=int,
    )
    face_rho_ranks = np.zeros((mesh.n_simplices, 4), dtype=int)
    non_attached_face_mask = np.abs(face_rho_values) > 1e-12
    face_rho_ranks[non_attached_face_mask] = np.asarray(
        [
            _rank_of_value(spectrum_values, float(value))
            for value in face_rho_values[non_attached_face_mask]
        ],
        dtype=int,
    )

    face_mu1_values, face_mu2_values, face_is_on_hull, face_records = _face_rank_data(mesh)
    face_mu1_ranks = np.asarray(
        [[int(np.min(simplex_rho_ranks[[simplex_index, int(neighbor)]]))
          if neighbor != -1 else int(simplex_rho_ranks[simplex_index])
          for face_index, neighbor in enumerate(mesh.neighbors[simplex_index])]
         for simplex_index in range(mesh.n_simplices)],
        dtype=int,
    )
    face_mu2_ranks = np.asarray(
        [[0 if face_is_on_hull[simplex_index, face_index]
          else int(np.max(simplex_rho_ranks[[simplex_index, int(neighbor)]]))
          for face_index, neighbor in enumerate(mesh.neighbors[simplex_index])]
         for simplex_index in range(mesh.n_simplices)],
        dtype=int,
    )
    base_rank = _rank_of_value(spectrum_values, 0.0)

    return CastpGeometry(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        solvent_radius=float(solvent_radius),
        radii_model=str(radii_model),
        atom_indices_map=np.asarray(atom_indices_heavy, dtype=int),
        atom_coordinates=np.asarray(atom_coordinates, dtype=float),
        atom_radii=np.asarray(atom_radii, dtype=float),
        mesh=mesh,
        simplex_regular_mask=np.asarray(simplex_regular_mask, dtype=bool),
        spectrum_values=np.asarray(spectrum_values, dtype=float),
        base_rank=int(base_rank),
        simplex_rho_values=np.asarray(simplex_rho_values, dtype=float),
        simplex_rho_ranks=np.asarray(simplex_rho_ranks, dtype=int),
        face_rho_values=np.asarray(face_rho_values, dtype=float),
        face_centers=np.asarray(face_centers, dtype=float),
        face_rho_ranks=np.asarray(face_rho_ranks, dtype=int),
        face_mu1_values=np.asarray(face_mu1_values, dtype=float),
        face_mu1_ranks=np.asarray(face_mu1_ranks, dtype=int),
        face_mu2_values=np.asarray(face_mu2_values, dtype=float),
        face_mu2_ranks=np.asarray(face_mu2_ranks, dtype=int),
        face_is_on_hull=np.asarray(face_is_on_hull, dtype=bool),
        face_records=list(face_records),
    )
