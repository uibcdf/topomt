"""Metric helpers for the native CASTp implementation."""

from collections import Counter

import numpy as np

from topomt.tools.geometry.primitives import triangle_area
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


def component_area(atom_coordinates: np.ndarray, faces: list[tuple[int, int, int]]) -> float:
    """Return the boundary area of a feature from its triangular faces."""

    if not faces:
        return 0.0

    total = 0.0
    for face in faces:
        a, b, c = (int(face[0]), int(face[1]), int(face[2]))
        total += triangle_area(atom_coordinates[[a, b, c]])
    return float(total)


def mouth_area(atom_coordinates: np.ndarray, faces: list[tuple[int, int, int]]) -> float:
    """Return the area of a mouth defined by triangular face triples."""

    if not faces:
        return 0.0
    return float(mouth_area_from_faces(list(faces), atom_coordinates))


def mouth_perimeter(atom_coordinates: np.ndarray, faces: list[tuple[int, int, int]]) -> float:
    """Return the perimeter of a mouth triangulation.

    The perimeter is the sum of boundary edges of the mouth patch, not the sum
    of all triangle edges.
    """

    if not faces:
        return 0.0

    edge_counter: Counter[tuple[int, int]] = Counter()
    for face in faces:
        a, b, c = (int(face[0]), int(face[1]), int(face[2]))
        edge_counter.update(
            (
                tuple(sorted((a, b))),
                tuple(sorted((b, c))),
                tuple(sorted((c, a))),
            )
        )

    total = 0.0
    for (source, target), count in edge_counter.items():
        if count != 1:
            continue
        total += float(np.linalg.norm(atom_coordinates[source] - atom_coordinates[target]))
    return float(total)
