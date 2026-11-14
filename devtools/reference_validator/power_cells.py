"""Propose complete exact multi-ball topology using clipped power-cell skeletons.

The saved checker independently enumerates the proposed supporting polytopes,
all their edges and original all-atom predicates. No DFND tessellation is used.
"""

from copy import deepcopy
from fractions import Fraction
from itertools import combinations
from typing import Any, Optional

from .model import Atom, Model, decode_point, encode_point, point
from .power_contracts import (
    PowerLimits,
    bounding_box,
    bounding_planes,
    certificate_header,
    coincident_dominators,
    domain_planes,
    proposed_planes,
)
from .verify.geometry import _squared, segment_is_free
from .verify.polytope import _cross, _evaluate


def _edges(
    vertices: tuple[tuple[Fraction, Fraction, Fraction], ...],
    planes: tuple[tuple[int, int, int, int], ...],
) -> list[tuple[int, int]]:
    active = [
        {i for i, p in enumerate(planes) if _evaluate(p, v) == 0} for v in vertices
    ]
    edges = []
    for i, j in combinations(range(len(vertices)), 2):
        shared = sorted(active[i] & active[j])
        if shared and any(
            any(_cross(planes[shared[0]][:3], planes[k][:3])) for k in shared[1:]
        ):
            edges.append((i, j))
    return edges


def _clip(
    model: Model, planes: tuple[tuple[int, int, int, int], ...], limits: PowerLimits
) -> tuple[list[int], tuple[tuple[Fraction, Fraction, Fraction], ...]]:
    enclosure = set(bounding_planes(model))
    seen = tuple(sorted(enclosure))
    vertices = tuple(sorted(bounding_box(model).vertices))
    for cut in planes:
        if cut in seen:
            continue
        values = [_evaluate(cut, v) for v in vertices]
        if min(values) > 0:
            kept = (
                enclosure
                | {p for p in seen if any(_evaluate(p, v) == 0 for v in vertices)}
                | {cut}
            )
            if len(kept) > limits.max_support_planes:
                raise ValueError('Power-cell supporting-plane budget exceeded')
            return sorted(planes.index(p) for p in kept), ()
        if max(values) < 0:
            # Strict slack on every vertex stays strict on every later subset.
            # This plane cannot define an edge or become active after clipping.
            # It remains in the full source inventory and final checker input.
            continue
        if max(values) > 0:
            retained = {v for v, value in zip(vertices, values) if value <= 0}
            for i, j in _edges(vertices, seen):
                if values[i] * values[j] < 0:
                    t = values[i] / (values[i] - values[j])
                    retained.add(
                        point(
                            [a + t * (b - a) for a, b in zip(vertices[i], vertices[j])]
                        )
                    )
            vertices = tuple(sorted(retained))
            if len(vertices) > limits.max_vertices_per_cell:
                raise ValueError('Power-cell vertex budget exceeded')
        # Keep exactly the active working planes plus the fixed enclosure.
        # A plane with no active vertex cannot support any current edge. No
        # geometric tolerance or obstacle selection participates in this step.
        seen = tuple(
            sorted(
                enclosure
                | {
                    p
                    for p in (*seen, cut)
                    if any(_evaluate(p, v) == 0 for v in vertices)
                }
            )
        )
    kept = enclosure | {
        p for p in planes if any(_evaluate(p, v) == 0 for v in vertices)
    }
    if len(kept) > limits.max_support_planes:
        raise ValueError('Power-cell supporting-plane budget exceeded')
    return sorted(planes.index(p) for p in kept), vertices


def _groups(nodes: list[int], edges: list[tuple[int, int]]) -> list[list[int]]:
    neighbors: dict[int, set[int]] = {i: set() for i in nodes}
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    remaining = set(nodes)
    result = []
    while remaining:
        todo = [min(remaining)]
        found = set()
        while todo:
            v = todo.pop()
            if v in found:
                continue
            found.add(v)
            todo.extend(neighbors[v] - found)
        remaining -= found
        result.append(sorted(found))
    return result


def _availability(
    model: Model,
    atom: Optional[Atom],
    vertices: tuple[tuple[Fraction, Fraction, Fraction], ...],
    edges: list[tuple[int, int]],
) -> tuple[list[int], list[tuple[int, int]]]:
    free = [
        i
        for i, v in enumerate(vertices)
        if atom is None or _squared(v, atom.center) > (atom.radius + model.probe) ** 2
    ]
    available = set(free)
    free_edges = [
        (i, j)
        for i, j in edges
        if i in available
        and j in available
        and segment_is_free(model, vertices[i], vertices[j])
    ]
    return free, free_edges


def topology_certificate(
    model: Model, *, limits: PowerLimits = PowerLimits()
) -> dict[str, Any]:
    """Construct a bounded complete topology proposal; independently verify it.

    Parameters
    ----------
    model : Model
        Original all-atom fixed-probe model and declared convex domain.
    limits : PowerLimits
        Finite cell/support/vertex/edge work limits, never geometric tolerances.

    Returns
    -------
    dict
        Unverified exhaustive power-cell/skeleton certificate, with proposed
        region and boundary-patch partitions. No nonempty-region volume precision.

    Raises
    ------
    ValueError
        Input or construction exceeds its admitted bounded envelope.
    """
    if len(model.atoms) > limits.max_atoms:
        raise ValueError('Power-cell atom budget exceeded')
    sorted_atoms = sorted(model.atoms, key=lambda a: a.source_id)
    owners: list[Optional[Atom]] = list(sorted_atoms)
    if not owners:
        owners.append(None)
    cells: list[dict[str, Any]] = []
    total_vertices = total_edges = steps = 0
    for atom in owners:
        if atom is not None and coincident_dominators(model, atom):
            cells.append(
                {
                    'atom_id': atom.source_id,
                    'coincident_dominator': coincident_dominators(model, atom)[0],
                }
            )
            continue
        planes = proposed_planes(model, atom)
        steps += len(planes)
        if steps > limits.max_clip_steps:
            raise ValueError('Power-cell clipping-step budget exceeded')
        support, vertices = _clip(model, planes, limits)
        if len(vertices) > limits.max_vertices_per_cell:
            raise ValueError('Power-cell vertex budget exceeded')
        edges = _edges(vertices, tuple(planes[i] for i in support))
        total_vertices += len(vertices)
        total_edges += len(edges)
        if total_vertices > limits.max_total_vertices or total_edges > limits.max_edges:
            raise ValueError('Power-cell total vertex/edge budget exceeded')
        free, free_edges = _availability(model, atom, vertices, edges)
        cells.append(
            {
                'atom_id': None if atom is None else atom.source_id,
                'support': support,
                'vertices': [encode_point(v) for v in vertices],
                'edges': [list(e) for e in edges],
                'free_vertices': free,
                'free_edges': [list(e) for e in free_edges],
            }
        )
    return _assemble(model, cells)


def _assemble(model: Model, cells: list[dict[str, Any]]) -> dict[str, Any]:

    points = sorted(
        {
            decode_point(cell['vertices'][i])
            for cell in cells
            if 'vertices' in cell
            for i in cell['free_vertices']
        }
    )
    ids = {p: i for i, p in enumerate(points)}
    global_edges = sorted(
        {
            (
                ids[decode_point(cell['vertices'][i])],
                ids[decode_point(cell['vertices'][j])],
            )
            for cell in cells
            if 'vertices' in cell
            for i, j in cell['free_edges']
        }
    )
    boundary = domain_planes(model)
    on_faces = [
        {i for i, p in enumerate(boundary) if _evaluate(p, v) == 0} for v in points
    ]
    boundary_nodes = [i for i, faces in enumerate(on_faces) if faces]
    boundary_edges = [(a, b) for a, b in global_edges if on_faces[a] & on_faces[b]]
    return {
        **certificate_header(model),
        'cells': cells,
        'nodes': [encode_point(v) for v in points],
        'components': _groups(list(range(len(points))), global_edges),
        'boundary_components': _groups(boundary_nodes, boundary_edges),
    }


def reprobe_certificate(
    source_model: Model,
    source_certificate: object,
    target_model: Model,
    *,
    limits: PowerLimits = PowerLimits(),
) -> dict[str, Any]:
    """Reuse checked cell geometry for a new probe with identical inequalities.

    Parameters
    ----------
    source_model : Model
        Original immutable model to which the source certificate is bound.
    source_certificate : object
        Complete power-cell proof, detached and independently checked here.
    target_model : Model
        Same atoms, source/frame/domain and numerical convention; only the
        probe may differ. Every full source/target power inequality must agree.
    limits : PowerLimits
        Finite checking envelope, never a geometric tolerance.

    Returns
    -------
    dict
        Unverified target proof with the same complete cell geometry. Every
        free vertex, whole-edge predicate and global/boundary partition is
        computed anew for the target probe. Independently verify before use.

    Raises
    ------
    ValueError
        Any nonprobe input changes, an inequality differs, or the source proof
        or work envelope is invalid. No partial subset or fallback is used.
    """
    from .verify.power_cells import check

    before, after = source_model.to_record(), target_model.to_record()
    before.pop('probe')
    after.pop('probe')
    if before != after:
        raise ValueError('Geometry reuse may change only the probe')
    if len(source_model.atoms) > limits.max_atoms:
        raise ValueError('Power-cell atom budget exceeded')
    sorted_atoms = sorted(source_model.atoms, key=lambda a: a.source_id)
    owners: list[Optional[Atom]] = list(sorted_atoms)
    if not owners:
        owners.append(None)
    if any(
        proposed_planes(source_model, a) != proposed_planes(target_model, a)
        for a in owners
    ):
        raise ValueError('Probe change alters full source power inequalities')
    detached = deepcopy(source_certificate)
    check(source_model, detached, limits=limits)
    if not isinstance(detached, dict):
        raise ValueError('Source certificate must be a record')
    cells = []
    for atom, row in zip(owners, detached['cells']):
        if 'coincident_dominator' in row:
            cells.append(dict(row))
            continue
        vertices = tuple(decode_point(v) for v in row['vertices'])
        edges = [(i, j) for i, j in row['edges']]
        free, free_edges = _availability(target_model, atom, vertices, edges)
        cells.append(
            {
                **{k: row[k] for k in ['atom_id', 'support', 'vertices', 'edges']},
                'free_vertices': free,
                'free_edges': [list(e) for e in free_edges],
            }
        )
    return _assemble(target_model, cells)
