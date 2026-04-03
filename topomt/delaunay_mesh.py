"""Delaunay-based geometric substrate for TopoMT."""

import numpy as np
from scipy.spatial import Delaunay

from topomt import pyunitwizard as puw


_SIMPLEX_FACE_LOCAL_INDICES = (
    (0, 1, 2),
    (0, 1, 3),
    (0, 2, 3),
    (1, 2, 3),
)


def _tetrahedron_volumes(points_of_alpha_sphere, points):
    volumes = np.empty(len(points_of_alpha_sphere), dtype=float)
    for index, tetrahedron_indices in enumerate(points_of_alpha_sphere):
        tetrahedron_points = points[tetrahedron_indices]
        tetrahedron_matrix = np.concatenate((tetrahedron_points, np.ones((4, 1))), axis=1)
        volumes[index] = abs(np.linalg.det(tetrahedron_matrix) / 6.0)
    return volumes


def _tetrahedron_edge_extrema(points_of_alpha_sphere, points):
    min_edges = np.empty(len(points_of_alpha_sphere), dtype=float)
    max_edges = np.empty(len(points_of_alpha_sphere), dtype=float)

    edge_pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))

    for index, tetrahedron_indices in enumerate(points_of_alpha_sphere):
        tetrahedron_points = points[tetrahedron_indices]
        edge_lengths = [
            np.linalg.norm(tetrahedron_points[ii] - tetrahedron_points[jj])
            for ii, jj in edge_pairs
        ]
        min_edges[index] = min(edge_lengths)
        max_edges[index] = max(edge_lengths)

    return min_edges, max_edges


def _tetrahedron_condition_numbers(points_of_alpha_sphere, points):
    condition_numbers = np.empty(len(points_of_alpha_sphere), dtype=float)

    for index, tetrahedron_indices in enumerate(points_of_alpha_sphere):
        tetrahedron_points = points[tetrahedron_indices]
        point_a, point_b, point_c, point_d = tetrahedron_points
        matrix = 2.0 * np.vstack((point_b - point_a, point_c - point_a, point_d - point_a))
        condition_numbers[index] = np.linalg.cond(matrix)

    return condition_numbers


def _circumsphere_centers_radii(points_of_alpha_sphere, points):
    centers = np.empty((len(points_of_alpha_sphere), 3), dtype=float)
    radii = np.zeros(len(points_of_alpha_sphere), dtype=float)

    for index, tetrahedron_indices in enumerate(points_of_alpha_sphere):
        tetrahedron_points = points[tetrahedron_indices]
        point_a = tetrahedron_points[0]
        point_b = tetrahedron_points[1] - point_a
        point_c = tetrahedron_points[2] - point_a
        point_d = tetrahedron_points[3] - point_a
        matrix = 2.0 * np.array([point_b, point_c, point_d], dtype=float)
        vector = np.array(
            [
                np.dot(point_b, point_b),
                np.dot(point_c, point_c),
                np.dot(point_d, point_d),
            ],
            dtype=float,
        )
        try:
            relative_center = np.linalg.solve(matrix, vector)
            centers[index] = relative_center + point_a
            radii[index] = float(np.linalg.norm(relative_center))
        except np.linalg.LinAlgError:
            centers[index] = tetrahedron_points.mean(axis=0)
            radii[index] = 0.0

    return centers, radii


def _tetrahedron_near_cospherical_counts(points_of_alpha_sphere, points, centers, radii, tolerance):
    near_cospherical_counts = np.zeros(len(points_of_alpha_sphere), dtype=int)

    for index, tetrahedron_indices in enumerate(points_of_alpha_sphere):
        tetrahedron_index_set = set(int(ii) for ii in tetrahedron_indices)
        center = centers[index]
        radius = radii[index]

        for point_index, point in enumerate(points):
            if point_index in tetrahedron_index_set:
                continue
            delta = abs(np.linalg.norm(point - center) - radius)
            if delta <= tolerance:
                near_cospherical_counts[index] += 1

    return near_cospherical_counts


class DelaunayMesh:
    """Persistent Delaunay mesh with alpha-sphere-derived views.

    Parameters
    ----------
    points : array-like or quantity, shape (n, 3)
        Point coordinates used to build the Delaunay triangulation.
    atom_radii : array-like or quantity, optional
        Atomic radii aligned with ``points``. When provided, they are stored as
        magnitudes in nanometers.

    Notes
    -----
    The mesh is the primary geometric representation. Alpha-sphere data is
    exposed as a derived view through circumcenter- and circumradius-based
    arrays associated with the Delaunay simplices.
    """

    def __init__(self, points=None, atom_radii=None):

        self.points = None
        self.n_points = 0
        self.atom_radii = None

        self.simplices = None
        self.oriented_simplices = None
        self.neighbors = None

        self.alpha_sphere_centers = None
        self.alpha_sphere_radii = None
        self.alpha_sphere_atom_indices = None
        self.n_alpha_spheres = 0
        self.alpha_sphere_volumes = None

        self._alpha_sphere_neighbor_map = None
        self._alpha_sphere_neighbor_pairs = None
        self._min_edges = None
        self._max_edges = None
        self._condition_numbers = None
        self._simplex_faces = None
        self._boundary_face_records = None

        if points is None:
            return

        if puw.is_quantity(points):
            points_value = np.asarray(puw.get_value(points, to_unit='nm'), dtype=float)
        else:
            points_value = np.asarray(points, dtype=float)

        if points_value.ndim != 2 or points_value.shape[1] != 3:
            raise ValueError('points must have shape (n, 3)')

        self.points = points_value
        self.n_points = points_value.shape[0]

        if atom_radii is not None:
            if puw.is_quantity(atom_radii):
                atom_radii_value = np.asarray(
                    puw.get_value(atom_radii, to_unit='nm'),
                    dtype=float,
                )
            else:
                atom_radii_value = np.asarray(atom_radii, dtype=float)

            if atom_radii_value.ndim != 1 or atom_radii_value.shape[0] != self.n_points:
                raise ValueError('atom_radii must have shape (n_points,)')

            self.atom_radii = atom_radii_value

        triangulation = Delaunay(points_value)

        self.oriented_simplices = np.asarray(triangulation.simplices, dtype=int)
        self.simplices = np.sort(self.oriented_simplices.copy(), axis=1)
        self.neighbors = np.asarray(triangulation.neighbors, dtype=int)

        self.alpha_sphere_atom_indices = self.simplices.copy()
        self.alpha_sphere_centers, self.alpha_sphere_radii = _circumsphere_centers_radii(
            self.alpha_sphere_atom_indices,
            points_value,
        )
        self.n_alpha_spheres = self.alpha_sphere_centers.shape[0]
        self.alpha_sphere_volumes = _tetrahedron_volumes(self.alpha_sphere_atom_indices, points_value)
        self._min_edges, self._max_edges = _tetrahedron_edge_extrema(
            self.alpha_sphere_atom_indices,
            points_value,
        )
        self._condition_numbers = _tetrahedron_condition_numbers(
            self.alpha_sphere_atom_indices,
            points_value,
        )

        self._alpha_sphere_neighbor_map = {
            int(index): sorted(int(neighbor) for neighbor in simplex_neighbors if neighbor != -1)
            for index, simplex_neighbors in enumerate(self.neighbors)
        }

        pairs = []
        for source, source_neighbors in self._alpha_sphere_neighbor_map.items():
            for target in source_neighbors:
                if source < target:
                    pairs.append((source, target))
        self._alpha_sphere_neighbor_pairs = np.asarray(pairs, dtype=int)

    def get_alpha_sphere_neighbors(self) -> dict[int, list[int]]:
        """Return alpha-sphere adjacency induced by simplex face sharing."""

        return self._alpha_sphere_neighbor_map

    def get_alpha_sphere_neighbor_pairs(self) -> np.ndarray:
        """Return alpha-sphere adjacency as unique index pairs."""

        return self._alpha_sphere_neighbor_pairs.copy()

    def get_simplex_faces(self) -> np.ndarray:
        """Return the sorted atom triples for each simplex face."""

        if self._simplex_faces is None:
            simplex_faces = np.empty((self.simplices.shape[0], 4, 3), dtype=int)
            for face_index, local_indices in enumerate(_SIMPLEX_FACE_LOCAL_INDICES):
                simplex_faces[:, face_index, :] = np.sort(
                    self.simplices[:, local_indices],
                    axis=1,
                )
            self._simplex_faces = simplex_faces
        return self._simplex_faces.copy()

    def get_face_atoms(self, simplex_index: int, face_index: int) -> tuple[int, int, int]:
        """Return the atom indices of a simplex face as a sorted triple."""

        local_indices = _SIMPLEX_FACE_LOCAL_INDICES[int(face_index)]
        return tuple(sorted(int(atom_index) for atom_index in self.simplices[int(simplex_index), local_indices]))

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

    def filter_alpha_spheres(
        self,
        min_radius=None,
        max_radius=None,
    ) -> np.ndarray:
        """Return a boolean mask selecting alpha-spheres by radius."""

        if self.alpha_sphere_radii is None:
            return np.zeros(0, dtype=bool)

        mask = np.ones(self.n_alpha_spheres, dtype=bool)

        if min_radius is not None:
            if puw.is_quantity(min_radius):
                min_radius_value = float(puw.get_value(min_radius, to_unit='nm'))
            else:
                min_radius_value = float(min_radius)
            mask &= self.alpha_sphere_radii >= min_radius_value

        if max_radius is not None:
            if puw.is_quantity(max_radius):
                max_radius_value = float(puw.get_value(max_radius, to_unit='nm'))
            else:
                max_radius_value = float(max_radius)
            mask &= self.alpha_sphere_radii <= max_radius_value

        return mask

    @property
    def centers(self):
        return self.alpha_sphere_centers

    @property
    def radii(self):
        return self.alpha_sphere_radii

    @property
    def points_of_alpha_sphere(self):
        return self.alpha_sphere_atom_indices

    def get_neighbors(self, criterion='face'):
        """Return alpha-sphere adjacency induced by simplex face sharing."""

        return self.get_alpha_sphere_neighbors()

    def get_volumes(self):
        """Return alpha-sphere-associated tetrahedron volumes."""

        return self.alpha_sphere_volumes

    def _rebuild_neighbor_cache(self, simplices, neighbors):
        self.simplices = simplices
        self.neighbors = neighbors
        self.alpha_sphere_atom_indices = simplices
        self.n_alpha_spheres = simplices.shape[0]
        self._simplex_faces = None
        self._boundary_face_records = None
        self._alpha_sphere_neighbor_map = {
            int(index): sorted(int(neighbor) for neighbor in simplex_neighbors if neighbor != -1)
            for index, simplex_neighbors in enumerate(neighbors)
        }
        pairs = []
        for source, source_neighbors in self._alpha_sphere_neighbor_map.items():
            for target in source_neighbors:
                if source < target:
                    pairs.append((source, target))
        self._alpha_sphere_neighbor_pairs = np.asarray(pairs, dtype=int)

    def remove_alpha_spheres(self, indices):
        """Remove selected alpha-sphere-derived entries from the mesh view."""

        if self.n_alpha_spheres == 0:
            return

        mask = np.ones(self.n_alpha_spheres, dtype=bool)
        mask[np.asarray(indices, dtype=int)] = False

        old_to_new = {
            int(old_index): int(new_index)
            for new_index, old_index in enumerate(np.where(mask)[0])
        }

        self._alpha_sphere_neighbor_map = {
            old_to_new[old_index]: [
                old_to_new[neighbor]
                for neighbor in neighbors
                if neighbor in old_to_new
            ]
            for old_index, neighbors in self._alpha_sphere_neighbor_map.items()
            if old_index in old_to_new
        }

        pairs = []
        for source, source_neighbors in self._alpha_sphere_neighbor_map.items():
            for target in source_neighbors:
                if source < target:
                    pairs.append((source, target))
        self._alpha_sphere_neighbor_pairs = np.asarray(pairs, dtype=int)
        self._simplex_faces = None
        self._boundary_face_records = None

        self.alpha_sphere_centers = self.alpha_sphere_centers[mask]
        self.alpha_sphere_radii = self.alpha_sphere_radii[mask]
        self.alpha_sphere_atom_indices = self.alpha_sphere_atom_indices[mask]
        self.alpha_sphere_volumes = self.alpha_sphere_volumes[mask]
        self._min_edges = self._min_edges[mask]
        self._max_edges = self._max_edges[mask]
        self._condition_numbers = self._condition_numbers[mask]
        self.n_alpha_spheres = int(np.count_nonzero(mask))

        if self.n_alpha_spheres == 0:
            self.alpha_sphere_centers = np.zeros((0, 3), dtype=float)
            self.alpha_sphere_radii = np.zeros(0, dtype=float)
            self.alpha_sphere_atom_indices = np.zeros((0, 4), dtype=int)
            self.alpha_sphere_volumes = np.zeros(0, dtype=float)
            self._min_edges = np.zeros(0, dtype=float)
            self._max_edges = np.zeros(0, dtype=float)
            self._condition_numbers = np.zeros(0, dtype=float)
            self._alpha_sphere_neighbor_map = {}
            self._alpha_sphere_neighbor_pairs = np.zeros((0, 2), dtype=int)

    def remove_small_alpha_spheres(self, minimum_radius):
        """Remove alpha-sphere entries below a radius threshold."""

        if puw.is_quantity(minimum_radius):
            minimum_radius_value = float(puw.get_value(minimum_radius, to_unit='nm'))
        else:
            minimum_radius_value = float(minimum_radius)
        indices = np.where(self.alpha_sphere_radii < minimum_radius_value)[0]
        self.remove_alpha_spheres(indices)

    def remove_big_alpha_spheres(self, maximum_radius):
        """Remove alpha-sphere entries above a radius threshold."""

        if puw.is_quantity(maximum_radius):
            maximum_radius_value = float(puw.get_value(maximum_radius, to_unit='nm'))
        else:
            maximum_radius_value = float(maximum_radius)
        indices = np.where(self.alpha_sphere_radii > maximum_radius_value)[0]
        self.remove_alpha_spheres(indices)

    def get_points_of_alpha_spheres(self, indices):
        """Return unique point indices touching a set of alpha-sphere entries."""

        return np.unique(self.alpha_sphere_atom_indices[np.asarray(indices, dtype=int)].reshape(-1))

    def get_ambiguity_indicators(self, cospherical_tolerance=0.01):
        """Return geometric indicators of potentially ambiguous alpha-sphere entries."""

        if puw.is_quantity(cospherical_tolerance):
            tolerance = float(puw.get_value(cospherical_tolerance, to_unit='nm'))
        else:
            tolerance = float(cospherical_tolerance)

        normalized_volumes = np.divide(
            self.alpha_sphere_volumes,
            np.power(self._min_edges, 3),
            out=np.zeros_like(self.alpha_sphere_volumes),
            where=self._min_edges > 0.0,
        )
        radius_over_min_edge = np.divide(
            self.alpha_sphere_radii,
            self._min_edges,
            out=np.zeros_like(self.alpha_sphere_radii),
            where=self._min_edges > 0.0,
        )
        near_cospherical_counts = _tetrahedron_near_cospherical_counts(
            self.alpha_sphere_atom_indices,
            self.points,
            self.alpha_sphere_centers,
            self.alpha_sphere_radii,
            tolerance,
        )

        return {
            'volume': self.alpha_sphere_volumes.copy(),
            'normalized_volume': normalized_volumes,
            'min_edge': self._min_edges.copy(),
            'max_edge': self._max_edges.copy(),
            'radius_over_min_edge': radius_over_min_edge,
            'condition_number': self._condition_numbers.copy(),
            'near_cospherical_count': near_cospherical_counts,
        }

    def get_potentially_ambiguous_alpha_spheres(
        self,
        cospherical_tolerance=0.01,
        minimum_near_cospherical_count=1,
        minimum_condition_number=10.0,
        maximum_normalized_volume=None,
    ):
        """Return indices of alpha-sphere entries that look geometrically ambiguous."""

        indicators = self.get_ambiguity_indicators(cospherical_tolerance=cospherical_tolerance)
        mask = np.zeros(self.n_alpha_spheres, dtype=bool)

        if minimum_near_cospherical_count is not None:
            mask |= indicators['near_cospherical_count'] >= int(minimum_near_cospherical_count)

        if minimum_condition_number is not None:
            mask |= indicators['condition_number'] >= float(minimum_condition_number)

        if maximum_normalized_volume is not None:
            mask |= indicators['normalized_volume'] <= float(maximum_normalized_volume)

        return np.where(mask)[0], indicators
