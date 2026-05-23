from typing import Any

from .graph import DelaunayFlowNetwork
from .data import DFNDData
from .. import pyunitwizard as puw
from ..features import Channel, Mouth, Pocket, Void
from ..topography.Topography import Topography


_FEATURE_CLASS_BY_FAMILY = {
    'pockets': Pocket,
    'voids': Void,
    'channels': Channel,
}


def _as_angstrom_float(value) -> float:
    try:
        return float(puw.get_value(value, to_unit='angstroms'))
    except Exception:
        return float(value)


def _feature_from_domain_record(record: dict[str, Any], feature_class, source: str = 'dfnd'):
    feature = feature_class(
        atom_indices=record['atom_indices'],
        source=source,
        source_id=f"{source}:{record['family']}:{record['id']}",
    )
    feature.family = record['family']
    feature.tetrahedron_indices = record['tetrahedron_indices']
    feature.resident_tetrahedron_indices = record['resident_tetrahedron_indices']
    feature.transit_connector_tetrahedron_indices = record[
        'transit_connector_tetrahedron_indices'
    ]
    feature.center = puw.quantity(record['center'], 'angstroms')
    feature.volume_topological_resident = puw.quantity(
        record['volume_topological_resident'],
        'angstroms**3',
    )
    feature.volume_solvent_estimate = puw.quantity(
        record['volume_solvent_estimate'],
        'angstroms**3',
    )
    feature.n_mouths = record['n_mouths']
    feature.mouth_area = puw.quantity(record['mouth_area'], 'angstroms**2')
    feature.mouths = record['mouths']
    feature.mouth_face_clusters = record['mouth_face_clusters']
    feature.flags = record['flags']
    feature.raw_record = record
    return feature


def _run_dfnd(
    molecular_system,
    selection: str,
    structure_indices: int,
    probe_radius: float,
    sea_level: float | None,
    min_size: int,
    epsilon: float,
    hydrogen_policy: str,
    radii_model: str,
    transit_policy: str,
    gate_intrusion_policy: str,
) -> tuple[DelaunayFlowNetwork, dict[str, Any]]:
    """Build the network and run the decomposition. Shared by the public entry points."""
    network = DelaunayFlowNetwork(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        epsilon=epsilon,
        hydrogen_policy=hydrogen_policy,
        radii_model=radii_model,
    )
    result = network.get_topography(
        probe_radius=_as_angstrom_float(probe_radius),
        sea_level=sea_level,
        min_size=min_size,
        transit_policy=transit_policy,
        gate_intrusion_policy=gate_intrusion_policy,
    )
    return network, result


def dfnd_to_topography(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    probe_radius: float = 1.4,
    sea_level: float | None = None,
    min_size: int = 0,
    epsilon: float = 1e-6,
    hydrogen_policy: str = 'exclude',
    radii_model: str = 'vdw',
    transit_policy: str = 'with_connectors',
    gate_intrusion_policy: str = 'flag_only',
) -> Topography:
    """Run DFND and promote compatibility domains into a ``Topography`` object.

    All DFND substrate (mesh, network, components) is attached to the single
    ``topography.dfnd`` object (see ``devguide/DFND/object_model.md``); the public
    top level holds only the promoted features. Direct calls to ``dfnd`` still
    return the raw-first dictionary used for method development and validation.
    """
    network, result = _run_dfnd(
        molecular_system, selection, structure_indices, probe_radius, sea_level,
        min_size, epsilon, hydrogen_policy, radii_model, transit_policy,
        gate_intrusion_policy,
    )
    topography = Topography(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
    )
    topography.dfnd = DFNDData(network, result)

    # Promote each wet domain to a concavity feature, and each of its mouth motifs
    # (external links) to a child Mouth feature. Provenance: feature.component_id /
    # source_id point back to the dfnd component. See object_model.md sections 7.
    for family_key, feature_class in _FEATURE_CLASS_BY_FAMILY.items():
        for record in result['wet'][family_key]:
            feature = _feature_from_domain_record(record, feature_class)
            feature.component_id = f"WET-{record['id']}"
            feature.source_id = feature.component_id
            topography.add_feature(feature)
            for link in record['mouths']:
                mouth = Mouth(
                    atom_indices=list(link['atom_indices']),
                    source='dfnd',
                    source_id=f"dfnd:mouth:{link['external_link_id']}",
                )
                mouth.component_id = feature.component_id
                mouth.external_link_id = link['external_link_id']
                mouth.area = puw.quantity(link['area_geometric'], 'angstroms**2')
                topography.add_feature(mouth)
                topography.connect_features(mouth, feature)

    return topography


def dfnd(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    probe_radius: float = 1.4,
    sea_level: float | None = None,
    min_size: int = 0,
    epsilon: float = 1e-6,
    hydrogen_policy: str = 'exclude',
    radii_model: str = 'vdw',
    transit_policy: str = 'with_connectors',
    gate_intrusion_policy: str = 'flag_only',
) -> dict[str, dict[str, Any]]:
    """Run the DFND topography decomposition (raw-first dictionary)."""
    _network, raw_topography = _run_dfnd(
        molecular_system, selection, structure_indices, probe_radius, sea_level,
        min_size, epsilon, hydrogen_policy, radii_model, transit_policy,
        gate_intrusion_policy,
    )

    pockets = [
        _feature_from_domain_record(pocket_data, Pocket)
        for pocket_data in raw_topography['wet']['pockets']
    ]
    voids = [
        _feature_from_domain_record(void_data, Void)
        for void_data in raw_topography['wet']['voids']
    ]
    channels = [
        _feature_from_domain_record(channel_data, Channel)
        for channel_data in raw_topography['wet']['channels']
    ]

    return {
        'raw': raw_topography['raw'],
        'wet': {
            'pockets': pockets,
            'voids': voids,
            'channels': channels,
            'surface_concavities': raw_topography['wet']['surface_concavities'],
            'nonresident_passages': raw_topography['wet']['nonresident_passages'],
            'degenerate_subprobes': raw_topography['wet'][
                'degenerate_subprobes'
            ],
        },
        'dry': raw_topography['dry'],
    }
