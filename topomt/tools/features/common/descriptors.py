"""Common geometric descriptors for TopoMT features."""

import math
from typing import Sequence

import numpy as np


def _to_numpy(points) -> np.ndarray:
    return np.asarray(points, dtype=float)


def bounding_metrics(points: Sequence[Sequence[float]]) -> dict[str, float | np.ndarray]:
    """Compute oriented bounding-box-like metrics using PCA axes."""

    point_array = _to_numpy(points)
    if point_array.shape[0] == 0:
        return {
            'centroid': np.zeros(3),
            'axes': np.zeros((3, 3)),
            'lengths': np.zeros(3),
            'elongation': 0.0,
        }

    centroid = point_array.mean(axis=0)
    centered = point_array - centroid
    covariance = centered.T @ centered / max(1, point_array.shape[0] - 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, order]

    projected = centered @ eigenvectors
    mins = projected.min(axis=0)
    maxs = projected.max(axis=0)
    lengths = maxs - mins
    elongation = lengths[0] / lengths[1] if lengths[1] > 0 else math.inf

    return {
        'centroid': centroid,
        'axes': eigenvectors,
        'lengths': lengths,
        'elongation': float(elongation),
    }


def effective_center_radius(points: Sequence[Sequence[float]]) -> tuple[np.ndarray, float, float]:
    """Return centroid, mean radial distance, and max radial distance."""

    point_array = _to_numpy(points)
    if point_array.shape[0] == 0:
        return np.zeros(3), 0.0, 0.0

    centroid = point_array.mean(axis=0)
    distances = np.linalg.norm(point_array - centroid, axis=1)
    return centroid, float(distances.mean()), float(distances.max())
