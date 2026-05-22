from collections import namedtuple

import numpy as np


SolventVolumeResult = namedtuple(
    'SolventVolumeResult',
    ['volume', 'empty_fraction', 'occupied_fraction', 'n_samples'],
)


def tetrahedron_volume(vertices) -> float:
    """Return the Euclidean volume of a tetrahedron."""
    vertices = np.asarray(vertices, dtype=float)
    if vertices.shape != (4, 3):
        raise ValueError('vertices must have shape (4, 3)')
    matrix = np.column_stack(
        [vertices[1] - vertices[0], vertices[2] - vertices[0], vertices[3] - vertices[0]]
    )
    return abs(float(np.linalg.det(matrix))) / 6.0


def _simplex_lattice_weights(resolution: int, alpha: float = 0.5) -> np.ndarray:
    """Return deterministic interior barycentric samples for a tetrahedron.

    The half-cell shift avoids sampling exactly on atoms at tetrahedron vertices.
    This is a stable first estimator, not an analytic solvent-volume formula.
    """
    if resolution < 1:
        raise ValueError('resolution must be >= 1')
    weights = []
    denominator = float(resolution + 4.0 * alpha)
    for i in range(resolution + 1):
        for j in range(resolution + 1 - i):
            for k in range(resolution + 1 - i - j):
                l = resolution - i - j - k
                weights.append(
                    [
                        (i + alpha) / denominator,
                        (j + alpha) / denominator,
                        (k + alpha) / denominator,
                        (l + alpha) / denominator,
                    ]
                )
    return np.asarray(weights, dtype=float)


_WEIGHT_CACHE: dict[int, np.ndarray] = {}


def tetrahedron_solvent_volume_estimate(
    vertices,
    radii,
    resolution: int = 8,
    epsilon: float = 1e-9,
) -> SolventVolumeResult:
    """Estimate empty volume inside a tetrahedron after local atom exclusion.

    The estimator samples deterministic barycentric points inside the tetrahedron
    and counts the fraction that is outside the four local atomic spheres. It is
    deliberately named as an estimate because it does not yet subtract exact
    sphere-tetrahedron intersections and does not include non-local atom
    intrusions.
    """
    vertices = np.asarray(vertices, dtype=float)
    radii = np.asarray(radii, dtype=float)
    if vertices.shape != (4, 3):
        raise ValueError('vertices must have shape (4, 3)')
    if radii.shape != (4,):
        raise ValueError('radii must have shape (4,)')

    volume = tetrahedron_volume(vertices)
    if volume <= epsilon:
        return SolventVolumeResult(0.0, 0.0, 1.0, 0)

    weights = _WEIGHT_CACHE.get(resolution)
    if weights is None:
        weights = _simplex_lattice_weights(resolution)
        _WEIGHT_CACHE[resolution] = weights

    points = weights @ vertices
    distances = np.linalg.norm(points[:, None, :] - vertices[None, :, :], axis=2)
    occupied = np.any(distances <= radii[None, :] + epsilon, axis=1)
    occupied_fraction = float(np.count_nonzero(occupied)) / float(len(points))
    empty_fraction = 1.0 - occupied_fraction
    return SolventVolumeResult(
        volume * empty_fraction,
        empty_fraction,
        occupied_fraction,
        int(len(points)),
    )


def tetrahedron_solvent_volume_estimate_batch(
    vertices,
    radii,
    resolution: int = 8,
    epsilon: float = 1e-9,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Estimate solvent volumes for a batch of tetrahedra."""
    vertices = np.asarray(vertices, dtype=float)
    radii = np.asarray(radii, dtype=float)
    if vertices.ndim != 3 or vertices.shape[1:] != (4, 3):
        raise ValueError('vertices must have shape (n_tetrahedra, 4, 3)')
    if radii.shape != vertices.shape[:2]:
        raise ValueError('radii must have shape (n_tetrahedra, 4)')

    volumes = np.zeros(vertices.shape[0], dtype=float)
    empty_fractions = np.zeros(vertices.shape[0], dtype=float)
    occupied_fractions = np.zeros(vertices.shape[0], dtype=float)
    n_samples = np.zeros(vertices.shape[0], dtype=int)
    for index in range(vertices.shape[0]):
        result = tetrahedron_solvent_volume_estimate(
            vertices[index],
            radii[index],
            resolution=resolution,
            epsilon=epsilon,
        )
        volumes[index] = result.volume
        empty_fractions[index] = result.empty_fraction
        occupied_fractions[index] = result.occupied_fraction
        n_samples[index] = result.n_samples
    return volumes, empty_fractions, occupied_fractions, n_samples
