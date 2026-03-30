import numpy as np
import molsysmt as msm
from scipy.spatial import Delaunay
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import math
from topomt import pyunitwizard as puw

# Import functions from the newly created core module
from .core.apollonius import solve_apollonius_3d
from .core.permeability import check_face_permeability

# Import Feature classes
from ...features import Pocket, Void, Mouth

class AlphaFlowNetwork:
    """
    The main container for the AFND analysis.
    Built once per structure; queried multiple times for different probes.
    """
    
    def __init__(self, molecular_system, selection='all', structure_indices=0, epsilon=1e-6):
        """
        Initializes the AlphaFlowNetwork by building the Delaunay mesh and pre-calculating
        all necessary geometric properties for tetrahedra and faces.
        """
        self.molecular_system = molecular_system
        self.selection = selection
        self.structure_indices = structure_indices
        self.epsilon = epsilon

        # 1. Extract coordinates and radii
        topo = msm.convert(molecular_system, to_form='molsysmt.MolSys', structure_indices=structure_indices)
        atom_indices_selection = msm.select(topo, selection=selection)
        atom_indices_heavy = msm.select(topo, selection='atom_type != "H"', mask=atom_indices_selection)
        
        self.atom_coords = puw.get_value(
            msm.get(topo, selection=atom_indices_heavy, coordinates=True), to_unit='angstroms'
        )[0]
        self.atom_radii = puw.get_value(
            msm.get(topo, selection=atom_indices_heavy, atom_radius=True), to_unit='angstroms'
        )
        self.atom_indices_map = atom_indices_heavy # Map local index to global atom index

        if self.atom_coords.shape[0] < 4:
            raise ValueError("Not enough atoms to build Delaunay triangulation (min 4).")

        # 2. Build Delaunay triangulation
        self.delaunay = Delaunay(self.atom_coords)
        self.tetra_atoms = self.delaunay.simplices # N_tet x 4 atom indices
        self.n_tetrahedra = self.tetra_atoms.shape[0]

        # 3. Pre-calculate tetrahedron metrics (R_insphere)
        self.tetra_habitability = np.zeros(self.n_tetrahedra, dtype=np.float32)
        for i, tet_atom_indices in enumerate(self.tetra_atoms):
            p1, p2, p3, p4 = self.atom_coords[tet_atom_indices]
            r1, r2, r3, r4 = self.atom_radii[tet_atom_indices]
            
            r_insphere, _ = solve_apollonius_3d(p1, r1, p2, r2, p3, r3, p4, r4, self.epsilon)
            self.tetra_habitability[i] = r_insphere
            
        # 4. Pre-calculate face metrics (R_gate for each face)
        self.face_r_gates_per_tet_face = np.zeros((self.n_tetrahedra, 4), dtype=np.float32)

        unique_face_r_gates = {}
        self.adjacency_list = [[] for _ in range(self.n_tetrahedra)]
        sources = []
        targets = []
        edge_weights = []

        for i, tet_atom_indices in enumerate(self.tetra_atoms):
            faces_local_atom_indices = [
                (tet_atom_indices[0], tet_atom_indices[1], tet_atom_indices[2]),
                (tet_atom_indices[0], tet_atom_indices[1], tet_atom_indices[3]),
                (tet_atom_indices[0], tet_atom_indices[2], tet_atom_indices[3]),
                (tet_atom_indices[1], tet_atom_indices[2], tet_atom_indices[3]),
            ]
            
            for face_idx_in_tet, current_face_atom_indices in enumerate(faces_local_atom_indices):
                unique_face_key = tuple(sorted(current_face_atom_indices))
                
                p1, p2, p3 = self.atom_coords[[current_face_atom_indices[0], current_face_atom_indices[1], current_face_atom_indices[2]]]
                r1, r2, r3 = self.atom_radii[[current_face_atom_indices[0], current_face_atom_indices[1], current_face_atom_indices[2]]]
                
                r_gate = check_face_permeability(p1, p2, p3, r1, r2, r3, self.epsilon) 
                r_gate = r_gate[1] # Extract float value
                
                self.face_r_gates_per_tet_face[i, face_idx_in_tet] = r_gate
                
                if unique_face_key not in unique_face_r_gates:
                    unique_face_r_gates[unique_face_key] = r_gate
                else:
                    unique_face_r_gates[unique_face_key] = min(unique_face_r_gates[unique_face_key], r_gate)
                    
                neighbor_tet_idx = self.delaunay.neighbors[i, face_idx_in_tet]
                if neighbor_tet_idx != -1: # Internal face
                    self.adjacency_list[i].append((neighbor_tet_idx, r_gate))
                    
                    if i < neighbor_tet_idx:
                        sources.append(i)
                        targets.append(neighbor_tet_idx)
                        edge_weights.append(r_gate)
        
        self.sources = np.array(sources, dtype=np.int32)
        self.targets = np.array(targets, dtype=np.int32)
        self.edge_weights = np.array(edge_weights, dtype=np.float32)

        self.unique_face_r_gates_map = unique_face_r_gates
        # Boundary faces are those where neighbor is -1
        # We can identify them quickly later if needed.


    def get_topography(self, probe_radius=1.4, sea_level=10.0, min_size=4):
        """
        Queries the pre-built AlphaFlowNetwork for a specific probe radius
        and generates a rich topological decomposition.
        
        Parameters
        ----------
        probe_radius : float
            Radius of the solvent probe (Angstroms).
        sea_level : float
            Radius defining the bulk solvent 'Ocean' in Angstroms. 
            Tetrahedra with R_insphere > sea_level are considered OCEAN.
        min_size : int
            Minimum number of tetrahedra for a component to be kept (Pruning).
            
        Returns
        -------
        dict
            Dictionary containing 'wet' (pockets, voids) and 'dry' (core, islands) components.
            Each component is a dict with 'tetrahedron_indices' and 'atom_indices'.
        """
        # 1. Classify Nodes
        mask_ocean = self.tetra_habitability >= sea_level
        # STRICT definition: TRANSIT means the probe fits INSIDE.
        mask_transit = (self.tetra_habitability >= probe_radius) & (~mask_ocean)
        # COAST candidates: R_in < probe, but might be attached to a pocket.
        # Initially, anything not ocean and not transit is a candidate for solid or coast.
        # We will distinguish Coast from Solid by connectivity later.
        
        # --- WET NETWORK ANALYSIS (Core Connectivity) ---
        
        # We build the graph using ONLY TRANSIT nodes as the backbone.
        # Flow can only go THROUGH Transit nodes.
        
        mask_edges_permeable = self.edge_weights >= probe_radius
        
        # Filter edges where both source and target are TRANSIT
        mask_edges_transit = mask_transit[self.sources] & mask_transit[self.targets]
            mask_valid_edges_wet = mask_edges_permeable & mask_edges_transit
            
            valid_sources_wet = self.sources[mask_valid_edges_wet]
            valid_targets_wet = self.targets[mask_valid_edges_wet]
            valid_weights_wet = np.ones(len(valid_sources_wet), dtype=np.int8)
            
            adj_matrix_wet = coo_matrix((valid_weights_wet, (valid_sources_wet, valid_targets_wet)), 
                                        shape=(self.n_tetrahedra, self.n_tetrahedra))
            
            n_comps_wet, labels_wet = connected_components(adj_matrix_wet, directed=False)
            
            # Identify Mouths (Connections to Ocean from TRANSIT backbone)
            connected_to_ocean = np.zeros(n_comps_wet, dtype=bool)
            
            mask_edges_to_ocean = mask_edges_permeable & (
                (mask_transit[self.sources] & mask_ocean[self.targets]) |
                (mask_transit[self.targets] & mask_ocean[self.sources])
            )
            
            mouth_sources = self.sources[mask_edges_to_ocean]
            mouth_targets = self.targets[mask_edges_to_ocean]
            transit_nodes_at_mouth = np.where(mask_transit[mouth_sources], mouth_sources, mouth_targets)
            connected_to_ocean[labels_wet[transit_nodes_at_mouth]] = True
            
            # Check boundary faces for mouths
            for i in np.where(mask_transit)[0]:
                neighbors = self.delaunay.neighbors[i]
                for face_idx, neighbor in enumerate(neighbors):
                    if neighbor == -1: 
                        if self.face_r_gates_per_tet_face[i, face_idx] >= probe_radius:
                            connected_to_ocean[labels_wet[i]] = True
                            break
            
            # --- EXPANSION: Identify COAST Nodes ---
            # A node is COAST if:
            # 1. It is NOT Transit and NOT Ocean (i.e., it is structurally "Solid-like" or "Sliver")
            # 2. It shares a permeable face with a TRANSIT node.
            # We attach these Coast nodes to the component of their Transit neighbor.
            
            mask_candidate_coast = (~mask_transit) & (~mask_ocean)
            
            # Find edges between TRANSIT and CANDIDATE_COAST
            mask_edges_to_coast = mask_edges_permeable & (
                (mask_transit[self.sources] & mask_candidate_coast[self.targets]) |
                (mask_transit[self.targets] & mask_candidate_coast[self.sources])
            )
            
            coast_sources = self.sources[mask_edges_to_coast]
            coast_targets = self.targets[mask_edges_to_coast]
            
                # Map: Coast Node Index -> Component Label
                # Note: A coast node might touch multiple components. We assign it to one (first found) or duplicate?
                # Standard: Assign to one.
                coast_node_to_label = {}
                
                for s, t in zip(coast_sources, coast_targets):
                    transit_idx = s if mask_transit[s] else t
                    coast_idx = t if mask_transit[s] else s
                    
                    comp_label = labels_wet[transit_idx]
                    coast_node_to_label[coast_idx] = comp_label
        
                # --- Aggregation and Pruning ---
        # Group WET results
        pockets = []
        voids = []
        channels = []
        
        nodes_by_component_wet = {}
        for idx in np.where(mask_transit)[0]:
            lab = labels_wet[idx]
            if lab not in nodes_by_component_wet:
                nodes_by_component_wet[lab] = []
            nodes_by_component_wet[lab].append(idx)
            
        for lab, nodes in nodes_by_component_wet.items():
            # PRUNING
            if len(nodes) < min_size:
                continue

            atom_indices_local = set()
            for tet_idx in nodes:
                atom_indices_local.update(self.tetra_atoms[tet_idx])
            atom_indices_global = [self.atom_indices_map[k] for k in atom_indices_local]
            
            # Identify which nodes are COAST for metadata
            transit_subset = [n for n in nodes if mask_transit[n]]
            coast_subset = [n for n in nodes if not mask_transit[n]]
            
            feature_data = {
                'id': int(lab),
                'tetrahedron_indices': nodes,
                'transit_indices': transit_subset,
                'coast_indices': coast_subset,
                'atom_indices': sorted(list(atom_indices_global)),
                'volume': 0.0 # Placeholder
            }
            
            # --- CHANNEL DETECTION (Mouth Clustering) ---
            if connected_to_ocean[lab]:
                # 1. Collect all Mouth Faces for this component
                # A mouth face is a face of a node in 'nodes' that connects to OCEAN/Infinite
                # AND is permeable.
                
                mouth_faces = [] # List of tuples (atom_idx1, atom_idx2, atom_idx3) - sorted
                
                # Check internal edges to OCEAN from this component
                # Optimization: iterate over nodes in component
                for tet_idx in nodes:
                    # Check internal neighbors
                    neighbors = self.delaunay.neighbors[tet_idx]
                    for face_idx, neighbor in enumerate(neighbors):
                        is_mouth = False
                        if neighbor == -1: # Boundary
                            if self.face_r_gates_per_tet_face[tet_idx, face_idx] >= probe_radius:
                                is_mouth = True
                        elif mask_ocean[neighbor]: # Connected to OCEAN node
                            if self.face_r_gates_per_tet_face[tet_idx, face_idx] >= probe_radius:
                                is_mouth = True
                        
                        if is_mouth:
                            # Get atoms of this face
                            # face_idx 0: (0,1,2), 1: (0,1,3), 2: (0,2,3), 3: (1,2,3)
                            tet_atoms = self.tetra_atoms[tet_idx]
                            if face_idx == 0:   face_atoms = (tet_atoms[0], tet_atoms[1], tet_atoms[2])
                            elif face_idx == 1: face_atoms = (tet_atoms[0], tet_atoms[1], tet_atoms[3])
                            elif face_idx == 2: face_atoms = (tet_atoms[0], tet_atoms[2], tet_atoms[3])
                            elif face_idx == 3: face_atoms = (tet_atoms[1], tet_atoms[2], tet_atoms[3])
                            mouth_faces.append(tuple(sorted(face_atoms)))
                
                # 2. Build Face Adjacency Graph
                # Two faces are connected if they share 2 atoms (an edge)
                # Map: edge (atom_a, atom_b) -> [face_index_in_list, ...]
                
                edge_to_faces = {}
                for f_idx, face in enumerate(mouth_faces):
                    # Edges of the face: (0,1), (0,2), (1,2)
                    edges = [
                        (face[0], face[1]),
                        (face[0], face[2]),
                        (face[1], face[2])
                    ]
                    for edge in edges:
                        if edge not in edge_to_faces:
                            edge_to_faces[edge] = []
                        edge_to_faces[edge].append(f_idx)
                
                # Build adjacency list for faces
                n_faces = len(mouth_faces)
                if n_faces > 0:
                    face_adj = [[] for _ in range(n_faces)]
                    for edge, f_indices in edge_to_faces.items():
                        # If an edge is shared by multiple mouth faces, they are connected
                        # In a manifold surface, an edge is shared by at most 2 faces.
                        # But here "mouth faces" might be a cloud.
                        for i in range(len(f_indices)):
                            for j in range(i + 1, len(f_indices)):
                                u, v = f_indices[i], f_indices[j]
                                face_adj[u].append(v)
                                face_adj[v].append(u)
                    
                    # Connected components of faces
                    # Simple BFS/DFS
                    visited_faces = [False] * n_faces
                    n_mouths = 0
                    for f in range(n_faces):
                        if not visited_faces[f]:
                            n_mouths += 1
                            stack = [f]
                            visited_faces[f] = True
                            while stack:
                                curr = stack.pop()
                                for neighbor in face_adj[curr]:
                                    if not visited_faces[neighbor]:
                                        visited_faces[neighbor] = True
                                        stack.append(neighbor)
                else:
                    n_mouths = 0 # Should not happen if connected_to_ocean is true, unless only via corner?
                
                feature_data['n_mouths'] = n_mouths
                
                if n_mouths > 1:
                    channels.append(feature_data)
                else:
                    pockets.append(feature_data)
            else:
                # Void (0 mouths)
                feature_data['n_mouths'] = 0
                voids.append(feature_data)
        
                # --- DRY NETWORK ANALYSIS (Unchanged) ---
                # The Dry Network is the complement of (Wet + Ocean).
                # Wet = Transit + Coast.
                # So Dry = Solid - Coast.
                # Effectively, nodes that are "Deep Solid".
                
                mask_dry_final = mask_candidate_coast.copy() # Start with all candidates
                # Remove those that became COAST
                for c_idx in coast_node_to_label:
                    mask_dry_final[c_idx] = False
                    
                # Also remove nodes that are actually too small (R_in very small)? 
                # No, SOLID is SOLID.
                
                # Build adjacency for DRY nodes
                mask_edges_solid = mask_dry_final[self.sources] & mask_dry_final[self.targets]
                
                valid_sources_dry = self.sources[mask_edges_solid]
                valid_targets_dry = self.targets[mask_edges_solid]
                valid_weights_dry = np.ones(len(valid_sources_dry), dtype=np.int8)
                
                adj_matrix_dry = coo_matrix((valid_weights_dry, (valid_sources_dry, valid_targets_dry)), 
                                            shape=(self.n_tetrahedra, self.n_tetrahedra))
                
                n_comps_dry, labels_dry = connected_components(adj_matrix_dry, directed=False)
                
                dry_components = []
                nodes_by_component_dry = {}
                
                for idx in np.where(mask_dry_final)[0]:
                    lab = labels_dry[idx]
                    if lab not in nodes_by_component_dry:
                        nodes_by_component_dry[lab] = []
                    nodes_by_component_dry[lab].append(idx)
                    
                for lab, nodes in nodes_by_component_dry.items():
                    if len(nodes) < min_size: continue # Pruning for dry as well? Maybe.
                    
                    atom_indices_local = set()
                    for tet_idx in nodes:
                        atom_indices_local.update(self.tetra_atoms[tet_idx])
                    atom_indices_global = [self.atom_indices_map[k] for k in atom_indices_local]
                    
                    dry_components.append({
                        'id': int(lab),
                        'tetrahedron_indices': nodes,
                        'atom_indices': sorted(list(atom_indices_global)),
                        'size': len(nodes)
                    })
                    
                dry_components.sort(key=lambda x: x['size'], reverse=True)
                core = dry_components[0] if dry_components else None
                islands = dry_components[1:] if len(dry_components) > 1 else []
        
                return {
                    'wet': {
                        'pockets': pockets,
                        'voids': voids
                    },
                    'dry': {
                        'core': core,
                        'islands': islands
                    }
                }
