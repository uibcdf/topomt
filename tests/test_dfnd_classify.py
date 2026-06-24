"""The catalog classifier (topomt/dfnd/classify.py) -- the single naming source.

``classify_topology`` is the topological family from the grounded signature (the
phase-1 inversion); ``classify`` is the additive morphological layer that refines
the 1-mouth resident family into pocket/groove by occlusion. Both are pure
functions of the grounded measurements; the component attaches them as
``component.classification`` alongside the (unchanged) ``component.family``.
"""

import numpy as np

from topomt.dfnd import families as fam
from topomt.dfnd import synthetic
from topomt.dfnd.classify import OPEN_CONCAVITY, classify, classify_topology
from topomt.dfnd.components import build_components
from topomt.dfnd.graph import DelaunayFlowNetwork


def test_classify_topology_reproduces_every_family():
    assert classify_topology(0, 1, 5) == fam.VOID
    assert classify_topology(0, 0, 5) == fam.DEGENERATE_SUBPROBE
    assert classify_topology(1, 1, 5) == fam.POCKET
    assert classify_topology(1, 0, 5) == fam.SURFACE_CONCAVITY
    assert classify_topology(2, 1, 5) == fam.CHANNEL
    assert classify_topology(2, 0, 5) == fam.NONRESIDENT_PASSAGE
    # resident with no enclosing wall faces -> percolating override
    assert classify_topology(1, 1, 0) == fam.PERCOLATING


def test_classify_splits_one_mouth_pocket_by_occlusion():
    assert classify(1, 1, 5, occlusion=2.0)['name'] == fam.POCKET  # occluded
    assert classify(1, 1, 5, occlusion=0.8)['name'] == OPEN_CONCAVITY  # open
    # occlusion is name-determining only for one mouth (S5 criterion)
    assert classify(2, 1, 5, occlusion=0.5)['name'] == fam.CHANNEL
    # other families pass through unchanged
    assert classify(0, 1, 5)['name'] == fam.VOID
    assert classify(1, 1, 5, occlusion=None)['name'] == fam.POCKET


def test_classify_flags_marginal_near_the_pocket_groove_boundary():
    assert classify(1, 1, 5, occlusion=1.05)['marginal'] is True
    assert classify(1, 1, 5, occlusion=2.0)['marginal'] is False


def test_classify_confidence_is_per_threshold():
    # topological names are exact given the signature -> confidence 1.0 (their
    # probe-margin lives in characteristic_radii, not here; decision S7)
    assert classify(0, 1, 5)['confidence'] == 1.0  # void
    assert classify(2, 1, 5)['confidence'] == 1.0  # channel
    assert classify(1, 1, 0)['confidence'] == 1.0  # percolating
    # the morphological pocket/open_concavity call ramps with |occlusion - 1|
    assert classify(1, 1, 5, occlusion=2.0)['confidence'] == 1.0  # far -> full
    near = classify(1, 1, 5, occlusion=1.05)
    assert near['confidence'] < 0.1 and near['marginal'] is True  # near boundary


def _largest(system, probe, family):
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        np.asarray(system.coords, float), np.asarray(system.radii, float)
    )
    components = build_components(
        network.get_topography(probe_radius=probe, transit_policy='with_connectors'),
        network,
    )
    candidates = [c for c in components.wet if c.family == family and c.size >= 8]
    return max(candidates, key=lambda c: c.size) if candidates else None


def test_bridge_carries_catalog_layer_onto_features():
    # front 1.a: dfnd_to_topography promotes components to features that carry the
    # catalog layer (classification, morphometrics, boundary, motifs) -- additive,
    # feature_type unchanged; the viewer keys on feature.classification['name'].
    from topomt.get_topography import get_topography

    system = synthetic.to_molsysmt(
        synthetic.dumbbell().coords, synthetic.dumbbell().radii
    )
    topo = get_topography(system, method='dfnd', probe_radius=1.0)
    features = [
        topo[fid]
        for fid in topo
        if getattr(topo[fid], 'feature_type', None) in ('pocket', 'void', 'channel')
    ]
    assert features
    for feature in features:
        assert 'name' in feature.classification
        assert isinstance(feature.morphometrics, dict)
        assert 'n_connected_walls' in feature.boundary
        assert isinstance(feature.motifs, list)
    names = {f.classification['name'] for f in features}
    assert names <= {'pocket', 'open_concavity', 'void', 'channel'}
    assert 'pocket' in names  # the dumbbell's occluded lobe-pocket at probe 1.0


def test_component_classification_coexists_with_unchanged_family():
    # the open surface bowl keeps the topological family 'pocket' but the catalog
    # classification refines it to the generic 'open_concavity' -- additive,
    # family unchanged
    bowl = _largest(synthetic.surface_bowl(), 1.4, 'pocket')
    assert bowl is not None
    assert bowl.family == fam.POCKET
    assert bowl.classification['name'] == OPEN_CONCAVITY

    # an occluded pocket keeps family 'pocket' and classifies as 'pocket'
    pocket = _largest(synthetic.dumbbell(), 1.0, 'pocket')
    assert pocket.family == fam.POCKET
    assert pocket.classification['name'] == fam.POCKET
