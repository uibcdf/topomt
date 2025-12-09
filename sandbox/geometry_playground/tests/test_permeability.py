import numpy as np
import math
from core.permeability import check_face_permeability

def test_equilateral_open():
    p1 = np.array([0, 0, 0])
    p2 = np.array([10, 0, 0])
    p3 = np.array([5, 8.66025404, 0]) # sqrt(75) = 8.66
    r = 1.0
    probe = 1.4
    
    passable, r_gate = check_face_permeability(p1, p2, p3, r, r, r, probe)
    assert abs(r_gate - 1.8867) < 0.01
    assert passable

def test_tight_squeeze():
    p1 = np.array([0, 0, 0])
    p2 = np.array([2, 0, 0])
    p3 = np.array([1, math.sqrt(3), 0])
    r = 1.0
        
    probe = 0.1
    passable, r_gate = check_face_permeability(p1, p2, p3, r, r, r, probe)
    assert abs(r_gate - 0.1547) < 0.01

def test_overlap_blocked():
    p1 = np.array([0, 0, 0])
    p2 = np.array([1, 0, 0])
    p3 = np.array([0.5, 0.8660254, 0]) # Equilateral triangle side 1
    r = 1.0 # Overlap since dist=1 < 2*r
    
    passable, r_gate = check_face_permeability(p1, p2, p3, r, r, r, 0.1)
    assert r_gate == 0.0
    assert not passable