import numpy as np

from topomt.third_party.castp3._native_impl import castp as _native_castp


def get_topography(molecular_system, **kwargs):
    """Run the local CASTp native implementation and return a Topography."""

    from topomt import Topography
    from topomt import pyunitwizard as puw

    feature_records, mesh = _native_castp(molecular_system, **kwargs)
    del mesh

    topography = Topography(molecular_system=molecular_system)

    for feature_index, record in enumerate(feature_records, start=1):
        feature_type = record.get('feature_type', 'pocket')
        source_id = record.get('source_id', f'castp:{feature_type}:{feature_index}')

        parent_feature_id = topography.add_new_feature(
            feature_type=feature_type,
            atom_indices=sorted(record.get('atom_indices', [])),
            source='castp',
            source_id=source_id,
        )
        parent_feature = topography[parent_feature_id]

        if 'center' in record and record['center'] is not None:
            parent_feature.center = puw.quantity(
                np.asarray(record['center']) / 10.0, 'nm'
            )
        if 'area' in record and record['area'] is not None:
            parent_feature.area = puw.quantity(float(record['area']) / 100.0, 'nm**2')
        if 'volume' in record and record['volume'] is not None:
            parent_feature.volume = puw.quantity(
                float(record['volume']) / 1000.0, 'nm**3'
            )
        if 'mouth_area' in record and record['mouth_area'] is not None:
            parent_feature.mouth_area = puw.quantity(
                float(record['mouth_area']) / 100.0, 'nm**2'
            )
        if 'mouth_perimeter' in record and record['mouth_perimeter'] is not None:
            parent_feature.mouth_perimeter = puw.quantity(
                float(record['mouth_perimeter']) / 10.0, 'nm'
            )
        if 'n_mouths' in record:
            parent_feature.n_mouths = record['n_mouths']
        if 'iT' in record:
            parent_feature.iT = record['iT']
        if 'tetrahedron_indices' in record:
            parent_feature.tetrahedron_indices = record['tetrahedron_indices']
        if 'properties' in record:
            parent_feature.properties = record['properties']
        if 'score' in record:
            parent_feature.score = record['score']

        for mouth in record.get('mouths', []):
            mouth_feature_id = topography.add_new_feature(
                feature_type='mouth',
                atom_indices=sorted(mouth.get('atom_indices', [])),
                source='castp',
                source_id=f'{source_id}:mouth:{mouth["id"]}',
                area=puw.quantity(float(mouth.get('area', 0.0)) / 100.0, 'nm**2'),
            )
            topography.connect_features(mouth_feature_id, parent_feature_id)

    return topography
