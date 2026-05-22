from typing import Any

from .graph import DelaunayFlowNetwork
from .. import pyunitwizard as puw
from ..features import Channel, Pocket, Void
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
        source_id=f"{source}:{record['domain_family']}:{record['id']}",
    )
    feature.domain_family = record['domain_family']
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


def dfnd_to_topography(
    molecular_system,
    selection: str = 'all',
    structure_indices: int = 0,
    **kwargs,
) -> Topography:
    """Run DFND and convert compatibility domains into a Topography object.

    The raw DFND records remain attached to the returned object as dfnd_records.
    Direct calls to dfnd still return the raw-first dictionary used for method
    development and validation.
    """
    result = dfnd(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        **kwargs,
    )
    topography = Topography(
        molecular_system=molecular_system,
        selection=selection,
        structure_indices=structure_indices,
    )
    topography.dfnd_records = result['raw']
    topography.dfnd_result = result
    topography.dfnd_concavity_domains = result['raw']['concavity_domains']
    topography.dfnd_external_links = result['raw']['external_links']
    topography.dfnd_dry_components = result['dry']['components']
    topography.dfnd_dry_interfaces = result['raw']['dry_interfaces']
    topography.dfnd_dry_motifs = result['raw']['dry_motifs']
    topography.dfnd_surface_concavities = result['wet']['surface_concavities']
    topography.dfnd_nonresident_passages = result['wet']['nonresident_passages']
    topography.dfnd_degenerate_subprobe_domains = result['wet'][
        'degenerate_subprobe_domains'
    ]

    for family_key, feature_class in _FEATURE_CLASS_BY_FAMILY.items():
        for feature_or_record in result['wet'][family_key]:
            if isinstance(feature_or_record, dict):
                feature = _feature_from_domain_record(feature_or_record, feature_class)
            else:
                feature = feature_or_record
            topography.add_feature(feature)

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
    """Run the DFND topography decomposition."""
    probe_radius = _as_angstrom_float(probe_radius)

    network = DelaunayFlowNetwork(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        epsilon=epsilon,
        hydrogen_policy=hydrogen_policy,
        radii_model=radii_model,
    )
    raw_topography = network.get_topography(
        probe_radius=probe_radius,
        sea_level=sea_level,
        min_size=min_size,
        transit_policy=transit_policy,
        gate_intrusion_policy=gate_intrusion_policy,
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
            'degenerate_subprobe_domains': raw_topography['wet'][
                'degenerate_subprobe_domains'
            ],
        },
        'dry': raw_topography['dry'],
    }
