"""
Unit and regression test for the openpocket package.
"""

# Import package, test suite, and other packages as needed
import topomt
import pytest
import sys

import molsysviewer_topomt

def test_openpocket_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "topomt" in sys.modules

def test_molsysviewer_topomt_all_has_no_duplicates():

    assert len(molsysviewer_topomt.__all__) == len(set(molsysviewer_topomt.__all__))
