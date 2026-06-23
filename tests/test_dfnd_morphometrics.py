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
