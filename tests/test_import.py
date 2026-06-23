"""
Unit and regression test for the openpocket package.
"""

# Import package, test suite, and other packages as needed
import sys

import molsysviewer_topomt
import topomt


def test_openpocket_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "topomt" in sys.modules

def test_molsysviewer_topomt_all_has_no_duplicates():

    assert len(molsysviewer_topomt.__all__) == len(set(molsysviewer_topomt.__all__))

def test_topomt_all_declares_public_api_v0():
    expected = {
        '__version__',
        '__print_version__',
        'pyunitwizard',
        'config',
        'demo',
        'features',
        'Topography',
        'DelaunayMesh',
        'WeightedDelaunayMesh',
        'get_delaunay_mesh',
        'get_topography',
        'io',
        'third_party',
        'dfnd',
        'tools',
    }

    assert set(topomt.__all__) == expected
    assert len(topomt.__all__) == len(set(topomt.__all__))
    for name in expected:
        assert hasattr(topomt, name)


def test_broken_legacy_get_pockets_stub_is_not_public():
    assert 'get_pockets' not in topomt.__all__
    assert 'show_pockets' not in topomt.__all__
    assert not hasattr(topomt, 'get_pockets')
    assert not hasattr(topomt, 'show_pockets')
