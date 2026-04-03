"""Primitive geometric operations."""

import numpy as np


def triangle_area(points: np.ndarray) -> float:
    """Return the area of a triangle from its 3D coordinates."""

    pts = np.asarray(points, dtype=float)
    if pts.shape != (3, 3):
        return 0.0
    return float(0.5 * np.linalg.norm(np.cross(pts[1] - pts[0], pts[2] - pts[0])))
