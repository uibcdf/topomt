"""AlphaSpace2-like pocket detection using Voronoi vertices and clustering.
"""

from __future__ import annotations

import warnings
from typing import Iterable, Sequence

import molsysmt as msm
import numpy as np
from scipy.spatial import Voronoi
from scipy.cluster.hierarchy import linkage, fcluster
from topomt._private.puw_utils import get_magnitude, get_magnitudes


def alphaspace2(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    min_radius: float = 0.35, # Default in NM (3.5 A)
    max_radius: float = 0.55, # Default in NM (5.5 A)
    cluster_cutoff: float = 0.4, # Default in NM (4.0 A)
    cluster_method: str = 'average',
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
):
    """
    Detect pockets using AlphaSpace2 workflow. Internal logic in NM.
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
    
    # Safe normalization to NM
    coords_nm = get_magnitudes(coords, unit='nm')
    min_r_nm = get_magnitude(min_radius, unit='nm')
    max_r_nm = get_magnitude(max_radius, unit='nm')
    cut_nm = get_magnitude(cluster_cutoff, unit='nm')

    if coords_nm.shape[0] < 4:
        return [], np.zeros((0, 3)), np.zeros(0), None

    vor = Voronoi(coords_nm)
    vertices = vor.vertices
    
    # Compute radii: distance to nearest atom
    from scipy.spatial import cKDTree
    tree = cKDTree(coords_nm)
    radii, _ = tree.query(vertices, k=1)
    
    # Filter alpha-spheres
    mask = (radii >= min_r_nm) & (radii <= max_r_nm)
    filtered_vertices = vertices[mask]
    filtered_radii = radii[mask]
    
    if len(filtered_vertices) < 2:
        return [], vertices, radii, None
        
    # Clustering
    from scipy.spatial.distance import pdist
    D = pdist(filtered_vertices)
    Z = linkage(D, method=cluster_method)
    labels = fcluster(Z, t=cut_nm, criterion='distance')
    
    clusters = []
    real_indices = np.where(mask)[0]
    for lab in np.unique(labels):
        comp = real_indices[np.where(labels == lab)[0]].tolist()
        clusters.append(comp)
        
    return clusters, vertices, radii, None
