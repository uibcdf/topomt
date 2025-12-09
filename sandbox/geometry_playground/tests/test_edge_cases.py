import numpy as np
import math
from core.permeability import check_face_permeability, check_face_permeability_mc

def test_cross_validation_mc():
    s = 2.5
    p1 = np.array([0, 0, 0])
    p2 = np.array([s, 0, 0])
    p3 = np.array([s/2, s*math.sqrt(3)/2, 0])
    r = 1.0
    
    probe_pass = 0.2
    probe_fail = 0.3
    
    ok_pass, r_gate = check_face_permeability(p1, p2, p3, r, r, r, probe_pass)
    ok_fail, _      = check_face_permeability(p1, p2, p3, r, r, r, probe_fail)
    
    mc_pass = check_face_permeability_mc(p1, p2, p3, r, r, r, probe_pass, n_samples=500000, epsilon=1e-9)
    mc_fail = check_face_permeability_mc(p1, p2, p3, r, r, r, probe_fail, n_samples=500000, epsilon=1e-9)
        
    assert abs(r_gate - 0.25) < 0.01 # New expected r_gate
    assert ok_pass == True
    assert ok_fail == False
    assert mc_pass == True
    assert mc_fail == False 

def test_asymmetric_triangle():
    p1 = np.array([0, 0, 0])
    p2 = np.array([4, 0, 0])
    p3 = np.array([2, 1, 0])
    r = 0.4
        
    # Analytic solve
    passable, r_gate = check_face_permeability(p1, p2, p3, r, r, r, 0.01) # Test with a small probe
    print(f"Analytic R_gate: {r_gate:.4f} (Expected ~0.718)")
    
    # Verify with MC around the threshold

        
    mc_pass = check_face_permeability_mc(p1, p2, p3, r, r, r, r_gate - 0.01, n_samples=1000000, epsilon=1e-9)
    mc_fail = check_face_permeability_mc(p1, p2, p3, r, r, r, r_gate + 0.01, n_samples=1000000, epsilon=1e-9)
        
    assert abs(r_gate - 0.718) < 0.01 # Check that the analytic is correct now (based on re-evaluation)
    assert mc_pass == True
    assert mc_fail == False