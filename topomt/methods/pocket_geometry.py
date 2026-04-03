"""
Geometry and analysis utilities for pocket characterization.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence, Dict, List, Union, Tuple, Set

import numpy as np
import molsysmt as msm
from scipy.spatial.distance import cdist
from depdigest import dep_digest
from topomt.tools.geometry import (
    clip_mesh_with_plane,
    convex_hull_metrics,
    marching_cubes_union,
    union_volume_monte_carlo,
)
from topomt.tools.features.common import (
    bounding_metrics,
    effective_center_radius,
    jaccard_overlap_clusters,
)
from topomt.tools.features.channels import (
    cross_section_profile,
    min_cross_section_radius,
    shortest_path_length,
    thickness_profile,
)
from topomt.tools.features.mouths import mouth_area_on_plane
from topomt.tools.features.pockets import (
    apolar_ratio,
    get_physicochemical_properties,
    ligand_contact_distances,
    ligand_contact_mask,
    nonpolar_ratio_from_sasa,
    probe_scoring,
    sasa_contact_validation,
)


def _to_numpy(array: Iterable) -> np.ndarray:
    return np.asarray(array, dtype=float)


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


# ---------------------------------------------------------------------------
# AlphaSpace-inspired extras
# ---------------------------------------------------------------------------


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
