"""Dependency contract tests for TopoMT packaging and optional features."""

import depdigest.core.decorator as depdigest_decorator
import numpy as np
import pytest
import tomllib

from topomt._private.smonitor import LibraryNotFoundError

CORE_DEPENDENCIES = {
    'argdigest',
    'depdigest',
    'molsysmt',
    'numpy',
    'pyunitwizard',
    'scipy',
    'smonitor',
}


def test_pyproject_declares_core_dependencies_and_extras():
    with open('pyproject.toml', 'rb') as file:
        pyproject = tomllib.load(file)

    dependencies = set(pyproject['project']['dependencies'])
    assert CORE_DEPENDENCIES <= dependencies
    assert 'networkx' not in dependencies
    assert 'nglview' not in dependencies
    assert 'py3Dmol' not in dependencies

    extras = pyproject['project']['optional-dependencies']
    assert extras['centerline'] == ['networkx']
    assert extras['alphaspace2'] == ['mdtraj']
    assert extras['pocketeer'] == ['biotite']
    assert extras['third-party'] == ['topomt[alphaspace2,pocketeer]']
    assert set(extras['tools']) == {'scikit-image', 'scikit-learn'}
    assert extras['viewer'] == ['molsysviewer', 'topomt[centerline]']


def test_depdigest_inventory_tracks_feature_dependencies_only():
    from topomt._depdigest import LIBRARIES, MAPPING

    assert LIBRARIES['numpy']['type'] == 'hard'
    assert LIBRARIES['scipy']['type'] == 'hard'
    assert LIBRARIES['molsysmt']['type'] == 'hard'

    assert LIBRARIES['networkx']['type'] == 'soft'
    assert LIBRARIES['skimage']['pypi'] == 'scikit-image'
    assert LIBRARIES['sklearn']['pypi'] == 'scikit-learn'
    assert LIBRARIES['mdtraj']['type'] == 'soft'
    assert LIBRARIES['biotite']['type'] == 'soft'

    assert 'argdigest' not in LIBRARIES
    assert 'smonitor' not in LIBRARIES
    assert 'nglview' not in LIBRARIES
    assert 'py3Dmol' not in LIBRARIES

    assert MAPPING['networkx_Graph'] == 'networkx'
    assert MAPPING['sklearn_neighbors'] == 'sklearn'
    assert MAPPING['mdtraj_load'] == 'mdtraj'
    assert MAPPING['biotite_structure'] == 'biotite'


def _raise_missing_dependency(module_name, pypi_name=None, caller=None, exception_class=ImportError):
    raise exception_class(library=pypi_name or module_name, caller=caller)


def test_channel_skeleton_reports_missing_networkx_cleanly(monkeypatch):
    from topomt.dfnd.centerline import channel_skeleton

    monkeypatch.setattr(
        depdigest_decorator,
        'check_dependency',
        _raise_missing_dependency,
    )

    with pytest.raises(LibraryNotFoundError):
        channel_skeleton(raw={}, component={})


def test_thickness_profile_reports_missing_sklearn_only_for_fallback(monkeypatch):
    from topomt.tools.features.channels.profiles import thickness_profile

    monkeypatch.setattr(
        depdigest_decorator,
        'check_dependency',
        _raise_missing_dependency,
    )

    centers = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    axis = np.array([1.0, 0.0, 0.0])

    with pytest.raises(LibraryNotFoundError):
        thickness_profile(centers, axis)

    _bin_centers, profile = thickness_profile(
        centers,
        axis,
        neighbor_pairs=np.array([[0, 1]]),
        n_bins=2,
    )
    assert profile.shape == (2,)


def test_backend_entry_points_report_missing_optional_libraries(monkeypatch):
    from topomt.third_party.alphaspace2.library import (
        get_topography as alphaspace2_library,
    )
    from topomt.third_party.pocketeer._native_impl import pocketeer

    monkeypatch.setattr(
        depdigest_decorator,
        'check_dependency',
        _raise_missing_dependency,
    )

    with pytest.raises(LibraryNotFoundError):
        alphaspace2_library(molecular_system=None)

    with pytest.raises(LibraryNotFoundError):
        pocketeer(molecular_system=None)
