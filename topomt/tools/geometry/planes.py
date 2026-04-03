"""Plane-based geometric helpers."""

from collections.abc import Sequence

import numpy as np
from scipy.spatial import ConvexHull


def clip_mesh_with_plane(
    vertices: np.ndarray,
    faces: np.ndarray,
    plane_point: Sequence[float],
    plane_normal: Sequence[float],
) -> tuple[np.ndarray, float, float]:
    """Intersect a mesh with a plane and return polygon, area, and perimeter."""

    verts = np.asarray(vertices, dtype=float)
    tri = np.asarray(faces, dtype=int)
    point = np.asarray(plane_point, dtype=float)
    normal = np.asarray(plane_normal, dtype=float)
    normal_norm = np.linalg.norm(normal)
    if normal_norm == 0:
        return np.zeros((0, 3)), 0.0, 0.0
    normal_unit = normal / normal_norm

    distances = (verts - point) @ normal_unit
    polygon_points = []

    for triangle in tri:
        triangle_vertices = verts[triangle]
        triangle_distances = distances[triangle]
        for i, j in ((0, 1), (1, 2), (2, 0)):
            distance_i = triangle_distances[i]
            distance_j = triangle_distances[j]
            if distance_i * distance_j < 0 or distance_i == 0 or distance_j == 0:
                fraction = distance_i / (distance_i - distance_j) if (distance_i - distance_j) != 0 else 0.0
                intersection = triangle_vertices[i] + fraction * (triangle_vertices[j] - triangle_vertices[i])
                polygon_points.append(intersection)

    if len(polygon_points) < 3:
        return np.zeros((0, 3)), 0.0, 0.0

    polygon = np.unique(np.round(polygon_points, decimals=6), axis=0)
    if polygon.shape[0] < 3:
        return np.zeros((0, 3)), 0.0, 0.0

    reference = np.array([1.0, 0.0, 0.0]) if abs(normal_unit[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    basis_u = np.cross(normal_unit, reference)
    basis_u /= np.linalg.norm(basis_u)
    basis_v = np.cross(normal_unit, basis_u)

    relative = polygon - point
    x_coord = relative.dot(basis_u)
    y_coord = relative.dot(basis_v)
    projected = np.stack([x_coord, y_coord], axis=1)
    hull = ConvexHull(projected)
    polygon_2d = projected[hull.vertices]
    perimeter = float(
        np.sum(
            np.linalg.norm(
                np.diff(np.vstack([polygon_2d, polygon_2d[0]]), axis=0),
                axis=1,
            )
        )
    )
    return polygon, float(hull.volume), perimeter
