import numpy as np
import pytest

from topomt.dfnd.graph import DelaunayFlowNetwork


def test_regular_tetrahedron_is_wet_sealed_void_domain():
    coords = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )
    radii = np.full(4, 1.7, dtype=float)

    network = DelaunayFlowNetwork.from_arrays(coords, radii)
    result = network.get_topography(probe_radius=1.4, min_size=0)

    assert len(result['raw']['concavity_domains']) == 1
    domain = result['raw']['concavity_domains'][0]
    assert domain['domain_family'] == 'void_domain'
    assert domain['n_external_links'] == 0
    assert domain['has_residence'] is True
    assert domain['has_open_interior'] is False

    tetra = result['raw']['tetrahedra'][0]
    assert tetra['residence_state'] == 'resident'
    assert tetra['local_class'] == 'sealed'
    assert tetra['combined_class'] == 'wet_sealed'


def test_access_residence_classifier_does_not_require_open_interior():
    network = DelaunayFlowNetwork.__new__(DelaunayFlowNetwork)

    assert network._classify_domain(0, 1) == 'void_domain'
    assert network._classify_domain(0, 0) == 'degenerate_subprobe_domain'
    assert network._classify_domain(1, 1) == 'pocket_domain'
    assert network._classify_domain(1, 0) == 'surface_concavity_domain'
    assert network._classify_domain(2, 1) == 'multi_external_link_domain'
    assert network._classify_domain(2, 0) == 'nonresident_passage_domain'


def test_threshold_state_policy_is_deterministic_at_epsilon_boundary():
    network = DelaunayFlowNetwork.__new__(DelaunayFlowNetwork)
    network.epsilon = 1e-6

    assert network._state_from_delta(1.0 + 2e-6, 1.0) == (True, 'open')
    assert network._state_from_delta(1.0 - 2e-6, 1.0) == (False, 'closed')
    assert network._state_from_delta(1.0 + 0.5e-6, 1.0) == (False, 'marginal')
    assert network._state_from_delta(1.0 - 0.5e-6, 1.0) == (False, 'marginal')
    assert network._state_from_delta(1.0, 1.0) == (False, 'marginal')


def test_marginal_residence_is_flagged_in_raw_tetrahedron_records():
    coords = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )
    radii = np.full(4, 1.7, dtype=float)
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-6)
    probe_radius = float(network.tetra_residence[0])

    result = network.get_topography(probe_radius=probe_radius, min_size=0)
    tetrahedron = result['raw']['tetrahedra'][0]

    assert tetrahedron['residence_state'] == 'non_resident'
    assert tetrahedron['residence_margin'] == pytest.approx(0.0, abs=1e-12)
    assert 'marginal' in tetrahedron['flags']
    assert result['raw']['concavity_domains'] == []


def test_marginal_gate_is_flagged_in_raw_face_and_owner_tetrahedron_records():
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [4.0, 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 4.0],
            [4.0, 4.0, 4.0],
        ],
        dtype=float,
    )
    radii = np.full(5, 0.5, dtype=float)
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-6)
    probe_radius = float(network.face_r_gates_per_tet_face[0, 0])

    result = network.get_topography(probe_radius=probe_radius, min_size=0)
    marginal_faces = [
        face
        for face in result['raw']['faces']
        if abs(face['R_gate'] - probe_radius) <= network.epsilon
    ]
    assert marginal_faces
    assert all('marginal' in face['flags'] for face in marginal_faces)
    assert all(face['permeability_state'] == 'non_permeable' for face in marginal_faces)

    marginal_owner_ids = {face['owner_tetrahedron_id'] for face in marginal_faces}
    owner_tetrahedra = [
        tetrahedron
        for tetrahedron in result['raw']['tetrahedra']
        if tetrahedron['tetrahedron_id'] in marginal_owner_ids
    ]
    assert owner_tetrahedra
    assert all('marginal' in tetrahedron['flags'] for tetrahedron in owner_tetrahedra)


def test_transit_policy_is_recorded_and_validated():
    coords = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )
    radii = np.full(4, 1.7, dtype=float)
    network = DelaunayFlowNetwork.from_arrays(coords, radii)

    result = network.get_topography(probe_radius=1.4, transit_policy='resident_only')
    assert result['raw']['parameters']['transit_policy'] == 'resident_only'


def test_input_policy_is_recorded_for_array_toys():
    coords = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )
    radii = np.full(4, 1.7, dtype=float)
    network = DelaunayFlowNetwork.from_arrays(coords, radii)
    result = network.get_topography(probe_radius=1.4)

    assert result['raw']['parameters']['hydrogen_policy'] == 'provided_atoms'
    assert result['raw']['parameters']['radii_model'] == 'provided'


def test_dry_open_cut_connector_policy_can_merge_resident_regions():
    coords = np.array(
        [
            [-0.42, -0.58, -0.19],
            [0.17, -0.34, 1.52],
            [-0.36, 1.2, 1.1],
            [-0.2, 1.4, 1.85],
            [9.66, 0.89, -1.73],
            [9.61, 1.13, 1.86],
            [8.58, 0.24, 1.23],
            [8.34, 0.67, -2.9],
            [4.43, 0.69, -0.26],
            [4.82, 0.07, -0.52],
        ],
        dtype=float,
    )
    radii = np.array(
        [1.51, 1.48, 1.51, 1.67, 1.65, 1.59, 1.52, 1.61, 1.61, 1.6], dtype=float
    )

    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    resident_only = network.get_topography(
        probe_radius=1.4,
        transit_policy='resident_only',
        min_size=0,
    )
    with_connectors = network.get_topography(
        probe_radius=1.4,
        transit_policy='with_connectors',
        min_size=0,
    )

    connector_domains = [
        domain
        for domain in with_connectors['raw']['concavity_domains']
        if domain['n_transit_connector_nodes'] >= 1 and domain['n_resident_nodes'] >= 2
    ]
    assert connector_domains

    merged_domain = connector_domains[0]
    merged_residents = set(merged_domain['resident_tetrahedron_ids'])
    assert 'contains_transit_connector' in merged_domain['flags']

    # Without connectors, those resident tetrahedra are not all in one domain:
    # the connector is what bridges them.
    resident_only_domains = [
        set(domain['resident_tetrahedron_ids'])
        for domain in resident_only['raw']['concavity_domains']
    ]
    assert not any(merged_residents <= domain for domain in resident_only_domains)


def test_wet_coast_one_link_domain_is_pocket_not_surface_concavity():
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [5.56834006, 0.0, 0.0],
            [2.47806446, 5.50825565, 0.0],
            [2.61734153, 1.81724939, 3.46531621],
        ],
        dtype=float,
    )
    radii = np.array([1.71923894, 1.53403038, 1.75274022, 1.87381129], dtype=float)

    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-8)
    result = network.get_topography(probe_radius=1.4, min_size=0)

    assert len(result['raw']['concavity_domains']) == 1
    domain = result['raw']['concavity_domains'][0]
    tetrahedron = result['raw']['tetrahedra'][0]

    assert tetrahedron['combined_class'] == 'wet_coast'
    assert tetrahedron['n_permeable_contacts'] < 4
    assert domain['n_external_links'] == 1
    assert domain['has_residence'] is True
    assert domain['has_open_interior'] is False
    assert domain['domain_family'] == 'pocket_domain'
    assert result['wet']['surface_concavities'] == []


def test_external_link_clustering_uses_face_edge_connectivity():
    network = DelaunayFlowNetwork.__new__(DelaunayFlowNetwork)
    external_faces = [
        {'face_atoms_local': (0, 1, 2)},
        {'face_atoms_local': (0, 1, 3)},
        {'face_atoms_local': (4, 5, 6)},
    ]

    clusters = network._cluster_external_faces(external_faces)
    cluster_sizes = sorted(len(cluster) for cluster in clusters)

    assert cluster_sizes == [1, 2]


def test_external_link_clustering_does_not_merge_vertex_only_contact():
    network = DelaunayFlowNetwork.__new__(DelaunayFlowNetwork)
    external_faces = [
        {'face_atoms_local': (0, 1, 2)},
        {'face_atoms_local': (0, 3, 4)},
    ]

    clusters = network._cluster_external_faces(external_faces)

    assert len(clusters) == 2


def _network_from_random_points(seed, n_atoms):
    rng = np.random.default_rng(seed)
    coords = rng.uniform(0.0, 8.0, size=(n_atoms, 3))
    radii = rng.uniform(1.0, 1.9, size=n_atoms)
    return DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)


def _two_tetrahedra_fixture():
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [4.0, 0.0, 0.0],
            [0.0, 4.0, 0.0],
            [0.0, 0.0, 4.0],
            [4.0, 4.0, 4.0],
        ],
        dtype=float,
    )
    radii = np.full(5, 0.5, dtype=float)
    return DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-8)


def test_face_records_are_traceable_to_global_face_ids_and_atom_triples():
    network = _two_tetrahedra_fixture()
    result = network.get_topography(probe_radius=0.5, min_size=0)

    face_records = result['raw']['faces']
    by_face_id = {}
    for face in face_records:
        owner = face['owner_tetrahedron_id']
        face_index = face['face_index']
        face_atoms = tuple(face['face_atoms_local'])
        face_id = face['face_id']

        assert face_atoms == network.mesh.get_face_atoms(owner, face_index)
        assert face_id == network.mesh.get_face_index(owner, face_index)
        assert face_id == network.mesh.get_face_index_from_atoms(face_atoms)
        by_face_id.setdefault(face_id, []).append(face)

    for owners in by_face_id.values():
        assert len(owners) in {1, 2}
        if len(owners) == 1:
            assert owners[0]['neighbor_tetrahedron_id'] == -1
        else:
            left, right = owners
            assert left['neighbor_tetrahedron_id'] == right['owner_tetrahedron_id']
            assert right['neighbor_tetrahedron_id'] == left['owner_tetrahedron_id']
            assert left['face_atoms_local'] == right['face_atoms_local']


def test_shared_faces_have_one_gate_value_and_one_global_face_id():
    network = _two_tetrahedra_fixture()
    result = network.get_topography(probe_radius=0.5, min_size=0)

    records_by_id = {}
    for face in result['raw']['faces']:
        records_by_id.setdefault(face['face_id'], []).append(face)

    shared = [records for records in records_by_id.values() if len(records) == 2]
    assert shared
    for left, right in shared:
        assert left['face_id'] == right['face_id']
        assert left['face_atoms_local'] == right['face_atoms_local']
        assert left['R_gate'] == pytest.approx(right['R_gate'], abs=1e-12)
        assert left['permeability_state'] == right['permeability_state']


def test_external_links_reference_existing_boundary_faces_and_atoms():
    network = DelaunayFlowNetwork.from_arrays(
        np.array(
            [
                [6.45, 1.31, 4.88],
                [2.66, 6.55, 1.36],
                [1.78, 0.8, 3.18],
                [4.82, 2.04, 6.28],
                [5.6, 1.9, 4.23],
                [4.59, 0.96, 4.54],
                [4.38, 6.1, 2.08],
                [0.96, 3.81, 6.01],
                [0.84, 1.45, 0.73],
                [6.91, 5.32, 0.65],
            ],
            dtype=float,
        ),
        np.array(
            [1.72, 1.52, 1.31, 1.33, 1.42, 1.32, 1.38, 1.33, 1.37, 1.35],
            dtype=float,
        ),
        epsilon=1e-7,
    )
    result = network.get_topography(probe_radius=1.4, min_size=0)
    face_by_id = {face['face_id']: face for face in result['raw']['faces']}

    for external_link in result['raw']['external_links']:
        link_atoms = set(external_link['atom_indices'])
        assert external_link['face_ids']
        assert len(external_link['face_ids']) == len(set(external_link['face_ids']))
        assert external_link['area_geometric'] >= 0.0
        assert external_link['R_gate_min'] <= external_link['R_gate_max']

        for face_id, face_atoms in zip(external_link['face_ids'], external_link['faces']):
            face = face_by_id[face_id]
            assert face['neighbor_tetrahedron_id'] == -1
            assert face['permeability_state'] == 'permeable'
            assert face['face_atoms_local'] == face_atoms
            assert set(face['atom_indices']) <= link_atoms


def test_multi_external_link_domain_has_distinct_external_links():
    coords = np.array(
        [
            [2.86, 0.57, 5.29],
            [6.82, 1.67, 2.13],
            [0.1, 2.12, 0.51],
            [6.78, 6.22, 0.11],
            [3.61, 0.42, 1.71],
            [4.6, 0.57, 1.28],
            [1.44, 5.0, 3.62],
            [0.53, 0.09, 4.84],
            [3.1, 1.69, 2.29],
            [2.42, 5.39, 1.5],
            [2.61, 2.49, 0.49],
        ],
        dtype=float,
    )
    radii = np.array(
        [1.53, 1.56, 1.34, 1.39, 1.69, 1.68, 1.67, 1.59, 1.56, 1.64, 1.55], dtype=float
    )

    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    result = network.get_topography(probe_radius=1.4, min_size=0)

    domains = result['raw']['concavity_domains']
    multi_domains = [domain for domain in domains if domain['domain_family'] == 'multi_external_link_domain']
    assert len(multi_domains) == 1

    domain = multi_domains[0]
    assert domain['n_external_links'] == 2
    assert domain['has_residence'] is True

    links = [
        result['raw']['external_links'][link_id - 1]
        for link_id in domain['external_link_ids']
    ]
    assert len(links) == 2
    for link in links:
        assert len(link['face_ids']) == len(set(link['face_ids']))


def test_surface_dent_one_link_has_no_residence():
    coords = np.array(
        [
            [4.04, 0.31, -0.05],
            [5.43, 2.25, -0.22],
            [6.66, 6.89, 0.04],
            [4.22, 6.35, -0.75],
            [2.5, 1.92, 0.72],
            [5.11, 3.91, -0.46],
            [0.17, 2.44, -0.67],
            [0.06, 2.16, 0.17],
        ],
        dtype=float,
    )
    radii = np.array([1.7, 1.49, 1.85, 1.39, 1.4, 1.81, 1.57, 1.64], dtype=float)

    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    result = network.get_topography(probe_radius=1.4, min_size=0, transit_policy='with_connectors')

    dents = [
        domain
        for domain in result['raw']['concavity_domains']
        if domain['domain_family'] == 'surface_concavity_domain'
    ]
    assert len(dents) == 1

    dent = dents[0]
    assert dent['n_external_links'] == 1
    assert dent['has_residence'] is False
    assert dent['n_resident_nodes'] == 0
    assert dent['n_transit_connector_nodes'] >= 1
    assert 'provisional' in dent['flags']


@pytest.mark.skip(
    reason="The nonresident_passage family (>=2 external links, no residence) is "
    "covered directly by the classifier unit test (_classify_domain(2, 0)) and the "
    "non-resident transit-connector machinery is exercised end-to-end by the "
    "surface_dent and degenerate toys. A stable two-mouth, fully non-resident "
    "fixture is hard to construct (the two openings tend to merge into one link "
    "or pick up residence); deferred until a deterministic construction is found."
)
def test_nonresident_passage_two_links_has_no_residence():
    raise NotImplementedError


@pytest.mark.skip(
    reason="The degenerate_subprobe family (0 external links, no residence) is "
    "covered directly by the classifier unit test (_classify_domain(0, 0)). A "
    "stable end-to-end fixture needs a fully buried non-resident transit cluster "
    "(no permeable hull face), which is hard to construct robustly and is fragile "
    "to mesh face/neighbor conventions; deferred like nonresident_passage."
)
def test_degenerate_subprobe_domain_has_no_links_and_no_residence():
    raise NotImplementedError


def test_min_size_filters_compatibility_views_not_raw_domains():
    coords = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )
    radii = np.full(4, 1.7, dtype=float)

    network = DelaunayFlowNetwork.from_arrays(coords, radii)
    result = network.get_topography(probe_radius=1.4, min_size=2)

    assert len(result['raw']['concavity_domains']) == 1
    assert result['raw']['concavity_domains'][0]['domain_family'] == 'void_domain'
    assert result['wet']['voids'] == []



def _dry_record_maps(result):
    tetrahedra = {
        record['tetrahedron_id']: record for record in result['raw']['tetrahedra']
    }
    faces = {
        (face['owner_tetrahedron_id'], face['face_index']): face
        for face in result['raw']['faces']
    }
    return tetrahedra, faces


def test_dry_components_cover_all_and_only_non_resident_tetrahedra():
    network = _two_tetrahedra_fixture()
    result = network.get_topography(probe_radius=10.0, min_size=0)
    tetrahedra, _faces = _dry_record_maps(result)

    dry_nodes = {
        tetrahedron_id
        for tetrahedron_id, record in tetrahedra.items()
        if record['residence_state'] == 'non_resident'
    }
    component_nodes = {
        tetrahedron_id
        for component in result['dry']['components']
        for tetrahedron_id in component['tetrahedron_indices']
    }

    assert dry_nodes
    assert component_nodes == dry_nodes
    assert result['dry']['core'] == result['dry']['components'][0]
    assert result['dry']['islands'] == result['dry']['components'][1:]


def test_dry_component_edges_use_only_non_permeable_shared_faces():
    network = _two_tetrahedra_fixture()
    result = network.get_topography(probe_radius=10.0, min_size=0)
    tetrahedra, faces = _dry_record_maps(result)

    for component in result['dry']['components']:
        assert component['size'] == len(component['tetrahedron_indices'])
        assert component['dry_edge_face_ids']
        for tetrahedron_id in component['tetrahedron_indices']:
            assert tetrahedra[tetrahedron_id]['residence_state'] == 'non_resident'

        component_node_set = set(component['tetrahedron_indices'])
        for edge in component['dry_edges']:
            left = edge['source_tetrahedron_id']
            right = edge['target_tetrahedron_id']
            face = faces[(left, edge['source_face_index'])]
            opposite_face = faces[(right, edge['target_face_index'])]
            assert left in component_node_set
            assert right in component_node_set
            assert face['face_id'] == edge['face_id']
            assert opposite_face['face_id'] == edge['face_id']
            assert face['permeability_state'] == 'non_permeable'
            assert opposite_face['permeability_state'] == 'non_permeable'


def test_permeable_shared_faces_do_not_create_dry_edges():
    coords = np.array(
        [
            [6.37, 5.23, 3.3],
            [7.54, 4.73, 0.47],
            [6.4, 2.32, 6.95],
            [5.75, 5.24, 0.32],
            [7.79, 0.99, 7.09],
            [4.14, 4.77, 2.65],
            [7.4, 3.38, 6.36],
            [2.18, 5.87, 0.84],
            [2.64, 3.03, 7.53],
        ],
        dtype=float,
    )
    radii = np.array(
        [1.58, 1.42, 1.61, 1.92, 1.09, 1.86, 1.77, 1.63, 1.63],
        dtype=float,
    )
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    result = network.get_topography(probe_radius=1.4, min_size=0)
    tetrahedra, faces = _dry_record_maps(result)

    for component in result['dry']['components']:
        component_node_set = set(component['tetrahedron_indices'])
        for left in component_node_set:
            for face_index, neighbor in enumerate(network.simplex_neighbors[left]):
                neighbor = int(neighbor)
                if neighbor not in component_node_set or left >= neighbor:
                    continue
                face = faces[(left, face_index)]
                assert face['permeability_state'] == 'non_permeable'

    permeable_dry_pairs = []
    for left in range(network.n_tetrahedra):
        if tetrahedra[left]['residence_state'] != 'non_resident':
            continue
        for face_index, neighbor in enumerate(network.simplex_neighbors[left]):
            neighbor = int(neighbor)
            if neighbor == -1 or left >= neighbor:
                continue
            if tetrahedra[neighbor]['residence_state'] != 'non_resident':
                continue
            face = faces[(left, face_index)]
            if face['permeability_state'] == 'permeable':
                permeable_dry_pairs.append((left, neighbor))
    assert permeable_dry_pairs

    component_by_node = {}
    for component in result['dry']['components']:
        for node in component['tetrahedron_indices']:
            component_by_node[node] = component['id']
    assert all(
        component_by_node[left] != component_by_node[right]
        for left, right in permeable_dry_pairs
    )



def test_dry_interfaces_reference_existing_components_and_faces():
    network = _two_tetrahedra_fixture()
    result = network.get_topography(probe_radius=10.0, min_size=0)
    component_ids = {component['id'] for component in result['dry']['components']}
    face_ids = {face['face_id'] for face in result['raw']['faces']}

    assert result['dry']['interfaces'] == result['raw']['dry_interfaces']
    assert result['dry']['interfaces']
    for interface in result['dry']['interfaces']:
        assert interface['dry_component_id'] in component_ids
        assert interface['face_id'] in face_ids
        assert interface['permeability_state'] in {'permeable', 'non_permeable'}
        assert interface['interface_kind'] in {
            'hull_permeable',
            'hull_blocked',
            'dry_permeable_contact',
            'transit_contact',
            'resident_wall',
        }


def test_dry_depth_is_zero_on_boundary_nodes_and_consistent_with_dry_edges():
    network = _two_tetrahedra_fixture()
    result = network.get_topography(probe_radius=10.0, min_size=0)

    for component in result['dry']['components']:
        depths = component['dry_depth_by_tetrahedron']
        boundary_nodes = set(component['dry_boundary_tetrahedron_ids'])
        assert component['dry_interface_ids']
        assert boundary_nodes
        assert all(depths[node] == 0 for node in boundary_nodes)
        finite_depths = [depth for depth in depths.values() if depth is not None]
        assert component['dry_depth_min'] == min(finite_depths)
        assert component['dry_depth_max'] == max(finite_depths)
        assert component['dry_depth_mean'] == pytest.approx(float(np.mean(finite_depths)))

        for edge in component['dry_edges']:
            left = edge['source_tetrahedron_id']
            right = edge['target_tetrahedron_id']
            assert abs(depths[left] - depths[right]) <= 1


def test_singleton_dry_component_with_interface_has_depth_zero():
    coords = np.array(
        [
            [1.874, 1.874, 1.874],
            [1.874, -1.874, -1.874],
            [-1.874, 1.874, -1.874],
            [-1.874, -1.874, 1.874],
        ],
        dtype=float,
    )
    radii = np.full(4, 1.7, dtype=float)
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    result = network.get_topography(probe_radius=2.0, min_size=0)

    singletons = [
        component for component in result['dry']['components'] if component['size'] == 1
    ]
    assert len(singletons) == 1
    component = singletons[0]
    assert component['dry_interface_ids']
    assert list(component['dry_depth_by_tetrahedron'].values()) == [0]
    assert component['dry_depth_min'] == 0
    assert component['dry_depth_max'] == 0
    assert component['dry_depth_mean'] == 0.0

def test_dry_motifs_reference_existing_components_interfaces_and_dry_nodes():
    network = _network_from_random_points(seed=4, n_atoms=20)
    result = network.get_topography(probe_radius=1.4, min_size=0)

    components = result['dry']['components']
    component_ids = {component['id'] for component in components}
    dry_nodes = {
        node for component in components for node in component['tetrahedron_indices']
    }
    interface_ids = {
        interface['dry_interface_id'] for interface in result['dry']['interfaces']
    }

    assert result['dry']['motifs'] == result['raw']['dry_motifs']
    assert result['dry']['motifs']
    for motif in result['dry']['motifs']:
        assert motif['dry_component_id'] in component_ids
        assert set(motif['tetrahedron_ids']) <= dry_nodes
        assert set(motif['dry_interface_ids']) <= interface_ids
        assert 'candidate' in motif['flags']


def test_dry_core_candidate_uses_component_maximum_dry_depth():
    network = _network_from_random_points(seed=5, n_atoms=24)
    result = network.get_topography(probe_radius=1.4, min_size=0)

    components = {component['id']: component for component in result['dry']['components']}
    core_motifs = [
        motif
        for motif in result['dry']['motifs']
        if motif['motif_type'] == 'dry_core_candidate'
    ]
    for motif in core_motifs:
        component = components[motif['dry_component_id']]
        assert motif['dry_depth'] == component['dry_depth_max']
        for tetrahedron_id in motif['tetrahedron_ids']:
            assert component['dry_depth_by_tetrahedron'][tetrahedron_id] == motif['dry_depth']


def test_gate_intrusion_suspect_is_flagged_and_can_block_face():
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [5.5, 0.0, 0.0],
            [2.75, 4.7, 0.0],
            [2.75, 1.6, 0.4],
        ],
        dtype=float,
    )
    radii = np.array([1.4, 1.4, 1.4, 1.8], dtype=float)

    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-8)
    flagged = network.get_topography(
        probe_radius=1.0,
        gate_intrusion_policy='flag_only',
        min_size=0,
    )
    blocked = network.get_topography(
        probe_radius=1.0,
        gate_intrusion_policy='block_suspect',
        min_size=0,
    )

    flagged_faces = [
        face
        for face in flagged['raw']['faces']
        if 'intrusion_suspect' in face['flags']
    ]
    blocked_faces = [
        face
        for face in blocked['raw']['faces']
        if 'blocked_by_intrusion_policy' in face['flags']
    ]

    assert flagged_faces
    assert blocked_faces
    assert any(face['permeability_state'] == 'permeable' for face in flagged_faces)
    assert all(face['permeability_state'] == 'non_permeable' for face in blocked_faces)
