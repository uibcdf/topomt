"""Tests for the interface-feature prototype (topomt.dfnd.interfaces).

Interfaces are derived from raw DFND topography by the multi-body-lining rule
(devguide/DFND/interfaces.md): a wet domain lined by atoms from >=2 bodies is an
interface. Bodies come either from the dry network (native route) or from
explicit per-atom labels (robust route for tightly packed, fused interfaces).
"""

import numpy as np

from topomt.dfnd.graph import DelaunayFlowNetwork
from topomt.dfnd import synthetic as syn
from topomt.dfnd import interfaces as ifc


def _topography(coords, radii, probe_radius=1.4):
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    return network.get_topography(probe_radius=probe_radius, min_size=0)


def test_native_route_flags_the_wet_gap_between_two_separated_blocks():
    # Solvent-wide gap -> two dry bodies emerge -> the wet gap pocket is flagged an
    # interface, with its lining shared between the two banks. No labels needed.
    coords, radii = syn.two_blocks(gap=5.0, seed=0)
    topo = _topography(coords, radii)

    interfaces = ifc.annotate_interfaces(topo, len(coords))
    assert len(interfaces) == 1
    record = interfaces[0]
    assert record['interface_family'] == 'interface_pocket'
    assert record['n_lining_bodies'] == 2
    assert min(record['lining_body_split'].values()) >= 10


def test_single_body_system_has_no_interface():
    # Negative control: one body (a hollow sphere) -> the native route finds one
    # dry component, so no domain can be a multi-body interface.
    coords, radii = syn.hollow_sphere(sphere_radius=10.0, wall_spacing=3.5, jitter=0.1, seed=0)
    topo = _topography(coords, radii)

    assert ifc.annotate_interfaces(topo, len(coords)) == []


def test_tight_interface_needs_explicit_labels():
    # Tightly packed blocks fuse into one dry component, so the native route misses
    # the interface cavity; explicit chain-like labels recover it as an interface
    # pocket plus a buried interface void (interfaces.md section 4).
    coords, radii = syn.interface_pocket(gap=2.0, pocket_radius=6.0, seed=0)
    topo = _topography(coords, radii)

    assert ifc.annotate_interfaces(topo, len(coords)) == []      # native route fuses -> misses it

    labels = (coords[:, 0] >= 0).astype(int)                     # left / right body
    interfaces = ifc.annotate_interfaces(topo, len(coords), body_labels=labels)
    families = {r['interface_family'] for r in interfaces}
    assert 'interface_pocket' in families
    assert 'interface_void' in families
    dominant = max(interfaces, key=lambda r: r['n_resident_nodes'])
    assert dominant['minority_fraction'] > 0.3                   # genuinely shared lining


def test_three_body_junction_cavity_has_three_lining_bodies():
    # The central cavity of three blocks is lined by all three bodies.
    coords, radii = syn.three_body_junction(place_radius=9.0, pocket_radius=5.5, seed=0)
    topo = _topography(coords, radii)

    angle = np.arctan2(coords[:, 1], coords[:, 0])
    labels = (np.round(angle / (2.0 * np.pi / 3.0)) % 3).astype(int)
    interfaces = ifc.annotate_interfaces(topo, len(coords), body_labels=labels)

    dominant = max(interfaces, key=lambda r: r['n_resident_nodes'])
    assert dominant['interface_family'] == 'interface_pocket'
    assert dominant['n_lining_bodies'] == 3
