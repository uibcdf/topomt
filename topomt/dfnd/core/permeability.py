from .clearance import face_gate_radius


def check_face_permeability(p1, p2, p3, r1, r2, r3, epsilon=1e-6):
    """Return the scalar local gate radius for a triangular face.

    This compatibility wrapper keeps the historical DFND call site stable while
    the physical primitive lives in clearance.face_gate_radius. The richer
    GateResult keeps the active-set kind and center; this wrapper intentionally
    returns only the radius for older code paths.
    """
    return float(face_gate_radius(p1, p2, p3, r1, r2, r3, epsilon).radius)
