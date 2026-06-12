"""Channel profile helpers."""

import math

import numpy as np


def _to_numpy(array: np.ndarray | list | tuple) -> np.ndarray:
    return np.asarray(array, dtype=float)


def _validate_profile_inputs(points: np.ndarray, axis: np.ndarray, n_bins: int) -> None:
    if points.ndim != 2 or points.shape[1] != 3 or len(points) == 0:
        raise ValueError('centers must contain at least one point with shape (n, 3)')
    if axis.shape != (3,):
        raise ValueError('axis must have shape (3,)')
    if not isinstance(n_bins, int) or isinstance(n_bins, bool) or n_bins <= 0:
        raise ValueError('n_bins must be a positive integer')


def cross_section_profile(
    centers: np.ndarray,
    axis: np.ndarray,
    n_bins: int = 20,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a radial profile along an axis.

    Parameters
    ----------
    centers : ndarray
        Points sampling the cavity or channel.
    axis : ndarray
        Direction vector defining the profiling axis.
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
    projection = points.dot(axis_unit)
    projection_min, projection_max = projection.min(), projection.max()
    bins = np.linspace(projection_min, projection_max, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    radial_max = np.zeros(n_bins, dtype=float)

    axis_projection = np.outer(projection, axis_unit)
    perpendicular = points - axis_projection
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
) -> float:
    """Return the minimum non-zero radial extent along the profiling axis."""

    _, radial = cross_section_profile(centers, axis, n_bins=n_bins)
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
    n_points = points.shape[0]
    adjacency: list[list[tuple[int, float]]] = [[] for _ in range(n_points)]

    for node_i, node_j in neighbor_pairs:
        index_i = int(node_i)
        index_j = int(node_j)
        weight = float(np.linalg.norm(points[index_i] - points[index_j]))
        adjacency[index_i].append((index_j, weight))
        adjacency[index_j].append((index_i, weight))

    targets = {int(index) for index in end_indices}
    distances = [math.inf] * n_points
    queue: list[tuple[float, int]] = []

    for start in start_indices:
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


def thickness_profile(
    centers: np.ndarray,
    axis: np.ndarray,
    neighbor_pairs: np.ndarray | list | tuple | None = None,
    n_bins: int = 20,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a simple local-thickness profile along an axis."""

    points = _to_numpy(centers)
    axis = _to_numpy(axis)
    _validate_profile_inputs(points, axis, n_bins)
    norm = np.linalg.norm(axis)
    if norm == 0:
        raise ValueError('Axis vector cannot be zero.')

    axis_unit = axis / norm
    projection = points.dot(axis_unit)
    projection_min, projection_max = projection.min(), projection.max()
    bins = np.linspace(projection_min, projection_max, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    if neighbor_pairs is not None:
        adjacency = [[] for _ in range(len(points))]
        for node_i, node_j in neighbor_pairs:
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
