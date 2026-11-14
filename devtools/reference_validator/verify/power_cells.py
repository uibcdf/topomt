"""Independently verify clipped power cells and exhaustive free-region gluing.

Completeness uses the documented convex-cap/polytope-skeleton lemma, not a
sampled graph heuristic. Producer clipping and graph search are never imported.
"""

from copy import deepcopy
from fractions import Fraction
from itertools import combinations
from math import comb
from typing import Any, Optional

from ..hull_model import HullLimits
from ..model import (
    Atom,
    Model,
    _record,
    decode_point,
    encode_point,
    encode_scalar,
    point,
    record_digest,
)
from ..power_contracts import PowerLimits, bounding_planes, domain_planes
from .geometry import _squared, contains, point_is_free, segment_is_free, volume
from .polytope import _canonical, _cross, _evaluate, _vertices


def _planes(
    model: Model, atom: Optional[Atom]
) -> tuple[tuple[int, int, int, int], ...]:
    """Independently expand each q_i-q_j affine polynomial."""
    planes = set(domain_planes(model)) | set(bounding_planes(model))
    if atom is not None:
        own = (
            *(-2 * x for x in atom.center),
            sum((x * x for x in atom.center), Fraction())
            - (atom.radius + model.probe) ** 2,
        )
        for other in model.atoms:
            if other.center == atom.center:
                continue
            theirs = (
                *(-2 * x for x in other.center),
                sum((x * x for x in other.center), Fraction())
                - (other.radius + model.probe) ** 2,
            )
            difference = tuple(a - b for a, b in zip(own, theirs))
            planes.add(_canonical((*difference[:3], -difference[3])))
    return tuple(sorted(planes))


def _indices(raw: object, size: int) -> list[int]:
    if (
        not isinstance(raw, list)
        or any(type(v) is not int or not 0 <= v < size for v in raw)
        or raw != sorted(set(raw))
    ):
        raise ValueError('Noncanonical power-cell index list')
    return raw


def _pairs(raw: object, size: int) -> list[tuple[int, int]]:
    if not isinstance(raw, list):
        raise ValueError('Power-cell edges must be arrays')
    result = []
    for pair in raw:
        if (
            not isinstance(pair, list)
            or len(pair) != 2
            or any(type(i) is not int for i in pair)
            or not 0 <= pair[0] < pair[1] < size
        ):
            raise ValueError('Invalid power-cell edge')
        result.append((pair[0], pair[1]))
    if result != sorted(set(result)):
        raise ValueError('Duplicated or unsorted cell edges')
    return result


def _geometric_edges(
    vertices: tuple[tuple[Fraction, Fraction, Fraction], ...],
    planes: tuple[tuple[int, int, int, int], ...],
) -> list[tuple[int, int]]:
    """Enumerate plane-pair lines, independently of producer vertex-pair ranks."""
    on = [{i for i, v in enumerate(vertices) if _evaluate(p, v) == 0} for p in planes]
    edges = set()
    for a, b in combinations(range(len(planes)), 2):
        if not any(_cross(planes[a][:3], planes[b][:3])):
            continue
        shared = sorted(on[a] & on[b])
        if len(shared) > 2:
            raise ValueError('Verified convex cell has non-extreme collinear vertices')
        if len(shared) == 2:
            edges.add((shared[0], shared[1]))
    return sorted(edges)


def _parts(nodes: list[int], edges: list[tuple[int, int]]) -> list[list[int]]:
    parent = {i: i for i in nodes}

    def root(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b in edges:
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    groups: dict[int, list[int]] = {}
    for i in nodes:
        groups.setdefault(root(i), []).append(i)
    return sorted(groups.values(), key=lambda g: g[0])


def _partition(raw: object, expected: list[list[int]], size: int) -> None:
    if not isinstance(raw, list):
        raise ValueError('Component partition must be an array')
    for group in raw:
        if not _indices(group, size):
            raise ValueError('Empty proposed component')
    if raw != expected:
        raise ValueError('Component partition differs from complete checked incidence')


def check(
    model: Model, certificate: object, *, limits: PowerLimits = PowerLimits()
) -> dict[str, Any]:
    """Check complete all-atom cells, edges, free regions and boundary incidences."""
    cert = _record(
        certificate,
        {
            'schema',
            'kind',
            'model_sha256',
            'arithmetic',
            'construction',
            'cells',
            'nodes',
            'components',
            'boundary_components',
        },
    )
    if (
        cert['schema'] != 'topomt.reference-validator.certificate/1'
        or cert['kind'] != 'power_cell_topology'
        or cert['arithmetic'] != 'rational-exact/1'
        or cert['model_sha256'] != model.digest
        or cert['construction'] != 'power-skeleton-caps/1'
    ):
        raise ValueError('Power-cell proof convention or model binding differs')
    if len(model.atoms) > limits.max_atoms:
        raise ValueError('Power-cell atom budget exceeded')
    sorted_atoms = sorted(model.atoms, key=lambda a: a.source_id)
    owners: list[Optional[Atom]] = list(sorted_atoms)
    if not owners:
        owners.append(None)
    rows = cert['cells']
    if not isinstance(rows, list) or len(rows) != len(owners):
        raise ValueError('Complete source-cell inventory differs')
    cells = []
    total_vertices = total_edges = steps = 0
    for atom, row in zip(owners, rows):
        if (
            not isinstance(row, dict)
            or (atom is not None and type(row.get('atom_id')) is not int)
            or row.get('atom_id') != (None if atom is None else atom.source_id)
        ):
            raise ValueError('Power-cell source identity or order differs')
        if 'coincident_dominator' in row:
            _record(row, {'atom_id', 'coincident_dominator'})
            source_id = row['coincident_dominator']
            other = next(
                (
                    a
                    for a in model.atoms
                    if type(source_id) is int and a.source_id == source_id
                ),
                None,
            )
            if (
                atom is None
                or other is None
                or other.center != atom.center
                or other.radius <= atom.radius
            ):
                raise ValueError('Coincident-cell infeasibility is false')
            cells.append(
                {
                    'atom_id': row['atom_id'],
                    'vertices': (),
                    'free_vertices': [],
                    'free_edges': [],
                }
            )
            continue
        _record(
            row,
            {'atom_id', 'support', 'vertices', 'edges', 'free_vertices', 'free_edges'},
        )
        if atom is not None and any(
            a.center == atom.center and a.radius > atom.radius for a in model.atoms
        ):
            raise ValueError(
                'A strictly dominated coincident cell needs its infeasibility witness'
            )
        planes = _planes(model, atom)
        steps += len(planes)
        if steps > limits.max_clip_steps:
            raise ValueError('Power-cell constraint budget exceeded')
        ids = _indices(row['support'], len(planes))
        if not 6 <= len(ids) <= limits.max_support_planes:
            raise ValueError('Power-cell support budget exceeded')
        kept = tuple(planes[i] for i in ids)
        if not set(bounding_planes(model)) <= set(kept):
            raise ValueError('Cell boundedness enclosure is omitted')
        vertices = _vertices(
            kept,
            HullLimits(
                max_facets=limits.max_support_planes,
                max_plane_triples=comb(limits.max_support_planes, 3),
            ),
        )
        if (
            not isinstance(row['vertices'], list)
            or tuple(decode_point(v) for v in row['vertices']) != vertices
        ):
            raise ValueError('Complete power-cell vertex inventory differs')
        if any(_evaluate(p, v) > 0 for v in vertices for p in planes):
            raise ValueError('Supporting subset enlarges the true source power cell')
        # Direct polynomial comparisons are a second guard on linearization.
        if atom is not None and any(
            _squared(v, atom.center) - (atom.radius + model.probe) ** 2
            > _squared(v, a.center) - (a.radius + model.probe) ** 2
            for v in vertices
            for a in model.atoms
        ):
            raise ValueError('A source power ordering is false')
        edges = _geometric_edges(vertices, kept)
        if _pairs(row['edges'], len(vertices)) != edges:
            raise ValueError('Complete geometric edge inventory differs')
        free = [i for i, v in enumerate(vertices) if point_is_free(model, v)]
        if _indices(row['free_vertices'], len(vertices)) != free:
            raise ValueError('Free vertex inventory differs from all atoms')
        available = set(free)
        free_edges = [
            (i, j)
            for i, j in edges
            if i in available
            and j in available
            and segment_is_free(model, vertices[i], vertices[j])
        ]
        if _pairs(row['free_edges'], len(vertices)) != free_edges:
            raise ValueError('Free whole-edge inventory differs')
        total_vertices += len(vertices)
        total_edges += len(edges)
        if (
            len(vertices) > limits.max_vertices_per_cell
            or total_vertices > limits.max_total_vertices
            or total_edges > limits.max_edges
        ):
            raise ValueError('Power-cell vertex/edge work budget exceeded')
        cells.append(
            {
                'atom_id': row['atom_id'],
                'vertices': vertices,
                'free_vertices': free,
                'free_edges': free_edges,
            }
        )
    points = sorted(
        {cell['vertices'][i] for cell in cells for i in cell['free_vertices']}
    )
    if (
        not isinstance(cert['nodes'], list)
        or [decode_point(v) for v in cert['nodes']] != points
    ):
        raise ValueError('Complete glued free-vertex inventory differs')
    node_id = {v: i for i, v in enumerate(points)}
    edges = sorted(
        {
            (node_id[cell['vertices'][i]], node_id[cell['vertices'][j]])
            for cell in cells
            for i, j in cell['free_edges']
        }
    )
    groups = _parts(list(range(len(points))), edges)
    _partition(cert['components'], groups, len(points))
    boundary = domain_planes(model)
    faces = [
        {i for i, p in enumerate(boundary) if _evaluate(p, v) == 0} for v in points
    ]
    patches = _parts(
        [i for i, f in enumerate(faces) if f],
        [(a, b) for a, b in edges if faces[a] & faces[b]],
    )
    _partition(cert['boundary_components'], patches, len(points))
    region_of = {v: i for i, g in enumerate(groups) for v in g}
    boundary_patches = []
    for index, nodes in enumerate(patches):
        incidence = {region_of[i] for i in nodes}
        if len(incidence) != 1:
            raise ValueError('Boundary patch has inconsistent region incidence')
        node_set = set(nodes)
        supports = []
        for cell in cells:
            for face_index, plane in enumerate(boundary):
                local = [
                    i
                    for i in cell['free_vertices']
                    if node_id[cell['vertices'][i]] in node_set
                    and _evaluate(plane, cell['vertices'][i]) == 0
                ]
                if local:
                    supports.append(
                        {
                            'atom_id': cell['atom_id'],
                            'domain_plane_index': face_index,
                            'local_free_vertex_ids': local,
                        }
                    )
        boundary_patches.append(
            {
                'patch_id': f'PATCH-{index + 1}',
                'region_id': f'REG-{next(iter(incidence)) + 1}',
                'node_ids': nodes,
                'face_supports': supports,
            }
        )
    regions = []
    for index, nodes in enumerate(groups):
        supports = []
        for cell in cells:
            local = [
                i
                for i in cell['free_vertices']
                if region_of[node_id[cell['vertices'][i]]] == index
            ]
            if local:
                supports.append(
                    {'atom_id': cell['atom_id'], 'local_free_vertex_ids': local}
                )
        attached = [
            p['patch_id']
            for p in boundary_patches
            if p['region_id'] == f'REG-{index + 1}'
        ]
        regions.append(
            {
                'region_id': f'REG-{index + 1}',
                'node_ids': nodes,
                'representative': encode_point(points[nodes[0]]),
                'cell_supports': supports,
                'boundary_patch_ids': attached,
                'touches_domain_boundary': bool(attached),
            }
        )
    return {
        'topology_complete': True,
        'topology_status': 'resolved',
        'n_components': len(groups),
        'regions': regions,
        'n_boundary_patches': len(patches),
        'boundary_status': 'resolved',
        'boundary_patches': boundary_patches,
        'length_unit': 'nm',
        'nodes': cert['nodes'],
        'edges': [list(e) for e in edges],
        'support_meaning': 'Strict free subsets of source power cells (or their declared domain faces) classified by their supporting-root vertex component; never entire convex cells or faces.',
        'per_region_volume_status': 'not_computed',
        'volume_lower': encode_scalar(Fraction()),
        'volume_upper': encode_scalar(volume(model.domain) if groups else Fraction()),
        'volume_unit': 'nm**3',
        'volume_enclosure_status': 'resolved',
        'precision_status': 'not_requested',
        'construction': 'power-skeleton-caps/1',
        'power_limits': limits.to_record(),
    }


def _locate(
    model: Model,
    cert: dict[str, Any],
    checked: dict[str, Any],
    x: tuple[Fraction, Fraction, Fraction],
) -> dict[str, Any]:
    state = (
        'outside_domain'
        if not contains(model.domain, x)
        else 'free'
        if point_is_free(model, x)
        else 'blocked'
    )
    result: dict[str, Any] = {
        'model_sha256': model.digest,
        'topology_certificate_sha256': record_digest(cert),
        'point': encode_point(x),
        'length_unit': 'nm',
        'point_state': state,
        'region_id': None,
        'boundary_patch_id': None,
    }
    if state != 'free':
        return result
    atom = (
        min(
            model.atoms,
            key=lambda a: (
                _squared(x, a.center) - (a.radius + model.probe) ** 2,
                a.source_id,
            ),
        )
        if model.atoms
        else None
    )
    cell = next(
        c
        for c in cert['cells']
        if c['atom_id'] == (None if atom is None else atom.source_id)
    )
    vertices = [decode_point(v) for v in cell['vertices']]
    center = point((0, 0, 0)) if atom is None else atom.center

    def root(
        candidates: list[tuple[Fraction, Fraction, Fraction]],
    ) -> tuple[Fraction, Fraction, Fraction]:
        v = max(
            candidates,
            key=lambda v: sum((a - b) * (c - b) for a, b, c in zip(x, center, v)),
        )
        if not segment_is_free(model, x, v):
            raise ValueError('Supporting-root segment is not free')
        return v

    v = root(vertices)
    node = checked['nodes'].index(encode_point(v))
    result['region_id'] = next(
        r['region_id'] for r in checked['regions'] if node in r['node_ids']
    )
    result['root_point'] = encode_point(v)
    for plane in domain_planes(model):
        if _evaluate(plane, x) == 0:
            face_root = root([q for q in vertices if _evaluate(plane, q) == 0])
            face_node = checked['nodes'].index(encode_point(face_root))
            result['boundary_patch_id'] = next(
                p['patch_id']
                for p in checked['boundary_patches']
                if face_node in p['node_ids']
            )
            break
    return result


def locate(
    model: Model, certificate: object, x: tuple[Fraction, Fraction, Fraction]
) -> dict[str, Any]:
    """Assign a point to a complete checked physical region and boundary patch.

    Parameters
    ----------
    model : Model
        All-atom model, fixed probe and bounded convex observation domain.
    certificate : object
        Complete power-cell certificate; independently checked before use.
    x : tuple of Fraction
        Exact probe-center coordinates in nm.

    Returns
    -------
    dict
        Occupancy, model-scoped region and optional boundary-patch identity.
        A free point includes its exactly checked supporting-root endpoint.

    Raises
    ------
    ValueError
        The certificate, coordinates or geometric support are invalid.
    """
    from . import verify

    checked = verify(model, certificate)
    if (
        not isinstance(certificate, dict)
        or certificate['kind'] != 'power_cell_topology'
    ):
        raise ValueError('Region location requires a complete power-cell certificate')
    return _locate(model, certificate, checked, point(x))


def path_between(
    model: Model,
    certificate: object,
    start: tuple[Fraction, Fraction, Fraction],
    end: tuple[Fraction, Fraction, Fraction],
) -> dict[str, Any]:
    """Prove anchor separation or return a separately checkable continuous path.

    Parameters
    ----------
    model : Model
        All-atom model, fixed probe and bounded convex observation domain.
    certificate : object
        Complete power-cell certificate; independently checked before use.
    start, end : tuple of Fraction
        Exact free probe-center anchors in nm.

    Returns
    -------
    dict
        Input bindings and resolved connectivity. Separated anchors identify
        different complete regions. Connected anchors include a continuous
        piecewise-linear path independently checked against every source atom.

    Raises
    ------
    ValueError
        A certificate is invalid or either anchor is blocked/outside the domain.
    """
    from . import verify

    checked = verify(model, certificate)
    if (
        not isinstance(certificate, dict)
        or certificate['kind'] != 'power_cell_topology'
    ):
        raise ValueError('Connectivity requires a complete power-cell certificate')
    return _path_between_checked(model, certificate, checked, start, end)


def _path_between_checked(
    model: Model,
    certificate: dict[str, Any],
    checked: dict[str, Any],
    start: tuple[Fraction, Fraction, Fraction],
    end: tuple[Fraction, Fraction, Fraction],
) -> dict[str, Any]:
    from . import verify

    start, end = point(start), point(end)
    a, b = (_locate(model, certificate, checked, x) for x in [start, end])
    if a['point_state'] != 'free' or b['point_state'] != 'free':
        raise ValueError(
            'Connectivity anchors must both be free in the declared domain'
        )
    common = {
        'connectivity_status': 'resolved',
        'model_sha256': model.digest,
        'topology_certificate_sha256': record_digest(certificate),
        'start': encode_point(start),
        'end': encode_point(end),
        'length_unit': 'nm',
        'start_membership': a,
        'end_membership': b,
    }
    if a['region_id'] != b['region_id']:
        return {
            **common,
            'connected': False,
            'start_region_id': a['region_id'],
            'end_region_id': b['region_id'],
        }
    first, last = (checked['nodes'].index(q['root_point']) for q in [a, b])
    neighbors: dict[int, list[int]] = {i: [] for i in range(len(checked['nodes']))}
    for i, j in checked['edges']:
        neighbors[i].append(j)
        neighbors[j].append(i)
    parent: dict[int, Optional[int]] = {first: None}
    todo = [first]
    while todo and last not in parent:
        v = todo.pop(0)
        for w in neighbors[v]:
            if w not in parent:
                parent[w] = v
                todo.append(w)
    chain = []
    cursor: Optional[int] = last
    while cursor is not None:
        chain.append(cursor)
        cursor = parent[cursor]
    points = [
        encode_point(start),
        *[checked['nodes'][i] for i in reversed(chain)],
        encode_point(end),
    ]
    proof = {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'path',
        'model_sha256': model.digest,
        'arithmetic': 'rational-exact/1',
        'points': points,
    }
    verify(model, proof)
    return {
        **common,
        'connected': True,
        'region_id': a['region_id'],
        'path_certificate': proof,
    }


def query_anchors(
    model: Model,
    certificate: object,
    *,
    anchors: dict[str, tuple[Fraction, Fraction, Fraction]],
    pairs: list[tuple[str, str]],
) -> dict[str, Any]:
    """Check one detached topology proof and answer a bounded batch of queries.

    Parameters
    ----------
    model : Model
        Immutable all-atom fixed-probe model and declared convex domain.
    certificate : object
        Complete power-cell certificate, detached and independently checked
        once for this batch. No unchecked caller-supplied result is accepted.
    anchors : dict
        At most 32 named exact probe-center positions in nm.
    pairs : list of tuple of str
        At most 32 pairs of existing anchor names; both positions must be free.

    Returns
    -------
    dict
        Detached points, checked region/patch memberships and resolved pair
        answers. Each returned continuous path is independently checked against
        every source ball. No verification state is cached across calls.

    Raises
    ------
    ValueError
        The proof, named inputs, work budget or connection anchors are invalid.
    """
    from . import verify

    if (
        not isinstance(anchors, dict)
        or len(anchors) > 32
        or any(not isinstance(k, str) or not k for k in anchors)
        or not isinstance(pairs, list)
        or len(pairs) > 32
    ):
        raise ValueError('Invalid anchor batch or work budget')
    points = {name: point(x) for name, x in anchors.items()}
    connections = []
    for pair in pairs:
        if (
            not isinstance(pair, (tuple, list))
            or len(pair) != 2
            or any(not isinstance(k, str) or k not in points for k in pair)
        ):
            raise ValueError('A connection needs two existing named anchors')
        connections.append((pair[0], pair[1]))
    detached = deepcopy(certificate)
    checked = verify(model, detached)
    if not isinstance(detached, dict) or detached['kind'] != 'power_cell_topology':
        raise ValueError('Anchor batches require a complete power-cell certificate')
    locations = {
        name: _locate(model, detached, checked, x) for name, x in points.items()
    }
    return {
        'length_unit': 'nm',
        'model_sha256': model.digest,
        'topology_certificate_sha256': record_digest(detached),
        'points': {name: encode_point(x) for name, x in points.items()},
        'locations': locations,
        'pairs': [
            _path_between_checked(model, detached, checked, points[a], points[b])
            for a, b in connections
        ],
    }
