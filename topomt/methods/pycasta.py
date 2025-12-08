"""PyCASTA-like pocket detection based on alpha-shapes and discrete flow on tetrahedra.

This is a lightweight reimplementation inspired by the pycasta project:
- Build a (weighted) Delaunay triangulation of atom coordinates (here unweighted).
- Keep tetrahedra whose circumsphere radius is below `alpha` (alpha-complex).
- On tetrahedra outside the alpha-complex, run a discrete flow toward minima of the
  proxy value (sigma_p * circumsphere radius) with a relative tolerance.
- Group tetrahedra by sinks and connectivity (shared faces) to form pockets.
- Optionally merge nearby pockets and filter by minimum volume.

Returns pockets as lists of tetrahedron indices (into the simplices array).
"""

from __future__ import annotations

import warnings
from typing import Iterable, Sequence

import molsysmt as msm
import numpy as np
from scipy.spatial import Delaunay

from topomt._private.digestion import digest


@digest()
def pycasta(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    alpha: float = 2.0,
    min_pocket_volume: float = 50.0,
    merge_clusters: bool = True,
    merge_threshold: float = 18.0,
    sigma_p: float = 1.4,
    tol_fraction: float = 0.01,
    max_steps: int = 100,
    adaptive: bool = True,
    adaptive_factor: float = 0.5,
    min_steps: int = 3,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    Detect pockets using a PyCASTA-style alpha-shape + discrete flow approach.

    Parameters
    ----------
    molecular_system
        Input molecular system (compatible with MolSysMT).
    selection : str, optional
        Atom selection (MolSysMT syntax).
    structure_indices : int, optional
        Structure index to use.
    alpha : float, optional
        Alpha threshold for the alpha-complex (tetra circumsphere radius cutoff).
    min_pocket_volume : float, optional
        Minimum pocket volume (sum of tetra volumes) to keep.
    merge_clusters : bool, optional
        Whether to merge pocket clusters whose centroids are within `merge_threshold`.
    merge_threshold : float, optional
        Distance threshold for merging pocket clusters (Å).
    sigma_p : float, optional
        Scaling for proxy values in the flow step (proxy = sigma_p * radius).
    tol_fraction : float, optional
        Relative tolerance for descending in the flow (neighbor must be this fraction lower).
    max_steps : int, optional
        Maximum flow steps per tetrahedron.
    adaptive : bool, optional
        If True, relax tolerance when stuck.
    adaptive_factor : float, optional
        Multiplicative factor to relax tolerance when no lower neighbor is found.
    min_steps : int, optional
        Minimum steps for a flow to be considered valid.
    syntax : str, optional
        Selection syntax for MolSysMT.

    Returns
    -------
    pockets : list[list[int]]
        Lists of tetrahedron indices (into the Delaunay simplices) per pocket, sorted by volume.
    volumes : list[float]
        Pocket volumes (Å^3), sorted in the same order as `pockets`.
    simplices : np.ndarray
        The Delaunay simplices used to define tetrahedra (indices into atom array).
    """
    topo = msm.convert(molecular_system, to_form='molsysmt.MolSys', structure_indices=structure_indices)
    atom_indices = msm.select(
        molecular_system=topo,
        selection=selection,
        syntax=syntax,
    )
    # remove water/ions/small molecules and hydrogens (mirrors fpocket4 cleaning)
    remove_idx = msm.select(
        molecular_system=topo,
        selection="group_type in ['water', 'ion', 'small molecule']",
        mask=atom_indices,
        syntax='MolSysMT',
    )
    if len(remove_idx) > 0:
        atom_indices = list(set(atom_indices) - set(remove_idx))

    atom_indices = msm.select(
        molecular_system=topo,
        selection='atom_type not in ["H"]',
        mask=atom_indices,
        syntax='MolSysMT',
    )

    coords = msm.get(
        molecular_system=topo,
        selection=atom_indices,
        structure_indices=structure_indices,
        coordinates=True,
    )[0]
    if coords.shape[0] < 4:
        return [], [], np.empty((0, 4), dtype=int)

    delaunay = Delaunay(coords)
    simplices = delaunay.simplices  # (n_tet, 4)
    tetra_pos = coords[simplices]

    radii = _circumsphere_radii(tetra_pos)
    alpha_mask = radii < alpha

    pockets = _flow_detection(
        simplices,
        alpha_mask,
        radii,
        sigma_p=sigma_p,
        tol_fraction=tol_fraction,
        max_steps=max_steps,
        adaptive=adaptive,
        adaptive_factor=adaptive_factor,
        min_steps=min_steps,
    )

    if merge_clusters:
        pockets = _merge_clusters(pockets, tetra_pos, merge_threshold)

    # volumes and filtering
    volumes = []
    filtered = []
    for pocket in pockets:
        vol = _tetra_group_volume(tetra_pos, pocket)
        if vol >= min_pocket_volume:
            filtered.append(pocket)
            volumes.append(vol)

    # sort by volume desc
    pockets_vol = sorted(zip(filtered, volumes), key=lambda x: x[1], reverse=True)
    pockets_sorted = [p for p, _ in pockets_vol]
    volumes_sorted = [v for _, v in pockets_vol]
    return pockets_sorted, volumes_sorted, simplices


def _circumsphere_radii(tetra_positions: np.ndarray) -> np.ndarray:
    """Circumsphere radius for each tetrahedron (vectorized)."""
    a = tetra_positions[:, 0]
    b = tetra_positions[:, 1]
    c = tetra_positions[:, 2]
    d = tetra_positions[:, 3]
    ba = b - a
    ca = c - a
    da = d - a
    # volume factor
    cross_cd = np.cross(ca, da)
    vol6 = np.abs(np.einsum('ij,ij->i', ba, cross_cd))
    # squared edge lengths
    a2 = np.sum(ba * ba, axis=1)
    b2 = np.sum(ca * ca, axis=1)
    c2 = np.sum(da * da, axis=1)
    # circumsphere radius formula: R = (abc)/(6V)
    numerator = np.sqrt(
        a2 * b2 * c2
        + 2 * np.sum(ba * ca, axis=1) * np.sum(ca * da, axis=1) * np.sum(da * ba, axis=1)
        - a2 * (np.sum(ca * da, axis=1) ** 2)
        - b2 * (np.sum(da * ba, axis=1) ** 2)
        - c2 * (np.sum(ba * ca, axis=1) ** 2)
    )
    with np.errstate(divide='ignore', invalid='ignore'):
        r = numerator / (2.0 * vol6)
    r[~np.isfinite(r)] = np.inf
    return r


def _flow_detection(
    simplices: np.ndarray,
    alpha_mask: np.ndarray,
    radii: np.ndarray,
    *,
    sigma_p: float,
    tol_fraction: float,
    max_steps: int,
    adaptive: bool,
    adaptive_factor: float,
    min_steps: int,
) -> list[list[int]]:
    """Discrete flow on empty tetrahedra; group by sinks and connectivity."""
    proxies = sigma_p * radii
    empty_idx = np.where(~alpha_mask)[0]

    face_to_tetra = {}
    for i, tet in enumerate(simplices):
        faces = [
            tuple(sorted(tet[[a, b, c]]))
            for (a, b, c) in [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
        ]
        for face in faces:
            face_to_tetra.setdefault(face, []).append(i)

    neighbors = {}
    for i in empty_idx:
        faces = [
            tuple(sorted(simplices[i, [a, b, c]]))
            for (a, b, c) in [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
        ]
        neigh = set()
        for f in faces:
            neigh.update(face_to_tetra.get(f, []))
        neighbors[i] = [j for j in neigh if j != i and not alpha_mask[j]]

    flow_target = {}
    for i in empty_idx:
        current = i
        steps = 0
        current_proxy = proxies[current]
        cur_tol = tol_fraction
        while steps < max_steps:
            lower = [
                j
                for j in neighbors[current]
                if (current_proxy - proxies[j]) > cur_tol * current_proxy
            ]
            if not lower:
                if adaptive:
                    cur_tol *= adaptive_factor
                    lower = [
                        j
                        for j in neighbors[current]
                        if (current_proxy - proxies[j]) > cur_tol * current_proxy
                    ]
                if not lower:
                    break
            next_cur = min(lower, key=lambda j: proxies[j])
            current = next_cur
            current_proxy = proxies[current]
            steps += 1
        if steps >= min_steps:
            flow_target[i] = current

    sink_groups = {}
    for i, sink in flow_target.items():
        sink_groups.setdefault(sink, []).append(i)

    pockets: list[list[int]] = []
    for _, group in sink_groups.items():
        # connectivity within sink group by shared faces
        graph = {idx: [] for idx in group}
        for idx, i in enumerate(group):
            for j in group[idx + 1 :]:
                if len(set(simplices[i]) & set(simplices[j])) == 3:
                    graph[i].append(j)
                    graph[j].append(i)
        visited = set()
        for node in group:
            if node in visited:
                continue
            comp = []
            stack = [node]
            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                visited.add(cur)
                comp.append(cur)
                stack.extend(graph[cur])
            pockets.append(comp)
    return pockets


def _merge_clusters(pockets: list[list[int]], tetra_positions: np.ndarray, threshold: float) -> list[list[int]]:
    """Merge pockets whose centroids are within the given threshold."""
    clusters = [list(p) for p in pockets]
    changed = True
    while changed:
        changed = False
        new_clusters: list[list[int]] = []
        merged = [False] * len(clusters)
        for i, ci in enumerate(clusters):
            if merged[i] or not ci:
                continue
            coords_i = np.concatenate(tetra_positions[ci], axis=0)
            centroid_i = coords_i.mean(axis=0)
            for j in range(i + 1, len(clusters)):
                if merged[j] or not clusters[j]:
                    continue
                coords_j = np.concatenate(tetra_positions[clusters[j]], axis=0)
                centroid_j = coords_j.mean(axis=0)
                if np.linalg.norm(centroid_i - centroid_j) < threshold:
                    ci = list(set(ci) | set(clusters[j]))
                    merged[j] = True
                    changed = True
                    coords_i = np.concatenate(tetra_positions[ci], axis=0)
                    centroid_i = coords_i.mean(axis=0)
            new_clusters.append(ci)
        clusters = new_clusters
    return clusters


def _tetra_group_volume(tetra_positions: np.ndarray, indices: Sequence[int]) -> float:
    """Sum of tetra volumes for a group of indices."""
    if len(indices) == 0:
        return 0.0
    tets = tetra_positions[np.asarray(indices, dtype=int)]
    a = tets[:, 0]
    b = tets[:, 1]
    c = tets[:, 2]
    d = tets[:, 3]
    vol = np.abs(np.einsum('ij,ij->i', a, np.cross(b - d, c - d))) / 6.0
    return float(vol.sum())
