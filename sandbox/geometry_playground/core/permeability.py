import numpy as np
import math
from .apollonius import solve_apollonius_js_port
from .utils import is_point_in_triangle_2d

def check_face_permeability(p1, p2, p3, r1, r2, r3, probe_radius, epsilon=1e-6):
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
    probe_radius : float
        Radius of the spherical probe.
    epsilon : float, optional
        Tolerance for floating point comparisons.
    
    Returns
    -------
    bool: True if a probe of probe_radius can pass.
    float: The maximum radius R_gate that can pass through the face.
    """
    max_r_gate_candidates = []
    
    # 1. Project 3D atom centers to 2D plane of the face
    orig_p1 = p1
    orig_p2 = p2
    orig_p3 = p3

    v12_3d = orig_p2 - orig_p1
    v13_3d = orig_p3 - orig_p1
    
    # Define orthonormal basis in the plane of the triangle
    norm_v12 = np.linalg.norm(v12_3d)
    if norm_v12 < epsilon: # Collinear points or degenerate triangle
        return False, 0.0
    u_vec = v12_3d / norm_v12
    
    v_perp_to_u = v13_3d - np.dot(v13_3d, u_vec) * u_vec
    norm_v_perp = np.linalg.norm(v_perp_to_u)
    if norm_v_perp < epsilon: # Collinear points or degenerate triangle
        return False, 0.0 
    v_vec = v_perp_to_u / norm_v_perp
    
    # 2D coordinates in this local basis (orig_p1 at origin)
    c1_2d = np.array([0.0, 0.0])
    c2_2d = np.array([norm_v12, 0.0])
    c3_2d = np.array([np.dot(v13_3d, u_vec), np.dot(v13_3d, v_vec)])
    
    # 2. Consider Apollonius solutions (tangent to 3 atoms)
    # Using the JS port which returns a single optimal solution (usually).
    sol = solve_apollonius_js_port(c1_2d, r1, c2_2d, r2, c3_2d, r3, epsilon)
    
    if sol:
        r_sol, center_sol = sol
        # We only care about positive radii (a gap exists)
        # And the center must be inside or on the boundary of the triangle to represent a passage THROUGH the face.
        if r_sol > epsilon and is_point_in_triangle_2d(center_sol, c1_2d, c2_2d, c3_2d, epsilon=epsilon, strict_interior=False):
            max_r_gate_candidates.append(r_sol)
            
    # 3. Consider Edge-limited permeabilities (hole dominated by 2 spheres, not 3)
    # This covers cases where the Apollonius solution is outside the triangle or non-physical.
    atom_data_2d = [(c1_2d, r1), (c2_2d, r2), (c3_2d, r3)]
    tri_points_2d = [c1_2d, c2_2d, c3_2d]
    
    for i in range(3):
        for j in range(i + 1, 3):
            (cA_2d, rA) = atom_data_2d[i]
            (cB_2d, rB) = atom_data_2d[j]
            (cC_2d, rC) = atom_data_2d[3 - i - j] # The third atom
            
            dist_AB = np.linalg.norm(cA_2d - cB_2d)
            
            # Max radius of a sphere fitting between A and B, whose center is on the line AB
            r_candidate_pair = max(0.0, (dist_AB - rA - rB) / 2.0)
            
            if r_candidate_pair > epsilon:
                vec_AB = (cB_2d - cA_2d) / dist_AB
                center_candidate = cA_2d + (rA + r_candidate_pair) * vec_AB
                
                # Check collision with the third atom C.
                # And check if this center is inside the main triangle (on boundary allowed)
                if np.linalg.norm(center_candidate - cC_2d) >= (rC + r_candidate_pair - epsilon) and \
                   is_point_in_triangle_2d(center_candidate, *tri_points_2d, epsilon=epsilon, strict_interior=False):
                    max_r_gate_candidates.append(r_candidate_pair)
                    
    # 4. Heuristic: Incircle solution for symmetrical cases with equal radii (robust for inner gap)
    # This specifically addresses the equilateral triangle case where Apollonius might not yield the inner gap directly,
    # and provides a robust value for the central hole for identical atoms.
    if abs(r1 - r2) < epsilon and abs(r2 - r3) < epsilon: # Only if radii are approximately equal
        # Calculate semi-perimeter
        s = (np.linalg.norm(c1_2d - c2_2d) + np.linalg.norm(c2_2d - c3_2d) + np.linalg.norm(c3_2d - c1_2d)) / 2.0
        # Calculate area (using original coordinates for better numerical stability)
        # Using shoelace formula for area of 2D triangle: 0.5 * |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)|
        area = 0.5 * abs(c1_2d[0]*(c2_2d[1]-c3_2d[1]) + c2_2d[0]*(c3_2d[1]-c1_2d[1]) + c3_2d[0]*(c1_2d[1]-c2_2d[1]))
        
        if s > epsilon: # Avoid division by zero
            incircle_radius_geometric = area / s
            r_incircle_candidate = max(0.0, incircle_radius_geometric - r1) # Subtract common radius
            
            # Check if this incircle candidate is the largest, or if it provides a better inner gap
            if r_incircle_candidate > epsilon:
                 max_r_gate_candidates.append(r_incircle_candidate)
                
    
    # Select the maximum valid radius found
    final_r_gate = max(max_r_gate_candidates) if max_r_gate_candidates else 0.0
    
    return final_r_gate >= probe_radius, final_r_gate


def check_face_permeability_mc(p1, p2, p3, r1, r2, r3, probe_radius, n_samples=500000, epsilon=1e-6):
    """
    Monte Carlo check for permeability.
    Ground truth validator: samples points in the triangle and checks if they fit a probe.
    
    Parameters
    ----------
    p1, p2, p3 : np.ndarray
        3D coordinates of the atomic centers.
    r1, r2, r3 : float
        Van der Waals radii of the atoms.
    probe_radius : float
        Radius of the spherical probe.
    n_samples : int, optional
        Number of Monte Carlo samples.
    epsilon : float, optional
        Tolerance for floating point comparisons.
    
    Returns
    -------
    bool: True if a probe of probe_radius can pass.
    """
    # 1. Project 3D atom centers to 2D plane of the face
    orig_p1 = p1
    orig_p2 = p2
    orig_p3 = p3

    v12_3d = p2 - orig_p1
    v13_3d = p3 - orig_p1
    
    norm_v12 = np.linalg.norm(v12_3d)
    if norm_v12 < epsilon: return False # Collinear
    u_vec = v12_3d / norm_v12
    
    v_perp_to_u = v13_3d - np.dot(v13_3d, u_vec) * u_vec
    norm_v_perp = np.linalg.norm(v_perp_to_u)
    if norm_v_perp < epsilon: return False # Collinear
    v_vec = v_perp_to_u / norm_v_perp
    
    c1_2d = np.array([0.0, 0.0])
    c2_2d = np.array([norm_v12, 0.0])
    c3_2d = np.array([np.dot(v13_3d, u_vec), np.dot(v13_3d, v_vec)])
    
    # Bounding box for sampling (triangle bounding box)
    min_x = min(c1_2d[0], c2_2d[0], c3_2d[0])
    max_x = max(c1_2d[0], c2_2d[0], c3_2d[0])
    min_y = min(c1_2d[1], c2_2d[1], c3_2d[1])
    max_y = max(c1_2d[1], c2_2d[1], c3_2d[1])
    
    # Sample points. Strictly inside the bounding box of the triangle.
    pts = np.random.uniform(low=[min_x, min_y], 
                            high=[max_x, max_y], 
                            size=(n_samples, 2))
                            
    # Distance checks squared
    sq_dist1 = np.sum((pts - c1_2d)**2, axis=1)
    sq_dist2 = np.sum((pts - c2_2d)**2, axis=1)
    sq_dist3 = np.sum((pts - c3_2d)**2, axis=1)
    
    limit1 = (r1 + probe_radius)**2
    limit2 = (r2 + probe_radius)**2
    limit3 = (r3 + probe_radius)**2
    
    # Barycentric coordinates check to ensure point is strictly INSIDE the triangle
    inside_triangle = np.array([is_point_in_triangle_2d(p_test, c1_2d, c2_2d, c3_2d, epsilon=epsilon, strict_interior=False) for p_test in pts]) # Use default epsilon, allow boundary

    valid_points = (sq_dist1 >= limit1) & (sq_dist2 >= limit2) & (sq_dist3 >= limit3) & inside_triangle
    
    return np.any(valid_points)
