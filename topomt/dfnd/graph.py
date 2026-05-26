import molsysmt as msm
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from topomt import pyunitwizard as puw
from topomt.delaunay_mesh import DelaunayMesh
from topomt.tools.tessellation import mouth_area_from_faces

from .core.clearance import (
    _KIND_BY_CODE,
    face_gate_radius_batch,
    tetrahedron_residence_radius_batch,
)
from .core.solvent_volume import tetrahedron_solvent_volume_estimate_batch


class DelaunayFlowNetwork:
    """Delaunay Flow Network substrate for DFND analysis."""

    def __init__(
        self,
        molecular_system,
        selection='all',
        structure_indices=0,
        epsilon=1e-6,
        hydrogen_policy='exclude',
        radii_model='vdw',
    ):
        self.molecular_system = molecular_system
        self.selection = selection
        self.structure_indices = structure_indices
        self.epsilon = float(epsilon)
        self.hydrogen_policy = hydrogen_policy
        self.radii_model = radii_model

        topo = msm.convert(
            molecular_system,
            to_form='molsysmt.MolSys',
            structure_indices=structure_indices,
        )
        atom_indices = self._select_atoms(topo, selection, hydrogen_policy)

        atom_coords = puw.get_value(
            msm.get(topo, selection=atom_indices, coordinates=True),
            to_unit='angstroms',
        )[0]
        atom_radii = puw.get_value(
            msm.physchem.get_atomic_radius(
                topo,
                element='atom',
                selection=atom_indices,
                definition=radii_model,
                syntax='MolSysMT',
            ),
            to_unit='angstroms',
        )

        self._initialize_geometry(atom_coords, atom_radii, atom_indices)

    @staticmethod
    def _select_atoms(topo, selection, hydrogen_policy):
        atom_indices = np.asarray(msm.select(topo, selection=selection), dtype=int)
        if atom_indices.size == 0:
            raise ValueError('DFND selection produced no atoms.')
        if hydrogen_policy == 'exclude':
            atom_indices = np.asarray(
                msm.select(topo, selection='atom_type != "H"', mask=atom_indices),
                dtype=int,
            )
            if atom_indices.size == 0:
                raise ValueError(
                    'DFND selection produced no non-hydrogen atoms after hydrogen exclusion.'
                )
            return atom_indices
        if hydrogen_policy == 'include':
            return atom_indices
        raise ValueError("hydrogen_policy must be 'exclude' or 'include'")

    @classmethod
    def from_arrays(cls, coordinates, radii, atom_indices=None, epsilon=1e-6):
        """Build a DFN directly from coordinates and radii for toy systems."""
        instance = cls.__new__(cls)
        instance.molecular_system = None
        instance.selection = 'array'
        instance.structure_indices = 0
        instance.epsilon = float(epsilon)
        instance.hydrogen_policy = 'provided_atoms'
        instance.radii_model = 'provided'
        coordinates = np.asarray(coordinates, dtype=float)
        radii = np.asarray(radii, dtype=float)
        if atom_indices is None:
            atom_indices = np.arange(coordinates.shape[0], dtype=int)
        instance._initialize_geometry(
            coordinates,
            radii,
            np.asarray(atom_indices, dtype=int),
        )
        return instance

    def _initialize_geometry(self, atom_coords, atom_radii, atom_indices_map):
        self.atom_coords = np.asarray(atom_coords, dtype=float)
        self.atom_radii = np.asarray(atom_radii, dtype=float)
        self.atom_indices_map = np.asarray(atom_indices_map, dtype=int)

        if self.atom_coords.ndim != 2 or self.atom_coords.shape[1] != 3:
            raise ValueError('coordinates must have shape (n_atoms, 3)')
        if (
            self.atom_radii.ndim != 1
            or self.atom_radii.shape[0] != self.atom_coords.shape[0]
        ):
            raise ValueError('radii must have shape (n_atoms,)')
        if (
            self.atom_indices_map.ndim != 1
            or self.atom_indices_map.shape[0] != self.atom_coords.shape[0]
        ):
            raise ValueError('atom_indices must have shape (n_atoms,)')
        if self.atom_coords.shape[0] == 0:
            raise ValueError('DFND input contains no atoms.')
        if not np.all(np.isfinite(self.atom_coords)):
            raise ValueError('DFND input coordinates must be finite.')
        if not np.all(np.isfinite(self.atom_radii)):
            raise ValueError('DFND input atomic radii must be finite.')
        if np.any(self.atom_radii <= 0.0):
            raise ValueError('DFND input atomic radii must be positive.')
        if self.atom_coords.shape[0] < 4:
            raise ValueError(
                'Not enough atoms to build Delaunay triangulation (min 4).'
            )

        self.mesh = DelaunayMesh(points=self.atom_coords, atom_radii=self.atom_radii)
        self.tetra_atoms = self.mesh.simplices
        self.simplex_neighbors = self.mesh.neighbors
        self.n_tetrahedra = int(self.tetra_atoms.shape[0])

        tetra_coords = self.atom_coords[self.tetra_atoms]  # (T, 4, 3)
        tetra_radii = self.atom_radii[self.tetra_atoms]  # (T, 4)
        radius, centers, kind_code, r_apollonius4, apollonius4_valid = (
            tetrahedron_residence_radius_batch(tetra_coords, tetra_radii, self.epsilon)
        )
        self.tetra_residence = radius.astype(float)
        self.tetra_residence_centers = centers.astype(float)
        self.tetra_residence_kind = [
            _KIND_BY_CODE[code] if code >= 0 else 'none' for code in kind_code
        ]
        self.tetra_r_apollonius4 = r_apollonius4.astype(float)
        self.tetra_apollonius4_valid = apollonius4_valid.astype(bool)
        (
            solvent_volume,
            solvent_empty_fraction,
            solvent_occupied_fraction,
            solvent_n_samples,
        ) = tetrahedron_solvent_volume_estimate_batch(
            tetra_coords,
            tetra_radii,
            resolution=8,
            epsilon=self.epsilon,
        )
        self.tetra_volume_solvent_estimate = solvent_volume.astype(float)
        self.tetra_solvent_empty_fraction = solvent_empty_fraction.astype(float)
        self.tetra_solvent_occupied_fraction = solvent_occupied_fraction.astype(float)
        self.tetra_solvent_n_samples = solvent_n_samples.astype(int)

        # Per-(tet, face) sorted atom triples. The local face indices match the
        # mesh/SciPy neighbor convention (oriented simplex order); the gate is
        # order-invariant, so sorting the triple is safe.
        face_local_indices = np.array(((1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)))
        face_atom_indices = self.mesh.oriented_simplices[:, face_local_indices]
        self.face_atom_keys_per_tet_face = np.sort(
            face_atom_indices, axis=2
        )  # (T, 4, 3)
        flat_keys = self.face_atom_keys_per_tet_face.reshape(-1, 3)  # (4T, 3)
        unique_faces, first_index, inverse = np.unique(
            flat_keys, axis=0, return_index=True, return_inverse=True
        )
        inverse = np.ravel(inverse)

        # Gate once per UNIQUE face (each internal face is shared by two
        # tetrahedra), then scatter back to (tet, face). This also makes the two
        # sides of a shared face bit-identical.
        unique_gates, _gate_centers, _gate_kinds = face_gate_radius_batch(
            self.atom_coords[unique_faces], self.atom_radii[unique_faces], self.epsilon
        )
        self.face_r_gates_per_tet_face = unique_gates[inverse].reshape(
            self.n_tetrahedra, 4
        )

        # Reproduce the mesh's global face id: 1-based, in first-appearance order
        # over the (simplex, face) iteration (row index == tetrahedron * 4 + face).
        appearance_order = np.argsort(first_index, kind='stable')
        appearance_rank = np.empty(unique_faces.shape[0], dtype=int)
        appearance_rank[appearance_order] = np.arange(unique_faces.shape[0])
        self.face_ids_per_tet_face = (appearance_rank[inverse] + 1).reshape(
            self.n_tetrahedra, 4
        )

        # Gate per unique face (vestigial map kept for compatibility).
        self.unique_face_r_gates_map = {
            tuple(int(a) for a in unique_faces[i]): float(unique_gates[i])
            for i in range(unique_faces.shape[0])
        }

        # Wet/dry edge graph: one undirected edge per internal face (ti < neighbor).
        neighbors = self.simplex_neighbors
        owner_index = np.arange(self.n_tetrahedra)[:, None]
        edge_mask = (neighbors != -1) & (owner_index < neighbors)
        rows, cols = np.nonzero(edge_mask)
        self.sources = rows.astype(int)
        self.targets = neighbors[rows, cols].astype(int)
        self.edge_weights = self.face_r_gates_per_tet_face[rows, cols].astype(float)
        self.edge_source_faces = cols.astype(int)
        self.edge_target_faces = np.array(
            [
                int(np.where(self.simplex_neighbors[target] == source)[0][0])
                for source, target in zip(self.sources.tolist(), self.targets.tolist())
            ],
            dtype=int,
        )
        self.edge_faces = [
            (
                int(r),
                int(c),
                tuple(int(a) for a in self.face_atom_keys_per_tet_face[r, c]),
            )
            for r, c in zip(rows.tolist(), cols.tolist())
        ]
        self.face_intrusion_suspect_per_tet_face = np.zeros(
            (self.n_tetrahedra, 4), dtype=bool
        )
        for tetrahedron_index in range(self.n_tetrahedra):
            for face_index in range(4):
                self.face_intrusion_suspect_per_tet_face[
                    tetrahedron_index, face_index
                ] = self._gate_intrusion_suspect(tetrahedron_index, face_index)

    @staticmethod
    def _classify_component(n_external_links, n_resident_nodes):
        has_residence = n_resident_nodes >= 1
        if n_external_links == 0:
            return 'void' if has_residence else 'degenerate_subprobe'
        if n_external_links == 1:
            return 'pocket' if has_residence else 'surface_concavity'
        return 'multi_external_link' if has_residence else 'nonresident_passage'

    def _state_from_delta(self, value, threshold):
        delta = float(value) - float(threshold)
        if delta > self.epsilon:
            return True, 'open'
        if delta < -self.epsilon:
            return False, 'closed'
        return False, 'marginal'

    def _cluster_external_faces(self, external_faces):
        if not external_faces:
            return []

        edge_to_faces = {}
        for face_list_index, face_record in enumerate(external_faces):
            atoms = face_record['face_atoms_local']
            edges = (
                tuple(sorted((atoms[0], atoms[1]))),
                tuple(sorted((atoms[0], atoms[2]))),
                tuple(sorted((atoms[1], atoms[2]))),
            )
            for edge in edges:
                edge_to_faces.setdefault(edge, []).append(face_list_index)

        adjacency = [[] for _ in external_faces]
        for face_indices in edge_to_faces.values():
            for left_index, left in enumerate(face_indices):
                for right in face_indices[left_index + 1 :]:
                    adjacency[left].append(right)
                    adjacency[right].append(left)

        clusters = []
        visited = np.zeros(len(external_faces), dtype=bool)
        for start in range(len(external_faces)):
            if visited[start]:
                continue
            stack = [start]
            visited[start] = True
            cluster = []
            while stack:
                current = stack.pop()
                cluster.append(external_faces[current])
                for neighbor in adjacency[current]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        stack.append(neighbor)
            clusters.append(cluster)
        return clusters

    def get_topography(
        self,
        probe_radius=1.4,
        sea_level=None,
        min_size=0,
        transit_policy='with_connectors',
        gate_intrusion_policy='flag_only',
        residence_tolerance=0.0,
        permeability_tolerance=0.0,
    ):
        """Return DFND raw records and compatibility feature dictionaries.

        Residence and permeability use an inclusive ``>=`` threshold, with the
        numerical ``epsilon`` applied *in favour of* resident/permeable so the
        equality case is robust to floating-point error. Physical tolerances
        (default 0.0, user-controllable) widen the threshold further to absorb
        structural flexibility / coordinate imprecision:

            permeable(F) = R_gate(F)      >= R_probe - epsilon - permeability_tolerance
            resident(T)  = R_residence(T) >= R_probe - epsilon - residence_tolerance
        """
        probe_radius = float(probe_radius)
        residence_tolerance = float(residence_tolerance)
        permeability_tolerance = float(permeability_tolerance)
        if transit_policy not in {'resident_only', 'with_connectors'}:
            raise ValueError(
                "transit_policy must be 'resident_only' or 'with_connectors'"
            )
        if gate_intrusion_policy not in {'flag_only', 'block_suspect'}:
            raise ValueError(
                "gate_intrusion_policy must be 'flag_only' or 'block_suspect'"
            )

        residence_slack = self.epsilon + residence_tolerance
        permeability_slack = self.epsilon + permeability_tolerance

        residence_delta = self.tetra_residence - probe_radius
        resident = residence_delta >= -residence_slack
        marginal_residence = np.abs(residence_delta) <= residence_slack

        face_delta = self.face_r_gates_per_tet_face - probe_radius
        face_permeable = face_delta >= -permeability_slack
        face_marginal = np.abs(face_delta) <= permeability_slack
        intrusion_suspect = self.face_intrusion_suspect_per_tet_face
        if gate_intrusion_policy == 'block_suspect':
            face_permeable = face_permeable & ~intrusion_suspect

        n_permeable_contacts = np.count_nonzero(face_permeable, axis=1).astype(int)
        connector_candidate = (~resident) & (n_permeable_contacts >= 2)
        if transit_policy == 'with_connectors':
            transit_connector = connector_candidate
        else:
            transit_connector = np.zeros(self.n_tetrahedra, dtype=bool)
        terminal_contact = (~resident) & (n_permeable_contacts == 1)
        if transit_policy == 'resident_only':
            terminal_contact = terminal_contact | connector_candidate
        finite_transit = resident | transit_connector

        valid_edge_mask = (
            finite_transit[self.sources]
            & finite_transit[self.targets]
            & face_permeable[self.sources, self.edge_source_faces]
            & face_permeable[self.targets, self.edge_target_faces]
            & (self.edge_weights > probe_radius + self.epsilon)
        )
        valid_sources = self.sources[valid_edge_mask]
        valid_targets = self.targets[valid_edge_mask]

        adjacency = coo_matrix(
            (
                np.ones(valid_sources.shape[0], dtype=np.int8),
                (valid_sources.astype(int), valid_targets.astype(int)),
            ),
            shape=(self.n_tetrahedra, self.n_tetrahedra),
        )
        _n_components, labels = connected_components(adjacency, directed=False)

        transit_nodes = np.where(finite_transit)[0]
        nodes_by_label = {}
        for node in transit_nodes:
            nodes_by_label.setdefault(int(labels[node]), []).append(int(node))

        face_records = []
        tetrahedron_records = []
        for tetrahedron_index in range(self.n_tetrahedra):
            permeable_count = int(n_permeable_contacts[tetrahedron_index])
            if permeable_count == 4:
                local_class = 'open'
            elif permeable_count == 0:
                local_class = 'sealed'
            else:
                local_class = 'coast'

            if resident[tetrahedron_index]:
                residence_state = 'resident'
                transit_role = 'resident_transit'
            elif transit_connector[tetrahedron_index]:
                residence_state = 'non_resident'
                transit_role = 'transit_connector'
            elif terminal_contact[tetrahedron_index]:
                residence_state = 'non_resident'
                transit_role = 'terminal_contact'
            else:
                residence_state = 'non_resident'
                transit_role = 'non_transit'

            flags = []
            if marginal_residence[tetrahedron_index] or np.any(
                face_marginal[tetrahedron_index]
            ):
                flags.append('marginal')

            tetrahedron_records.append(
                {
                    'tetrahedron_id': int(tetrahedron_index),
                    'atom_indices': [
                        int(self.atom_indices_map[index])
                        for index in self.tetra_atoms[tetrahedron_index]
                    ],
                    'local_atom_indices': [
                        int(index) for index in self.tetra_atoms[tetrahedron_index]
                    ],
                    'R_residence': float(self.tetra_residence[tetrahedron_index]),
                    'residence_candidate_kind': self.tetra_residence_kind[
                        tetrahedron_index
                    ],
                    'R_apollonius4': float(self.tetra_r_apollonius4[tetrahedron_index]),
                    'apollonius4_valid': bool(
                        self.tetra_apollonius4_valid[tetrahedron_index]
                    ),
                    'residence_margin': float(
                        self.tetra_residence[tetrahedron_index] - probe_radius
                    ),
                    'center': self.tetra_residence_centers[tetrahedron_index].tolist(),
                    'volume_topological': float(
                        self.mesh.simplex_volumes[tetrahedron_index]
                    ),
                    'volume_solvent_estimate': float(
                        self.tetra_volume_solvent_estimate[tetrahedron_index]
                    ),
                    'solvent_empty_fraction_estimate': float(
                        self.tetra_solvent_empty_fraction[tetrahedron_index]
                    ),
                    'solvent_occupied_fraction_estimate': float(
                        self.tetra_solvent_occupied_fraction[tetrahedron_index]
                    ),
                    'solvent_volume_n_samples': int(
                        self.tetra_solvent_n_samples[tetrahedron_index]
                    ),
                    'residence_state': residence_state,
                    'transit_role': transit_role,
                    'n_permeable_contacts': permeable_count,
                    'local_class': local_class,
                    'combined_class': f'{"wet" if resident[tetrahedron_index] else "dry"}_{local_class}',
                    'flags': flags,
                }
            )

            for face_index in range(4):
                face_atoms_local = self.face_atom_keys_per_tet_face[tetrahedron_index][
                    face_index
                ]
                face_records.append(
                    {
                        'face_id': int(
                            self.face_ids_per_tet_face[tetrahedron_index, face_index]
                        ),
                        'owner_tetrahedron_id': int(tetrahedron_index),
                        'neighbor_tetrahedron_id': int(
                            self.simplex_neighbors[tetrahedron_index, face_index]
                        ),
                        'face_index': int(face_index),
                        'face_atoms_local': [int(index) for index in face_atoms_local],
                        'atom_indices': [
                            int(self.atom_indices_map[index])
                            for index in face_atoms_local
                        ],
                        'R_gate': float(
                            self.face_r_gates_per_tet_face[
                                tetrahedron_index, face_index
                            ]
                        ),
                        'permeability_state': 'permeable'
                        if face_permeable[tetrahedron_index, face_index]
                        else 'non_permeable',
                        'flags': self._face_flags(
                            tetrahedron_index,
                            face_index,
                            face_marginal,
                            intrusion_suspect,
                            gate_intrusion_policy,
                        ),
                    }
                )

        wet_components = []
        residence_regions = []
        external_links = []
        pockets = []
        voids = []
        channels = []
        surface_concavities = []
        nonresident_passages = []
        degenerate_subprobes = []
        percolatings = []
        compatibility_records = []

        for component_index, (_label, nodes) in enumerate(
            sorted(nodes_by_label.items()), start=1
        ):
            graph_label = int(_label)
            node_set = set(nodes)
            resident_nodes = [node for node in nodes if resident[node]]
            connector_nodes = [node for node in nodes if transit_connector[node]]
            open_resident_nodes = [
                node for node in resident_nodes if int(n_permeable_contacts[node]) == 4
            ]

            external_face_records = []
            seen_external_face_ids = set()
            for node in nodes:
                for face_index in range(4):
                    if (
                        int(self.simplex_neighbors[node, face_index]) == -1
                        and face_permeable[node, face_index]
                    ):
                        face_id = int(self.face_ids_per_tet_face[node, face_index])
                        if face_id in seen_external_face_ids:
                            continue
                        seen_external_face_ids.add(face_id)
                        face_atoms_local = self.face_atom_keys_per_tet_face[node][
                            face_index
                        ]
                        external_face_records.append(
                            {
                                'tetrahedron_id': int(node),
                                'face_index': int(face_index),
                                'face_id': face_id,
                                'face_atoms_local': tuple(
                                    int(index) for index in face_atoms_local
                                ),
                                'atom_indices': [
                                    int(self.atom_indices_map[index])
                                    for index in face_atoms_local
                                ],
                                'R_gate': float(
                                    self.face_r_gates_per_tet_face[node, face_index]
                                ),
                            }
                        )

            external_face_clusters = self._cluster_external_faces(external_face_records)
            component_external_link_ids = []
            for link_offset, cluster in enumerate(external_face_clusters, start=1):
                link_id = len(external_links) + 1
                component_external_link_ids.append(link_id)
                cluster_faces = [record['face_atoms_local'] for record in cluster]
                external_links.append(
                    {
                        'external_link_id': link_id,
                        'component_id': component_index,
                        'local_link_id': link_offset,
                        'face_ids': [record['face_id'] for record in cluster],
                        'tetrahedron_ids': sorted(
                            {record['tetrahedron_id'] for record in cluster}
                        ),
                        'faces': [
                            list(record['face_atoms_local']) for record in cluster
                        ],
                        'atom_indices': sorted(
                            {
                                atom
                                for record in cluster
                                for atom in record['atom_indices']
                            }
                        ),
                        'area_geometric': mouth_area_from_faces(
                            cluster_faces, self.atom_coords
                        ),
                        'R_gate_min': float(
                            min(record['R_gate'] for record in cluster)
                        ),
                        'R_gate_max': float(
                            max(record['R_gate'] for record in cluster)
                        ),
                        'flags': [],
                    }
                )

            n_external_links = len(component_external_link_ids)
            # Walls = non-permeable boundary faces of the component (faces whose other
            # side is OCEAN or another component). A resident component with zero walls
            # is fully permeable/exposed (porous), not a concavity -> percolating.
            n_wall_faces = 0
            for node in nodes:
                for face_index in range(4):
                    neighbor = int(self.simplex_neighbors[node, face_index])
                    is_boundary = neighbor == -1 or neighbor not in node_set
                    if is_boundary and not face_permeable[node, face_index]:
                        n_wall_faces += 1
            family = self._classify_component(n_external_links, len(resident_nodes))
            if resident_nodes and n_wall_faces == 0:
                family = 'percolating'
            atom_indices = sorted(
                {
                    int(self.atom_indices_map[atom_index])
                    for node in nodes
                    for atom_index in self.tetra_atoms[node]
                }
            )
            volume_topological_transit = float(np.sum(self.mesh.simplex_volumes[nodes]))
            volume_topological_resident = (
                float(np.sum(self.mesh.simplex_volumes[resident_nodes]))
                if resident_nodes
                else 0.0
            )
            volume_solvent_estimate = (
                float(np.sum(self.tetra_volume_solvent_estimate[resident_nodes]))
                if resident_nodes
                else 0.0
            )
            edge_capacities = []
            for source, target, weight, edge_face in zip(
                self.sources, self.targets, self.edge_weights, self.edge_faces
            ):
                owner, face_index, _face_key = edge_face
                target_face_indices = np.where(
                    self.simplex_neighbors[target] == source
                )[0]
                target_face_permeable = (
                    bool(face_permeable[target, target_face_indices[0]])
                    if len(target_face_indices)
                    else True
                )
                shared_face_permeable = (
                    bool(face_permeable[owner, face_index]) and target_face_permeable
                )
                if (
                    int(source) in node_set
                    and int(target) in node_set
                    and shared_face_permeable
                    and weight > probe_radius + self.epsilon
                ):
                    edge_capacities.append(float(weight - probe_radius))
            path_capacity_min = min(edge_capacities) if edge_capacities else None

            component_record = {
                'id': component_index,
                'graph_label': graph_label,
                'family': family,
                'tetrahedron_ids': nodes,
                'resident_tetrahedron_ids': resident_nodes,
                'transit_connector_tetrahedron_ids': connector_nodes,
                'atom_indices': atom_indices,
                'n_nodes': len(nodes),
                'n_resident_nodes': len(resident_nodes),
                'n_transit_connector_nodes': len(connector_nodes),
                'n_external_links': n_external_links,
                'external_link_ids': component_external_link_ids,
                'n_wall_faces': n_wall_faces,
                'has_residence': bool(resident_nodes),
                'n_open_resident_nodes': len(open_resident_nodes),
                'has_open_interior': bool(open_resident_nodes),
                'volume_topological_transit': volume_topological_transit,
                'volume_topological_resident': volume_topological_resident,
                'volume_solvent_estimate': volume_solvent_estimate,
                'path_capacity_min': path_capacity_min,
                'center': np.mean(self.mesh.simplex_centers[nodes], axis=0).tolist(),
                'flags': [],
            }
            if family in {
                'surface_concavity',
                'nonresident_passage',
                'degenerate_subprobe',
            }:
                component_record['flags'].append('provisional')
            if connector_nodes:
                component_record['flags'].append('contains_transit_connector')

            wet_components.append(component_record)

            if resident_nodes:
                residence_regions.append(
                    {
                        'residence_region_id': len(residence_regions) + 1,
                        'component_id': component_index,
                        'tetrahedron_ids': resident_nodes,
                        'transit_connector_tetrahedron_ids': connector_nodes,
                        'volume_topological_resident': volume_topological_resident,
                        'volume_solvent_estimate': volume_solvent_estimate,
                        'flags': [],
                    }
                )

            compatibility_record = {
                'id': component_index,
                'graph_label': graph_label,
                'family': family,
                'tetrahedron_indices': nodes,
                'transit_indices': nodes,
                'resident_tetrahedron_indices': resident_nodes,
                'transit_connector_tetrahedron_indices': connector_nodes,
                'atom_indices': atom_indices,
                'center': np.asarray(component_record['center'], dtype=float),
                'n_wall_faces': n_wall_faces,
                'volume_topological_resident': volume_topological_resident,
                'volume_solvent_estimate': volume_solvent_estimate,
                'n_mouths': n_external_links,
                'mouth_area': float(
                    sum(
                        external_links[link_id - 1]['area_geometric']
                        for link_id in component_external_link_ids
                    )
                ),
                'mouths': [
                    external_links[link_id - 1]
                    for link_id in component_external_link_ids
                ],
                'mouth_face_clusters': [
                    external_links[link_id - 1]['faces']
                    for link_id in component_external_link_ids
                ],
                'flags': list(component_record['flags']),
            }

            compatibility_records.append(compatibility_record)

            include_in_compatibility_view = not min_size or len(nodes) >= min_size
            if include_in_compatibility_view:
                if family == 'void':
                    voids.append(compatibility_record)
                elif family == 'pocket':
                    pockets.append(compatibility_record)
                elif family == 'multi_external_link':
                    channels.append(compatibility_record)
                elif family == 'surface_concavity':
                    surface_concavities.append(compatibility_record)
                elif family == 'nonresident_passage':
                    nonresident_passages.append(compatibility_record)
                elif family == 'percolating':
                    percolatings.append(compatibility_record)
                else:
                    degenerate_subprobes.append(compatibility_record)

        wet_components.sort(
            key=lambda record: (-record['n_nodes'], record['graph_label'])
        )
        wet_id_map = {}
        for component_index, record in enumerate(wet_components):
            old_id = int(record['id'])
            new_id = component_index + 1
            wet_id_map[old_id] = new_id
            record['id'] = new_id
            record['component_index'] = component_index
            record['size_rank'] = new_id

        for link in external_links:
            link['component_id'] = wet_id_map[int(link['component_id'])]
        for region in residence_regions:
            region['component_id'] = wet_id_map[int(region['component_id'])]
        for record in compatibility_records:
            old_id = int(record['id'])
            new_id = wet_id_map[old_id]
            record['id'] = new_id
            record['component_index'] = new_id - 1
            record['size_rank'] = new_id

        for family_records in (
            pockets,
            voids,
            channels,
            surface_concavities,
            nonresident_passages,
            percolatings,
            degenerate_subprobes,
        ):
            family_records.sort(
                key=lambda record: (
                    -len(record['tetrahedron_indices']),
                    record['graph_label'],
                )
            )

        dry_mask = ~resident
        dry_components = self._build_dry_components(dry_mask, face_permeable, min_size)
        dry_components.sort(key=lambda record: (-record['size'], record['graph_label']))
        for component_index, record in enumerate(dry_components):
            new_id = component_index + 1
            record['id'] = new_id
            record['component_index'] = component_index
            record['size_rank'] = new_id
        dry_interfaces = self._build_dry_interfaces(
            dry_components, dry_mask, face_permeable
        )
        self._assign_dry_depths(dry_components, dry_interfaces)
        dry_motifs = self._build_dry_motifs(dry_components, dry_interfaces)

        return {
            'raw': {
                'parameters': {
                    'probe_radius': probe_radius,
                    'epsilon_length': self.epsilon,
                    'residence_tolerance': residence_tolerance,
                    'permeability_tolerance': permeability_tolerance,
                    'sea_level': sea_level,
                    'radii_model': self.radii_model,
                    'selection': self.selection,
                    'hydrogen_policy': self.hydrogen_policy,
                    'transit_policy': transit_policy,
                    'gate_intrusion_policy': gate_intrusion_policy,
                },
                'tetrahedra': tetrahedron_records,
                'faces': face_records,
                'wet_components': wet_components,
                'residence_regions': residence_regions,
                'external_links': external_links,
                'dry_interfaces': dry_interfaces,
                'dry_motifs': dry_motifs,
                'flags': [],
            },
            'wet': {
                'pockets': pockets,
                'voids': voids,
                'channels': channels,
                'surface_concavities': surface_concavities,
                'nonresident_passages': nonresident_passages,
                'degenerate_subprobes': degenerate_subprobes,
                'percolatings': percolatings,
            },
            'dry': {
                'core': dry_components[0] if dry_components else None,
                'islands': dry_components[1:] if len(dry_components) > 1 else [],
                'components': dry_components,
                'interfaces': dry_interfaces,
                'motifs': dry_motifs,
            },
        }

    def _face_flags(
        self,
        tetrahedron_index,
        face_index,
        face_marginal,
        intrusion_suspect,
        gate_intrusion_policy,
    ):
        flags = []
        if face_marginal[tetrahedron_index, face_index]:
            flags.append('marginal')
        if intrusion_suspect[tetrahedron_index, face_index]:
            flags.append('intrusion_suspect')
            if gate_intrusion_policy == 'block_suspect':
                flags.append('blocked_by_intrusion_policy')
        return flags

    def _gate_intrusion_suspect(self, tetrahedron_index, face_index):
        face_atoms = set(
            self.face_atom_keys_per_tet_face[tetrahedron_index][face_index]
        )
        tetra_atoms = set(int(index) for index in self.tetra_atoms[tetrahedron_index])
        opposite_atoms = list(tetra_atoms - face_atoms)
        if not opposite_atoms:
            return False
        opposite_atom = opposite_atoms[0]
        face_atom_indices = list(face_atoms)
        p0, p1, p2 = self.atom_coords[face_atom_indices]
        normal = np.cross(p1 - p0, p2 - p0)
        norm = np.linalg.norm(normal)
        if norm <= self.epsilon:
            return True
        distance = abs(
            float(np.dot(self.atom_coords[opposite_atom] - p0, normal / norm))
        )
        return distance <= float(self.atom_radii[opposite_atom]) + self.epsilon

    def _build_dry_interfaces(self, dry_components, dry_mask, face_permeable):
        component_id_by_node = {}
        for component in dry_components:
            for node in component['tetrahedron_indices']:
                component_id_by_node[int(node)] = int(component['id'])

        dry_interfaces = []
        for tetrahedron_index in sorted(component_id_by_node):
            component_id = component_id_by_node[tetrahedron_index]
            for face_index, neighbor in enumerate(
                self.simplex_neighbors[tetrahedron_index]
            ):
                neighbor = int(neighbor)
                is_permeable = bool(face_permeable[tetrahedron_index, face_index])
                if neighbor >= 0 and dry_mask[neighbor] and not is_permeable:
                    continue

                if neighbor == -1:
                    interface_kind = (
                        'hull_permeable' if is_permeable else 'hull_blocked'
                    )
                    target_component_id = None
                    target_tetrahedron_id = None
                    target_residence_state = 'ocean'
                elif dry_mask[neighbor]:
                    interface_kind = 'dry_permeable_contact'
                    target_component_id = component_id_by_node.get(neighbor)
                    target_tetrahedron_id = neighbor
                    target_residence_state = 'non_resident'
                else:
                    target_component_id = None
                    target_tetrahedron_id = neighbor
                    if np.count_nonzero(face_permeable[neighbor]) >= 2:
                        target_residence_state = 'resident_or_transit'
                        interface_kind = 'transit_contact'
                    else:
                        target_residence_state = 'resident'
                        interface_kind = 'resident_wall'

                face_atoms_local = self.face_atom_keys_per_tet_face[tetrahedron_index][
                    face_index
                ]
                dry_interfaces.append(
                    {
                        'dry_interface_id': len(dry_interfaces) + 1,
                        'dry_component_id': component_id,
                        'tetrahedron_id': int(tetrahedron_index),
                        'face_index': int(face_index),
                        'face_id': int(
                            self.face_ids_per_tet_face[
                                tetrahedron_index,
                                face_index,
                            ]
                        ),
                        'face_atoms_local': [int(atom) for atom in face_atoms_local],
                        'atom_indices': [
                            int(self.atom_indices_map[atom])
                            for atom in face_atoms_local
                        ],
                        'neighbor_tetrahedron_id': target_tetrahedron_id,
                        'target_dry_component_id': target_component_id,
                        'target_residence_state': target_residence_state,
                        'interface_kind': interface_kind,
                        'R_gate': float(
                            self.face_r_gates_per_tet_face[
                                tetrahedron_index,
                                face_index,
                            ]
                        ),
                        'permeability_state': (
                            'permeable' if is_permeable else 'non_permeable'
                        ),
                        'touches_hull': bool(neighbor == -1),
                        'touches_ocean': bool(neighbor == -1 and is_permeable),
                        'flags': [],
                    }
                )
        return dry_interfaces

    def _assign_dry_depths(self, dry_components, dry_interfaces):
        interfaces_by_component = {}
        for interface in dry_interfaces:
            component_id = int(interface['dry_component_id'])
            interfaces_by_component.setdefault(component_id, []).append(interface)

        for component in dry_components:
            nodes = [int(node) for node in component['tetrahedron_indices']]
            node_set = set(nodes)
            adjacency = {node: set() for node in nodes}
            for edge in component['dry_edges']:
                source = int(edge['source_tetrahedron_id'])
                target = int(edge['target_tetrahedron_id'])
                if source in node_set and target in node_set:
                    adjacency[source].add(target)
                    adjacency[target].add(source)

            component_interfaces = interfaces_by_component.get(int(component['id']), [])
            boundary_nodes = sorted(
                {int(interface['tetrahedron_id']) for interface in component_interfaces}
            )
            depths = {node: None for node in nodes}
            queue = list(boundary_nodes)
            for node in queue:
                depths[node] = 0

            cursor = 0
            while cursor < len(queue):
                node = queue[cursor]
                cursor += 1
                for neighbor in sorted(adjacency[node]):
                    if depths[neighbor] is None:
                        depths[neighbor] = depths[node] + 1
                        queue.append(neighbor)

            finite_depths = [depth for depth in depths.values() if depth is not None]
            component['dry_interface_ids'] = [
                int(interface['dry_interface_id']) for interface in component_interfaces
            ]
            component['dry_boundary_tetrahedron_ids'] = boundary_nodes
            component['dry_depth_by_tetrahedron'] = depths
            component['dry_depth_min'] = min(finite_depths) if finite_depths else None
            component['dry_depth_max'] = max(finite_depths) if finite_depths else None
            component['dry_depth_mean'] = (
                float(np.mean(finite_depths)) if finite_depths else None
            )

    def _build_dry_motifs(self, dry_components, dry_interfaces):
        interfaces_by_component = {}
        for interface in dry_interfaces:
            component_id = int(interface['dry_component_id'])
            interfaces_by_component.setdefault(component_id, []).append(interface)

        dry_motifs = []
        for component in dry_components:
            component_id = int(component['id'])
            depth_by_node = {
                int(node): depth
                for node, depth in component['dry_depth_by_tetrahedron'].items()
            }
            component_interfaces = interfaces_by_component.get(component_id, [])

            boundary_nodes = sorted(
                {int(interface['tetrahedron_id']) for interface in component_interfaces}
            )
            if boundary_nodes:
                dry_motifs.append(
                    self._dry_motif_record(
                        dry_motifs,
                        component_id,
                        'dry_boundary_shell',
                        boundary_nodes,
                        component_interfaces,
                        None,
                    )
                )

            ocean_interfaces = [
                interface
                for interface in component_interfaces
                if interface['touches_ocean']
            ]
            ocean_nodes = sorted(
                {int(interface['tetrahedron_id']) for interface in ocean_interfaces}
            )
            if ocean_nodes:
                dry_motifs.append(
                    self._dry_motif_record(
                        dry_motifs,
                        component_id,
                        'dry_ocean_exposed_shell',
                        ocean_nodes,
                        ocean_interfaces,
                        None,
                    )
                )

            lining_interfaces = [
                interface
                for interface in component_interfaces
                if interface['interface_kind'] in {'resident_wall', 'transit_contact'}
            ]
            lining_nodes = sorted(
                {int(interface['tetrahedron_id']) for interface in lining_interfaces}
            )
            if lining_nodes:
                dry_motifs.append(
                    self._dry_motif_record(
                        dry_motifs,
                        component_id,
                        'dry_resident_lining',
                        lining_nodes,
                        lining_interfaces,
                        None,
                    )
                )

            finite_depths = [
                depth for depth in depth_by_node.values() if depth is not None
            ]
            if finite_depths:
                max_depth = max(finite_depths)
                if max_depth > 0:
                    core_nodes = sorted(
                        node
                        for node, depth in depth_by_node.items()
                        if depth == max_depth
                    )
                    dry_motifs.append(
                        self._dry_motif_record(
                            dry_motifs,
                            component_id,
                            'dry_core_candidate',
                            core_nodes,
                            [],
                            max_depth,
                        )
                    )
        return dry_motifs

    def _dry_motif_record(
        self,
        dry_motifs,
        component_id,
        motif_type,
        tetrahedron_ids,
        interfaces,
        dry_depth,
    ):
        atom_indices = sorted(
            {
                int(self.atom_indices_map[atom_index])
                for node in tetrahedron_ids
                for atom_index in self.tetra_atoms[node]
            }
        )
        return {
            'dry_motif_id': len(dry_motifs) + 1,
            'dry_component_id': int(component_id),
            'motif_type': motif_type,
            'tetrahedron_ids': [int(node) for node in tetrahedron_ids],
            'atom_indices': atom_indices,
            'dry_interface_ids': [
                int(interface['dry_interface_id']) for interface in interfaces
            ],
            'dry_depth': None if dry_depth is None else int(dry_depth),
            'flags': ['candidate'],
        }

    def _build_dry_components(self, dry_mask, face_permeable, min_size):
        sources = []
        targets = []
        dry_edges = []
        for tetrahedron_index in range(self.n_tetrahedra):
            if not dry_mask[tetrahedron_index]:
                continue
            for face_index, neighbor in enumerate(
                self.simplex_neighbors[tetrahedron_index]
            ):
                neighbor = int(neighbor)
                if neighbor == -1 or tetrahedron_index >= neighbor:
                    continue
                target_face_indices = np.where(
                    self.simplex_neighbors[neighbor] == tetrahedron_index
                )[0]
                target_face_index = (
                    int(target_face_indices[0]) if len(target_face_indices) else -1
                )
                shared_face_non_permeable = not bool(
                    face_permeable[tetrahedron_index, face_index]
                )
                if target_face_index >= 0:
                    shared_face_non_permeable = shared_face_non_permeable and not bool(
                        face_permeable[neighbor, target_face_index]
                    )
                if dry_mask[neighbor] and shared_face_non_permeable:
                    sources.append(tetrahedron_index)
                    targets.append(neighbor)
                    dry_edges.append(
                        {
                            'source_tetrahedron_id': int(tetrahedron_index),
                            'target_tetrahedron_id': int(neighbor),
                            'source_face_index': int(face_index),
                            'target_face_index': target_face_index,
                            'face_id': int(
                                self.face_ids_per_tet_face[
                                    tetrahedron_index, face_index
                                ]
                            ),
                            'face_atoms_local': [
                                int(atom)
                                for atom in self.face_atom_keys_per_tet_face[
                                    tetrahedron_index,
                                    face_index,
                                ]
                            ],
                        }
                    )

        adjacency = coo_matrix(
            (
                np.ones(len(sources), dtype=np.int8),
                (np.asarray(sources, dtype=int), np.asarray(targets, dtype=int)),
            ),
            shape=(self.n_tetrahedra, self.n_tetrahedra),
        )
        _n_components, labels = connected_components(adjacency, directed=False)

        nodes_by_label = {}
        for node in np.where(dry_mask)[0]:
            nodes_by_label.setdefault(int(labels[node]), []).append(int(node))

        edges_by_label = {}
        for edge in dry_edges:
            label = int(labels[edge['source_tetrahedron_id']])
            edges_by_label.setdefault(label, []).append(edge)

        dry_components = []
        for label, nodes in nodes_by_label.items():
            if min_size and len(nodes) < min_size:
                continue
            atom_indices = sorted(
                {
                    int(self.atom_indices_map[atom_index])
                    for node in nodes
                    for atom_index in self.tetra_atoms[node]
                }
            )
            component_edges = edges_by_label.get(label, [])
            dry_components.append(
                {
                    'id': int(label),
                    'graph_label': int(label),
                    'tetrahedron_indices': nodes,
                    'atom_indices': atom_indices,
                    'size': len(nodes),
                    'dry_edges': component_edges,
                    'dry_edge_face_ids': [edge['face_id'] for edge in component_edges],
                    'flags': [],
                }
            )
        return dry_components
