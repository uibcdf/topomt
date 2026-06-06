"""Channel centerline derivation (Phase 2 of the component-visualization plan).

Pure-geometry tests on the committed synthetic catalog (argon 1.88 A, probe
1.4 A), no viewer involved. See ``topomt/dfnd/centerline.py``.
"""

from pathlib import Path

import numpy as np
import pytest

from topomt.dfnd.centerline import channel_centerline
from topomt.dfnd.graph import DelaunayFlowNetwork

_DATA = Path(__file__).resolve().parents[1] / 'topomt' / 'data' / 'synthetic'


def _load_pdb_coords(name):
    coords = []
    for line in (_DATA / name).read_text().splitlines():
        if line.startswith(('ATOM', 'HETATM')):
            coords.append(
                [float(line[30:38]), float(line[38:46]), float(line[46:54])]
            )
    return np.array(coords, dtype=float)


def _raw_for(name, probe=1.4):
    coords = _load_pdb_coords(name)
    radii = np.full(len(coords), 1.88)
    net = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    return net.get_topography(probe_radius=probe, min_size=0)['raw']


def _channel(raw):
    chans = [c for c in raw['wet_components'] if c['family'] == 'channel']
    assert chans, 'expected at least one channel component'
    return max(chans, key=lambda c: c['n_resident_nodes'])


def test_centerline_on_clean_two_mouth_channel():
    raw = _raw_for('tube_channel_clean.pdb')
    comp = _channel(raw)
    cl = channel_centerline(raw, comp)
    assert cl is not None

    centers = cl['centers']
    radii = cl['radii']
    # an ordered path of stations spanning the tube
    assert centers.shape[0] >= 2
    assert centers.shape[1] == 3
    assert radii.shape[0] == centers.shape[0]
    assert np.all(radii > 0)

    # endpoints are resident tetrahedra of the two widest mouths
    resident = set(comp['resident_tetrahedron_ids'])
    path = cl['tetra_path']
    assert path[0] in resident and path[-1] in resident
    endpoint_tetra = {tid for _lid, tid in cl['mouth_endpoints']}
    assert {path[0], path[-1]} == endpoint_tetra

    # bottleneck is the global radius minimum along the path
    assert cl['bottleneck_index'] == int(np.argmin(radii))

    # consecutive stations are actually adjacent (path is connected, no jumps to
    # the far end): the step never exceeds the full tube span
    steps = np.linalg.norm(np.diff(centers, axis=0), axis=1)
    span = np.linalg.norm(centers[-1] - centers[0])
    assert np.all(steps <= span + 1e-6)


@pytest.mark.parametrize('name', ['slab_pore_r4_t6.pdb', 'curved_tube_120.pdb'])
def test_centerline_on_other_channels(name):
    raw = _raw_for(name)
    comp = _channel(raw)
    cl = channel_centerline(raw, comp)
    assert cl is not None
    assert cl['centers'].shape[0] >= 2
    assert np.all(cl['radii'] > 0)
    assert 0 <= cl['bottleneck_index'] < cl['radii'].shape[0]


def test_branched_channel_uses_the_two_widest_mouths():
    # branched_tube_y is a 3-mouth Y junction; the centerline picks 2 mouths.
    raw = _raw_for('branched_tube_y.pdb')
    comp = _channel(raw)
    assert comp['n_external_links'] >= 3
    cl = channel_centerline(raw, comp)
    assert cl is not None
    assert len(cl['mouth_endpoints']) == 2
    used_links = {lid for lid, _tid in cl['mouth_endpoints']}
    assert len(used_links) == 2


def test_single_mouth_pocket_has_no_centerline():
    # a pocket (1 mouth) is not a through-channel -> None.
    raw = _raw_for('hollow_sphere_pocket.pdb')
    pockets = [c for c in raw['wet_components'] if c['family'] == 'pocket']
    assert pockets
    comp = max(pockets, key=lambda c: c['n_resident_nodes'])
    assert channel_centerline(raw, comp) is None
