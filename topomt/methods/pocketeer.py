"""Pocketeer-inspired pocket detection using alpha-spheres with SASA burial and graph clustering."""

from __future__ import annotations

from dataclasses import dataclass
import warnings
import molsysmt as msm
import numpy as np
from scipy.spatial import Delaunay, cKDTree

from topomt._private.molsysmt_preparation import build_heavy_receptor_view
from topomt._private.smonitor import (
    PocketeerDelaunayWarning,
    PocketeerSasaBackendWarning,
    signal,
)
from topomt.methods.pocket_geometry import marching_cubes_union
from topomt import pyunitwizard as puw

MIN_RADIUS_A = 3.5
MAX_RADIUS_A = 5.0
SCORE_RADIUS_BONUS = 1.8
GRID_SPACING_NM = 0.075


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


@signal(tags=['method', 'pocketeer', 'native'])
def pocketeer(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    r_min: float = 3.0,
    r_max: float = 6.0,
    sasa_threshold: float | puw.Quantity = 20.0,
    merge_distance: float = 1.75,
    min_spheres: int = 35,
    syntax: str = 'MolSysMT',
    polar_probe_radius: float | puw.Quantity = 1.4,
    skip_digestion: bool = False,
    return_atom_indices: bool = False,
):
    """
    Detect pockets via alpha-spheres with SASA burial and graph clustering.

    Steps:
        1. Build a heavy-atom receptor view and compute Delaunay alpha spheres.
        2. Label spheres by SASA using the requested polar probe radius.
        3. Filter to buried spheres and cluster them via graph adjacency.
        4. Evaluate pocket descriptors (centroid, volume, score) and sort by score.
    """
    molsys, receptor, atom_indices, coords_nm = build_heavy_receptor_view(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )

    def _to_nm(value: float | puw.Quantity) -> float:
        if puw.is_quantity(value):
            return float(puw.get_value(value, to_unit='nm'))
        return float(value) / 10.0

    def _to_nm2(value: float | puw.Quantity) -> float:
        if puw.is_quantity(value):
            return float(puw.get_value(value, to_unit='nm**2'))
        return float(value) / 100.0

    r_min_nm = _to_nm(r_min)
    r_max_nm = _to_nm(r_max)
    merge_dist_nm = _to_nm(merge_distance)
    sasa_threshold_nm2 = _to_nm2(sasa_threshold)
    polar_probe_radius_nm = _to_nm(polar_probe_radius)
    min_spheres = max(1, int(min_spheres))

    if coords_nm.shape[0] < 4:
        if return_atom_indices:
            return [], [], atom_indices
        return [], []

    coords_ang = coords_nm * 10.0
    try:
        tri = Delaunay(coords_ang)
    except Exception as exc:
        warnings.warn(PocketeerDelaunayWarning(reason=str(exc)))
        if return_atom_indices:
            return [], [], atom_indices
        return [], []

    spheres: list[PocketeerSphere] = _extract_alpha_spheres(
        coords_nm, coords_ang, tri, r_min_nm, r_max_nm
    )
    if not spheres:
        if return_atom_indices:
            return [], [], atom_indices
        return [], []

    sasa_vals = _sasa_molsysmt(receptor, coords_nm, polar_probe_radius_nm)
    for sphere in spheres:
        if sphere.atom_indices:
            sphere.mean_sasa = float(np.mean(sasa_vals[np.asarray(sphere.atom_indices, int)]))

    buried = [sphere for sphere in spheres if sphere.mean_sasa < sasa_threshold_nm2]
    if not buried:
        if return_atom_indices:
            return [], spheres, atom_indices
        return [], spheres

    graph = _sphere_graph(buried, merge_dist_nm)
    clusters = [comp for comp in _connected_components(graph) if len(comp) >= min_spheres]

    pockets: list[PocketeerPocket] = []
    for pocket_id, component in enumerate(clusters):
        pocket_spheres = [buried[idx] for idx in component]
        centers = np.array([sphere.center for sphere in pocket_spheres])
        centroid = centers.mean(axis=0) if len(centers) else np.zeros(3)
        volume = _estimate_pocket_volume(pocket_spheres)
        avg_radius_nm = np.mean([sphere.radius for sphere in pocket_spheres]) if pocket_spheres else 0.0
        score = _score_pocket(volume, len(pocket_spheres), avg_radius_nm)
        pockets.append(
            PocketeerPocket(
                pocket_id=pocket_id,
                spheres=pocket_spheres,
                centroid=centroid,
                volume=volume,
                score=score,
            )
        )

    pockets.sort(key=lambda pocket: pocket.score, reverse=True)

    if return_atom_indices:
        return pockets, buried, atom_indices
    return pockets, buried


def _extract_alpha_spheres(
    coords_nm: np.ndarray,
    coords_ang: np.ndarray,
    tri: Delaunay,
    r_min: float,
    r_max: float,
) -> list[PocketeerSphere]:
    tree = cKDTree(coords_nm)
    spheres: list[PocketeerSphere] = []
    for sphere_id, simplex in enumerate(tri.simplices):
        tet_ang = coords_ang[simplex]
        center_ang, radius_ang = _circumsphere(tet_ang)
        center = center_ang / 10.0
        radius = radius_ang / 10.0
        if radius < r_min or radius > r_max:
            continue
        indices = simplex.tolist()
        if not _is_sphere_empty(center, radius, tree, set(indices)):
            continue
        spheres.append(
            PocketeerSphere(
                sphere_id=sphere_id,
                center=center,
                radius=float(radius),
                atom_indices=indices,
            )
        )
    return spheres


def _estimate_pocket_volume(pocket_spheres: list[PocketeerSphere]) -> float:
    if not pocket_spheres:
        return 0.0
    centers = np.array([sphere.center for sphere in pocket_spheres], dtype=float)
    radii = np.array([sphere.radius for sphere in pocket_spheres], dtype=float)
    try:
        _, _, volume, _ = marching_cubes_union(centers, radii, grid_spacing=GRID_SPACING_NM)
    except Exception:
        volume = 0.0
    if volume <= 0:
        volume = float(len(pocket_spheres)) * (0.1 ** 3)
    return volume


def _score_pocket(volume_nm3: float, n_spheres: int, avg_radius_nm: float) -> float:
    volume_a3 = volume_nm3 * 1000.0
    avg_radius_a = avg_radius_nm * 10.0
    score = float(volume_a3 / 500.0 + (n_spheres / 50.0))
    if MIN_RADIUS_A <= avg_radius_a <= MAX_RADIUS_A:
        score += SCORE_RADIUS_BONUS
    return score


def _sasa_molsysmt(receptor, coords_nm: np.ndarray, polar_probe_radius_nm: float) -> np.ndarray:
    if coords_nm.shape[0] == 0:
        return np.zeros(0, dtype=float)
    try:
        from biotite.structure import AtomArray
        from biotite.structure import sasa
    except ModuleNotFoundError as exc:
        warnings.warn(PocketeerSasaBackendWarning(reason=str(exc)))
        return np.zeros(coords_nm.shape[0], dtype=float)
    try:
        atom_names = np.asarray(
            msm.get(receptor, element='atom', atom_name=True), dtype=str
        )
        atom_types = np.asarray(
            msm.get(receptor, element='atom', atom_type=True), dtype=str
        )
        chain_ids = np.asarray(
            msm.get(receptor, element='atom', chain_id=True), dtype=str
        )
        res_names = np.asarray(
            msm.get(receptor, element='atom', residue_name=True), dtype=str
        )
        coords_ang = coords_nm * 10.0
        atomarray = AtomArray(coords_ang.shape[0])
        atomarray.coord = coords_ang
        atomarray.atom_name = atom_names
        atomarray.element = atom_types
        atomarray.chain_id = chain_ids
        atomarray.res_name = res_names
        polar_probe_radius_ang = polar_probe_radius_nm * 10.0
        sasa_array = sasa(atomarray, probe_radius=polar_probe_radius_ang)
    except Exception as exc:
        warnings.warn(PocketeerSasaBackendWarning(reason=str(exc)))
        return np.zeros(coords_nm.shape[0], dtype=float)
    sasa_values = np.asarray(sasa_array, dtype=float) / 100.0
    if sasa_values.ndim == 1:
        return sasa_values
    return sasa_values[0]


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
        radius = float(np.linalg.norm(rel))
        return center, radius
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
    centers = np.array([sphere.center for sphere in spheres])
    tree = cKDTree(centers)
    graph: dict[int, set[int]] = {i: set() for i in range(len(spheres))}
    for idx, center in enumerate(centers):
        neighbors = tree.query_ball_point(center, dist_th)
        for neighbor in neighbors:
            if idx == neighbor:
                continue
            graph[idx].add(neighbor)
            graph[neighbor].add(idx)
    return graph


def _connected_components(graph: dict[int, set[int]]) -> list[list[int]]:
    visited = set()
    components: list[list[int]] = []
    for node in graph:
        if node in visited:
            continue
        stack = [node]
        component: list[int] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(graph[current])
        components.append(component)
    return components
