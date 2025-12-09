import numpy as np
import math
from .apollonius import solve_apollonius_js_port
from .utils import is_point_in_triangle_2d

def check_face_permeability(p1, p2, p3, r1, r2, r3, epsilon=1e-6):
    """
    Determines the maximum radius of a probe that can pass through the triangle formed by atoms 1,2,3.
    This combines Apollonius solutions (tangent to 3 atoms) and edge-limited solutions (tangent to 2 atoms),
    considering the physical constraints of the face.
    
    Parameters
    ----------
    p1, p2, p3 : np.ndarray
        3D coordinates of the atomic centers.
    r1, r2, r3 : float
        Van der Waals radii of the atoms.
    epsilon : float, optional
        Tolerance for floating point comparisons.
    
    Returns
    -------
    float: The maximum radius R_gate that can pass through the face.
    """
    max_r_gate_candidates = []
    
    # 1. Project 3D atom centers to 2D plane of the face
    orig_p1 = p1
    v12_3d = p2 - orig_p1
    v13_3d = p3 - orig_p1
    
    norm_v12 = np.linalg.norm(v12_3d)
    if norm_v12 < epsilon: # Collinear points or degenerate triangle
        return 0.0
    u_vec = v12_3d / norm_v12
    
    v_perp_to_u = v13_3d - np.dot(v13_3d, u_vec) * u_vec
    norm_v_perp = np.linalg.norm(v_perp_to_u)
    if norm_v_perp < epsilon: # Collinear points or degenerate triangle
        return 0.0 
    v_vec = v_perp_to_u / norm_v_perp
    
    # 2D coordinates in this local basis (orig_p1 at origin)
    c1_2d = np.array([0.0, 0.0])
    c2_2d = np.array([norm_v12, 0.0])
    c3_2d = np.array([np.dot(v13_3d, u_vec), np.dot(v13_3d, v_vec)])
    
    # 2. Consider Apollonius solutions (tangent to 3 atoms)
    sol = solve_apollonius_js_port(c1_2d, r1, c2_2d, r2, c3_2d, r3, epsilon)
    
    if sol:
        r_sol, center_sol = sol
        if r_sol > epsilon and is_point_in_triangle_2d(center_sol, c1_2d, c2_2d, c3_2d, epsilon=epsilon, strict_interior=False):
            max_r_gate_candidates.append(r_sol)
            
    # 3. Consider Edge-limited permeabilities (hole dominated by 2 spheres, not 3)
    atom_data_2d = [(c1_2d, r1), (c2_2d, r2), (c3_2d, r3)]
    tri_points_2d = [c1_2d, c2_2d, c3_2d]
    
    for i in range(3):
        for j in range(i + 1, 3):
            (cA_2d, rA) = atom_data_2d[i]
            (cB_2d, rB) = atom_data_2d[j]
            (cC_2d, rC) = atom_data_2d[3 - i - j] # The third atom
            
            dist_AB = np.linalg.norm(cA_2d - cB_2d)
            r_candidate_pair = max(0.0, (dist_AB - rA - rB) / 2.0)
            
            if r_candidate_pair > epsilon:
                vec_AB = (cB_2d - cA_2d) / dist_AB
                center_candidate = cA_2d + (rA + r_candidate_pair) * vec_AB
                
                if np.linalg.norm(center_candidate - cC_2d) >= (rC + r_candidate_pair - epsilon) and \
                   is_point_in_triangle_2d(center_candidate, *tri_points_2d, epsilon=epsilon, strict_interior=False):
                    max_r_gate_candidates.append(r_candidate_pair)
                    
    if abs(r1 - r2) < epsilon and abs(r2 - r3) < epsilon:
        s = (np.linalg.norm(c1_2d - c2_2d) + np.linalg.norm(c2_2d - c3_2d) + np.linalg.norm(c3_2d - c1_2d)) / 2.0
        area = 0.5 * abs(c1_2d[0]*(c2_2d[1]-c3_2d[1]) + c2_2d[0]*(c3_2d[1]-c1_2d[1]) + c3_2d[0]*(c1_2d[1]-c2_2d[1]))
        if s > epsilon:
            incircle_radius_geometric = area / s
            r_incircle_candidate = max(0.0, incircle_radius_geometric - r1)
            if r_incircle_candidate > epsilon:
                 max_r_gate_candidates.append(r_incircle_candidate)
                
    return max(max_r_gate_candidates) if max_r_gate_candidates else 0.0
