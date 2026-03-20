import numpy as np

def is_point_in_triangle_2d(p, c1, c2, c3, epsilon=1e-6, strict_interior=False):
    """
    Checks if point p is inside or on the boundary of triangle (c1, c2, c3) in 2D.
    Uses barycentric coordinates.
    
    Parameters
    ----------
    p : np.ndarray
        The 2D point to check.
    c1, c2, c3 : np.ndarray
        The 2D vertices of the triangle.
    epsilon : float, optional
        Tolerance for floating point comparisons.
    strict_interior : bool, optional
        If True, only points strictly inside the triangle (not on boundary) are considered.
    
    Returns
    -------
    bool
        True if the point is inside (or on boundary, if strict_interior is False).
    """
    x1, y1 = c1
    x2, y2 = c2
    x3, y3 = c3
    px, py = p

    # Calculate barycentric coordinates
    # Denominator for all barycentric coords
    det_T = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    
    # If det_T is zero, triangle is degenerate (collinear points), so point can't be "inside"
    if abs(det_T) < epsilon:
        return False

    alpha = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / det_T
    beta = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / det_T
    gamma = 1 - alpha - beta

    if strict_interior:
        # Check if barycentric coordinates are strictly greater than 0
        return (alpha > epsilon) and \
               (beta > epsilon) and \
               (gamma > epsilon)
    else:
        # Check if barycentric coordinates are within [0, 1] range (with tolerance)
        return (-epsilon <= alpha <= 1.0 + epsilon) and \
               (-epsilon <= beta <= 1.0 + epsilon) and \
               (-epsilon <= gamma <= 1.0 + epsilon)
