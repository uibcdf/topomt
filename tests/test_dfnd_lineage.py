"""Cross-frame component matching (dynamic-identity layer). Pure post-processing
over the static component keys; no viewer, no trajectory engine."""

from pathlib import Path

import numpy as np

from topomt.dfnd.graph import DelaunayFlowNetwork
from topomt.dfnd.data import DFNDData
from topomt.dfnd.lineage import jaccard, match_results

_DATA = Path(__file__).resolve().parents[1] / 'topomt' / 'data' / 'synthetic'


def _wet_components(name, *, jitter=0.0, seed=0):
    coords = []
    for line in (_DATA / name).read_text().splitlines():
        if line.startswith(('ATOM', 'HETATM')):
            coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    coords = np.array(coords, dtype=float)
    if jitter:
        rng = np.random.default_rng(seed)
        coords = coords + rng.normal(scale=jitter, size=coords.shape)
    net = DelaunayFlowNetwork.from_arrays(coords, np.full(len(coords), 1.88), epsilon=1e-7)
    dfnd = DFNDData(net, net.get_topography(probe_radius=1.4, min_size=0))
    return list(dfnd.dfn.components.wet)


def test_jaccard_basic():
    assert jaccard({1, 2, 3}, {1, 2, 3}) == 1.0
    assert jaccard({1, 2}, {3, 4}) == 0.0
    assert jaccard(set(), set()) == 0.0
    assert jaccard({1, 2, 3, 4}, {3, 4}) == 0.5


def test_same_result_matches_every_component_exactly():
    comps = _wet_components('tube_channel_clean.pdb')
    matches = match_results(comps, comps)
    # every component matches itself by support_key, exactly
    by_a = {m['a']: m for m in matches}
    for c in comps:
        assert c.component_key in by_a
        m = by_a[c.component_key]
        assert m['exact'] is True
        assert m['jaccard'] == 1.0
        assert m['b'] == c.component_key  # matched to itself


def test_jittered_frame_matches_by_lining_overlap():
    frame_a = _wet_components('tube_channel_clean.pdb', jitter=0.0)
    frame_b = _wet_components('tube_channel_clean.pdb', jitter=0.15, seed=1)
    matches = match_results(frame_a, frame_b, min_jaccard=0.2)
    assert matches  # something matched across the perturbed frame
    # the largest component of A should correspond to a component of B by overlap
    big_a = max(frame_a, key=lambda c: len(c.atom_indices or []))
    big_matches = [m for m in matches if m['a'] == big_a.component_key]
    assert big_matches
    assert max(m['jaccard'] for m in big_matches) > 0.2


def test_match_accepts_dict_records():
    a = [{'component_key': 'A', 'support_key': 's1', 'atom_indices': [1, 2, 3]}]
    b = [
        {'component_key': 'B1', 'support_key': 's1', 'atom_indices': [1, 2, 3]},
        {'component_key': 'B2', 'support_key': 's9', 'atom_indices': [3, 4, 5]},
    ]
    matches = match_results(a, b, min_jaccard=0.2)
    # exact support match wins for A -> B1
    exact = [m for m in matches if m['exact']]
    assert exact == [{'a': 'A', 'b': 'B1', 'jaccard': 1.0, 'exact': True}]
