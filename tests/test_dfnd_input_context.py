"""Historical selected-input recovery for the context slice of #60."""

import copy
import pickle

import molsysmt as msm
import numpy as np
import pytest

from topomt import pyunitwizard as puw
from topomt.dfnd import synthetic
from topomt.dfnd.api import dfnd_to_topography
from topomt.dfnd.data import DFNDData
from topomt.dfnd.graph import DelaunayFlowNetwork


@pytest.fixture
def trajectory():
    selected = np.array([6, 1, 4, 2])
    coords = np.full((8, 3), 20.0)
    coords[selected] = synthetic.tetrahedron(edge=5.8).coords
    system = synthetic.SyntheticSystem(coords, np.full(8, 1.88)).to_molsysmt()
    msm.set(system, element='atom', atom_name=[f'A{i}' for i in range(8)])
    second = msm.copy(system)
    msm.set(second, coordinates=puw.quantity(coords[None] * 0.1 + 1.0, 'nm'))
    msm.append_structures(system, second)
    third = msm.copy(second)
    msm.set(third, coordinates=puw.quantity(coords[None] * 0.1 + 2.0, 'nm'))
    msm.append_structures(system, third)
    msm.set(system, time=puw.quantity([0.0, 1.0, 2.0], 'ns'), structure_id=[10, 11, 12])
    return system, selected


def test_context_recovers_selected_frame_order_and_topology_after_live_edits(
    trajectory,
):
    source, indices = trajectory
    topo = dfnd_to_topography(source, selection=indices, structure_indices=1)
    context = topo.input_context
    resolved = topo.dfnd.network.atom_indices_map
    expected = puw.get_value(
        msm.get(source, selection=resolved, structure_indices=1, coordinates=True),
        to_unit='nm',
    )
    names = msm.get(source, element='atom', selection=resolved, atom_name=True)
    key = topo.dfnd.raw['parameters']['result_key']

    msm.set(source, coordinates=puw.quantity(np.zeros((3, 8, 3)), 'nm'))
    msm.set(source, element='atom', atom_name=['CHANGED'] * 8)
    recovered = context.recover_molecular_system()

    assert msm.get(recovered, n_atoms=True, n_structures=True) == [4, 1]
    assert msm.get(recovered, structure_id=True) == ['11']
    np.testing.assert_allclose(
        puw.get_value(msm.get(recovered, time=True), to_unit='ns'), [1.0], rtol=1e-12
    )
    assert msm.get(recovered, element='atom', atom_name=True) == names
    np.testing.assert_array_equal(
        puw.get_value(msm.get(recovered, coordinates=True), to_unit='nm'), expected
    )
    np.testing.assert_array_equal(context.atom_indices, np.sort(indices))
    assert context.selection == tuple(indices)
    assert context.selection_syntax == 'MolSysMT'
    assert context.structure_index == 1
    assert context.coordinate_unit == context.radii_unit == 'nm'
    assert context.coordinate_convention == 'nonperiodic_cartesian'
    assert context.coordinate_transform == 'identity'
    assert context.radii_model == 'vdw'
    assert context.hydrogen_policy == 'exclude'
    assert topo.dfnd.raw['parameters']['result_key'] == key
    assert context is topo.dfnd.input_context is topo.dfnd.network.input_context


def test_recovered_molsys_edits_do_not_change_saved_context(trajectory):
    source, indices = trajectory
    context = DelaunayFlowNetwork(source, selection=indices).input_context
    expected = puw.get_value(context.coordinates, to_unit='nm').copy()
    recovered = context.recover_molecular_system()
    msm.set(recovered, coordinates=puw.quantity(np.zeros((1, 4, 3)), 'nm'))
    msm.set(recovered, element='atom', atom_name=['EDITED'] * 4)
    again = context.recover_molecular_system()
    np.testing.assert_array_equal(
        puw.get_value(context.coordinates, to_unit='nm'), expected
    )
    np.testing.assert_array_equal(
        puw.get_value(msm.get(again, coordinates=True), to_unit='nm')[0], expected
    )
    assert msm.get(again, element='atom', atom_name=True) != ['EDITED'] * 4


def test_context_checks_source_namespace_and_selected_membership(trajectory):
    source, indices = trajectory
    first = DelaunayFlowNetwork(source, selection=indices).input_context
    second = DelaunayFlowNetwork(source, selection=indices).input_context
    assert first.source_id != second.source_id
    assert first.local_atom_indices([2, 6], source_id=first.source_id) == [1, 3]
    with pytest.raises(ValueError, match='source'):
        first.local_atom_indices([2], source_id=second.source_id)
    with pytest.raises(ValueError, match='selected'):
        first.local_atom_indices([7], source_id=first.source_id)
    with pytest.raises(ValueError, match='integer'):
        first.local_atom_indices([2.5], source_id=first.source_id)


def test_probe_reuses_context_and_protected_geometry_buffers(trajectory):
    source, indices = trajectory
    network = DelaunayFlowNetwork(source, selection=indices, structure_indices=[1])
    data = DFNDData(network, network.get_topography())
    other = data.at_probe(puw.quantity(2.2, 'angstroms'))
    context = data.input_context
    assert other.input_context is context
    for captured, native in (
        (puw.get_value(context.coordinates, to_unit='nm'), network.atom_coords),
        (puw.get_value(context.radii, to_unit='nm'), network.atom_radii),
        (context.atom_indices, network.atom_indices_map),
    ):
        assert np.shares_memory(captured, native)
        with pytest.raises(ValueError):
            captured.setflags(write=True)
    puw.get_value(context.coordinates).shape = (12,)
    assert puw.get_value(context.coordinates).shape == (4, 3)
    with pytest.raises(AttributeError):
        context.structure_index = 0


@pytest.mark.parametrize(
    'restore', [copy.deepcopy, lambda x: pickle.loads(pickle.dumps(x))]
)
def test_context_copy_and_restoration_preserve_recovery_and_protection(
    trajectory, restore
):
    source, indices = trajectory
    topo = dfnd_to_topography(source, selection=indices, structure_indices=1)
    restored = restore(topo)
    context = restored.input_context
    assert context.source_id == topo.input_context.source_id
    assert context is restored.dfnd.network.input_context
    np.testing.assert_array_equal(
        puw.get_value(context.coordinates),
        puw.get_value(topo.input_context.coordinates),
    )
    with pytest.raises(ValueError):
        puw.get_value(context.coordinates).setflags(write=True)
    assert msm.get(context.recover_molecular_system(), n_structures=True) == 1


@pytest.mark.parametrize('frames', [[], [0, 1], 'all', -1, 0.5, True])
def test_dfnd_rejects_ambiguous_or_invalid_frame_requests(trajectory, frames):
    source, indices = trajectory
    with pytest.raises(ValueError, match='single|one|frame'):
        DelaunayFlowNetwork(source, selection=indices, structure_indices=frames)


def test_array_context_has_geometry_without_fabricated_molecular_topology():
    coords, radii = synthetic.tetrahedron(edge=5.3)
    context = DelaunayFlowNetwork.from_coordinates_and_radii(
        coords, radii
    ).input_context
    assert context.selection == 'array'
    assert context.selection_syntax == 'explicit_indices'
    assert context.structure_index is None
    assert context.radii_model == 'provided'
    with pytest.raises(ValueError, match='topology'):
        context.recover_molecular_system()


def test_native_diagnostic_uses_saved_labels_after_live_topology_edit(
    trajectory, capsys
):
    source, indices = trajectory
    topo = dfnd_to_topography(source, selection=indices, structure_indices=1)
    msm.set(source, element='atom', atom_name=['CHANGED'] * 8)
    topo.dfnd.info(0)
    output = capsys.readouterr().out
    assert 'CHANGED' not in output
    for index in indices:
        assert f'Atom {index} (A{index})' in output


def test_topography_show_uses_saved_frame_and_maps_source_indices(
    trajectory, monkeypatch
):
    from topomt.features import Pocket

    source, indices = trajectory
    topo = dfnd_to_topography(source, selection=indices, structure_indices=1)
    topo.add_feature(Pocket(atom_indices=[6, 2]))
    msm.set(source, coordinates=puw.quantity(np.zeros((3, 8, 3)), 'nm'))
    calls = []

    class View:
        def add_surface(self, selection, **kwargs):
            calls.append(selection)

    def view(system, **kwargs):
        assert msm.get(system, n_atoms=True, n_structures=True) == [4, 1]
        np.testing.assert_array_equal(
            puw.get_value(msm.get(system, coordinates=True), to_unit='nm')[0],
            puw.get_value(topo.input_context.coordinates, to_unit='nm'),
        )
        return View()

    monkeypatch.setattr(msm, 'view', view)
    topo.show()
    assert '@3,1' in calls


def test_feature_labels_resolve_to_source_indices_in_saved_selected_topology(
    trajectory,
):
    from topomt.features import Pocket

    source, indices = trajectory
    topo = dfnd_to_topography(source, selection=indices, structure_indices=1)
    msm.set(source, element='atom', atom_name=['CHANGED'] * 8)
    feature = Pocket(
        atom_labels=['A6'], atom_label_format='{atom_name}', topography=topo
    )
    assert list(feature.atom_indices) == [6]
