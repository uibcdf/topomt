"""Typed components of the DFN decomposition, mirroring ``Topography``.

See ``devguide/DFND/object_model.md``. A *component* is the graph object (a set of
tetrahedron nodes) together with its *spatial representation* (the atoms that
realize it, volume, center); *motifs* are sub-structures of a component. The word
*feature* is reserved for the public ``Topography`` level and never appears here.

`Component` mirrors `BaseFeature` (a `side` derived from `family`, just as a
feature's `shape_type`/`dimensionality` are derived from `feature_type`).
`Components` mirrors the `Topography` registry (a `Mapping` with `_by_side` /
`_by_family` indexes and the same query API).
"""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterator, Mapping
from typing import Any

# side is derived from family, exactly as feature shape/dimensionality are derived
# from feature_type in features/_feature_constants.py
_SIDE_BY_FAMILY = {
    'void': 'wet',
    'pocket': 'wet',
    'channel': 'wet',
    'surface_concavity': 'wet',
    'nonresident_passage': 'wet',
    'degenerate_subprobe': 'wet',
    'percolating': 'wet',
    'dry_bank': 'dry',
}
_COMPONENT_PREFIX_BY_SIDE = {'wet': 'WET', 'dry': 'DRY'}


class Component:
    """A connected component of the DFN graph (mirrors ``BaseFeature``)."""

    def __init__(
        self,
        component_id=None,
        family=None,
        node_indices=None,
        atom_indices=None,
        boundary_face_ids=None,
        center=None,
        flags=None,
        component_index=None,
        size_rank=None,
        graph_label=None,
    ):
        self.component_id = component_id
        self.component_index = component_index
        self.size_rank = size_rank
        self.graph_label = graph_label
        self.family = family
        self.side = _SIDE_BY_FAMILY.get(family)  # derived from family
        # component facet (the graph object)
        self.node_indices = list(node_indices) if node_indices is not None else []
        self.boundary_face_ids = (
            list(boundary_face_ids) if boundary_face_ids is not None else []
        )
        # spatial representation (the atoms that realize it)
        self.atom_indices = list(atom_indices) if atom_indices is not None else []
        self.center = center
        # sub-structures of the component
        self.motifs: list[Any] = []
        self.flags = list(flags) if flags is not None else []
        self.raw_record: dict[str, Any] | None = None
        self._components: Components | None = None

    @property
    def size(self) -> int:
        return len(self.node_indices)

    def __repr__(self) -> str:
        return (
            f'<{type(self).__name__} {self.component_id} '
            f'family={self.family} nodes={self.size} atoms={len(self.atom_indices)}>'
        )


class WetComponent(Component):
    """A transit/concavity component (families void/pocket/channel/…)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resident_node_indices: list[int] = []
        self.transit_connector_node_indices: list[int] = []
        self.external_link_ids: list[int] = []
        self.n_mouths = 0
        self.n_wall_faces = 0
        self.has_residence = False
        self.has_open_interior = False
        self.volume_topological_resident = None
        self.volume_solvent_estimate = None
        # canonical motif layer (component_motifs.md section 3): topological depth
        self.topological_depth: dict[int, int] = {}
        self.depth_regions: list[dict[str, Any]] = []
        # experimental capacity-persistence motifs (component_motifs.md sections 4/6):
        # throats are low-capacity saddles, chambers are high-capacity basins,
        # ranked by topological persistence. Descriptors, not a hard classifier.
        self.throat_candidates: list[dict[str, Any]] = []
        self.chamber_candidates: list[dict[str, Any]] = []
        self.bottleneck: dict[str, Any] | None = None


class DryComponent(Component):
    """A dry bank (the dry-network side of the decomposition)."""

    def __init__(self, **kwargs):
        kwargs.pop('family', None)
        super().__init__(family='dry_bank', **kwargs)
        self.interface_ids: list[int] = []
        self.neighbor_component_ids: list[str] = []
        self.dry_depth_min = None
        self.dry_depth_max = None
        self.dry_depth_mean = None
        self.motif_ids: list[int] = []


class Components(Mapping):
    """Registry of components for one probe (mirrors ``Topography``)."""

    def __init__(self) -> None:
        self._components: dict[str, Component] = {}
        self._by_side: dict[str, set[str]] = {'wet': set(), 'dry': set()}
        self._by_family: dict[str, set[str]] = {}
        self._neighbors_of: dict[str, set[str]] = {}
        # boundary relations (raw records; components reference them by id)
        self.external_links: list[dict[str, Any]] = []  # wet component -> OCEAN
        self.interfaces: list[dict[str, Any]] = []  # dry <-> dry
        self.motifs: list[dict[str, Any]] = []  # dry-side motifs (wet pending)

    # -- Mapping interface (≡ Topography) --
    def __getitem__(self, component_id: str) -> Component:
        return self._components[component_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self._components)

    def __len__(self) -> int:
        return len(self._components)

    def __repr__(self) -> str:
        return (
            f'<dfnd.dfn.components wet={len(self._by_side["wet"])} '
            f'dry={len(self._by_side["dry"])}>'
        )

    # -- registration --
    def add(self, component: Component) -> str:
        component_id = component.component_id
        self._components[component_id] = component
        component._components = self
        self._by_side.setdefault(component.side, set()).add(component_id)
        self._by_family.setdefault(component.family, set()).add(component_id)
        self._neighbors_of.setdefault(component_id, set())
        return component_id

    def connect(self, component_id_a: str, component_id_b: str) -> None:
        """Record a boundary adjacency between two components (e.g. dry interface)."""
        self._neighbors_of.setdefault(component_id_a, set()).add(component_id_b)
        self._neighbors_of.setdefault(component_id_b, set()).add(component_id_a)

    # -- views (insertion order) --
    @property
    def wet(self) -> list[Component]:
        return [c for c in self._components.values() if c.side == 'wet']

    @property
    def dry(self) -> list[Component]:
        return [c for c in self._components.values() if c.side == 'dry']

    def by_family(self, family: str) -> list[Component]:
        return [c for c in self._components.values() if c.family == family]

    @property
    def surface_concavities(self) -> list[Component]:
        return self.by_family('surface_concavity')

    @property
    def nonresident_passages(self) -> list[Component]:
        return self.by_family('nonresident_passage')

    @property
    def degenerate_subprobes(self) -> list[Component]:
        return self.by_family('degenerate_subprobe')

    # -- lookups (≡ Topography) --
    def get_component_by_id(self, component_id: str) -> Component:
        return self._components[component_id]

    def neighbors_of(self, component_id: str) -> set[Component]:
        return {
            self._components[c] for c in self._neighbors_of.get(component_id, set())
        }

    def get_components(
        self, *, by: str | None = None, value=None, grouped_by: str | None = None
    ):
        if by is None:
            ids = set(self._components)
        elif by == 'side':
            ids = set(self._by_side.get(value, ()))
        elif by == 'family':
            ids = set(self._by_family.get(value, ()))
        elif by == 'id':
            ids = (
                {value} & set(self._components)
                if isinstance(value, str)
                else {v for v in value if v in self._components}
            )
        else:
            raise ValueError(f"Unknown 'by' criterion: {by!r}")

        if grouped_by is None:
            return {self._components[i] for i in ids}

        out: dict[Any, set] = {}
        for i in ids:
            component = self._components[i]
            key = component.side if grouped_by == 'side' else component.family
            out.setdefault(key, set()).add(component)
        return out

    def info(self) -> dict[str, Any]:
        return {
            'by_side': {side: len(ids) for side, ids in self._by_side.items()},
            'by_family': {family: len(ids) for family, ids in self._by_family.items()},
            'total': len(self._components),
        }


def build_components(result: dict[str, Any]) -> Components:
    """Build the typed registry from a ``get_topography`` result dict."""
    raw, dry = result['raw'], result['dry']
    components = Components()
    components.external_links = raw['external_links']
    components.interfaces = dry['interfaces']
    components.motifs = dry['motifs']

    for record in raw['wet_components']:
        component = WetComponent(
            component_id=f'WET-{record["id"]}',
            family=record['family'],
            node_indices=record['tetrahedron_ids'],
            atom_indices=record['atom_indices'],
            center=record['center'],
            flags=record['flags'],
            component_index=record.get('component_index'),
            size_rank=record.get('size_rank'),
            graph_label=record.get('graph_label'),
        )
        component.resident_node_indices = record['resident_tetrahedron_ids']
        component.transit_connector_node_indices = record[
            'transit_connector_tetrahedron_ids'
        ]
        component.external_link_ids = record['external_link_ids']
        component.n_mouths = record['n_external_links']
        component.n_wall_faces = record.get('n_wall_faces', 0)
        component.has_residence = record['has_residence']
        component.has_open_interior = record['has_open_interior']
        component.volume_topological_resident = record['volume_topological_resident']
        component.volume_solvent_estimate = record['volume_solvent_estimate']
        component.raw_record = record
        components.add(component)

    for record in dry['components']:
        component = DryComponent(
            component_id=f'DRY-{record["id"]}',
            node_indices=record['tetrahedron_indices'],
            atom_indices=record['atom_indices'],
            flags=record.get('flags', []),
            component_index=record.get('component_index'),
            size_rank=record.get('size_rank'),
            graph_label=record.get('graph_label'),
        )
        component.interface_ids = record.get('dry_interface_ids', [])
        component.dry_depth_min = record.get('dry_depth_min')
        component.dry_depth_max = record.get('dry_depth_max')
        component.dry_depth_mean = record.get('dry_depth_mean')
        component.raw_record = record
        components.add(component)

    _attach_wet_motifs(components, result)
    _attach_capacity_motifs(components, result)
    return components


def _permeable_adjacency(faces: list[dict[str, Any]]) -> dict[int, set[int]]:
    """Node adjacency through permeable internal faces (the wet/transit graph)."""
    adjacency: dict[int, set[int]] = defaultdict(set)
    for face in faces:
        if face['permeability_state'] != 'permeable':
            continue
        owner, neighbor = face['owner_tetrahedron_id'], face['neighbor_tetrahedron_id']
        if neighbor >= 0:
            adjacency[owner].add(neighbor)
            adjacency[neighbor].add(owner)
    return adjacency


def _connected_components(
    nodes: set[int], adjacency: dict[int, set[int]]
) -> list[list[int]]:
    """Connected components of ``nodes`` under ``adjacency`` (restricted to nodes)."""
    seen: set[int] = set()
    components = []
    for start in nodes:
        if start in seen:
            continue
        stack, group = [start], []
        seen.add(start)
        while stack:
            node = stack.pop()
            group.append(node)
            for neighbor in adjacency.get(node, ()):
                if neighbor in nodes and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(group))
    return components


def _attach_wet_motifs(components: Components, result: dict[str, Any]) -> None:
    """Attach the canonical motif layer to each wet component (component_motifs.md S3):
    topological depth from the external-boundary nodes, depth regions, and the
    ``external_mouth`` realization of each external link. Throat/chamber motifs are
    experimental (need a scoring/persistence policy) and are intentionally omitted.
    """
    raw = result['raw']
    adjacency = _permeable_adjacency(raw['faces'])
    external_links = {link['external_link_id']: link for link in raw['external_links']}
    atoms_by_node = {t['tetrahedron_id']: t['atom_indices'] for t in raw['tetrahedra']}

    for component in components.wet:
        node_set = set(component.node_indices)
        boundary = set()
        for link_id in component.external_link_ids:
            boundary.update(external_links[link_id]['tetrahedron_ids'])
        boundary &= node_set

        depth: dict[int, int] = {}
        if boundary:  # BFS from the exterior boundary
            queue = deque((node, 0) for node in boundary)
            for node in boundary:
                depth[node] = 0
            while queue:
                node, dist = queue.popleft()
                for neighbor in adjacency.get(node, ()):
                    if neighbor in node_set and neighbor not in depth:
                        depth[neighbor] = dist + 1
                        queue.append((neighbor, dist + 1))
        else:  # a void: no exterior reference
            depth = {node: 0 for node in node_set}
        component.topological_depth = depth

        layers: dict[int, set[int]] = defaultdict(set)
        for node, dist in depth.items():
            layers[dist].add(node)
        regions = []
        for dist in sorted(layers):
            for region_nodes in _connected_components(layers[dist], adjacency):
                atom_ids = sorted(
                    {a for node in region_nodes for a in atoms_by_node[node]}
                )
                regions.append(
                    {
                        'motif_type': 'depth_region',
                        'depth': dist,
                        'node_ids': region_nodes,
                        'atom_indices': atom_ids,
                    }
                )
        component.depth_regions = regions

        motifs = [
            {
                'motif_type': 'external_mouth',
                'external_link_id': link_id,
                'atom_indices': external_links[link_id]['atom_indices'],
            }
            for link_id in component.external_link_ids
        ]
        motifs.extend(regions)
        component.motifs = motifs


def _attach_capacity_motifs(
    components: Components, result: dict[str, Any], min_persistence: float = 1.0
) -> None:
    """Attach experimental throat/chamber/bottleneck descriptors to wet components.

    A merge tree is built over the component's internal faces ordered by capacity
    (``R_gate``, descending); when two basins join, the join face is a
    ``throat_candidate`` whose **persistence** is the prominence of the shallower
    basin (its peak ``R_residence`` minus the join capacity). The two basins are
    ``chamber_candidate``s. Throats/chambers are ranked descriptors gated by
    ``min_persistence`` (geometric prominence, in length units); they are NOT a
    probe threshold and NOT a hard classifier (component_motifs.md sections 2/4/6).
    """
    raw = result['raw']
    node_capacity = {t['tetrahedron_id']: t['R_residence'] for t in raw['tetrahedra']}
    atoms_by_node = {t['tetrahedron_id']: t['atom_indices'] for t in raw['tetrahedra']}

    # internal-face capacities per component (face shared by two component nodes)
    edges_by_component: dict[str, dict[tuple[int, int], float]] = defaultdict(dict)
    node_to_component = {}
    for component in components.wet:
        for node in component.node_indices:
            node_to_component[node] = component.component_id
    for face in raw['faces']:
        owner, neighbor = face['owner_tetrahedron_id'], face['neighbor_tetrahedron_id']
        if neighbor < 0:
            continue
        cid = node_to_component.get(owner)
        if cid is None or node_to_component.get(neighbor) != cid:
            continue
        key = (owner, neighbor) if owner < neighbor else (neighbor, owner)
        store = edges_by_component[cid]
        store[key] = max(store.get(key, -1.0), face['R_gate'])

    for component in components.wet:
        edges = edges_by_component.get(component.component_id, {})
        parent = {v: v for v in component.node_indices}
        peak = {v: node_capacity[v] for v in component.node_indices}
        members = {v: {v} for v in component.node_indices}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        throats = []
        chambers_by_peak: dict[int, dict[str, Any]] = {}
        for (a, b), capacity in sorted(edges.items(), key=lambda kv: -kv[1]):
            ra, rb = find(a), find(b)
            if ra == rb:
                continue
            persistence = min(peak[ra], peak[rb]) - capacity
            if persistence >= min_persistence:
                throats.append(
                    {
                        'motif_type': 'throat_candidate',
                        'face_atoms': sorted(
                            set(atoms_by_node[a]) & set(atoms_by_node[b])
                        ),
                        'R_gate': capacity,
                        'persistence': persistence,
                        'flags': ['experimental'],
                    }
                )
                for root in (ra, rb):
                    nodes = members[root]
                    chambers_by_peak[max(nodes, key=lambda n: node_capacity[n])] = {
                        'motif_type': 'chamber_candidate',
                        'peak_R_residence': peak[root],
                        'persistence': persistence,
                        'node_ids': sorted(nodes),
                        'atom_indices': sorted(
                            {at for n in nodes for at in atoms_by_node[n]}
                        ),
                        'flags': ['experimental'],
                    }
            big, small = (ra, rb) if peak[ra] >= peak[rb] else (rb, ra)
            parent[small] = big
            peak[big] = max(peak[ra], peak[rb])
            members[big] |= members[small]

        throats.sort(key=lambda m: -m['persistence'])
        component.throat_candidates = throats
        component.chamber_candidates = list(chambers_by_peak.values())
        component.bottleneck = throats[0] if throats else None
        component.motifs.extend(throats)
        component.motifs.extend(component.chamber_candidates)
