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
    """Return whether a face belongs to the alpha=0 base complex.

    For non-attached faces (rho > 0): in complex iff rho_rank <= base_rank,
    matching ``alf_is_in_complex(f, base_rank)`` from the C reference.

    For attached faces (rho = 0): the C code would also say "in complex"
    (0 <= base_rank always), but in the Python triangulation (no infinity
    vertex) this would incorrectly block empty-tetrahedra pairs that share an
    attached face but are both outside the alpha complex.  The mu1 proxy --
    "face is in complex iff at least one adjacent tet is in the base complex"
    -- recovers the right connectivity for the cases that matter for void
    detection.

    Note: callers that handle hull faces (neighbor == -1) must check for hull
    membership *before* calling this function.
    """

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
    """Compute tetrahedron depths following the wrapping-depth recursion (MKALF compute_tetra_depth2).

    Finds the MINIMUM-rho sink reachable through hidden-triangle links.  A
    hull-attached face only sets depth to infinity when no interior hidden
    neighbour has been found yet; a finite hidden neighbour always overrides
    the hull-attached infinity.  This matches ``do_wrap=1`` in MKALF
    ``alf_init_pockets`` and is required to reproduce CASTp server parity.
    """

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
        # min_ix == -1 means "no sink found yet" → tet is its own sink at end
        min_ix = -1
        min_rho = infinity_rank + 2  # sentinel: larger than any real rank

        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if geometry.face_is_on_hull[simplex_index, face_index]:
                # Hull-attached face: tentatively set depth to infinity, but
                # only if we have not yet found an interior hidden neighbour.
                if _triangle_is_attached(geometry, simplex_index, face_index) and min_ix == -1:
                    min_ix = infinity_marker
                    min_rho = infinity_rank + 1
                continue

            if neighbor == -1:
                continue
            if not _hidden_triangle(geometry, simplex_index, face_index, int(neighbor)):
                continue

            neighbor_depth = compute(int(neighbor))
            new_rho = (
                infinity_rank + 1
                if neighbor_depth == infinity_marker
                else int(geometry.simplex_rho_ranks[int(neighbor_depth)])
            )
            # Take the minimum-rho path; a finite interior neighbour overrides
            # any previously recorded hull-attached infinity.
            if new_rho < min_rho:
                min_rho = new_rho
                min_ix = neighbor_depth

        visiting[simplex_index] = False
        depth[simplex_index] = simplex_index if min_ix == -1 else int(min_ix)
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


def _triangle_in_complex_at(geometry, simplex_index: int, face_index: int, rank: int) -> bool:
    """Return whether a face is in the alpha complex at the given rank.

    For non-attached faces (rho > 0): in complex iff rho_rank <= rank,
    matching ``alf_is_in_complex(ALF_TRIANGLE, rank, face)`` from the C reference.

    For attached faces (rho = 0): the C code says always in complex (0 <= any
    rank).  However, in the scipy triangulation (no infinity vertex), applying
    that rule literally would prevent empty-tet pairs that share an attached face
    from being connected, shattering components that should be joined.  The mu1
    proxy — "face is in complex iff at least one adjacent tet is in the base
    complex" — recovers the right connectivity.  This proxy is consistent with
    ``_base_triangle_in_complex`` used for voids.
    """

    face_rho_rank = int(geometry.face_rho_ranks[int(simplex_index), int(face_index)])
    if face_rho_rank != 0:
        return bool(face_rho_rank <= rank)
    return bool(int(geometry.face_mu1_ranks[int(simplex_index), int(face_index)]) <= rank)


def _build_rank_driven_components(
    geometry,
    empty_mask: np.ndarray,
    size_limit_rank: int,
    rank1: int | None = None,
) -> tuple[dict[int, list[int]], set[int], np.ndarray]:
    """Build pockets using the original depth-and-delay construction.

    ``rank1`` is the lower alpha-rank threshold — equivalent to the ``rank1``
    parameter in ``alf_init_pockets(rank1, rank2, do_wrap)``.  Only tetrahedra
    with rho_rank in (rank1, size_limit_rank] are considered pocket candidates,
    and face connectivity is tested against ``rank1`` (faces not in the alpha
    complex at rank1 allow pocket-to-pocket union).

    For the classical CASTp pocket workflow, ``rank1`` should be the rank
    corresponding to probe_radius² (``_probe_rank``), not ``base_rank``.
    ``base_rank`` corresponds to alpha = 0 (molecular surface) and is correct
    for void detection but too permissive for pockets: it would include
    tetrahedra smaller than the probe sphere.
    """

    if rank1 is None:
        rank1 = geometry.base_rank

    mesh = geometry.mesh
    exterior = -1  # sentinel for the exterior component; -1 is always the smallest root so it wins in union
    simplex_indices = np.where(empty_mask)[0]
    if simplex_indices.size == 0:
        return {}, set(), np.full(mesh.n_simplices, -1, dtype=int)

    depth = _compute_pocket_depths(geometry, empty_mask)
    infinity_marker = mesh.n_simplices
    delayed_by_sink: dict[int, list[int]] = defaultdict(list)
    parents: dict[int, int] = {exterior: exterior}

    retained_simplex_indices = set()
    outside_simplex_indices = set()
    sorted_simplex_indices = sorted(
        (
            int(index)
            for index in simplex_indices
            if int(rank1) < int(geometry.simplex_rho_ranks[int(index)]) <= int(size_limit_rank)
        ),
        key=lambda index: (int(geometry.simplex_rho_ranks[index]), index),
    )

    def handle_tetrahedron(simplex_index: int) -> None:
        simplex_index = int(simplex_index)
        _union_find_add(parents, simplex_index)
        retained_simplex_indices.add(simplex_index)

        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if _triangle_in_complex_at(geometry, simplex_index, face_index, int(rank1)):
                continue
            if neighbor == -1:
                continue
            neighbor = int(neighbor)
            if neighbor in parents and _union_find_root(parents, neighbor) != exterior:
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
            _union_find_union(parents, simplex_index, exterior)
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
            _union_find_union(parents, simplex_index, exterior)
            outside_simplex_indices.add(simplex_index)

    components: dict[int, list[int]] = defaultdict(list)
    blocked_nodes = set(outside_simplex_indices)
    for simplex_index in retained_simplex_indices:
        root = _union_find_root(parents, simplex_index)
        if root == exterior:
            blocked_nodes.add(simplex_index)
            continue
        components[int(root)].append(int(simplex_index))

    ordered_components = {
        component_index: sorted(simplex_group)
        for component_index, simplex_group in components.items()
        if simplex_group
    }
    return ordered_components, blocked_nodes, depth


def _build_void_components(
    geometry,
    empty_mask: np.ndarray,
) -> tuple[dict[int, list[int]], set[int]]:
    """Build voids as complement components, following ``alf_find_voids``."""

    mesh = geometry.mesh
    exterior = -1  # sentinel for the exterior component; -1 is always the smallest root so it wins in union
    simplex_indices = np.where(empty_mask)[0]
    if simplex_indices.size == 0:
        return {}, {exterior}

    parents: dict[int, int] = {exterior: exterior}
    simplex_index_set = {int(index) for index in simplex_indices}

    for simplex_index in simplex_indices:
        simplex_index = int(simplex_index)
        _union_find_add(parents, simplex_index)

    for simplex_index in simplex_indices:
        simplex_index = int(simplex_index)
        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            # Hull faces always connect to the exterior.  In the C MKALF
            # triangulation these correspond to faces adjacent to the infinite
            # tetrahedron (always outside the complex).  Check hull membership
            # first so that attached hull faces are not mistakenly blocked.
            if neighbor == -1:
                _union_find_union(parents, simplex_index, exterior)
                continue

            if _base_triangle_in_complex(geometry, simplex_index, face_index):
                continue

            neighbor = int(neighbor)
            if neighbor in simplex_index_set:
                _union_find_union(parents, simplex_index, neighbor)
            else:
                _union_find_union(parents, simplex_index, exterior)

    components: dict[int, list[int]] = defaultdict(list)
    blocked_nodes = {exterior}
    for simplex_index in simplex_indices:
        root = _union_find_root(parents, int(simplex_index))
        if root == exterior:
            blocked_nodes.add(int(simplex_index))
            continue
        components[int(root)].append(int(simplex_index))

    ordered_components = {
        component_index: sorted(simplex_group)
        for component_index, simplex_group in components.items()
        if simplex_group
    }
    return ordered_components, blocked_nodes


def _component_boundary_faces(
    geometry,
    simplex_indices: list[int],
    blocked_nodes: set[int],
    depth: np.ndarray,
    size_limit_rank: int,
    rank1: int | None = None,
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int, int]], list[int]]:
    """Return component boundary faces and the subset that behaves as mouths.

    ``rank1`` is the lower alpha-rank threshold used to determine face
    complex membership (matching ``alf_init_pockets`` rank1).  For pockets
    this should be ``probe_rank``; defaults to ``geometry.base_rank``.

    ``size_limit_rank`` is the upper alpha-rank threshold (rank2 in the C
    code).  For CASTp pockets this is ``max_rank``; the condition
    ``depth_rank > size_limit_rank`` should therefore never trigger in
    normal operation.

    Returns a 3-tuple: ``(boundary_faces, mouth_faces, mouth_simplex_indices)``
    where ``mouth_simplex_indices[i]`` is the pocket-side simplex that owns
    ``mouth_faces[i]``.  These origins are required by the Fnext walk in
    ``cluster_mouth_faces``.
    """

    if rank1 is None:
        rank1 = geometry.base_rank

    mesh = geometry.mesh
    boundary_faces = []
    mouth_faces = []
    mouth_simplex_indices = []
    simplex_index_set = set(int(index) for index in simplex_indices)
    infinity_marker = mesh.n_simplices

    for simplex_index in simplex_indices:
        simplex_index = int(simplex_index)
        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if _triangle_in_complex_at(geometry, simplex_index, face_index, int(rank1)):
                continue

            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            if neighbor != -1 and int(neighbor) in simplex_index_set:
                continue

            boundary_faces.append(face_atoms)
            if neighbor == -1:
                mouth_faces.append(face_atoms)
                mouth_simplex_indices.append(simplex_index)
                continue

            neighbor = int(neighbor)
            if neighbor in blocked_nodes:
                mouth_faces.append(face_atoms)
                mouth_simplex_indices.append(simplex_index)
                continue

            neighbor_depth = int(depth[neighbor])
            if neighbor_depth == infinity_marker:
                mouth_faces.append(face_atoms)
                mouth_simplex_indices.append(simplex_index)
                continue
            if neighbor_depth >= 0 and int(geometry.simplex_rho_ranks[neighbor_depth]) > int(size_limit_rank):
                mouth_faces.append(face_atoms)
                mouth_simplex_indices.append(simplex_index)

    return boundary_faces, mouth_faces, mouth_simplex_indices


def _component_boundary_faces_void(
    geometry,
    simplex_indices: list[int],
) -> list[tuple[int, int, int]]:
    """Return complement-boundary faces for a void component."""

    mesh = geometry.mesh
    boundary_faces = []
    simplex_index_set = set(int(index) for index in simplex_indices)

    for simplex_index in simplex_indices:
        simplex_index = int(simplex_index)
        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if _base_triangle_in_complex(geometry, simplex_index, face_index):
                continue

            if neighbor != -1 and int(neighbor) in simplex_index_set:
                continue

            boundary_faces.append(mesh.get_face_atoms(simplex_index, face_index))

    return boundary_faces


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
    void_components, _void_blocked_nodes = _build_void_components(
        geometry,
        open_mask,
    )
    components, blocked_nodes, depth = _build_rank_driven_components(
        geometry,
        open_mask,
        size_limit_rank,
        rank1=geometry.base_rank,
    )

    feature_records = []
    counters = {'pocket': 0, 'channel': 0, 'void': 0}

    for simplex_indices in sorted(void_components.values(), key=len, reverse=True):
        boundary_faces = _component_boundary_faces_void(
            geometry,
            simplex_indices,
        )
        boundary_atom_indices = _map_local_atom_indices(
            geometry.atom_indices_map,
            {int(atom_index) for face in boundary_faces for atom_index in face},
        )
        volume = component_volume(mesh.simplex_volumes, simplex_indices)
        counters['void'] += 1
        feature_records.append(
            {
                'id': counters['void'],
                'feature_type': 'void',
                'type': 'Void',
                'source': 'castp',
                'source_id': f'castp:void:{counters["void"]}',
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
                'n_mouths': 0,
                'mouth_area': 0.0,
                'mouths': [],
            }
        )

    for simplex_indices in sorted(components.values(), key=len, reverse=True):
        boundary_faces, mouth_faces, mouth_simplex_indices = _component_boundary_faces(
            geometry,
            simplex_indices,
            blocked_nodes,
            depth,
            size_limit_rank,
            rank1=geometry.base_rank,
        )
        mouth_clusters = cluster_mouth_faces(
            mouth_faces,
            geometry.edge_rho_ranks,
            geometry.base_rank,
            face_simplex_indices=mouth_simplex_indices,
            mesh=mesh,
            depth=depth,
            infinity_marker=mesh.n_simplices,
        )
        n_mouths = len(mouth_clusters)

        if n_mouths == 0:
            continue
        if n_mouths == 1:
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
