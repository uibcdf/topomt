"""
Tests for CASTp method.
"""

import inspect

import pytest
import topomt as tmt
from topomt.methods.castp import castp


def test_castp_signature_keeps_canonical_probe_default():
    signature = inspect.signature(castp)
    assert signature.parameters['probe_radius'].default == 1.4


def test_castp_integration():
    # Use a demo file
    pdb_file = tmt.demo['TcTIM']['1TCD.pdb']

    # Run CASTp
    # Probe radius 1.4 A is the canonical CASTp default.
    pockets, mesh = castp(pdb_file, probe_radius=1.4)

    assert isinstance(pockets, list)
    assert len(pockets) > 1
    assert hasattr(mesh, 'centers')
    
    if len(pockets) > 0:
        p1 = pockets[0]
        assert 'id' in p1
        assert 'volume' in p1
        assert 'properties' in p1
        assert 'atom_indices' in p1
        assert 'boundary_atom_indices' in p1
        assert 'component_atom_indices' in p1
        assert isinstance(p1['properties'], dict)
        assert set(p1['atom_indices']).issubset(set(p1['component_atom_indices']))

def test_castp_empty_system():
    # Test graceful handling of no pockets or empty system
    # Just pass a dummy system that might fail selection or have no atoms
    # Or a system with widely separated atoms (no pockets)
    pass
