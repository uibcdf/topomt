"""Mouth descriptor helpers."""

import numpy as np
from scipy.spatial import ConvexHull


def mouth_area_on_plane(
    mouth_points: np.ndarray,
    plane_point: np.ndarray,
    plane_normal: np.ndarray,
) -> float:
    """Estimate mouth area by projecting rim points onto a plane.

    Parameters
    ----------
    mouth_points : ndarray
        Points defining the mouth rim.
    plane_point : ndarray
        A point on the mouth plane.
    plane_normal : ndarray
        Normal vector of the mouth plane.

    Returns
    -------
    float
        Area of the projected convex hull. Returns ``0.0`` when fewer than
        three points are provided or the plane normal is degenerate.
    """

    points = np.asarray(mouth_points, dtype=float)
    if points.shape[0] < 3:
        return 0.0

    point = np.asarray(plane_point, dtype=float)
    normal = np.asarray(plane_normal, dtype=float)
    norm = np.linalg.norm(normal)
    if norm == 0:
        return 0.0
    normal_unit = normal / norm

    reference = np.array([1.0, 0.0, 0.0]) if abs(normal_unit[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    basis_u = np.cross(normal_unit, reference)
    basis_u /= np.linalg.norm(basis_u)
    basis_v = np.cross(normal_unit, basis_u)

    relative = points - point
    x_coord = relative.dot(basis_u)
    y_coord = relative.dot(basis_v)
    projected = np.stack([x_coord, y_coord], axis=1)

    if projected.shape[0] < 3:
        return 0.0

    try:
        hull = ConvexHull(projected)
        return float(hull.volume)
    except Exception:
        order = np.argsort(np.arctan2(projected[:, 1], projected[:, 0]))
        polygon = projected[order]
        area = 0.5 * abs(
            np.dot(polygon[:, 0], np.roll(polygon[:, 1], 1))
            - np.dot(polygon[:, 1], np.roll(polygon[:, 0], 1))
        )
        return float(area)
