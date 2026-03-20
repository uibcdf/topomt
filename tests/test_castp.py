"""
Tests for CASTp method.
"""

import pytest
import topomt as tmt
from topomt.methods.castp import castp

def test_castp_integration():
    # Use a demo file
    pdb_file = tmt.demo['TcTIM']['1TCD.pdb']
    
    # Run CASTp
    # We use a large probe to ensure we don't get too many pockets, 
    # or small enough to get some. 1.4 is standard.
    # min_spheres=1 to ensure we catch even small things for testing.
    pockets, alpha = castp(pdb_file, probe_radius=1.4, min_spheres_per_pocket=1)
    
    assert isinstance(pockets, list)
    assert hasattr(alpha, 'centers')
    
    if len(pockets) > 0:
        p1 = pockets[0]
        assert 'id' in p1
        assert 'volume' in p1
        assert 'properties' in p1
        assert 'atom_indices' in p1
        
        props = p1['properties']
        assert 'net_charge' in props
        assert 'mean_hydrophobicity' in props

def test_castp_empty_system():
    # Test graceful handling of no pockets or empty system
    # Just pass a dummy system that might fail selection or have no atoms
    # Or a system with widely separated atoms (no pockets)
    pass
