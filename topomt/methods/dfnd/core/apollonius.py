import numpy as np
import math

def solve_apollonius_js_port(c1, r1, c2, r2, c3, r3, epsilon=1e-9):
    dx12 = c2[0] - c1[0]; dx23 = c3[0] - c2[0]; dx31 = c1[0] - c3[0]
    dy12 = c2[1] - c1[1]; dy23 = c3[1] - c2[1]; dy31 = c1[1] - c3[1]
    g1 = c1[0]**2 + c1[1]**2 - r1**2; g2 = c2[0]**2 + c2[1]**2 - r2**2; g3 = c3[0]**2 + c3[1]**2 - r3**2
    det123 = dx12 * dy23 - dx23 * dy12
    if abs(det123) < epsilon: # Collinear case not handled in this internal copy
        return None # For simplicity, we'll assume non-collinear
    D = 2 * (c1[1] * dx23 + c2[1] * dx31 + c3[1] * dx12)
    if abs(D) < epsilon: return None
    a = -(dy23 * g1 + dy31 * g2 + dy12 * g3); b = 2 * (r1 * dy23 + r2 * dy31 + r3 * dy12)
    c = dx23 * g1 + dx31 * g2 + dx12 * g3; d = -2 * (r1 * dx23 + r2 * dx31 + r3 * dx12)
    dx = D * c1[0] - a; dy = D * c1[1] - c; dr = D * r1
    P = b*b + d*d - D*D; Q = b*dx + d*dy + D*dr; R = dx*dx + dy*dy - dr*dr
    if abs(P) < epsilon: return None
    disc = Q * Q - P * R
    if abs(disc) < epsilon:
        disc = 0
    if disc < 0: return None
    r = (Q - math.sqrt(disc)) / P
    x = (a + b * r) / D; y = (c + d * r) / D
    return (r, np.array([x, y]))

def solve_apollonius_3d(p1, r1, p2, r2, p3, r3, p4, r4, epsilon=1e-9):
    """
    Solves the 3D Apollonius problem for 4 spheres (finding a tangent sphere).
    This function finds the radius and center of a sphere externally tangent to 4 given spheres.
    Used to calculate R_insphere (tetrahedron habitability).

    Parameters:
        p1, p2, p3, p4: np.ndarray (shape (3,)) - 3D coordinates of sphere centers.
        r1, r2, r3, r4: float - Radii of the spheres.
        epsilon: float - Numerical tolerance.

    Returns:
        float: The radius R of the tangent sphere, or 0.0 if no valid positive solution.
        np.ndarray (shape (3,)): The center of the tangent sphere.
    """
    # This is similar to the 2D problem, but with 4 spheres and a 3D center.
    # The algebraic reduction to a quadratic equation for R is more complex.
    # The equations are: ||P - pi||^2 = (R + ri)^2 for i=1..4.
    # Expand and subtract the 4th equation from the first three to linearize.
    
    # Shift coordinate system so p4 is at the origin for numerical stability.
    # This reduces p_i to p'_i = p_i - p4 and r_i to r_i.
    # And P to P' = P - p4.
    p1_p = p1 - p4; p2_p = p2 - p4; p3_p = p3 - p4
    
    # Define auxiliary constants for the system
    # Terms (pi^2 - ri^2)
    k1 = np.dot(p1_p, p1_p) - r1*r1
    k2 = np.dot(p2_p, p2_p) - r2*r2
    k3 = np.dot(p3_p, p3_p) - r3*r3
    k4 = 0.0 # for p4_p at origin
    
    # System of linear equations for P' (x,y,z) and R
    # 2 P' . p'_i - 2 R (ri - r4) = (pi_p^2 - ri^2) - (p4_p^2 - r4^2)
    # 2 P' . p'_1 - 2 R (r1 - r4) = k1 - k4
    # 2 P' . p'_2 - 2 R (r2 - r4) = k2 - k4
    # 2 P' . p'_3 - 2 R (r3 - r4) = k3 - k4

    # Let M * P' = V_k + V_r * R
    M = 2 * np.array([p1_p, p2_p, p3_p])
    V_k = np.array([k1 - k4, k2 - k4, k3 - k4])
    V_r = 2 * np.array([r1 - r4, r2 - r4, r3 - r4])

    try:
        M_inv = np.linalg.inv(M)
        # P' = M_inv @ V_k + M_inv @ V_r * R
        # Let A = M_inv @ V_r  and B = M_inv @ V_k
        A = M_inv @ V_r
        B = M_inv @ V_k

        # Substitute P' = A*R + B into the equation for P' and r4 (origin sphere)
        # ||A*R + B||^2 = (R + r4)^2
        # (A.A)R^2 + 2(A.B)R + (B.B) = R^2 + 2 R r4 + r4^2
        # (A.A - 1)R^2 + 2(A.B - r4)R + (B.B - r4^2) = 0
        
        a_q = np.dot(A,A) - 1.0
        b_q = 2.0 * (np.dot(A,B) - r4)
        c_q = np.dot(B,B) - r4*r4
        
        discriminant = b_q**2 - 4 * a_q * c_q
        
        if discriminant < -epsilon: # No real solution
            return 0.0, np.array([0.0, 0.0, 0.0])
        
        sqrt_d = math.sqrt(max(0.0, discriminant))
        
        roots = []
        if abs(a_q) < epsilon: # Linear case
            if abs(b_q) > epsilon:
                roots.append(-c_q / b_q)
        else:
            roots.append((-b_q + sqrt_d) / (2 * a_q))
            roots.append((-b_q - sqrt_d) / (2 * a_q))
        
        valid_radii = [r for r in roots if r > epsilon]
        
        if not valid_radii:
            return 0.0, np.array([0.0, 0.0, 0.0])
        
        # We need the smallest positive radius (inner void)
        r_insphere = min(valid_radii)
        
        # Calculate center P'
        center_p_prime = A * r_insphere + B
        center = center_p_prime + p4 # Shift back to original coordinates
        
        return r_insphere, center

    except np.linalg.LinAlgError:
        # M is singular, points are coplanar or otherwise degenerate
        return 0.0, np.array([0.0, 0.0, 0.0])
