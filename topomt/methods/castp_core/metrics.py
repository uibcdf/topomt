"""Metric helpers for the native CASTp implementation."""

import numpy as np

from topomt.tools.tessellation import mouth_area_from_faces


def component_center(simplex_centers: np.ndarray, simplex_indices: list[int]) -> np.ndarray:
    """Return the centroid of a simplex component."""

    if not simplex_indices:
        return np.zeros(3, dtype=float)
    return np.mean(simplex_centers[simplex_indices], axis=0)


def component_volume(simplex_volumes: np.ndarray, simplex_indices: list[int]) -> float:
    """Return the aggregate volume of a simplex component."""

    if not simplex_indices:
        return 0.0
    return float(np.sum(simplex_volumes[simplex_indices]))


def mouth_area(atom_coordinates: np.ndarray, faces: list[tuple[int, int, int]]) -> float:
    """Return the area of a mouth defined by triangular face triples."""

    if not faces:
        return 0.0
    return float(mouth_area_from_faces(list(faces), atom_coordinates))
