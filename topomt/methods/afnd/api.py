from typing import Union, List, Dict
import molsysmt as msm
import pyunitwizard as puw
from .graph import AlphaFlowNetwork
from ...features import Pocket, Void, Channel

def afnd(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    probe_radius: float = 1.4,
    sea_level: float = 10.0,
    min_size: int = 4,
    epsilon: float = 1e-6
) -> Dict[str, Dict[str, List]]:
    """
    Alpha-Flow Network Decomposition (AFND) method for pocket detection.

    Decomposes the molecular surface into pockets, voids, and solid structures based on 
    the flow of a spherical probe through the Delaunay triangulation network.

    Parameters
    ----------
    molecular_system : MolSysMT molecular system
        The molecular system to analyze.
    selection : str, optional
        Atom selection string (default 'all').
    structure_indices : int, optional
        Structure index to analyze (default 0).
    probe_radius : float, optional
        Radius of the solvent probe in Angstroms (default 1.4).
    sea_level : float, optional
        Radius threshold defining the bulk solvent 'Ocean' in Angstroms (default 10.0).
    min_size : int, optional
        Minimum number of tetrahedra for a component to be kept (default 4).
    epsilon : float, optional
        Numerical tolerance for geometric calculations (default 1e-6).

    Returns
    -------
    dict
        A structured dictionary with keys:
        - 'wet': {'pockets': List[Pocket], 'voids': List[Void], 'channels': List[Channel]}
        - 'dry': {'core': dict, 'islands': List[dict]}
    """
    
    # 1. Initialize the Network Engine
    network = AlphaFlowNetwork(
        molecular_system, 
        selection=selection, 
        structure_indices=structure_indices,
        epsilon=epsilon
    )
    
    # 2. Compute Topography
    raw_topo = network.get_topography(probe_radius=probe_radius, sea_level=sea_level, min_size=min_size)
    
    # 3. Convert to TopoMT Feature Objects
    
    # --- Wet Network ---
    pockets = []
    for p_data in raw_topo['wet']['pockets']:
        pocket_obj = Pocket() 
        pocket_obj.atom_indices = p_data['atom_indices']
        pocket_obj.tetrahedron_indices = p_data['tetrahedron_indices']
        # pocket_obj.volume = p_data.get('volume', None)
        pockets.append(pocket_obj)
        
    voids = []
    for v_data in raw_topo['wet']['voids']:
        void_obj = Void()
        void_obj.atom_indices = v_data['atom_indices']
        void_obj.tetrahedron_indices = v_data['tetrahedron_indices']
        voids.append(void_obj)
        
    channels = []
    if 'channels' in raw_topo['wet']:
        for c_data in raw_topo['wet']['channels']:
            channel_obj = Channel()
            channel_obj.atom_indices = c_data['atom_indices']
            channel_obj.tetrahedron_indices = c_data['tetrahedron_indices']
            channels.append(channel_obj)
        
    # --- Dry Network ---
    # Currently returning raw dicts for dry components as Feature classes for Core/Protrusion don't exist yet.
    core = raw_topo['dry']['core']
    islands = raw_topo['dry']['islands']
        
    return {
        'wet': {
            'pockets': pockets, 
            'voids': voids,
            'channels': channels
        },
        'dry': {
            'core': core,
            'islands': islands
        }
    }