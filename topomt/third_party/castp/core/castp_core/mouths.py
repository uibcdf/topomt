"""Mouth detection helpers for the native CASTp implementation."""

from collections import defaultdict

import numpy as np


def _fnext_walk_around_edge(
    a: int,
    b: int,
    start_third_vertex: int,
    start_tet: int,
    mesh,
    depth: np.ndarray,
    infinity_marker: int,
) -> tuple[tuple[int, int, int], int] | None:
    """Rotate around edge (a, b) through pocket tetrahedra (MKALF Fnext walk).

    Starting from face ``(a, b, start_third_vertex)`` in ``start_tet``, pivots
    around edge ``(a, b)`` one tetrahedron at a time until reaching a non-pocket
    tetrahedron (``depth[t] == infinity_marker``) or a hull face (``next_tet ==
    -1``).

    Returns ``(exit_face_atoms_sorted, exit_tet)`` when the walk exits the pocket.
    ``exit_tet`` is ``-1`` for a hull exit.  Returns ``None`` if a cycle is
    detected (safety valve — should not happen in a valid triangulation).
    """

    c = start_third_vertex
    current_tet = int(start_tet)
    max_steps = 100_000  # safety valve against degenerate cycles

    for _ in range(max_steps):
        tet_vertices = [int(v) for v in mesh.simplex_atom_indices[current_tet]]

        # d = the fourth vertex of current_tet not on the current face (a, b, c)
        d = next(v for v in tet_vertices if v not in (a, b, c))

        # The face (a, b, d) is opposite vertex c in current_tet.
        fi_c = next(i for i, v in enumerate(tet_vertices) if v == c)
        next_tet = int(mesh.neighbors[current_tet, fi_c])

        exit_face = tuple(sorted((a, b, d)))

        if next_tet == -1:
            # Hull face — exterior boundary
            return exit_face, -1

        if depth[next_tet] == infinity_marker:
            # Non-pocket tetrahedron — walk exits here
            return exit_face, next_tet

        # Continue rotating: the shared face with next_tet is (a, b, d); the
        # vertex "left behind" in next_tet's rotation is d.
        c = d
        current_tet = next_tet

    return None  # cycle detected


def cluster_mouth_faces(
    faces: list[tuple[int, int, int]],
    edge_rho_ranks: dict[tuple[int, int], int] | None = None,
    rank1: int = 0,
    *,
    face_simplex_indices: list[int] | None = None,
    mesh=None,
    depth: np.ndarray | None = None,
    infinity_marker: int | None = None,
) -> list[list[tuple[int, int, int]]]:
    """Group mouth faces into clusters (mouth openings).

    When ``face_simplex_indices``, ``mesh``, ``depth``, and ``infinity_marker``
    are all provided, uses the MKALF ``alf_init_mouths`` Fnext walk: two mouth
    faces are connected when they can be reached from each other by pivoting
    around an open edge through interior pocket tetrahedra.  Only edges that are
    NOT in the alpha complex at ``rank1`` (``edge_rho_rank > rank1``) trigger a
    walk; attached or "small" edges are shape edges and do not connect mouths.

    Falls back to simple edge-adjacency clustering when the Fnext data are not
    provided (used internally by tests and legacy callers).
    """

    if not faces:
        return []

    use_fnext = (
        face_simplex_indices is not None
        and mesh is not None
        and depth is not None
        and infinity_marker is not None
    )

    if use_fnext:
        return _cluster_mouth_faces_fnext(
            faces,
            face_simplex_indices,
            mesh,
            depth,
            infinity_marker,
            edge_rho_ranks or {},
            rank1,
        )

    # --- Fallback: simple edge-adjacency ---
    edge_to_face_indices: dict[tuple[int, int], list[int]] = defaultdict(list)
    for face_index, face in enumerate(faces):
        edges = (
            tuple(sorted((face[0], face[1]))),
            tuple(sorted((face[0], face[2]))),
            tuple(sorted((face[1], face[2]))),
        )
        for edge in edges:
            edge_to_face_indices[edge].append(face_index)

    face_adjacency = [[] for _ in range(len(faces))]
    for face_indices in edge_to_face_indices.values():
        for index, source in enumerate(face_indices):
            for target in face_indices[index + 1 :]:
                face_adjacency[source].append(target)
                face_adjacency[target].append(source)

    visited = [False] * len(faces)
    clusters = []
    for seed in range(len(faces)):
        if visited[seed]:
            continue
        stack = [seed]
        visited[seed] = True
        cluster = []
        while stack:
            current = stack.pop()
            cluster.append(faces[current])
            for neighbor in face_adjacency[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
        clusters.append(cluster)

    return clusters


def _cluster_mouth_faces_fnext(
    faces: list[tuple[int, int, int]],
    face_simplex_indices: list[int],
    mesh,
    depth: np.ndarray,
    infinity_marker: int,
    edge_rho_ranks: dict[tuple[int, int], int],
    rank1: int,
) -> list[list[tuple[int, int, int]]]:
    """Fnext-walk implementation of mouth clustering (MKALF alf_init_mouths).

    Two-step approach matching the observed oracle behaviour:

    1. **Shape edges** (rho_rank ≤ rank1, in the alpha complex at rank1): directly
       union any two mouth faces that share such an edge.  This connects mouth faces
       whose shared edge is part of the alpha shape (attached edges, rho=0, as well
       as edges smaller than the probe radius).

    2. **Open edges** (rho_rank > rank1, not in the alpha complex at rank1): use the
       MKALF Fnext walk to find the opposite mouth face around this edge through the
       pocket interior, and union them.  This connects non-adjacent mouth faces
       linked through interior pocket tetrahedra.

    The hybrid ensures that fully-attached mouth faces (all edges rho=0) are still
    grouped with their direct neighbours, while non-adjacent faces connected via
    open-edge tunnels are also merged.
    """

    n = len(faces)
    face_to_id = {face: i for i, face in enumerate(faces)}
    face_set = set(faces)
    parents = list(range(n))

    def find(x: int) -> int:
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x

    def union(x: int, y: int) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            if rx > ry:
                rx, ry = ry, rx
            parents[ry] = rx

    # Build edge → face index map for direct (shape-edge) adjacency
    edge_to_face_ids: dict[tuple[int, int], list[int]] = defaultdict(list)
    for face_id, face in enumerate(faces):
        a, b, c = face
        for ea, eb in ((a, b), (a, c), (b, c)):
            edge_to_face_ids[(min(ea, eb), max(ea, eb))].append(face_id)

    for face_id, (face, start_tet) in enumerate(zip(faces, face_simplex_indices)):
        a, b, c = face  # already sorted

        # Three edges of the face with their respective "third vertex"
        edges_with_third = (
            ((a, b), c),
            ((a, c), b),
            ((b, c), a),
        )

        for edge, third_vertex in edges_with_third:
            ea, eb = edge
            edge_key = (min(ea, eb), max(ea, eb))
            edge_rho_rank = edge_rho_ranks.get(edge_key, 0)

            if edge_rho_rank <= rank1:
                # Shape edge: directly union all mouth faces sharing this edge
                for other_id in edge_to_face_ids[edge_key]:
                    if other_id != face_id:
                        union(face_id, other_id)
            else:
                # Open edge: Fnext walk to find the opposite mouth face
                result = _fnext_walk_around_edge(
                    ea, eb, third_vertex, start_tet, mesh, depth, infinity_marker
                )
                if result is None:
                    continue
                exit_face, _exit_tet = result
                if exit_face in face_set and exit_face != face:
                    union(face_id, face_to_id[exit_face])

    clusters: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for face_id, face in enumerate(faces):
        clusters[find(face_id)].append(face)

    return list(clusters.values())
