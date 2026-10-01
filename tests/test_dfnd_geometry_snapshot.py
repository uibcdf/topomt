"""Geometry ownership guards for the native snapshot slice of #60."""

import copy
import pickle
from operator import attrgetter

import molsysmt as msm
import numpy as np
import pytest

from topomt import pyunitwizard as puw
from topomt.dfnd import synthetic
from topomt.dfnd.data import DFNDData
from topomt.dfnd.graph import DelaunayFlowNetwork


def _inputs():
    system = synthetic.tetrahedron(edge=5.3, atom_radius=1.7)
    return system.coords * 0.1, system.radii * 0.1, np.array([51, 4, 22, 8])


def _data():
    coords, radii, indices = _inputs()
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        puw.quantity(coords, 'nm'), puw.quantity(radii, 'nm'), atom_indices=indices
    )
    return DFNDData(network, network.get_topography())


@pytest.mark.parametrize('changed_input', ['coordinates', 'radii', 'indices'])
def test_network_owns_input_geometry_independently(changed_input):
    coords, radii, indices = _inputs()
    coordinates = puw.quantity(coords, 'nm')
    atomic_radii = puw.quantity(radii, 'nm')
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        coordinates, atomic_radii, atom_indices=indices
    )
    before = network.get_topography()
    expected = (network.atom_coords.copy(), network.atom_radii.copy(), indices.copy())

    if changed_input == 'coordinates':
        puw.get_value(coordinates)[:] *= 0.5
    elif changed_input == 'radii':
        puw.get_value(atomic_radii)[:] *= 2
    else:
        indices[:] += 100

    for actual, saved in zip(
        (network.atom_coords, network.atom_radii, network.atom_indices_map), expected
    ):
        np.testing.assert_array_equal(actual, saved)
    np.testing.assert_equal(network.get_topography(), before)


@pytest.mark.parametrize(
    'path',
    [
        'network.atom_coords',
        'network.atom_radii',
        'network.atom_indices_map',
        'network.tetra_residence',
        'network.face_r_gates_per_tet_face',
        'network.tetra_atoms',
        'network.simplex_neighbors',
        'mesh.atoms.coords',
        'mesh.atoms.radii',
        'mesh.atoms.index_map',
        'mesh.delaunay.points',
        'mesh.delaunay.atom_radii',
        'mesh.delaunay.simplex_volumes',
    ],
)
def test_native_geometry_views_reject_writes_and_write_flag_reactivation(path):
    data = _data()
    before = data.network.get_topography()
    array = attrgetter(path)(data)

    with pytest.raises(ValueError, match='read-only'):
        array.flat[0] = 0
    with pytest.raises(ValueError):
        array.setflags(write=True)

    np.testing.assert_equal(data.network.get_topography(), before)


@pytest.mark.parametrize(
    'path',
    [
        'network.atom_coords',
        'network.atom_radii',
        'network.atom_indices_map',
        'network.epsilon',
        'mesh.atoms.coords',
        'mesh.atoms.radii',
        'mesh.atoms.index_map',
        'mesh.delaunay.points',
        'mesh.delaunay.atom_radii',
        'mesh.delaunay.simplices',
    ],
)
def test_native_geometry_rejects_attribute_replacement(path):
    data = _data()
    owner_path, name = path.rsplit('.', 1)
    owner = attrgetter(owner_path)(data)
    with pytest.raises(AttributeError, match='read-only'):
        setattr(owner, name, copy.copy(getattr(owner, name)))


def test_changing_view_shape_cannot_change_canonical_geometry():
    data = _data()
    coordinates = data.mesh.atoms.coords
    coordinates.shape = (coordinates.size,)
    assert data.mesh.atoms.coords.shape == (4, 3)
    assert data.network.atom_coords.shape == (4, 3)


@pytest.mark.parametrize('change', ['coordinates', 'radii'])
def test_new_geometry_rebuilds_identity_and_residence_without_changing_history(change):
    data = _data()
    coords, radii, indices = _inputs()
    if change == 'coordinates':
        coords *= 0.5
    else:
        radii *= 2
    updated = DelaunayFlowNetwork.from_coordinates_and_radii(
        puw.quantity(coords, 'nm'), puw.quantity(radii, 'nm'), atom_indices=indices
    )
    result = updated.get_topography()

    assert updated.substrate_key != data.network.substrate_key
    assert (
        result['raw']['parameters']['result_key']
        != data.raw['parameters']['result_key']
    )
    assert data.raw['wet_components'][0]['family'] == 'void'
    assert result['raw']['wet_components'] == []
    assert set(data.raw['tetrahedra'][0]['atom_indices']) == {51, 4, 22, 8}
    assert data.network.get_topography()['raw'] == data.raw


def test_probe_queries_share_protected_geometry_and_preserve_previous_result():
    data = _data()
    before = copy.deepcopy(data.raw)
    reprobed = data.at_probe(puw.quantity(2.2, 'angstroms'))

    assert reprobed.network is data.network
    assert reprobed.mesh.delaunay is data.mesh.delaunay
    assert np.shares_memory(data.network.atom_coords, data.mesh.delaunay.points)
    assert np.shares_memory(data.network.atom_radii, data.mesh.delaunay.atom_radii)
    for name in ('coords', 'radii', 'index_map'):
        assert np.shares_memory(
            getattr(data.mesh.atoms, name), getattr(reprobed.mesh.atoms, name)
        )
    assert data.raw == before
    assert (
        reprobed.raw['parameters']['result_key'] != data.raw['parameters']['result_key']
    )
    assert reprobed.raw['wet_components'] == []


def test_deep_copy_retains_geometry_protection_and_independent_result_records():
    data = _data()
    copied = copy.deepcopy(data)
    with pytest.raises(ValueError, match='read-only'):
        copied.mesh.atoms.coords[0, 0] = 99
    copied.raw['parameters']['reporting']['min_size'] = 100
    assert data.raw['parameters']['reporting']['min_size'] == 0
    np.testing.assert_equal(
        copied.network.get_topography(), data.network.get_topography()
    )


def test_live_molecular_coordinate_mutation_does_not_retarget_native_result():
    molsys = synthetic.tetrahedron(edge=5.3, atom_radius=1.7).to_molsysmt()
    network = DelaunayFlowNetwork(molsys)
    coords = network.atom_coords.copy()
    before = network.get_topography()
    msm.set(molsys, coordinates=puw.quantity(np.zeros((1, 4, 3)), 'nm'))
    np.testing.assert_array_equal(network.atom_coords, coords)
    np.testing.assert_equal(network.get_topography(), before)


def test_pickle_roundtrip_restores_native_geometry_protection():
    data = _data()
    restored = pickle.loads(pickle.dumps(data))
    for path in ('network.atom_coords', 'mesh.atoms.radii', 'mesh.delaunay.points'):
        array = attrgetter(path)(restored)
        with pytest.raises(ValueError, match='read-only'):
            array.flat[0] = 0
        with pytest.raises(ValueError):
            array.setflags(write=True)
    np.testing.assert_equal(
        restored.network.get_topography(), data.network.get_topography()
    )
