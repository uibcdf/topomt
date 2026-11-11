"""Independent dumbbell reference replay and source-bound public receiving."""

import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np
import pyunitwizard as puw

_root = Path(__file__).resolve().parents[5]
_previous = sys.path[:]
try:
    sys.path.insert(0, str(_root))
    from devtools.benchlab import ball_study as _shared
finally:
    sys.path[:] = _previous

read = _shared.read
quantity = _shared.quantity
describe = _shared.describe
_tools = _shared._tools


def receive(directory: Path, probe: float, min_size: int = 0) -> Any:
    """Receive this fixed case through the actual public DFND API.

    Parameters
    ----------
    directory : Path
        Case directory in the checkout or extracted complete bundle.
    probe : float
        Explicit probe radius in angstroms.
    min_size : int, default=0
        Public reporting cutoff, distinct from the frozen query geometry.

    Returns
    -------
    topomt.Topography
        Native and public results with the original source/radius support.

    Raises
    ------
    ValueError
        The case identity, input/PDB hash or molecular radius assignment differs.
    """
    if read(directory / 'identity.json')['case_id'] != 'dumbbell':
        raise ValueError('Dumbbell study identity differs')
    return _shared.receive(directory, probe, min_size)


def references(directory: Path) -> dict:
    """Replay retained independent references without importing native DFND."""
    with _tools():
        from devtools.verify_dumbbell_reference import verify_reference

        folder = directory / 'artifacts/dumbbell_v1'
        return verify_reference(
            folder / 'input.json',
            folder / 'protocol.json',
            read(folder / 'reference_certificate.json'),
        )


def inspect_anchors(topo: Any, anchors: Any) -> list[dict]:
    """Locate dimensional reference points in actual native/public supports.

    Parameters
    ----------
    topo : topomt.Topography
        Existing result, without executing another query.
    anchors : quantity
        Reference coordinates with explicit length units, shape (n, 3).

    Returns
    -------
    list of dict
        Complete containing-cell inventory, source atoms, component/role and
        public parent correspondence. Bare reported lengths are angstroms.

    Raises
    ------
    ValueError
        Geometry or complete native support is unavailable.
    """
    points = np.asarray(puw.get_value(anchors, to_unit='angstroms'))
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError('Reference points must be finite dimensional coordinates')
    observed = describe(topo)
    centers = np.asarray(
        puw.get_value(topo.input_context.coordinates, to_unit='angstroms')
    )
    radii = np.asarray(puw.get_value(topo.input_context.radii, to_unit='angstroms'))
    network = topo.dfnd.network
    cells = np.asarray(network.tetra_atoms)
    owner = {
        node: c for c in topo.dfnd.dfn.components.values() for node in c.node_indices
    }
    if set(owner) != set(range(len(cells))):
        raise ValueError('The native cell inventory lacks a component owner')
    rows = []
    for point in points:
        hits = []
        for node, atoms in enumerate(cells):
            vertices = centers[atoms]
            bary = np.linalg.solve((vertices[1:] - vertices[0]).T, point - vertices[0])
            bary = np.r_[1 - bary.sum(), bary]
            if bary.min() < -1e-10:
                continue
            component = owner[node]
            role = 'dry'
            if component.side == 'wet':
                role = (
                    'resident'
                    if node in component.resident_node_indices
                    else 'connector'
                )
            hits.append(
                {
                    'tetrahedron_id': node,
                    'barycentric_coordinates': bary.tolist(),
                    'source_atom_indices': network.atom_indices_map[atoms].tolist(),
                    'component_id': component.component_id,
                    'component_key': component.component_key,
                    'side': component.side,
                    'native_role': role,
                }
            )
        keys = sorted({hit['component_key'] for hit in hits if hit['side'] == 'wet'})
        public = [
            f for f in observed['public_features'] if f.get('component_key') in keys
        ]
        rows.append(
            {
                'length_unit': 'angstroms',
                'point': point.tolist(),
                'cell_hits': hits,
                'physical_clearance_angstroms': float(
                    (np.linalg.norm(centers - point, axis=1) - radii).min()
                ),
                'wet_component_keys': keys,
                'public_parent_ids': [f['feature_id'] for f in public],
                'public_parent_types': [f['python_class'] for f in public],
            }
        )
    return rows


def inspect_hierarchy(topo: Any) -> dict:
    """Recover native hierarchy motifs and verify their actual public transport.

    Parameters
    ----------
    topo : topomt.Topography
        Existing source-bound DFND result.

    Returns
    -------
    dict
        Original native motif dictionaries in the declared nm protocol, their
        complete source supports and actual public parent correspondence.
        Provisional flags are preserved; no physical subregion is certified.

    Raises
    ------
    ValueError
        A motif support, parent/child key or public copy disagrees.
    """
    from topomt.dfnd.identity import external_link_support_key, motif_key, support_key

    with _tools():
        from devtools.benchlab.capture_volume import encode_quantities

        network = topo.dfnd.network
        source_atoms = set(map(int, network.atom_indices_map))
        rows, public_rows = [], []
        for component in topo.dfnd.dfn.components.wet:
            chambers, throats = (
                component.chamber_candidates,
                component.throat_candidates,
            )
            chamber_keys = {c['motif_key'] for c in chambers}
            for chamber in chambers:
                nodes = chamber['node_ids']
                if not set(nodes) <= set(component.node_indices):
                    raise ValueError('Chamber support leaves its native parent')
                atoms = sorted(
                    {
                        int(a)
                        for node in nodes
                        for a in network.atom_indices_map[network.tetra_atoms[node]]
                    }
                )
                expected = support_key(
                    [
                        network.atom_indices_map[network.tetra_atoms[n]].tolist()
                        for n in nodes
                    ]
                )
                if (
                    atoms != chamber['atom_indices']
                    or expected != chamber['motif_support_key']
                ):
                    raise ValueError('Chamber source support cannot be recovered')
            for throat in throats:
                if not set(throat['child_chamber_keys']) <= chamber_keys:
                    raise ValueError('Throat names an unavailable chamber')
                if not set(throat['face_atoms']) <= source_atoms:
                    raise ValueError('Throat source support leaves the input')
                if (
                    external_link_support_key([throat['face_atoms']])
                    != throat['motif_support_key']
                ):
                    raise ValueError('Throat face support cannot be recovered')
            for motif in [*chambers, *throats]:
                if motif['parent_component_key'] != component.component_key or motif[
                    'motif_key'
                ] != motif_key(
                    component.component_key,
                    motif['motif_type'],
                    motif['motif_support_key'],
                ):
                    raise ValueError('Hierarchy parent or motif identity differs')
            rows.append(
                {
                    'component_id': component.component_id,
                    'component_key': component.component_key,
                    'support_key': component.support_key,
                    'native_family': component.family,
                    'chambers': deepcopy(chambers),
                    'throats': deepcopy(throats),
                    'bottleneck': deepcopy(component.bottleneck),
                }
            )
        standalone = False
        for feature in topo.values():
            if feature.feature_type == 'mouth':
                continue
            component = topo.dfnd.dfn.components[feature.component_id]
            actual = [
                m
                for m in feature.motifs
                if m.get('motif_type') in ('chamber_candidate', 'throat_candidate')
            ]
            expected_motifs = [*component.throat_candidates, *component.chamber_candidates]
            if encode_quantities(actual) != encode_quantities(expected_motifs):
                raise ValueError(
                    'Public hierarchy motifs differ from their native parent'
                )
            standalone |= any(
                child.feature_type
                in ('chamber', 'throat', 'chamber_candidate', 'throat_candidate')
                for child in topo.children_of(feature.feature_id)
            )
            public_rows.append(
                {
                    'feature_id': feature.feature_id,
                    'python_class': type(feature).__name__,
                    'component_key': component.component_key,
                    'motif_keys': [m['motif_key'] for m in actual],
                    'public_child_ids': [
                        child.feature_id
                        for child in topo.children_of(feature.feature_id)
                    ],
                }
            )
        return {
            'schema': 'topomt.benchlab.dumbbell-hierarchy-receiving/1',
            'native_length_unit': 'nm',
            'components': rows,
            'public': public_rows,
            'public_motif_keys_match_native': True,
            'standalone_chamber_children_promoted': standalone,
            'scope': 'Actual provisional capacity hierarchy and copied public motifs; no physical all-atom chamber boundary, exact bottleneck or new component promotion is inferred.',
        }
