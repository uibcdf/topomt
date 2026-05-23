"""The single ``topography.dfnd`` container.

All DFND-specific substrate lives here, never at the ``Topography`` top level.
The organization follows ``devguide/DFND/object_model.md``:

    topography.dfnd
    ├── raw        # full raw records (provenance)
    ├── mesh       # probe-independent geometry (atoms, tetrahedra, faces)
    └── dfn        # probe-dependent network for one probe
        ├── parameters
        ├── graph        # nodes/faces records + external_links + OCEAN
        └── components   # the decomposition (wet + dry)

Terminology (object_model.md): a *component* is the graph object (set of
tetrahedron nodes); its *domain* is the atoms that realize it; *motifs* are
sub-structures of a domain. The word *feature* is reserved for the public
``Topography`` level and never appears here.

``dfn.components`` is the typed ``Components`` registry (see ``components.py``),
mirroring ``Topography``: a ``Mapping[ComponentID, Component]`` with ``_by_side`` /
``_by_family`` indexes and the same query API. ``mesh`` and ``raw`` remain
structured views over the existing records.
"""

from __future__ import annotations

from typing import Any

from .components import build_components

# A record from graph.py mixes probe-independent geometry with probe-dependent
# state. We split it so `mesh` exposes only geometry (built once, in principle)
# and `dfn.graph` exposes only the per-probe state. `raw` keeps the full records.
_TETRA_GEOMETRY_KEYS = (
    'tetrahedron_id', 'atom_indices', 'local_atom_indices',
    'R_residence', 'residence_candidate_kind', 'R_apollonius4', 'apollonius4_valid',
    'center', 'volume_topological', 'volume_solvent_estimate',
    'solvent_empty_fraction_estimate', 'solvent_occupied_fraction_estimate',
    'solvent_volume_n_samples',
)
_TETRA_STATE_KEYS = (
    'tetrahedron_id', 'residence_margin', 'residence_state', 'transit_role',
    'n_permeable_contacts', 'local_class', 'combined_class', 'flags',
)
_FACE_GEOMETRY_KEYS = (
    'face_id', 'owner_tetrahedron_id', 'neighbor_tetrahedron_id', 'face_index',
    'face_atoms_local', 'atom_indices', 'R_gate',
)
_FACE_STATE_KEYS = (
    'face_id', 'owner_tetrahedron_id', 'neighbor_tetrahedron_id', 'face_index',
    'permeability_state', 'flags',
)


def _project(records: list[dict[str, Any]], keys) -> list[dict[str, Any]]:
    return [{k: record[k] for k in keys if k in record} for record in records]


class MeshAtoms:
    """Vertices of the Delaunay mesh (the dummy/real atoms used by DFND)."""

    def __init__(self, network: Any) -> None:
        self.coords = network.atom_coords            # (N, 3) selected-atom coordinates
        self.radii = network.atom_radii              # (N,)
        self.index_map = network.atom_indices_map    # local index -> global atom index


class Mesh:
    """Probe-independent geometry: atoms, tetrahedra, faces (clearances included).

    Tetrahedron records expose geometry only (atoms, ``R_residence``, volumes);
    the probe-dependent state (residence/transit/permeability) lives in
    ``dfn.graph``. Both sides carry the identity keys for cross-reference.
    """

    def __init__(self, network: Any, raw: dict[str, Any]) -> None:
        self.atoms = MeshAtoms(network)
        self.tetrahedra = _project(raw['tetrahedra'], _TETRA_GEOMETRY_KEYS)
        self.faces = _project(raw['faces'], _FACE_GEOMETRY_KEYS)
        self.delaunay = network.mesh                 # the underlying DelaunayMesh object

    def __repr__(self) -> str:
        return (f"<dfnd.mesh atoms={len(self.atoms.radii)} "
                f"tetrahedra={len(self.tetrahedra)} faces={len(self.faces)}>")


class Graph:
    """The DFN flow graph for one probe: probe-dependent node/face state, OCEAN.

    Geometry (atoms, ``R_residence``, ``R_gate``) lives in ``mesh``; here the
    nodes/faces carry only the per-probe state (residence/transit/permeability),
    plus identity keys to cross-reference the mesh.
    """

    OCEAN = -1

    def __init__(self, raw: dict[str, Any]) -> None:
        self.nodes = _project(raw['tetrahedra'], _TETRA_STATE_KEYS)
        self.faces = _project(raw['faces'], _FACE_STATE_KEYS)
        self.external_links = raw['external_links']  # component -> OCEAN contacts


class DFN:
    """The probe-dependent network for one probe radius."""

    def __init__(self, result: dict[str, Any]) -> None:
        self.parameters = result['raw']['parameters']
        self.graph = Graph(result['raw'])
        self.components = build_components(result)

    def __repr__(self) -> str:
        return (f"<dfnd.dfn probe={self.parameters.get('probe_radius')} "
                f"{self.components!r}>")


class DFNDData:
    """Single ``topography.dfnd`` object holding all DFND substrate."""

    def __init__(self, network: Any, result: dict[str, Any]) -> None:
        self._network = network          # holds the cached, probe-independent mesh
        self.raw = result['raw']
        self.mesh = Mesh(network, result['raw'])
        self.dfn = DFN(result)

    @property
    def network(self) -> Any:
        return self._network

    def at_probe(self, probe_radius: float, **overrides) -> 'DFNDData':
        """Recompute the DFN and components at a new probe, **reusing the mesh**.

        The expensive Delaunay triangulation and the probe-independent clearances
        (``R_residence``, ``R_gate``) live on the cached network and are not
        rebuilt; only the per-probe thresholding, graph and decomposition are
        redone. Returns a new ``DFNDData`` sharing the same network. Unspecified
        query options default to those of the current query.
        """
        parameters = self.raw['parameters']
        result = self._network.get_topography(
            probe_radius=probe_radius,
            sea_level=overrides.get('sea_level', parameters.get('sea_level')),
            min_size=overrides.get('min_size', 0),
            transit_policy=overrides.get('transit_policy', parameters['transit_policy']),
            gate_intrusion_policy=overrides.get(
                'gate_intrusion_policy', parameters['gate_intrusion_policy']),
        )
        return DFNDData(self._network, result)

    def __repr__(self) -> str:
        return f"<DFNDData {self.mesh!r} {self.dfn!r}>"
