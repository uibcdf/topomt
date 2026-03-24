"""Pocketeer-inspired pocket detection using alpha-spheres with SASA burial and graph clustering.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from typing import Sequence

import molsysmt as msm
import numpy as np
from scipy.spatial import Delaunay, cKDTree

from topomt.methods.pocket_geometry import (
    analytic_tetra_volume,
    bounding_metrics,
    marching_cubes_union,
)
from topomt._pyunitwizard import pyunitwizard as puw
from topomt._private.puw_utils import get_magnitude, get_magnitudes


@dataclass
class PocketeerSphere:
    sphere_id: int
    center: np.ndarray
    radius: float
    atom_indices: list[int]
    mean_sasa: float = 0.0


@dataclass
class PocketeerPocket:
    pocket_id: int
    spheres: list[PocketeerSphere]
    centroid: np.ndarray
    volume: float
    score: float


def pocketeer(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    r_min: float = 3.0,
    r_max: float = 6.0,
    sasa_threshold: float = 20.0,
    merge_distance: float = 1.75,
    min_spheres: int = 35,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    Detect pockets via alpha-spheres with SASA burial and graph clustering.
    """
    topo = msm.convert(molecular_system, to_form='molsysmt.MolSys', structure_indices=structure_indices)
    atom_indices = msm.select(molecular_system=topo, selection=selection, syntax=syntax)
    remove_idx = msm.select(
        molecular_system=topo,
        selection="group_type in ['water', 'ion', 'small molecule']",
        mask=atom_indices,
        syntax='MolSysMT',
    )
    if len(remove_idx) > 0:
        atom_indices = [idx for idx in atom_indices if idx not in remove_idx]

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
    
    # Safe Normalization to NM
    coords_nm = get_magnitudes(coords, unit='nm')
    r_min_nm = get_magnitude(r_min, unit='nm')
    r_max_nm = get_magnitude(r_max, unit='nm')
    merge_dist_nm = get_magnitude(merge_distance, unit='nm')

    if coords_nm.shape[0] < 4:
        return [], []

    # Delaunay -> circumspheres
    try:
        tri = Delaunay(coords_nm)
    except Exception as e:
        warnings.warn(f'Delaunay tessellation failed: {e}')
        return [], []

    tree = cKDTree(coords_nm)
    spheres: list[PocketeerSphere] = []
    for sid, simplex in enumerate(tri.simplices):
        tet = coords_nm[simplex]
        center, radius = _circumsphere(tet)
        if radius < r_min_nm or radius > r_max_nm:
            continue
        if not _is_sphere_empty(center, radius, tree, set(simplex.tolist())):
            continue
        spheres.append(PocketeerSphere(sphere_id=sid, center=center, radius=float(radius), atom_indices=simplex.tolist()))

    if not spheres:
        return [], []

    # SASA mean for defining atoms
    sasa_vals = _sasa_molsysmt(topo, atom_indices=atom_indices)
    for s in spheres:
        s.mean_sasa = float(np.mean(sasa_vals[np.asarray(s.atom_indices, int)])) if len(s.atom_indices) == 4 else 0.0

    buried = [s for s in spheres if s.mean_sasa < sasa_threshold]
    if not buried:
        return [], spheres

    # clustering via graph connectivity
    graph = _sphere_graph(buried, merge_dist_nm)
    clusters = _connected_components(graph)
    clusters = [c for c in clusters if len(c) >= min_spheres]
    pockets: list[PocketeerPocket] = []
    for pid, comp in enumerate(clusters):
        pocket_spheres = [buried[idx] for idx in comp]
        centers = np.array([s.center for s in pocket_spheres])
        centroid = centers.mean(axis=0)
        
        try:
            verts, faces, vol, _ = marching_cubes_union(centers, [s.radius for s in pocket_spheres], grid_spacing=0.075)
        except Exception:
            vol = 0.0

        if vol == 0.0:
            vol = float(len(pocket_spheres)) * (0.1**3)
            
        score = _score_pocket(vol * 1000.0, len(pocket_spheres), np.mean([s.radius for s in pocket_spheres]) * 10.0)
        pockets.append(PocketeerPocket(pocket_id=pid, spheres=pocket_spheres, centroid=centroid, volume=vol, score=score))

    pockets.sort(key=lambda p: p.score, reverse=True)
    return pockets, buried


def _circumsphere(tet: np.ndarray) -> tuple[np.ndarray, float]:
    a = tet[0]
    b = tet[1] - a
    c = tet[2] - a
    d = tet[3] - a
    A = 2.0 * np.array([b, c, d])
    bvec = np.array([np.dot(b, b), np.dot(c, c), np.dot(d, d)])
    try:
        rel = np.linalg.solve(A, bvec)
        center = rel + a
        r = float(np.linalg.norm(rel))
        return center, r
    except np.linalg.LinAlgError:
        return tet.mean(axis=0), 0.0


def _is_sphere_empty(center: np.ndarray, radius: float, tree: cKDTree, exclude: set[int], tol: float = 1e-7) -> bool:
    close = tree.query_ball_point(center, radius)
    for idx in close:
        if idx in exclude:
            continue
        dist = np.linalg.norm(tree.data[idx] - center)
        if dist < radius - tol:
            return False
    return True


def _sphere_graph(spheres: list[PocketeerSphere], dist_th: float) -> dict[int, set[int]]:
    if not spheres:
        return {}
    centers = np.array([s.center for s in spheres])
    tree = cKDTree(centers)
    graph: dict[int, set[int]] = {i: set() for i in range(len(spheres))}
    for i, c in enumerate(centers):
        neigh = tree.query_ball_point(c, dist_th)
        for j in neigh:
            if i == j:
                continue
            graph[i].add(j)
            graph[j].add(i)
    return graph


def _connected_components(graph: dict[int, set[int]]) -> list[list[int]]:
    visited = set()
    comps: list[list[int]] = []
    for node in graph:
        if node in visited:
            continue
        stack = [node]
        comp: list[int] = []
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            comp.append(cur)
            stack.extend(graph[cur])
        comps.append(comp)
    return comps


def _sasa_molsysmt(topo, atom_indices: Sequence[int]) -> np.ndarray:
    warnings.warn('SASA backend not configured; mean_sasa set to 0.0 for all spheres.')
    return np.zeros(len(atom_indices))


def _score_pocket(volume_a3: float, n_spheres: int, avg_radius_a: float, v_ref: float = 500.0, n_ref: float = 50.0, r_win=(3.0, 6.0)) -> float:
    score = 0.0
    score += volume_a3 / v_ref
    score += n_spheres / n_ref
    if r_win[0] <= avg_radius_a <= r_win[1]:
        score += 2.0
    return float(score)
