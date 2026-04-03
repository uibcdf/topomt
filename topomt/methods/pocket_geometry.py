"""
Geometry and analysis utilities for pocket characterization.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence, Dict, List, Union, Tuple, Set

import numpy as np
import molsysmt as msm
from scipy.spatial import ConvexHull, distance_matrix
# from skimage.measure import marching_cubes  <-- moved to function
from scipy.spatial.distance import cdist
from scipy.cluster.hierarchy import fcluster, linkage
# import py3Dmol <-- moved to function
from depdigest import dep_digest
from topomt.tools.features.pockets import (
    apolar_ratio,
    get_physicochemical_properties,
    nonpolar_ratio_from_sasa,
)


def _to_numpy(array: Iterable) -> np.ndarray:
    return np.asarray(array, dtype=float)


def union_volume_monte_carlo(
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
    n_samples: int = 200_000,
    rng: np.random.Generator | None = None,
) -> float:
    """Estimate the volume of the union of spheres by Monte Carlo sampling.

    Parameters
    ----------
    centers : array-like, shape (n, 3)
        Sphere centers (alpha-sphere centers).
    radii : array-like, shape (n,)
        Sphere radii (same length as centers).
    n_samples : int, optional
        Number of random points to sample inside the bounding box.
    rng : np.random.Generator, optional
        Random generator for reproducibility.

    Returns
    -------
    volume : float
        Estimated volume in the same units as the input coordinates cubed.
    """
    if rng is None:
        rng = np.random.default_rng()

    c = _to_numpy(centers)
    r = _to_numpy(radii).reshape(-1, 1)
    if c.shape[0] == 0:
        return 0.0

    mins = np.min(c - r, axis=0)
    maxs = np.max(c + r, axis=0)
    box_vol = float(np.prod(maxs - mins))

    pts = rng.uniform(low=mins, high=maxs, size=(n_samples, 3))

    # chunked evaluation to keep memory reasonable
    inside = 0
    chunk = 50_000
    r2 = (r.squeeze()) ** 2
    for start in range(0, n_samples, chunk):
        stop = min(start + chunk, n_samples)
        sub = pts[start:stop]
        # dist^2 to all centers
        d2 = ((sub[:, None, :] - c[None, :, :]) ** 2).sum(axis=2)
        mask = np.any(d2 <= r2, axis=1)
        inside += int(np.sum(mask))

    frac = inside / n_samples
    return box_vol * frac


def convex_hull_metrics(points: Sequence[Sequence[float]]) -> tuple[float | None, float | None]:
    """Compute volume and area from the convex hull of input points.

    Parameters
    ----------
    points : array-like, shape (n, 3)
        Points defining the pocket boundary (e.g., atoms touching alpha-spheres).

    Returns
    -------
    volume : float or None
        Convex hull volume. None if hull cannot be built (fewer than 4 non-coplanar points).
    area : float or None
        Convex hull surface area. None if hull cannot be built.
    """
    pts = _to_numpy(points)
    if pts.shape[0] < 4:
        return None, None
    try:
        hull = ConvexHull(pts)
        return float(hull.volume), float(hull.area)
    except Exception:
        return None, None


def mouth_area_on_plane(
    mouth_points: Sequence[Sequence[float]],
    plane_point: Sequence[float],
    plane_normal: Sequence[float],
) -> float:
    """Estimate mouth area by projecting boundary points onto a plane and taking their convex hull.

    Parameters
    ----------
    mouth_points : array-like, shape (n, 3)
        Points defining the mouth rim (atoms or sphere centers near the opening).
    plane_point : array-like, shape (3,)
        A point on the mouth plane.
    plane_normal : array-like, shape (3,)
        Normal vector of the mouth plane.

    Returns
    -------
    area : float
        Area of the projected convex hull. Returns 0.0 if fewer than 3 points.
    """
    pts = _to_numpy(mouth_points)
    if pts.shape[0] < 3:
        return 0.0

    p0 = _to_numpy(plane_point)
    n = _to_numpy(plane_normal)
    norm = np.linalg.norm(n)
    if norm == 0:
        return 0.0
    n_unit = n / norm

    # Build an orthonormal basis (u, v) on the plane
    # Choose a vector not colinear with n_unit
    ref = np.array([1.0, 0.0, 0.0]) if abs(n_unit[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(n_unit, ref)
    u /= np.linalg.norm(u)
    v = np.cross(n_unit, u)

    # Project points to 2D coordinates in the plane basis
    rel = pts - p0
    x = rel.dot(u)
    y = rel.dot(v)
    proj = np.stack([x, y], axis=1)

    if proj.shape[0] < 3:
        return 0.0
    try:
        hull = ConvexHull(proj)
        return float(hull.area)
    except Exception:
        # fallback to shoelace on all points if hull fails
        order = np.argsort(np.arctan2(proj[:, 1], proj[:, 0]))
        poly = proj[order]
        area = 0.5 * abs(np.dot(poly[:, 0], np.roll(poly[:, 1], 1)) - np.dot(poly[:, 1], np.roll(poly[:, 0], 1)))
        return float(area)


def cross_section_profile(
    centers: Sequence[Sequence[float]],
    axis: Sequence[float],
    n_bins: int = 20,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a radial profile along a given axis (useful for channels/bottlenecks).

    Parameters
    ----------
    centers : array-like, shape (n, 3)
        Points sampling the cavity (alpha-sphere centers).
    axis : array-like, shape (3,)
        Direction vector defining the axis.
    n_bins : int, optional
        Number of slices along the axis.

    Returns
    -------
    bin_centers : ndarray, shape (n_bins,)
        Positions along the axis (projected coordinate).
    radial_max : ndarray, shape (n_bins,)
        Maximum radial distance to the axis per slice.
    """
    pts = _to_numpy(centers)
    a = _to_numpy(axis)
    norm = np.linalg.norm(a)
    if norm == 0:
        raise ValueError('Axis vector cannot be zero.')
    a_unit = a / norm

    # projections along axis
    t = pts.dot(a_unit)
    t_min, t_max = t.min(), t.max()
    bins = np.linspace(t_min, t_max, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    radial_max = np.zeros(n_bins, dtype=float)

    # perpendicular distances
    # distance from point p to axis: |p - (p·â)â|
    proj = np.outer(t, a_unit)
    perp = pts - proj
    r = np.linalg.norm(perp, axis=1)

    digit = np.digitize(t, bins) - 1
    for i in range(n_bins):
        mask = digit == i
        if np.any(mask):
            radial_max[i] = r[mask].max()
        else:
            radial_max[i] = 0.0
    return bin_centers, radial_max


def min_cross_section_radius(
    centers: Sequence[Sequence[float]],
    axis: Sequence[float],
    n_bins: int = 20,
) -> float:
    """Return the minimum cross-section radius along an axis (bottleneck estimate)."""
    _, radial = cross_section_profile(centers, axis, n_bins=n_bins)
    if radial.size == 0:
        return 0.0
    return float(radial[radial > 0].min()) if np.any(radial > 0) else 0.0


@dep_digest('skimage')
def marching_cubes_union(
    centers: Sequence[Sequence[float]],
    radii: Sequence[float],
    grid_spacing: float = 0.5,
    iso_level: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Build a mesh of the union of spheres via marching cubes and return vertices, faces, volume, area."""
    c = _to_numpy(centers)
    r = _to_numpy(radii)
    if c.shape[0] == 0:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=int), 0.0, 0.0

    mins = np.min(c - r[:, None], axis=0) - 1.0
    maxs = np.max(c + r[:, None], axis=0) + 1.0
    grid_shape = np.ceil((maxs - mins) / grid_spacing).astype(int) + 1

    xs = np.linspace(mins[0], maxs[0], grid_shape[0])
    ys = np.linspace(mins[1], maxs[1], grid_shape[1])
    zs = np.linspace(mins[2], maxs[2], grid_shape[2])
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing='ij')
    grid = np.stack([X, Y, Z], axis=-1)

    # signed distance: min over spheres of (|p-c| - r)
    dist = np.full(grid_shape, np.inf, dtype=float)
    for ci, ri in zip(c, r):
        d = np.linalg.norm(grid - ci, axis=-1) - ri
        dist = np.minimum(dist, d)

    from skimage.measure import marching_cubes

    verts, faces, _, _ = marching_cubes(dist, level=iso_level, spacing=(grid_spacing,) * 3)
    # marching_cubes coords are in grid index space times spacing; shift origin:
    verts = verts + np.array([mins[0], mins[1], mins[2]])

    # volume/area from faces
    volume, area = _mesh_volume_area(verts, faces)
    return verts, faces, volume, area


def _mesh_volume_area(vertices: np.ndarray, faces: np.ndarray) -> tuple[float, float]:
    """Compute volume and area of a triangular mesh."""
    v = vertices
    f = faces
    if len(f) == 0:
        return 0.0, 0.0
    tris = v[f]  # (n, 3, 3)
    # area
    cross = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    area = 0.5 * np.linalg.norm(cross, axis=1).sum()
    # volume (signed)
    volume = (np.einsum('ij,ij->i', tris[:, 0], cross)).sum() / 6.0
    return float(abs(volume)), float(area)


def clip_mesh_with_plane(
    vertices: np.ndarray,
    faces: np.ndarray,
    plane_point: Sequence[float],
    plane_normal: Sequence[float],
) -> tuple[np.ndarray, float, float]:
    """Intersect a mesh with a plane and return the intersection polygon, its area and perimeter."""
    p0 = _to_numpy(plane_point)
    n = _to_numpy(plane_normal)
    n_norm = np.linalg.norm(n)
    if n_norm == 0:
        return np.zeros((0, 3)), 0.0, 0.0
    n_unit = n / n_norm

    # signed distances of vertices to plane
    d = (vertices - p0) @ n_unit
    poly_pts = []

    for tri in faces:
        idx = tri
        v_tri = vertices[idx]
        d_tri = d[idx]
        # edges: (0,1), (1,2), (2,0)
        for (i, j) in ((0, 1), (1, 2), (2, 0)):
            di, dj = d_tri[i], d_tri[j]
            if di * dj < 0 or di == 0 or dj == 0:
                t = di / (di - dj) if (di - dj) != 0 else 0.0
                pt = v_tri[i] + t * (v_tri[j] - v_tri[i])
                poly_pts.append(pt)

    if len(poly_pts) < 3:
        return np.zeros((0, 3)), 0.0, 0.0

    poly = np.unique(np.round(poly_pts, decimals=6), axis=0)
    if poly.shape[0] < 3:
        return np.zeros((0, 3)), 0.0, 0.0

    # project to 2D basis on plane for area/perimeter
    ref = np.array([1.0, 0.0, 0.0]) if abs(n_unit[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(n_unit, ref)
    u /= np.linalg.norm(u)
    v = np.cross(n_unit, u)

    rel = poly - p0
    x = rel.dot(u)
    y = rel.dot(v)
    proj = np.stack([x, y], axis=1)
    hull = ConvexHull(proj)
    perim = 0.0
    verts2d = proj[hull.vertices]
    perim = float(np.sum(np.linalg.norm(np.diff(np.vstack([verts2d, verts2d[0]]), axis=0), axis=1)))
    return poly, float(hull.area), perim


def bounding_metrics(points: Sequence[Sequence[float]]) -> dict[str, float | np.ndarray]:
    """Compute oriented bounding box (via PCA) and axis lengths for elongation/orientation."""
    pts = _to_numpy(points)
    if pts.shape[0] == 0:
        return {
            'centroid': np.zeros(3),
            'axes': np.zeros((3, 3)),
            'lengths': np.zeros(3),
            'elongation': 0.0,
        }
    centroid = pts.mean(axis=0)
    centered = pts - centroid
    cov = centered.T @ centered / max(1, pts.shape[0] - 1)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    # project points and get extents
    proj = centered @ vecs
    mins = proj.min(axis=0)
    maxs = proj.max(axis=0)
    lengths = maxs - mins
    elong = lengths[0] / lengths[1] if lengths[1] > 0 else math.inf
    return {
        'centroid': centroid,
        'axes': vecs,
        'lengths': lengths,
        'elongation': float(elong),
    }


def effective_center_radius(points: Sequence[Sequence[float]]) -> tuple[np.ndarray, float, float]:
    """Return centroid, mean radial distance, and max radial distance (effective radius)."""
    pts = _to_numpy(points)
    if pts.shape[0] == 0:
        return np.zeros(3), 0.0, 0.0
    centroid = pts.mean(axis=0)
    dists = np.linalg.norm(pts - centroid, axis=1)
    return centroid, float(dists.mean()), float(dists.max())


def shortest_path_length(
    centers: Sequence[Sequence[float]],
    neighbor_pairs: Sequence[Sequence[int]],
    start_indices: Sequence[int],
    end_indices: Sequence[int],
) -> float:
    """Compute shortest path length over a graph of alpha-sphere centers.

    Parameters
    ----------
    centers : array-like, shape (n, 3)
        Node coordinates.
    neighbor_pairs : iterable of (i, j)
        Edges between alpha-spheres (e.g., sharing >= k atoms).
    start_indices : iterable of int
        Source nodes (e.g., mouth A).
    end_indices : iterable of int
        Target nodes (e.g., mouth B).
    """
    import heapq

    pts = _to_numpy(centers)
    n = pts.shape[0]
    adj: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for i, j in neighbor_pairs:
        i = int(i)
        j = int(j)
        w = float(np.linalg.norm(pts[i] - pts[j]))
        adj[i].append((j, w))
        adj[j].append((i, w))

    targets = set(int(i) for i in end_indices)
    dist = [math.inf] * n
    pq: list[tuple[float, int]] = []
    for s in start_indices:
        dist[int(s)] = 0.0
        heapq.heappush(pq, (0.0, int(s)))

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u in targets:
            return d
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return math.inf


def thickness_profile(
    centers: Sequence[Sequence[float]],
    axis: Sequence[float],
    neighbor_pairs: Sequence[Sequence[int]] | None = None,
    n_bins: int = 20,
) -> tuple[np.ndarray, np.ndarray]:
    """Continuous thickness profile along axis, averaging local radii from distances to neighbors."""
    pts = _to_numpy(centers)
    a = _to_numpy(axis)
    norm = np.linalg.norm(a)
    if norm == 0:
        raise ValueError('Axis vector cannot be zero.')
    a_unit = a / norm
    t = pts.dot(a_unit)
    t_min, t_max = t.min(), t.max()
    bins = np.linspace(t_min, t_max, n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    # local radius proxy: min distance to any neighbor (or overall)
    if neighbor_pairs is not None:
        adj = [[] for _ in range(len(pts))]
        for i, j in neighbor_pairs:
            i = int(i)
            j = int(j)
            d = np.linalg.norm(pts[i] - pts[j])
            adj[i].append(d)
            adj[j].append(d)
        local_r = np.array([min(nei) / 2 if nei else 0.0 for nei in adj])
    else:
        # fallback: distance to 2nd nearest neighbor as diameter estimate
        from sklearn.neighbors import NearestNeighbors

        nn = NearestNeighbors(n_neighbors=min(3, len(pts)), algorithm='auto').fit(pts)
        dists, _ = nn.kneighbors(pts)
        # exclude self (0)
        local_r = dists[:, 1] / 2.0 if dists.shape[1] > 1 else np.zeros(len(pts))

    profile = np.zeros(n_bins, dtype=float)
    counts = np.zeros(n_bins, dtype=int)
    digit = np.digitize(t, bins) - 1
    for i in range(n_bins):
        mask = digit == i
        if np.any(mask):
            profile[i] = local_r[mask].mean()
            counts[i] = mask.sum()
    return bin_centers, profile


# ---------------------------------------------------------------------------
# Pocket characterization utilities (reimplemented in our own style)
# ---------------------------------------------------------------------------


def analytic_tetra_volume(tetra_positions: np.ndarray, indices: Sequence[int] | Sequence[Sequence[int]]) -> float:
    """
    Compute the exact volume of a set of tetrahedra.

    This function calculates the volume of the Delaunay tetrahedra that make up
    the topological void of the pocket. This is consistent with CASTp's analytical
    method for determining the 'Dual Complex Volume'.

    Parameters
    ----------
    tetra_positions : ndarray
        Coordinates of the vertices.
        Can be (N_atoms, 3) if indices are lists of 4 ints.
        Can be (N_tet, 4, 3) if indices are just linear indices to select from N_tet.
    indices : Sequence[int] or Sequence[Sequence[int]]
        Indices defining the tetrahedra to sum.
        
    Returns
    -------
    float
        The total volume of the selected tetrahedra.
    """
    # Case 1: indices are a list of tetrahedra definitions (list of 4 ints) pointing to tetra_positions (N_atoms, 3)
    # Case 2: tetra_positions are already (N_tet, 4, 3) and indices are just selection indices (M,)
    
    tets = tetra_positions[np.asarray(indices, dtype=int)]
    
    if tets.ndim != 3 or tets.shape[1] != 4 or tets.shape[2] != 3:
         # Attempt to reshape or validate
         # If user passed (N_atoms, 3) and indices (M, 4), numpy fancy indexing produces (M, 4, 3) -> CORRECT
         # If user passed (N_tet, 4, 3) and indices (M,), numpy fancy indexing produces (M, 4, 3) -> CORRECT
         # So we just check if result is (M, 4, 3)
         if tets.ndim != 3 or tets.shape[-2:] != (4, 3):
             raise ValueError(f"Invalid shape for tetrahedra: {tets.shape}. Expected (N, 4, 3).")

    a, b, c, d = tets[:, 0], tets[:, 1], tets[:, 2], tets[:, 3]
    # Scalar triple product: dot(a-d, cross(b-d, c-d))
    # Volume = 1/6 * | det |
    vol = np.abs(np.einsum('ij,ij->i', a - d, np.cross(b - d, c - d))) / 6.0
    return float(vol.sum())


def mouth_area_from_faces(
    faces: Sequence[Tuple[int, int, int]],
    atom_coords: np.ndarray,
) -> float:
    """
    Compute the total area of specific triangular faces.
    
    This is used to calculate the exact area of the 'Mouths' of pockets,
    where a mouth is defined as the set of Delaunay triangles connecting 
    the pocket tetrahedra to the outside (bulk solvent) or forbidden region.

    Parameters
    ----------
    faces : Sequence[Tuple[int, int, int]]
        List of triangles, where each triangle is a tuple of 3 atom indices.
    atom_coords : ndarray (N, 3)
        Coordinates of the atoms.

    Returns
    -------
    float
        Total area of the faces.
    """
    total_area = 0.0
    if not faces:
        return 0.0
        
    for face in faces:
        pts = atom_coords[list(face)] # (3, 3)
        total_area += _triangle_area(pts)
        
    return float(total_area)


def mouth_metrics_from_tetrahedra(
    pocket_indices: Sequence[int],
    simplices: np.ndarray,
    atom_coords: np.ndarray,
) -> dict:
    """Compute mouth area/perimeter and rim atoms from pocket boundary faces (heuristic)."""
    face_count = {}
    for idx in pocket_indices:
        atoms = simplices[idx]
        faces = [
            tuple(sorted((atoms[0], atoms[1], atoms[2]))),
            tuple(sorted((atoms[0], atoms[1], atoms[3]))),
            tuple(sorted((atoms[0], atoms[2], atoms[3]))),
            tuple(sorted((atoms[1], atoms[2], atoms[3]))),
        ]
        for face in faces:
            face_count[face] = face_count.get(face, 0) + 1
    boundary_faces = [face for face, count in face_count.items() if count == 1]
    
    # Use the specific function for area
    total_area = mouth_area_from_faces(boundary_faces, atom_coords)
    
    total_perim = 0.0
    rim_atoms: set[int] = set()
    centroids = []
    for face in boundary_faces:
        pts = atom_coords[list(face)]
        centroids.append(pts.mean(axis=0))
        edges = [(face[i], face[j]) for i, j in [(0, 1), (1, 2), (2, 0)]]
        total_perim += sum(np.linalg.norm(atom_coords[e[0]] - atom_coords[e[1]]) for e in edges)
        rim_atoms.update(face)
    mouth_center = np.mean(centroids, axis=0) if centroids else np.zeros(3)
    return {
        'mouth_area': float(total_area),
        'mouth_perimeter': float(total_perim),
        'rim_atoms': list(rim_atoms),
        'mouth_center': mouth_center,
    }


def _triangle_area(pts: np.ndarray) -> float:
    """Area of a triangle given 3x3 coordinates."""
    if pts.shape != (3, 3):
        return 0.0
    return 0.5 * np.linalg.norm(np.cross(pts[1] - pts[0], pts[2] - pts[0]))


def representative_points_from_tetra(pockets: Sequence[Sequence[int]], tetra_positions: np.ndarray) -> list[np.ndarray]:
    """Centroid of all tetra vertices per pocket."""
    reps = []
    for pocket in pockets:
        if len(pocket) == 0:
            reps.append(np.zeros(3))
            continue
        coords = tetra_positions[np.asarray(pocket, int)].reshape(-1, 3)
        reps.append(coords.mean(axis=0))
    return reps


def simple_ranking(volumes: Sequence[float], pockets: Sequence[Sequence[int]], alpha: float = 1.0, beta: float = 0.1) -> list[float]:
    """Volume-based ranking with pocket size bonus."""
    scores = []
    for v, p in zip(volumes, pockets):
        scores.append(alpha * v + beta * len(p))
    return scores


def ligand_contact_distances(
    pocket_points: np.ndarray,
    ligand_coords: np.ndarray,
) -> dict[str, float | None]:
    """Min/mean/max distances between pocket points and ligand coords."""
    if pocket_points.size == 0 or ligand_coords.size == 0:
        return {'min': None, 'mean': None, 'max': None}
    dist = cdist(pocket_points, ligand_coords)
    return {
        'min': float(dist.min()),
        'mean': float(dist.mean()),
        'max': float(dist.max()),
    }


# ---------------------------------------------------------------------------
# AlphaSpace-inspired extras
# ---------------------------------------------------------------------------


def jaccard_overlap_clusters(
    lining_lists: list[list[int]],
    overlap_cutoff: float,
    total_index: int | None = None,
) -> dict[int, list[int]]:
    """Cluster pockets by Jaccard distance of lining-atom sets (AlphaSpace-like overlap clustering)."""
    if total_index is None:
        total_index = max((max(lst) for lst in lining_lists if lst), default=0) + 1
    if total_index <= 0 or not lining_lists:
        return {}

    # build binary vectors
    mat = np.zeros((len(lining_lists), total_index), dtype=int)
    for i, lst in enumerate(lining_lists):
        mat[i, np.asarray(lst, int)] = 1
    intersection = mat @ mat.T
    union = np.add.outer(mat.sum(axis=1), mat.sum(axis=1)) - intersection
    with np.errstate(divide='ignore', invalid='ignore'):
        jaccard = 1.0 - intersection / union
    jaccard[np.isnan(jaccard)] = 1.0
    z = linkage(distance_matrix(jaccard, jaccard), method='average')
    labels = fcluster(z, t=overlap_cutoff, criterion='distance') - 1
    clusters: dict[int, list[int]] = {}
    for idx, lab in enumerate(labels):
        clusters.setdefault(int(lab), []).append(idx)
    return clusters


def ligand_contact_mask(vertices: np.ndarray, ligand_coords: np.ndarray, hit_dist: float) -> np.ndarray:
    """Return boolean mask of vertices closer than hit_dist to any ligand atom."""
    if len(vertices) == 0 or len(ligand_coords) == 0:
        return np.zeros(len(vertices), dtype=bool)
    dist = cdist(vertices, ligand_coords)
    return (np.min(dist, axis=1) < hit_dist)


def sasa_contact_validation(
    pocket_coords: np.ndarray,
    ligand_coords: np.ndarray,
    atom_radii: np.ndarray | float | None = None,
    probe_radius: float = 1.4,
    contact_threshold: float = 1.0,
) -> dict[str, float]:
    """
    Distance-based proxy for SASA contact: counts pocket atoms whose spheres (r+probe) overlap ligand atoms.

    Parameters
    ----------
    pocket_coords : ndarray, shape (n, 3)
        Coordinates of pocket atoms.
    ligand_coords : ndarray, shape (m, 3)
        Coordinates of ligand atoms.
    atom_radii : ndarray or float, optional
        Atomic radii for pocket atoms. If float, applied to all; if None, uses 0.0.
    probe_radius : float, optional
        Solvent probe radius (Å).
    contact_threshold : float, optional
        Extra slack distance to count contact.

    Returns
    -------
    dict
        {'n_contact': int, 'fraction': float}
    """
    if pocket_coords.size == 0 or ligand_coords.size == 0:
        return {'n_contact': 0, 'fraction': 0.0}
    pocket_coords = np.asarray(pocket_coords, float)
    ligand_coords = np.asarray(ligand_coords, float)
    n_atoms = pocket_coords.shape[0]
    if atom_radii is None:
        radii = np.zeros(n_atoms, dtype=float)
    elif np.isscalar(atom_radii):
        radii = np.full(n_atoms, float(atom_radii))
    else:
        radii = np.asarray(atom_radii, float)
        if radii.shape[0] != n_atoms:
            raise ValueError('atom_radii length must match pocket_coords')
    dist = cdist(pocket_coords, ligand_coords)
    # min distance per pocket atom
    dmin = dist.min(axis=1)
    contact_mask = dmin < (radii + probe_radius + contact_threshold)
    n_contact = int(contact_mask.sum())
    frac = float(n_contact / n_atoms) if n_atoms else 0.0
    return {'n_contact': n_contact, 'fraction': frac}


def probe_scoring(
    vertices: np.ndarray,
    ligand_coords: np.ndarray,
    probe_weights: dict[str, float] | None = None,
    cutoff: float = 6.0,
    power: float = 2.0,
) -> dict[str, float]:
    """
    Simple distance-based probe scoring: sum_{v,l} w_probe * (cutoff / max(d, eps))^power.

    Parameters
    ----------
    vertices : ndarray, shape (n, 3)
        Alpha-sphere centers or pocket sample points.
    ligand_coords : ndarray, shape (m, 3)
        Ligand atom coordinates.
    probe_weights : dict, optional
        Map probe name -> weight. Defaults to {'C':1.0, 'N':0.8, 'O':0.7, 'X':1.0}.
    cutoff : float, optional
        Distance cutoff; beyond this, contribution decays strongly.
    power : float, optional
        Exponent for distance decay.

    Returns
    -------
    dict
        Scores per probe key.
    """
    if probe_weights is None:
        probe_weights = {'C': 1.0, 'N': 0.8, 'O': 0.7, 'X': 1.0}
    if vertices.size == 0 or ligand_coords.size == 0:
        return {k: 0.0 for k in probe_weights}
    dist = cdist(vertices, ligand_coords)
    eps = 1e-6
    inv = (cutoff / np.maximum(dist, eps)) ** power
    inv[dist > cutoff] = 0.0
    base = inv.sum()
    return {k: float(w * base) for k, w in probe_weights.items()}


# ---------------------------------------------------------------------------
# Simple visualization (py3Dmol) for pockets/alpha-spheres
# ---------------------------------------------------------------------------


@dep_digest('py3Dmol')
def view_pockets_py3dmol(
    atom_coords: np.ndarray,
    atom_elements: Sequence[str] | None,
    pockets: list[list[int]],
    sphere_centers: np.ndarray,
    sphere_radii: Sequence[float],
    *,
    sphere_opacity: float = 0.5,
    sphere_scale: float = 1.0,
    color_scheme: str = 'rainbow',
) -> 'py3Dmol.view':
    """Minimal py3Dmol viewer for alpha-sphere pockets (for quick inspection)."""
    import py3Dmol

    v = py3Dmol.view()
    # add atoms as spheres
    for coord, elem in zip(atom_coords, atom_elements or ['C'] * len(atom_coords)):
        v.addSphere(
            {
                'center': {'x': float(coord[0]), 'y': float(coord[1]), 'z': float(coord[2])},
                'radius': 0.5,
                'color': _element_color(elem),
                'opacity': 0.7,
            }
        )
    # colors per pocket
    colors = _color_palette(len(pockets), scheme=color_scheme)
    for pocket_idx, comp in enumerate(pockets):
        color = colors[pocket_idx % len(colors)]
        for s_idx in comp:
            c = sphere_centers[s_idx]
            r = sphere_radii[s_idx] * sphere_scale
            v.addSphere(
                {
                    'center': {'x': float(c[0]), 'y': float(c[1]), 'z': float(c[2])},
                    'radius': float(r),
                    'color': color,
                    'opacity': sphere_opacity,
                }
            )
    v.zoomTo()
    return v


def _color_palette(n: int, scheme: str = 'rainbow') -> list[str]:
    import colorsys
    if n <= 0:
        return []
    if scheme == 'rainbow':
        return [
            f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'
            for r, g, b in (colorsys.hsv_to_rgb(i / n, 0.8, 0.9) for i in range(n))
        ]
    elif scheme == 'grayscale':
        return [f'rgb({g},{g},{g})' for g in np.linspace(64, 224, n, dtype=int)]
    elif scheme == 'red_blue':
        return ['rgb(255,100,100)' if i % 2 == 0 else 'rgb(100,100,255)' for i in range(n)]
    return ['rgb(128,128,128)'] * n


def _element_color(element_symbol: str) -> str:
    """Basic element colors for atoms."""
    element_symbol = (element_symbol or 'C').upper()
    palette = {
        'H': 'rgb(255,255,255)',
        'C': 'rgb(50,50,50)',
        'N': 'rgb(64,64,255)',
        'O': 'rgb(255,0,0)',
        'S': 'rgb(255,200,50)',
        'P': 'rgb(255,150,0)',
    }
    return palette.get(element_symbol, 'rgb(180,180,180)')

