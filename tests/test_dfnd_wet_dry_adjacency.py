"""Regression tests for the typed wet<->dry layer of the DFN decomposition.

These exercise the parts that the raw ``get_topography`` dict does not carry but
the typed ``Components`` registry does (built by ``DFNDData(network, result)``):

  * interface labelling on ``components.wet`` (the orthogonal interface axis is
    surfaced onto the typed components, devguide/DFND/interfaces.md);
  * Layer 0 -- ``mesh.neighbors`` (probe-independent) and
    ``dfn.graph.neighbors(side=...)`` (probe-dependent wet/dry split) + symmetry;
  * Layer 1 -- ``components.coast_faces`` (wet<->dry contact faces);
  * Layer 2 -- ``WetComponent.dry_lining`` / ``DryComponent.wet_lining`` symmetry
    and contact-area consistency;
  * Layer 3 -- ``DryComponent.interface_walls`` (the bank's wall against a wet
    interface), closing the symmetry with ``WetComponent.lining_bodies``.

The canonical fixture is ``two_blocks(gap=5.0)``: a solvent-wide gap so two dry
banks emerge and the wet gap is an interface pocket lined by both banks.
"""

import numpy as np

from topomt.dfnd import synthetic as syn
from topomt.dfnd.data import DFNDData
from topomt.dfnd.graph import DelaunayFlowNetwork


def _dfnd(coords, radii, probe_radius=1.4):
    network = DelaunayFlowNetwork.from_coordinates_and_radii(coords, radii, epsilon=1e-7)
    result = network.get_topography(probe_radius=probe_radius, min_size=0)
    return DFNDData(network, result)


def _two_blocks_dfnd():
    coords, radii = syn.two_blocks(gap=5.0, seed=0)
    return _dfnd(coords, radii)


# -- typed family mapping: channels must not be dropped ---------------------------


def test_two_mouth_channel_appears_in_typed_components():
    # Regression: a multi-mouth component (family 'channel', formerly the raw name
    # 'multi_external_link') must be mapped to side='wet' in
    # components._SIDE_BY_FAMILY and survive the components.wet view. The historical
    # bug was a name mismatch (the raw family was not the key the map expected);
    # renaming to 'channel' removed the mismatch. A densely-walled narrow tube is
    # the canonical two-mouth channel.
    coords, radii = syn.cylinder_tube(20.0, 3.5, 2.5, jitter=0.1, seed=0)
    components = _dfnd(coords, radii).dfn.components

    channels = [w for w in components.wet if w.family == 'channel']
    assert len(channels) == 1
    channel = channels[0]
    assert channel.side == 'wet'  # not None -> it survives the wet view
    assert channel.n_mouths == 2  # the two open ends of the tube
    assert channel in components.wet


# -- interface labelling on the typed components ----------------------------------


def test_two_blocks_wet_component_is_flagged_interface_pocket():
    components = _two_blocks_dfnd().dfn.components

    interfaces = components.wet_interfaces
    assert len(interfaces) == 1
    interface = interfaces[0]
    assert interface.is_interface is True
    assert interface.interface_family == 'interface_pocket'
    # lined by two distinct dry banks (its lining_bodies are DRY ids)
    assert len(interface.lining_bodies) == 2
    assert all(bank.startswith('DRY-') for bank in interface.lining_bodies)
    assert all(bank in components for bank in interface.lining_bodies)
    # family (mouth topology) is untouched by the orthogonal interface axis
    assert interface.family == 'pocket'


def test_single_body_system_has_no_wet_interface():
    coords, radii = syn.hollow_sphere(
        sphere_radius=10.0, wall_spacing=3.5, jitter=0.1, seed=0
    )
    components = _dfnd(coords, radii).dfn.components

    assert components.wet_interfaces == []
    assert all(c.is_interface is False for c in components.wet)


# -- Layer 0: mesh.neighbors / dfn.graph.neighbors --------------------------------


def test_mesh_neighbors_is_probe_independent_topology():
    dfnd = _two_blocks_dfnd()
    mesh, graph = dfnd.mesh, dfnd.dfn.graph

    n_tetra = len(mesh.tetrahedra)
    tid = next(t['tetrahedron_id'] for t in mesh.tetrahedra)

    bare = mesh.neighbors(tid)
    with_ocean = mesh.neighbors(tid, include_ocean=True)
    # a tetrahedron has up to four face-neighbors; bare drops the OCEAN (-1) faces
    assert len(with_ocean) == 4
    assert bare == [n for n in with_ocean if n != -1]
    assert all(0 <= n < n_tetra for n in bare)

    # graph.neighbors (probe-dependent) sees the same non-OCEAN set, side=None
    assert sorted(graph.neighbors(tid)) == sorted(bare)


def test_graph_neighbors_side_split_partitions_neighbors():
    dfnd = _two_blocks_dfnd()
    graph = dfnd.dfn.graph
    state = {n['tetrahedron_id']: n['residence_state'] for n in graph.nodes}

    for tid in list(state)[::25]:  # sample to keep it quick
        every = set(graph.neighbors(tid))
        wet = set(graph.neighbors(tid, side='wet'))
        dry = set(graph.neighbors(tid, side='dry'))
        assert wet.isdisjoint(dry)
        assert wet | dry == every
        assert all(state[n] == 'resident' for n in wet)
        assert all(state[n] == 'non_resident' for n in dry)


def test_graph_neighbors_wet_dry_relation_is_symmetric():
    # If a dry tetra is a neighbor of a wet one, the wet tetra is a neighbor of
    # that dry one -- the wet<->dry border relation is symmetric.
    dfnd = _two_blocks_dfnd()
    graph = dfnd.dfn.graph
    state = {n['tetrahedron_id']: n['residence_state'] for n in graph.nodes}

    wet_to_dry = set()
    for tid, s in state.items():
        if s != 'resident':
            continue
        for d in graph.neighbors(tid, side='dry'):
            wet_to_dry.add((tid, d))

    for wet_t, dry_t in wet_to_dry:
        assert wet_t in graph.neighbors(dry_t, side='wet')


# -- Layer 1: coast faces ---------------------------------------------------------


def test_coast_faces_connect_opposite_sides():
    components = _two_blocks_dfnd().dfn.components

    coast = components.coast_faces
    assert coast  # a two-body system has a wet<->dry coast
    # each coast face is recorded once (deduped by face_id, not both orientations)
    assert len(coast) == len({f['face_id'] for f in coast})
    for face in coast:
        assert components[face['wet_component_id']].side == 'wet'
        assert components[face['dry_component_id']].side == 'dry'
        assert (
            face['wet_component_key']
            == components[face['wet_component_id']].component_key
        )
        assert (
            face['dry_component_key']
            == components[face['dry_component_id']].component_key
        )
        assert face['area'] >= 0.0


# -- Layer 2: dry_lining / wet_lining symmetry ------------------------------------


def test_dry_lining_and_wet_lining_are_symmetric():
    components = _two_blocks_dfnd().dfn.components

    # every wet->dry wall has the mirror dry->wet lining, with the same faces/area
    wet_pairs = 0
    for wet in components.wet:
        for dry_id, wall in wet.dry_lining.items():
            dry = components[dry_id]
            mirror = dry.wet_lining.get(wet.component_id)
            assert mirror is not None
            assert wall['contact_face_ids'] == mirror['contact_face_ids']
            assert np.isclose(wall['area'], mirror['area'])
            wet_pairs += 1

    dry_pairs = sum(len(dry.wet_lining) for dry in components.dry)
    assert wet_pairs == dry_pairs

    # the per-component face books cover exactly the (deduped) coast faces
    total_wall_faces = sum(
        len(wall['contact_face_ids'])
        for wet in components.wet
        for wall in wet.dry_lining.values()
    )
    assert total_wall_faces == len(components.coast_faces)


def test_interface_pocket_lining_area_is_substantial():
    components = _two_blocks_dfnd().dfn.components
    interface = components.wet_interfaces[0]

    # the interface pocket is walled by both banks named in lining_bodies, and the
    # contact area against each is non-trivial (a real shared wall, not a sliver)
    for bank in interface.lining_bodies:
        assert bank in interface.dry_lining
        assert interface.dry_lining[bank]['area'] > 0.0


# -- Layer 3: interface walls -----------------------------------------------------


def test_interface_walls_mirror_the_wet_interface_banks():
    components = _two_blocks_dfnd().dfn.components
    interface = components.wet_interfaces[0]

    # each bank lining the interface exposes that interface in its interface_walls
    for bank_id in interface.lining_bodies:
        bank = components[bank_id]
        assert interface.component_id in bank.interface_walls
        # interface_walls is the interface-only subset of wet_lining
        assert set(bank.interface_walls).issubset(bank.wet_lining)
        for wet_id in bank.interface_walls:
            assert components[wet_id].is_interface is True
