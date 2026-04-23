"""Weighted Delaunay / regular-triangulation substrate for TopoMT."""

import numpy as np
from scipy.spatial import ConvexHull

from topomt import pyunitwizard as puw
from topomt.delaunay_mesh import (
    _SIMPLEX_FACE_LOCAL_INDICES,
    _tetrahedron_condition_numbers,
    _tetrahedron_edge_extrema,
    _tetrahedron_volumes,
)


def _build_neighbors_from_simplices(simplices: np.ndarray) -> np.ndarray:
    """Return simplex neighbors induced by shared triangular faces."""

    neighbors = np.full((simplices.shape[0], 4), -1, dtype=int)
    face_owner: dict[tuple[int, int, int], tuple[int, int]] = {}

    for simplex_index, simplex in enumerate(simplices):
        for face_index, local_indices in enumerate(_SIMPLEX_FACE_LOCAL_INDICES):
            face = tuple(sorted(int(simplex[local_index]) for local_index in local_indices))
            previous = face_owner.get(face)
            if previous is None:
                face_owner[face] = (int(simplex_index), int(face_index))
                continue

            previous_simplex_index, previous_face_index = previous
            neighbors[simplex_index, face_index] = previous_simplex_index
            neighbors[previous_simplex_index, previous_face_index] = simplex_index

    return neighbors


def _orient_simplex_vertices(simplex: np.ndarray, points: np.ndarray) -> np.ndarray:
    """Return a positively oriented tetrahedron vertex order."""

    oriented_simplex = np.asarray(simplex, dtype=int).copy()
    tetrahedron_points = points[oriented_simplex]
    orientation = np.linalg.det(
        np.vstack(
            (
                tetrahedron_points[1] - tetrahedron_points[0],
                tetrahedron_points[2] - tetrahedron_points[0],
                tetrahedron_points[3] - tetrahedron_points[0],
            )
        )
    )

    if orientation < 0.0:
        oriented_simplex[[0, 1]] = oriented_simplex[[1, 0]]

    return oriented_simplex


def _oriented_face_local_indices(face_index: int) -> tuple[int, int, int]:
    """Return the outward-oriented local vertex order of a tetrahedron face.

    For a positively oriented tetrahedron ``[v0, v1, v2, v3]``, the boundary
    orientation is:

    - opposite ``v0``: ``(v1, v2, v3)``
    - opposite ``v1``: ``(v0, v3, v2)``
    - opposite ``v2``: ``(v0, v1, v3)``
    - opposite ``v3``: ``(v0, v2, v1)``

    This matches the alternating-sign boundary of an oriented 3-simplex and is
    the local face orientation needed to mimic MKALF edge-facet walks.
    """

    local_indices = _SIMPLEX_FACE_LOCAL_INDICES[int(face_index)]
    if int(face_index) % 2 == 1:
        return (local_indices[0], local_indices[2], local_indices[1])
    return local_indices


def _weighted_simplex_centers_power_values(
    simplices: np.ndarray,
    points: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return weighted circumcenters and power values for regular simplices."""

    centers = np.empty((simplices.shape[0], 3), dtype=float)
    power_values = np.empty(simplices.shape[0], dtype=float)

    for simplex_index, simplex_atom_indices in enumerate(simplices):
        simplex_points = points[simplex_atom_indices]
        simplex_weights = weights[simplex_atom_indices]

        point_a = simplex_points[0]
        weight_a = float(simplex_weights[0])
        matrix = 2.0 * np.vstack(
            [
                simplex_points[1] - point_a,
                simplex_points[2] - point_a,
                simplex_points[3] - point_a,
            ]
        )
        vector = np.array(
            [
                np.dot(simplex_points[1], simplex_points[1]) - np.dot(point_a, point_a) - simplex_weights[1] + weight_a,
                np.dot(simplex_points[2], simplex_points[2]) - np.dot(point_a, point_a) - simplex_weights[2] + weight_a,
                np.dot(simplex_points[3], simplex_points[3]) - np.dot(point_a, point_a) - simplex_weights[3] + weight_a,
            ],
            dtype=float,
        )

        try:
            center = np.linalg.solve(matrix, vector)
        except np.linalg.LinAlgError:
            center = simplex_points.mean(axis=0)

        centers[simplex_index] = center
        power_values[simplex_index] = float(np.dot(center - point_a, center - point_a) - weight_a)

    return centers, power_values


def _regular_triangulation_simplices(
    points: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return oriented and sorted regular-triangulation simplices."""

    if points.shape[0] == 4:
        oriented = np.asarray([_orient_simplex_vertices(np.asarray([0, 1, 2, 3]), points)], dtype=int)
        return oriented, np.sort(oriented.copy(), axis=1)

    if points.shape[0] < 4:
        raise ValueError('At least 4 weighted points are required to build a 3D regular triangulation.')

    lifted_points = np.concatenate(
        (
            points,
            (np.sum(points * points, axis=1) - weights)[:, None],
        ),
        axis=1,
    )
    hull = ConvexHull(lifted_points)

    oriented_simplices = []
    simplices = []
    seen = set()

    for simplex_vertices, equation in zip(hull.simplices, hull.equations):
        if equation[-2] >= 0.0:
            continue

        simplex = tuple(sorted(int(vertex) for vertex in simplex_vertices))
        if len(set(simplex)) != 4 or simplex in seen:
            continue

        seen.add(simplex)
        oriented_simplices.append(_orient_simplex_vertices(np.asarray(simplex_vertices, dtype=int), points))
        simplices.append(simplex)

    if not simplices:
        raise ValueError('Regular triangulation produced no tetrahedra for the given weighted points.')

    return np.asarray(oriented_simplices, dtype=int), np.asarray(simplices, dtype=int)


class WeightedDelaunayMesh:
    """Persistent weighted Delaunay mesh built from a regular triangulation.

    Parameters
    ----------
    points : array-like or quantity, shape (n, 3)
        Point coordinates used to build the regular triangulation.
    weights : array-like or quantity, shape (n,)
        Scalar weights associated with each point. For atomic spheres this is
        typically the squared radius in the same length units as ``points``.
    atom_radii : array-like or quantity, optional
        Atomic radii aligned with ``points``. Stored for downstream methods.
    """

    def __init__(self, points=None, weights=None, atom_radii=None):

        self.points = None
        self.n_points = 0
        self.atom_radii = None
        self.weights = None

        self.simplices = None
        self.oriented_simplices = None
        self.neighbors = None

        self.simplex_atom_indices = None
        self.simplex_centers = None
        self.simplex_power_values = None
        self.simplex_volumes = None

        self._simplex_neighbor_map = None
        self._simplex_neighbor_pairs = None
        self._simplex_faces = None
        self._boundary_face_records = None
        self._face_index_by_atoms = None
        self._face_index_by_owner = None
        self._min_edges = None
        self._max_edges = None
        self._condition_numbers = None

        if points is None:
            return

        if puw.is_quantity(points):
            points_value = np.asarray(puw.get_value(points, to_unit='nm'), dtype=float)
        else:
            points_value = np.asarray(points, dtype=float)

        if points_value.ndim != 2 or points_value.shape[1] != 3:
            raise ValueError('points must have shape (n, 3)')

        if weights is None:
            raise ValueError('weights must be provided for WeightedDelaunayMesh')

        if puw.is_quantity(weights):
            weights_value = np.asarray(puw.get_value(weights, to_unit='nm**2'), dtype=float)
        else:
            weights_value = np.asarray(weights, dtype=float)

        if weights_value.ndim != 1 or weights_value.shape[0] != points_value.shape[0]:
            raise ValueError('weights must have shape (n_points,)')

        self.points = points_value
        self.n_points = points_value.shape[0]
        self.weights = weights_value

        if atom_radii is not None:
            if puw.is_quantity(atom_radii):
                atom_radii_value = np.asarray(puw.get_value(atom_radii, to_unit='nm'), dtype=float)
            else:
                atom_radii_value = np.asarray(atom_radii, dtype=float)

            if atom_radii_value.ndim != 1 or atom_radii_value.shape[0] != self.n_points:
                raise ValueError('atom_radii must have shape (n_points,)')

            self.atom_radii = atom_radii_value

        oriented_simplices, simplices = _regular_triangulation_simplices(points_value, weights_value)
        neighbors = _build_neighbors_from_simplices(oriented_simplices)
        simplex_centers, simplex_power_values = _weighted_simplex_centers_power_values(
            oriented_simplices,
            points_value,
            weights_value,
        )

        self.oriented_simplices = oriented_simplices.copy()
        self.simplices = simplices.copy()
        self.neighbors = neighbors
        self.simplex_atom_indices = oriented_simplices.copy()
        self.simplex_centers = simplex_centers
        self.simplex_power_values = simplex_power_values
        self.simplex_volumes = _tetrahedron_volumes(oriented_simplices, points_value)
        self._min_edges, self._max_edges = _tetrahedron_edge_extrema(oriented_simplices, points_value)
        self._condition_numbers = _tetrahedron_condition_numbers(oriented_simplices, points_value)

        self._simplex_neighbor_map = {
            int(index): sorted(int(neighbor) for neighbor in simplex_neighbors if neighbor != -1)
            for index, simplex_neighbors in enumerate(neighbors)
        }
        pairs = []
        for source, source_neighbors in self._simplex_neighbor_map.items():
            for target in source_neighbors:
                if source < target:
                    pairs.append((source, target))
        self._simplex_neighbor_pairs = np.asarray(pairs, dtype=int)
        if self._simplex_neighbor_pairs.size == 0:
            self._simplex_neighbor_pairs = np.zeros((0, 2), dtype=int)

    @property
    def n_simplices(self):
        """Return the number of simplices in the regular triangulation."""

        return 0 if self.simplices is None else int(self.simplices.shape[0])

    @property
    def centers(self):
        """Return simplex centers as the primary weighted geometric view."""

        return self.simplex_centers

    @property
    def radii(self):
        """Return non-negative orthogonal-ball radii for weighted simplices."""

        return np.sqrt(np.maximum(self.simplex_power_values, 0.0))

    def get_simplex_neighbors(self) -> dict[int, list[int]]:
        """Return simplex adjacency induced by shared triangular faces."""

        return {} if self._simplex_neighbor_map is None else self._simplex_neighbor_map

    def get_simplex_neighbor_pairs(self) -> np.ndarray:
        """Return simplex adjacency as unique index pairs."""

        if self._simplex_neighbor_pairs is None:
            return np.zeros((0, 2), dtype=int)
        return self._simplex_neighbor_pairs.copy()

    def get_simplex_faces(self) -> np.ndarray:
        """Return the sorted atom triples for each simplex face."""

        if self._simplex_faces is None:
            simplex_faces = np.empty((self.simplices.shape[0], 4, 3), dtype=int)
            for face_index, local_indices in enumerate(_SIMPLEX_FACE_LOCAL_INDICES):
                simplex_faces[:, face_index, :] = np.sort(
                    self.oriented_simplices[:, local_indices],
                    axis=1,
                )
            self._simplex_faces = simplex_faces
        return self._simplex_faces.copy()

    def _ensure_face_index_cache(self) -> None:
        """Build global triangle indices from unique face atom triples."""

        if self._face_index_by_atoms is not None and self._face_index_by_owner is not None:
            return

        face_index_by_atoms = {}
        face_index_by_owner = {}

        next_face_index = 1
        for simplex_index in range(self.simplices.shape[0]):
            for face_index in range(4):
                face_atoms = self.get_face_atoms(simplex_index, face_index)
                global_face_index = face_index_by_atoms.get(face_atoms)
                if global_face_index is None:
                    global_face_index = next_face_index
                    face_index_by_atoms[face_atoms] = global_face_index
                    next_face_index += 1
                face_index_by_owner[(int(simplex_index), int(face_index))] = int(global_face_index)

        self._face_index_by_atoms = face_index_by_atoms
        self._face_index_by_owner = face_index_by_owner

    def get_face_atoms(self, simplex_index: int, face_index: int) -> tuple[int, int, int]:
        """Return the atom indices of a simplex face as a sorted triple."""

        local_indices = _SIMPLEX_FACE_LOCAL_INDICES[int(face_index)]
        return tuple(
            sorted(
                int(atom_index)
                for atom_index in self.oriented_simplices[int(simplex_index), local_indices]
            )
        )

    def get_face_index(self, simplex_index: int, face_index: int) -> int:
        """Return the global triangle index analogous to historical `TrIndex`."""

        self._ensure_face_index_cache()
        return int(self._face_index_by_owner[(int(simplex_index), int(face_index))])

    def get_face_index_from_atoms(self, face_atoms: tuple[int, int, int]) -> int | None:
        """Return the global triangle index for a sorted face triple if present."""

        self._ensure_face_index_cache()
        return self._face_index_by_atoms.get(tuple(sorted(int(atom_index) for atom_index in face_atoms)))

    def get_face_owner_indices(self, simplex_index: int, face_index: int) -> tuple[int, int]:
        """Return the two tetrahedron owners of one face.

        The first owner is always the supplied local owner. The second owner is
        the neighboring tetrahedron index, or ``-1`` for hull faces.
        """

        simplex_index = int(simplex_index)
        face_index = int(face_index)
        return (simplex_index, int(self.neighbors[simplex_index, face_index]))

    def get_oriented_face_atoms(self, simplex_index: int, face_index: int) -> tuple[int, int, int]:
        """Return the outward-oriented atom order of a simplex face."""

        local_indices = _oriented_face_local_indices(int(face_index))
        return tuple(
            int(self.oriented_simplices[int(simplex_index), local_index])
            for local_index in local_indices
        )

    def get_boundary_face_records(self) -> list[tuple[int, int, tuple[int, int, int]]]:
        """Return boundary faces as ``(simplex_index, face_index, face_atoms)`` records."""

        if self._boundary_face_records is None:
            records = []
            for simplex_index, simplex_neighbors in enumerate(self.neighbors):
                for face_index, neighbor in enumerate(simplex_neighbors):
                    if neighbor == -1:
                        records.append(
                            (
                                int(simplex_index),
                                int(face_index),
                                self.get_face_atoms(simplex_index, face_index),
                            )
                        )
            self._boundary_face_records = records
        return list(self._boundary_face_records)
