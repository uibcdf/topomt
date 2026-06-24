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
from collections import Counter, defaultdict, deque
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
        # Morphology discriminators (the topology->morphology bridge); see
        # _attach_morphometrics and feature_definitions.md.
        self.morphometrics: dict[str, Any] = {}
        # Derived boundary measurements (the grounded boundary layer); see
        # _attach_boundary_helpers and taxonomy_architecture_decision.md.
        self.boundary: dict[str, Any] = {}

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
        self.face_depth_min = None
        self.face_depth_max = None
        self.face_depth_mean = None
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
        component.face_depth_min = record.get('face_depth_min')
        component.face_depth_max = record.get('face_depth_max')
        component.face_depth_mean = record.get('face_depth_mean')
        component.raw_record = record
        components.add(component)

    _attach_interface_labels(components, result)
    _attach_coast_and_lining(components, result, network)
    _attach_wet_motifs(components, result)
    _attach_capacity_motifs(components, result)
    _attach_morphometrics(components, result)
    _attach_boundary_helpers(components, result, network)
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
    components: Components, result: dict[str, Any], min_persistence: float = 0.1
) -> None:
    """Attach the internal sub-chamber hierarchy (a merge tree) to each wet component.

    The component is **not** re-segmented: it stays one probe-connected region,
    preserving the wet-component invariant and avoiding shared-owner ambiguity
    (cf. Q17). Its internal topographic hierarchy is exposed as a descriptor --
    the resolution of L1.3 (nested concavities under a single-scale ``OCEAN``).

    A merge tree is built over the component's internal **transit** faces ordered
    by capacity (``R_gate``, descending). Using ``transit_edge`` rather than raw
    face geometry excludes non-permeable and intrusion-suspect faces by
    construction, so a sliver's spurious wide face cannot forge a throat. Each
    tetrahedron starts as a basin with ``peak = R_residence``; when two basins
    join, the shallower basin's prominence is ``peak - capacity``. A join that
    clears ``min_persistence`` is a ``throat_candidate``; the two basins it
    separates are sibling ``chamber_candidate``s -- symmetric lobes are co-equal
    (same ``separation_radius``), never a forced parent/child. ``min_persistence``
    is only a mesh-noise floor in length units; the physical scale is reported per
    feature as ``separation_radius`` -- the probe radius at which the sub-feature
    detaches from its sibling (the throat ``R_gate``). Throats/chambers are
    provisional: the scoring policy is fixed and toy-validated, real-system
    validation remains for canonical (component_motifs.md sections 2/4/6;
    output_status.py / Q25).
    """
    raw = result['raw']
    node_capacity = {t['tetrahedron_id']: t['R_residence'] for t in raw['tetrahedra']}
    atoms_by_node = {t['tetrahedron_id']: t['atom_indices'] for t in raw['tetrahedra']}

    node_to_component = {}
    for component in components.wet:
        for node in component.node_indices:
            node_to_component[node] = component.component_id

    # internal navigable (transit) faces per component; transit_edge already
    # excludes non-permeable and intrusion-suspect faces, so a sliver cannot
    # forge a throat. Keep the widest face per node pair, with its atoms.
    edges_by_component: dict[
        str, dict[tuple[int, int], tuple[float, list[int]]]
    ] = defaultdict(dict)
    for face in raw['faces']:
        if not face.get('transit_edge'):
            continue
        owner, neighbor = face['owner_tetrahedron_id'], face['neighbor_tetrahedron_id']
        if neighbor < 0:
            continue
        cid = node_to_component.get(owner)
        if cid is None or node_to_component.get(neighbor) != cid:
            continue
        key = (owner, neighbor) if owner < neighbor else (neighbor, owner)
        store = edges_by_component[cid]
        prev = store.get(key)
        if prev is None or face['R_gate'] > prev[0]:
            store[key] = (face['R_gate'], list(face['atom_indices']))

    for component in components.wet:
        edges = edges_by_component.get(component.component_id, {})
        depth = component.topological_depth or {}
        parent = {v: v for v in component.node_indices}
        peak = {v: v for v in component.node_indices}  # basin root -> peak node
        members = {v: {v} for v in component.node_indices}

        def _chamber(peak_node, basin_nodes, separation_radius, comp=component, dep=depth):
            nodes = sorted(basin_nodes)
            chamber_support = support_key([atoms_by_node[n] for n in nodes])
            return {
                'motif_type': 'chamber_candidate',
                'parent_component_key': comp.component_key,
                'motif_support_key': chamber_support,
                'motif_key': motif_key(
                    comp.component_key, 'chamber_candidate', chamber_support
                ),
                'peak_R_residence': node_capacity[peak_node],
                'separation_radius': separation_radius,
                'persistence': node_capacity[peak_node] - separation_radius,
                'topological_depth': min(
                    (dep[n] for n in nodes if n in dep), default=0
                ),
                'node_ids': nodes,
                'atom_indices': sorted({a for n in nodes for a in atoms_by_node[n]}),
                'parent_throat_key': None,
                'flags': ['provisional'],
            }

        chamber_by_peak: dict[int, dict[str, Any]] = {}
        throats = []
        for (a, b), (capacity, face_atom_indices) in sorted(
            edges.items(), key=lambda kv: -kv[1][0]
        ):
            ra, rb = _union_find_root(parent, a), _union_find_root(parent, b)
            if ra == rb:
                continue
            if node_capacity[peak[ra]] >= node_capacity[peak[rb]]:
                hi_root, lo_root = ra, rb
            else:
                hi_root, lo_root = rb, ra
            hi_peak, lo_peak = peak[hi_root], peak[lo_root]
            prominence = node_capacity[lo_peak] - capacity
            if prominence >= min_persistence:
                face_atoms = sorted(
                    set(atoms_by_node[a]) & set(atoms_by_node[b])
                ) or sorted(face_atom_indices)
                throat_support = external_link_support_key([face_atoms])
                throat = {
                    'motif_type': 'throat_candidate',
                    'parent_component_key': component.component_key,
                    'motif_support_key': throat_support,
                    'motif_key': motif_key(
                        component.component_key, 'throat_candidate', throat_support
                    ),
                    'face_atoms': face_atoms,
                    'R_gate': capacity,
                    'separation_radius': capacity,
                    'persistence': prominence,
                    'child_chamber_keys': [],
                    'flags': ['provisional'],
                }
                # both basins are siblings under this throat; keep the first
                # (smallest, highest-capacity) snapshot per peak so a leaf is
                # never swallowed by the growing super-basin.
                lo_chamber = chamber_by_peak.get(lo_peak)
                if lo_chamber is None:
                    lo_chamber = _chamber(lo_peak, members[lo_root], capacity)
                    chamber_by_peak[lo_peak] = lo_chamber
                lo_chamber['parent_throat_key'] = throat['motif_key']
                hi_chamber = chamber_by_peak.get(hi_peak)
                if hi_chamber is None:
                    hi_chamber = _chamber(hi_peak, members[hi_root], capacity)
                    chamber_by_peak[hi_peak] = hi_chamber
                throat['child_chamber_keys'] = [
                    lo_chamber['motif_key'],
                    hi_chamber['motif_key'],
                ]
                throats.append(throat)
            parent[lo_root] = hi_root
            peak[hi_root] = hi_peak
            members[hi_root] |= members[lo_root]

        throats.sort(key=lambda m: -m['persistence'])
        component.throat_candidates = throats
        component.chamber_candidates = list(chamber_by_peak.values())
        component.bottleneck = throats[0] if throats else None
        component.motifs.extend(throats)
        component.motifs.extend(component.chamber_candidates)


def _attach_boundary_helpers(
    components: Components, result: dict[str, Any], network: Any
) -> None:
    """Derived boundary measurements per wet component (the grounded boundary layer).

    The boundary of a wet component partitions into mouths (permeable, to OCEAN)
    and walls (non-permeable). Here we cluster the walls -- *cluster first, then
    characterize* -- with the same edge-adjacency the kernel uses for mouths:

    - ``n_connected_walls`` = number of connected non-permeable boundary clusters.
      It subsumes the binary ``exposed`` flag: ``n_connected_walls == 0`` <=> a
      fully exposed/porous (percolating) component.
    - ``n_dry_contacts`` = distinct dry banks lining the component
      (= ``len(lining_bodies)``); ``interface`` is the catalog predicate
      ``n_dry_contacts >= 2``.

    Each wall is then characterized (*cluster first, characterize after*) by its
    other side: ``coast`` (a dry bank), ``constriction`` (another wet cavity -- a
    closed throat / septum face, S6), or ``exterior`` (a non-permeable OCEAN face).
    ``n_septa`` = walls whose other side is wet (the inter-cavity boundaries whose
    ``R_gate`` is a merge radius). See taxonomy_architecture_decision.md S4/S6.
    """
    raw = result['raw']
    node_component = {}
    node_side = {}
    for component in components.values():
        for node in component.node_indices:
            node_component[node] = component.component_id
            node_side[node] = component.side

    def _face_class(face):
        neighbor = face['neighbor_tetrahedron_id']
        if neighbor < 0:
            return 'exterior'
        side = node_side.get(neighbor)
        return 'coast' if side == 'dry' else ('constriction' if side == 'wet' else 'exterior')

    walls_by_component: dict[str, list] = defaultdict(list)
    for face in raw['faces']:
        if face['permeability_state'] == 'permeable':
            continue  # permeable boundary faces are mouths, not walls
        owner = face['owner_tetrahedron_id']
        cid = node_component.get(owner)
        if cid is None or node_side.get(owner) != 'wet':
            continue
        neighbor = face['neighbor_tetrahedron_id']
        if neighbor >= 0 and node_component.get(neighbor) == cid:
            continue  # internal non-permeable face (same component), not a boundary wall
        walls_by_component[cid].append(face)

    for component in components.wet:
        faces = walls_by_component.get(component.component_id, [])
        clusters = network._cluster_external_faces(faces) if faces else []
        walls = []
        for cluster in clusters:
            composition = Counter(_face_class(f) for f in cluster)
            walls.append(
                {
                    'kind': composition.most_common(1)[0][0],
                    'n_faces': len(cluster),
                    'composition': dict(composition),
                }
            )
        component.boundary = {
            'n_connected_walls': len(clusters),
            'n_dry_contacts': len(component.lining_bodies),
            'n_septa': sum(1 for w in walls if w['kind'] == 'constriction'),
            'walls': walls,
        }


def _attach_morphometrics(components: Components, result: dict[str, Any]) -> None:
    """Attach morphology discriminators to each wet component -- the topology ->
    morphology bridge that the public feature layer (``dfnd_to_topography``,
    feature_definitions.md) uses to refine a topological family (e.g. ``pocket``)
    into a morphological type (groove / occluded pocket / funnel / ...).

    All are assembled from quantities DFND already computes; none introduces a new
    geometric primitive:

    - ``mouth_radius``    -- the widest aperture (max external-link ``R_gate_max``).
      It is the **seal radius**: the probe radius above which every mouth face
      closes and the cavity becomes an enclosed void.
    - ``interior_radius`` -- the widest interior clearance (max ``R_residence`` over
      the resident nodes). It is the **residence-death radius**: the largest probe
      that still resides; above it there is no residence.
    - ``occlusion``       -- ``interior_radius / mouth_radius``. ``<=1`` is an open
      groove/dent (the mouth is at the widest point, clearance only narrows inward,
      so the cavity loses residence and mouth together and never becomes a void);
      ``>1`` narrows at the mouth and widens inside (the enclosed / "druggable"
      kind -- the interior holds the probe after the mouth has sealed).
    - ``occlusion_gap``   -- ``interior_radius - mouth_radius`` in length units: the
      width of the probe-radius window in which this cavity exists as an enclosed
      **void** (mouth sealed, residence alive). This is the probe sweep's
      pocket -> void interval, compressed -- no sweep is run because ``R_residence``
      and ``R_gate`` are probe-independent, so the endpoints are read directly.
    - ``enclosable``      -- ``occlusion_gap > 0``: becomes a void as the probe grows
      (the robust groove vs occluded-pocket discriminator).
    - ``buriedness``      -- the deepest residence depth from the mouth
      (max ``topological_depth``).

    These are descriptors only; the morphological *naming* and its thresholds are
    a public-layer policy, deliberately not fixed here. Note the global ratio can
    miss a deep narrow sub-pocket behind a wide mouth; the merge-tree hierarchy and
    the depth-ordered access profile cover that compound case.
    """
    raw = result['raw']
    node_residence = {t['tetrahedron_id']: t['R_residence'] for t in raw['tetrahedra']}
    links = {link['external_link_id']: link for link in raw['external_links']}

    for component in components.wet:
        resident_nodes = getattr(
            component, 'resident_node_indices', None
        ) or component.node_indices
        interior_radius = max(
            (node_residence[n] for n in resident_nodes if n in node_residence),
            default=0.0,
        )
        mouth_radii = [
            links[lid]['R_gate_max']
            for lid in component.external_link_ids
            if lid in links
        ]
        mouth_radius = max(mouth_radii) if mouth_radii else None
        buriedness = max((component.topological_depth or {}).values(), default=0)
        if mouth_radius and mouth_radius > 0.0:
            occlusion = interior_radius / mouth_radius
            occlusion_gap = interior_radius - mouth_radius
            enclosable = occlusion_gap > 0.0
        else:  # no mouth (a void): already enclosed
            occlusion = None
            occlusion_gap = None
            enclosable = None
        # Compound morphology (a deep narrow sub-pocket behind a wide mouth that the
        # global ratio misses): read it off the merge-tree hierarchy instead of a
        # new traversal. The deepest sub-chamber sits behind the throat it merges
        # through; ``access_occlusion = peak / separation_radius > 1`` means the
        # route to it narrows (a buried sub-site). A groove has no chambers -> None.
        chambers = component.chamber_candidates
        if chambers:
            deepest = max(chambers, key=lambda c: c['topological_depth'])
            sep = deepest['separation_radius']
            deepest_chamber = {
                'topological_depth': deepest['topological_depth'],
                'peak_R_residence': deepest['peak_R_residence'],
                'separation_radius': sep,
                'access_occlusion': (
                    deepest['peak_R_residence'] / sep if sep and sep > 0.0 else None
                ),
            }
        else:
            deepest_chamber = None

        component.morphometrics = {
            'mouth_radius': mouth_radius,
            'interior_radius': interior_radius,
            'occlusion': occlusion,
            'occlusion_gap': occlusion_gap,
            'enclosable': enclosable,
            'buriedness': buriedness,
            'deepest_chamber': deepest_chamber,
        }
