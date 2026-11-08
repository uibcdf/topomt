"""Original feature kinds stay distinct from native Topography admission."""

import pytest

from topomt.provider_output import ProviderRun
from topomt.third_party.output import ProviderGeometry, ProviderOutput, ProviderRecord


def test_original_feature_access_does_not_invent_pockets(tmp_path):
    source = tmp_path / 'source.pdb'
    source.write_text('REMARK Protocol fixture\n')
    run = ProviderRun.capture('fixture', 'files', source, tmp_path / 'absent')
    output_type = type('OriginalOutput', (ProviderOutput,), {'provider': 'fixture'})
    kinds = ('pocket', 'cavity', 'channel', 'site', 'mouth_aggregate')
    geometry = ProviderGeometry(
        'centerline', ((1.0, 2.0, 3.0),), 'Ordered path', (0.1,)
    )
    records = tuple(
        ProviderRecord(kind, kind, run, _geometries=(geometry,)) for kind in kinds
    )
    output = output_type(run, records)
    for kind, group in [
        ('pocket', output.pockets),
        ('cavity', output.cavities),
        ('channel', output.channels),
        ('site', output.sites),
    ]:
        assert tuple(record.source_id for record in group) == (kind,)
    assert output.channels[0].geometries['centerline'].radii_nm == (0.1,)
    with pytest.raises(ValueError, match='supported kind'):
        ProviderRecord('invalid', 'native_void', run)
