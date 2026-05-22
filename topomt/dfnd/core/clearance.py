import math
from collections import namedtuple

import numpy as np

# DFND clearance primitives answer physical questions: can a probe center cross
# a face, and can it reside in a tetrahedron. Apollonius constructions are used
# internally to generate candidate centers, but the public API deliberately uses
# clearance/residence names because Apollonius candidates are not the full
# physical contract by themselves.
GateResult = namedtuple('GateResult', ['radius', 'center', 'kind'])
ResidenceResult = namedtuple(
    'ResidenceResult', ['radius', 'center', 'kind', 'r_apollonius4', 'apollonius4_valid']
)


def face_three_atom_clearance_candidate_2d(c1, r1, c2, r2, c3, r3, epsilon=1e-9):
    """Return the three-atom face-clearance candidate.

    This is an Apollonius construction internally: it solves for a circle
    tangent to the three atomic disks in the face plane. The public name avoids
    equating that construction with the full DFND gate primitive, because the
    final gate radius also considers two-atom and validation constraints.
    """
    dx12 = c2[0] - c1[0]
    dx23 = c3[0] - c2[0]
    dx31 = c1[0] - c3[0]
    dy12 = c2[1] - c1[1]
    dy23 = c3[1] - c2[1]
    dy31 = c1[1] - c3[1]
    g1 = c1[0] ** 2 + c1[1] ** 2 - r1**2
    g2 = c2[0] ** 2 + c2[1] ** 2 - r2**2
    g3 = c3[0] ** 2 + c3[1] ** 2 - r3**2
    det123 = dx12 * dy23 - dx23 * dy12
    if abs(det123) < epsilon:
        return None
    denominator = 2 * (c1[1] * dx23 + c2[1] * dx31 + c3[1] * dx12)
    if abs(denominator) < epsilon:
        return None
    a = -(dy23 * g1 + dy31 * g2 + dy12 * g3)
    b = 2 * (r1 * dy23 + r2 * dy31 + r3 * dy12)
    c = dx23 * g1 + dx31 * g2 + dx12 * g3
    d = -2 * (r1 * dx23 + r2 * dx31 + r3 * dx12)
    dx = denominator * c1[0] - a
    dy = denominator * c1[1] - c
    dr = denominator * r1
    p_coef = b * b + d * d - denominator * denominator
    q_coef = b * dx + d * dy + denominator * dr
    r_coef = dx * dx + dy * dy - dr * dr
    if abs(p_coef) < epsilon:
        return None
    discriminant = q_coef * q_coef - p_coef * r_coef
    if abs(discriminant) < epsilon:
        discriminant = 0
    if discriminant < 0:
        return None
    radius = (q_coef - math.sqrt(discriminant)) / p_coef
    x = (a + b * radius) / denominator
    y = (c + d * radius) / denominator
    return radius, np.array([x, y])


def _point_in_triangle_2d(point, a, b, c, epsilon=1e-9):
    point = np.asarray(point, dtype=float)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)
    v0 = c - a
    v1 = b - a
    v2 = point - a
    dot00 = np.dot(v0, v0)
    dot01 = np.dot(v0, v1)
    dot02 = np.dot(v0, v2)
    dot11 = np.dot(v1, v1)
    dot12 = np.dot(v1, v2)
    denominator = dot00 * dot11 - dot01 * dot01
    if abs(denominator) < epsilon:
        return False
    inv_denominator = 1.0 / denominator
    u = (dot11 * dot02 - dot01 * dot12) * inv_denominator
    v = (dot00 * dot12 - dot01 * dot02) * inv_denominator
    return bool(u >= -epsilon and v >= -epsilon and u + v <= 1.0 + epsilon)


def _face_three_atom_candidate_centers_2d(c1, r1, c2, r2, c3, r3, epsilon):
    """Both Apollonius branches: centers of circles tangent to three face disks.

    The single-branch helper above keeps the inner solution for compatibility,
    but the gate needs both roots because in some triangles the inner candidate
    is the (q + sqrt) branch while (q - sqrt) is the exterior circle.
    """
    dx12 = c2[0] - c1[0]
    dx23 = c3[0] - c2[0]
    dx31 = c1[0] - c3[0]
    dy12 = c2[1] - c1[1]
    dy23 = c3[1] - c2[1]
    dy31 = c1[1] - c3[1]
    g1 = c1[0] ** 2 + c1[1] ** 2 - r1**2
    g2 = c2[0] ** 2 + c2[1] ** 2 - r2**2
    g3 = c3[0] ** 2 + c3[1] ** 2 - r3**2
    if abs(dx12 * dy23 - dx23 * dy12) < epsilon:
        return []
    denominator = 2 * (c1[1] * dx23 + c2[1] * dx31 + c3[1] * dx12)
    if abs(denominator) < epsilon:
        return []
    a = -(dy23 * g1 + dy31 * g2 + dy12 * g3)
    b = 2 * (r1 * dy23 + r2 * dy31 + r3 * dy12)
    c = dx23 * g1 + dx31 * g2 + dx12 * g3
    d = -2 * (r1 * dx23 + r2 * dx31 + r3 * dx12)
    dx = denominator * c1[0] - a
    dy = denominator * c1[1] - c
    dr = denominator * r1
    p_coef = b * b + d * d - denominator * denominator
    q_coef = b * dx + d * dy + denominator * dr
    r_coef = dx * dx + dy * dy - dr * dr
    if abs(p_coef) < epsilon:
        return []
    discriminant = q_coef * q_coef - p_coef * r_coef
    if discriminant < 0:
        return []
    sqrt_discriminant = math.sqrt(discriminant)
    centers = []
    for radius in ((q_coef - sqrt_discriminant) / p_coef, (q_coef + sqrt_discriminant) / p_coef):
        if radius > epsilon:
            x = (a + b * radius) / denominator
            y = (c + d * radius) / denominator
            centers.append(np.array([x, y]))
    return centers


def face_gate_radius(p1, p2, p3, r1, r2, r3, epsilon=1e-6):
    """Largest empty circle clipped to a triangular face (the gate).

    A clipped largest-empty-circle active-set solver, mirroring
    tetrahedron_residence_radius in 2D: enumerate interior (three-atom, both
    Apollonius branches) and edge (two-atom on each triangle edge line)
    candidates, keep those whose center lies in the face, recompute the actual
    clearance against the three atoms, and return the largest.
    """
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    p3 = np.asarray(p3, dtype=float)
    v12 = p2 - p1
    v13 = p3 - p1
    norm_v12 = np.linalg.norm(v12)
    if norm_v12 < epsilon:
        return GateResult(0.0, np.zeros(2), 'none')
    u_vec = v12 / norm_v12
    v_perp = v13 - np.dot(v13, u_vec) * u_vec
    norm_v_perp = np.linalg.norm(v_perp)
    if norm_v_perp < epsilon:
        return GateResult(0.0, np.zeros(2), 'none')
    v_vec = v_perp / norm_v_perp

    c1 = np.array([0.0, 0.0])
    c2 = np.array([norm_v12, 0.0])
    c3 = np.array([np.dot(v13, u_vec), np.dot(v13, v_vec)])
    points = (c1, c2, c3)
    radii = (float(r1), float(r2), float(r3))
    edges = ((0, 1), (0, 2), (1, 2))
    candidates = []

    # Interior candidates: tangent to all three atoms (both Apollonius branches).
    for center in _face_three_atom_candidate_centers_2d(c1, r1, c2, r2, c3, r3, epsilon):
        candidates.append(('face3', center))

    # Edge candidates: largest empty circle tangent to an atom pair with center
    # on a triangle edge line (every pair against every edge line). This is the
    # 2D analogue of the tetrahedron edge stratum and replaces the old gap-waist
    # candidate, which computed a bottleneck rather than a max-clearance point.
    for edge_a, edge_b in edges:
        q0 = points[edge_a]
        direction = points[edge_b] - points[edge_a]
        norm = np.linalg.norm(direction)
        if norm < epsilon:
            continue
        direction = direction / norm
        for pair_a, pair_b in edges:
            for center in _tangent2_on_line(
                q0, direction, points[pair_a], radii[pair_a], points[pair_b], radii[pair_b], epsilon
            ):
                candidates.append(('pair2', center))

    best_radius = 0.0
    best_center = np.zeros(2)
    best_kind = 'none'
    stacked = np.vstack(points)
    for kind, center in candidates:
        if not _point_in_triangle_2d(center, c1, c2, c3, epsilon=epsilon):
            continue
        radius = float(np.min(np.linalg.norm(stacked - center, axis=1) - np.asarray(radii)))
        if radius > best_radius:
            best_radius = radius
            best_center = center
            best_kind = kind

    return GateResult(best_radius, best_center, best_kind)


def _inside_tetrahedron(point, vertices, tol=1e-7):
    """Return true if point lies in the closed tetrahedron."""
    matrix = np.column_stack(
        [vertices[0] - vertices[3], vertices[1] - vertices[3], vertices[2] - vertices[3]]
    )
    try:
        bary = np.linalg.solve(matrix, point - vertices[3])
    except np.linalg.LinAlgError:
        return False
    return bool(np.all(bary >= -tol) and bary.sum() <= 1.0 + tol)


_FACES = ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))
_TRIPLES = ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))
_EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))


def _quadratic_roots(a_q, b_q, c_q, epsilon):
    discriminant = b_q * b_q - 4.0 * a_q * c_q
    if discriminant < -epsilon:
        return []
    sqrt_discriminant = math.sqrt(max(0.0, discriminant))
    if abs(a_q) < epsilon:
        return [-c_q / b_q] if abs(b_q) > epsilon else []
    return [
        (-b_q + sqrt_discriminant) / (2.0 * a_q),
        (-b_q - sqrt_discriminant) / (2.0 * a_q),
    ]


def _tangent3_on_plane(p1, r1, p2, r2, p3, r3, q0, normal, epsilon):
    """Return three-atom Apollonius candidate centers on a plane."""
    matrix = np.array([2.0 * (p2 - p1), 2.0 * (p3 - p1), normal])
    try:
        matrix_inverse = np.linalg.inv(matrix)
    except np.linalg.LinAlgError:
        return []
    u = np.array(
        [
            (p2 @ p2 - p1 @ p1) - (r2 * r2 - r1 * r1),
            (p3 @ p3 - p1 @ p1) - (r3 * r3 - r1 * r1),
            normal @ q0,
        ]
    )
    v = np.array([-2.0 * (r2 - r1), -2.0 * (r3 - r1), 0.0])
    A = matrix_inverse @ v
    B = matrix_inverse @ u
    D = B - p1
    a_q = A @ A - 1.0
    b_q = 2.0 * (A @ D - r1)
    c_q = D @ D - r1 * r1
    return [A * radius + B for radius in _quadratic_roots(a_q, b_q, c_q, epsilon) if radius > epsilon]


def _tangent2_on_line(q0, direction, ca, ra, cb, rb, epsilon):
    """Return two-atom tangency candidate centers on a line."""
    diff = ca - cb
    linear = direction @ diff
    constant = -2.0 * (q0 @ diff) + (ca @ ca - cb @ cb) - (ra * ra - rb * rb)
    centers = []
    if abs(ra - rb) > epsilon:
        alpha = -linear / (ra - rb)
        beta = constant / (2.0 * (ra - rb))
        qa = q0 - ca
        a_q = 1.0 - alpha * alpha
        b_q = 2.0 * (direction @ qa) - 2.0 * alpha * (beta + ra)
        c_q = qa @ qa - (beta + ra) ** 2
        for value in _quadratic_roots(a_q, b_q, c_q, epsilon):
            if alpha * value + beta > epsilon:
                centers.append(q0 + value * direction)
    elif abs(linear) > epsilon:
        value = constant / (2.0 * linear)
        center = q0 + value * direction
        if float(np.linalg.norm(center - ca)) - ra > epsilon:
            centers.append(center)
    return centers


def _apollonius4_roots(vertices, radii, epsilon):
    """Return positive four-atom Apollonius radii and linear coefficients."""
    origin = vertices[3]
    a1 = vertices[0] - origin
    a2 = vertices[1] - origin
    a3 = vertices[2] - origin
    k = (
        np.dot(a1, a1) - radii[0] ** 2,
        np.dot(a2, a2) - radii[1] ** 2,
        np.dot(a3, a3) - radii[2] ** 2,
        -radii[3] ** 2,
    )
    matrix = 2.0 * np.array([a1, a2, a3])
    v_k = np.array([k[0] - k[3], k[1] - k[3], k[2] - k[3]])
    v_r = -2.0 * np.array([radii[0] - radii[3], radii[1] - radii[3], radii[2] - radii[3]])
    try:
        matrix_inverse = np.linalg.inv(matrix)
    except np.linalg.LinAlgError:
        return [], None, None, origin
    A = matrix_inverse @ v_r
    B = matrix_inverse @ v_k
    a_q = np.dot(A, A) - 1.0
    b_q = 2.0 * (np.dot(A, B) - radii[3])
    c_q = np.dot(B, B) - radii[3] ** 2
    roots = [root for root in _quadratic_roots(a_q, b_q, c_q, epsilon) if root > epsilon]
    return roots, A, B, origin


def tetrahedron_residence_radius(coords, radii, epsilon=1e-9):
    """Return the residence radius of a Delaunay tetrahedron."""
    vertices = np.asarray(coords, dtype=float)
    radii = np.asarray(radii, dtype=float)
    candidates = []

    # Four-atom Apollonius candidates are interior candidates only. They do not
    # define residence unless their center is valid and no better lower-stratum
    # candidate exists.
    roots, A, B, origin = _apollonius4_roots(vertices, radii, epsilon)
    r_apollonius4 = max(roots) if roots else 0.0
    apollonius4_valid = False
    for root in roots:
        center = A * root + B + origin
        candidates.append(('interior4', center))
        if _inside_tetrahedron(center, vertices):
            clearance = float(np.min(np.linalg.norm(vertices - center, axis=1) - radii))
            if abs(clearance - root) <= 1e-6:
                apollonius4_valid = True

    # Three-atom Apollonius candidates on each face catch optima controlled by a
    # face active set rather than by all four atoms.
    for first, second, third in _FACES:
        q0 = vertices[first]
        normal = np.cross(vertices[second] - vertices[first], vertices[third] - vertices[first])
        norm = np.linalg.norm(normal)
        if norm < epsilon:
            continue
        normal = normal / norm
        for t1, t2, t3 in _TRIPLES:
            centers = _tangent3_on_plane(
                vertices[t1], radii[t1], vertices[t2], radii[t2], vertices[t3], radii[t3], q0, normal, epsilon
            )
            for center in centers:
                candidates.append(('face3', center))

    # Two-atom line candidates recover sliver and edge optima that are invisible
    # to higher-order Apollonius candidates.
    for edge_a, edge_b in _EDGES:
        q0 = vertices[edge_a]
        direction = vertices[edge_b] - vertices[edge_a]
        norm = np.linalg.norm(direction)
        if norm < epsilon:
            continue
        direction = direction / norm
        for pair_a, pair_b in _EDGES:
            centers = _tangent2_on_line(
                q0, direction, vertices[pair_a], radii[pair_a], vertices[pair_b], radii[pair_b], epsilon
            )
            for center in centers:
                candidates.append(('edge2', center))

    best_radius = 0.0
    best_center = np.array([0.0, 0.0, 0.0])
    best_kind = 'none'
    for kind, center in candidates:
        if not _inside_tetrahedron(center, vertices):
            continue
        clearance = float(np.min(np.linalg.norm(vertices - center, axis=1) - radii))
        if clearance > best_radius:
            best_radius = clearance
            best_center = center
            best_kind = kind

    return ResidenceResult(best_radius, best_center, best_kind, float(r_apollonius4), apollonius4_valid)



# --- Vectorized batch residence ("brute-force" reference for the mesh) --------
# Same active-set enumeration as tetrahedron_residence_radius, but the Python
# loop runs only over the ~53 active-set combinations (interior/face/edge) while
# every operation is batched over all T tetrahedra. It bit-matches the scalar
# solver (to floating-point precision); a differential test guards that. This is
# the redundant, simple reference; a redundancy-free (unique face/edge) version
# can later be diff-tested against it.

_KIND_BY_CODE = ('interior4', 'face3', 'edge2')


def _det3_batch(a, b, c):
    return np.einsum('...i,...i->...', a, np.cross(b, c))


def _solve3_batch(matrix, rhs):
    c0, c1, c2 = matrix[:, :, 0], matrix[:, :, 1], matrix[:, :, 2]
    det = _det3_batch(c0, c1, c2)
    safe = np.where(np.abs(det) < 1e-12, 1.0, det)
    x = np.stack([_det3_batch(rhs, c1, c2) / safe,
                  _det3_batch(c0, rhs, c2) / safe,
                  _det3_batch(c0, c1, rhs) / safe], axis=1)
    x[np.abs(det) < 1e-12] = np.nan
    return x


def _quad_roots_batch(a, b, c, epsilon):
    disc = b * b - 4.0 * a * c
    real = disc >= -epsilon
    sqrt_disc = np.sqrt(np.clip(disc, 0.0, None))
    lin = np.abs(a) < epsilon
    a_safe = np.where(lin, 1.0, a)
    r1 = np.where(real, (-b + sqrt_disc) / (2.0 * a_safe), np.nan)
    r2 = np.where(real, (-b - sqrt_disc) / (2.0 * a_safe), np.nan)
    b_safe = np.where(np.abs(b) < epsilon, 1.0, b)
    r_lin = np.where(lin & (np.abs(b) >= epsilon), -c / b_safe, np.nan)
    return np.stack([np.where(lin, r_lin, r1), np.where(lin, np.nan, r2)], axis=1)


def tetrahedron_residence_radius_batch(coords, radii, epsilon=1e-9, inside_tol=1e-7):
    """Vectorized residence radius for many tetrahedra at once.

    coords: (T, 4, 3), radii: (T, 4). Returns (radius (T,), center (T, 3),
    kind_code (T,), r_apollonius4 (T,), apollonius4_valid (T,)) where kind_code
    indexes _KIND_BY_CODE, or -1 for 'none'.
    """
    V = np.asarray(coords, dtype=float)
    radii = np.asarray(radii, dtype=float)
    candidates = []
    kinds = []

    def add(center, code):
        candidates.append(center)
        kinds.append(code)

    # interior: tangent to four atoms
    origin = V[:, 3]
    a1, a2, a3 = V[:, 0] - origin, V[:, 1] - origin, V[:, 2] - origin
    k4 = -radii[:, 3] ** 2
    kk = [np.einsum('ti,ti->t', a, a) - radii[:, j] ** 2 for a, j in ((a1, 0), (a2, 1), (a3, 2))]
    M = np.stack([2 * a1, 2 * a2, 2 * a3], axis=1)
    v_k = np.stack([kk[0] - k4, kk[1] - k4, kk[2] - k4], axis=1)
    v_r = -2 * np.stack([radii[:, 0] - radii[:, 3], radii[:, 1] - radii[:, 3], radii[:, 2] - radii[:, 3]], axis=1)
    A = _solve3_batch(M, v_r)
    B = _solve3_batch(M, v_k)
    aq = np.einsum('ti,ti->t', A, A) - 1.0
    bq = 2.0 * (np.einsum('ti,ti->t', A, B) - radii[:, 3])
    cq = np.einsum('ti,ti->t', B, B) - radii[:, 3] ** 2
    roots = _quad_roots_batch(aq, bq, cq, epsilon)
    for k in range(2):
        rt = roots[:, k]
        center = A * rt[:, None] + B + origin
        add(np.where((rt > epsilon)[:, None], center, np.nan), 0)

    # face: tangent to three atoms with center on a face plane
    for fa, fb, fc in _FACES:
        q0 = V[:, fa]
        normal = np.cross(V[:, fb] - V[:, fa], V[:, fc] - V[:, fa])
        norm = np.linalg.norm(normal, axis=1, keepdims=True)
        normal = np.where(norm < epsilon, 0.0, normal / np.where(norm < epsilon, 1.0, norm))
        for ta, tb, tc in _TRIPLES:
            p1, p2, p3 = V[:, ta], V[:, tb], V[:, tc]
            r1, r2, r3 = radii[:, ta], radii[:, tb], radii[:, tc]
            MM = np.stack([2 * (p2 - p1), 2 * (p3 - p1), normal], axis=1)
            u = np.stack([np.einsum('ti,ti->t', p2, p2) - np.einsum('ti,ti->t', p1, p1) - (r2 * r2 - r1 * r1),
                          np.einsum('ti,ti->t', p3, p3) - np.einsum('ti,ti->t', p1, p1) - (r3 * r3 - r1 * r1),
                          np.einsum('ti,ti->t', normal, q0)], axis=1)
            vv = np.stack([-2 * (r2 - r1), -2 * (r3 - r1), np.zeros_like(r1)], axis=1)
            Aa = _solve3_batch(MM, vv)
            Bb = _solve3_batch(MM, u)
            D = Bb - p1
            aq2 = np.einsum('ti,ti->t', Aa, Aa) - 1.0
            bq2 = 2.0 * (np.einsum('ti,ti->t', Aa, D) - r1)
            cq2 = np.einsum('ti,ti->t', D, D) - r1 * r1
            r2roots = _quad_roots_batch(aq2, bq2, cq2, epsilon)
            for k in range(2):
                rt = r2roots[:, k]
                add(np.where((rt > epsilon)[:, None], Aa * rt[:, None] + Bb, np.nan), 1)

    # edge: tangent to two atoms with center on an edge line
    for ea, eb in _EDGES:
        q0 = V[:, ea]
        direction = V[:, eb] - V[:, ea]
        norm = np.linalg.norm(direction, axis=1, keepdims=True)
        direction = np.where(norm < epsilon, 0.0, direction / np.where(norm < epsilon, 1.0, norm))
        for pa, pb in _EDGES:
            ca, cb = V[:, pa], V[:, pb]
            ra, rb = radii[:, pa], radii[:, pb]
            diff = ca - cb
            linear = np.einsum('ti,ti->t', direction, diff)
            const = (-2 * np.einsum('ti,ti->t', q0, diff)
                     + (np.einsum('ti,ti->t', ca, ca) - np.einsum('ti,ti->t', cb, cb)) - (ra * ra - rb * rb))
            neq = np.abs(ra - rb) > epsilon
            rad = np.where(neq, ra - rb, 1.0)
            alpha = -linear / rad
            beta = const / (2.0 * rad)
            qa = q0 - ca
            aq3 = 1.0 - alpha * alpha
            bq3 = 2.0 * np.einsum('ti,ti->t', direction, qa) - 2.0 * alpha * (beta + ra)
            cq3 = np.einsum('ti,ti->t', qa, qa) - (beta + ra) ** 2
            troots = _quad_roots_batch(aq3, bq3, cq3, epsilon)
            for k in range(2):
                t = troots[:, k]
                R = alpha * t + beta
                add(np.where((neq & (R > epsilon))[:, None], q0 + t[:, None] * direction, np.nan), 2)
            lin_ok = (~neq) & (np.abs(linear) >= epsilon)
            l_safe = np.where(np.abs(linear) < epsilon, 1.0, linear)
            t = const / (2.0 * l_safe)
            center = q0 + t[:, None] * direction
            R = np.linalg.norm(center - ca, axis=1) - ra
            add(np.where((lin_ok & (R > epsilon))[:, None], center, np.nan), 2)

    C = np.stack(candidates, axis=1)              # (T, K, 3)
    code = np.asarray(kinds)                      # (K,)
    e0, e1, e2 = V[:, 0] - V[:, 3], V[:, 1] - V[:, 3], V[:, 2] - V[:, 3]
    vol = _det3_batch(e0, e1, e2)
    vol_safe = np.where(np.abs(vol) < epsilon, 1.0, vol)
    d = C - V[:, 3][:, None, :]
    b0 = np.einsum('tki,ti->tk', d, np.cross(e1, e2)) / vol_safe[:, None]
    b1 = np.einsum('tki,ti->tk', d, np.cross(e2, e0)) / vol_safe[:, None]
    b2 = np.einsum('tki,ti->tk', d, np.cross(e0, e1)) / vol_safe[:, None]
    inside = ((b0 >= -inside_tol) & (b1 >= -inside_tol) & (b2 >= -inside_tol)
              & ((1 - b0 - b1 - b2) >= -inside_tol) & (np.abs(vol)[:, None] > epsilon))
    dist = np.linalg.norm(C[:, :, None, :] - V[:, None, :, :], axis=3) - radii[:, None, :]
    clearance_raw = dist.min(axis=2)
    clearance = np.where(inside & np.isfinite(clearance_raw), clearance_raw, -np.inf)
    best = np.argmax(clearance, axis=1)
    rows = np.arange(C.shape[0])
    radius = clearance[rows, best]
    center = C[rows, best]
    kind_code = code[best]
    has = radius > 0
    radius = np.where(has, radius, 0.0)
    center = np.where(has[:, None], center, 0.0)
    kind_code = np.where(has, kind_code, -1)

    # four-atom Apollonius diagnostics (the interior candidates are columns 0, 1)
    pos = roots > epsilon
    masked = np.where(pos, roots, -np.inf)
    r_apollonius4 = np.where(masked.max(axis=1) > 0, masked.max(axis=1), 0.0)
    apollonius4_valid = (
        inside[:, :2] & (np.abs(clearance_raw[:, :2] - roots) <= 1e-6) & pos
    ).any(axis=1)
    return radius, center, kind_code, r_apollonius4, apollonius4_valid


# --- Vectorized batch face gate (brute reference, mirrors the residence batch) -
_GATE_KIND_BY_CODE = ('face3', 'pair2')


def face_gate_radius_batch(coords, radii, epsilon=1e-6):
    """Vectorized face gate for many faces at once.

    coords: (P, 3, 3), radii: (P, 3). Returns (radius (P,), center2d (P, 2),
    kind_code (P,)) where kind_code indexes _GATE_KIND_BY_CODE, or -1 for 'none'.
    Bit-matches the scalar face_gate_radius (a differential test guards it).
    """
    coords = np.asarray(coords, dtype=float)
    radii = np.asarray(radii, dtype=float)
    P = coords.shape[0]
    p1, p2, p3 = coords[:, 0], coords[:, 1], coords[:, 2]

    # Project each face into its own 2D frame (batched).
    v12 = p2 - p1
    n12 = np.linalg.norm(v12, axis=1)
    u = v12 / np.where(n12 < epsilon, 1.0, n12)[:, None]
    v13 = p3 - p1
    v_perp = v13 - np.einsum('pi,pi->p', v13, u)[:, None] * u
    nperp = np.linalg.norm(v_perp, axis=1)
    vv = v_perp / np.where(nperp < epsilon, 1.0, nperp)[:, None]
    degenerate = (n12 < epsilon) | (nperp < epsilon)

    c1 = np.zeros((P, 2))
    c2 = np.stack([n12, np.zeros(P)], axis=1)
    c3 = np.stack([np.einsum('pi,pi->p', v13, u), np.einsum('pi,pi->p', v13, vv)], axis=1)
    pts = np.stack([c1, c2, c3], axis=1)            # (P, 3, 2)
    r = radii                                       # (P, 3)
    candidates = []
    kinds = []

    # Interior: tangent to all three atoms (both Apollonius branches), in 2D.
    cx = pts[:, :, 0]
    cy = pts[:, :, 1]
    dx12 = cx[:, 1] - cx[:, 0]; dx23 = cx[:, 2] - cx[:, 1]; dx31 = cx[:, 0] - cx[:, 2]
    dy12 = cy[:, 1] - cy[:, 0]; dy23 = cy[:, 2] - cy[:, 1]; dy31 = cy[:, 0] - cy[:, 2]
    g1 = cx[:, 0] ** 2 + cy[:, 0] ** 2 - r[:, 0] ** 2
    g2 = cx[:, 1] ** 2 + cy[:, 1] ** 2 - r[:, 1] ** 2
    g3 = cx[:, 2] ** 2 + cy[:, 2] ** 2 - r[:, 2] ** 2
    det123 = dx12 * dy23 - dx23 * dy12
    denom = 2 * (cy[:, 0] * dx23 + cy[:, 1] * dx31 + cy[:, 2] * dx12)
    aa = -(dy23 * g1 + dy31 * g2 + dy12 * g3)
    bb = 2 * (r[:, 0] * dy23 + r[:, 1] * dy31 + r[:, 2] * dy12)
    cc = dx23 * g1 + dx31 * g2 + dx12 * g3
    dd = -2 * (r[:, 0] * dx23 + r[:, 1] * dx31 + r[:, 2] * dx12)
    dxv = denom * cx[:, 0] - aa
    dyv = denom * cy[:, 0] - cc
    drv = denom * r[:, 0]
    p_coef = bb * bb + dd * dd - denom * denom
    q_coef = bb * dxv + dd * dyv + denom * drv
    r_coef = dxv * dxv + dyv * dyv - drv * drv
    disc = q_coef * q_coef - p_coef * r_coef
    ok3 = (np.abs(det123) >= epsilon) & (np.abs(denom) >= epsilon) & (np.abs(p_coef) >= epsilon) & (disc >= 0)
    sqrt3 = np.sqrt(np.clip(disc, 0.0, None))
    p_safe = np.where(np.abs(p_coef) < epsilon, 1.0, p_coef)
    den_safe = np.where(np.abs(denom) < epsilon, 1.0, denom)
    for sign in (-1.0, 1.0):
        root = (q_coef + sign * sqrt3) / p_safe
        center = np.stack([(aa + bb * root) / den_safe, (cc + dd * root) / den_safe], axis=1)
        keep = ok3 & (root > epsilon)
        candidates.append(np.where(keep[:, None], center, np.nan))
        kinds.append(0)

    # Edge: largest empty circle tangent to a pair, center on a triangle edge line.
    edges = ((0, 1), (0, 2), (1, 2))
    for ea, eb in edges:
        q0 = pts[:, ea]
        direction = pts[:, eb] - pts[:, ea]
        norm = np.linalg.norm(direction, axis=1)
        direction = direction / np.where(norm < epsilon, 1.0, norm)[:, None]
        for pa, pb in edges:
            ca, cb = pts[:, pa], pts[:, pb]
            ra, rb = r[:, pa], r[:, pb]
            diff = ca - cb
            linear = np.einsum('pi,pi->p', direction, diff)
            const = (-2 * np.einsum('pi,pi->p', q0, diff)
                     + (np.einsum('pi,pi->p', ca, ca) - np.einsum('pi,pi->p', cb, cb)) - (ra * ra - rb * rb))
            neq = np.abs(ra - rb) > epsilon
            rad = np.where(neq, ra - rb, 1.0)
            alpha = -linear / rad
            beta = const / (2.0 * rad)
            qa = q0 - ca
            aq = 1.0 - alpha * alpha
            bq = 2.0 * np.einsum('pi,pi->p', direction, qa) - 2.0 * alpha * (beta + ra)
            cq = np.einsum('pi,pi->p', qa, qa) - (beta + ra) ** 2
            troots = _quad_roots_batch(aq, bq, cq, epsilon)
            for k in range(2):
                t = troots[:, k]
                R = alpha * t + beta
                center = q0 + t[:, None] * direction
                candidates.append(np.where((neq & (R > epsilon))[:, None], center, np.nan))
                kinds.append(1)
            lin_ok = (~neq) & (np.abs(linear) >= epsilon)
            l_safe = np.where(np.abs(linear) < epsilon, 1.0, linear)
            t = const / (2.0 * l_safe)
            center = q0 + t[:, None] * direction
            R = np.linalg.norm(center - ca, axis=1) - ra
            candidates.append(np.where((lin_ok & (R > epsilon))[:, None], center, np.nan))
            kinds.append(1)

    C = np.stack(candidates, axis=1)                # (P, K, 2)
    code = np.asarray(kinds)
    # point-in-triangle (barycentric, matches _point_in_triangle_2d)
    v0 = (c3 - c1)[:, None, :]
    v1 = (c2 - c1)[:, None, :]
    v2 = C - c1[:, None, :]
    dot00 = np.einsum('pki,pki->pk', v0, v0)
    dot01 = np.einsum('pki,pki->pk', v0, v1)
    dot11 = np.einsum('pki,pki->pk', v1, v1)
    dot02 = np.einsum('pki,pki->pk', v0, v2)
    dot12 = np.einsum('pki,pki->pk', v1, v2)
    bary_den = dot00 * dot11 - dot01 * dot01
    bary_safe = np.where(np.abs(bary_den) < epsilon, 1.0, bary_den)
    bu = (dot11 * dot02 - dot01 * dot12) / bary_safe
    bv = (dot00 * dot12 - dot01 * dot02) / bary_safe
    inside = (bu >= -epsilon) & (bv >= -epsilon) & (bu + bv <= 1.0 + epsilon) & (np.abs(bary_den) >= epsilon)
    dist = np.linalg.norm(C[:, :, None, :] - pts[:, None, :, :], axis=3) - r[:, None, :]
    clearance = dist.min(axis=2)
    clearance = np.where(inside & np.isfinite(clearance) & ~degenerate[:, None], clearance, -np.inf)
    best = np.argmax(clearance, axis=1)
    rows = np.arange(P)
    radius = clearance[rows, best]
    center = C[rows, best]
    kind_code = code[best]
    has = radius > 0
    radius = np.where(has, radius, 0.0)
    center = np.where(has[:, None], center, 0.0)
    kind_code = np.where(has, kind_code, -1)
    return radius, center, kind_code
