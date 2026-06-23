"""Internal sub-chamber hierarchy of wet components (the L1.3 resolution).

A wet component is one probe-connected region and is **never re-segmented**; its
nested topographic structure is exposed as a merge-tree descriptor -- basins
(``chamber_candidate``) joined by saddles (``throat_candidate``), each carrying a
physical ``separation_radius`` (the probe radius at which the sub-feature detaches
from its sibling). These toys are sealed voids built from smooth Fibonacci-sphere
walls, so the designed hierarchy is deterministic and dominates mesh noise:

- ``hollow_sphere``      -> one smooth cavity, no internal structure (control);
- ``dumbbell``           -> two equal lobes + one waist (symmetric, 2 chambers);
- ``asymmetric_dumbbell``-> a small chamber nested off a big one (distinct peaks);
- ``trilobed``           -> three lobes + two waists (a multi-level chain).
"""

import numpy as np

from topomt.dfnd import synthetic
from topomt.dfnd.components import _attach_capacity_motifs, build_components
from topomt.dfnd.graph import DelaunayFlowNetwork


def _topography(system, probe, transit_policy='with_connectors'):
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        np.asarray(system.coords, dtype=float),
        np.asarray(system.radii, dtype=float),
    )
    result = network.get_topography(probe_radius=probe, transit_policy=transit_policy)
    return network, result


def _wet_components(system, probe, transit_policy='with_connectors'):
    network, result = _topography(system, probe, transit_policy)
    return build_components(result, network)


def _with_hierarchy(components):
    return [c for c in components.wet if c.chamber_candidates or c.throat_candidates]


# --- the four casuistry fixtures -------------------------------------------


def test_single_void_has_no_internal_hierarchy():
    # Negative control: a smooth single cavity must NOT be over-segmented.
    for probe in (1.0, 1.4, 1.8, 2.2):
        assert _with_hierarchy(_wet_components(synthetic.hollow_sphere(), probe)) == []


def test_symmetric_bilobed_two_chambers_one_throat():
    structured = _with_hierarchy(_wet_components(synthetic.dumbbell(), 1.8))
    assert len(structured) == 1
    void = structured[0]
    assert void.family == 'void'
    assert len(void.chamber_candidates) == 2
    assert len(void.throat_candidates) == 1

    throat = void.throat_candidates[0]
    assert throat['separation_radius'] > 0
    assert throat['separation_radius'] == throat['R_gate']
    # the throat names exactly its two sibling chambers (navigable tree)
    assert set(throat['child_chamber_keys']) == {
        chamber['motif_key'] for chamber in void.chamber_candidates
    }
    # symmetric lobes detach at the same radius -> no forced parent/child asymmetry
    separations = {
        round(chamber['separation_radius'], 6) for chamber in void.chamber_candidates
    }
    assert len(separations) == 1
    assert void.bottleneck is throat


def test_asymmetric_bilobed_has_distinct_chamber_peaks():
    structured = _with_hierarchy(
        _wet_components(synthetic.asymmetric_dumbbell(jitter=0.0), 1.4)
    )
    assert len(structured) == 1
    void = structured[0]
    assert len(void.chamber_candidates) == 2
    assert len(void.throat_candidates) == 1
    peaks = sorted(c['peak_R_residence'] for c in void.chamber_candidates)
    # genuinely unequal chambers: a small sub-pocket nested off a large one
    assert peaks[1] - peaks[0] > 0.1
    # each chamber's prominence is its peak above the shared separation radius
    for chamber in void.chamber_candidates:
        assert chamber['persistence'] == (
            chamber['peak_R_residence'] - chamber['separation_radius']
        )


def test_linear_trilobed_three_chambers_two_throats():
    structured = _with_hierarchy(_wet_components(synthetic.trilobed(), 1.8))
    assert len(structured) == 1
    void = structured[0]
    assert len(void.chamber_candidates) == 3
    assert len(void.throat_candidates) == 2
    assert all(t['separation_radius'] > 0 for t in void.throat_candidates)
    # the chambers are sub-regions of the ONE component, not a partition of it
    node_set = set(void.node_indices)
    for chamber in void.chamber_candidates:
        assert set(chamber['node_ids']) <= node_set


# --- the invariant: characterize, do not partition --------------------------


def test_hierarchy_does_not_split_the_component():
    components = _wet_components(synthetic.dumbbell(), 1.8)
    voids = [c for c in components.wet if c.family == 'void']
    assert len(voids) == 1  # the bilobed cavity stays ONE wet component
    void = voids[0]
    node_set = set(void.node_indices)
    covered = set()
    for chamber in void.chamber_candidates:
        assert set(chamber['node_ids']) <= node_set
        covered |= set(chamber['node_ids'])
    # the two chambers are disjoint sub-regions (the throat is shared boundary,
    # not adjudicated to either) yet both live inside the single component
    chamber_nodes = [set(c['node_ids']) for c in void.chamber_candidates]
    assert chamber_nodes[0].isdisjoint(chamber_nodes[1])
    assert covered <= node_set


# --- tolerance / stability (validation_plan C4 + Q25 promotion evidence) -----


def test_chamber_count_is_stable_across_a_probe_window():
    # C4: no spurious jumps under a probe sweep. The physical scale is the probe.
    for system, n_chambers, n_throats in (
        (synthetic.dumbbell(), 2, 1),
        (synthetic.trilobed(), 3, 2),
    ):
        for probe in (1.4, 1.6, 1.8, 2.0, 2.2):
            structured = _with_hierarchy(_wet_components(system, probe))
            assert len(structured) == 1, (system, probe)
            void = structured[0]
            assert len(void.chamber_candidates) == n_chambers, (system, probe)
            assert len(void.throat_candidates) == n_throats, (system, probe)
    for probe in (1.4, 1.6, 1.8, 2.0, 2.2):
        assert _with_hierarchy(_wet_components(synthetic.hollow_sphere(), probe)) == []


def test_persistence_floor_prunes_without_over_segmentation():
    # The merge tree is gated by a single mesh-noise floor (length units); raising
    # it past the toy's throat prominence prunes the sub-chambers (no spurious
    # over-segmentation), and the structure is recovered below it. This is the
    # tolerance-stability evidence behind the throat/chamber promotion gate (Q25).
    network, result = _topography(synthetic.dumbbell(), 1.8)
    components = build_components(result, network)
    void = _with_hierarchy(components)[0]
    prominence = void.throat_candidates[0]['persistence']

    _attach_capacity_motifs(components, result, min_persistence=prominence + 0.05)
    assert [c for c in components.wet if c.throat_candidates] == []

    _attach_capacity_motifs(components, result, min_persistence=prominence * 0.5)
    recovered = [c for c in components.wet if c.throat_candidates][0]
    assert len(recovered.chamber_candidates) == 2
    assert len(recovered.throat_candidates) == 1
