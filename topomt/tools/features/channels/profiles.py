"""Channel profile helpers."""

import math

import numpy as np
from depdigest import dep_digest


def _to_numpy(array: np.ndarray | list | tuple) -> np.ndarray:
    return np.asarray(array, dtype=float)


def _validate_profile_inputs(points: np.ndarray, axis: np.ndarray, n_bins: int) -> None:
    if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0:
        raise ValueError('centers must contain at least one point with shape (n, 3)')
    if not np.all(np.isfinite(points)):
        raise ValueError('centers must contain finite values')
    if axis.shape != (3,):
        raise ValueError('axis must have shape (3,)')
    if not np.all(np.isfinite(axis)):
        raise ValueError('axis must contain finite values')
    if not isinstance(n_bins, int) or isinstance(n_bins, bool) or n_bins <= 0:
        raise ValueError('n_bins must be a positive integer')


def _profile_axis_point(points: np.ndarray, axis_point) -> np.ndarray:
    if axis_point is None:
        return points.mean(axis=0)
    point = _to_numpy(axis_point)
    if point.shape != (3,):
        raise ValueError('axis_point must have shape (3,)')
    if not np.all(np.isfinite(point)):
        raise ValueError('axis_point must contain finite values')
    return point


def _validate_index_array(indices, n_points: int, name: str) -> np.ndarray:
    array = np.asarray(indices, dtype=int)
    if array.ndim != 1:
        raise ValueError(f'{name} must be a one-dimensional sequence of indices')
    if array.size == 0:
        raise ValueError(f'{name} must contain at least one index')
    if np.any((array < 0) | (array >= n_points)):
        raise ValueError(f'{name} contains out-of-range indices')
    return array


def _validate_neighbor_pairs(neighbor_pairs, n_points: int) -> np.ndarray:
    pairs = np.asarray(neighbor_pairs, dtype=int)
    if pairs.size == 0:
        return np.zeros((0, 2), dtype=int)
    if pairs.ndim != 2 or pairs.shape[1] != 2:
        raise ValueError('neighbor_pairs must have shape (n_edges, 2)')
    if np.any((pairs < 0) | (pairs >= n_points)):
        raise ValueError('neighbor_pairs contains out-of-range indices')
    return pairs


def cross_section_profile(
    centers: np.ndarray,
    axis: np.ndarray,
    n_bins: int = 20,
    *,
    axis_point: np.ndarray | list | tuple | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a radial profile along an axis.

    Parameters
    ----------
    centers : ndarray
        Points sampling the cavity or channel.
    axis : ndarray
        Direction vector defining the profiling axis.
    axis_point : ndarray, optional
        Point where the profiling axis passes through. If omitted, the centroid
        of ``centers`` is used so translated channels are handled consistently.
    n_bins : int, default=20
        Number of bins along the axis.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Bin centers along the axis and the maximum radial extent in each bin.
    """

    points = _to_numpy(centers)
    axis = _to_numpy(axis)
    _validate_profile_inputs(points, axis, n_bins)
    norm = np.linalg.norm(axis)
    if norm == 0:
        raise ValueError('Axis vector cannot be zero.')

    axis_unit = axis / norm
    origin = _profile_axis_point(points, axis_point)
    centered = points - origin
    projection = centered.dot(axis_unit)
    projection_min, projection_max = projection.min(), projection.max()
    bins = np.linspace(projection_min, projection_max, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    radial_max = np.zeros(n_bins, dtype=float)

    axis_projection = np.outer(projection, axis_unit)
    perpendicular = centered - axis_projection
    radial_distances = np.linalg.norm(perpendicular, axis=1)

    indices = np.clip(np.digitize(projection, bins) - 1, 0, n_bins - 1)
    for bin_index in range(n_bins):
        mask = indices == bin_index
        if np.any(mask):
            radial_max[bin_index] = radial_distances[mask].max()

    return bin_centers, radial_max


def min_cross_section_radius(
    centers: np.ndarray,
    axis: np.ndarray,
    n_bins: int = 20,
    *,
    axis_point: np.ndarray | list | tuple | None = None,
) -> float:
    """Return the minimum non-zero radial extent along the profiling axis."""

    _, radial = cross_section_profile(
        centers, axis, axis_point=axis_point, n_bins=n_bins
    )
    if radial.size == 0:
        return 0.0

    positive = radial[radial > 0]
    if positive.size == 0:
        return 0.0

    return float(positive.min())


def shortest_path_length(
    centers: np.ndarray,
    neighbor_pairs: np.ndarray | list | tuple,
    start_indices: np.ndarray | list | tuple,
    end_indices: np.ndarray | list | tuple,
) -> float:
    """Compute the shortest path length over an alpha-sphere or simplex graph."""

    import heapq

    points = _to_numpy(centers)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0:
        raise ValueError('centers must contain at least one point with shape (n, 3)')
    if not np.all(np.isfinite(points)):
        raise ValueError('centers must contain finite values')
    n_points = points.shape[0]
    pairs = _validate_neighbor_pairs(neighbor_pairs, n_points)
    starts = _validate_index_array(start_indices, n_points, 'start_indices')
    targets = set(_validate_index_array(end_indices, n_points, 'end_indices'))
    adjacency: list[list[tuple[int, float]]] = [[] for _ in range(n_points)]

    for node_i, node_j in pairs:
        index_i = int(node_i)
        index_j = int(node_j)
        weight = float(np.linalg.norm(points[index_i] - points[index_j]))
        adjacency[index_i].append((index_j, weight))
        adjacency[index_j].append((index_i, weight))

    distances = [math.inf] * n_points
    queue: list[tuple[float, int]] = []

    for start in starts:
        start = int(start)
        distances[start] = 0.0
        heapq.heappush(queue, (0.0, start))

    while queue:
        distance, node = heapq.heappop(queue)
        if distance > distances[node]:
            continue
        if node in targets:
            return distance

        for neighbor, weight in adjacency[node]:
            next_distance = distance + weight
            if next_distance < distances[neighbor]:
                distances[neighbor] = next_distance
                heapq.heappush(queue, (next_distance, neighbor))

    return math.inf


@dep_digest('sklearn', when={'neighbor_pairs': None})
def thickness_profile(
    centers: np.ndarray,
    axis: np.ndarray,
    neighbor_pairs: np.ndarray | list | tuple | None = None,
    n_bins: int = 20,
    *,
    axis_point: np.ndarray | list | tuple | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a simple local-thickness profile along an axis."""

    points = _to_numpy(centers)
    axis = _to_numpy(axis)
    _validate_profile_inputs(points, axis, n_bins)
    norm = np.linalg.norm(axis)
    if norm == 0:
        raise ValueError('Axis vector cannot be zero.')

    axis_unit = axis / norm
    origin = _profile_axis_point(points, axis_point)
    projection = (points - origin).dot(axis_unit)
    projection_min, projection_max = projection.min(), projection.max()
    bins = np.linspace(projection_min, projection_max, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    if neighbor_pairs is not None:
        adjacency = [[] for _ in range(len(points))]
        pairs = _validate_neighbor_pairs(neighbor_pairs, len(points))
        for node_i, node_j in pairs:
            index_i = int(node_i)
            index_j = int(node_j)
            distance = np.linalg.norm(points[index_i] - points[index_j])
            adjacency[index_i].append(distance)
            adjacency[index_j].append(distance)
        local_radii = np.array([min(neighbors) / 2 if neighbors else 0.0 for neighbors in adjacency])
    else:
        from sklearn.neighbors import NearestNeighbors

        neighbors = NearestNeighbors(n_neighbors=min(3, len(points)), algorithm='auto').fit(points)
        distances, _ = neighbors.kneighbors(points)
        if distances.shape[1] > 1:
            local_radii = distances[:, 1] / 2.0
        else:
            local_radii = np.zeros(len(points))

    profile = np.zeros(n_bins, dtype=float)
    indices = np.clip(np.digitize(projection, bins) - 1, 0, n_bins - 1)
    for bin_index in range(n_bins):
        mask = indices == bin_index
        if np.any(mask):
            profile[bin_index] = local_radii[mask].mean()

    return bin_centers, profile
