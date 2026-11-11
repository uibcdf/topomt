"""Inspect the actual public/native route on declared BenchLab controls.

This study helper validates recoverable support and native relations. It does
not infer a physical interface, swept region or neutral support API from them.
"""

from collections import deque
from copy import deepcopy
from typing import Any, get_args

import numpy as np

from devtools.benchlab.capture_volume import encode_quantities
from topomt import pyunitwizard as puw
from topomt.features.BaseFeature import ShapeType


def _support_inventory(topo):
    data = topo.dfnd
    network = data.network
    records = {row['tetrahedron_id']: row for row in data.raw['tetrahedra']}
    if set(records) != set(range(len(network.tetra_atoms))):
        raise ValueError('Incomplete native tetrahedron inventory')
    for node, row in records.items():
        expected = network.atom_indices_map[network.tetra_atoms[node]]
        if sorted(row['atom_indices']) != sorted(expected):
            raise ValueError('Raw source support disagrees with captured mesh')
    owner = {}
    for component in data.dfn.components.values():
        for node in component.node_indices:
            if node not in records or node in owner:
                raise ValueError('Invalid or overlapping native component support')
            owner[node] = component
        expected = {
            tuple(sorted(records[node]['atom_indices']))
            for node in component.node_indices
        }
        if {tuple(sorted(row)) for row in component.tetrahedron_support} != expected:
            raise ValueError('Typed component support differs from source tetrahedra')
        if not set(component.atom_indices) <= set(network.atom_indices_map):
            raise ValueError('Lining atoms leave the captured source namespace')
    if set(owner) != set(records):
        raise ValueError('Wet/dry banks do not cover the native node inventory')
    for node in records:
        all_neighbors = data.dfn.graph.neighbors(node)
        for side in ('wet', 'dry'):
            expected = [
                neighbor for neighbor in all_neighbors if owner[neighbor].side == side
            ]
            if data.dfn.graph.neighbors(node, component_side=side) != expected:
                raise ValueError(
                    'Component-side neighbors disagree with native membership'
                )
    for component in data.dfn.components.wet:
        resident = set(component.resident_node_indices)
        connector = set(component.transit_connector_node_indices)
        if resident & connector or resident | connector != set(component.node_indices):
            raise ValueError('Resident/connector support is not a partition')
        depth = component.topological_depth
        if set(depth) != set(component.node_indices):
            raise ValueError('Native depth omits component support')
        roots = {
            node
            for link in data.raw['external_links']
            if link['external_link_id'] in component.external_link_ids
            for node in link['tetrahedron_ids']
        } & set(component.node_indices)
        if roots:
            adjacency = {node: set() for node in component.node_indices}
            for face in data.raw['faces']:
                a, b = face['owner_tetrahedron_id'], face['neighbor_tetrahedron_id']
                if face.get('transit_edge') and a in adjacency and b in adjacency:
                    adjacency[a].add(b)
                    adjacency[b].add(a)
            expected_depth = dict.fromkeys(roots, 0)
            pending = deque(roots)
            while pending:
                node = pending.popleft()
                for neighbor in adjacency[node]:
                    if neighbor not in expected_depth:
                        expected_depth[neighbor] = expected_depth[node] + 1
                        pending.append(neighbor)
        else:
            expected_depth = dict.fromkeys(component.node_indices, 0)
        if depth != expected_depth:
            raise ValueError(
                'Native depth disagrees with admitted graph distances/convention'
            )
        covered = []
        for region in component.depth_regions:
            if region['parent_component_key'] != component.component_key:
                raise ValueError('Depth region has another contextual parent')
            covered.extend(region['node_ids'])
            if any(depth[node] != region['depth'] for node in region['node_ids']):
                raise ValueError('Depth region values disagree with native depth')
        if sorted(covered) != sorted(component.node_indices):
            raise ValueError('Depth regions do not partition component support')
    return records, owner


def _coast_inventory(topo, owner):
    components = topo.dfnd.dfn.components
    raw_faces = topo.dfnd.raw['faces']
    expected = {
        row['face_id']
        for row in raw_faces
        if row['neighbor_tetrahedron_id'] is not None
        and row['neighbor_tetrahedron_id'] >= 0
        and owner[row['owner_tetrahedron_id']].side
        != owner[row['neighbor_tetrahedron_id']].side
    }
    coast = components.coast_faces
    if {row['face_id'] for row in coast} != expected or len(coast) != len(expected):
        raise ValueError('Coast face inventory is incomplete or duplicated')
    mapping = {int(atom): i for i, atom in enumerate(topo.input_context.atom_indices)}
    coords = np.asarray(puw.get_value(topo.input_context.coordinates, to_unit='nm'))
    groups = {}
    for row in coast:
        wet, dry = (
            components[row['wet_component_id']],
            components[row['dry_component_id']],
        )
        if wet.side != 'wet' or dry.side != 'dry':
            raise ValueError('Coast component roles disagree')
        if (
            row['wet_tetrahedron_id'] not in wet.node_indices
            or row['dry_tetrahedron_id'] not in dry.node_indices
        ):
            raise ValueError('Coast tetrahedra leave their component support')
        triangle = coords[[mapping[int(atom)] for atom in row['atom_indices']]]
        area = float(
            np.linalg.norm(
                np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
            )
            / 2
        )
        if not np.isclose(row['area'], area, rtol=1e-12, atol=1e-14):
            raise ValueError('Coast carrier area differs from source triangle')
        kind = 'beach' if row['permeability_state'] == 'permeable' else 'shore'
        if row['kind'] != kind:
            raise ValueError('Coast role disagrees with native incidence')
        key = (wet.component_id, dry.component_id)
        group = groups.setdefault(key, {'faces': set(), 'area': 0.0})
        group['faces'].add(row['face_id'])
        group['area'] += area
    for (wet_id, dry_id), group in groups.items():
        wet = components[wet_id].dry_lining[dry_id]
        dry = components[dry_id].wet_lining[wet_id]
        if (
            set(wet['contact_face_ids']) != group['faces']
            or set(dry['contact_face_ids']) != group['faces']
        ):
            raise ValueError('Wet/dry lining incidences are not symmetric')
        if not all(
            np.isclose(row['area'], group['area'], rtol=1e-12, atol=1e-14)
            for row in (wet, dry)
        ):
            raise ValueError('Symmetric lining carrier areas disagree')


def _public_inventory(topo):
    rows = []
    for feature in topo.values():
        if feature.shape_type not in get_args(ShapeType):
            raise ValueError('Reported shape is absent from the public type contract')
        if feature.topography is not topo:
            raise ValueError('Public feature is bound to another registry')
        parents = topo.parents_of(feature.feature_id)
        children = topo.children_of(feature.feature_id)
        for parent in parents:
            if feature not in topo.children_of(parent.feature_id):
                raise ValueError('Parent/child relation is not symmetric')
        for child in children:
            if feature not in topo.parents_of(child.feature_id):
                raise ValueError('Child/parent relation is not symmetric')
        row = {
            'feature_id': feature.feature_id,
            'python_class': type(feature).__name__,
            'feature_type': feature.feature_type,
            'shape_type': feature.shape_type,
            'legacy_dimensionality': feature.dimensionality,
            'parent_ids': sorted(parent.feature_id for parent in parents),
            'child_ids': sorted(child.feature_id for child in children),
            'source_id': feature.source_id,
            'support_key': getattr(feature, 'support_key', None),
            'lining_source_atom_indices': list(feature.atom_indices),
        }
        if feature.feature_type != 'mouth':
            native = topo.dfnd.dfn.components[feature.component_id]
            if feature.signature != native.signature:
                raise ValueError(
                    'Public grounded signature differs from native component'
                )
            if (
                feature.classification != native.classification
                or feature.feature_type != native.classification['name']
            ):
                raise ValueError(
                    'Public catalog refinement differs from native provenance'
                )
            if (
                feature.component_key != native.component_key
                or feature.support_key != native.support_key
            ):
                raise ValueError('Public component/source support identity differs')
            row.update(
                {
                    'component_id': feature.component_id,
                    'component_key': feature.component_key,
                    'signature': deepcopy(feature.signature),
                    'classification': deepcopy(feature.classification),
                    'center': feature.center,
                    'carrier_volume': feature.volume_topological_resident,
                    'local_solvent_proxy': feature.volume_solvent_estimate,
                    'native_bank_interface_flag': feature.is_interface,
                    'physical_openings': deepcopy(
                        feature.boundary.get('physical_openings')
                    ),
                }
            )
        else:
            if len(parents) != 1:
                raise ValueError('A promoted native Mouth must retain its one parent')
            parent = next(iter(parents))
            if feature.parent_component_key != parent.component_key:
                raise ValueError('Mouth parent context differs')
            row.update(
                {
                    'parent_component_key': feature.parent_component_key,
                    'carrier_area': feature.area,
                    'face_ids': list(feature.face_ids),
                    'source_faces': deepcopy(feature.faces),
                }
            )
        rows.append(encode_quantities(row))
    return rows


def describe_public_contract(topo: Any) -> dict[str, Any]:
    """Validate and describe actual native support, relations and public availability.

    Parameters
    ----------
    topo : topomt.Topography
        Actual DFND public result on a declared frozen study input.

    Returns
    -------
    dict
        Detached study observation with explicit native numeric units and public
        quantities, source support, wet/dry/depth context and unavailable roles.
        Its availability descriptions are study interpretations, not new API fields.

    Raises
    ------
    ValueError
        DFND/input context is missing, or observed supports/relations disagree.
    """
    if getattr(topo, 'dfnd', None) is None or topo.input_context is None:
        raise ValueError('This receiving requires actual DFND and captured input')
    records, owner = _support_inventory(topo)
    _coast_inventory(topo, owner)
    public = _public_inventory(topo)
    data = topo.dfnd
    wet = []
    for component in data.dfn.components.wet:
        wet.append(
            {
                'component_id': component.component_id,
                'component_key': component.component_key,
                'support_key': component.support_key,
                'node_indices': list(component.node_indices),
                'resident_node_indices': list(component.resident_node_indices),
                'connector_node_indices': list(
                    component.transit_connector_node_indices
                ),
                'tetrahedron_source_support': deepcopy(component.tetrahedron_support),
                'lining_source_atom_indices': list(component.atom_indices),
                'signature': deepcopy(component.signature),
                'classification': deepcopy(component.classification),
                'native_external_link_ids': list(component.external_link_ids),
                'topological_depth': dict(component.topological_depth),
                'depth_reference': 'native_exterior_graph_hops'
                if component.external_link_ids
                else 'no_exterior_zero_convention',
                'depth_regions': deepcopy(component.depth_regions),
                'boundary': deepcopy(component.boundary),
                'dry_lining': deepcopy(component.dry_lining),
                'characteristic_radii_nm': deepcopy(component.characteristic_radii),
                'native_bank_interface_flag': component.is_interface,
                'native_bank_ids': list(component.lining_bodies),
                'candidate_atom_union': list(component.accessible_atom_indices),
                'beach_candidate_proxy': deepcopy(component.beach_pocket),
            }
        )
    dry = [
        {
            'component_id': c.component_id,
            'component_key': c.component_key,
            'support_key': c.support_key,
            'node_indices': list(c.node_indices),
            'tetrahedron_source_support': deepcopy(c.tetrahedron_support),
            'lining_source_atom_indices': list(c.atom_indices),
            'wet_lining': deepcopy(c.wet_lining),
            'raw_bank_record': deepcopy(c.raw_record),
        }
        for c in data.dfn.components.dry
    ]
    physical = data.raw['boundary_connectivity']
    return {
        'schema': 'topomt.benchlab.public-contract-observation/1',
        'units': deepcopy(data.raw['units']),
        'neighbor_filters': {
            'side': 'Legacy local residence state; nonresident can include wet connectors',
            'component_side': 'Captured native wet carrier or dry bank, including connector membership',
            'admitted_edges': 'These are filtered face incidences; graph depth uses transit_edge separately',
            'all_node_memberships_verified': True,
        },
        'input_source_id': topo.input_context.source_id,
        'source_atom_indices': topo.input_context.atom_indices.tolist(),
        'query': deepcopy(data.raw['parameters']['query']),
        'result_key': data.raw['parameters']['result_key'],
        'node_inventory': {
            'wet_nodes': sum(c.side == 'wet' for c in owner.values()),
            'dry_nodes': sum(c.side == 'dry' for c in owner.values()),
            'total': len(records),
        },
        'tetrahedron_source_atoms': {
            str(node): row['atom_indices'].copy() for node, row in records.items()
        },
        'node_roles': [
            {
                key: deepcopy(row[key])
                for key in (
                    'tetrahedron_id',
                    'residence_state',
                    'transit_role',
                    'flags',
                    'R_residence',
                )
                if key in row
            }
            for row in records.values()
        ],
        'wet_components': wet,
        'dry_components': dry,
        'coast_faces': deepcopy(data.dfn.components.coast_faces),
        'public_features': public,
        'physical_boundary': {
            key: deepcopy(physical.get(key))
            for key in ('schema', 'status', 'reason', 'n_patches', 'query')
        },
        'public_molecular_interface_validation': 'not_established',
        'public_dry_relief_promotion': 'not_implemented_by_this_bridge',
        'versioned_public_topography_interchange': 'not_implemented',
        'native_pickle': 'Existing source-bound Python restoration guards, not a versioned public interchange schema',
        'scope': 'Native banks/incidences/depth/candidate proxies and public registry receiving; no supplied molecular participant, physical wetting or exact burial claim',
    }
