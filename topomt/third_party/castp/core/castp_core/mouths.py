"""Mouth detection helpers for the native CASTp implementation."""

from collections import defaultdict
from dataclasses import dataclass

import numpy as np

from .geometry import _edge_is_in_complex_at


@dataclass(frozen=True)
class MouthFaceRecord:
    """Canonical record for one regular mouth triangle seed."""

    face_atoms: tuple[int, int, int]
    simplex_index: int
    face_index: int
    triangle_index: int | None = None


@dataclass(frozen=True)
class EdgeFacetRecord:
    """Native analogue of one historical edge-facet in the mouth walk."""

    oriented_face_atoms: tuple[int, int, int]
    face_atoms: tuple[int, int, int]
    triangle_index: int | None
    simplex_index: int


def _ensure_mouth_face_triangle_index(record: MouthFaceRecord, mesh) -> MouthFaceRecord:
    """Return a mouth-face record with canonical triangle identity when possible."""

    if record.triangle_index is not None:
        return record
    triangle_index = None
    if hasattr(mesh, 'get_face_index'):
        triangle_index = mesh.get_face_index(int(record.simplex_index), int(record.face_index))
    if triangle_index is not None:
        return MouthFaceRecord(
            face_atoms=record.face_atoms,
            simplex_index=int(record.simplex_index),
            face_index=int(record.face_index),
            triangle_index=triangle_index,
        )
    return record


def _local_face_index(simplex_index: int, a: int, b: int, c: int, mesh) -> int:
    """Return the local face index of `(a, b, c)` within one tetrahedron."""

    tet_vertices = [int(v) for v in mesh.simplex_atom_indices[int(simplex_index)]]
    if not all(vertex in tet_vertices for vertex in (int(a), int(b), int(c))):
        raise ValueError('Edge-facet face atoms are not local to the provided simplex.')
    return next(i for i, v in enumerate(tet_vertices) if v not in (int(a), int(b), int(c)))


def _make_edge_facet(
    a: int,
    b: int,
    c: int,
    simplex_index: int,
    mesh,
) -> EdgeFacetRecord:
    """Build one native edge-facet record from explicit local state."""

    simplex_index = int(simplex_index)
    a = int(a)
    b = int(b)
    c = int(c)
    face_atoms = tuple(sorted((a, b, c)))
    triangle_index = None
    face_index = _local_face_index(simplex_index, a, b, c, mesh)
    if hasattr(mesh, 'get_face_index'):
        triangle_index = mesh.get_face_index(simplex_index, face_index)
    return EdgeFacetRecord(
        oriented_face_atoms=(a, b, c),
        face_atoms=face_atoms,
        triangle_index=triangle_index,
        simplex_index=simplex_index,
    )


def _mouth_face_edge_facets(
    face_atoms: tuple[int, int, int],
) -> tuple[tuple[tuple[int, int], int], ...]:
    """Return the three outward edge-facets in historical `Enext` order.

    For an outward-oriented mouth triangle `(a, b, c)`, MKALF visits:

    - `tri[0]`
    - `Enext(tri[0])`
    - `Enext(Enext(tri[0]))`

    At the level of undirected edges plus opposite vertex, that sequence is:

    - edge `(a, b)` with third vertex `c`
    - edge `(b, c)` with third vertex `a`
    - edge `(c, a)` with third vertex `b`
    """

    a, b, c = (int(face_atoms[0]), int(face_atoms[1]), int(face_atoms[2]))
    return (
        ((a, b), c),
        ((b, c), a),
        ((c, a), b),
    )


def _edge_facet_enext(edge_facet: EdgeFacetRecord) -> EdgeFacetRecord:
    """Return the native analogue of `Enext(edge_facet)`."""

    a, b, c = edge_facet.oriented_face_atoms
    return EdgeFacetRecord(
        oriented_face_atoms=(b, c, a),
        face_atoms=edge_facet.face_atoms,
        triangle_index=edge_facet.triangle_index,
        simplex_index=edge_facet.simplex_index,
    )


def _mouth_face_initial_edge_facets(
    simplex_index: int,
    face_index: int,
    mesh,
    depth: np.ndarray,
    infinity_marker: int,
    simplex_rho_ranks: np.ndarray | None,
    rank2: int | None,
) -> tuple[EdgeFacetRecord, EdgeFacetRecord, EdgeFacetRecord]:
    """Return the three outward initial edge-facets for one mouth face."""

    outward_atoms = _mouth_face_outward_atoms(
        simplex_index,
        face_index,
        mesh,
        depth,
        infinity_marker,
        simplex_rho_ranks,
        rank2,
    )
    tri0 = _make_edge_facet(
        outward_atoms[0],
        outward_atoms[1],
        outward_atoms[2],
        simplex_index,
        mesh,
    )
    tri1 = _edge_facet_enext(tri0)
    tri2 = _edge_facet_enext(tri1)
    return (tri0, tri1, tri2)


def _edge_facet_fnext(
    edge_facet: EdgeFacetRecord,
    mesh,
) -> EdgeFacetRecord:
    """Return the next edge-facet around edge `(a, b)`.

    This is the native analogue of applying `Fnext` once to an oriented
    edge-facet record. The returned record is owned by the neighboring
    tetrahedron when such a tetrahedron exists, which is closer to the
    historical edge-facet semantics than reconstructing the next state from
    detached scalars.

    The returned edge-facet record carries the simplex index of the neighboring
    tetrahedron that owns the next walk state. When the rotation hits the hull,
    the returned simplex index is `-1`.
    """

    simplex_index = int(edge_facet.simplex_index)
    a, b, c = (int(atom_index) for atom_index in edge_facet.oriented_face_atoms)
    tet_vertices = [int(v) for v in mesh.simplex_atom_indices[simplex_index]]
    d = next(v for v in tet_vertices if v not in (a, b, c))

    face_index = next(i for i, v in enumerate(tet_vertices) if v == c)
    next_simplex_index = int(mesh.neighbors[simplex_index, face_index])
    if next_simplex_index == -1:
        triangle_index = None
        if hasattr(mesh, 'get_face_index'):
            triangle_index = mesh.get_face_index(simplex_index, face_index)
        next_edge_facet = EdgeFacetRecord(
            oriented_face_atoms=(a, b, d),
            face_atoms=tuple(sorted((a, b, d))),
            triangle_index=triangle_index,
            simplex_index=-1,
        )
        return next_edge_facet

    next_edge_facet = _make_edge_facet(a, b, d, next_simplex_index, mesh)
    return next_edge_facet


def _mouth_face_outward_atoms(
    simplex_index: int,
    face_index: int,
    mesh,
    depth: np.ndarray,
    infinity_marker: int,
    simplex_rho_ranks: np.ndarray | None,
    rank2: int | None,
) -> tuple[int, int, int]:
    """Return the outward-oriented mouth triangle atoms for `alf_init_mouths`.

    This mirrors the historical:

    - `tri[0] = EdFacet(t, 0)`
    - `dp = depth[alf_tetra_index(tri[0])]`
    - if `dp == infinity` or `rho(dp) > rank2`: `tri[0] = Sym(tri[0])`

    In the native path, the `MouthFaceRecord` simplex identifies the pocket-side
    tetrahedron. For such tetrahedra, the outward-oriented face order given by
    the mesh is the direct analogue of `tri[0]`. If the supplied simplex is not
    on the pocket side, we reverse the orientation to emulate `Sym(tri[0])`.
    """

    simplex_index = int(simplex_index)
    face_index = int(face_index)
    oriented = tuple(
        int(atom_index)
        for atom_index in mesh.get_oriented_face_atoms(simplex_index, face_index)
    )

    sink = int(depth[simplex_index])
    sink_is_outside = sink == int(infinity_marker)
    if not sink_is_outside and simplex_rho_ranks is not None and rank2 is not None:
        sink_is_outside = int(simplex_rho_ranks[sink]) > int(rank2)

    if sink_is_outside:
        return (oriented[0], oriented[2], oriented[1])
    return oriented


def _fnext_walk_around_edge(
    start_edge_facet: EdgeFacetRecord,
    mesh,
    depth: np.ndarray,
    infinity_marker: int,
    simplex_rho_ranks: np.ndarray | None = None,
    rank2: int | None = None,
) -> EdgeFacetRecord | None:
    """Rotate around edge (a, b) through pocket tetrahedra (MKALF Fnext walk).

    Starting from one explicit edge-facet record, pivots around its edge one
    tetrahedron at a time until reaching:

    - a hull face (`next_tet == -1`)
    - a tetrahedron flowing to infinity (`depth[t] == infinity_marker`)
    - or a tetrahedron whose sink is not in the rank2 shape

    Returns the exit edge-facet record itself. The simplex index is ``-1`` for
    a hull exit. Returns ``None`` if a cycle is detected (safety valve —
    should not happen in a valid triangulation).
    """

    current_edge_facet = start_edge_facet
    max_steps = 100_000  # safety valve against degenerate cycles

    for _ in range(max_steps):
        next_edge_facet = _edge_facet_fnext(current_edge_facet, mesh)
        next_tet = int(next_edge_facet.simplex_index)

        if next_tet == -1:
            return next_edge_facet

        if depth[next_tet] == infinity_marker:
            # Non-pocket tetrahedron — walk exits here
            return next_edge_facet

        if simplex_rho_ranks is not None and rank2 is not None:
            sink = int(depth[next_tet])
            if sink >= 0 and int(simplex_rho_ranks[sink]) > int(rank2):
                return next_edge_facet

        current_edge_facet = next_edge_facet

    return None  # cycle detected


def cluster_mouth_faces(
    faces: list[tuple[int, int, int]] | list[MouthFaceRecord],
    edge_rho_ranks: dict[tuple[int, int], int] | None = None,
    edge_mu1_ranks: dict[tuple[int, int], int] | None = None,
    rank1: int = 0,
    *,
    mesh=None,
    depth: np.ndarray | None = None,
    infinity_marker: int | None = None,
    simplex_rho_ranks: np.ndarray | None = None,
    rank2: int | None = None,
) -> list[list[tuple[int, int, int]]] | list[list[MouthFaceRecord]]:
    """Group mouth faces into clusters (mouth openings).

    When canonical ``MouthFaceRecord`` inputs, ``mesh``, ``depth``, and
    ``infinity_marker`` are all provided, uses the MKALF ``alf_init_mouths``
    Fnext walk: two mouth faces are connected when they can be reached from each
    other by pivoting around an open edge through interior pocket tetrahedra.
    Only edges that are NOT in the alpha complex at ``rank1`` trigger a walk;
    attached or "small" edges are shape edges and do not connect mouths.

    Falls back to simple edge-adjacency clustering only when canonical Fnext
    context is not requested. The Fnext path intentionally rejects detached
    tuple faces because reconstructing simplex/face identity from parallel
    arrays is not the historical edge-facet representation.
    """

    if not faces:
        return []

    face_records = None
    if isinstance(faces[0], MouthFaceRecord):
        face_records = [face for face in faces]
        face_tuples = [record.face_atoms for record in face_records]
    else:
        face_tuples = [face for face in faces]

    canonical_context_requested = (
        mesh is not None
        or depth is not None
        or infinity_marker is not None
        or simplex_rho_ranks is not None
        or rank2 is not None
    )
    if face_records is None and canonical_context_requested:
        raise ValueError(
            'Canonical Fnext mouth clustering requires MouthFaceRecord inputs with '
            'explicit simplex and triangle identity.'
        )

    use_fnext = (
        face_records is not None
        and mesh is not None
        and depth is not None
        and infinity_marker is not None
    )

    if use_fnext:
        if mesh is None or not hasattr(mesh, 'get_face_index'):
            raise ValueError(
                'Canonical Fnext mouth clustering requires a mesh with explicit triangle identity.'
            )
        canonical_face_records = [
            _ensure_mouth_face_triangle_index(record, mesh)
            for record in face_records
        ]
        if any(record.triangle_index is None for record in canonical_face_records):
            raise ValueError(
                'Canonical Fnext mouth clustering requires triangle_index on every '
                'mouth-face record.'
            )
        return _cluster_mouth_faces_fnext(
            canonical_face_records,
            mesh,
            depth,
            infinity_marker,
            simplex_rho_ranks,
            rank2,
            edge_rho_ranks or {},
            edge_mu1_ranks or {},
            rank1,
        )

    # --- Fallback: simple edge-adjacency ---
    edge_to_face_indices: dict[tuple[int, int], list[int]] = defaultdict(list)
    for face_index, face in enumerate(face_tuples):
        edges = (
            tuple(sorted((face[0], face[1]))),
            tuple(sorted((face[0], face[2]))),
            tuple(sorted((face[1], face[2]))),
        )
        for edge in edges:
            edge_to_face_indices[edge].append(face_index)

    face_adjacency = [[] for _ in range(len(face_tuples))]
    for face_indices in edge_to_face_indices.values():
        for index, source in enumerate(face_indices):
            for target in face_indices[index + 1 :]:
                face_adjacency[source].append(target)
                face_adjacency[target].append(source)

    visited = [False] * len(face_tuples)
    clusters = []
    for seed in range(len(face_tuples)):
        if visited[seed]:
            continue
        stack = [seed]
        visited[seed] = True
        cluster = []
        while stack:
            current = stack.pop()
            cluster.append(face_tuples[current])
            for neighbor in face_adjacency[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
        clusters.append(cluster)

    return clusters


def _cluster_mouth_faces_fnext(
    face_records: list[MouthFaceRecord],
    mesh,
    depth: np.ndarray,
    infinity_marker: int,
    simplex_rho_ranks: np.ndarray | None,
    rank2: int | None,
    edge_rho_ranks: dict[tuple[int, int], int],
    edge_mu1_ranks: dict[tuple[int, int], int],
    rank1: int,
) -> list[list[MouthFaceRecord]]:
    """Fnext-walk implementation of mouth clustering (MKALF alf_init_mouths).

    This mirrors the original C logic in ``alf_init_mouths``:

    1. start from regular mouth triangles already known to belong to the pocket
    2. inspect each of their three oriented edge-facets
    3. only consider edges that are NOT in the alpha complex at ``rank1``
    4. use the Fnext walk around that open edge until leaving the pocket
    5. if the exit triangle is also a mouth triangle, union both mouths

    Importantly, MKALF does NOT directly union mouth triangles just because they
    share a shape edge. Doing so over-merges openings and collapses channels into
    pockets in cases such as CASTp 3.0 ``1STP Pocket 7``.
    """

    n = len(face_records)
    face_ids_by_triangle_index: dict[int, list[int]] = defaultdict(list)
    for face_id, record in enumerate(face_records):
        if record.triangle_index is not None:
            face_ids_by_triangle_index[int(record.triangle_index)].append(face_id)
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

    for face_id, record in enumerate(face_records):
        initial_edge_facets = _mouth_face_initial_edge_facets(
            record.simplex_index,
            record.face_index,
            mesh,
            depth,
            infinity_marker,
            simplex_rho_ranks,
            rank2,
        )

        for initial_edge_facet in initial_edge_facets:
            ea, eb, _third_vertex = initial_edge_facet.oriented_face_atoms
            edge_key = (min(ea, eb), max(ea, eb))
            if _edge_is_in_complex_at(edge_rho_ranks, edge_mu1_ranks, edge_key, int(rank1)):
                continue

            result = _fnext_walk_around_edge(
                initial_edge_facet,
                mesh,
                depth,
                infinity_marker,
                simplex_rho_ranks,
                rank2,
            )
            if result is None:
                continue

            if result.triangle_index is None:
                continue
            neighbor_face_ids = face_ids_by_triangle_index.get(int(result.triangle_index), [])

            for neighbor_face_id in neighbor_face_ids:
                if neighbor_face_id != face_id:
                    union(face_id, neighbor_face_id)

    clusters: dict[int, list[MouthFaceRecord]] = defaultdict(list)
    for face_id, record in enumerate(face_records):
        clusters[find(face_id)].append(record)

    return list(clusters.values())
