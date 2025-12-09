import numpy as np
import math

def solve_apollonius_ccc_robust(c1, r1, c2, r2, c3, r3, epsilon=1e-9):
    """
    Solves the Problem of Apollonius for 3 circles (finding all tangent circles).
    Returns a list of (radius, center) tuples for all real, non-negative radius solutions.
    Handles coordinate shifting for numerical stability.
    """
    # Shift to place c1 at origin (0,0) for stability
    orig_c1 = c1
    x1, y1 = 0.0, 0.0
    x2, y2 = c2[0] - orig_c1[0], c2[1] - orig_c1[1]
    x3, y3 = c3[0] - orig_c1[0], c3[1] - orig_c1[1]

    # Check for collinearity of projected centers (degenerate triangle)
    det_c = x2*y3 - x3*y2
    if abs(det_c) < epsilon:
        # Collinear centers: this solver cannot give a unique tangent circle
        return []

    # System reduction
    K2 = r2**2 - r1**2 - x2**2 - y2**2
    K3 = r3**2 - r1**2 - x3**2 - y3**2
    
    inv_M_det = 1.0 / (4.0 * det_c)
    m11, m12 = 2*x2, 2*y2
    m21, m22 = 2*x3, 2*y3
    
    vr1, vr2 = 2*(r1-r2), 2*(r1-r3)
    vc1, vc2 = -K2, -K3
    
    alpha_x = (m22 * vr1 - m12 * vr2) * inv_M_det
    beta_x  = (m22 * vc1 - m12 * vc2) * inv_M_det
    
    alpha_y = (-m21 * vr1 + m11 * vr2) * inv_M_det
    beta_y  = (-m21 * vc1 + m11 * vc2) * inv_M_det
    
    A_q = alpha_x**2 + alpha_y**2 - 1
    B_q = 2*alpha_x*beta_x + 2*alpha_y*beta_y - 2*r1
    C_q = beta_x**2 + beta_y**2 - r1**2
    
    discriminant = B_q**2 - 4*A_q*C_q
    
    solutions = []
    if discriminant >= -epsilon: # Allow small negative for numerical noise
        sqrt_d = math.sqrt(max(0, discriminant))
        
        # Two roots from quadratic equation
        roots = []
        if abs(A_q) < epsilon: # Linear case if A_q is close to 0
            if abs(B_q) > epsilon:
                roots.append(-C_q / B_q)
        else:
            roots = [(-B_q + sqrt_d) / (2*A_q), (-B_q - sqrt_d) / (2*A_q)]
        
        for r_sol in roots:
            # Check for real, non-negative radius solutions
            if r_sol >= -epsilon: 
                cx_rel = alpha_x * r_sol + beta_x
                cy_rel = alpha_y * r_sol + beta_y
                # Shift center back to original coordinate system
                center = np.array([cx_rel + orig_c1[0], cy_rel + orig_c1[1]])
                solutions.append((r_sol, center))
                
    return solutions
