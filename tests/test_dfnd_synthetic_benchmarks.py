"""Synthetic-shape benchmarks for DFND with known ground truth.

Dummy argon atoms arranged in simple geometries whose topography is known by
construction: a sealed hollow sphere is one enclosed void, an open tube is a
channel, a filled ball has no cavity. See
``devguide/DFND/synthetic_benchmarks.md``. A small fixed-seed jitter breaks the
exact cosphericity/lattice degeneracy so the triangulation is portable.
"""

import numpy as np

from topomt.dfnd.graph import DelaunayFlowNetwork
from topomt.dfnd import synthetic as syn


def _domains(coords, radii, probe_radius=1.4):
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    return network.get_topography(probe_radius=probe_radius, min_size=0)['raw']['wet_components']


def test_hollow_sphere_is_a_single_enclosed_void():
    coords, radii = syn.hollow_sphere(sphere_radius=10.0, wall_spacing=3.5, jitter=0.1, seed=0)
    domains = _domains(coords, radii)

    voids = [d for d in domains if d['family'] == 'void']
    assert len(voids) == 1

    void = voids[0]
    assert void['n_external_links'] == 0          # sealed -> no exterior access
    assert void['has_residence'] is True
    # Empty interior ~ inner ball of radius (R - r_atom) ≈ 8.1 -> ~2200-3100 A^3.
    assert 1000.0 < void['volume_solvent_estimate'] < 5000.0


def test_hollow_tube_is_a_multi_mouth_channel():
    coords, radii = syn.cylinder_tube(length=20.0, tube_radius=6.0, wall_spacing=3.5, jitter=0.1, seed=0)
    domains = _domains(coords, radii)

    channels = [d for d in domains if d['family'] == 'channel']
    assert channels

    main = max(channels, key=lambda d: d['n_resident_nodes'])
    assert main['n_external_links'] >= 2          # open tube -> at least two mouths
    assert main['has_residence'] is True


def test_solid_ball_has_no_significant_cavity():
    # Negative control: a filled ball must not produce an enclosed void or any
    # large interior cavity (only tiny surface-texture pockets).
    coords, radii = syn.solid_ball(ball_radius=8.0, spacing=3.5, jitter=0.1, seed=0)
    domains = _domains(coords, radii)

    assert all(d['family'] != 'void' for d in domains)
    assert all(d['volume_solvent_estimate'] < 5.0 for d in domains)


def test_sphere_with_opening_is_a_pocket():
    coords, radii = syn.hollow_sphere_with_opening(
        sphere_radius=10.0, wall_spacing=3.5, opening_half_angle_deg=30.0, jitter=0.1, seed=0
    )
    domains = _domains(coords, radii)

    pockets = [d for d in domains if d['family'] == 'pocket']
    assert len(pockets) == 1
    pocket = pockets[0]
    assert pocket['n_external_links'] == 1        # one opening -> one mouth
    assert pocket['has_residence'] is True


def _topography(coords, radii, probe_radius=1.4):
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    return network.get_topography(probe_radius=probe_radius, min_size=0)


def _lining_body_span(coords, domain):
    # Bodies in the block systems are split by the sign of x; count lining atoms
    # contributed by each body (the multi-body-lining interface discriminator).
    xs = coords[domain['atom_indices'], 0]
    return int(np.sum(xs < 0)), int(np.sum(xs > 0))


def _significant_voids(domains, min_residents=5):
    return [
        d for d in domains
        if d['family'] == 'void' and d['n_resident_nodes'] >= min_residents
    ]


def test_dumbbell_throat_splits_void_as_probe_grows():
    # Volume vs connectivity (DFND's distinctive demonstration): two chambers
    # joined by a throat. A small probe sees one connected void; a larger probe
    # is blocked at the throat, so the same geometry becomes two separate voids.
    coords, radii = syn.dumbbell(lobe_radius=7.0, separation=12.5, wall_spacing=3.5, jitter=0.1, seed=0)

    small = _domains(coords, radii, probe_radius=1.4)
    large = _domains(coords, radii, probe_radius=2.2)
    assert len(_significant_voids(small)) == 1    # connected through the throat
    assert len(_significant_voids(large)) == 2    # throat closed -> two chambers


def test_blind_well_is_a_single_pocket():
    # A cylindrical well bored into a solid slab: one mouth -> one dominant pocket,
    # no enclosed void. (Grid surface texture adds only tiny extra pockets.)
    coords, radii = syn.blind_well(well_radius=6.0, depth=8.0, seed=0)
    domains = _domains(coords, radii)

    assert all(d['family'] != 'void' for d in domains)
    dominant = max(domains, key=lambda d: d['n_resident_nodes'])
    assert dominant['family'] == 'pocket'
    assert dominant['n_external_links'] == 1
    assert dominant['volume_solvent_estimate'] > 300.0


def test_slab_pore_is_a_through_channel():
    # A pore drilled through a slab connects both faces: a single multi-mouth
    # channel dominates (>=2 external links).
    coords, radii = syn.slab_with_pore(pore_radius=4.0, thickness=6.0, seed=0)
    domains = _domains(coords, radii)

    channels = [d for d in domains if d['family'] == 'channel']
    assert len(channels) == 1
    assert channels[0]['n_external_links'] >= 2
    assert channels[0] is max(domains, key=lambda d: d['n_resident_nodes'])


def test_two_disjoint_voids_are_counted_separately():
    # Two well-separated hollow spheres must stay two distinct enclosed voids.
    coords, radii = syn.two_voids(sphere_radius=8.0, gap=14.0, seed=0)
    domains = _domains(coords, radii)

    voids = [d for d in domains
             if d['family'] == 'void' and d['n_resident_nodes'] >= 5]
    assert len(voids) == 2
    v0, v1 = sorted(v['volume_solvent_estimate'] for v in voids)
    assert v1 - v0 < 0.2 * v1                     # the two voids are ~equal in size


def test_surface_bowl_is_an_open_pocket_with_surface_texture():
    # A spherical dent in a slab is an open concavity (a pocket, never a void).
    # The grid wall also produces several tiny "texture" pockets between surface
    # atoms -- a deliberately studied phenomenon, not enclosed cavities.
    coords, radii = syn.surface_bowl(bowl_radius=9.0, depth=6.0, seed=0)
    domains = _domains(coords, radii)

    assert all(d['family'] != 'void' for d in domains)
    pockets = [d for d in domains if d['family'] == 'pocket']
    assert len(pockets) >= 2                       # one real bowl + surface texture
    dominant = max(pockets, key=lambda d: d['n_resident_nodes'])
    texture = [p for p in pockets if p is not dominant]
    assert dominant['n_resident_nodes'] > 10 * max(t['n_resident_nodes'] for t in texture)


def test_branched_tube_is_a_three_mouth_channel():
    # A Y junction of three open tubes is one channel with three mouths.
    coords, radii = syn.branched_tube(arm_length=11.0, tube_radius=5.0, seed=0)
    domains = _domains(coords, radii)

    channels = [d for d in domains if d['family'] == 'channel']
    assert len(channels) == 1
    assert channels[0]['n_external_links'] == 3
    assert channels[0] is max(domains, key=lambda d: d['n_resident_nodes'])


def test_nested_spheres_are_two_separate_voids():
    # A hollow sphere inside a hollow sphere: the core and the shell gap are two
    # distinct enclosed voids (nested-cavity separation).
    coords, radii = syn.nested_spheres(outer_radius=14.0, inner_radius=7.0, seed=0)
    domains = _domains(coords, radii)

    voids = [d for d in domains
             if d['family'] == 'void' and d['n_resident_nodes'] >= 5]
    assert len(voids) == 2


def test_curved_tube_is_a_two_mouth_channel():
    # Channel detection must not depend on the channel being straight.
    coords, radii = syn.curved_tube(bend_radius=12.0, arc_deg=120.0, tube_radius=5.0, seed=0)
    domains = _domains(coords, radii)

    channels = [d for d in domains if d['family'] == 'channel']
    assert len(channels) == 1
    assert channels[0]['n_external_links'] >= 2
    assert channels[0] is max(domains, key=lambda d: d['n_resident_nodes'])


def test_flask_neck_gates_the_chamber():
    # A narrow neck seals the chamber into an enclosed void (the throat closes);
    # widening the neck opens it, so the void disappears (throat/gating behavior).
    narrow, narrow_r = syn.flask(neck_radius=2.5, seed=0)
    wide, wide_r = syn.flask(neck_radius=5.0, seed=0)

    n_void_narrow = sum(1 for d in _domains(narrow, narrow_r) if d['family'] == 'void')
    n_void_wide = sum(1 for d in _domains(wide, wide_r) if d['family'] == 'void')
    assert n_void_narrow >= 1          # narrow neck -> chamber sealed as a void
    assert n_void_wide == 0            # wide neck -> open pocket, no void


def test_second_mouth_must_exceed_a_size_threshold_to_count():
    # Two openings of unequal size: a pinhole second mouth (10 deg) does not
    # register -> pocket; a larger second mouth (25 deg) does -> channel.
    pinhole, pinhole_r = syn.hollow_sphere_two_openings(
        opening1_half_angle_deg=35.0, opening2_half_angle_deg=10.0, seed=0)
    open2, open2_r = syn.hollow_sphere_two_openings(
        opening1_half_angle_deg=35.0, opening2_half_angle_deg=25.0, seed=0)

    pinhole_dom = max(_domains(pinhole, pinhole_r), key=lambda d: d['n_resident_nodes'])
    open2_dom = max(_domains(open2, open2_r), key=lambda d: d['n_resident_nodes'])
    assert pinhole_dom['family'] == 'pocket'
    assert pinhole_dom['n_external_links'] == 1
    assert open2_dom['family'] == 'channel'
    assert open2_dom['n_external_links'] >= 2


def test_asymmetric_dumbbell_throat_splits_void_as_probe_grows():
    # Like the symmetric dumbbell but with unequal chambers (throat offset from the
    # midpoint): one void at a small probe, two at a larger probe.
    coords, radii = syn.asymmetric_dumbbell(lobe_radius1=8.0, lobe_radius2=5.0, separation=11.0, seed=0)
    assert len(_significant_voids(_domains(coords, radii, probe_radius=1.4))) == 1
    assert len(_significant_voids(_domains(coords, radii, probe_radius=2.2))) == 2


def test_swiss_cheese_percolates_into_one_cluster():
    # Overlapping carved voids merge and reach the surface: instead of many
    # separate voids, DFND reports one dominant connected cavity (a mega-cluster).
    coords, radii = syn.swiss_cheese(block_half=11.0, void_radius=4.5, void_spacing=7.0, seed=0)
    domains = _domains(coords, radii)

    assert len(_significant_voids(domains)) == 0          # not a set of isolated voids
    dominant = max(domains, key=lambda d: d['n_resident_nodes'])
    assert dominant['n_resident_nodes'] > 300
    assert dominant['family'] in {'pocket', 'channel'}


def test_void_with_island_is_still_one_void():
    # A solid island inside a hollow sphere: the cavity wraps around it. DFND v1
    # reports a single void (it does not track the cavity's genus/topology).
    coords, radii = syn.void_with_island(sphere_radius=11.0, island_radius=3.0, seed=0)
    voids = [d for d in _domains(coords, radii)
             if d['family'] == 'void' and d['n_resident_nodes'] >= 5]
    assert len(voids) == 1


def test_helical_tube_is_a_two_mouth_channel():
    # A channel following a 3D helix is still one channel with two mouths.
    coords, radii = syn.helical_tube(turns=1.5, helix_radius=8.0, pitch=10.0, tube_radius=4.5, seed=0)
    domains = _domains(coords, radii)

    channels = [d for d in domains if d['family'] == 'channel']
    assert len(channels) == 1
    assert channels[0]['n_external_links'] >= 2
    assert channels[0] is max(domains, key=lambda d: d['n_resident_nodes'])


def test_onion_shells_are_three_nested_voids():
    # Three concentric shells -> a core void plus two shell-gap voids = three voids.
    coords, radii = syn.onion_shells(radii=(18.0, 12.0, 6.0), seed=0)
    voids = [d for d in _domains(coords, radii)
             if d['family'] == 'void' and d['n_resident_nodes'] >= 5]
    assert len(voids) == 3


def test_flat_sheet_has_no_false_tunnel_or_void():
    # Adversarial: a flat sheet's Delaunay slivers have huge circumradii, so
    # alpha-shape detectors can invent a tunnel through it. DFND scores in-sphere
    # clearance, so it must report no enclosed void and no through-channel.
    coords, radii = syn.sliver_sheet(extent=18.0, spacing=3.5, seed=0)
    domains = _domains(coords, radii)

    assert all(d['family'] != 'void' for d in domains)
    significant_channels = [d for d in domains
                            if d['family'] == 'channel'
                            and d['n_resident_nodes'] >= 5]
    assert significant_channels == []


def test_dumbbell_fusion_separation_flips_in_a_narrow_probe_window():
    # Fusion/separation sensitivity: tuned so a 0.1 A probe change flips the throat.
    # Unlike a binary fits/doesn't-fit detector, DFND resolves the transition.
    coords, radii = syn.dumbbell(lobe_radius=7.0, separation=12.5, wall_spacing=3.5, jitter=0.1, seed=0)
    assert len(_significant_voids(_domains(coords, radii, probe_radius=1.5))) == 1   # fused
    assert len(_significant_voids(_domains(coords, radii, probe_radius=1.6))) == 2   # separated


def test_mouth_intruder_atom_seals_a_pocket_into_a_void():
    # A single atom in the mouth flips a pocket into a sealed void. A detector that
    # scores only the 3-atom wall gate (ignoring the 4th intruding atom) misses this.
    open_coords, open_radii = syn.pocket_with_mouth_intruder(intruder=False, seed=0)
    sealed_coords, sealed_radii = syn.pocket_with_mouth_intruder(intruder=True, seed=0)

    open_dom = max(_domains(open_coords, open_radii), key=lambda d: d['n_resident_nodes'])
    sealed_dom = max(_domains(sealed_coords, sealed_radii), key=lambda d: d['n_resident_nodes'])
    assert open_dom['family'] == 'pocket'
    assert sealed_dom['family'] == 'void'


def test_void_detection_is_orientation_invariant():
    # A Delaunay method must not depend on the molecule's orientation (grid/voxel
    # detectors do). The same hollow sphere rotated arbitrarily gives the same void.
    base_coords, radii = syn.hollow_sphere(sphere_radius=10.0, wall_spacing=3.5, jitter=0.1, seed=0)
    results = []
    for angles in [(0, 0, 0), (37, 0, 0), (0, 52, 0), (23, 41, 67)]:
        domains = _domains(syn.rotate(base_coords, angles), radii)
        voids = [d for d in domains if d['family'] == 'void']
        assert len(voids) == 1
        results.append((voids[0]['n_resident_nodes'], voids[0]['volume_solvent_estimate']))

    residents = {r for r, _v in results}
    volumes = [v for _r, v in results]
    assert len(residents) == 1                                  # identical resident count
    assert max(volumes) - min(volumes) < 1e-6                   # identical volume


def test_cryptic_chamber_is_revealed_only_by_a_smaller_probe():
    # A gated chamber: at the water probe (1.4) the neck is sealed, so it reads as a
    # buried, inaccessible void; a smaller probe (1.0) opens the neck and reveals an
    # accessible pocket. Static single-probe detectors miss the accessibility.
    coords, radii = syn.flask(neck_radius=3.0, neck_length=2.5, seed=0)

    sealed = max(_domains(coords, radii, probe_radius=1.4), key=lambda d: d['n_resident_nodes'])
    opened = max(_domains(coords, radii, probe_radius=1.0), key=lambda d: d['n_resident_nodes'])
    assert sealed['family'] == 'void'
    assert sealed['n_external_links'] == 0                      # inaccessible at 1.4
    assert opened['family'] == 'pocket'
    assert opened['n_external_links'] >= 1                      # accessible at 1.0


def test_rough_surface_sprays_tiny_spurious_features():
    # Surface roughness produces many sub-probe dimples -> a spray of tiny spurious
    # domains (micro pockets and voids). None is a real cavity. Documents the
    # over-reporting / noise regime that downstream filtering must handle.
    coords, radii = syn.rough_surface(extent=20.0, amplitude=1.3, seed=0)
    domains = _domains(coords, radii)

    assert len(domains) > 15                                    # many spurious features
    assert max(d['n_resident_nodes'] for d in domains) < 40     # but none is a real cavity


def test_two_blocks_form_two_dry_bodies_with_a_shared_wet_interface():
    # Two blocks separated by a solvent-wide gap: two dry banks (dry components)
    # plus a wet interface region in the gap lined by atoms from BOTH bodies.
    coords, radii = syn.two_blocks(gap=5.0, seed=0)
    topo = _topography(coords, radii)

    big_dry = [c for c in topo['dry']['components'] if c['size'] >= 50]
    assert len(big_dry) == 2                       # two dry banks emerge at this gap

    domains = topo['raw']['wet_components']
    dominant = max(domains, key=lambda d: d['n_resident_nodes'])
    left, right = _lining_body_span(coords, dominant)
    assert left >= 5 and right >= 5                # wet interface lined by both bodies


def test_three_blocks_form_three_dry_bodies():
    # Three blocks in a row -> three dry banks and (by construction) two interfaces.
    coords, radii = syn.three_blocks(gap=5.0, seed=0)
    topo = _topography(coords, radii)

    big_dry = [c for c in topo['dry']['components'] if c['size'] >= 50]
    assert len(big_dry) == 3


def test_interface_pocket_is_lined_by_both_bodies():
    # A cavity carved at the contact plane of two blocks: the buried pocket's
    # lining is contributed by both bodies. That multi-body lining -- not the
    # mouth count -- is what marks it an interface cavity (vs an ordinary pocket).
    coords, radii = syn.interface_pocket(gap=2.0, pocket_radius=6.0, seed=0)
    domains = _topography(coords, radii)['raw']['wet_components']

    dominant = max(domains, key=lambda d: d['n_resident_nodes'])
    left, right = _lining_body_span(coords, dominant)
    assert left >= 10 and right >= 10              # spans both bodies
    minority = min(left, right) / (left + right)
    assert minority > 0.3                          # genuinely shared, not single-body texture


def test_interface_pocket_with_a_mouth_is_an_open_interface_pocket():
    # A mouth bored from the buried interface cavity to the surface: now a one-mouth
    # pocket, still lined by both bodies (an accessible interface pocket).
    coords, radii = syn.interface_pocket(gap=2.0, pocket_radius=6.0, mouth=True, seed=0)
    domains = _topography(coords, radii)['raw']['wet_components']

    dominant = max(domains, key=lambda d: d['n_resident_nodes'])
    assert dominant['family'] == 'pocket'
    assert dominant['n_external_links'] == 1
    left, right = _lining_body_span(coords, dominant)
    assert left >= 10 and right >= 10


def test_three_body_junction_cavity_is_lined_by_three_bodies():
    # Three blocks meeting at 120 deg with a central cavity: the cavity's lining is
    # contributed by all three bodies (a three-way interface junction).
    coords, radii = syn.three_body_junction(place_radius=9.0, pocket_radius=5.5, seed=0)
    domains = _topography(coords, radii)['raw']['wet_components']

    dominant = max(domains, key=lambda d: d['n_resident_nodes'])
    angle = np.arctan2(coords[dominant['atom_indices'], 1], coords[dominant['atom_indices'], 0])
    sectors = (np.round(angle / (2.0 * np.pi / 3.0)) % 3).astype(int)
    per_body = [int(np.sum(sectors == k)) for k in range(3)]
    assert all(count >= 10 for count in per_body)  # all three bodies line the cavity


def test_probe_sweep_wall_seals_the_larger_probe():
    # Counterintuitive but correct: a larger probe cannot pass the wall gaps, so
    # it is the one that gets enclosed. At wall_spacing 4.5 the gaps leak a 1.0 A
    # probe (it escapes -> not a void) but seal a 1.8 A probe (enclosed void).
    coords, radii = syn.hollow_sphere(sphere_radius=12.0, wall_spacing=4.5, jitter=0.1, seed=0)

    small = _domains(coords, radii, probe_radius=1.0)
    large = _domains(coords, radii, probe_radius=1.8)

    n_void_small = sum(1 for d in small if d['family'] == 'void')
    n_void_large = sum(1 for d in large if d['family'] == 'void')
    assert n_void_small == 0          # small probe leaks through the wall gaps
    assert n_void_large >= 1          # larger probe cannot pass -> enclosed void


def test_rotate_is_not_wrapped_as_a_synthetic_system_builder():
    assert not hasattr(syn.rotate, "__wrapped__")
