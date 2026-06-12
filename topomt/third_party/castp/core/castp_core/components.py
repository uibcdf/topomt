"""Component assembly for the native CASTp implementation."""

from collections import defaultdict

import numpy as np

from .geometry import (
    ALF_RHO,
    ALF_TETRA,
    ALF_TRIANGLE,
    _edge_is_in_complex_at,
    _exact_threshold_ratio,
    _face_is_in_complex_at,
    _rank_of_ratio,
    _rank_table_is_interior,
    _vertex_is_in_complex_at,
    _vertex_is_interior_at as _geometry_vertex_is_interior_at,
    _weighted_hidden2,
)
from .metrics import (
    component_area,
    component_center,
    component_volume,
    mouth_area,
    mouth_perimeter,
)
from .mouths import MouthFaceRecord, cluster_mouth_faces

ALF_POC_RANK = 0
ALF_POC_TETRA = 1
ALF_POC_BURIED = 2
ALF_POC_UNION_SAME = 3
ALF_POC_UNION_TWO = 4
ALF_POC_MOUTH = 5


def _face_atom_map_by_triangle_index(geometry) -> dict[int, tuple[int, int, int]]:
    """Return local atom triples keyed by historical triangle index."""

    mesh = geometry.mesh
    face_atom_map = {}
    for simplex_index in range(mesh.n_simplices):
        for face_index in range(4):
            if not hasattr(mesh, 'get_face_index'):
                triangle_index = int(face_index)
            else:
                triangle_index = int(mesh.get_face_index(simplex_index, face_index))
            face_atom_map.setdefault(
                triangle_index,
                tuple(
                    int(atom_index)
                    for atom_index in mesh.get_face_atoms(simplex_index, face_index)
                ),
            )
    return face_atom_map


def _face_owner_map_by_triangle_index(geometry) -> dict[int, tuple[int, int]]:
    """Return canonical owner tetrahedra keyed by historical triangle index."""

    mesh = geometry.mesh
    face_owner_map = {}
    for simplex_index in range(mesh.n_simplices):
        for face_index in range(4):
            if not hasattr(mesh, 'get_face_index'):
                triangle_index = int(face_index)
            else:
                triangle_index = int(mesh.get_face_index(simplex_index, face_index))
            face_owner_map.setdefault(
                triangle_index,
                _canonical_face_owner_indices(geometry, simplex_index, face_index),
            )
    return face_owner_map


def castp1_pocket_metric_signatures(
    geometry,
    alpha_rank: int,
    beta_rank: int,
) -> dict:
    """Return MKALF-style pocket metric signatures through `beta_rank`.

    This follows `sig/poc-metric.c`: tetra events add Euclidean tetrahedral
    volume, mouth events add triangle area, and union events subtract the same
    triangle area from the mouth signature.
    """

    face_atom_map = _face_atom_map_by_triangle_index(geometry)
    face_owner_map = _face_owner_map_by_triangle_index(geometry)
    current = {
        'num_pockets': 0,
        'num_tetra': 0,
        'num_buried_triangles': 0,
        'max_tetra': 0,
        'pocket_volume': 0.0,
        'buried_area': 0.0,
        'mouth_area': 0.0,
        'mouth_triangles': 0,
        'max_pocket_volume': 0.0,
    }
    metric_parents = {}
    metric_sizes = {}
    metric_volumes = {}
    by_rank = {}

    def triangle_area_for_event(triangle_index: int) -> float:
        return component_area(
            geometry.atom_coordinates,
            [face_atom_map[int(triangle_index)]],
        )

    current_rank = {'value': int(alpha_rank) + 1}

    def event_hook(index: int, event_type: int) -> None:
        index = int(index)
        event_type = int(event_type)
        if event_type == ALF_POC_TETRA:
            tetra_volume = float(geometry.mesh.simplex_volumes[index])
            _union_find_add(metric_parents, metric_sizes, index)
            metric_volumes[index] = tetra_volume
            current['num_pockets'] += 1
            current['num_tetra'] += 1
            current['max_tetra'] = max(int(current['max_tetra']), 1)
            current['pocket_volume'] += tetra_volume
            current['max_pocket_volume'] = max(
                float(current['max_pocket_volume']),
                tetra_volume,
            )
        elif event_type == ALF_POC_BURIED:
            current['num_buried_triangles'] += 1
            current['buried_area'] += triangle_area_for_event(index)
        elif event_type == ALF_POC_MOUTH:
            current['mouth_area'] += triangle_area_for_event(index)
            current['mouth_triangles'] += 1
        elif event_type in (ALF_POC_UNION_TWO, ALF_POC_UNION_SAME):
            current['mouth_area'] -= triangle_area_for_event(index)
            current['mouth_triangles'] -= 1
            if event_type == ALF_POC_UNION_TWO:
                owner_left, owner_right = face_owner_map[int(index)]
                if owner_left in metric_parents and owner_right in metric_parents:
                    root_left = _union_find_root(metric_parents, int(owner_left))
                    root_right = _union_find_root(metric_parents, int(owner_right))
                    if root_left != root_right:
                        current['num_pockets'] -= 1
                        merged_tetra = (
                            int(metric_sizes[root_left])
                            + int(metric_sizes[root_right])
                        )
                        merged_volume = (
                            float(metric_volumes.get(root_left, 0.0))
                            + float(metric_volumes.get(root_right, 0.0))
                        )
                        if int(metric_sizes[root_left]) >= int(metric_sizes[root_right]):
                            keep_root, drop_root = root_left, root_right
                        else:
                            keep_root, drop_root = root_right, root_left
                        metric_parents[drop_root] = keep_root
                        metric_sizes[keep_root] = merged_tetra
                        metric_volumes[keep_root] = merged_volume
                        metric_volumes[drop_root] = 0.0
                        current['max_tetra'] = max(
                            int(current['max_tetra']),
                            merged_tetra,
                        )
                        current['max_pocket_volume'] = max(
                            float(current['max_pocket_volume']),
                            merged_volume,
                        )
        elif event_type == ALF_POC_RANK:
            rank_values = dict(current)
            rank_values['mouth_area'] = max(float(rank_values['mouth_area']), 0.0)
            by_rank[int(current_rank['value'])] = rank_values
            current_rank['value'] += 1

    _build_rank_driven_components(
        geometry,
        size_limit_rank=int(beta_rank),
        rank1=int(alpha_rank),
        event_hook=event_hook,
    )

    return {
        'by_rank': by_rank,
        'final': by_rank.get(int(beta_rank), dict(current)),
    }


def _feature_record_type(feature_type: str) -> str:
    """Return the canonical record label for a CASTp feature type."""

    if feature_type == 'branched_channel':
        return 'BranchedChannel'
    return feature_type.capitalize()


def _feature_type_from_n_mouths(n_mouths: int) -> str:
    """Return the CAST-style feature type implied by the number of mouths."""

    n_mouths = int(n_mouths)
    if n_mouths == 0:
        return 'void'
    if n_mouths == 1:
        return 'pocket'
    if n_mouths == 2:
        return 'channel'
    return 'branched_channel'


def _build_empty_simplex_mask(geometry, probe_radius: float) -> np.ndarray:
    """Select tetrahedra outside the weighted alpha complex of the base union."""

    del probe_radius

    return np.asarray(geometry.simplex_rho_ranks > geometry.base_rank, dtype=bool)


def _geometry_max_rank(geometry) -> int:
    """Return MKALF's global `alfi->ranks` analogue for a geometry."""

    spectrum_ratios = getattr(geometry, 'spectrum_ratios', ())
    if spectrum_ratios:
        return int(len(spectrum_ratios) + 1)
    spectrum_values = getattr(geometry, 'spectrum_values', np.asarray([]))
    if np.asarray(spectrum_values).size:
        return int(np.asarray(spectrum_values).size + 1)
    if geometry.simplex_rho_ranks.size:
        return int(np.max(geometry.simplex_rho_ranks))
    return int(geometry.base_rank)


def _probe_rank(geometry, probe_radius: float) -> int:
    """Return the MKALF-like rank corresponding to the probe threshold."""

    if not hasattr(geometry, 'spectrum_ratios') or not hasattr(geometry, 'spectrum_decimals'):
        raise ValueError(
            'Canonical CASTp probe-rank evaluation requires exact '
            'spectrum_ratios and spectrum_decimals.'
        )

    return _rank_of_ratio(
        tuple(geometry.spectrum_ratios),
        _exact_threshold_ratio(float(probe_radius), int(geometry.spectrum_decimals)),
    )


def _base_triangle_in_complex(geometry, simplex_index: int, face_index: int) -> bool:
    """Return canonical base-complex membership for one triangle."""

    return _face_is_in_complex_at(geometry, simplex_index, face_index, int(geometry.base_rank))


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


def _compute_pocket_depths(geometry) -> np.ndarray:
    """Compute tetrahedron pocket depths following MKALF ``compute_tetra_depth``.

    The canonical non-wrapping pocket workflow used by
    ``render_pocket_new(..., FALSE)`` in the historical code selects the
    MAXIMUM-rho sink reachable through hidden-triangle links. A hull-attached
    face immediately sends the tetrahedron to infinity. This differs from the
    wrapping-depth path (`compute_tetra_depth2`), which uses the minimum-rho
    sink and only tentatively assigns infinity.
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
        max_ix = simplex_index
        max_rho = int(geometry.simplex_rho_ranks[simplex_index])

        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if geometry.face_is_on_hull[simplex_index, face_index]:
                if _triangle_is_attached(geometry, simplex_index, face_index):
                    max_ix = infinity_marker
                    max_rho = infinity_rank + 1
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
            if new_rho >= max_rho:
                max_rho = new_rho
                max_ix = neighbor_depth

        visiting[simplex_index] = False
        depth[simplex_index] = int(max_ix)
        return int(depth[simplex_index])

    for simplex_index in _iter_master_tetra_rho_indices(
        geometry,
        descending=True,
        rank_start=1,
        rank_end=int(np.max(geometry.simplex_rho_ranks)),
    ):
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


def _union_find_add(parents: dict[int, int], sizes: dict[int, int], node: int) -> None:
    """Add a node to a union-find dictionary."""

    node = int(node)
    if node not in parents:
        parents[node] = node
        sizes[node] = 1


def _union_find_union(
    parents: dict[int, int],
    sizes: dict[int, int],
    left: int,
    right: int,
    exterior: int,
) -> int:
    """Union two nodes using MKALF-like union-by-size semantics."""

    left_root = _union_find_root(parents, left)
    right_root = _union_find_root(parents, right)
    if left_root == right_root:
        return left_root

    if right_root == int(exterior):
        left_root, right_root = right_root, left_root
    elif left_root != int(exterior) and int(sizes.get(left_root, 1)) < int(sizes.get(right_root, 1)):
        left_root, right_root = right_root, left_root

    parents[right_root] = left_root
    sizes[left_root] = int(sizes.get(left_root, 1)) + int(sizes.get(right_root, 1))
    sizes.pop(right_root, None)
    return left_root


def _triangle_in_complex_at(geometry, simplex_index: int, face_index: int, rank: int) -> bool:
    """Return canonical triangle membership at the given alpha rank."""

    return _face_is_in_complex_at(geometry, simplex_index, face_index, int(rank))


def _canonical_face_owner_indices(geometry, simplex_index: int, face_index: int) -> tuple[int, int]:
    """Return the canonical owner pair for a triangle, analogous to `EdFacet(t, 0/1)`."""

    mesh = geometry.mesh
    if not hasattr(geometry, 'face_records'):
        if hasattr(mesh, 'get_face_owner_indices'):
            return tuple(int(owner) for owner in mesh.get_face_owner_indices(simplex_index, face_index))
        return (int(simplex_index), int(mesh.neighbors[int(simplex_index), int(face_index)]))

    face_atoms = mesh.get_face_atoms(int(simplex_index), int(face_index))
    for owner_simplex_index, owner_face_index, owner_face_atoms in geometry.face_records:
        if tuple(owner_face_atoms) != tuple(face_atoms):
            continue
        neighbor = int(mesh.neighbors[int(owner_simplex_index), int(owner_face_index)])
        return (
            int(owner_simplex_index),
            -1 if neighbor == -1 else neighbor,
        )

    if hasattr(mesh, 'get_face_owner_indices'):
        return tuple(int(owner) for owner in mesh.get_face_owner_indices(simplex_index, face_index))
    return (int(simplex_index), int(mesh.neighbors[int(simplex_index), int(face_index)]))


def _handle_tetra_seq(
    geometry,
    simplex_index: int,
    rank1: int,
    parents: dict[int, int],
    sizes: dict[int, int],
    exterior: int,
    event_hook=None,
) -> None:
    """Process one tetrahedron following MKALF ``handle_tetra_seq``."""

    mesh = geometry.mesh
    simplex_index = int(simplex_index)
    _union_find_add(parents, sizes, simplex_index)
    if event_hook is not None:
        event_hook(simplex_index, ALF_POC_TETRA)

    for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
        triangle_index = (
            int(mesh.get_face_index(simplex_index, face_index))
            if hasattr(mesh, 'get_face_index')
            else int(face_index)
        )
        if hasattr(mesh, 'get_face_owner_indices'):
            _, owner_right = mesh.get_face_owner_indices(simplex_index, face_index)
        else:
            owner_right = int(neighbor)
        canonical_owner_left, canonical_owner_right = _canonical_face_owner_indices(
            geometry,
            simplex_index,
            face_index,
        )
        if _triangle_in_complex_at(geometry, simplex_index, face_index, int(rank1)):
            if event_hook is not None:
                event_hook(triangle_index, ALF_POC_BURIED)
            continue

        if owner_right != -1:
            owner_right = int(owner_right)
            if owner_right in parents and _union_find_root(parents, owner_right) != int(exterior):
                simplex_root = _union_find_root(parents, simplex_index)
                neighbor_root = _union_find_root(parents, owner_right)
                if event_hook is not None:
                    if simplex_root == neighbor_root:
                        event_hook(triangle_index, ALF_POC_UNION_SAME)
                    else:
                        event_hook(triangle_index, ALF_POC_UNION_TWO)
                _union_find_union(
                    parents,
                    sizes,
                    int(canonical_owner_left),
                    int(canonical_owner_right),
                    exterior,
                )
                continue

        if event_hook is not None:
            event_hook(triangle_index, ALF_POC_MOUTH)


def _handle_tetra_pocket(
    geometry,
    simplex_index: int,
    rank1: int,
    parents: dict[int, int],
    sizes: dict[int, int],
    exterior: int,
) -> None:
    """Process one tetrahedron following MKALF ``handle_tetra_pocket``."""

    mesh = geometry.mesh
    simplex_index = int(simplex_index)
    _union_find_add(parents, sizes, simplex_index)

    for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
        if _triangle_in_complex_at(geometry, simplex_index, face_index, int(rank1)):
            continue
        if int(neighbor) == -1:
            continue
        neighbor = int(neighbor)
        if neighbor in parents and _union_find_root(parents, neighbor) != int(exterior):
            _union_find_union(parents, sizes, simplex_index, neighbor, exterior)


def _build_rank_driven_components(
    geometry,
    size_limit_rank: int,
    rank1: int | None = None,
    event_hook=None,
) -> tuple[dict[int, list[int]], set[int], np.ndarray]:
    """Build pockets using the original depth-and-delay construction.

    ``rank1`` is the lower alpha-rank threshold — equivalent to the ``rank1``
    parameter in ``alf_init_pockets(rank1, rank2, do_wrap)``. Tetrahedra are
    processed rank by rank, scanning the tetrahedron rho-entry sublists between
    ``rank1 + 1`` and ``size_limit_rank``. Face connectivity is tested against
    ``rank1`` (faces not in the alpha complex at rank1 allow pocket-to-pocket
    union).

    In the historical MKALF pocket workflow, tetrahedra are *not* first filtered
    through an "empty simplex mask". They enter the pocket construction when
    their rho-rank is reached while scanning the master list.
    """

    if rank1 is None:
        rank1 = geometry.base_rank

    mesh = geometry.mesh
    exterior = -1  # sentinel for the exterior component; -1 is always the smallest root so it wins in union
    if mesh.n_simplices == 0:
        return {}, set(), np.full(mesh.n_simplices, -1, dtype=int)

    depth = _compute_pocket_depths(geometry)
    infinity_marker = mesh.n_simplices
    delayed_by_sink: dict[int, list[int]] = defaultdict(list)
    parents: dict[int, int] = {exterior: exterior}
    sizes: dict[int, int] = {exterior: 1}

    retained_simplex_indices = set()
    outside_simplex_indices = set()
    def handle_tetrahedron(simplex_index: int) -> None:
        simplex_index = int(simplex_index)
        retained_simplex_indices.add(simplex_index)
        if event_hook is None:
            _handle_tetra_pocket(
                geometry,
                simplex_index,
                int(rank1),
                parents,
                sizes,
                exterior,
            )
        else:
            _handle_tetra_seq(
                geometry,
                simplex_index,
                int(rank1),
                parents,
                sizes,
                exterior,
                event_hook=event_hook,
            )

    for rank in range(int(rank1) + 1, int(size_limit_rank) + 1):
        for simplex_index in _iter_master_tetra_rho_indices(
            geometry,
            descending=False,
            rank_start=int(rank),
            rank_end=int(rank),
        ):
            simplex_index = int(simplex_index)
            depth_index = int(depth[simplex_index])
            simplex_rho_rank = int(geometry.simplex_rho_ranks[simplex_index])

            if depth_index == simplex_index:
                if simplex_index in delayed_by_sink:
                    delayed_stack = delayed_by_sink.pop(simplex_index)
                    while delayed_stack:
                        delayed_simplex_index = delayed_stack.pop()
                        handle_tetrahedron(delayed_simplex_index)
                handle_tetrahedron(simplex_index)
                continue

            if depth_index == infinity_marker:
                _union_find_add(parents, sizes, simplex_index)
                _union_find_union(parents, sizes, simplex_index, exterior, exterior)
                outside_simplex_indices.add(simplex_index)
                continue

            depth_rho_rank = int(geometry.simplex_rho_ranks[depth_index])
            if depth_rho_rank <= int(size_limit_rank):
                if event_hook is None and depth_rho_rank == simplex_rho_rank:
                    handle_tetrahedron(simplex_index)
                else:
                    delayed_by_sink[depth_index].append(simplex_index)
            else:
                _union_find_add(parents, sizes, simplex_index)
                _union_find_union(parents, sizes, simplex_index, exterior, exterior)
                outside_simplex_indices.add(simplex_index)

        if event_hook is not None:
            event_hook(0, ALF_POC_RANK)

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


def _iter_master_tetra_rho_indices(
    geometry,
    *,
    descending: bool,
    rank_start: int,
    rank_end: int,
):
    """Yield tetrahedron rho entries from the geometry master-list view.

    This mirrors the MKALF pattern of scanning rank sublists through the
    explicit master list and reacting only to tetrahedron rho events.
    """

    master_entries = getattr(geometry, 'master_entries', None)
    master_rank_offsets = getattr(geometry, 'master_rank_offsets', None)
    if master_entries is None or master_rank_offsets is None:
        raise ValueError('CASTp component assembly requires explicit master-list entries.')

    rank_iter = (
        range(int(rank_end), int(rank_start) - 1, -1)
        if descending
        else range(int(rank_start), int(rank_end) + 1)
    )
    for rank in rank_iter:
        bounds = master_rank_offsets.get(int(rank))
        if bounds is None:
            continue
        start, end = bounds
        entries = master_entries[start:end]
        if descending:
            entries = reversed(entries)
        for entry in entries:
            if int(entry.f_type) == ALF_TETRA and int(entry.r_type) == ALF_RHO:
                yield int(entry.index)


def _build_void_components(
    geometry,
    empty_mask: np.ndarray,
) -> tuple[dict[int, list[int]], set[int]]:
    """Build voids as complement components, following ``alf_find_voids``."""

    del empty_mask

    mesh = geometry.mesh
    exterior = -1  # sentinel for the exterior component; -1 is always the smallest root so it wins in union
    parents: dict[int, int] = {exterior: exterior}
    sizes: dict[int, int] = {exterior: 1}

    face_id_to_owner_indices: dict[int, tuple[int, int]] = {}
    face_id_by_atoms: dict[tuple[int, int, int], int] = {}
    for simplex_index, face_index, face_atoms in geometry.face_records:
        face_id = face_id_by_atoms.setdefault(tuple(face_atoms), len(face_id_by_atoms))
        if face_id in face_id_to_owner_indices:
            continue
        neighbor = int(mesh.neighbors[int(simplex_index), int(face_index)])
        face_id_to_owner_indices[int(face_id)] = (
            int(simplex_index),
            exterior if neighbor == -1 else neighbor,
        )

    max_rank = _geometry_max_rank(geometry)
    master_entries = getattr(geometry, 'master_entries', None)
    master_rank_offsets = getattr(geometry, 'master_rank_offsets', None)
    if master_entries is None or master_rank_offsets is None:
        raise ValueError('CASTp void assembly requires explicit master-list entries.')

    for rank in range(max_rank, int(geometry.base_rank), -1):
        bounds = master_rank_offsets.get(int(rank))
        if bounds is None:
            continue
        start, end = bounds
        entries = list(reversed(master_entries[start:end]))
        for entry in entries:
            if int(entry.f_type) == ALF_TETRA and int(entry.r_type) == ALF_RHO:
                _union_find_add(parents, sizes, int(entry.index))
                continue

            if int(entry.f_type) != ALF_TRIANGLE or not bool(entry.is_first):
                continue

            owner_left, owner_right = face_id_to_owner_indices[int(entry.index)]
            if owner_left not in parents or owner_right not in parents:
                continue
            _union_find_union(parents, sizes, owner_left, owner_right, exterior)

    components: dict[int, list[int]] = defaultdict(list)
    blocked_nodes = {exterior}
    for simplex_index in sorted(node for node in parents if node != exterior):
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
    active_pocket_nodes: set[int] | None = None,
) -> tuple[list[tuple[int, int, int]], list[MouthFaceRecord]]:
    """Return pocket boundary faces and regular mouth seeds.

    This is the Python analogue of the historical `alf_scan_pocket_f1()`
    selection rule:

    - triangle not in the alpha complex at `rank1`
    - opposite tetrahedron is either absent (hull) or not in the current
      pocket structure

    The mouth faces returned here are therefore the regular pocket triangles
    that seed `alf_init_mouths()`. They are not filtered again through extra
    depth or beta-side heuristics at this stage.
    """

    if rank1 is None:
        rank1 = geometry.base_rank

    mesh = geometry.mesh
    boundary_faces = []
    mouth_faces = []
    simplex_index_set = set(int(index) for index in simplex_indices)
    active_pocket_nodes = (
        set(simplex_index_set)
        if active_pocket_nodes is None
        else {int(index) for index in active_pocket_nodes}
    )

    for simplex_index in simplex_indices:
        simplex_index = int(simplex_index)
        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if _triangle_in_complex_at(geometry, simplex_index, face_index, int(rank1)):
                continue

            face_atoms = mesh.get_face_atoms(simplex_index, face_index)
            if neighbor != -1 and int(neighbor) in active_pocket_nodes:
                continue

            boundary_faces.append(face_atoms)
            if neighbor == -1:
                mouth_faces.append(
                    MouthFaceRecord(
                        face_atoms=face_atoms,
                        simplex_index=simplex_index,
                        face_index=int(face_index),
                        triangle_index=(
                            int(mesh.get_face_index(simplex_index, face_index))
                            if hasattr(mesh, 'get_face_index')
                            else None
                        ),
                    )
                )
                continue

            neighbor = int(neighbor)
            if neighbor not in active_pocket_nodes:
                mouth_faces.append(
                    MouthFaceRecord(
                        face_atoms=face_atoms,
                        simplex_index=simplex_index,
                        face_index=int(face_index),
                        triangle_index=(
                            int(mesh.get_face_index(simplex_index, face_index))
                            if hasattr(mesh, 'get_face_index')
                            else None
                        ),
                    )
                )

    return boundary_faces, mouth_faces


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


def _map_local_edge(atom_indices_map: np.ndarray, edge: tuple[int, int]) -> tuple[int, int]:
    """Map one local edge to a sorted global atom pair."""

    left, right = sorted((int(edge[0]), int(edge[1])))
    return (
        int(atom_indices_map[left]),
        int(atom_indices_map[right]),
    )


def _map_local_face(
    atom_indices_map: np.ndarray,
    face: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Map one local face to a sorted global atom triple."""

    return tuple(
        sorted(int(atom_indices_map[int(atom_index)]) for atom_index in face)
    )


def _component_atom_indices(mesh, atom_indices_map: np.ndarray, simplex_indices: list[int]) -> list[int]:
    """Return the current component atom set from its tetrahedra."""

    local_atom_indices = {
        int(atom_index)
        for simplex_index in simplex_indices
        for atom_index in mesh.simplex_atom_indices[int(simplex_index)]
    }
    return _map_local_atom_indices(atom_indices_map, local_atom_indices)


def _vertex_is_interior_at(geometry, vertex_index: int, rank: int) -> bool:
    """Return whether a vertex is interior at the given rank, following MKALF."""

    return _geometry_vertex_is_interior_at(geometry, int(vertex_index), int(rank))


def _component_face_partitions(
    geometry,
    simplex_indices: list[int],
    rank1: int,
    active_pocket_nodes: set[int] | None = None,
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]]:
    """Return the canonical pocket/void face partition (`iF`, `rF`)."""

    mesh = geometry.mesh
    simplex_index_set = {int(index) for index in simplex_indices}
    active_pocket_nodes = (
        set(simplex_index_set)
        if active_pocket_nodes is None
        else {int(index) for index in active_pocket_nodes}
    )
    seen_interior = set()
    seen_regular = set()
    interior_faces = []
    regular_faces = []

    for simplex_index in simplex_indices:
        simplex_index = int(simplex_index)
        for face_index, neighbor in enumerate(mesh.neighbors[simplex_index]):
            if _triangle_in_complex_at(geometry, simplex_index, face_index, int(rank1)):
                continue

            triangle_index = None
            if hasattr(mesh, 'get_face_index'):
                triangle_index = int(mesh.get_face_index(simplex_index, face_index))
            if triangle_index is None:
                triangle_index = _map_local_face(
                    geometry.atom_indices_map,
                    mesh.get_face_atoms(simplex_index, face_index),
                )

            face_atoms = _map_local_face(
                geometry.atom_indices_map,
                mesh.get_face_atoms(simplex_index, face_index),
            )
            if neighbor == -1:
                if triangle_index not in seen_interior:
                    seen_interior.add(triangle_index)
                    interior_faces.append(face_atoms)
                if triangle_index not in seen_regular:
                    seen_regular.add(triangle_index)
                    regular_faces.append(face_atoms)
                continue

            if neighbor != -1 and int(neighbor) in active_pocket_nodes:
                if triangle_index not in seen_interior:
                    seen_interior.add(triangle_index)
                    interior_faces.append(face_atoms)
                continue

            if triangle_index not in seen_regular:
                seen_regular.add(triangle_index)
                regular_faces.append(face_atoms)

    return sorted(interior_faces), sorted(regular_faces)


def _component_edge_partitions(
    geometry,
    simplex_indices: list[int],
    touched_simplex_indices: set[int],
    rank1: int,
    rank2: int,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Return the canonical pocket/void edge partition (`iE`, `rE`)."""

    mesh = geometry.mesh
    component_edges = set()
    touched_edges = set()

    for simplex_index in simplex_indices:
        simplex_atom_indices = mesh.simplex_atom_indices[int(simplex_index)]
        component_edges.update(
            {
                tuple(sorted((int(simplex_atom_indices[0]), int(simplex_atom_indices[1])))),
                tuple(sorted((int(simplex_atom_indices[0]), int(simplex_atom_indices[2])))),
                tuple(sorted((int(simplex_atom_indices[0]), int(simplex_atom_indices[3])))),
                tuple(sorted((int(simplex_atom_indices[1]), int(simplex_atom_indices[2])))),
                tuple(sorted((int(simplex_atom_indices[1]), int(simplex_atom_indices[3])))),
                tuple(sorted((int(simplex_atom_indices[2]), int(simplex_atom_indices[3])))),
            }
        )

    for simplex_index in touched_simplex_indices:
        if int(simplex_index) < 0:
            continue
        simplex_atom_indices = mesh.simplex_atom_indices[int(simplex_index)]
        touched_edges.update(
            {
                tuple(sorted((int(simplex_atom_indices[0]), int(simplex_atom_indices[1])))),
                tuple(sorted((int(simplex_atom_indices[0]), int(simplex_atom_indices[2])))),
                tuple(sorted((int(simplex_atom_indices[0]), int(simplex_atom_indices[3])))),
                tuple(sorted((int(simplex_atom_indices[1]), int(simplex_atom_indices[2])))),
                tuple(sorted((int(simplex_atom_indices[1]), int(simplex_atom_indices[3])))),
                tuple(sorted((int(simplex_atom_indices[2]), int(simplex_atom_indices[3])))),
            }
        )

    interior_edges = []
    regular_edges = []
    for edge in sorted(component_edges):
        if _edge_is_in_complex_at(
            geometry.edge_rho_ranks,
            geometry.edge_mu1_ranks,
            edge,
            int(rank1),
        ):
            continue

        edge_mu2_rank = int(geometry.edge_mu2_ranks.get(tuple(sorted(edge)), 0))
        edge_is_interior = _rank_table_is_interior(edge_mu2_rank, int(rank2))
        edge_is_touched = tuple(sorted(edge)) in touched_edges
        global_edge = _map_local_edge(geometry.atom_indices_map, edge)

        if edge_is_interior and not edge_is_touched:
            interior_edges.append(global_edge)
        else:
            regular_edges.append(global_edge)

    return sorted(interior_edges), sorted(regular_edges)


def _component_vertex_partitions(
    geometry,
    simplex_indices: list[int],
    touched_simplex_indices: set[int],
    rank1: int,
    rank2: int,
) -> tuple[list[int], list[int]]:
    """Return the canonical pocket/void vertex partition (`iV`, `rV`)."""

    mesh = geometry.mesh
    local_component_vertices = {
        int(atom_index)
        for simplex_index in simplex_indices
        for atom_index in mesh.simplex_atom_indices[int(simplex_index)]
    }
    local_touched_vertices = {
        int(atom_index)
        for simplex_index in touched_simplex_indices
        if int(simplex_index) >= 0
        for atom_index in mesh.simplex_atom_indices[int(simplex_index)]
    }

    interior_vertices = []
    regular_vertices = []
    for vertex_index in sorted(local_component_vertices):
        if _vertex_is_in_complex_at(geometry, int(vertex_index), int(rank1)):
            continue

        is_interior = _vertex_is_interior_at(geometry, int(vertex_index), int(rank2))
        is_touched = int(vertex_index) in local_touched_vertices
        global_vertex = int(geometry.atom_indices_map[int(vertex_index)])

        if is_interior and not is_touched:
            interior_vertices.append(global_vertex)
        else:
            regular_vertices.append(global_vertex)

    return sorted(interior_vertices), sorted(regular_vertices)


def _component_regular_vertex_indices(
    geometry,
    simplex_indices: list[int],
    touched_simplex_indices: set[int],
    rank2: int,
) -> list[int]:
    """Return the MKALF-like regular vertex set (`rV`) for a pocket component."""

    _interior_vertices, regular_vertices = _component_vertex_partitions(
        geometry,
        simplex_indices,
        touched_simplex_indices,
        rank1=int(geometry.base_rank),
        rank2=int(rank2),
    )
    return regular_vertices


def build_castp_feature_records(
    geometry,
    probe_radius: float,
    alpha_rank: int | None = None,
    beta_rank: int | None = None,
) -> list[dict]:
    """Build CASTp-like feature records from the weighted tetrahedral substrate."""

    original_base_rank = int(geometry.base_rank)
    effective_base_rank = original_base_rank if alpha_rank is None else int(alpha_rank)
    size_limit_rank = _probe_rank(geometry, probe_radius) if beta_rank is None else int(beta_rank)
    geometry.base_rank = int(effective_base_rank)
    try:
        return _build_castp_feature_records_at_ranks(
            geometry,
            probe_radius,
            int(effective_base_rank),
            int(size_limit_rank),
        )
    finally:
        geometry.base_rank = int(original_base_rank)


def _build_castp_feature_records_at_ranks(
    geometry,
    probe_radius: float,
    alpha_rank: int,
    beta_rank: int,
) -> list[dict]:
    """Build feature records using explicit CASTp rank cutoffs."""

    mesh = geometry.mesh
    open_mask = _build_empty_simplex_mask(geometry, probe_radius=probe_radius)
    size_limit_rank = int(beta_rank)
    components, blocked_nodes, depth = _build_rank_driven_components(
        geometry,
        size_limit_rank,
        rank1=int(alpha_rank),
    )
    void_components, _void_blocked_nodes = _build_void_components(
        geometry,
        open_mask,
    )

    feature_records = []
    counters = {'pocket': 0, 'channel': 0, 'branched_channel': 0, 'void': 0}
    emitted_component_keys: set[tuple[int, ...]] = set()
    active_pocket_nodes = {
        int(simplex_index)
        for simplex_group in components.values()
        for simplex_index in simplex_group
    }

    for simplex_indices in sorted(void_components.values(), key=len, reverse=True):
        simplex_key = tuple(sorted(int(simplex_index) for simplex_index in simplex_indices))
        boundary_faces = _component_boundary_faces_void(
            geometry,
            simplex_indices,
        )
        max_rank = _geometry_max_rank(geometry)
        interior_faces, _regular_faces = _component_face_partitions(
            geometry,
            simplex_indices,
            rank1=int(geometry.base_rank),
        )
        interior_edges, _regular_edges = _component_edge_partitions(
            geometry,
            simplex_indices,
            {
                int(simplex_index)
                for simplex_index in blocked_nodes
                if int(simplex_index) >= 0
            },
            rank1=int(geometry.base_rank),
            rank2=max_rank,
        )
        interior_vertices, _regular_vertices = _component_vertex_partitions(
            geometry,
            simplex_indices,
            {
                int(simplex_index)
                for simplex_index in blocked_nodes
                if int(simplex_index) >= 0
            },
            rank1=int(geometry.base_rank),
            rank2=max_rank,
        )
        boundary_atom_indices = _map_local_atom_indices(
            geometry.atom_indices_map,
            {int(atom_index) for face in boundary_faces for atom_index in face},
        )
        volume = component_volume(mesh.simplex_volumes, simplex_indices)
        area = component_area(geometry.atom_coordinates, boundary_faces)
        counters['void'] += 1
        feature_records.append(
            {
                'id': counters['void'],
                'feature_type': 'void',
                'type': 'Void',
                'source': 'castp',
                'source_id': f'castp:void:{counters["void"]}',
                'iT': list(simplex_indices),
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
                'area': area,
                'volume': volume,
                'score': volume,
                'n_mouths': 0,
                'mouth_area': 0.0,
                'mouth_perimeter': 0.0,
                'mouths': [],
                'iF': list(interior_faces),
                # CASTp1 print_voids emits only t0/f0/e0/v0 scans.
                'rF': [],
                'iE': list(interior_edges),
                'rE': [],
                'iV': list(interior_vertices),
                'rV': [],
            }
        )
        emitted_component_keys.add(simplex_key)

    component_entries = []
    component_key_by_simplex: dict[int, int] = {}
    global_mouth_faces: list[MouthFaceRecord] = []

    for component_key, simplex_indices in enumerate(
        sorted(components.values(), key=len, reverse=True)
    ):
        for simplex_index in simplex_indices:
            component_key_by_simplex[int(simplex_index)] = int(component_key)
        boundary_faces, mouth_faces = _component_boundary_faces(
            geometry,
            simplex_indices,
            blocked_nodes,
            depth,
            size_limit_rank,
            rank1=geometry.base_rank,
            active_pocket_nodes=active_pocket_nodes,
        )
        component_entries.append(
            {
                'component_key': int(component_key),
                'simplex_indices': list(simplex_indices),
                'boundary_faces': list(boundary_faces),
                'mouth_face_atoms': {
                    tuple(face.face_atoms if isinstance(face, MouthFaceRecord) else face)
                    for face in mouth_faces
                },
            }
        )
        global_mouth_faces.extend(mouth_faces)

    global_mouth_clusters = cluster_mouth_faces(
        global_mouth_faces,
        getattr(geometry, 'edge_rho_ranks', {}),
        getattr(geometry, 'edge_mu1_ranks', {}),
        geometry.base_rank,
        mesh=mesh,
        depth=depth,
        infinity_marker=mesh.n_simplices,
        simplex_rho_ranks=geometry.simplex_rho_ranks,
        rank2=size_limit_rank,
    )
    mouth_clusters_by_component: dict[int, list[list[MouthFaceRecord]]] = defaultdict(list)

    for mouth_cluster in global_mouth_clusters:
        owner_component_key = None
        for face in mouth_cluster:
            if isinstance(face, MouthFaceRecord):
                owner_component_key = component_key_by_simplex.get(int(face.simplex_index))
                if owner_component_key is not None:
                    break
        if owner_component_key is None:
            cluster_face_atoms = {
                tuple(face.face_atoms if isinstance(face, MouthFaceRecord) else face)
                for face in mouth_cluster
            }
            for component_entry in component_entries:
                if cluster_face_atoms & component_entry['mouth_face_atoms']:
                    owner_component_key = int(component_entry['component_key'])
                    break
        if owner_component_key is not None:
            mouth_clusters_by_component[int(owner_component_key)].append(list(mouth_cluster))

    for component_entry in component_entries:
        simplex_indices = component_entry['simplex_indices']
        boundary_faces = component_entry['boundary_faces']
        mouth_clusters = mouth_clusters_by_component.get(
            int(component_entry['component_key']),
            [],
        )
        n_mouths = len(mouth_clusters)
        simplex_key = tuple(sorted(int(simplex_index) for simplex_index in simplex_indices))
        feature_type = _feature_type_from_n_mouths(n_mouths)

        if simplex_key in emitted_component_keys:
            continue

        counters[feature_type] += 1
        mouths = []
        total_mouth_area = 0.0
        total_mouth_perimeter = 0.0
        for mouth_index, cluster_faces in enumerate(mouth_clusters, start=1):
            cluster_face_atoms = [
                face.face_atoms if isinstance(face, MouthFaceRecord) else face
                for face in cluster_faces
            ]
            mouth_atom_indices_local = sorted({atom for face in cluster_face_atoms for atom in face})
            mouth_atom_indices = [
                int(geometry.atom_indices_map[atom_index]) for atom_index in mouth_atom_indices_local
            ]
            area = mouth_area(geometry.atom_coordinates, cluster_face_atoms)
            perimeter = mouth_perimeter(geometry.atom_coordinates, cluster_face_atoms)
            total_mouth_area += area
            total_mouth_perimeter += perimeter
            mouths.append(
                {
                    'id': mouth_index,
                    'atom_indices': sorted(mouth_atom_indices),
                    'area': area,
                    'perimeter': perimeter,
                    'faces': list(cluster_face_atoms),
                    'triangle_indices': [
                        int(face.triangle_index)
                        for face in cluster_faces
                        if isinstance(face, MouthFaceRecord) and face.triangle_index is not None
                    ],
                }
            )

        regular_vertex_indices = _component_regular_vertex_indices(
            geometry,
            simplex_indices,
            {
                int(simplex_index)
                for simplex_index in blocked_nodes
                if int(simplex_index) >= 0
            },
            size_limit_rank,
        )
        interior_faces, regular_faces = _component_face_partitions(
            geometry,
            simplex_indices,
            rank1=int(geometry.base_rank),
            active_pocket_nodes=active_pocket_nodes,
        )
        interior_edges, regular_edges = _component_edge_partitions(
            geometry,
            simplex_indices,
            {
                int(simplex_index)
                for simplex_index in blocked_nodes
                if int(simplex_index) >= 0
            },
            rank1=int(geometry.base_rank),
            rank2=int(size_limit_rank),
        )
        interior_vertices, regular_vertices = _component_vertex_partitions(
            geometry,
            simplex_indices,
            {
                int(simplex_index)
                for simplex_index in blocked_nodes
                if int(simplex_index) >= 0
            },
            rank1=int(geometry.base_rank),
            rank2=int(size_limit_rank),
        )
        volume = component_volume(mesh.simplex_volumes, simplex_indices)
        area = component_area(geometry.atom_coordinates, boundary_faces)
        feature_records.append(
            {
                'id': counters[feature_type],
                'feature_type': feature_type,
                'type': _feature_record_type(feature_type),
                'source': 'castp',
                'source_id': f'castp:{feature_type}:{counters[feature_type]}',
                'iT': list(simplex_indices),
                'tetrahedron_indices': list(simplex_indices),
                'atom_indices': _component_atom_indices(
                    mesh,
                    geometry.atom_indices_map,
                    simplex_indices,
                ),
                'boundary_atom_indices': list(regular_vertex_indices),
                'component_atom_indices': _component_atom_indices(
                    mesh,
                    geometry.atom_indices_map,
                    simplex_indices,
                ),
                'center': component_center(mesh.simplex_centers, simplex_indices),
                'area': area,
                'volume': volume,
                'score': volume,
                'n_mouths': n_mouths,
                'mouth_area': total_mouth_area,
                'mouth_perimeter': total_mouth_perimeter,
                'mouths': mouths,
                'iF': list(interior_faces),
                'rF': list(regular_faces),
                'iE': list(interior_edges),
                'rE': list(regular_edges),
                'iV': list(interior_vertices),
                'rV': list(regular_vertices),
            }
        )
        emitted_component_keys.add(simplex_key)

    feature_records.sort(key=lambda record: record['volume'], reverse=True)
    return feature_records
