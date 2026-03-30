"""
CASTp-like pocket detection using Alpha Spheres and flow logic.
"""

from typing import List, Dict, Union, Tuple, Set
import numpy as np
from topomt.alpha_spheres import AlphaSpheres
from topomt._private.molsysmt_preparation import build_heavy_receptor_view
from topomt._private.smonitor import signal
from topomt.methods.pocket_geometry import (
    analytic_tetra_volume,
    mouth_area_from_faces,
    get_physicochemical_properties
)
from topomt import pyunitwizard as puw


@signal(tags=['method', 'castp', 'native'])
def castp(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    probe_radius: float = 1.4,
    min_spheres_per_pocket: int = 5,
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
) -> Tuple[List[Dict], AlphaSpheres]:
    """
    Detect pockets using a CASTp-inspired algorithm based on Alpha Spheres and Flow.
    """
    
    # 1. Infrastructure and Normalization (Forced to NM for internal logic)
    def _to_nm(val):
        if puw.is_quantity(val):
            try: return float(puw.get_value(val, to_unit='nm'))
            except Exception: return float(puw.get_value(val))
        try: return float(puw.get_value(puw.quantity(val), to_unit='nm'))
        except Exception: return float(val) / 10.0 # Assume Angstroms if float

    probe_r_nm = _to_nm(probe_radius)

    # 2. Prepare Molecular System
    molsys, _, atom_indices, coords_nm = build_heavy_receptor_view(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )
    
    # 3. Generate Alpha Spheres (Voronoi/Delaunay) - Results in NM
    alpha = AlphaSpheres(points=coords_nm)
    
    # 4. Identify Accessible Space
    valid_sphere_indices = np.where(alpha.radii >= probe_r_nm)[0]
    
    if len(valid_sphere_indices) == 0:
        return [], alpha

    # 5. Connectivity and Flow Analysis
    all_neighbors = alpha.get_neighbors(criterion='face')
    valid_set = set(valid_sphere_indices)
    adj_list = {}
    
    for idx in valid_sphere_indices:
        neighbors = all_neighbors.get(idx, [])
        valid_neighbors = [n for n in neighbors if n in valid_set]
        adj_list[idx] = valid_neighbors
        
    # Find Connected Components
    visited = set()
    components = []
    
    for idx in valid_sphere_indices:
        if idx not in visited:
            component = []
            stack = [idx]
            visited.add(idx)
            while stack:
                curr = stack.pop()
                component.append(curr)
                for n in adj_list.get(curr, []):
                    if n not in visited:
                        visited.add(n)
                        stack.append(n)
            components.append(component)
            
    pockets_data = []
    
    for i, comp_indices in enumerate(components):
        if len(comp_indices) < min_spheres_per_pocket:
            continue
            
        # 5a. Volume (Topological)
        valid_tets_indices = [alpha.points_of_alpha_sphere[s_idx] for s_idx in comp_indices]
        vol = analytic_tetra_volume(coords_nm, valid_tets_indices)
        
        # 5b. Mouth Detection
        mouth_faces = []
        wall_faces = []
        pocket_set = set(comp_indices)
        
        for s_idx in comp_indices:
            neighbors = all_neighbors.get(s_idx, [])
            s_atoms = set(alpha.points_of_alpha_sphere[s_idx])
            found_faces = set()
            
            for n_idx in neighbors:
                n_atoms = set(alpha.points_of_alpha_sphere[n_idx])
                shared = tuple(sorted(list(s_atoms.intersection(n_atoms))))
                if len(shared) == 3:
                    found_faces.add(shared)
                    if n_idx not in pocket_set:
                        # Neighbor is protein or other pocket
                        wall_faces.append(shared)
            
            # Boundary faces of triangulation are Mouths
            atoms_list = sorted(list(s_atoms))
            all_4_faces = [
                tuple(sorted((atoms_list[0], atoms_list[1], atoms_list[2]))),
                tuple(sorted((atoms_list[0], atoms_list[1], atoms_list[3]))),
                tuple(sorted((atoms_list[0], atoms_list[2], atoms_list[3]))),
                tuple(sorted((atoms_list[1], atoms_list[2], atoms_list[3])))
            ]
            for f in all_4_faces:
                if f not in found_faces:
                    mouth_faces.append(f)

        # Calculate Areas (NM^2)
        mouth_area = mouth_area_from_faces(mouth_faces, coords_nm)
        wall_area = mouth_area_from_faces(wall_faces, coords_nm) 
        
        lining_atoms_local = set()
        for s_idx in comp_indices:
            lining_atoms_local.update(alpha.points_of_alpha_sphere[s_idx])
        lining_atoms_global = [atom_indices[k] for k in lining_atoms_local]
        
        # Props calculation
        try:
            props = get_physicochemical_properties(molsys, lining_atoms_global)
        except Exception:
            props = {}
        
        pockets_data.append({
            'id': i + 1,
            'alpha_sphere_indices': comp_indices,
            'atom_indices': lining_atoms_global,
            'volume': vol,
            'mouth_area': mouth_area,
            'surface_area': wall_area + mouth_area,
            'properties': props,
            'score': vol,
            'type': 'Void' if mouth_area == 0 else 'Pocket'
        })
        
    pockets_data.sort(key=lambda x: x['volume'], reverse=True)
    for i, p in enumerate(pockets_data):
        p['id'] = i + 1
        
    return pockets_data, alpha
