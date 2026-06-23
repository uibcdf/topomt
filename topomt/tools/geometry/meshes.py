"""Mesh-oriented geometric helpers."""

from collections.abc import Sequence

import numpy as np
from depdigest import dep_digest


def _mesh_volume_area(vertices: np.ndarray, faces: np.ndarray) -> tuple[float, float]:
    """Return volume and area of a triangular mesh."""

    verts = np.asarray(vertices, dtype=float)
    tri = np.asarray(faces, dtype=int)
    if verts.ndim != 2 or verts.shape[1] != 3:
        raise ValueError('vertices must have shape (n_vertices, 3)')
    if tri.ndim != 2 or tri.shape[1] != 3:
        raise ValueError('faces must have shape (n_faces, 3)')
    if verts.size == 0 or tri.size == 0:
        return 0.0, 0.0
    if not np.all(np.isfinite(verts)):
        raise ValueError('vertices must contain finite values')
    if np.any((tri < 0) | (tri >= verts.shape[0])):
        raise ValueError('faces contain out-of-range vertex indices')

    tris = verts[tri]
    v0 = tris[:, 0]
    v1 = tris[:, 1]
    v2 = tris[:, 2]
    cross = np.cross(v1 - v0, v2 - v0)
    area = 0.5 * np.linalg.norm(cross, axis=1).sum()
    volume = abs(np.einsum('ij,ij->i', v0, cross).sum()) / 6.0
    return float(volume), float(area)


@dep_digest('skimage')
def marching_cubes_union(
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
    grid_spacing: float = 0.5,
    iso_level: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Build a mesh of the union of spheres via marching cubes."""

    if grid_spacing <= 0.0:
        raise ValueError('grid_spacing must be positive')
    c = np.asarray(centers, dtype=float)
    r = np.asarray(radii, dtype=float)
    if c.ndim != 2 or c.shape[1] != 3:
        raise ValueError('centers must have shape (n_spheres, 3)')
    if r.ndim != 1 or r.shape[0] != c.shape[0]:
        raise ValueError('radii must have shape (n_spheres,)')
    if not np.all(np.isfinite(c)):
        raise ValueError('centers must contain finite values')
    if not np.all(np.isfinite(r)):
        raise ValueError('radii must contain finite values')
    if np.any(r < 0.0):
        raise ValueError('radii must be non-negative')
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
