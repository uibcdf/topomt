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
from topomt.dfnd.classify import GROOVE, classify, classify_topology
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
    assert classify(1, 1, 5, occlusion=0.8)['name'] == GROOVE  # open
    # occlusion is name-determining only for one mouth (S5 criterion)
    assert classify(2, 1, 5, occlusion=0.5)['name'] == fam.CHANNEL
    # other families pass through unchanged
    assert classify(0, 1, 5)['name'] == fam.VOID
    assert classify(1, 1, 5, occlusion=None)['name'] == fam.POCKET


def test_classify_flags_marginal_near_the_pocket_groove_boundary():
    assert classify(1, 1, 5, occlusion=1.05)['marginal'] is True
    assert classify(1, 1, 5, occlusion=2.0)['marginal'] is False


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


def test_component_classification_coexists_with_unchanged_family():
    # the open surface bowl keeps the topological family 'pocket' but the catalog
    # classification refines it to 'groove' -- additive, family unchanged
    bowl = _largest(synthetic.surface_bowl(), 1.4, 'pocket')
    assert bowl is not None
    assert bowl.family == fam.POCKET
    assert bowl.classification['name'] == GROOVE

    # an occluded pocket keeps family 'pocket' and classifies as 'pocket'
    pocket = _largest(synthetic.dumbbell(), 1.0, 'pocket')
    assert pocket.family == fam.POCKET
    assert pocket.classification['name'] == fam.POCKET
