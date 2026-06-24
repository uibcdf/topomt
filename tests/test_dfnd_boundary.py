"""Derived boundary measurements per wet component (the grounded boundary layer).

The boundary of a wet component splits into mouths (permeable, to OCEAN) and walls
(non-permeable). ``n_connected_walls`` clusters the walls; it subsumes the binary
``exposed`` flag (``== 0`` is percolating). ``n_dry_contacts`` counts the distinct
dry banks lining the component (``interface`` = ``>= 2``). See
``_attach_boundary_helpers`` and taxonomy_architecture_decision.md S4.
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


def _largest(components, family, min_size=8):
    candidates = [
        c for c in components.wet if c.family == family and c.size >= min_size
    ]
    return max(candidates, key=lambda c: c.size) if candidates else None


def test_enclosed_void_has_one_connected_wall():
    # a single hollow shell encloses the void with exactly one connected wall
    void = _largest(_wet(synthetic.hollow_sphere(), 1.4), 'void')
    assert void is not None
    assert void.boundary['n_connected_walls'] == 1
    assert void.boundary['n_dry_contacts'] == 0


def test_two_body_interface_has_two_walls_and_two_dry_contacts():
    # the wet slot between two solid blocks is lined by two separate walls (one per
    # block) and contacts two distinct dry banks -- the canonical interface
    components = _wet(synthetic.two_blocks_interface_slabs(), 1.4)
    slot = max(
        (c for c in components.wet if c.size >= 50),
        key=lambda c: c.size,
        default=None,
    )
    assert slot is not None
    assert slot.boundary['n_connected_walls'] == 2
    assert slot.boundary['n_dry_contacts'] == 2


def test_inter_cavity_constriction_is_counted_as_a_septum():
    # two chambers separated by a sub-probe pinch share a wet<->wet wall -- a
    # constriction / closed throat -- which is characterized as a septum
    components = _wet(synthetic.two_chambers_septum(4.5, 1.0, seed=0), 1.4)
    assert any(c.boundary['n_septa'] >= 1 for c in components.wet if c.size >= 8)


def test_signature_is_grounded_and_name_free():
    # the grounded signature references no family/classification names, so a
    # consumer (the component renderer) that keys on it survives family retirement
    void = _largest(_wet(synthetic.dumbbell(), 1.8), 'void')
    assert void is not None
    sig = void.signature
    assert set(sig) == {'n_mouths', 'resident', 'exposed', 'n_septa', 'branched'}
    assert sig['n_mouths'] == 0
    assert sig['resident'] is True

    channel = _largest(_wet(synthetic.cylinder_tube(), 1.4), 'channel')
    assert channel is not None
    assert channel.signature['n_mouths'] >= 2


def test_characteristic_radii_expose_grounded_transitions():
    # the classification transitions over probe, read from the probe-independent
    # grounded values (no sweep): seal = widest mouth gate, residence_death =
    # widest interior clearance; merge/split = constriction/throat radii
    pocket = _largest(_wet(synthetic.dumbbell(), 1.0), 'pocket')
    assert pocket is not None
    cr = pocket.characteristic_radii
    assert cr['seal_radius'] is not None and cr['seal_radius'] > 0
    # an occluded pocket: interior wider than the mouth
    assert cr['residence_death_radius'] >= cr['seal_radius']
    assert isinstance(cr['merge_radii'], list)
    assert isinstance(cr['split_radii'], list)

    # a void has no mouths -> no seal radius
    void = _largest(_wet(synthetic.dumbbell(), 1.8), 'void')
    assert void.characteristic_radii['seal_radius'] is None
    assert void.characteristic_radii['residence_death_radius'] is not None


def test_every_wet_component_has_boundary_counts():
    # the helper runs for all wet components and yields non-negative integer counts
    for component in _wet(synthetic.dumbbell(), 1.8).wet:
        b = component.boundary
        assert b['n_connected_walls'] >= 0
        assert b['n_dry_contacts'] >= 0
        assert b['n_septa'] >= 0
        assert len(b['walls']) == b['n_connected_walls']
