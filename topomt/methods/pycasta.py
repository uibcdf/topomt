"""PyCASTA-like pocket detection based on alpha-shapes and discrete flow on tetrahedra.
"""

from __future__ import annotations

import warnings
from typing import Iterable, Sequence

import molsysmt as msm
import numpy as np
from scipy.spatial import Delaunay
from topomt._private.puw_utils import get_magnitude, get_magnitudes


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
    return_atom_indices: bool = False,
):
    """
    Detect pockets using a PyCASTA-style approach. Internal logic in NM.
    """
    
    # Normalization to NM
    alpha_nm = get_magnitude(alpha, unit='nm')
    # 50 A^3 = 0.05 nm^3
    min_vol_nm3 = get_magnitude(min_pocket_volume, unit='nm**3') if not isinstance(min_pocket_volume, (int, float)) else min_pocket_volume / 1000.0
    merge_threshold_nm = get_magnitude(merge_threshold, unit='nm')

    from topomt import Topography
    topo_obj = Topography(molecular_system=molecular_system, structure_indices=structure_indices)
    molsys = topo_obj._molsys

    atom_indices = msm.select(molsys, selection=selection, syntax=syntax)
    remove_idx = msm.select(molsys, selection="group_type in ['water', 'ion', 'small molecule']", mask=atom_indices)
    if len(remove_idx) > 0:
        atom_indices = [idx for idx in atom_indices if idx not in remove_idx]

    atom_indices = msm.select(molsys, selection='atom_type not in ["H"]', mask=atom_indices)

    coords = msm.get(molsys, selection=atom_indices, structure_indices=structure_indices, coordinates=True)[0]
    coords_nm = get_magnitudes(coords, unit='nm')
    
    if coords_nm.shape[0] < 4:
        if return_atom_indices:
            return [], [], np.empty((0, 4), dtype=int), atom_indices
        return [], [], np.empty((0, 4), dtype=int)

    delaunay = Delaunay(coords_nm)
    simplices = delaunay.simplices
    tetra_pos = coords_nm[simplices]

    radii = _circumsphere_radii(tetra_pos)
    alpha_mask = radii < alpha_nm

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
        pockets = _merge_clusters(pockets, tetra_pos, merge_threshold_nm)

    volumes = []
    filtered = []
    for pocket in pockets:
        vol = _tetra_group_volume(tetra_pos, pocket)
        if vol >= min_vol_nm3:
            filtered.append(pocket)
            volumes.append(vol)

    pockets_vol = sorted(zip(filtered, volumes), key=lambda x: x[1], reverse=True)
    pockets_sorted = [p for p, _ in pockets_vol]
    volumes_sorted = [v for _, v in pockets_vol]
    if return_atom_indices:
        return pockets_sorted, volumes_sorted, simplices, atom_indices
    return pockets_sorted, volumes_sorted, simplices


def _circumsphere_radii(tetra_positions: np.ndarray) -> np.ndarray:
    a = tetra_positions[:, 0]
    b = tetra_positions[:, 1]
    c = tetra_positions[:, 2]
    d = tetra_positions[:, 3]
    ba = b - a
    ca = c - a
    da = d - a
    cross_cd = np.cross(ca, da)
    Ba = np.einsum('ij,ij->i', ba, cross_cd)
    vol6 = np.abs(Ba)
    a2 = np.sum(ba * ba, axis=1)
    b2 = np.sum(ca * ca, axis=1)
    c2 = np.sum(da * da, axis=1)
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
    if len(indices) == 0:
        return 0.0
    tets = tetra_positions[np.asarray(indices, dtype=int)]
    a = tets[:, 0]
    b = tets[:, 1]
    c = tets[:, 2]
    d = tets[:, 3]
    vol = np.abs(Ba := a[:,0]*((b[:,1]-d[:,1])*(c[:,2]-d[:,2]) - (b[:,2]-d[:,2])*(c[:,1]-d[:,1])) + \
                 a[:,1]*((b[:,2]-d[:,2])*(c[:,0]-d[:,0]) - (b[:,0]-d[:,0])*(c[:,2]-d[:,2])) + \
                 a[:,2]*((b[:,0]-d[:,0])*(c[:,1]-d[:,1]) - (b[:,1]-d[:,1])*(c[:,0]-d[:,0]))) / 6.0
    return float(vol.sum())
