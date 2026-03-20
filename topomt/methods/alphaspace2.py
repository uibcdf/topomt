"""AlphaSpace2-like pocket detection using Voronoi vertices and clustering.

This is a lightweight adaptation of the AlphaSpace2 tessellation workflow:
- Delaunay triangulation of receptor heavy atoms.
- Voronoi vertices = alpha-spheres centers; radii from nearest vertex–atom distance.
- Filter alpha-spheres by radius window [min_r, max_r].
- Cluster filtered vertices (average linkage on coordinates) with distance cutoff.
- Return pockets as lists of alpha-sphere indices belonging to each cluster.

Optional: compute simple descriptors (volume via grid approximation, nonpolar ratio via SASA).
"""

from __future__ import annotations

import warnings
from typing import Sequence

import molsysmt as msm
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial import Delaunay, Voronoi, cKDTree
from scipy.spatial.distance import cdist

from topomt._private.digestion import digest


@digest()
def alphaspace2(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    min_radius: float = 1.6,   # Å (AlphaSpace uses nm internally; here we stay in Å)
    max_radius: float = 6.0,
    cluster_method: str = 'average',  # SciPy linkage method
    cluster_cutoff: float = 1.8,      # distance in Å (AlphaSpace uses /10 on nm)
    hit_dist: float = 4.0,            # contact cutoff to binder/ligand (Å)
    binder_coords: np.ndarray | None = None,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    Detect pockets by clustering Voronoi vertices (alpha-spheres) as in AlphaSpace2.

    Parameters
    ----------
    molecular_system
        Input molecular system (MolSysMT-compatible).
    selection : str, optional
        Atom selection.
    structure_indices : int, optional
        Structure index to use.
    min_radius, max_radius : float
        Radius window to keep alpha-spheres.
    cluster_method : str
        Linkage method for SciPy `linkage`.
    cluster_cutoff : float
        Distance cutoff for `fcluster` (same units as coords).
    hit_dist : float
        Distance to count a vertex as ligand-contact (if binder_coords provided).
    binder_coords : np.ndarray, optional
        Coordinates of binder/ligand atoms (shape (m, 3)) in Å; if provided, compute contact flags.
    syntax : str
        Selection syntax for MolSysMT.

    Returns
    -------
    pockets : list[list[int]]
        Clusters of alpha-sphere indices.
    vertices : np.ndarray
        Alpha-sphere centers kept after filtering, shape (k, 3).
    radii : np.ndarray
        Alpha-sphere radii kept after filtering, shape (k,).
    vertex_contacts : np.ndarray
        Bool mask of vertex–binder contact (len == k), or None if no binder provided.
    """
    topo = msm.convert(molecular_system, to_form='molsysmt.MolSys', structure_indices=structure_indices)
    atom_indices = msm.select(
        molecular_system=topo,
        selection=selection,
        syntax=syntax,
    )
    # drop waters/ions/small and hydrogens
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
        warnings.warn('Not enough atoms to build Voronoi.')
        return [], np.zeros((0, 3)), np.zeros(0), None

    vor = Voronoi(coords)
    vertices = vor.vertices  # alpha centers

    # radii: min distance to atoms
    tree = cKDTree(coords)
    radii, _ = tree.query(vertices, k=1)

    # filter by radius window
    keep = (radii >= min_radius) & (radii <= max_radius)
    vertices = vertices[keep]
    radii = radii[keep]
    if len(vertices) == 0:
        return [], np.zeros((0, 3)), np.zeros(0), None

    # cluster vertices
    zmat = linkage(vertices, method=cluster_method)
    labels = fcluster(zmat, cluster_cutoff, criterion='distance') - 1  # zero-based
    pockets = []
    for lab in np.unique(labels):
        idx = np.where(labels == lab)[0].tolist()
        pockets.append(idx)

    # ligand contact flags
    vertex_contacts = None
    if binder_coords is not None and len(binder_coords) > 0:
        dist = cdist(vertices, binder_coords)
        vertex_contacts = (np.min(dist, axis=1) < hit_dist).astype(bool)

    return pockets, vertices, radii, vertex_contacts


# Additional characterization ideas (AlphaSpace-inspired)

def alphaball_volume(vertices: np.ndarray, radii: np.ndarray, grid_res: float = 0.5, threshold: float = 1.6) -> float:
    """Grid-based volume approximation around alpha-sphere centers."""
    if len(vertices) == 0:
        return 0.0
    max_coord = np.max(vertices, axis=0)
    min_coord = np.min(vertices, axis=0)
    coord_range = np.array([min_coord, max_coord]).T.tolist()
    x, y, z = [np.arange(start=ax[0] - threshold, stop=ax[1] + threshold, step=grid_res) for ax in coord_range]
    grid_coords = np.array(np.meshgrid(x, y, z)).transpose().reshape((-1, 3))
    tree = cKDTree(vertices)
    d, _ = tree.query(grid_coords, k=1)
    inside = d < threshold
    return float(np.count_nonzero(inside) * (grid_res ** 3))
