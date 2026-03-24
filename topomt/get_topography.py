from __future__ import annotations
from typing import Any
import numpy as np
import molsysmt as msm
from .topography.Topography import Topography
from argdigest import arg_digest
from smonitor import signal
from scipy.spatial import cKDTree

@signal(tags=["api", "topography"])
@arg_digest()
def get_topography(molecular_system: Any, method: str = 'pocketeer', selection: str = 'all',
                   structure_indices: int | list[int] = 0, syntax: str = 'MolSysMT', 
                   skip_digestion: bool = False, **kwargs) -> Topography:
    """
    Generate a Topography object from a molecular system using a specified method.
    """

    method_lower = method.lower()
    
    if method_lower == 'pocketeer':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        topo = _run_pocketeer(topo, **kwargs)

    elif method_lower in ['fpocket', 'fpocket4']:
        from .methods.fpocket4 import fpocket4
        topo = fpocket4(molecular_system, selection=selection, structure_indices=structure_indices, **kwargs)

    elif method_lower == 'alphaspace2':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        topo = _run_alphaspace2(topo, **kwargs)

    elif method_lower == 'castp':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        topo = _run_castp(topo, **kwargs)

    elif method_lower == 'pycasta':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        topo = _run_pycasta(topo, **kwargs)

    elif method_lower == 'afnd':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        from .methods.afnd.api import afnd
        topo = afnd(topo, **kwargs)

    else:
        raise ValueError(f"Unknown method {method!r}. Supported: 'pocketeer', 'fpocket', 'alphaspace2', 'castp', 'pycasta'.")

    return topo

def _run_pocketeer(topo: Topography, **kwargs) -> Topography:
    from .methods.pocketeer import pocketeer
    from .features.Pocket import Pocket
    
    pockets_data, spheres = pocketeer(topo.molecular_system, selection=topo.selection, 
                                      structure_indices=topo.structure_indices, **kwargs)
    
    for p in pockets_data:
        all_atom_indices = set()
        for s in p.spheres:
            all_atom_indices.update(s.atom_indices)
        
        pocket_feature = Pocket(
            atom_indices=sorted(list(all_atom_indices)),
            center=p.centroid,
            volume=p.volume,
            score=p.score
        )
        topo.add_feature(pocket_feature)
        
    return topo

def _run_alphaspace2(topo: Topography, min_vertices: int = 20, **kwargs) -> Topography:
    from .methods.alphaspace2 import alphaspace2
    from .features.Pocket import Pocket
    from ._pyunitwizard import pyunitwizard as puw
    
    clusters, vertices, radii, contacts = alphaspace2(topo.molecular_system, selection=topo.selection,
                                                      structure_indices=topo.structure_indices, **kwargs)
    
    atom_indices = msm.select(topo.molecular_system, selection=topo.selection)
    atom_coords = msm.get(topo.molecular_system, selection=atom_indices, coordinates=True)[0]
    atom_coords = puw.get_value(atom_coords, to_unit='nm')
    tree = cKDTree(atom_coords)

    for i, cluster in enumerate(clusters):
        if len(cluster) < min_vertices:
            continue
            
        cluster_vertices = vertices[cluster]
        cluster_radii = radii[cluster]
        centroid = np.mean(cluster_vertices, axis=0) if len(cluster_vertices) > 0 else None
        
        involved_atoms = set()
        for v, r in zip(cluster_vertices, cluster_radii):
            near_atoms = tree.query_ball_point(v, r + 0.02) # tolerance in nm (0.2 A)
            involved_atoms.update([atom_indices[idx] for idx in near_atoms])

        if not involved_atoms:
            continue

        pocket_feature = Pocket(
            atom_indices=sorted(list(involved_atoms)),
            center=centroid,
        )
        try:
            from .methods.pocket_geometry import marching_cubes_union
            _, _, vol, _ = marching_cubes_union(cluster_vertices, cluster_radii, grid_spacing=0.05)
            pocket_feature.volume = vol
        except Exception:
            pass

        topo.add_feature(pocket_feature)
        
    return topo

def _run_castp(topo: Topography, **kwargs) -> Topography:
    from .methods.castp import castp
    from .features.Pocket import Pocket
    
    # CASTp can be very memory intensive if probe is small
    pockets_data, alpha = castp(topo.molecular_system, selection=topo.selection,
                                 structure_indices=topo.structure_indices, **kwargs)
    
    # Skip the bulk solvent (usually the one with thousands of atoms)
    # But keep it if it's the only one? No, usually users want real pockets.
    for p in pockets_data:
        atom_indices = p['atom_indices']
        if len(atom_indices) > 1000: # Heuristic for bulk solvent in typical protein
            continue

        pocket_feature = Pocket(
            atom_indices=sorted(atom_indices),
            center=p.get('center'),
            volume=p.get('volume', 0.0),
            score=p.get('score', 0.0)
        )
        if 'mouth_area' in p:
            pocket_feature.mouth_area = p['mouth_area']
            
        topo.add_feature(pocket_feature)
        
    return topo

def _run_pycasta(topo: Topography, **kwargs) -> Topography:
    from .methods.pycasta import pycasta
    from .features.Pocket import Pocket
    
    # Use larger alpha for pycasta to find empty space in nm
    if 'alpha' not in kwargs:
        kwargs['alpha'] = 0.4 # 4.0 A
        
    pockets_tet, volumes, simplices = pycasta(topo.molecular_system, selection=topo.selection,
                                              structure_indices=topo.structure_indices, **kwargs)
    
    atom_indices = msm.select(topo.molecular_system, selection=topo.selection)
    
    for p_tet, vol in zip(pockets_tet, volumes):
        involved_local_indices = set()
        for tet_idx in p_tet:
            involved_local_indices.update(simplices[tet_idx])
            
        involved_global_indices = [atom_indices[i] for i in involved_local_indices]
        
        # Calculate center manually since pycasta doesn't return it
        atom_coords = msm.get(topo.molecular_system, selection=involved_global_indices, coordinates=True)[0]
        from ._pyunitwizard import pyunitwizard as puw
        center = np.mean(puw.get_value(atom_coords, to_unit='nm'), axis=0)
        
        pocket_feature = Pocket(
            atom_indices=sorted(involved_global_indices),
            center=center,
            volume=vol,
            score=vol
        )
        topo.add_feature(pocket_feature)
        
    return topo
