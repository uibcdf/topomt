"""Mesh-oriented geometric helpers."""

from collections.abc import Sequence

import numpy as np
from depdigest import dep_digest


def _mesh_volume_area(vertices: np.ndarray, faces: np.ndarray) -> tuple[float, float]:
    """Return volume and area of a triangular mesh."""

    verts = np.asarray(vertices, dtype=float)
    tri = np.asarray(faces, dtype=int)
    if verts.size == 0 or tri.size == 0:
        return 0.0, 0.0

    tris = verts[tri]
    v0 = tris[:, 0]
    v1 = tris[:, 1]
    v2 = tris[:, 2]
    cross = np.cross(v1 - v0, v2 - v0)
    area = 0.5 * np.linalg.norm(cross, axis=1).sum()
    volume = np.abs(np.einsum('ij,ij->i', v0, cross)).sum() / 6.0
    return float(volume), float(area)


@dep_digest('skimage')
def marching_cubes_union(
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
    grid_spacing: float = 0.5,
    iso_level: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Build a mesh of the union of spheres via marching cubes."""

    c = np.asarray(centers, dtype=float)
    r = np.asarray(radii, dtype=float)
    if c.shape[0] == 0:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=int), 0.0, 0.0

    mins = np.min(c - r[:, None], axis=0) - 1.0
    maxs = np.max(c + r[:, None], axis=0) + 1.0
    grid_shape = np.ceil((maxs - mins) / grid_spacing).astype(int) + 1

    xs = np.linspace(mins[0], maxs[0], grid_shape[0])
    ys = np.linspace(mins[1], maxs[1], grid_shape[1])
    zs = np.linspace(mins[2], maxs[2], grid_shape[2])
    x_grid, y_grid, z_grid = np.meshgrid(xs, ys, zs, indexing='ij')
    grid = np.stack([x_grid, y_grid, z_grid], axis=-1)

    dist = np.full(grid_shape, np.inf, dtype=float)
    for center, radius in zip(c, r):
        delta = np.linalg.norm(grid - center, axis=-1) - radius
        dist = np.minimum(dist, delta)

    from skimage.measure import marching_cubes

    verts, faces, _, _ = marching_cubes(
        dist,
        level=iso_level,
        spacing=(grid_spacing,) * 3,
    )
    verts = verts + np.array([mins[0], mins[1], mins[2]])
    volume, area = _mesh_volume_area(verts, faces)
    return verts, faces, volume, area
