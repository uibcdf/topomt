"""Convex-hull-based geometric descriptors."""

from collections.abc import Sequence

import numpy as np
from scipy.spatial import ConvexHull


def convex_hull_metrics(points: Sequence[Sequence[float]]) -> tuple[float | None, float | None]:
    """Compute convex-hull volume and area."""

    pts = np.asarray(points, dtype=float)
    if pts.shape[0] < 4:
        return None, None
    try:
        hull = ConvexHull(pts)
        return float(hull.volume), float(hull.area)
    except Exception:
        return None, None
