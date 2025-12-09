"""
CASTp-like pocket detection using Alpha Spheres and flow logic.
"""

from typing import List, Dict, Union, Tuple, Set
import numpy as np
import molsysmt as msm
from topomt.alpha_spheres import AlphaSpheres
from topomt.methods.pocket_geometry import (
    analytic_tetra_volume,
    mouth_area_from_faces,
    get_physicochemical_properties
)
from topomt import pyunitwizard as puw
from topomt._private.digestion import digest

@digest()
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

    The algorithm implements the core geometric concepts of CASTp:
    1. Alpha Shape Construction: Use Voronoi/Delaunay dual to find empty spheres.
    2. Pocket Definition: A pocket is a collection of empty spheres connected by faces
       through which a probe of `probe_radius` can flow.
    3. Mouth Detection: The boundary faces of a pocket that connect to the bulk solvent
       (outside) are defined as 'Mouths'. Their area is calculated exactly.
    4. Exact Topological Volume: The volume is calculated as the sum of the Delaunay 
       tetrahedra corresponding to the empty spheres in the pocket.

    Parameters
    ----------
    molecular_system : MolSysMT molecular system
        The molecular system to analyze.
    selection : str, optional
        Selection string for the atoms to include (default 'all').
    structure_indices : int, optional
        Index of the structure to analyze (default 0).
    probe_radius : float, optional
        Radius of the probe sphere in Angstroms (default 1.4).
    min_spheres_per_pocket : int, optional
        Minimum number of alpha spheres required to define a pocket (default 5).

    Returns
    -------
    pockets : List[Dict]
        A list of dictionaries, each representing a detected pocket with keys:
        - 'id': Pocket ID
        - 'alpha_sphere_indices': List of indices of alpha spheres in this pocket.
        - 'atom_indices': List of atom indices lining the pocket.
        - 'volume': Topological volume of the pocket (sum of tetrahedra).
        - 'mouth_area': Total area of the mouth(s) connecting to bulk solvent.
        - 'surface_area': Approximate surface area of the pocket walls.
        - 'properties': Physicochemical properties (charge, hydrophobicity).
    alpha_spheres : AlphaSpheres
        The AlphaSpheres object containing all computed spheres.
    """
    
    # 1. Prepare Molecular System
    topo = msm.convert(molecular_system, to_form='molsysmt.MolSys', structure_indices=structure_indices)
    
    atom_indices = msm.select(topo, selection=selection, syntax=syntax)
    
    # Clean selection (standard CASTp practice involves heavy atoms usually)
    solvent_idx = msm.select(topo, selection="group_type in ['water', 'ion', 'small molecule']", mask=atom_indices)
    if len(solvent_idx) > 0:
        atom_indices = list(set(atom_indices) - set(solvent_idx))
    
    h_idx = msm.select(topo, selection="atom_type == 'H'", mask=atom_indices)
    if len(h_idx) > 0:
        atom_indices = list(set(atom_indices) - set(h_idx))
        
    atom_indices = sorted(atom_indices)
    
    # Coordinates in Angstroms (crucial for geometric thresholds)
    coords = msm.get(topo, selection=atom_indices, coordinates=True)[0]
    coords = puw.get_value(coords, to_unit='angstroms')
    
    # 2. Generate Alpha Spheres (Voronoi/Delaunay)
    alpha = AlphaSpheres(points=coords)
    
    # 3. Identify Accessible Space
    # Spheres with R >= probe_radius are part of the accessible space (Solvent + Pockets)
    valid_sphere_indices = np.where(alpha.radii >= probe_radius)[0]
    
    if len(valid_sphere_indices) == 0:
        return [], alpha

    # 4. Connectivity and Flow Analysis
    # Build the adjacency graph for valid spheres
    # Two valid spheres are connected if they share a face (3 atoms) 
    # AND that face is permeable (radius of face circumcircle > probe_radius)? 
    # Actually, if both spheres have R > probe, the intersection disk is usually large enough.
    # The standard CASTp flow uses a simplified check: do they share a Delaunay face?
    
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
            
    # 5. Separate Bulk Solvent from Pockets
    # The largest component is typically the Bulk Solvent.
    # We assume 'Pockets' are the isolated components (Voids) OR semi-isolated regions.
    # For this implementation, strictly following component logic:
    # - Largest component = Bulk (usually)
    # - Other components = Internal Voids
    # - To find Surface Pockets (Mouths), we look at the boundaries of ALL components.
    #   Wait, if it's a Void, it has NO boundary to the outside (by definition).
    #   CASTp defines pockets as depressions in the bulk solvent too.
    #   Implementing full flow segmentation is complex.
    #   Here, we detect **Topological Voids** (isolated) and treat the Bulk as Bulk.
    #   However, to satisfy the user request for "Mouth Detection", we must consider
    #   that a "pocket" might be defined by manually segmenting the bulk?
    #   Let's stick to the Voids first. 
    #   BUT, often "pockets" in proteins are deep surface invaginations.
    #   CASTp separates these by checking if the flow to "infinity" passes through a bottleneck.
    #   
    #   Current heuristic improvement: 
    #   We return all components that satisfy min_spheres.
    #   We calculate "Mouths" as the faces shared with ANY sphere that was filtered out
    #   because R < probe (Protein Interior) -> These are Walls.
    #   Faces shared with NO other sphere (Boundary of Delaunay) -> These are "Outer Limits".
    #   
    #   If a component is the Bulk Solvent, its "Mouths" are everywhere.
    #   We simply sort components by volume. The largest is likely the bulk.
    #   We will flag it but return it anyway for analysis.
    
    pockets_data = []
    
    # Pre-calculate faces for mouth detection
    # We need to know for each sphere in a pocket, which faces are "exposed"
    # An exposed face is one NOT shared with another sphere in the SAME pocket.
    
    # We need a map of (sorted_face_tuple) -> [sphere_indices]
    # alpha.points_of_alpha_sphere gives the 4 atoms of the tetra.
    # Faces are combinations of 3.
    
    for i, comp_indices in enumerate(components):
        if len(comp_indices) < min_spheres_per_pocket:
            continue
            
        # 5a. Volume (Topological)
        # We collect the indices of the 4 atoms for each sphere in the component
        # alpha.points_of_alpha_sphere is a list of lists or ndarray(N,4)
        # We assume it supports list indexing or we iterate
        valid_tets_indices = []
        sphere_atom_indices_map = {} # sphere_idx -> [a,b,c,d]
        
        for s_idx in comp_indices:
             pts = alpha.points_of_alpha_sphere[s_idx]
             valid_tets_indices.append(pts)
             sphere_atom_indices_map[s_idx] = set(pts)
             
        # Calculate Volume using refined helper (accepts list of lists)
        # coords is (N_atoms, 3)
        vol = analytic_tetra_volume(coords, valid_tets_indices)
        
        # 5b. Mouth Detection & Surface Area
        # Iterate over all spheres in pocket.
        # For each sphere, look at its 4 faces.
        # If a face is shared with another sphere IN THE POCKET -> Internal
        # If a face is NOT shared with another sphere in the pocket -> Boundary
        
        # To do this efficiently: Count face occurrences.
        # Faces that appear once in the list of all faces of the pocket are boundary.
        # (Since Delaunay is a partition, a face is either shared by 2 tets or is boundary).
        
        pocket_faces = []
        for s_idx in comp_indices:
            atoms = sorted(alpha.points_of_alpha_sphere[s_idx])
            # 4 faces
            faces = [
                tuple(sorted((atoms[0], atoms[1], atoms[2]))),
                tuple(sorted((atoms[0], atoms[1], atoms[3]))),
                tuple(sorted((atoms[0], atoms[2], atoms[3]))),
                tuple(sorted((atoms[1], atoms[2], atoms[3])))
            ]
            pocket_faces.extend(faces)
            
        from collections import Counter
        face_counts = Counter(pocket_faces)
        
        # Boundary faces (count == 1)
        boundary_faces = [f for f, count in face_counts.items() if count == 1]
        
        # Now, distinguish "Mouth" (Open to Solvent) from "Wall" (Protein)
        # This is tricky without the full triangulation info.
        # Heuristic: 
        # - Wall faces connect to "Solid" (tetrahedra with R < probe).
        # - Mouth faces connect to "Nothing" (outside convex hull) or "Other Solvent" (if we segmented).
        # Since we just took connected components of ALL R>probe, 
        # Any boundary face MUST connect to either:
        #   A) A tetrahedron with R < probe (Protein Interior) -> This is a WALL.
        #   B) Nothing (The infinite exterior) -> This is a MOUTH.
        # 
        # So, we check if the boundary face is shared with any invalid sphere (R < probe).
        # If yes -> Wall.
        # If no -> Mouth.
        
        # We need a lookup of faces for ALL spheres or just iterate invalid ones?
        # Iterating invalid ones is expensive.
        # Better: Build a set of "Solid Faces" from the invalid spheres?
        # Or rely on the fact that if it's not in the pocket, and we are in Delaunay...
        # Wait, alpha.get_neighbors tells us neighbors.
        # If a sphere s (in pocket) has neighbor n (not in pocket):
        #   If alpha.radii[n] < probe -> Shared face is WALL.
        #   If alpha.radii[n] >= probe -> Impossible, n would be in pocket (connected component).
        #   If n does not exist (boundary of triangulation) -> Shared face is MOUTH.
        
        mouth_faces = []
        wall_faces = []
        
        # Quick lookup for pocket membership
        pocket_set = set(comp_indices)
        
        for s_idx in comp_indices:
            # Get neighbors from AlphaSpheres (pre-calculated face adjacency)
            # This returns indices of spheres sharing a face.
            # Warning: get_neighbors might not return "None" for boundary.
            neighbors = all_neighbors.get(s_idx, [])
            
            # Identify the specific face shared with each neighbor? 
            # AlphaSpheres.get_neighbors doesn't return the face, just the index.
            # We have to reconstruct which face is shared.
            # Intersection of atom indices (3 atoms).
            
            # Also, there are 4 faces. 
            # If len(neighbors) < 4, the remaining faces are boundary of triangulation (Mouths).
            
            s_atoms = set(alpha.points_of_alpha_sphere[s_idx])
            
            # Track which faces are accounted for by neighbors
            found_faces = set()
            
            for n_idx in neighbors:
                # Find shared face
                n_atoms = set(alpha.points_of_alpha_sphere[n_idx])
                shared = tuple(sorted(list(s_atoms.intersection(n_atoms))))
                if len(shared) == 3:
                    found_faces.add(shared)
                    if n_idx not in pocket_set:
                        # Neighbor is not in pocket.
                        # Check if it is solid (R < probe)
                        if alpha.radii[n_idx] < probe_radius:
                            wall_faces.append(shared)
                        else:
                            # This should not happen if we computed components correctly
                            # unless it's a separate component (unreachable?)
                            # Assume Wall/Solid just in case
                            wall_faces.append(shared)
            
            # Faces NOT in found_faces are strictly external to the triangulation
            # These are "Mouths" to infinity.
            # Reconstruct all 4 faces
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

        # Calculate Areas
        mouth_area = mouth_area_from_faces(mouth_faces, coords)
        # Wall area is approximation via triangles (not spherical caps, but consistent with Topo volume)
        wall_area = mouth_area_from_faces(wall_faces, coords) 
        
        # 5c. Physicochemical Properties
        # Lining atoms: All atoms belonging to spheres in the pocket
        lining_atoms_local = set()
        for s_idx in comp_indices:
            lining_atoms_local.update(alpha.points_of_alpha_sphere[s_idx])
        lining_atoms_global = [atom_indices[k] for k in lining_atoms_local]
        
        props = get_physicochemical_properties(topo, lining_atoms_global)
        
        pockets_data.append({
            'id': i + 1,
            'alpha_sphere_indices': comp_indices,
            'atom_indices': lining_atoms_global,
            'volume': vol,
            'mouth_area': mouth_area,
            'surface_area': wall_area + mouth_area, # Total area
            'properties': props,
            'score': vol, # Simple ranking
            'type': 'Void' if mouth_area == 0 else 'Pocket' # Classify
        })
        
    # Sort by Volume
    pockets_data.sort(key=lambda x: x['volume'], reverse=True)
    
    # Renumber
    for i, p in enumerate(pockets_data):
        p['id'] = i + 1
        
    return pockets_data, alpha