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
tetrahedron nodes) together with its *spatial representation* (the atoms that
realize it, volume, center); *motifs* are sub-structures of a component. The word
*feature* is reserved for the public ``Topography`` level and never appears here.

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
    'tetrahedron_id',
    'atom_indices',
    'local_atom_indices',
    'R_residence',
    'residence_candidate_kind',
    'R_apollonius4',
    'apollonius4_valid',
    'center',
    'volume_topological',
    'volume_solvent_estimate',
    'solvent_empty_fraction_estimate',
    'solvent_occupied_fraction_estimate',
    'solvent_volume_n_samples',
)
_TETRA_STATE_KEYS = (
    'tetrahedron_id',
    'residence_margin',
    'residence_state',
    'transit_role',
    'n_permeable_contacts',
    'local_class',
    'combined_class',
    'flags',
)
_FACE_GEOMETRY_KEYS = (
    'face_id',
    'owner_tetrahedron_id',
    'neighbor_tetrahedron_id',
    'face_index',
    'face_atoms_local',
    'atom_indices',
    'R_gate',
)
_FACE_STATE_KEYS = (
    'face_id',
    'owner_tetrahedron_id',
    'neighbor_tetrahedron_id',
    'face_index',
    'permeability_state',
    'flags',
)


def _project(records: list[dict[str, Any]], keys) -> list[dict[str, Any]]:
    return [{k: record[k] for k in keys if k in record} for record in records]


class MeshAtoms:
    """Vertices of the Delaunay mesh (the dummy/real atoms used by DFND)."""

    def __init__(self, network: Any) -> None:
        self.coords = network.atom_coords  # (N, 3) selected-atom coordinates
        self.radii = network.atom_radii  # (N,)
        self.index_map = network.atom_indices_map  # local index -> global atom index


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
        self.delaunay = network.mesh  # the underlying DelaunayMesh object

    def neighbors(self, tetrahedron_id: int, *, include_ocean: bool = False) -> list[int]:
        """Bare face-neighbors of a tetrahedron (probe-independent topology).

        Each tetrahedron borders up to four others across its faces; ``-1`` marks a
        face on the convex hull (the OCEAN side). Reads the single shared adjacency
        array (``delaunay.neighbors``) -- the topology is not duplicated per record.
        The probe-dependent wet/dry split lives in ``dfn.graph.neighbors``.
        """
        row = self.delaunay.neighbors[int(tetrahedron_id)]
        return [int(n) for n in row if include_ocean or int(n) != -1]

    def __repr__(self) -> str:
        return (
            f'<dfnd.mesh atoms={len(self.atoms.radii)} '
            f'tetrahedra={len(self.tetrahedra)} faces={len(self.faces)}>'
        )


class Graph:
    """The DFN flow graph for one probe: probe-dependent node/face state, OCEAN.

    Geometry (atoms, ``R_residence``, ``R_gate``) lives in ``mesh``; here the
    nodes/faces carry only the per-probe state (residence/transit/permeability),
    plus identity keys to cross-reference the mesh.
    """

    OCEAN = -1

    _WET_STATE = 'resident'
    _DRY_STATE = 'non_resident'

    def __init__(self, raw: dict[str, Any], adjacency: Any = None) -> None:
        self.nodes = _project(raw['tetrahedra'], _TETRA_STATE_KEYS)
        self.faces = _project(raw['faces'], _FACE_STATE_KEYS)
        self.external_links = raw['external_links']  # component -> OCEAN contacts
        # Shared (N, 4) face-adjacency array (probe-independent), kept by reference
        # so the wet/dry-aware neighbor query does not duplicate the topology.
        self._adjacency = adjacency
        self._state_by_id = {
            node['tetrahedron_id']: node.get('residence_state') for node in self.nodes
        }

    def neighbors(self, node_id: int, side: str | None = None) -> list[int]:
        """Face-neighbors of a node, optionally filtered by ``side``.

        ``side=None`` returns every (non-OCEAN) neighbor; ``side='wet'`` keeps only
        resident neighbors and ``side='dry'`` only non-resident ones. This is the
        probe-dependent counterpart of ``mesh.neighbors`` -- it answers "which dry
        tetrahedra border this wet one" (and vice versa) in one call.
        """
        if self._adjacency is None:
            raise RuntimeError(
                "Graph has no adjacency; build it via DFN(result, network)."
            )
        if side not in (None, 'wet', 'dry'):
            raise ValueError("side must be None, 'wet' or 'dry'")
        ids = [int(n) for n in self._adjacency[int(node_id)] if int(n) != self.OCEAN]
        if side is None:
            return ids
        want = self._WET_STATE if side == 'wet' else self._DRY_STATE
        return [i for i in ids if self._state_by_id.get(i) == want]


class DFN:
    """The probe-dependent network for one probe radius."""

    def __init__(self, result: dict[str, Any], network: Any = None) -> None:
        self.parameters = result['raw']['parameters']
        adjacency = getattr(network, 'simplex_neighbors', None)
        self.graph = Graph(result['raw'], adjacency=adjacency)
        self.components = build_components(result, network)

    def __repr__(self) -> str:
        return (
            f'<dfnd.dfn probe={self.parameters.get("probe_radius")} '
            f'{self.components!r}>'
        )


class DFNDData:
    """Single ``topography.dfnd`` object holding all DFND substrate."""

    def __init__(self, network: Any, result: dict[str, Any]) -> None:
        self._network = network  # holds the cached, probe-independent mesh
        self.raw = result['raw']
        self.mesh = Mesh(network, result['raw'])
        self.dfn = DFN(result, network)

    @property
    def network(self) -> Any:
        return self._network

    def get_tetrahedra(
        self, tetrahedron_ids: Any = None, **filters
    ) -> list[dict[str, Any]]:
        """Return raw tetrahedron records matching ids and optional filters."""
        from .selectors import select_tetrahedra

        return select_tetrahedra(
            self,
            tetrahedron_ids=tetrahedron_ids,
            **filters,
        )

    def get_tetrahedron(self, tetrahedron_id: int) -> dict[str, Any]:
        """Return one raw tetrahedron record by ``tetrahedron_id``."""
        records = self.get_tetrahedra(tetrahedron_id)
        if not records:
            raise KeyError(f'Tetrahedron ID {tetrahedron_id} not found.')
        return records[0]

    def at_probe(self, probe_radius: float, **overrides) -> DFNDData:
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
            transit_policy=overrides.get(
                'transit_policy', parameters['transit_policy']
            ),
            gate_intrusion_policy=overrides.get(
                'gate_intrusion_policy', parameters['gate_intrusion_policy']
            ),
            residence_tolerance=overrides.get(
                'residence_tolerance', parameters.get('residence_tolerance', 0.0)
            ),
            permeability_tolerance=overrides.get(
                'permeability_tolerance', parameters.get('permeability_tolerance', 0.0)
            ),
        )
        return DFNDData(self._network, result)

    def info(self, tetrahedron_id: Any = None) -> None:
        """Print a premium scientific diagnostic card for one or several Delaunay tetrahedra."""
        import molsysmt as msm
        import numpy as np

        tetrahedra_list = self.raw.get('tetrahedra', [])
        if not tetrahedra_list:
            print('No Delaunay tetrahedra found in this topography.')
            return

        if tetrahedron_id is None:
            print(f'Topography has {len(tetrahedra_list)} Delaunay tetrahedra.')
            print(
                'Please specify a tetrahedron_id (e.g., topography.dfnd.info(0)) to see its detailed diagnostic card.'
            )
            return

        if isinstance(tetrahedron_id, (int, np.integer)):
            target_ids = [int(tetrahedron_id)]
        else:
            try:
                target_ids = [int(x) for x in tetrahedron_id]
            except Exception:
                target_ids = [int(tetrahedron_id)]

        mol_sys = getattr(self._network, 'molecular_system', None)

        for tid in target_ids:
            tet_rec = None
            for idx, t in enumerate(tetrahedra_list):
                if t.get('tetrahedron_id', idx) == tid:
                    tet_rec = t
                    break

            if not tet_rec:
                print(f'Error: Tetrahedron ID {tid} not found.')
                continue

            orig_atoms = tet_rec.get('local_atom_indices', [])
            residue_details = []
            if mol_sys is not None:
                try:
                    atom_names = msm.get(mol_sys, selection=orig_atoms, atom_name=True)
                    res_names = msm.get(
                        mol_sys, selection=orig_atoms, residue_name=True
                    )
                    res_ids = msm.get(mol_sys, selection=orig_atoms, residue_id=True)

                    if not isinstance(atom_names, (list, tuple, np.ndarray)):
                        atom_names = [atom_names]
                    if not isinstance(res_names, (list, tuple, np.ndarray)):
                        res_names = [res_names]
                    if not isinstance(res_ids, (list, tuple, np.ndarray)):
                        res_ids = [res_ids]

                    for a_idx, a_name, r_name, r_id in zip(
                        orig_atoms, atom_names, res_names, res_ids
                    ):
                        residue_details.append(
                            f'Atom {a_idx} ({a_name}) inside Residue {r_name} (ID: {r_id})'
                        )
                except Exception:
                    residue_details = [f'Atom index: {a}' for a in orig_atoms]
            else:
                residue_details = [f'Atom index: {a}' for a in orig_atoms]

            print('=' * 60)
            print('🔬 TOPOMT DELAUNAY TETRAHEDRON DIAGNOSTIC CARD')
            print('-' * 60)
            print(f'  • Tetrahedron ID   : {tid}')
            print(f'  • Combined Class   : {tet_rec.get("combined_class", "N/A")}')
            print(f'  • Transit Role     : {tet_rec.get("transit_role", "N/A")}')
            print(f'  • Residence State  : {tet_rec.get("residence_state", "N/A")}')
            print('-' * 60)
            print(
                f'  • Topological Vol  : {tet_rec.get("volume_topological", "N/A")} Å³'
            )
            print(
                f'  • Solvent Est. Vol : {tet_rec.get("volume_solvent_estimate", "N/A")} Å³'
            )
            print(f'  • Clearance (R_res): {tet_rec.get("R_residence", 0.0):.3f} Å')
            print('-' * 60)
            print('  • Atomic Lining composition:')
            for detail in residue_details:
                print(f'      - {detail}')
            print('=' * 60)
            print()

    def __repr__(self) -> str:
        return f'<DFNDData {self.mesh!r} {self.dfn!r}>'
