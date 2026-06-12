"""Sampling-based geometric helpers."""

from collections.abc import Sequence

import numpy as np


def union_volume_monte_carlo(
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
    n_samples: int = 200_000,
    rng: np.random.Generator | None = None,
) -> float:
    """Estimate the volume of the union of spheres by Monte Carlo sampling."""

    if not isinstance(n_samples, int) or isinstance(n_samples, bool) or n_samples <= 0:
        raise ValueError('n_samples must be a positive integer')

    if rng is None:
        rng = np.random.default_rng()

    sphere_centers = np.asarray(centers, dtype=float)
    sphere_radii = np.asarray(radii, dtype=float).reshape(-1, 1)
    if sphere_centers.shape[0] == 0:
        return 0.0

    mins = np.min(sphere_centers - sphere_radii, axis=0)
    maxs = np.max(sphere_centers + sphere_radii, axis=0)
    box_volume = float(np.prod(maxs - mins))

    points = rng.uniform(low=mins, high=maxs, size=(n_samples, 3))

    inside = 0
    chunk = 50_000
    radius_squared = sphere_radii.squeeze() ** 2
    for start in range(0, n_samples, chunk):
        stop = min(start + chunk, n_samples)
        sample = points[start:stop]
        distance_squared = ((sample[:, None, :] - sphere_centers[None, :, :]) ** 2).sum(axis=2)
        mask = np.any(distance_squared <= radius_squared, axis=1)
        inside += int(np.sum(mask))

    return box_volume * (inside / n_samples)
