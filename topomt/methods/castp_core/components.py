"""Component assembly for the native CASTp implementation."""

from collections import defaultdict

import numpy as np

from .geometry import _weighted_hidden2
from .metrics import component_center, component_volume, mouth_area
from .mouths import cluster_mouth_faces


def _build_empty_simplex_mask(geometry, probe_radius: float) -> np.ndarray:
    """Select tetrahedra outside the weighted alpha complex of the base union."""

    del probe_radius

    return np.asarray(geometry.simplex_rho_ranks > geometry.base_rank, dtype=bool)


def _probe_rank(geometry, probe_radius: float) -> int:
    """Return the MKALF-like rank corresponding to the probe threshold."""

    probe_value = float(probe_radius) * float(probe_radius)
    spectrum_values = np.asarray(geometry.spectrum_values, dtype=float)

    if spectrum_values.size == 0:
        return 1
    if probe_value <= float(spectrum_values[0]):
        return 1
    if probe_value >= float(spectrum_values[-1]):
        return int(spectrum_values.size)
    return int(np.searchsorted(spectrum_values, probe_value, side='right'))


def _base_triangle_in_complex(geometry, simplex_index: int, face_index: int) -> bool:
    """Return whether a face belongs to the alpha=0 base complex."""

    simplex_index = int(simplex_index)
    face_index = int(face_index)
    face_rho_rank = int(geometry.face_rho_ranks[simplex_index, face_index])
    if face_rho_rank != 0:
        return bool(face_rho_rank <= geometry.base_rank)
    return bool(int(geometry.face_mu1_ranks[simplex_index, face_index]) <= geometry.base_rank)


def _triangle_is_attached(geometry, simplex_index: int, face_index: int) -> bool:
    """Return whether a triangle is attached in the MKALF sense."""

    return bool(int(geometry.face_rho_ranks[int(simplex_index), int(face_index)]) == 0)


def _hidden_triangle(geometry, simplex_index: int, face_index: int, neighbor_index: int) -> bool:
    """Return whether the face is hidden by the neighbor, following CAST logic."""

    simplex_index = int(simplex_index)
    face_index = int(face_index)
    neighbor_index = int(neighbor_index)

    face_mu1_rank = int(geometry.face_mu1_ranks[simplex_index, face_index])
    face_rho_rank = int(geometry.face_rho_ranks[simplex_index, face_index])
    simplex_rho_rank = int(geometry.simplex_rho_ranks[simplex_index])
    neighbor_rho_rank = int(geometry.simplex_rho_ranks[neighbor_index])

    if face_rho_rank != 0:
        return False
    if face_mu1_rank < simplex_rho_rank:
        return False
    if face_mu1_rank < neighbor_rho_rank:
        return True

    face_atom_indices = geometry.mesh.get_face_atoms(simplex_index, face_index)
    face_atom_indices_array = np.asarray(face_atom_indices, dtype=int)
    face_points = geometry.atom_coordinates[face_atom_indices_array]
    face_weights = geometry.mesh.weights[face_atom_indices_array]
    neighbor_atom_indices = geometry.mesh.simplex_atom_indices[neighbor_index]
    opposite_atom_index = next(
        int(atom_index)
        for atom_index in neighbor_atom_indices
        if int(atom_index) not in face_atom_indices
    )
    opposite_point = geometry.atom_coordinates[opposite_atom_index]
    opposite_hidden = _weighted_hidden2(
        face_points,
        face_weights,
        opposite_point,
        float(geometry.mesh.weights[opposite_atom_index]),
    )
    return bool(opposite_hidden == 1)


def _compute_pocket_depths(geometry, empty_mask: np.ndarray | None = None) -> np.ndarray:
    """Compute tetrahedron depths following the original pocket-depth recursion."""

    mesh = geometry.mesh
    n_simplices = mesh.n_simplices
    infinity_marker = n_simplices
    infinity_rank = int(np.max(geometry.simplex_rho_ranks)) + 1
    depth = np.full(n_simplices, -1, dtype=int)
    visiting = np.zeros(n_simplices, dtype=bool)

    def compute(simplex_index: int) -> int:
        simplex_index = int(simplex_index)
        if depth[simplex_index] != -1:
            return int(depth[simplex_index])
        if visiting[simplex_index]:
            return simplex_index

        visiting[simplex_index] = True
        max_depth_index = simplex_index
        max_rho_rank = int(geometry.simplex_rho_ranks[simplex_index])

        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if geometry.face_is_on_hull[simplex_index, face_index]:
                if _triangle_is_attached(geometry, simplex_index, face_index):
                    max_depth_index = infinity_marker
                    max_rho_rank = infinity_rank
                continue

            if neighbor == -1:
                continue
            if not _hidden_triangle(geometry, simplex_index, face_index, int(neighbor)):
                continue

            neighbor_depth = compute(int(neighbor))
            new_rho_rank = (
                infinity_rank
                if neighbor_depth == infinity_marker
                else int(geometry.simplex_rho_ranks[int(neighbor_depth)])
            )
            if new_rho_rank >= max_rho_rank:
                max_rho_rank = new_rho_rank
                max_depth_index = neighbor_depth

        visiting[simplex_index] = False
        depth[simplex_index] = int(max_depth_index)
        return int(depth[simplex_index])

    del empty_mask

    simplex_indices = np.arange(mesh.n_simplices, dtype=int)
    sort_order = np.argsort(-geometry.simplex_rho_ranks[simplex_indices], kind='stable')
    for simplex_index in simplex_indices[sort_order]:
        if depth[int(simplex_index)] == -1:
            compute(int(simplex_index))

    return depth


def _union_find_root(parents: dict[int, int], node: int) -> int:
    """Return the representative of a node in a union-find dictionary."""

    node = int(node)
    parent = parents.get(node, node)
    if parent != node:
        parents[node] = _union_find_root(parents, parent)
        return parents[node]
    parents[node] = node
    return node


def _union_find_add(parents: dict[int, int], node: int) -> None:
    """Add a node to a union-find dictionary."""

    node = int(node)
    parents.setdefault(node, node)


def _union_find_union(parents: dict[int, int], left: int, right: int) -> int:
    """Union two nodes in a union-find dictionary."""

    left_root = _union_find_root(parents, left)
    right_root = _union_find_root(parents, right)
    if left_root == right_root:
        return left_root

    if left_root > right_root:
        left_root, right_root = right_root, left_root
    parents[right_root] = left_root
    return left_root


def _build_rank_driven_components(
    geometry,
    empty_mask: np.ndarray,
    size_limit_rank: int,
) -> tuple[dict[int, list[int]], set[int], np.ndarray]:
    """Build pockets using the original depth-and-delay construction."""

    mesh = geometry.mesh
    simplex_indices = np.where(empty_mask)[0]
    if simplex_indices.size == 0:
        return {}, set(), np.full(mesh.n_simplices, -1, dtype=int)

    depth = _compute_pocket_depths(geometry, empty_mask)
    infinity_marker = mesh.n_simplices
    delayed_by_sink: dict[int, list[int]] = defaultdict(list)
    parents: dict[int, int] = {0: 0}

    retained_simplex_indices = set()
    outside_simplex_indices = set()
    sorted_simplex_indices = sorted(
        (
            int(index)
            for index in simplex_indices
            if geometry.base_rank < int(geometry.simplex_rho_ranks[int(index)]) <= int(size_limit_rank)
        ),
        key=lambda index: (int(geometry.simplex_rho_ranks[index]), index),
    )

    def handle_tetrahedron(simplex_index: int) -> None:
        simplex_index = int(simplex_index)
        _union_find_add(parents, simplex_index)
        retained_simplex_indices.add(simplex_index)

        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if _base_triangle_in_complex(geometry, simplex_index, face_index):
                continue
            if neighbor == -1:
                continue
            neighbor = int(neighbor)
            if neighbor in parents and _union_find_root(parents, neighbor) != 0:
                _union_find_union(parents, simplex_index, neighbor)

    for simplex_index in sorted_simplex_indices:
        depth_index = int(depth[simplex_index])
        simplex_rho_rank = int(geometry.simplex_rho_ranks[simplex_index])

        if depth_index == simplex_index:
            if simplex_index in delayed_by_sink:
                for delayed_simplex_index in delayed_by_sink.pop(simplex_index):
                    handle_tetrahedron(delayed_simplex_index)
            handle_tetrahedron(simplex_index)
            continue

        if depth_index == infinity_marker:
            _union_find_add(parents, simplex_index)
            _union_find_union(parents, simplex_index, 0)
            outside_simplex_indices.add(simplex_index)
            continue

        depth_rho_rank = int(geometry.simplex_rho_ranks[depth_index])
        if depth_rho_rank <= int(size_limit_rank):
            if depth_rho_rank == simplex_rho_rank:
                handle_tetrahedron(simplex_index)
            else:
                delayed_by_sink[depth_index].append(simplex_index)
        else:
            _union_find_add(parents, simplex_index)
            _union_find_union(parents, simplex_index, 0)
            outside_simplex_indices.add(simplex_index)

    components: dict[int, list[int]] = defaultdict(list)
    blocked_nodes = set(outside_simplex_indices)
    for simplex_index in retained_simplex_indices:
        root = _union_find_root(parents, simplex_index)
        if root == 0:
            blocked_nodes.add(simplex_index)
            continue
        components[int(root)].append(int(simplex_index))

    ordered_components = {
        component_index: sorted(simplex_group)
        for component_index, simplex_group in components.items()
        if simplex_group
    }
    return ordered_components, blocked_nodes, depth


def _component_boundary_faces(
    geometry,
    simplex_indices: list[int],
    blocked_nodes: set[int],
    depth: np.ndarray,
    size_limit_rank: int,
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]]:
    """Return component boundary faces and the subset that behaves as mouths."""

    mesh = geometry.mesh
    boundary_faces = []
    mouth_faces = []
    simplex_index_set = set(int(index) for index in simplex_indices)
    infinity_marker = mesh.n_simplices

    for simplex_index in simplex_indices:
        simplex_index = int(simplex_index)
        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if _base_triangle_in_complex(geometry, simplex_index, face_index):
                continue

            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            if neighbor != -1 and int(neighbor) in simplex_index_set:
                continue

            boundary_faces.append(face_atoms)
            if neighbor == -1:
                mouth_faces.append(face_atoms)
                continue

            neighbor = int(neighbor)
            if neighbor in blocked_nodes:
                mouth_faces.append(face_atoms)
                continue

            neighbor_depth = int(depth[neighbor])
            if neighbor_depth == infinity_marker:
                mouth_faces.append(face_atoms)
                continue
            if neighbor_depth >= 0 and int(geometry.simplex_rho_ranks[neighbor_depth]) > int(size_limit_rank):
                mouth_faces.append(face_atoms)

    return boundary_faces, mouth_faces


def _map_local_atom_indices(atom_indices_map: np.ndarray, local_atom_indices: set[int]) -> list[int]:
    """Map component-local atom indices back to global atom indices."""

    return sorted(int(atom_indices_map[index]) for index in sorted(local_atom_indices))


def _component_atom_indices(mesh, atom_indices_map: np.ndarray, simplex_indices: list[int]) -> list[int]:
    """Return the current component atom set from its tetrahedra."""

    local_atom_indices = {
        int(atom_index)
        for simplex_index in simplex_indices
        for atom_index in mesh.simplex_atom_indices[int(simplex_index)]
    }
    return _map_local_atom_indices(atom_indices_map, local_atom_indices)


def build_castp_feature_records(
    geometry,
    probe_radius: float,
) -> list[dict]:
    """Build CASTp-like feature records from the weighted tetrahedral substrate."""

    mesh = geometry.mesh
    open_mask = _build_empty_simplex_mask(geometry, probe_radius=probe_radius)
    probe_rank = _probe_rank(geometry, probe_radius)
    size_limit_rank = int(geometry.spectrum_values.size)
    components, blocked_nodes, depth = _build_rank_driven_components(
        geometry,
        open_mask,
        size_limit_rank,
    )

    feature_records = []
    counters = {'pocket': 0, 'channel': 0, 'void': 0}

    for simplex_indices in sorted(components.values(), key=len, reverse=True):
        boundary_faces, mouth_faces = _component_boundary_faces(
            geometry,
            simplex_indices,
            blocked_nodes,
            depth,
            probe_rank,
        )
        mouth_clusters = cluster_mouth_faces(mouth_faces)
        n_mouths = len(mouth_clusters)

        if n_mouths == 0:
            feature_type = 'void'
        elif n_mouths == 1:
            feature_type = 'pocket'
        else:
            feature_type = 'channel'

        counters[feature_type] += 1
        mouths = []
        total_mouth_area = 0.0
        for mouth_index, cluster_faces in enumerate(mouth_clusters, start=1):
            mouth_atom_indices_local = sorted({atom for face in cluster_faces for atom in face})
            mouth_atom_indices = [
                int(geometry.atom_indices_map[atom_index]) for atom_index in mouth_atom_indices_local
            ]
            area = mouth_area(geometry.atom_coordinates, cluster_faces)
            total_mouth_area += area
            mouths.append(
                {
                    'id': mouth_index,
                    'atom_indices': sorted(mouth_atom_indices),
                    'area': area,
                    'faces': list(cluster_faces),
                }
            )

        boundary_atom_indices = _map_local_atom_indices(
            geometry.atom_indices_map,
            {int(atom_index) for face in boundary_faces for atom_index in face},
        )
        volume = component_volume(mesh.simplex_volumes, simplex_indices)
        feature_records.append(
            {
                'id': counters[feature_type],
                'feature_type': feature_type,
                'type': feature_type.capitalize(),
                'source': 'castp',
                'source_id': f'castp:{feature_type}:{counters[feature_type]}',
                'tetrahedron_indices': list(simplex_indices),
                'atom_indices': _component_atom_indices(
                    mesh,
                    geometry.atom_indices_map,
                    simplex_indices,
                ),
                'boundary_atom_indices': list(boundary_atom_indices),
                'component_atom_indices': _component_atom_indices(
                    mesh,
                    geometry.atom_indices_map,
                    simplex_indices,
                ),
                'center': component_center(mesh.simplex_centers, simplex_indices),
                'volume': volume,
                'score': volume,
                'n_mouths': n_mouths,
                'mouth_area': total_mouth_area,
                'mouths': mouths,
            }
        )

    feature_records.sort(key=lambda record: record['volume'], reverse=True)
    return feature_records
