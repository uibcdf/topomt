"""Characterization hashes for DFND raw records.

These tests protect behavior-preserving refactors of ``DelaunayFlowNetwork``.
They hash the complete canonical JSON raw record rather than a selected subset,
so changes in values, order, ids, rankings, schema, or records are caught.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from topomt.dfnd.graph import DelaunayFlowNetwork

_DATA = Path(__file__).resolve().parents[1] / 'topomt' / 'data' / 'synthetic'

_RAW_HASHES = {
    'tube_channel_clean.pdb': '419e09116f1bb8f013090bb57bc504d01c005c8745e6f64b15276f7ee6f16743',
    'hollow_sphere_void.pdb': '3cfa230bc8bac330ab39a59f2147e24707acb4d076e1d296e7861514a1815b8a',
    'hollow_sphere_pocket.pdb': '0cfbb19dea266ccdd1a46c19656972b1a25a65f91c08a710d9aebd59284dfc87',
    'two_blocks_interface.pdb': 'f29e462c930385e6ee8fde328c4f894672b035e14ff74ac5a41cc4a5ea340062',
}


def _load_pdb_coords(name: str) -> np.ndarray:
    coords = []
    for line in (_DATA / name).read_text().splitlines():
        if line.startswith(('ATOM', 'HETATM')):
            coords.append(
                [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            )
    return np.array(coords, dtype=float)


def _canonical_raw_hash(raw: dict) -> str:
    blob = json.dumps(raw, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(blob.encode()).hexdigest()


@pytest.mark.parametrize('name,expected_hash', sorted(_RAW_HASHES.items()))
def test_dfnd_raw_characterization_hash(name, expected_hash):
    coords = _load_pdb_coords(name)
    radii = np.full(len(coords), 1.88)
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords,
        radii,
        epsilon=1e-7,
    )

    raw = network.get_topography(probe_radius=1.4, min_size=0)['raw']

    assert raw['schema_version'] == 'dfnd.raw.nm.v2'
    assert _canonical_raw_hash(raw) == expected_hash
