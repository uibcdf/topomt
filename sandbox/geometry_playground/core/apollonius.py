import numpy as np
import math

def bitangent(c1, r1, c2, r2, epsilon=1e-9):
    """
    Find a circle that is externally tangent to the circles c1, c2.
    If the circles overlap, will return a circle with radius 0.
    If there is gap between the two circles, will return a circle with the diameter equal to the gap.
    
    Returns: (radius, center) or None
    """
    dx = c2[0] - c1[0]
    dy = c2[1] - c1[1]
    d = math.sqrt(dx*dx + dy*dy)
    
    if d < epsilon:
        # Concentric
        if abs(r1 - r2) < epsilon:
            # Share radius -> infinite circles? No, logic says radius 0 at circumference?
            # The JS code returns r=0 at x=c1.x+c1.r.
            return (0.0, np.array([c1[0]+r1, c1[1]]))
        return None
        
    if r1 + r2 <= d:
        # Gap exists
        gap = d - r1 - r2
        r = gap / 2.0
        # Center is at distance r1+r from c1 along the line
        # x = c1.x + (r1+r) * dx/d
        scale = (r1 + r) / d
        x = c1[0] + scale * dx
        y = c1[1] + scale * dy
        return (r, np.array([x, y]))
        
    # No gap (overlap). Return r=0 at intersection?
    # JS code calculates intersection points for r=0.
    # We stick to our logic: if overlap, gate is closed (r=0).
    # But returning a valid center is useful.
    # For now, return 0.0
    return (0.0, c1) # Dummy center? Or intersection?


def solve_dependent(c1, r1, c2, r2, c3, r3, epsilon=1e-9):
    """
    Handle linearly dependent (collinear) centers.
    Delegates to bitangent of the pair that contains the gap?
    The JS code checks if two are equal, or if they are collinear.
    For collinear 1-2-3, the gap is determined by the pair that is NOT enclosing the other?
    Actually, JS code checks which pair defines the line and calls bitangent.
    """
    dx12 = c2[0] - c1[0]
    dy12 = c2[1] - c1[1]
    dx23 = c3[0] - c2[0]
    dy23 = c3[1] - c2[1]
    dx31 = c1[0] - c3[0]
    dy31 = c1[1] - c3[1]
    
    # If points are same... handle
    if abs(dx12) + abs(dy12) < epsilon:
        return bitangent(c3, r3, c1, r1, epsilon)
    if abs(dx23) + abs(dy23) < epsilon:
        return bitangent(c1, r1, c2, r2, epsilon)
    if abs(dx31) + abs(dy31) < epsilon:
        return bitangent(c2, r2, c3, r3, epsilon)
        
    # Collinear logic from JS
    # b such that c3 = c1 + b*v12
    if abs(dx12) >= epsilon:
        b = -dx31 / dx12
    elif abs(dy12) >= epsilon:
        b = -dy31 / dy12
    else:
        return None
        
    scale2 = 1.0 / (dx12*dx12 + dy12*dy12)
    scale = math.sqrt(scale2)
    
    dr12 = (r2 - r1) * scale
    dr23 = (r3 - r2) * scale
    dr31 = (r1 - r3) * scale
    
    D = -2 * (b * dr12 + dr31)
    if abs(D) < epsilon: return None
    
    rr1 = r1*r1 * scale2
    rr2 = r2*r2 * scale2
    rr3 = r3*r3 * scale2
    
    disc = -(dr12 - 1) * (dr12 + 1) * (dr31 - b) * (dr31 + b) * (dr23 - b + 1) * (dr23 + b - 1)
    if abs(disc) < epsilon: disc = 0
    if disc < 0: return None
    
    bb = b*b
    xhat = (rr1 * dr23 + rr2 * dr31 + rr3 * dr12 - bb * dr12 - dr31) / D
    yhat = math.sqrt(disc) / D
    rhat = -(rr3 - b * rr2 + (b - 1) * rr1 - bb + b) / D
    
    x = c1[0] + xhat * dx12 - yhat * dy12
    y = c1[1] + xhat * dy12 + yhat * dx12
    r = rhat / scale
    
    return (r, np.array([x, y]))


def solve_apollonius_js_port(c1, r1, c2, r2, c3, r3, epsilon=1e-9):
    """
    Port of 'apollonius' npm package.
    """
    dx12 = c2[0] - c1[0]
    dx23 = c3[0] - c2[0]
    dx31 = c1[0] - c3[0]
    
    dy12 = c2[1] - c1[1]
    dy23 = c3[1] - c2[1]
    dy31 = c1[1] - c3[1]
    
    g1 = c1[0]**2 + c1[1]**2 - r1**2
    g2 = c2[0]**2 + c2[1]**2 - r2**2
    g3 = c3[0]**2 + c3[1]**2 - r3**2
    
    det123 = dx12 * dy23 - dx23 * dy12
    
    if abs(det123) < epsilon:
        return solve_dependent(c1, r1, c2, r2, c3, r3, epsilon)
        
    D = 2 * (c1[1] * dx23 + c2[1] * dx31 + c3[1] * dx12)
    if abs(D) < epsilon: return None
    
    a = -(dy23 * g1 + dy31 * g2 + dy12 * g3)
    b = 2 * (r1 * dy23 + r2 * dy31 + r3 * dy12)
    c = dx23 * g1 + dx31 * g2 + dx12 * g3
    d = -2 * (r1 * dx23 + r2 * dx31 + r3 * dx12)
    
    dx = D * c1[0] - a
    dy = D * c1[1] - c
    dr = D * r1
    
    P = b*b + d*d - D*D
    Q = b*dx + d*dy + D*dr
    R = dx*dx + dy*dy - dr*dr
    
    if abs(P) < epsilon: return None
    
    disc = Q*Q - P*R
    if abs(disc) < epsilon: disc = 0
    if disc < 0: return None
    
    # JS uses (Q - sqrt) / P
    r = (Q - math.sqrt(disc)) / P
    x = (a + b * r) / D
    y = (c + d * r) / D
    
    return (r, np.array([x, y]))
