import numpy as np
from scipy.spatial import Delaunay, Voronoi

from topomt import pyunitwizard as puw


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


class AlphaSpheres:

    """Set of alpha-spheres

    Object with a set of alpha-spheres. Internal data is stored as pure NumPy arrays 
    (magnitudes) in nanometers (nm) to ensure high performance.
    """

    def __init__(self, points=None, radii=None, method='voronoi', skip_digestion=False):

        self.points=None
        self.n_points=None
        self.centers=None
        self.points_of_alpha_sphere=None
        self.radii=None
        self.volumes=None
        self.n_alpha_spheres=None
        self._neighbors = None
        self._min_edges = None
        self._max_edges = None
        self._condition_numbers = None

        if points is not None:

            if puw.is_quantity(points):
                points_value = np.asarray(puw.get_value(points, to_unit='nm'), dtype=float)
            else:
                points_value = np.asarray(points, dtype=float)

            self.points = points_value
            self.n_points = points_value.shape[0]

            triangulation = Delaunay(points_value)
            voronoi = Voronoi(points_value)

            # Internal storage as pure magnitudes in nm
            self.centers = voronoi.vertices
            self.n_alpha_spheres = voronoi.vertices.shape[0]
            self.points_of_alpha_sphere = np.sort(
                np.asarray(triangulation.simplices, dtype=int),
                axis=1,
            )

            # Compute radii as magnitudes in nm
            self.radii = np.zeros(self.n_alpha_spheres)
            for ii in range(self.n_alpha_spheres):
                self.radii[ii] = np.linalg.norm(
                    self.centers[ii] - points_value[self.points_of_alpha_sphere[ii][0]]
                )

            self.volumes = _tetrahedron_volumes(self.points_of_alpha_sphere, points_value)
            self._min_edges, self._max_edges = _tetrahedron_edge_extrema(
                self.points_of_alpha_sphere, points_value
            )
            self._condition_numbers = _tetrahedron_condition_numbers(
                self.points_of_alpha_sphere, points_value
            )

            self._neighbors = {}
            for i, neighs in enumerate(triangulation.neighbors):
                self._neighbors[i] = sorted([int(n) for n in neighs if n != -1])

    def get_neighbors(self, criterion='face'):
        return self._neighbors

    def get_volumes(self):
        return self.volumes

    def remove_alpha_spheres(self, indices):
        mask = np.ones(self.n_alpha_spheres, dtype=bool)
        mask[indices] = False
        old_to_new = {
            old_index: new_index for new_index, old_index in enumerate(np.where(mask)[0])
        }
        self._neighbors = {
            old_to_new[old_index]: [
                old_to_new[neighbor]
                for neighbor in neighbors
                if neighbor in old_to_new
            ]
            for old_index, neighbors in self._neighbors.items()
            if old_index in old_to_new
        }
        self.centers = self.centers[mask,:]
        self.points_of_alpha_sphere = self.points_of_alpha_sphere[mask]
        self.radii = self.radii[mask]
        self.volumes = self.volumes[mask]
        self._min_edges = self._min_edges[mask]
        self._max_edges = self._max_edges[mask]
        self._condition_numbers = self._condition_numbers[mask]
        self.n_alpha_spheres = np.count_nonzero(mask)

    def remove_small_alpha_spheres(self, minimum_radius):
        if puw.is_quantity(minimum_radius):
            min_val = float(puw.get_value(minimum_radius, to_unit='nm'))
        else:
            min_val = float(minimum_radius)
        indices_to_remove = np.where(self.radii < min_val)[0]
        self.remove_alpha_spheres(indices_to_remove)

    def remove_big_alpha_spheres(self, maximum_radius):
        if puw.is_quantity(maximum_radius):
            max_val = float(puw.get_value(maximum_radius, to_unit='nm'))
        else:
            max_val = float(maximum_radius)
        indices_to_remove = np.where(self.radii > max_val)[0]
        self.remove_alpha_spheres(indices_to_remove)

    def get_points_of_alpha_spheres(self, indices):
        return np.unique(self.points_of_alpha_sphere[indices].reshape(-1))

    def get_ambiguity_indicators(self, cospherical_tolerance=0.01):
        """Return geometric indicators of potentially ambiguous alpha-spheres.

        Parameters
        ----------
        cospherical_tolerance : float or quantity, default=0.01
            Tolerance used to count nearby points that lie close to the
            circumsphere of an alpha-sphere. The value is interpreted in
            nanometers.

        Returns
        -------
        dict
            Dictionary with one NumPy array per indicator:
            `volume`, `normalized_volume`, `min_edge`, `max_edge`,
            `radius_over_min_edge`, `condition_number`,
            `near_cospherical_count`.
        """

        if puw.is_quantity(cospherical_tolerance):
            tolerance = float(puw.get_value(cospherical_tolerance, to_unit='nm'))
        else:
            tolerance = float(cospherical_tolerance)
        normalized_volumes = np.divide(
            self.volumes,
            np.power(self._min_edges, 3),
            out=np.zeros_like(self.volumes),
            where=self._min_edges > 0.0,
        )
        radius_over_min_edge = np.divide(
            self.radii,
            self._min_edges,
            out=np.zeros_like(self.radii),
            where=self._min_edges > 0.0,
        )
        near_cospherical_counts = _tetrahedron_near_cospherical_counts(
            self.points_of_alpha_sphere,
            self.points,
            self.centers,
            self.radii,
            tolerance,
        )

        return {
            'volume': self.volumes.copy(),
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
        """Return alpha-sphere indices that look geometrically ambiguous.

        Parameters
        ----------
        cospherical_tolerance : float or quantity, default=0.01
            Tolerance used to count nearby points that lie close to the
            circumsphere of an alpha-sphere. The value is interpreted in
            nanometers.
        minimum_near_cospherical_count : int, default=1
            Minimum number of nearby points close to the circumsphere required
            to flag an alpha-sphere as ambiguous.
        minimum_condition_number : float, default=10.0
            Minimum tetrahedron linear-system condition number required to flag
            an alpha-sphere as ambiguous.
        maximum_normalized_volume : float, optional
            If provided, alpha-spheres with normalized tetrahedron volume lower
            than or equal to this value are also flagged.

        Returns
        -------
        tuple[np.ndarray, dict]
            Tuple with the flagged alpha-sphere indices and the full indicator
            dictionary returned by `get_ambiguity_indicators()`.
        """

        indicators = self.get_ambiguity_indicators(
            cospherical_tolerance=cospherical_tolerance,
        )

        mask = np.zeros(self.n_alpha_spheres, dtype=bool)

        if minimum_near_cospherical_count is not None:
            mask |= (
                indicators['near_cospherical_count']
                >= minimum_near_cospherical_count
            )

        if minimum_condition_number is not None:
            mask |= indicators['condition_number'] >= minimum_condition_number

        if maximum_normalized_volume is not None:
            mask |= indicators['normalized_volume'] <= maximum_normalized_volume

        return np.where(mask)[0], indicators
