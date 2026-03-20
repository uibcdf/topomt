import numpy as np

def is_point_in_triangle_2d(p, c1, c2, c3, epsilon=1e-6, strict_interior=False):
    x1, y1 = c1; x2, y2 = c2; x3, y3 = c3; px, py = p
    det_T = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    if abs(det_T) < epsilon: return False
    alpha = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / det_T
    beta = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / det_T
    gamma = 1 - alpha - beta
    if strict_interior:
        return (alpha > epsilon) and (beta > epsilon) and (gamma > epsilon)
    else:
        return (-epsilon <= alpha <= 1.0 + epsilon) and \
               (-epsilon <= beta <= 1.0 + epsilon) and \
               (-epsilon <= gamma <= 1.0 + epsilon)