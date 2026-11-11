"""Scientific evidence preserves JSON metadata alongside real quantities."""

import json

import numpy as np
import pyunitwizard as puw
from pyunitwizard import QuantityRecord

from devtools.benchlab.capture_volume import encode_quantities


def test_capture_preserves_bibliography_strings_and_quantity_units():
    metadata = {
        'version': '2.5.4',
        'issue': '7825',
        'pages': '357-362',
        'title': '1.4',
        'doi': '10.1038/s41586-020-2649-2',
    }
    value = {
        'attribution': metadata,
        'radius': puw.quantity(1.88, 'angstroms'),
        'indices': np.array([1, 2], dtype=np.int64).tolist(),
        'count': np.int64(77),
        'missing': None,
        'valid': True,
    }
    captured = json.loads(json.dumps(encode_quantities(value)))
    assert captured['attribution'] == metadata
    assert captured['count'] == 77 and captured['valid'] is True
    assert captured['indices'] == [1, 2] and captured['missing'] is None
    restored = QuantityRecord.from_dict(captured['radius']).to_quantity(
        field='radius', unit='angstroms'
    )
    np.testing.assert_allclose(puw.get_value(restored, to_unit='angstroms'), 1.88)
