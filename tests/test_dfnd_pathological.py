"""Pathological synthetic systems: cases where DFND currently FAILS.

These are not success benchmarks. Each test pins the *current, wrong* behaviour of
DFND on a system whose correct answer is known, and documents what the answer
*should* be. They are regression markers: when DFND is improved (better
multi-scale segmentation, degeneracy handling, noise filtering), these tests will
start failing and must be updated to assert the corrected behaviour.

See ``devguide/DFND/pathological_systems.md``.
"""

from collections import Counter

import numpy as np

from topomt.dfnd.graph import DelaunayFlowNetwork
from topomt.dfnd import synthetic as syn
from topomt.dfnd.core.clearance import tetrahedron_residence_radius


def _domains(coords, radii, probe_radius=1.4):
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    return network.get_topography(probe_radius=probe_radius, min_size=0)['raw']['wet_components']


def _significant_families(domains, min_residents=5):
    return Counter(d['family'] for d in domains if d['n_resident_nodes'] >= min_residents)


def test_known_failure_deep_narrow_well_fragments_into_a_stack_of_pockets():
    # SHOULD BE: one pocket (a single deep blind well).
    # CURRENTLY: the narrow lumen fragments into several stacked pockets along its
    # depth -- single-scale segmentation cannot keep a deep narrow concavity whole.
    coords, radii = syn.blind_well(well_radius=3.0, depth=14.0, seed=0)
    families = _significant_families(_domains(coords, radii))

    assert families['pocket'] >= 3          # fragmented (ideal: 1)


def test_known_failure_long_pore_loses_through_connectivity():
    # SHOULD BE: one channel (multi_external_link) joining both faces.
    # CURRENTLY: the long thin lumen does not stay connected, so no through-channel
    # is found -- it collapses into separate one-mouth pockets at each end.
    coords, radii = syn.slab_with_pore(pore_radius=3.0, thickness=14.0, seed=0)
    families = _significant_families(_domains(coords, radii))

    assert families['multi_external_link'] == 0   # connectivity lost (ideal: 1)
    assert families['pocket'] >= 2


def test_known_failure_flat_slab_emits_spurious_enclosed_voids():
    # SHOULD BE: zero cavities (a flat, purely convex surface -- a negative control).
    # CURRENTLY: at spacing 4.0 the grid wall produces false enclosed voids between
    # surface atoms -- false positives a real detector must not emit.
    coords, radii = syn.flat_slab(extent=20.0, thickness=4.0, spacing=4.0, seed=0)
    families = _significant_families(_domains(coords, radii))

    assert families['void'] >= 1            # spurious voids (ideal: 0)


def test_known_failure_perfect_lattice_is_unstable_under_tiny_perturbation():
    # SHOULD BE: stable -- a 0.1 A perturbation must not change the topology.
    # CURRENTLY: a perfect cubic lattice is massively cospherical/coplanar (WP4
    # Delaunay degeneracy), so the jittered and unjittered cubes give different
    # family counts.
    perfect = _significant_families(_domains(*syn.hollow_cube(8.0, 3.5, jitter=0.0, seed=0)))
    jittered = _significant_families(_domains(*syn.hollow_cube(8.0, 3.5, jitter=0.1, seed=0)))

    assert dict(perfect) != dict(jittered)         # unstable (ideal: identical)


def test_known_failure_two_convex_bodies_make_a_phantom_pocket():
    # SHOULD BE: zero cavities (two convex balls have no pocket).
    # CURRENTLY: the concave saddle in the open space between the two bodies is
    # reported as a large pocket -- a false positive when a single-structure
    # detector meets two bodies.
    coords, radii = syn.two_balls(ball_radius=6.0, gap=8.0, seed=0)
    domains = _domains(coords, radii)

    pockets = [d for d in domains
               if d['family'] == 'pocket' and d['n_resident_nodes'] >= 5]
    assert pockets                                 # phantom pocket (ideal: none)
    assert max(p['volume_solvent_estimate'] for p in pockets) > 200.0


def test_known_failure_same_cavity_classified_differently_by_sampling_density():
    # SHOULD BE: one family -- the cavity is the same geometry at every wall
    # sampling. CURRENTLY: at fixed probe (1.4), varying only the wall point
    # density reclassifies the SAME sphere as void / pocket / channel, because
    # sparser walls leak the probe. Detection depends on sampling, not geometry.
    families = set()
    for spacing in (3.0, 3.4, 4.0, 4.3, 4.6):
        coords, radii = syn.hollow_sphere(10.0, spacing, jitter=0.1, seed=0)
        families.update(d['family'] for d in _domains(coords, radii)
                        if d['n_resident_nodes'] >= 5)
    assert len(families) >= 2                      # unstable classification (ideal: 1)


def test_known_failure_thin_gap_between_plates_fragments_into_voids():
    # SHOULD BE: an open slot or one feature. CURRENTLY: a 3 A gap between two
    # plates fragments into several spurious enclosed voids.
    coords, radii = syn.parallel_plates(separation=3.0, seed=0)
    families = _significant_families(_domains(coords, radii))

    assert families['void'] >= 1            # spurious voids (ideal: 0)


def test_known_failure_void_volume_is_overestimated():
    # SHOULD BE: close to the analytic empty interior. CURRENTLY: the solvent
    # volume estimate overshoots the analytic inner ball by ~40%.
    coords, radii = syn.hollow_sphere(10.0, 3.5, jitter=0.1, seed=0)
    void = next(d for d in _domains(coords, radii) if d['family'] == 'void')

    analytic = 4.0 / 3.0 * np.pi * (10.0 - syn.ARGON_VDW_RADIUS) ** 3
    assert void['volume_solvent_estimate'] / analytic > 1.3   # overestimate (ideal: ~1.0)


def test_known_failure_thin_tube_is_not_recognized_as_a_channel():
    # SHOULD BE: one channel (an open tube). CURRENTLY: a thin tube fragments into
    # pockets with no through-channel -- and the nonresident_passage family that
    # should cover a passable-but-not-residable lumen never appears.
    coords, radii = syn.cylinder_tube(length=16.0, tube_radius=2.5, wall_spacing=3.0, jitter=0.1, seed=0)
    families = _significant_families(_domains(coords, radii))

    assert families['multi_external_link'] == 0   # no channel (ideal: 1)
    assert families['pocket'] >= 2


def test_known_failure_nonuniform_sampling_flips_a_closed_cavity_open():
    # SHOULD BE: a void (the cavity is geometrically closed). CURRENTLY: making one
    # hemisphere's wall sparsely sampled leaks the probe and the SAME closed cavity
    # is reclassified as an open channel -- the realistic, within-one-body version
    # of the sampling-density failure.
    dense = _significant_families(_domains(*syn.hollow_sphere(10.0, 3.0, jitter=0.1, seed=0)))
    patchy = _significant_families(_domains(*syn.hollow_sphere_patchy(10.0, 3.0, 0.6, seed=0)))

    assert dense['void'] == 1                     # dense wall -> closed void
    assert patchy['void'] == 0                    # sparse wall -> not a void
    assert patchy['multi_external_link'] >= 1     # leaks open (ideal: still a void)


def test_known_failure_radius_distribution_changes_classification():
    # SHOULD BE: stable -- the geometry is identical. CURRENTLY: on the SAME
    # coordinates, different per-atom radius distributions reclassify the cavity as
    # void / pocket / channel (R_gate is exact only for equal radii).
    coords, _uniform = syn.hollow_sphere(10.0, 4.0, jitter=0.1, seed=0)
    rng = np.random.default_rng(0)
    families = set()
    for low, high in [(1.4, 2.4), (1.0, 2.8), (0.7, 3.2)]:
        radii = rng.uniform(low, high, len(coords))
        families.update(d['family'] for d in _domains(coords, radii)
                        if d['n_resident_nodes'] >= 5)
    assert len(families) >= 2                            # radius-driven instability (ideal: 1)


def test_known_failure_element_encoded_mixed_radii_changes_class():
    # The PDB-shareable version of the radius failure: the SAME wall atoms, given
    # noble-gas mixed radii (encoded by element) vs uniform argon, are classified
    # differently. Confirms the radius model alone changes the answer, on a system
    # that survives a PDB round trip.
    coords, mixed_radii, _elements = syn.mixed_radii_shell(10.0, 4.3, seed=0)
    uniform_radii = np.full(len(coords), syn.ARGON_VDW_RADIUS)

    uniform = _significant_families(_domains(coords, uniform_radii))
    mixed = _significant_families(_domains(coords, mixed_radii))
    assert dict(uniform) != dict(mixed)                  # radius model flips the class


def test_known_failure_marginal_residence_flickers_under_noise():
    # SHOULD BE: stable. CURRENTLY: a tetrahedron sized so R_residence ~ probe
    # (edge 5.4 -> ~1.43) flips resident/non-resident under a 0.2 A jitter -- the
    # cavity exists or not depending on noise, near the residence threshold.
    resident = [tetrahedron_residence_radius(*syn.tetrahedron(edge=5.4, jitter=0.2, seed=s)).radius >= 1.4
                for s in range(10)]
    assert 0 < sum(resident) < 10                        # flickers (ideal: all-or-nothing stable)


def test_known_failure_marginal_gate_flickers_under_noise():
    # SHOULD BE: one stable family. CURRENTLY: a sphere whose wall gate sits at the
    # probe threshold (spacing 4.2) is classified void / pocket / channel depending
    # only on the jitter seed.
    signatures = set()
    for seed in range(8):
        coords, radii = syn.hollow_sphere(11.0, 4.2, jitter=0.2, seed=seed)
        families = _significant_families(_domains(coords, radii), min_residents=1)
        signatures.add(tuple(sorted(families.items())))
    assert len(signatures) >= 3                          # unstable (ideal: 1)


def test_known_failure_more_features_appear_at_a_larger_probe():
    # SHOULD BE: a bigger probe finds no MORE features. CURRENTLY: the dumbbell
    # yields 2 significant domains at probe 1.4 but 5 at probe 2.0 -- spurious
    # over-fragmentation grows with probe, so feature count is not monotone.
    coords, radii = syn.dumbbell(7.0, 12.5, 3.5, jitter=0.1, seed=0)
    n_small = sum(1 for d in _domains(coords, radii, probe_radius=1.4) if d['n_resident_nodes'] >= 5)
    n_big = sum(1 for d in _domains(coords, radii, probe_radius=2.0) if d['n_resident_nodes'] >= 5)
    assert n_big > n_small                               # more features at bigger probe (ideal: <=)


def test_known_failure_isolated_outlier_atom_creates_a_phantom_pocket():
    # SHOULD BE: an isolated far atom adds nothing. CURRENTLY: appending one atom
    # far away spans huge Delaunay slivers and produces a spurious extra domain.
    coords, radii = syn.hollow_sphere(10.0, 3.5, jitter=0.1, seed=0)
    base = sum(1 for d in _domains(coords, radii) if d['n_resident_nodes'] >= 5)

    far_coords = np.vstack([coords, [100.0, 100.0, 100.0]])
    far_radii = np.append(radii, syn.ARGON_VDW_RADIUS)
    with_outlier = sum(1 for d in _domains(far_coords, far_radii) if d['n_resident_nodes'] >= 5)
    assert with_outlier > base                           # phantom feature (ideal: equal)


def test_robustness_classification_is_stable_across_epsilon():
    # A mechanism DFND HANDLES: the tolerance knob does not change the result.
    coords, radii = syn.hollow_sphere(11.0, 4.5, jitter=0.1, seed=0)
    families = set()
    for epsilon in (1e-9, 1e-7, 1e-5, 1e-3, 1e-2):
        network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=epsilon)
        domains = network.get_topography(probe_radius=1.4, min_size=0)['raw']['wet_components']
        families.add(tuple(sorted(_significant_families(domains).items())))
    assert len(families) == 1                            # epsilon-robust


def test_robustness_extreme_probes_degrade_cleanly():
    # A mechanism DFND HANDLES: a too-large probe vanishes cleanly (no junk), and a
    # probe that still fits keeps the void.
    coords, radii = syn.hollow_sphere(10.0, 3.5, jitter=0.1, seed=0)
    assert _significant_families(_domains(coords, radii, probe_radius=5.0))['void'] == 1
    assert len(_domains(coords, radii, probe_radius=8.0)) == 0


def _significant_pockets(domains, min_residents=5):
    return [d for d in domains
            if d['family'] == 'pocket' and d['n_resident_nodes'] >= min_residents]


def test_known_failure_oblate_slit_void_fragments():
    # SHOULD BE: one void (a thin sealed disk). CURRENTLY: the anisotropic cavity
    # fragments into two voids plus surface texture.
    families = _significant_families(_domains(*syn.oblate_void(7.0, 2.0, seed=0)))
    assert families['void'] >= 2                  # fragmented (ideal: 1)


def test_known_failure_tapering_cone_is_not_one_channel():
    # SHOULD BE: one channel/pocket. CURRENTLY: the lumen crosses the residence
    # threshold along the taper and fragments into pockets, with no channel.
    families = _significant_families(_domains(*syn.conical_channel(6.0, 1.5, 16.0, seed=0)))
    assert families['multi_external_link'] == 0
    assert families['pocket'] >= 2


def test_known_failure_star_void_lobes_fragment():
    # SHOULD BE: one void (a central chamber with arms). CURRENTLY: the lobes
    # fragment into several pockets and the void is not even the dominant domain.
    domains = _domains(*syn.star_void(seed=0))
    dominant = max(domains, key=lambda d: d['n_resident_nodes'])
    assert dominant['family'] != 'void'    # lobes fragment off the core
    assert len(_significant_pockets(domains)) >= 3


def test_known_failure_toroidal_void_splits_in_two():
    # SHOULD BE: one (genus-1) void. CURRENTLY: the donut cavity splits into two
    # separate voids -- topology is not preserved.
    families = _significant_families(_domains(*syn.toroidal_void(seed=0)))
    assert families['void'] >= 2                  # split (ideal: 1)


def test_known_failure_u_channel_is_not_connected_as_a_channel():
    # SHOULD BE: one channel with two mouths on the same face. CURRENTLY: the
    # U-tunnel is not recognised as a channel and even yields a spurious void.
    families = _significant_families(_domains(*syn.u_channel(seed=0)))
    assert families['multi_external_link'] == 0   # connectivity lost (ideal: 1)


def test_known_failure_pocket_in_pocket_has_no_hierarchy():
    # SHOULD BE: a pocket with a nested sub-pocket (~2 features, hierarchical).
    # CURRENTLY: it over-segments into many flat pockets with no nesting.
    pockets = _significant_pockets(_domains(*syn.pocket_in_pocket(seed=0)))
    assert len(pockets) >= 4                             # over-segmented (ideal: ~2 nested)


def test_known_failure_edge_cavity_fragments():
    # SHOULD BE: one pocket at the block corner. CURRENTLY: the peripheral cavity
    # fragments into several pockets (it does not crash on the hull, at least).
    pockets = _significant_pockets(_domains(*syn.edge_cavity(seed=0)))
    assert len(pockets) >= 3                             # fragmented (ideal: 1)


def test_robustness_thin_septum_keeps_two_voids_apart():
    # A mechanism DFND HANDLES: even a 1 A internal wall keeps two sealed chambers
    # as two distinct voids (it does not bleed them together).
    families = _significant_families(_domains(*syn.two_chambers_septum(4.5, 1.0, seed=0)))
    assert families['void'] == 2


def test_known_failure_loosely_packed_blob_sprays_phantom_voids():
    # SHOULD BE: zero cavities (a solid blob has none). CURRENTLY: a loosely packed
    # blob (gaps between atoms) sprays many phantom voids -- the false-positive rate
    # is a steep function of packing density. This is the headline noise number.
    domains = _domains(*syn.packed_blob(12.0, 3.8, seed=0))
    significant = [d for d in domains if d['n_resident_nodes'] >= 5]
    assert len(significant) >= 5                         # phantom features (ideal: 0)


def test_robustness_densely_packed_blob_has_no_phantom_features():
    # A mechanism DFND HANDLES: at true vdW contact (atoms overlapping, like a real
    # structure) a solid blob produces no spurious features -- the false-positive
    # problem largely vanishes at realistic packing.
    domains = _domains(*syn.packed_blob(12.0, 3.0, seed=0))
    assert [d for d in domains if d['n_resident_nodes'] >= 5] == []


def test_known_failure_coarse_grained_shell_leaks_instead_of_sealing():
    # SHOULD BE: a void. CURRENTLY: a coarse-grained closed shell (few large beads,
    # the CA-only / low-resolution case) leaks the probe through uneven sampling and
    # is misclassified as open.
    coords, _r = syn.hollow_sphere(12.0, 5.0, jitter=0.1, seed=0)
    radii = np.full(len(coords), 2.5)                    # large CG beads
    families = _significant_families(_domains(coords, radii))
    assert families['void'] == 0                  # leaks (ideal: 1 void)
