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

import copy
from collections import defaultdict, deque
from collections.abc import Iterator, Mapping
from typing import Any

# side is derived from family (single source of truth in families.py), exactly as
# feature shape/dimensionality are derived from feature_type in _feature_constants.
from . import families as fam
from .identity import external_link_support_key, motif_key, support_key

_SIDE_BY_FAMILY = fam.SIDE_BY_FAMILY
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
        node_count_rank=None,
        size_rank=None,
        graph_label=None,
        support_key=None,
        component_key=None,
        tetrahedron_support=None,
    ):
        self._component_id = component_id
        self.component_index = component_index
        self.node_count_rank = node_count_rank
        self.size_rank = size_rank
        self.graph_label = graph_label
        self.support_key = support_key
        self.component_key = component_key
        self.tetrahedron_support = (
            [tuple(item) for item in tetrahedron_support]
            if tetrahedron_support is not None
            else []
        )
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
    def component_id(self):
        return self._component_id

    @component_id.setter
    def component_id(self, value):
        if self._components is not None and value != self._component_id:
            raise AttributeError(
                'component_id is immutable while registered; use Components.rename().'
            )
        self._component_id = value

    def _set_registered_component_id(self, value: str) -> None:
        self._component_id = value

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
        self.external_link_keys: list[str] = []
        self.n_mouths = 0
        self.n_wall_faces = 0
        self.has_residence = False
        self.has_open_interior = False
        self.volume_topological_resident = None
        self.volume_solvent_estimate = None
        # interface descriptor (orthogonal axis, see devguide/DFND/interfaces.md):
        # set when the component's lining is contributed by >=2 dry banks. ``family``
        # stays the mouth-topology family; ``interface_family`` is the cross-product
        # label (interface_pocket / interface_void / …). ``lining_bodies`` names the
        # dry banks (DRY-ids) that line it.
        self.is_interface = False
        self.interface_family: str | None = None
        self.lining_bodies: list[str] = []
        self.lining_body_split: dict[int, int] = {}
        # wet/dry adjacency (layer 2): the dry banks that line this wet component,
        # keyed by DRY-id -> {tetrahedron_ids (the dry wall tetrahedra),
        # contact_face_ids (the coast faces), area}. See devguide/DFND/interfaces.md.
        self.dry_lining: dict[str, dict[str, Any]] = {}
        # Canonical and experimental wet-component motifs.
        self.topological_depth: dict[int, int] = {}
        self.depth_regions: list[dict[str, Any]] = []
        self.throat_candidates: list[dict[str, Any]] = []
        self.chamber_candidates: list[dict[str, Any]] = []
        self.bottleneck: dict[str, Any] | None = None

    def __repr__(self) -> str:
        tag = f' {self.interface_family}' if self.is_interface else ''
        return (
            f'<{type(self).__name__} {self.component_id} '
            f'family={self.family}{tag} nodes={self.size} '
            f'atoms={len(self.atom_indices)}>'
        )


class DryComponent(Component):
    """A dry bank (the dry-network side of the decomposition)."""

    def __init__(self, **kwargs):
        kwargs.pop('family', None)
        super().__init__(family=fam.DRY_BANK, **kwargs)
        self.interface_ids: list[int] = []
        self.neighbor_component_ids: list[str] = []
        self.dry_depth_min = None
        self.dry_depth_max = None
        self.dry_depth_mean = None
        self.motif_ids: list[int] = []
        self.motif_keys: list[str] = []
        # wet/dry adjacency (layer 2): the wet components this bank lines, keyed by
        # WET-id -> {tetrahedron_ids (the wet tetrahedra it borders),
        # contact_face_ids, area}. The symmetric counterpart of
        # ``WetComponent.dry_lining``.
        self.wet_lining: dict[str, dict[str, Any]] = {}

    @property
    def interface_walls(self) -> dict[str, dict[str, Any]]:
        """The subset of ``wet_lining`` facing wet *interface* components (layer 3).

        Named view, no extra computation: the bank's wall against each wet region
        that is itself an interface. Closes the symmetry with
        ``WetComponent.lining_bodies``.
        """
        if self._components is None:
            return {}
        return {
            wet_id: wall
            for wet_id, wall in self.wet_lining.items()
            if getattr(self._components.get(wet_id), 'is_interface', False)
        }


class Components(Mapping):
    """Registry of components for one probe (mirrors ``Topography``)."""

    def __init__(self) -> None:
        self._components: dict[str, Component] = {}
        self._by_side: dict[str, set[str]] = {'wet': set(), 'dry': set()}
        self._by_family: dict[str, set[str]] = {}
        self._by_key: dict[str, str] = {}
        self._neighbors_of: dict[str, set[str]] = {}
        # boundary relations (raw records; components reference them by id)
        self.external_links: list[dict[str, Any]] = []  # wet component -> OCEAN
        self.interfaces: list[dict[str, Any]] = []  # dry <-> dry
        self.motifs: list[dict[str, Any]] = []  # dry-side motifs (wet pending)
        self.coast_faces: list[dict[str, Any]] = []  # wet<->dry contact faces (layer 1)

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
    @staticmethod
    def _validate_component_id(component_id: str) -> None:
        if not isinstance(component_id, str):
            raise TypeError('component_id must be a string')
        if not component_id:
            raise ValueError('component_id must not be empty')

    def _validate_new_component(
        self, component: Component, *, allowed_id: str | None = None
    ) -> str:
        if not isinstance(component, Component):
            raise TypeError('component must be a Component')
        component_id = component.component_id
        self._validate_component_id(component_id)
        if component.side not in {'wet', 'dry'}:
            raise ValueError(f'Unknown component family: {component.family!r}')
        if component._components is not None and component._components is not self:
            raise ValueError('Component belongs to a different Components registry.')
        if component_id in self._components and component_id != allowed_id:
            raise ValueError(f"Component ID '{component_id}' is already registered.")
        if component.component_key is not None:
            owner_id = self._by_key.get(component.component_key)
            if owner_id is not None and owner_id != allowed_id:
                raise ValueError(
                    f"Component key '{component.component_key}' is already registered."
                )
        return component_id

    def _add_to_indexes(self, component: Component) -> None:
        self._by_side.setdefault(component.side, set()).add(component.component_id)
        self._by_family.setdefault(component.family, set()).add(component.component_id)
        if component.component_key is not None:
            self._by_key[component.component_key] = component.component_id

    def _remove_from_indexes(self, component: Component) -> None:
        self._by_side.get(component.side, set()).discard(component.component_id)
        self._by_family.get(component.family, set()).discard(component.component_id)
        if component.component_key is not None:
            self._by_key.pop(component.component_key, None)

    def add(self, component: Component) -> str:
        if (
            isinstance(component, Component)
            and component.component_id in self._components
            and self._components[component.component_id] is component
        ):
            return component.component_id
        component_id = self._validate_new_component(component)
        self._components[component_id] = component
        component._components = self
        self._add_to_indexes(component)
        self._neighbors_of.setdefault(component_id, set())
        return component_id

    def replace(self, component_id: str, component: Component) -> Component:
        """Atomically replace one component while preserving its relations."""
        self._validate_component_id(component_id)
        if component_id not in self._components:
            raise KeyError(component_id)
        replacement_id = self._validate_new_component(
            component, allowed_id=component_id
        )
        if replacement_id != component_id:
            raise ValueError('Replacement component_id must match the registered ID.')
        previous = self._components[component_id]
        if component is previous:
            return previous
        self._remove_from_indexes(previous)
        self._components[component_id] = component
        component._components = self
        self._add_to_indexes(component)
        previous._components = None
        return previous

    def rename(self, component_id: str, new_component_id: str) -> None:
        """Atomically rename a registered component and registry references."""
        self._validate_component_id(component_id)
        self._validate_component_id(new_component_id)
        if component_id not in self._components:
            raise KeyError(component_id)
        if new_component_id in self._components:
            raise ValueError(
                f"Component ID '{new_component_id}' is already registered."
            )
        if component_id == new_component_id:
            return
        component = self._components[component_id]
        self._components = {
            (new_component_id if key == component_id else key): value
            for key, value in self._components.items()
        }
        for ids in (*self._by_side.values(), *self._by_family.values()):
            if component_id in ids:
                ids.remove(component_id)
                ids.add(new_component_id)
        self._neighbors_of = {
            (new_component_id if key == component_id else key): {
                new_component_id if neighbor == component_id else neighbor
                for neighbor in neighbors
            }
            for key, neighbors in self._neighbors_of.items()
        }
        component._set_registered_component_id(new_component_id)
        if component.component_key is not None:
            self._by_key[component.component_key] = new_component_id
        self._rename_references(component_id, new_component_id)

    def remove(self, component_id: str) -> Component:
        """Atomically remove a component and clean registry-owned relations."""
        self._validate_component_id(component_id)
        if component_id not in self._components:
            raise KeyError(component_id)
        component = self._components.pop(component_id)
        self._remove_from_indexes(component)
        self._neighbors_of.pop(component_id, None)
        for neighbors in self._neighbors_of.values():
            neighbors.discard(component_id)
        self._remove_references(component_id)
        component._components = None
        return component

    def copy(self, deep: bool = True):
        """Return a semantic registry copy with correctly rebound components."""
        if deep:
            return copy.deepcopy(self)
        copied = copy.copy(self)
        copied._components = {}
        for component_id, component in self._components.items():
            new_component = copy.copy(component)
            new_component._components = copied
            copied._components[component_id] = new_component
        copied._by_side = {key: set(value) for key, value in self._by_side.items()}
        copied._by_family = {key: set(value) for key, value in self._by_family.items()}
        copied._by_key = dict(self._by_key)
        copied._neighbors_of = {
            key: set(value) for key, value in self._neighbors_of.items()
        }
        return copied

    def connect(self, component_id_a: str, component_id_b: str) -> None:
        """Record a boundary adjacency between two registered components."""
        self._validate_component_id(component_id_a)
        self._validate_component_id(component_id_b)
        for component_id in (component_id_a, component_id_b):
            if component_id not in self._components:
                raise KeyError(component_id)
        self._neighbors_of[component_id_a].add(component_id_b)
        self._neighbors_of[component_id_b].add(component_id_a)

    def _rename_references(self, old_id: str, new_id: str) -> None:
        for component in self._components.values():
            if isinstance(component, WetComponent):
                if old_id in component.dry_lining:
                    component.dry_lining[new_id] = component.dry_lining.pop(old_id)
                component.lining_bodies = [
                    new_id if value == old_id else value
                    for value in component.lining_bodies
                ]
            if isinstance(component, DryComponent):
                if old_id in component.wet_lining:
                    component.wet_lining[new_id] = component.wet_lining.pop(old_id)
                component.neighbor_component_ids = [
                    new_id if value == old_id else value
                    for value in component.neighbor_component_ids
                ]
        for face in self.coast_faces:
            for field in ('wet_component_id', 'dry_component_id'):
                if face.get(field) == old_id:
                    face[field] = new_id

    def _remove_references(self, component_id: str) -> None:
        for component in self._components.values():
            if isinstance(component, WetComponent):
                component.dry_lining.pop(component_id, None)
                component.lining_bodies = [
                    value for value in component.lining_bodies if value != component_id
                ]
            if isinstance(component, DryComponent):
                component.wet_lining.pop(component_id, None)
                component.neighbor_component_ids = [
                    value
                    for value in component.neighbor_component_ids
                    if value != component_id
                ]
        self.coast_faces = [
            face
            for face in self.coast_faces
            if face.get('wet_component_id') != component_id
            and face.get('dry_component_id') != component_id
        ]

    # -- views (insertion order) --
    @property
    def wet(self) -> list[Component]:
        return [c for c in self._components.values() if c.side == 'wet']

    @property
    def dry(self) -> list[Component]:
        return [c for c in self._components.values() if c.side == 'dry']

    @property
    def wet_interfaces(self) -> list[Component]:
        """Wet components flagged as interfaces (lining spans >=2 dry banks)."""
        return [c for c in self.wet if getattr(c, 'is_interface', False)]

    def by_family(self, family: str) -> list[Component]:
        return [c for c in self._components.values() if c.family == family]

    @property
    def surface_concavities(self) -> list[Component]:
        return self.by_family(fam.SURFACE_CONCAVITY)

    @property
    def nonresident_passages(self) -> list[Component]:
        return self.by_family(fam.NONRESIDENT_PASSAGE)

    @property
    def degenerate_subprobes(self) -> list[Component]:
        return self.by_family(fam.DEGENERATE_SUBPROBE)

    # -- lookups (≡ Topography) --
    def get_component_by_id(self, component_id: str) -> Component:
        return self._components[component_id]

    def get_component_by_key(self, component_key: str) -> Component:
        return self._components[self._by_key[component_key]]

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
        elif by == 'key':
            values = {value} if isinstance(value, str) else set(value)
            ids = {self._by_key[key] for key in values if key in self._by_key}
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


def build_components(result: dict[str, Any], network: Any = None) -> Components:
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
            node_count_rank=record.get('node_count_rank'),
            size_rank=record.get('size_rank'),
            graph_label=record.get('graph_label'),
            support_key=record.get('support_key'),
            component_key=record.get('component_key'),
            tetrahedron_support=record.get('tetrahedron_support'),
        )
        component.resident_node_indices = record['resident_tetrahedron_ids']
        component.transit_connector_node_indices = record[
            'transit_connector_tetrahedron_ids'
        ]
        component.external_link_ids = record['external_link_ids']
        component.external_link_keys = record.get('external_link_keys', [])
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
            node_count_rank=record.get('node_count_rank'),
            size_rank=record.get('size_rank'),
            graph_label=record.get('graph_label'),
            support_key=record.get('support_key'),
            component_key=record.get('component_key'),
            tetrahedron_support=record.get('tetrahedron_support'),
        )
        component.interface_ids = record.get('dry_interface_ids', [])
        component.motif_ids = record.get('dry_motif_ids', [])
        component.motif_keys = record.get('motif_keys', [])
        component.dry_depth_min = record.get('dry_depth_min')
        component.dry_depth_max = record.get('dry_depth_max')
        component.dry_depth_mean = record.get('dry_depth_mean')
        component.raw_record = record
        components.add(component)

    _attach_interface_labels(components, result)
    _attach_coast_and_lining(components, result, network)
    _attach_wet_motifs(components, result)
    _attach_capacity_motifs(components, result)
    return components


def _attach_coast_and_lining(
    components: Components, result: dict[str, Any], network: Any
) -> None:
    """Materialize the wet<->dry contact and the per-component lining (layers 1-2).

    A *coast face* is an internal face whose two tetrahedra belong to components of
    opposite side (one wet, one dry). From the coast we fill, symmetrically, each
    ``WetComponent.dry_lining`` (the dry banks lining it) and each
    ``DryComponent.wet_lining`` (the wet regions it lines), each carrying the
    bordering tetrahedra, the contact face ids and the contact area. Areas need
    coordinates; with ``network is None`` they are left at 0.0.
    """
    raw = result['raw']
    atom_coords = getattr(network, 'atom_coords', None)
    triangle_area = None
    if atom_coords is not None:
        from topomt.tools.tessellation.mouths import triangle_area as _triangle_area

        triangle_area = _triangle_area

    node_to_component: dict[int, str] = {}
    for component in components.wet:
        for node in component.node_indices:
            node_to_component[node] = component.component_id
    for component in components.dry:
        for node in component.node_indices:
            node_to_component[node] = component.component_id

    def _slot(store: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
        return store.setdefault(
            key,
            {'tetrahedron_ids': set(), 'contact_face_ids': set(), 'area': 0.0},
        )

    coast: list[dict[str, Any]] = []
    seen_faces: set[int] = set()
    for face in raw['faces']:
        owner = face['owner_tetrahedron_id']
        neighbor = face['neighbor_tetrahedron_id']
        if neighbor is None or neighbor < 0:
            continue
        # each internal face is listed in both orientations (same face_id); keep one
        # so the coast and the lining areas are not double-counted.
        if face['face_id'] in seen_faces:
            continue
        seen_faces.add(face['face_id'])
        owner_cid = node_to_component.get(owner)
        neighbor_cid = node_to_component.get(neighbor)
        if owner_cid is None or neighbor_cid is None:
            continue
        owner_side = components[owner_cid].side
        if owner_side == components[neighbor_cid].side:
            continue  # same side -> not a coast face
        if owner_side == 'wet':
            wet_t, dry_t, wet_cid, dry_cid = owner, neighbor, owner_cid, neighbor_cid
        else:
            wet_t, dry_t, wet_cid, dry_cid = neighbor, owner, neighbor_cid, owner_cid

        area = 0.0
        if triangle_area is not None and face.get('face_atoms_local'):
            area = float(triangle_area(atom_coords[face['face_atoms_local']]))

        coast.append(
            {
                'face_id': face['face_id'],
                'wet_tetrahedron_id': wet_t,
                'dry_tetrahedron_id': dry_t,
                'wet_component_id': wet_cid,
                'wet_component_key': components[wet_cid].component_key,
                'dry_component_id': dry_cid,
                'dry_component_key': components[dry_cid].component_key,
                'atom_indices': face['atom_indices'],
                'area': area,
                'R_gate': face.get('R_gate'),
                'permeability_state': face.get('permeability_state'),
            }
        )

        wall = _slot(components[wet_cid].dry_lining, dry_cid)
        wall['component_key'] = components[dry_cid].component_key
        wall['tetrahedron_ids'].add(dry_t)
        wall['contact_face_ids'].add(face['face_id'])
        wall['area'] += area

        lining = _slot(components[dry_cid].wet_lining, wet_cid)
        lining['component_key'] = components[wet_cid].component_key
        lining['tetrahedron_ids'].add(wet_t)
        lining['contact_face_ids'].add(face['face_id'])
        lining['area'] += area

    for component in components.wet:
        for entry in component.dry_lining.values():
            entry['tetrahedron_ids'] = sorted(entry['tetrahedron_ids'])
            entry['contact_face_ids'] = sorted(entry['contact_face_ids'])
    for component in components.dry:
        for entry in component.wet_lining.values():
            entry['tetrahedron_ids'] = sorted(entry['tetrahedron_ids'])
            entry['contact_face_ids'] = sorted(entry['contact_face_ids'])
    components.coast_faces = coast


def _attach_interface_labels(components: Components, result: dict[str, Any]) -> None:
    """Tag each wet component as an interface when its lining spans >=2 dry banks.

    Native (label-free) route of ``interfaces.py``: bodies are the dry banks. The
    ``family`` (mouth topology) is untouched; this only adds the orthogonal
    interface descriptor (``is_interface`` / ``interface_family`` / lining split /
    the DRY banks it interfaces). See devguide/DFND/interfaces.md §2-3.
    """
    from . import interfaces as ifc

    dry_components = result['dry']['components']
    if len(dry_components) < 2:
        return  # an interface needs at least two banks

    max_atom = -1
    for record in dry_components:
        if record['atom_indices']:
            max_atom = max(max_atom, max(record['atom_indices']))
    for record in result['raw']['wet_components']:
        if record['atom_indices']:
            max_atom = max(max_atom, max(record['atom_indices']))
    if max_atom < 0:
        return

    body_labels = ifc.body_labels_from_dry_components(result, max_atom + 1)
    classified = ifc.classify_interface_components(
        result['raw']['wet_components'], body_labels
    )
    # body ids are dry banks ranked by size (mirrors body_labels_from_dry_components)
    ranked = sorted(
        (c for c in dry_components if c['size'] >= 1),
        key=lambda c: c['size'],
        reverse=True,
    )
    body_to_bank = {i: f'DRY-{record["id"]}' for i, record in enumerate(ranked)}
    by_wet_id = {record['component_id']: record for record in classified}

    for component in components.wet:
        wet_id = int(component.component_id.split('-')[1])
        record = by_wet_id.get(wet_id)
        if record is None:
            continue
        component.is_interface = bool(record['is_interface'])
        component.lining_body_split = dict(record['lining_body_split'])
        if component.is_interface:
            component.interface_family = record['interface_family']
            component.lining_bodies = sorted(
                body_to_bank[b]
                for b in record['lining_body_split']
                if b in body_to_bank
            )


def _permeable_adjacency(faces: list[dict[str, Any]]) -> dict[int, set[int]]:
    """Node adjacency through permeable internal faces (the wet/transit graph)."""
    adjacency: dict[int, set[int]] = defaultdict(set)
    for face in faces:
        if not face.get('transit_edge', face['permeability_state'] == 'permeable'):
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
                motif_support = support_key(
                    [atoms_by_node[node] for node in region_nodes]
                )
                regions.append(
                    {
                        'motif_type': 'depth_region',
                        'parent_component_key': component.component_key,
                        'motif_support_key': motif_support,
                        'motif_key': motif_key(
                            component.component_key, 'depth_region', motif_support
                        ),
                        'depth': dist,
                        'node_ids': region_nodes,
                        'atom_indices': atom_ids,
                    }
                )
        component.depth_regions = regions

        motifs = [
            {
                'motif_type': 'external_mouth',
                'parent_component_key': component.component_key,
                'motif_support_key': external_links[link_id][
                    'external_link_support_key'
                ],
                'motif_key': motif_key(
                    component.component_key,
                    'external_mouth',
                    external_links[link_id]['external_link_support_key'],
                ),
                'external_link_id': link_id,
                'external_link_key': external_links[link_id]['external_link_key'],
                'atom_indices': external_links[link_id]['atom_indices'],
            }
            for link_id in component.external_link_ids
        ]
        motifs.extend(regions)
        component.motifs = motifs


def _union_find_root(parent: dict[int, int], node: int) -> int:
    while parent[node] != node:
        parent[node] = parent[parent[node]]
        node = parent[node]
    return node


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

        throats = []
        chambers_by_peak: dict[int, dict[str, Any]] = {}
        for (a, b), capacity in sorted(edges.items(), key=lambda kv: -kv[1]):
            ra, rb = _union_find_root(parent, a), _union_find_root(parent, b)
            if ra == rb:
                continue
            persistence = min(peak[ra], peak[rb]) - capacity
            if persistence >= min_persistence:
                face_atoms = sorted(set(atoms_by_node[a]) & set(atoms_by_node[b]))
                throat_support = external_link_support_key([face_atoms])
                throats.append(
                    {
                        'motif_type': 'throat_candidate',
                        'parent_component_key': component.component_key,
                        'motif_support_key': throat_support,
                        'motif_key': motif_key(
                            component.component_key,
                            'throat_candidate',
                            throat_support,
                        ),
                        'face_atoms': face_atoms,
                        'R_gate': capacity,
                        'persistence': persistence,
                        'flags': ['experimental'],
                    }
                )
                for root in (ra, rb):
                    nodes = members[root]
                    chamber_support = support_key(
                        [atoms_by_node[node] for node in nodes]
                    )
                    chambers_by_peak[max(nodes, key=lambda n: node_capacity[n])] = {
                        'motif_type': 'chamber_candidate',
                        'parent_component_key': component.component_key,
                        'motif_support_key': chamber_support,
                        'motif_key': motif_key(
                            component.component_key,
                            'chamber_candidate',
                            chamber_support,
                        ),
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
