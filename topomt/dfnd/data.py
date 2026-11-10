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

from typing import Any, Optional

from topomt._ackredit import attributed, scientific_call

from .. import pyunitwizard as puw
from ..tools.geometry.arrays import _GeometrySnapshot
from ..topography.input_context import InputContext
from .components import WetComponent, build_components
from .config import DFNDQuery


def _angstrom_from_nm(value):
    return float(value) * puw.conversion_factor('nm', 'angstroms')


def _angstrom3_from_nm3(value):
    return float(value) * puw.conversion_factor('nm', 'angstroms') ** 3


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
    'gate_margin',
    'effective_gate_margin',
    'transit_edge',
    'permeability_state',
    'flags',
)


def _project(records: list[dict[str, Any]], keys) -> list[dict[str, Any]]:
    return [{k: record[k] for k in keys if k in record} for record in records]


class MeshAtoms(_GeometrySnapshot):
    """Vertices of the Delaunay mesh (the dummy/real atoms used by DFND)."""

    def __init__(self, network: Any) -> None:
        self.coords = network.atom_coords  # (N, 3) selected-atom coordinates
        self.radii = network.atom_radii  # (N,)
        self.index_map = network.atom_indices_map  # local index -> global atom index
        self._freeze_arrays()


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

    def neighbors(
        self, tetrahedron_id: int, *, include_ocean: bool = False
    ) -> list[int]:
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
                'Graph has no adjacency; build it via DFN(result, network).'
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
        query_parameters = self.parameters.get('query')
        if query_parameters is None:
            defaults = DFNDQuery().to_dict()
            query_parameters = {
                name: self.parameters.get(name, default)
                for name, default in defaults.items()
            }
        self.query = DFNDQuery(**query_parameters)
        adjacency = getattr(network, 'simplex_neighbors', None)
        self.graph = Graph(result['raw'], adjacency=adjacency)
        self.boundary_connectivity = result['raw'].get('boundary_connectivity')
        self.components = build_components(result, network)

    def __repr__(self) -> str:
        return (
            f'<dfnd.dfn probe={self.parameters.get("probe_radius")} '
            f'{self.components!r}>'
        )


class DFNDData:
    """Single ``topography.dfnd`` object holding all DFND substrate."""

    def __init__(self, network: Any, result: dict[str, Any]) -> None:
        import json

        self._attribution_json = json.dumps(result.get('scientific_attribution'))
        self._network = network  # holds the cached, probe-independent mesh
        self.mesh_config = getattr(network, 'mesh_config', None)
        self.raw = result['raw']
        self.mesh = Mesh(network, result['raw'])
        self.dfn = DFN(result, network)

    @property
    def attribution(self) -> Optional[dict[str, Any]]:
        """Return detached query bibliography, preserving construction versions."""
        from topomt._ackredit import attribution_of

        return attribution_of(self)

    @property
    def network(self) -> Any:
        return self._network

    @property
    def input_context(self) -> InputContext | None:
        """Return historical input shared by every query of this native network.

        Returns
        -------
        InputContext or None
            Native captured input; None for legacy diagnostic-only containers.
        """
        return getattr(self._network, 'input_context', None)

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
        mesh_fields = set(parameters['mesh_config'])
        forbidden = sorted(mesh_fields.intersection(overrides))
        if forbidden:
            raise ValueError(
                'at_probe cannot override mesh configuration fields: '
                + ', '.join(forbidden)
            )
        min_size = overrides.pop(
            'min_size', parameters.get('reporting', {}).get('min_size', 0)
        )
        from .api import _public_length_to_nm, _warn_bare_length_args

        _warn_bare_length_args(probe_radius=probe_radius)
        try:
            query = self.dfn.query.replace(
                probe_radius=_public_length_to_nm('probe_radius', probe_radius),
                **overrides,
            )
        except TypeError as exc:
            raise ValueError(f'Unknown DFND query override: {exc}') from exc
        result = self._network.get_topography(query=query, min_size=min_size)
        return DFNDData(self._network, result)

    def _region_geometry(
        self, component_id: str, region: str, probe_radius: float = 0.0
    ):
        """Tetrahedra ``(K,4,3)`` and the reaching atoms (centers, radii) for a
        wet component's ``'resident'`` or ``'transit'`` region. ``None`` if empty.

        The atom set is every atom whose ball can reach a region tetrahedron
        (the four vertices *and* non-local intruders), gathered by a spatial query.
        """
        import numpy as np
        from scipy.spatial import cKDTree

        if region not in {'resident', 'transit'}:
            raise ValueError("region must be 'resident' or 'transit'")
        component = self.dfn.components[component_id]
        if not isinstance(component, WetComponent) or component.side != 'wet':
            raise ValueError('A wet component is required for this volume measurement')
        node_indices = list(component.resident_node_indices)
        if region == 'transit':
            node_indices += list(component.transit_connector_node_indices)
        nodes = np.asarray(node_indices, dtype=int)
        if nodes.size == 0:
            return None

        network = self._network
        tetrahedra = network.atom_coords[network.tetra_atoms[nodes]]  # (K, 4, 3)
        centroids = tetrahedra.mean(axis=1)
        bounding = np.linalg.norm(tetrahedra - centroids[:, None, :], axis=2).max(
            axis=1
        )
        tree = scientific_call('scipy', cKDTree, network.atom_coords)
        max_radius = float(np.max(network.atom_radii)) + probe_radius
        neighbor_lists = tree.query_ball_point(centroids, bounding + max_radius)
        flat = [index for sublist in neighbor_lists for index in sublist]
        atom_index = (
            np.unique(np.asarray(flat, dtype=int)) if flat else np.array([], dtype=int)
        )
        return (
            tetrahedra,
            network.atom_coords[atom_index],
            network.atom_radii[atom_index] + probe_radius,
        )

    @attributed('dfnd')
    def solvent_volume_measurement(
        self,
        component_id: str,
        *,
        region: str = 'resident',
        observable: str = 'bare_empty',
        method: str = 'mc',
        n_samples: int = 40000,
        seed: int = 0,
        confidence_level: float = 0.95,
        n_quad: int = 24,
        max_order: int = 96,
        relative_tolerance: float = 1e-4,
        absolute_tolerance: Any = None,
        max_work: int = 2000000,
    ) -> dict[str, Any]:
        """Measure a declared finite support with explicit numerical availability.

        Parameters
        ----------
        component_id : str
            Native wet component identity from this result.
        region : {'resident', 'transit'}
            Resident cells, or resident cells plus transit connectors.
        observable : {'carrier', 'bare_empty', 'probe_center'}
            Complete carrier, original-ball exclusion, or exclusion expanded by
            this query's probe. No globally accessible-volume integral is implied.
        method : {'mc', 'quadrature', 'exact'}
            Seeded IID sampling, bounded order refinement, or legacy fixed order.
        n_samples, seed : int
            Positive sample count and reproducible seed for Monte Carlo.
        confidence_level : float
            Conditional binomial confidence, default 0.95.
        n_quad, max_order : int
            Initial/legacy order and bounded refinement ceiling.
        relative_tolerance : float
            Order-difference target relative to complete carrier volume.
        absolute_tolerance : quantity, optional
            Additional volume tolerance, converted to nm**3; None means zero.
        max_work : int
            Sum K*order**2*max(1,A) quadrature-work proxy ceiling.

        Returns
        -------
        dict
            ``dfnd.volume_measurement.v1`` record with quantity-valued volume,
            uncertainty/interval/history, method/status, recoverable support and
            detached attribution. Unavailable values are None. Sampling error
            excludes model/support bias; order differences are not rigorous bounds.

        Raises
        ------
        KeyError
            The component identity is absent.
        ValueError
            Observable, wet support, units or numerical controls are invalid.

        Examples
        --------
        ``data.solvent_volume_measurement(cid, observable='probe_center')``
        measures admissible centers inside the same declared carrier support.
        """
        import numpy as np

        from .core.solvent_volume import _cell_volumes
        from .core.volume_precision import VolumeMeasurement, measure_region_volume

        if observable not in {'carrier', 'bare_empty', 'probe_center'}:
            raise ValueError(
                "observable must be 'carrier', 'bare_empty' or 'probe_center'"
            )
        if region not in {'resident', 'transit'}:
            raise ValueError("region must be 'resident' or 'transit'")
        if method not in {'mc', 'quadrature', 'exact'}:
            raise ValueError("method must be 'mc', 'quadrature' or 'exact'")
        component = self.dfn.components[component_id]
        if not isinstance(component, WetComponent) or component.side != 'wet':
            raise ValueError('A wet component is required for this volume measurement')
        nodes = list(component.resident_node_indices)
        if region == 'transit':
            nodes += list(component.transit_connector_node_indices)
        nodes = sorted(set(map(int, nodes)))
        network = self._network
        cell_atoms = network.tetra_atoms[np.asarray(nodes, dtype=int)]
        cells = network.atom_coords[cell_atoms]
        carrier = float(_cell_volumes(cells).sum())
        probe = (
            float(self.dfn.query.probe_radius) if observable == 'probe_center' else 0.0
        )
        if absolute_tolerance is None:
            atol = 0.0
        elif puw.is_quantity(absolute_tolerance):
            atol = float(puw.get_value(absolute_tolerance, to_unit='nm**3'))
        else:
            raise ValueError('absolute_tolerance requires explicit volume units')
        geometry = self._region_geometry(component_id, region, probe_radius=probe)
        if geometry is None or observable == 'carrier':
            measured = VolumeMeasurement(
                carrier,
                0.0,
                'carrier' if observable == 'carrier' else method,
                'analytic',
                'geometric_proof',
            )
            n_balls = 0
        else:
            tetrahedra, centers, radii = geometry
            n_balls = len(centers)
            measured = measure_region_volume(
                tetrahedra,
                centers,
                radii,
                method=method,
                n_samples=n_samples,
                seed=seed,
                confidence_level=confidence_level,
                n_quad=n_quad,
                max_order=max_order,
                relative_tolerance=relative_tolerance,
                absolute_tolerance=atol,
                max_work=max_work,
            )

        def volume_quantity(value):
            return None if value is None else puw.quantity(value, 'nm**3')

        context = self.input_context
        return {
            'schema': 'dfnd.volume_measurement.v1',
            'observable': observable,
            'region': region,
            'method': measured.method,
            'status': measured.status,
            'error_kind': measured.error_kind,
            'volume': volume_quantity(measured.volume),
            'error': volume_quantity(measured.error),
            'interval': None
            if measured.interval is None
            else tuple(volume_quantity(v) for v in measured.interval),
            'confidence_level': measured.confidence_level,
            'n_samples': measured.n_samples,
            'n_empty': measured.n_empty,
            'seed': seed if measured.n_samples else None,
            'quadrature_history': [
                {'order': order, 'volume': volume_quantity(value)}
                for order, value in measured.history
            ],
            'reason': measured.reason,
            'carrier_volume': volume_quantity(carrier),
            'exclusion_expansion': puw.quantity(probe, 'nm'),
            'support': {
                'source_id': None if context is None else context.source_id,
                'result_key': self.raw['parameters'].get('result_key'),
                'mesh_key': self.raw['parameters'].get('mesh_key'),
                'component_id': component_id,
                'tetrahedron_ids': nodes,
                'tetrahedra_source_atom_indices': network.atom_indices_map[
                    cell_atoms
                ].tolist(),
                'selected_source_atom_indices': network.atom_indices_map.tolist(),
                'n_excluding_balls': n_balls,
                'boundary_convention': 'nonperiodic_cartesian',
            },
            'uncertainty_scope': 'Conditional numerical/sampling uncertainty on the declared support and ball model; excludes support/model error',
        }

    def solvent_volume(
        self,
        component_id: str,
        *,
        region: str = 'resident',
        method: str = 'mc',
        n_samples: int = 40000,
        seed: int = 0,
        n_quad: int = 24,
    ):
        """Return bare empty volume and conditional numerical uncertainty.

        On-demand: this is *not* computed during ``get_topography``; call it on the
        components of interest. ``region='resident'`` selects resident tetrahedra;
        ``region='transit'`` adds the transit connectors. These are finite carrier
        domains, not globally reachable or swept solvent volumes. Overlapping
        van der Waals spheres and non-local intruder atoms are handled natively.

        ``method='mc'`` returns the volume and maximum distance to its asymmetric
        95% Clopper–Pearson interval endpoints. ``method='quadrature'`` uses bounded
        order refinement; its error is a convergence diagnostic or None if
        unresolved. Legacy ``method='exact'`` preserves fixed-order values and
        ``(volume, None)`` with explicitly unknown quadrature error. Values use
        nm**3 quantities; if no order could run, volume is None. Inspect
        ``solvent_volume_measurement`` for the full status, support and history.
        """
        result = self.solvent_volume_measurement(
            component_id,
            region=region,
            method=method,
            n_samples=n_samples,
            seed=seed,
            n_quad=n_quad,
        )
        return result['volume'], None if method == 'exact' else result['error']

    def occupancy_grid(
        self,
        component_id: str,
        *,
        region: str = 'resident',
        spacing: float = 0.05,
    ):
        """Voxel occupancy grid (the 3D *shape*) of a wet component's empty space.

        On-demand companion to ``solvent_volume``: instead of a scalar it returns
        the boolean grid of empty voxels (centre inside the region and outside every
        ball) — for visualization, marching-cubes surfaces, diffusion, or shape
        descriptors. ``spacing`` is the voxel size in nm.

        Returns a dict ``{'volume', 'grid', 'origin', 'spacing'}``: ``volume`` (an
        independent, discretization-limited cross-check of ``solvent_volume``) and
        ``origin``/``spacing`` are ``nm`` quantities; ``grid`` is a boolean array.
        """
        from .core.solvent_volume import region_occupancy_grid

        geometry = self._region_geometry(component_id, region)
        if geometry is None:
            return {
                'volume': puw.quantity(0.0, 'nm**3'),
                'grid': None,
                'origin': None,
                'spacing': puw.quantity(spacing, 'nm'),
            }
        tetrahedra, centers, radii = geometry
        result = region_occupancy_grid(tetrahedra, centers, radii, spacing=spacing)
        return {
            'volume': puw.quantity(result.volume, 'nm**3'),
            'grid': result.grid,
            'origin': puw.quantity(result.origin, 'nm'),
            'spacing': puw.quantity(result.spacing, 'nm'),
        }

    def info(self, tetrahedron_id: Any = None) -> None:
        """Print a scientific diagnostic card for Delaunay tetrahedra."""
        import molsysmt as msm
        import numpy as np

        tetrahedra_list = self.raw.get('tetrahedra', [])
        if not tetrahedra_list:
            print('No Delaunay tetrahedra found in this topography.')
            return

        if tetrahedron_id is None:
            print(f'Topography has {len(tetrahedra_list)} Delaunay tetrahedra.')
            print(
                'Please specify a tetrahedron_id '
                '(e.g., topography.dfnd.info(0)) to see its diagnostic card.'
            )
            return

        if isinstance(tetrahedron_id, (int, np.integer)):
            target_ids = [int(tetrahedron_id)]
        else:
            try:
                target_ids = [int(x) for x in tetrahedron_id]
            except Exception:
                target_ids = [int(tetrahedron_id)]

        context = self.input_context
        if context is None:
            mol_sys = getattr(self._network, 'molecular_system', None)
        else:
            try:
                mol_sys = context.recover_molecular_system()
            except ValueError:
                mol_sys = None

        for tid in target_ids:
            tet_rec = None
            for idx, t in enumerate(tetrahedra_list):
                if t.get('tetrahedron_id', idx) == tid:
                    tet_rec = t
                    break

            if not tet_rec:
                print(f'Error: Tetrahedron ID {tid} not found.')
                continue

            system_atom_indices = tet_rec.get('atom_indices', [])
            residue_details = []
            if mol_sys is not None:
                try:
                    local_indices = (
                        system_atom_indices
                        if context is None
                        else context.local_atom_indices(
                            system_atom_indices, source_id=context.source_id
                        )
                    )
                    atom_names = msm.get(
                        mol_sys, element='atom', selection=local_indices, atom_name=True
                    )
                    res_names = msm.get(
                        mol_sys,
                        element='atom',
                        selection=local_indices,
                        residue_name=True,
                    )
                    res_ids = msm.get(
                        mol_sys,
                        element='atom',
                        selection=local_indices,
                        residue_id=True,
                    )

                    if not isinstance(atom_names, (list, tuple, np.ndarray)):
                        atom_names = [atom_names]
                    if not isinstance(res_names, (list, tuple, np.ndarray)):
                        res_names = [res_names]
                    if not isinstance(res_ids, (list, tuple, np.ndarray)):
                        res_ids = [res_ids]

                    for a_idx, a_name, r_name, r_id in zip(
                        system_atom_indices, atom_names, res_names, res_ids
                    ):
                        residue_details.append(
                            f'Atom {a_idx} ({a_name}) inside Residue '
                            f'{r_name} (ID: {r_id})'
                        )
                except Exception:
                    residue_details = [f'Atom index: {a}' for a in system_atom_indices]
            else:
                residue_details = [f'Atom index: {a}' for a in system_atom_indices]

            print('=' * 60)
            print('🔬 TOPOMT DELAUNAY TETRAHEDRON DIAGNOSTIC CARD')
            print('-' * 60)
            print(f'  • Tetrahedron ID   : {tid}')
            print(f'  • Combined Class   : {tet_rec.get("combined_class", "N/A")}')
            print(f'  • Transit Role     : {tet_rec.get("transit_role", "N/A")}')
            print(f'  • Residence State  : {tet_rec.get("residence_state", "N/A")}')
            print('-' * 60)
            topological_volume = _angstrom3_from_nm3(
                tet_rec.get('volume_topological', 0.0)
            )
            solvent_volume = _angstrom3_from_nm3(
                tet_rec.get('volume_solvent_estimate', 0.0)
            )
            residence_clearance = _angstrom_from_nm(tet_rec.get('R_residence', 0.0))
            print(f'  • Topological Vol  : {topological_volume} Å³')
            print(f'  • Solvent Est. Vol : {solvent_volume} Å³')
            print(f'  • Clearance (R_res): {residence_clearance:.3f} Å')
            print('-' * 60)
            print('  • Atomic Lining composition:')
            for detail in residue_details:
                print(f'      - {detail}')
            print('=' * 60)
            print()

    def __repr__(self) -> str:
        return f'<DFNDData {self.mesh!r} {self.dfn!r}>'
