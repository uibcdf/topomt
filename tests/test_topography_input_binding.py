"""Binding a new source must not retarget an existing analysis."""

import molsysmt as msm
import numpy as np
import pytest

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt.dfnd import synthetic
from topomt.dfnd.api import dfnd_to_topography
from topomt.features import Pocket


@pytest.mark.parametrize('replacement', [None, 'invalid-new-input'])
def test_populated_topography_rejects_source_replacement_atomically(replacement):
    source = synthetic.tetrahedron(edge=5.3).to_molsysmt()
    topo = Topography(source, features=[Pocket(feature_id='POC-1')])
    original_molsys = topo._molsys
    with pytest.raises(ValueError, match='new Topography|new analysis'):
        topo.molecular_system = replacement
    assert topo.molecular_system is source
    assert topo._molsys is original_molsys
    assert topo['POC-1'].molecular_system is source


def test_empty_native_result_cannot_be_rebound():
    source = synthetic.tetrahedron(edge=5.3).to_molsysmt()
    topo = dfnd_to_topography(source, min_size=100)
    assert len(topo) == 0
    with pytest.raises(ValueError, match='new Topography|new analysis'):
        topo.molecular_system = None


def test_empty_binding_respects_selection_frame_and_failed_conversion_is_atomic():
    source = synthetic.tetrahedron(edge=5.3).to_molsysmt()
    second = msm.copy(source)
    expected = np.ones((1, 4, 3))
    msm.set(second, coordinates=puw.quantity(expected, 'nm'))
    msm.append_structures(source, second)
    topo = Topography(selection=[3, 1], structure_indices=1)
    topo.molecular_system = source
    assert msm.get(topo._molsys, n_atoms=True, n_structures=True) == [2, 1]
    np.testing.assert_array_equal(
        puw.get_value(msm.get(topo._molsys, coordinates=True), to_unit='nm'),
        expected[:, [3, 1]],
    )
    original = topo._molsys
    with pytest.raises(Exception):
        topo.molecular_system = 'invalid-new-input'
    assert topo.molecular_system is source
    assert topo._molsys is original
    topo.molecular_system = None
    assert topo.molecular_system is topo._molsys is None


def test_unadopted_topography_declares_absent_input_context():
    assert Topography().input_context is None


def test_completed_provider_run_cannot_be_rebound_when_no_features_are_reported():
    from topomt.provider_output import ProviderRun

    topo = Topography()
    topo.add_provider_run(ProviderRun('fpocket', 'files', 'run-test', (), '{}'))
    with pytest.raises(ValueError, match='new Topography'):
        topo.molecular_system = None
