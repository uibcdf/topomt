"""Morphology discriminators on wet components (the topology -> morphology bridge).

A DFND ``pocket`` is purely topological (one mouth + residence). The public
feature layer refines it into a morphological type from these descriptors. The
key discriminator is **enclosability**: an occluded pocket's interior is wider
than its mouth, so as the probe grows the mouth seals while the interior still
holds the probe -> the pocket becomes a void; a groove's mouth is its widest
point, so it loses mouth and residence together and never becomes a void.

Because ``R_residence`` and ``R_gate`` are probe-independent, this is a single
query comparison (``interior_radius`` vs ``mouth_radius``), not a probe sweep --
the sweep would give the same verdict at higher cost (and can undersample).
"""

import numpy as np

from topomt.dfnd import synthetic
from topomt.dfnd.components import build_components
from topomt.dfnd.graph import DelaunayFlowNetwork


def _wet(system, probe):
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        np.asarray(system.coords, dtype=float),
        np.asarray(system.radii, dtype=float),
    )
    return build_components(
        network.get_topography(probe_radius=probe, transit_policy='with_connectors'),
        network,
    )


def _largest(components, family, min_size=1):
    candidates = [
        c for c in components.wet if c.family == family and c.size >= min_size
    ]
    return max(candidates, key=lambda c: c.size) if candidates else None


def test_enclosable_pocket_has_occlusion_above_one():
    # The dumbbell at a small probe is one pocket whose interior is far wider than
    # its waist mouth: occlusion >> 1, enclosable (it seals into a void).
    pocket = _largest(_wet(synthetic.dumbbell(), 1.0), 'pocket')
    assert pocket is not None
    m = pocket.morphometrics
    assert m['occlusion'] > 1.0
    assert m['enclosable'] is True
    assert m['occlusion_gap'] > 0.0
    assert m['interior_radius'] > m['mouth_radius']


def test_open_groove_has_occlusion_below_one():
    # A surface bowl is an open dent: the mouth is its widest point -> occlusion
    # < 1, not enclosable.
    pocket = _largest(_wet(synthetic.surface_bowl(), 1.4), 'pocket')
    assert pocket is not None
    m = pocket.morphometrics
    assert m['occlusion'] < 1.0
    assert m['enclosable'] is False
    assert m['occlusion_gap'] < 0.0


def test_void_has_no_mouth_relative_metrics():
    void = _largest(_wet(synthetic.hollow_sphere(), 1.4), 'void', min_size=8)
    assert void is not None
    m = void.morphometrics
    assert m['mouth_radius'] is None
    assert m['occlusion'] is None
    assert m['enclosable'] is None
    assert m['interior_radius'] > 0.0


def test_enclosability_agrees_with_an_actual_probe_sweep():
    # The static criterion must match a real sweep: the enclosable dumbbell pocket
    # becomes a void at a larger probe; the groove bowl never does.
    pocket = _largest(_wet(synthetic.dumbbell(), 1.0), 'pocket')
    assert pocket.morphometrics['enclosable'] is True
    assert _largest(_wet(synthetic.dumbbell(), 1.6), 'void', min_size=8) is not None

    bowl = _largest(_wet(synthetic.surface_bowl(), 1.4), 'pocket')
    assert bowl.morphometrics['enclosable'] is False
    for probe in (1.8, 2.2, 2.6, 3.0):
        assert _largest(_wet(synthetic.surface_bowl(), probe), 'void', min_size=8) is None


def test_buriedness_separates_shallow_from_deep():
    shallow = _largest(_wet(synthetic.edge_cavity(), 1.4), 'pocket')
    deep = _largest(_wet(synthetic.u_channel(), 1.4), 'pocket')
    assert shallow is not None and deep is not None
    assert shallow.morphometrics['buriedness'] < deep.morphometrics['buriedness']


def test_per_mouth_occlusion_is_one_value_per_mouth():
    # a channel reports an occlusion per mouth (entrance constriction per end)
    channel = next(
        (c for c in _wet(synthetic.cylinder_tube(), 1.4).wet if c.family == 'channel'),
        None,
    )
    assert channel is not None
    pmo = channel.morphometrics['per_mouth_occlusion']
    assert len(pmo) == len(channel.external_link_ids)

    # for a single-mouth pocket it collapses to the global occlusion
    pocket = _largest(_wet(synthetic.dumbbell(), 1.0), 'pocket')
    single = pocket.morphometrics['per_mouth_occlusion']
    assert len(single) == 1
    assert abs(single[0] - pocket.morphometrics['occlusion']) < 1e-9


def test_deepest_chamber_reads_a_buried_subpocket_from_the_hierarchy():
    # The compound case (a deep narrow sub-pocket behind a wider mouth, which the
    # global occlusion ratio can miss) is read off the merge-tree hierarchy, not a
    # new traversal: the dumbbell's far lobe is a chamber at depth>0 behind the
    # waist constriction (access_occlusion>1). A smooth single void has no internal
    # structure -> None. (Lattice toys grow spurious *shallow* chambers; depth
    # gates them, and the global occlusion stays the primary classifier -- this is
    # a supporting descriptor, not a standalone groove/pocket gate.)
    pocket = _largest(_wet(synthetic.dumbbell(), 1.0), 'pocket')
    deepest = pocket.morphometrics['deepest_chamber']
    assert deepest is not None
    assert deepest['topological_depth'] > 0  # genuinely buried
    assert deepest['access_occlusion'] > 1.0  # the route to it narrows

    void = _largest(_wet(synthetic.hollow_sphere(), 1.4), 'void', min_size=8)
    assert void.morphometrics['deepest_chamber'] is None


def test_morphometrics_carry_shape_elongation():
    # elongation = ratio of the two largest PCA standard deviations of the residence
    # centers (>= 1; ~1 round, high = elongated) -- the grounded metric that refines
    # the generic open_concavity into the leaf groove (elongated + an axis).
    components = _wet(synthetic.cylinder_tube(), 1.4)  # an elongated tube
    elongated = max((c for c in components.wet if c.size >= 8), key=lambda c: c.size)
    metrics = elongated.morphometrics
    assert metrics['elongation'] is not None and metrics['elongation'] > 2.0
    axis = metrics['elongation_axis']
    assert isinstance(axis, list) and len(axis) == 3


def test_funnel_motif_detects_steady_narrowing():
    # the access-funnel motif: a steady, appreciable narrowing of the clearance (a
    # directing truncated cone) is a funnel; a uniform tube is not (flat gradient);
    # an occluded pocket widens inward, not a funnel (PROVISIONAL thresholds).
    cone = max(
        (c for c in _wet(synthetic.surface_funnel(), 1.4).wet if c.size >= 8),
        key=lambda c: c.size,
    )
    funnel = cone.morphometrics['funnel']
    assert funnel['is_funnel'] is True
    assert funnel['gradient'] < 0 and funnel['steadiness'] >= 0.8

    tube = max(
        (c for c in _wet(synthetic.cylinder_tube(), 1.4).wet if c.size >= 8),
        key=lambda c: c.size,
    )
    assert tube.morphometrics['funnel']['is_funnel'] is False  # a uniform tube
