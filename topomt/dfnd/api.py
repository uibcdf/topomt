import warnings
from numbers import Real
from typing import Any

import numpy as np

from .. import pyunitwizard as puw
from ..features import (
    Channel,
    Groove,
    Mouth,
    OpenConcavity,
    Percolating,
    Pocket,
    Void,
)
from ..topography.Topography import Topography
from .config import DFNDMeshConfig, DFNDQuery
from .data import DFNDData
from .graph import DelaunayFlowNetwork

_FEATURE_CLASS_BY_FAMILY = {
    'pockets': Pocket,
    'voids': Void,
    'channels': Channel,
    'percolatings': Percolating,
}

# Catalog-name overrides within a topological family: the 1-mouth family splits into
# the occluded `pocket` (default) and the open `open_concavity` by occlusion (decision
# S5.2). Other families' classification name == the family default, so they need no
# entry. feature_type then IS the catalog name.
_FEATURE_CLASS_BY_NAME = {
    'open_concavity': OpenConcavity,
    'groove': Groove,
}

# Families whose external links are promoted to child Mouth features. Voids have
# no mouths; percolating regions are fully open (their single external link is the
# whole boundary, not a real mouth), so neither gets Mouth children.
_FAMILIES_WITH_MOUTHS = {'pockets', 'channels'}


def _public_length_to_nm(name: str, value: Any) -> float:
    """Normalize a public DFND length argument to nanometers.

    Quantities are the canonical public form; bare numeric values are legacy
    compatibility inputs interpreted as angstroms. This converter is silent and
    safe to reuse internally; the bare-float deprecation warning is emitted at the
    public boundary instead (see ``_warn_bare_length_args``).
    """
    if puw.is_quantity(value):
        return float(puw.get_value(value, to_unit='nm'))
    if isinstance(value, Real):
        return float(value) * 0.1
    return float(puw.get_value(value, to_unit='nm'))


def _warn_bare_length_args(**named_values: Any) -> None:
    """Emit the bare-float deprecation from a public entry point.

    Call this directly from a user-facing function (``dfnd``,
    ``dfnd_to_topography``, ``at_probe``). It is always exactly one frame below the
    function the user called, so a fixed ``stacklevel=3`` (warn -> here -> entry
    point -> user) attributes the warning to the user's call regardless of internal
    plumbing -- unlike a constant buried in the shared converter, which sat at
    different depths on different call paths.
    """
    for name, value in named_values.items():
        if value is None or puw.is_quantity(value):
            continue
        if isinstance(value, Real):
            warnings.warn(
                f"DFND length argument '{name}' received a bare float. Bare floats "
                'are deprecated in public APIs; pass a PyUnitWizard quantity instead. '
                'For compatibility this value is interpreted as angstroms.',
                FutureWarning,
                stacklevel=3,
            )


def _feature_from_component_record(
    record: dict[str, Any], feature_class, source: str = 'dfnd'
):
    feature = feature_class(
        atom_indices=record['atom_indices'],
        source=source,
        source_id=f'{source}:{record["family"]}:{record["id"]}',
    )
    feature.family = record['family']
    feature.component_key = record.get('component_key')
    feature.support_key = record.get('support_key')
    feature.component_index = record.get('component_index')
    feature.node_count_rank = record.get('node_count_rank')
    feature.size_rank = record.get('size_rank')
    feature.tetrahedron_indices = record['tetrahedron_indices']
    feature.resident_tetrahedron_indices = record['resident_tetrahedron_indices']
    feature.transit_connector_tetrahedron_indices = record[
        'transit_connector_tetrahedron_indices'
    ]
    feature.center = puw.quantity(record['center'], 'nm')
    feature.volume_topological_resident = puw.quantity(
        record['volume_topological_resident'], 'nm**3'
    )
    feature.volume_solvent_estimate = puw.quantity(
        record['volume_solvent_estimate'], 'nm**3'
    )
    feature.n_mouths = record['n_mouths']
    feature.mouth_area = puw.quantity(record['mouth_area'], 'nm**2')
    feature.mouths = record['mouths']
    feature.mouth_face_clusters = record['mouth_face_clusters']
    feature.flags = record['flags']
    feature.raw_record = record
    return feature


def _reject_conflicting_legacy_values(
    object_name: str,
    values: dict[str, Any],
    defaults: dict[str, Any],
    configured: dict[str, Any],
) -> None:
    def equal(left: Any, right: Any) -> bool:
        try:
            # Float-tolerant: nm-converted length args carry rounding error
            # (e.g. 1.4 angstroms -> 0.14000000000000001 nm).
            return bool(np.isclose(float(left), float(right)))
        except (TypeError, ValueError):
            pass
        try:
            return bool(np.array_equal(left, right))
        except Exception:
            return left == right

    conflicts = [
        name
        for name, value in values.items()
        if not equal(value, defaults[name]) and not equal(value, configured[name])
    ]
    if conflicts:
        raise ValueError(
            f'{object_name} conflicts with explicit arguments: ' + ', '.join(conflicts)
        )


def _run_dfnd(
    molecular_system,
    selection: str,
    structure_indices: int,
    probe_radius: float,
    min_size: int,
    epsilon: float,
    hydrogen_policy: str,
    radii_model: str,
    transit_policy: str,
    gate_intrusion_policy: str,
    residence_tolerance: float,
    permeability_tolerance: float,
    dry_adjacency: str,
    mesh_config: DFNDMeshConfig | None = None,
    query: DFNDQuery | None = None,
) -> tuple[DelaunayFlowNetwork, dict[str, Any]]:
    """Build the network and run the decomposition. Shared by the public entry points."""
    mesh_values = {
        'selection': selection,
        'structure_indices': structure_indices,
        'epsilon': _public_length_to_nm('epsilon', epsilon),
        'hydrogen_policy': hydrogen_policy,
        'radii_model': radii_model,
    }
    mesh_defaults = {
        'selection': 'all',
        'structure_indices': 0,
        'epsilon': 1e-7,
        'hydrogen_policy': 'exclude',
        'radii_model': 'vdw',
    }
    if mesh_config is None:
        mesh_config = DFNDMeshConfig(**mesh_values)
    elif not isinstance(mesh_config, DFNDMeshConfig):
        raise TypeError('mesh_config must be a DFNDMeshConfig')
    else:
        _reject_conflicting_legacy_values(
            'mesh_config', mesh_values, mesh_defaults, mesh_config.to_dict()
        )

    query_values = {
        'probe_radius': _public_length_to_nm('probe_radius', probe_radius),
        'residence_tolerance': _public_length_to_nm(
            'residence_tolerance', residence_tolerance
        ),
        'permeability_tolerance': _public_length_to_nm(
            'permeability_tolerance', permeability_tolerance
        ),
        'transit_policy': transit_policy,
        'gate_intrusion_policy': gate_intrusion_policy,
        'dry_adjacency': dry_adjacency,
    }
    query_defaults = DFNDQuery().to_dict()
    if query is None:
        query = DFNDQuery(**query_values)
    elif not isinstance(query, DFNDQuery):
        raise TypeError('query must be a DFNDQuery')
    else:
        _reject_conflicting_legacy_values(
            'query', query_values, query_defaults, query.to_dict()
        )

    network = DelaunayFlowNetwork(
        molecular_system,
        **mesh_config.to_dict(),
    )
    result = network.get_topography(
        query=query,
        min_size=min_size,
    )
    return network, result


def dfnd_to_topography(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    probe_radius: Any = puw.quantity(1.4, 'angstroms'),
    min_size: int = 0,
    epsilon: Any = puw.quantity(1e-6, 'angstroms'),
    hydrogen_policy: str = 'exclude',
    radii_model: str = 'vdw',
    transit_policy: str = 'with_connectors',
    gate_intrusion_policy: str = 'flag_only',
    residence_tolerance: Any = puw.quantity(0.0, 'angstroms'),
    permeability_tolerance: Any = puw.quantity(0.0, 'angstroms'),
    dry_adjacency: str = 'face',
    mesh_config: DFNDMeshConfig | None = None,
    query: DFNDQuery | None = None,
) -> Topography:
    """Run DFND and promote compatibility components into a ``Topography`` object.

    All DFND substrate (mesh, network, components) is attached to the single
    ``topography.dfnd`` object (see ``devguide/DFND/object_model.md``); the public
    top level holds only the promoted features. Direct calls to ``dfnd`` still
    return the raw-first dictionary used for method development and validation.
    """
    _warn_bare_length_args(
        probe_radius=probe_radius,
        epsilon=epsilon,
        residence_tolerance=residence_tolerance,
        permeability_tolerance=permeability_tolerance,
    )
    network, result = _run_dfnd(
        molecular_system,
        selection,
        structure_indices,
        probe_radius,
        min_size,
        epsilon,
        hydrogen_policy,
        radii_model,
        transit_policy,
        gate_intrusion_policy,
        residence_tolerance,
        permeability_tolerance,
        dry_adjacency,
        mesh_config,
        query,
    )
    topography = Topography(
        molecular_system=molecular_system,
        selection=network.mesh_config.selection,
        structure_indices=network.mesh_config.structure_indices,
    )
    topography.dfnd = DFNDData(network, result)

    # Promote each wet component to a concavity feature, and each of its mouth motifs
    # (external links) to a child Mouth feature. The local component_id remains a
    # display selector; contextual provenance uses component_key.
    components = topography.dfnd.dfn.components
    for family_key, default_class in _FEATURE_CLASS_BY_FAMILY.items():
        for record in result['wet'][family_key]:
            component = components.get(f'WET-{record["id"]}')
            # Promote by the catalog classification -- feature_type IS the classification
            # (decision S5.2). The only split within a topological family is the 1-mouth
            # bucket: an OPEN concavity (occlusion <= 1) is OpenConcavity, the occluded
            # case stays Pocket; every other family's classification == its name.
            name = (getattr(component, 'classification', None) or {}).get('name')
            feature_class = _FEATURE_CLASS_BY_NAME.get(name, default_class)
            feature = _feature_from_component_record(record, feature_class)
            feature.component_id = f'WET-{record["id"]}'
            feature.source_id = feature.component_key
            # Carry the interface descriptor (orthogonal axis) from the typed
            # component onto the public feature, so an interface is catalogued as
            # one. See devguide/DFND/interfaces.md.
            if component is not None:
                feature.is_interface = bool(getattr(component, 'is_interface', False))
                feature.interface_family = getattr(component, 'interface_family', None)
                feature.lining_bodies = list(getattr(component, 'lining_bodies', []))
                # Carry the catalog layer onto the public feature (front 1.a:
                # DFND component -> layer 0). The morphological classification
                # (pocket / open_concavity / ...) is an ADDITIVE attribute that
                # coexists with feature_type; the viewer keys on it (front 1.b).
                # Grounded measurements and the motifs ride along too.
                feature.classification = dict(getattr(component, 'classification', {}))
                feature.morphometrics = dict(getattr(component, 'morphometrics', {}))
                feature.boundary = dict(getattr(component, 'boundary', {}))
                feature.motifs = list(getattr(component, 'motifs', []))
                # The grounded, name-free signature (for consumers that key on
                # topology, not names -- survives family retirement).
                signature = getattr(component, 'signature', None)
                if signature is not None:
                    feature.signature = dict(signature)
                # Past-beach wetted contact (coast/shore/beach): the dry pockets the
                # probe wets THROUGH permeable wet-dry faces, and the solvent volume
                # the probe can reach (residence + those pockets).
                feature.beach_pocket = dict(getattr(component, 'beach_pocket', {}))
                accessible = getattr(component, 'volume_solvent_accessible', None)
                if accessible is not None:
                    feature.volume_solvent_accessible = puw.quantity(
                        accessible, 'nm**3'
                    )
                # The probe-accessible atoms a ligand here can interact with: the
                # component lining + the past-beach atoms 'kissed' in the dry coast.
                feature.accessible_atom_indices = list(
                    getattr(component, 'accessible_atom_indices', [])
                )
            topography.add_feature(feature)
            if family_key not in _FAMILIES_WITH_MOUTHS:
                continue
            for link in record['mouths']:
                mouth = Mouth(
                    atom_indices=list(link['atom_indices']),
                    source='dfnd',
                    source_id=link['external_link_key'],
                )
                mouth.component_id = feature.component_id
                mouth.component_key = feature.component_key
                mouth.parent_component_key = feature.component_key
                mouth.external_link_id = link['external_link_id']
                mouth.external_link_support_key = link['external_link_support_key']
                mouth.external_link_key = link['external_link_key']
                mouth.external_link_record = link
                mouth.face_ids = list(link.get('face_ids', []))
                mouth.tetrahedron_ids = list(link.get('tetrahedron_ids', []))
                mouth.faces = [list(face) for face in link.get('faces', [])]
                mouth.flags = list(link.get('flags', []))
                mouth.area = puw.quantity(link['area_geometric'], 'nm**2')
                mouth.R_gate_min = puw.quantity(link['R_gate_min'], 'nm')
                mouth.R_gate_mean = puw.quantity(link['R_gate_mean'], 'nm')
                mouth.R_gate_max = puw.quantity(link['R_gate_max'], 'nm')
                topography.add_feature(mouth)
                topography.connect_features(mouth, feature)

    return topography


def dfnd(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    probe_radius: Any = puw.quantity(1.4, 'angstroms'),
    min_size: int = 0,
    epsilon: Any = puw.quantity(1e-6, 'angstroms'),
    hydrogen_policy: str = 'exclude',
    radii_model: str = 'vdw',
    transit_policy: str = 'with_connectors',
    gate_intrusion_policy: str = 'flag_only',
    residence_tolerance: Any = puw.quantity(0.0, 'angstroms'),
    permeability_tolerance: Any = puw.quantity(0.0, 'angstroms'),
    dry_adjacency: str = 'face',
    mesh_config: DFNDMeshConfig | None = None,
    query: DFNDQuery | None = None,
) -> dict[str, dict[str, Any]]:
    """Run the DFND topography decomposition (raw-first dictionary)."""
    _warn_bare_length_args(
        probe_radius=probe_radius,
        epsilon=epsilon,
        residence_tolerance=residence_tolerance,
        permeability_tolerance=permeability_tolerance,
    )
    _network, raw_topography = _run_dfnd(
        molecular_system,
        selection,
        structure_indices,
        probe_radius,
        min_size,
        epsilon,
        hydrogen_policy,
        radii_model,
        transit_policy,
        gate_intrusion_policy,
        residence_tolerance,
        permeability_tolerance,
        dry_adjacency,
        mesh_config,
        query,
    )

    pockets = [
        _feature_from_component_record(pocket_data, Pocket)
        for pocket_data in raw_topography['wet']['pockets']
    ]
    voids = [
        _feature_from_component_record(void_data, Void)
        for void_data in raw_topography['wet']['voids']
    ]
    channels = [
        _feature_from_component_record(channel_data, Channel)
        for channel_data in raw_topography['wet']['channels']
    ]
    percolatings = [
        _feature_from_component_record(percolating_data, Percolating)
        for percolating_data in raw_topography['wet']['percolatings']
    ]

    return {
        'raw': raw_topography['raw'],
        'wet': {
            'pockets': pockets,
            'voids': voids,
            'channels': channels,
            'percolatings': percolatings,
            'surface_concavities': raw_topography['wet']['surface_concavities'],
            'nonresident_passages': raw_topography['wet']['nonresident_passages'],
            'degenerate_subprobes': raw_topography['wet']['degenerate_subprobes'],
        },
        'dry': raw_topography['dry'],
    }
