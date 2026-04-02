"""PyCASTA-like pocket detection based on alpha-shapes and discrete flow."""

from typing import Sequence

import numpy as np
from scipy.spatial import Delaunay

from topomt._private.molsysmt_preparation import build_heavy_receptor_view
from topomt._private.smonitor import signal
from topomt import pyunitwizard as puw


@signal(tags=['method', 'pycasta', 'native'])
def pycasta(
    molecular_system,
    selection: str = 'molecule_type == "protein"',
    structure_indices: int = 0,
    alpha: float = 0.2,
    min_pocket_volume: float = 0.05,
    merge_clusters: bool = True,
    merge_threshold: float = 1.8,
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
    Detect pockets using a PyCASTA-style approach.

    Bare-float defaults follow TopoMT canonical units:

    - `alpha=0.2` means `0.2 nm` (upstream default `2.0 Å`)
    - `min_pocket_volume=0.05` means `0.05 nm**3` (upstream default `50 Å^3`)
    - `merge_threshold=1.8` means `1.8 nm` (upstream default `18 Å`)
    """
    
    alpha_nm = float(puw.get_value(alpha, to_unit='nm')) if puw.is_quantity(alpha) else float(alpha)
    min_vol_nm3 = (
        float(puw.get_value(min_pocket_volume, to_unit='nm**3'))
        if puw.is_quantity(min_pocket_volume)
        else float(min_pocket_volume)
    )
    merge_threshold_nm = (
        float(puw.get_value(merge_threshold, to_unit='nm'))
        if puw.is_quantity(merge_threshold)
        else float(merge_threshold)
    )
    _, _, atom_indices, coords_nm = build_heavy_receptor_view(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )
    
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

    max_index = coords_nm.shape[0] - 1
    pockets = [
        pocket
        for pocket in pockets
        if all(0 <= tetra_index <= max_index for tetra_index in pocket)
    ]

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
    radii = np.empty(tetra_positions.shape[0], dtype=float)

    for index, tetra in enumerate(tetra_positions):
        if tetra.shape[0] != 4:
            radii[index] = np.inf
            continue

        atom_a, atom_b, atom_c, atom_d = tetra
        vector_ab = atom_b - atom_a
        vector_ac = atom_c - atom_a
        vector_ad = atom_d - atom_a
        matrix = np.vstack([vector_ab, vector_ac, vector_ad]).T

        try:
            rhs = 0.5 * np.array(
                [
                    np.dot(vector_ab, vector_ab),
                    np.dot(vector_ac, vector_ac),
                    np.dot(vector_ad, vector_ad),
                ]
            )
            solution = np.linalg.solve(matrix, rhs)
            radii[index] = np.linalg.norm(solution)
        except np.linalg.LinAlgError:
            radii[index] = np.inf

    return radii


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
        while steps < max_steps:
            lower = [
                j
                for j in neighbors[current]
                if (current_proxy - proxies[j]) > tol_fraction * current_proxy
            ]
            if not lower:
                if adaptive:
                    tol_fraction *= adaptive_factor
                    lower = [
                        j
                        for j in neighbors[current]
                        if (current_proxy - proxies[j]) > tol_fraction * current_proxy
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
    atom_a = tets[:, 0]
    atom_b = tets[:, 1]
    atom_c = tets[:, 2]
    atom_d = tets[:, 3]
    volumes = np.abs(
        np.einsum(
            'ij,ij->i',
            atom_a - atom_d,
            np.cross(atom_b - atom_d, atom_c - atom_d),
        )
    ) / 6.0
    return float(volumes.sum())
