"""Synthetic dummy-atom shapes for DFND validation and exploration.

These produce coordinates (and optional PDBs) of argon-like dummy atoms in simple
geometries whose topography is known by construction: a hollow sphere is an
enclosed void, a tube is a channel, a solid ball has no cavity. See
``devguide/DFND/synthetic_benchmarks.md`` for the design and the probe-tight wall
spacing rule ``d < sqrt(3) * (r_atom + R_probe)``.
"""

import numpy as np

ARGON_VDW_RADIUS = 1.88

# Bondi vdW radii of noble-gas elements, used as inert dummy atoms whose radius is
# encoded by the element symbol so mixed-radii systems survive a PDB round trip.
VDW_RADIUS_BY_ELEMENT = {'HE': 1.40, 'NE': 1.54, 'AR': 1.88, 'KR': 2.02, 'XE': 2.16}


def _finalize(coords, atom_radius, jitter, seed):
    coords = np.asarray(coords, dtype=float)
    if jitter:
        rng = np.random.default_rng(seed)
        coords = coords + rng.normal(scale=jitter, size=coords.shape)
    radii = np.full(coords.shape[0], float(atom_radius), dtype=float)
    return coords, radii


def argon_cube(probe_radius=1.4, atom_radius=ARGON_VDW_RADIUS, jitter=0.0, seed=0):
    """Eight argon atoms, one at each cube vertex, sized so the body diagonal
    (opposite vertices) equals exactly ``2*atom_radius + 2*probe_radius``.

    Then the cube centre is exactly ``atom_radius + probe_radius`` from every
    vertex, so the largest empty ball at the centre has radius exactly
    ``probe_radius``: the probe *just* fits. The simplest possible enclosed cell,
    and a marginal-residence + cospherical-degenerate corner case by design."""
    body_diagonal = 2.0 * (atom_radius + probe_radius)
    edge = body_diagonal / np.sqrt(3.0)
    h = edge / 2.0
    pts = np.array([[sx * h, sy * h, sz * h]
                    for sx in (-1.0, 1.0) for sy in (-1.0, 1.0) for sz in (-1.0, 1.0)])
    return _finalize(pts, atom_radius, jitter, seed)


def tetrahedron(edge=5.3, atom_radius=ARGON_VDW_RADIUS, jitter=0.0, seed=0):
    """Four atoms at the vertices of a regular tetrahedron."""
    scale = edge / (2.0 * np.sqrt(2.0))
    pts = np.array(
        [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float
    ) * scale
    return _finalize(pts, atom_radius, jitter, seed)


def hollow_cube(half=8.0, wall_spacing=3.5, atom_radius=ARGON_VDW_RADIUS, jitter=0.0, seed=0):
    """A cubic shell: atoms on the faces of a cube on a perfect cubic lattice ->
    an enclosed void. On a perfect lattice (jitter=0) the points are massively
    coplanar/cospherical -> the worst case for Delaunay degeneracy (WP4)."""
    axis = np.arange(-half, half + 1e-9, wall_spacing)
    gx, gy, gz = np.meshgrid(axis, axis, axis, indexing='ij')
    grid = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
    on_face = np.any(np.abs(np.abs(grid) - half) < 1e-6, axis=1)
    return _finalize(grid[on_face], atom_radius, jitter, seed)


def hollow_sphere(sphere_radius=10.0, wall_spacing=4.0, atom_radius=ARGON_VDW_RADIUS,
                  jitter=0.0, seed=0):
    """Atoms evenly spread on a sphere surface (Fibonacci sphere) -> enclosed void.

    The interior void exists only if the wall is probe-tight at the chosen
    ``wall_spacing`` (see the module docstring).
    """
    n = max(4, int(round(4.0 * np.pi * sphere_radius**2 / wall_spacing**2)))
    i = np.arange(n)
    golden = np.pi * (3.0 - np.sqrt(5.0))
    y = 1.0 - 2.0 * (i + 0.5) / n
    r = np.sqrt(np.clip(1.0 - y * y, 0.0, None))
    theta = golden * i
    pts = np.stack([np.cos(theta) * r, y, np.sin(theta) * r], axis=1) * sphere_radius
    return _finalize(pts, atom_radius, jitter, seed)


def mixed_radii_shell(sphere_radius=10.0, wall_spacing=4.0,
                      elements=('HE', 'NE', 'AR', 'KR', 'XE'), jitter=0.1, seed=0):
    """A hollow sphere whose wall atoms are a random mix of noble-gas elements of
    different vdW radius. Mixed radii are encoded by element symbol, so this
    survives a PDB round trip (a reader re-derives radii from the element).
    Returns ``(coords, radii, element_symbols)``."""
    coords, _r = hollow_sphere(sphere_radius, wall_spacing, jitter=0.0, seed=seed)
    rng = np.random.default_rng(seed)
    symbols = rng.choice(np.array(elements), size=len(coords))
    radii = np.array([VDW_RADIUS_BY_ELEMENT[s] for s in symbols], dtype=float)
    if jitter:
        coords = coords + np.random.default_rng(seed + 1).normal(scale=jitter, size=coords.shape)
    return coords, radii, symbols


def hollow_sphere_patchy(sphere_radius=10.0, wall_spacing=3.0, sparse_fraction=0.6,
                         atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A closed hollow sphere whose +y hemisphere is sparsely sampled (a fraction of
    its atoms removed). The cavity is still geometrically closed, but the sparse
    side leaks the probe -- non-uniform surface sampling within a single body, the
    realistic version of the wall-density sensitivity failure."""
    coords, _r = hollow_sphere(sphere_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    rng = np.random.default_rng(seed)
    upper = np.where(coords[:, 1] > 0)[0]
    drop = rng.choice(upper, size=int(sparse_fraction * len(upper)), replace=False)
    keep = np.ones(len(coords), dtype=bool)
    keep[drop] = False
    return _finalize(coords[keep], atom_radius, jitter, seed)


def hollow_sphere_with_opening(sphere_radius=10.0, wall_spacing=3.5, opening_half_angle_deg=30.0,
                               atom_radius=ARGON_VDW_RADIUS, jitter=0.0, seed=0):
    """Hollow sphere with a polar cap removed -> one mouth -> a pocket."""
    coords, _radii = hollow_sphere(sphere_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    # Pole axis is +y (see hollow_sphere). Remove atoms within the cap angle.
    cos_cut = np.cos(np.deg2rad(opening_half_angle_deg))
    keep = (coords[:, 1] / sphere_radius) < cos_cut
    return _finalize(coords[keep], atom_radius, jitter, seed)


def dumbbell(lobe_radius=6.0, separation=8.0, wall_spacing=3.5,
             atom_radius=ARGON_VDW_RADIUS, jitter=0.0, seed=0):
    """Two overlapping hollow spheres along x -> a peanut shell enclosing one void
    with an internal waist (throat). Demonstrates volume vs connectivity: a small
    probe sees one connected void; a large probe is blocked at the waist."""
    if separation >= 2.0 * lobe_radius:
        raise ValueError('separation must be < 2*lobe_radius so the lobes overlap')
    base, _r = hollow_sphere(lobe_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    c1 = base + np.array([-separation / 2.0, 0.0, 0.0])
    c2 = base + np.array([separation / 2.0, 0.0, 0.0])
    center1 = np.array([-separation / 2.0, 0.0, 0.0])
    center2 = np.array([separation / 2.0, 0.0, 0.0])
    keep1 = np.linalg.norm(c1 - center2, axis=1) >= lobe_radius
    keep2 = np.linalg.norm(c2 - center1, axis=1) >= lobe_radius
    coords = np.vstack([c1[keep1], c2[keep2]])
    return _finalize(coords, atom_radius, jitter, seed)


def cylinder_tube(length=20.0, tube_radius=6.0, wall_spacing=4.0,
                  atom_radius=ARGON_VDW_RADIUS, jitter=0.0, seed=0):
    """Atoms on an open cylindrical surface (no end caps) -> channel with two mouths."""
    n_rings = max(2, int(round(length / wall_spacing)) + 1)
    n_circ = max(3, int(round(2.0 * np.pi * tube_radius / wall_spacing)))
    z_values = np.linspace(-length / 2.0, length / 2.0, n_rings)
    angles = np.linspace(0.0, 2.0 * np.pi, n_circ, endpoint=False)
    pts = []
    for z in z_values:
        for a in angles:
            pts.append([tube_radius * np.cos(a), tube_radius * np.sin(a), z])
    return _finalize(pts, atom_radius, jitter, seed)


def solid_ball(ball_radius=8.0, spacing=3.5, atom_radius=ARGON_VDW_RADIUS,
               jitter=0.0, seed=0):
    """Atoms filling a ball on a cubic grid -> no interior cavity (negative control)."""
    n = int(np.ceil(2.0 * ball_radius / spacing))
    axis = (np.arange(n + 1) - n / 2.0) * spacing
    gx, gy, gz = np.meshgrid(axis, axis, axis, indexing='ij')
    grid = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
    inside = np.linalg.norm(grid, axis=1) <= ball_radius
    return _finalize(grid[inside], atom_radius, jitter, seed)


def _grid_box(half_x, half_y, z_min, z_max, spacing):
    """Cubic-lattice points filling [-half_x, half_x] x [-half_y, half_y] x [z_min, z_max]."""
    ax = np.arange(-half_x, half_x + 1e-9, spacing)
    ay = np.arange(-half_y, half_y + 1e-9, spacing)
    az = np.arange(z_min, z_max + 1e-9, spacing)
    gx, gy, gz = np.meshgrid(ax, ay, az, indexing='ij')
    return np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)


def _tube_surface(start, end, radius, wall_spacing):
    """Ring points on the open cylindrical surface from ``start`` to ``end`` (no caps)."""
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    axis = end - start
    length = float(np.linalg.norm(axis))
    axis = axis / length
    # An orthonormal frame (u, v) spanning the plane perpendicular to the axis.
    tmp = np.array([1.0, 0.0, 0.0]) if abs(axis[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(axis, tmp)
    u = u / np.linalg.norm(u)
    v = np.cross(axis, u)
    n_rings = max(2, int(round(length / wall_spacing)) + 1)
    n_circ = max(3, int(round(2.0 * np.pi * radius / wall_spacing)))
    ts = np.linspace(0.0, length, n_rings)
    angles = np.linspace(0.0, 2.0 * np.pi, n_circ, endpoint=False)
    pts = []
    for t in ts:
        center = start + axis * t
        for a in angles:
            pts.append(center + radius * (np.cos(a) * u + np.sin(a) * v))
    return np.asarray(pts, dtype=float)


def rotate(coords, angles_deg=(0.0, 0.0, 0.0)):
    """Rotate coordinates by intrinsic X, Y, Z angles (for orientation-invariance tests)."""
    rx, ry, rz = np.deg2rad(angles_deg)
    cx, sx = np.cos(rx), np.sin(rx)
    cy, sy = np.cos(ry), np.sin(ry)
    cz, sz = np.cos(rz), np.sin(rz)
    mx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    my = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    mz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    rotation = mz @ my @ mx
    return np.asarray(coords, dtype=float) @ rotation.T


def surface_bowl(bowl_radius=8.0, depth=4.0, margin=6.0, slab_extra=2.0, spacing=3.5,
                 atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A solid slab with a spherical-cap depression carved into its top face.

    Shallow ``depth`` -> a wide shallow dent (surface_concavity); deep ``depth``
    approaching ``bowl_radius`` -> a deeper bowl (pocket). Open upward (+z)."""
    mouth_radius = np.sqrt(max(bowl_radius**2 - (bowl_radius - depth) ** 2, 0.0))
    half = mouth_radius + margin
    thickness = depth + slab_extra
    grid = _grid_box(half, half, 0.0, thickness, spacing)
    # Carving sphere center sits above the top face so it bites ``depth`` into it.
    carve_center = np.array([0.0, 0.0, thickness + bowl_radius - depth])
    keep = np.linalg.norm(grid - carve_center, axis=1) >= bowl_radius
    return _finalize(grid[keep], atom_radius, jitter, seed)


def blind_well(well_radius=4.0, depth=10.0, margin=6.0, floor=3.5, spacing=3.5,
               atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A solid slab with a blind cylindrical well bored from the top (one mouth -> pocket)."""
    half = well_radius + margin
    thickness = depth + floor
    grid = _grid_box(half, half, 0.0, thickness, spacing)
    radial = np.hypot(grid[:, 0], grid[:, 1])
    bored = (radial < well_radius) & (grid[:, 2] > thickness - depth)
    return _finalize(grid[~bored], atom_radius, jitter, seed)


def slab_with_pore(pore_radius=4.0, thickness=10.0, margin=6.0, spacing=3.5,
                   atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A solid slab pierced by a cylindrical pore through its full thickness (two mouths -> channel)."""
    half = pore_radius + margin
    grid = _grid_box(half, half, 0.0, thickness, spacing)
    radial = np.hypot(grid[:, 0], grid[:, 1])
    return _finalize(grid[radial >= pore_radius], atom_radius, jitter, seed)


def two_voids(sphere_radius=8.0, wall_spacing=3.5, gap=14.0,
              atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Two disjoint hollow spheres along x (two separate enclosed voids -> counting test)."""
    base, _r = hollow_sphere(sphere_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    offset = sphere_radius + gap / 2.0
    left = base + np.array([-offset, 0.0, 0.0])
    right = base + np.array([offset, 0.0, 0.0])
    return _finalize(np.vstack([left, right]), atom_radius, jitter, seed)


def _point_segment_distance(points, a, b):
    """Distance from each row of ``points`` to the segment a-b."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    ab = b - a
    t = np.clip((points - a) @ ab / (ab @ ab), 0.0, 1.0)
    proj = a + t[:, None] * ab
    return np.linalg.norm(points - proj, axis=1)


def branched_tube(arm_length=11.0, tube_radius=5.0, wall_spacing=3.5,
                  atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Three open tube arms meeting at the origin (a Y/T junction) -> channel with 3 mouths.

    Wall atoms that fall inside another arm's lumen near the junction are removed,
    so the junction stays hollow and the three arms form one connected channel."""
    o = np.zeros(3)
    axes = ([arm_length, 0.0, 0.0], [-arm_length, 0.0, 0.0], [0.0, arm_length, 0.0])
    arms = [_tube_surface(o, end, tube_radius, wall_spacing) for end in axes]
    kept = []
    for i, arm in enumerate(arms):
        intrudes = np.zeros(len(arm), dtype=bool)
        for j, end in enumerate(axes):
            if j == i:
                continue
            intrudes |= _point_segment_distance(arm, o, end) < tube_radius - 0.5
        kept.append(arm[~intrudes])
    return _finalize(np.vstack(kept), atom_radius, jitter, seed)


def nested_spheres(outer_radius=14.0, inner_radius=7.0, wall_spacing=3.5,
                   atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Two concentric hollow spheres -> a core void inside the inner shell plus a
    shell-gap void between the shells (tests nested-cavity separation)."""
    outer, _o = hollow_sphere(outer_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    inner, _i = hollow_sphere(inner_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed + 1)
    return _finalize(np.vstack([outer, inner]), atom_radius, jitter, seed)


def curved_tube(bend_radius=12.0, arc_deg=120.0, tube_radius=5.0, wall_spacing=3.5,
                n_segments=8, atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """An open tube whose axis follows a circular arc -> a bent channel (2 mouths)."""
    angles = np.linspace(0.0, np.deg2rad(arc_deg), n_segments + 1)
    axis_pts = np.stack([bend_radius * np.cos(angles), bend_radius * np.sin(angles),
                         np.zeros_like(angles)], axis=1)
    segments = [
        _tube_surface(axis_pts[i], axis_pts[i + 1], tube_radius, wall_spacing)
        for i in range(n_segments)
    ]
    return _finalize(np.vstack(segments), atom_radius, jitter, seed)


def flask(chamber_radius=9.0, neck_radius=3.0, neck_length=8.0, opening_half_angle_deg=28.0,
          wall_spacing=3.5, atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A spherical chamber with a narrow cylindrical neck to the surface (+y).

    Narrow ``neck_radius`` -> a pocket with a throat near the mouth; widen it and
    the throat opens. Demonstrates throat/bottleneck detection."""
    chamber, _c = hollow_sphere(chamber_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    cos_cut = np.cos(np.deg2rad(opening_half_angle_deg))
    chamber = chamber[(chamber[:, 1] / chamber_radius) < cos_cut]   # remove +y cap
    neck_start = np.array([0.0, chamber_radius * cos_cut, 0.0])
    neck_end = np.array([0.0, chamber_radius + neck_length, 0.0])
    neck = _tube_surface(neck_start, neck_end, neck_radius, wall_spacing)
    return _finalize(np.vstack([chamber, neck]), atom_radius, jitter, seed)


def hollow_sphere_two_openings(sphere_radius=10.0, wall_spacing=3.5,
                               opening1_half_angle_deg=35.0, opening2_half_angle_deg=15.0,
                               atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Hollow sphere with two polar caps removed (+y and -y), of possibly unequal
    size -> a channel with two mouths, one of which can be marginal."""
    coords, _r = hollow_sphere(sphere_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    yn = coords[:, 1] / sphere_radius
    keep = (yn < np.cos(np.deg2rad(opening1_half_angle_deg))) & \
           (yn > -np.cos(np.deg2rad(opening2_half_angle_deg)))
    return _finalize(coords[keep], atom_radius, jitter, seed)


def asymmetric_dumbbell(lobe_radius1=8.0, lobe_radius2=5.0, separation=11.0, wall_spacing=3.5,
                        atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Two overlapping hollow spheres of unequal radius -> a peanut void with a
    throat offset from the midpoint (asymmetric chambers)."""
    s1, _a = hollow_sphere(lobe_radius1, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    s2, _b = hollow_sphere(lobe_radius2, wall_spacing, atom_radius, jitter=0.0, seed=seed + 1)
    c1 = np.array([-separation / 2.0, 0.0, 0.0])
    c2 = np.array([separation / 2.0, 0.0, 0.0])
    s1 = s1 + c1
    s2 = s2 + c2
    keep1 = np.linalg.norm(s1 - c2, axis=1) >= lobe_radius2
    keep2 = np.linalg.norm(s2 - c1, axis=1) >= lobe_radius1
    return _finalize(np.vstack([s1[keep1], s2[keep2]]), atom_radius, jitter, seed)


def swiss_cheese(block_half=11.0, void_radius=4.5, void_spacing=7.0, spacing=3.0,
                 atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A solid block with a lattice of carved spherical voids. When the voids are
    spaced closer than 2*void_radius they merge -> a percolating cavity network."""
    grid = _grid_box(block_half, block_half, -block_half, block_half, spacing)
    centers_axis = np.arange(-block_half + void_spacing / 2.0, block_half, void_spacing)
    cx, cy, cz = np.meshgrid(centers_axis, centers_axis, centers_axis, indexing='ij')
    centers = np.stack([cx.ravel(), cy.ravel(), cz.ravel()], axis=1)
    carved = np.zeros(len(grid), dtype=bool)
    for c in centers:
        carved |= np.linalg.norm(grid - c, axis=1) < void_radius
    return _finalize(grid[~carved], atom_radius, jitter, seed)


def void_with_island(sphere_radius=11.0, island_radius=3.0, wall_spacing=3.5, island_spacing=3.0,
                     atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A hollow sphere with a small solid cluster floating at its centre. The void
    wraps around the island (a non-simply-connected cavity)."""
    shell, _s = hollow_sphere(sphere_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    island, _i = solid_ball(island_radius, island_spacing, atom_radius, jitter=0.0, seed=seed)
    return _finalize(np.vstack([shell, island]), atom_radius, jitter, seed)


def helical_tube(turns=1.5, helix_radius=8.0, pitch=10.0, tube_radius=4.5, wall_spacing=3.5,
                 n_segments=24, atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """An open tube whose axis follows a helix -> a channel along a complex 3D path."""
    t = np.linspace(0.0, 2.0 * np.pi * turns, n_segments + 1)
    axis_pts = np.stack([helix_radius * np.cos(t), helix_radius * np.sin(t),
                         pitch * t / (2.0 * np.pi)], axis=1)
    segments = [
        _tube_surface(axis_pts[i], axis_pts[i + 1], tube_radius, wall_spacing)
        for i in range(n_segments)
    ]
    return _finalize(np.vstack(segments), atom_radius, jitter, seed)


def onion_shells(radii=(15.0, 10.0, 5.5), wall_spacing=3.5,
                 atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Concentric hollow spheres -> a core void plus one shell-gap void per gap
    (tests counting of nested cavities)."""
    shells = []
    for k, sphere_radius in enumerate(radii):
        pts, _r = hollow_sphere(sphere_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed + k)
        shells.append(pts)
    return _finalize(np.vstack(shells), atom_radius, jitter, seed)


def sliver_sheet(extent=18.0, spacing=3.5, z_noise=0.15,
                 atom_radius=ARGON_VDW_RADIUS, jitter=0.0, seed=0):
    """A single near-coplanar layer of atoms (a flat sheet). Adversarial: the flat
    Delaunay slivers have huge circumradii, so alpha-shape detectors can invent a
    false tunnel through the sheet; DFND's in-sphere clearance should report no
    enclosed cavity. ``z_noise`` keeps the triangulation well-defined."""
    half = extent / 2.0
    axis = np.arange(-half, half + 1e-9, spacing)
    gx, gy = np.meshgrid(axis, axis, indexing='ij')
    rng = np.random.default_rng(seed)
    z = rng.normal(scale=z_noise, size=gx.size)
    pts = np.stack([gx.ravel(), gy.ravel(), z], axis=1)
    return _finalize(pts, atom_radius, jitter, seed)


def pocket_with_mouth_intruder(intruder=True, sphere_radius=9.0, wall_spacing=3.5,
                               opening_half_angle_deg=18.0,
                               atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A hollow sphere with one opening (a pocket). With ``intruder=True`` a single
    extra atom sits in the mouth: it caps the opening so the chamber seals into a
    void. A detector that scores only the 3-atom wall gate misses this 4th atom."""
    coords, _r = hollow_sphere(sphere_radius, wall_spacing, atom_radius, jitter=0.0, seed=seed)
    cos_cut = np.cos(np.deg2rad(opening_half_angle_deg))
    coords = coords[(coords[:, 1] / sphere_radius) < cos_cut]   # remove +y cap -> mouth
    if intruder:
        mouth = np.array([[0.0, sphere_radius * cos_cut, 0.0]])  # one atom in the opening
        coords = np.vstack([coords, mouth])
    return _finalize(coords, atom_radius, jitter, seed)


def rough_surface(extent=20.0, spacing=4.4, amplitude=1.3, n_layers=3,
                  atom_radius=ARGON_VDW_RADIUS, jitter=0.0, seed=0):
    """A solid slab whose top face is roughened: the top layer of atoms is displaced
    in z into sub-probe bumps. No real cavity exists, but the many shallow dimples
    between surface atoms produce a spray of tiny spurious pockets -- a deliberate
    over-reporting / surface-noise study (the dimples open upward, so no void traps)."""
    half = extent / 2.0
    axis = np.arange(-half, half + 1e-9, spacing)
    gx, gy = np.meshgrid(axis, axis, indexing='ij')
    flat_x, flat_y = gx.ravel(), gy.ravel()
    rng = np.random.default_rng(seed)
    layers = [np.stack([flat_x, flat_y, np.full(flat_x.size, -layer * spacing)], axis=1)
              for layer in range(1, n_layers)]                      # filled backing below z=0
    bump_z = amplitude * np.sin(flat_x) * np.cos(flat_y) + rng.normal(scale=0.35, size=flat_x.size)
    top = np.stack([flat_x, flat_y, bump_z], axis=1)                # roughened surface layer
    return _finalize(np.vstack(layers + [top]), atom_radius, jitter, seed)


def solid_block(half=7.0, spacing=3.2):
    """A solid cubic-lattice block centred at the origin (a dummy 'body')."""
    return _grid_box(half, half, -half, half, spacing)


def two_balls(ball_radius=6.0, gap=8.0, spacing=3.2,
              atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Two solid (convex) balls separated by a gap along x. There is no cavity, yet
    the concave saddle between the two bodies is reported as a phantom pocket: a
    false positive of running a single-structure pocket detector on two bodies."""
    ball, _r = solid_ball(ball_radius, spacing, atom_radius, jitter=0.0, seed=seed)
    offset = ball_radius + gap / 2.0
    coords = np.vstack([ball + np.array([-offset, 0.0, 0.0]),
                        ball + np.array([offset, 0.0, 0.0])])
    return _finalize(coords, atom_radius, jitter, seed)


def parallel_plates(extent=20.0, separation=3.0, plate_thickness=2.0, spacing=3.2,
                    atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Two flat plates facing each other across a thin gap. A thin gap fragments
    into spurious voids and pockets instead of one clean feature."""
    half = extent / 2.0
    bottom = _grid_box(half, half, -plate_thickness, 0.0, spacing)
    top = _grid_box(half, half, separation, separation + plate_thickness, spacing)
    return _finalize(np.vstack([bottom, top]), atom_radius, jitter, seed)


def flat_slab(extent=20.0, thickness=4.0, spacing=4.0,
              atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A flat solid slab -- a purely convex surface with no cavity (a negative
    control). At some grid spacings it nonetheless emits spurious surface pockets
    and even false enclosed voids: a pathological false-positive case."""
    half = extent / 2.0
    grid = _grid_box(half, half, -thickness, 0.0, spacing)
    return _finalize(grid, atom_radius, jitter, seed)


def two_blocks(gap=4.0, half=7.0, spacing=3.2, atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Two solid blocks separated by a gap along x -> two bodies sharing one
    interface. The wet layer in the gap is the wet half of the interface; each
    block is a dry bank. ``gap`` is the spacing between the facing inner faces."""
    block = solid_block(half, spacing)
    offset = half + gap / 2.0
    left = block + np.array([-offset, 0.0, 0.0])
    right = block + np.array([offset, 0.0, 0.0])
    return _finalize(np.vstack([left, right]), atom_radius, jitter, seed)


def three_blocks(gap=4.0, half=6.0, spacing=3.2, atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Three solid blocks in a row along x -> three bodies and two interfaces."""
    block = solid_block(half, spacing)
    step = 2.0 * half + gap
    blocks = [block + np.array([k * step, 0.0, 0.0]) for k in (-1, 0, 1)]
    return _finalize(np.vstack(blocks), atom_radius, jitter, seed)


def interface_pocket(gap=2.0, pocket_radius=5.0, half=8.0, spacing=3.2, mouth=False,
                     atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Two blocks in tight contact except for a spherical cavity carved out of the
    contact plane -> a buried pocket whose lining comes from both bodies (the
    protein-protein interface pocket). With ``mouth=True`` a channel is also bored
    from the cavity to the +z surface, so the interface pocket gains one mouth."""
    block = solid_block(half, spacing)
    offset = half + gap / 2.0
    left = block + np.array([-offset, 0.0, 0.0])
    right = block + np.array([offset, 0.0, 0.0])
    coords = np.vstack([left, right])
    carved = np.linalg.norm(coords, axis=1) < pocket_radius     # carve cavity at contact centre
    if mouth:                                                   # bore a throat up to +z
        radial = np.hypot(coords[:, 0], coords[:, 1])
        carved |= (radial < pocket_radius * 0.55) & (coords[:, 2] > 0.0)
    return _finalize(coords[~carved], atom_radius, jitter, seed)


def three_body_junction(place_radius=9.0, pocket_radius=5.5, half=6.0, spacing=3.2,
                        atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Three blocks arranged at 120 deg around the origin with a cavity carved at
    the meeting point -> a central cavity lined by three bodies (a three-way
    interface junction)."""
    block = solid_block(half, spacing)
    blocks = []
    for k in range(3):
        angle = 2.0 * np.pi * k / 3.0
        center = np.array([place_radius * np.cos(angle), place_radius * np.sin(angle), 0.0])
        blocks.append(block + center)
    coords = np.vstack(blocks)
    carved = np.linalg.norm(coords, axis=1) < pocket_radius
    return _finalize(coords[~carved], atom_radius, jitter, seed)


def packed_blob(blob_radius=12.0, min_separation=3.4, atom_radius=ARGON_VDW_RADIUS,
                jitter=0.0, seed=0):
    """A random close-packed ball of atoms with no cavity (a realistic negative
    control). Used to measure the spurious-feature (false-positive) rate at scale.
    Points are rejection-sampled in a ball with a minimum separation."""
    rng = np.random.default_rng(seed)
    accepted = []
    attempts = 0
    target = int(8.0 * blob_radius ** 3 / min_separation ** 3)
    while len(accepted) < target and attempts < 60 * target:
        attempts += 1
        p = rng.uniform(-blob_radius, blob_radius, size=3)
        if np.linalg.norm(p) > blob_radius:
            continue
        if accepted and np.min(np.linalg.norm(np.asarray(accepted) - p, axis=1)) < min_separation:
            continue
        accepted.append(p)
    return _finalize(np.asarray(accepted, dtype=float), atom_radius, jitter, seed)


def oblate_void(disk_radius=7.0, half_thickness=2.0, margin=3.0, spacing=3.0,
                atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A sealed oblate (disk-shaped) cavity carved inside a solid block -- a thin
    flat void about one probe thick. Tests anisotropic (slit-like) cavities."""
    half = disk_radius + margin
    halfz = half_thickness + margin
    grid = _grid_box(half, half, -halfz, halfz, spacing)
    radial = np.hypot(grid[:, 0], grid[:, 1])
    carved = (radial / disk_radius) ** 2 + (grid[:, 2] / half_thickness) ** 2 < 1.0
    return _finalize(grid[~carved], atom_radius, jitter, seed)


def conical_channel(top_radius=6.0, bottom_radius=1.5, length=16.0, wall_spacing=3.0,
                    atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """An open channel that tapers from a wide mouth to a sub-probe tip. The lumen
    crosses the residence threshold gradually along its length."""
    n_rings = max(2, int(round(length / wall_spacing)) + 1)
    z_values = np.linspace(0.0, length, n_rings)
    pts = []
    for z in z_values:
        radius = top_radius + (bottom_radius - top_radius) * (z / length)
        n_circ = max(3, int(round(2.0 * np.pi * radius / wall_spacing)))
        for a in np.linspace(0.0, 2.0 * np.pi, n_circ, endpoint=False):
            pts.append([radius * np.cos(a), radius * np.sin(a), z])
    return _finalize(np.asarray(pts, dtype=float), atom_radius, jitter, seed)


def star_void(core_radius=3.0, arm_length=7.0, arm_radius=2.0, n_arms=5, half=11.0, spacing=3.0,
              atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A sealed cavity with a central chamber and several radial arms carved inside
    a solid block (a star/branched void). Tests over-segmentation of lobes."""
    grid = _grid_box(half, half, -half, half, spacing)
    carved = np.linalg.norm(grid, axis=1) < core_radius
    for k in range(n_arms):
        angle = 2.0 * np.pi * k / n_arms
        axis = np.array([np.cos(angle), np.sin(angle), 0.0])
        proj = grid @ axis
        perp = np.linalg.norm(grid - np.outer(proj, axis), axis=1)
        carved |= (perp < arm_radius) & (proj > 0) & (proj < arm_length)
    return _finalize(grid[~carved], atom_radius, jitter, seed)


def two_chambers_septum(chamber_radius=4.5, septum=2.0, half=9.0, spacing=3.0,
                        atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """Two sealed spherical cavities separated by a thin internal wall (septum).
    Tests whether a thin wall keeps two voids apart or lets them merge into one."""
    grid = _grid_box(half, half, -half, half, spacing)
    offset = chamber_radius + septum / 2.0
    left = np.linalg.norm(grid - np.array([-offset, 0, 0]), axis=1) < chamber_radius
    right = np.linalg.norm(grid - np.array([offset, 0, 0]), axis=1) < chamber_radius
    return _finalize(grid[~(left | right)], atom_radius, jitter, seed)


def toroidal_void(major_radius=6.0, minor_radius=2.5, margin=3.0, spacing=3.0,
                  atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A sealed donut-shaped (genus-1) cavity carved inside a solid block. Tests
    non-trivial cavity topology."""
    half = major_radius + minor_radius + margin
    halfz = minor_radius + margin
    grid = _grid_box(half, half, -halfz, halfz, spacing)
    radial = np.hypot(grid[:, 0], grid[:, 1])
    carved = (radial - major_radius) ** 2 + grid[:, 2] ** 2 < minor_radius ** 2
    return _finalize(grid[~carved], atom_radius, jitter, seed)


def pocket_in_pocket(outer_radius=8.0, outer_depth=5.0, inner_radius=3.0, inner_depth=6.0,
                     margin=4.0, spacing=3.0, atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A wide shallow bowl with a smaller deeper well bored into its floor (a
    sub-pocket nested in a pocket). Tests hierarchical / multi-scale concavities."""
    half = outer_radius + margin
    thickness = outer_depth + inner_depth + margin
    grid = _grid_box(half, half, 0.0, thickness, spacing)
    radial = np.hypot(grid[:, 0], grid[:, 1])
    bowl = (radial < outer_radius) & (grid[:, 2] > thickness - outer_depth)
    well = (radial < inner_radius) & (grid[:, 2] > thickness - outer_depth - inner_depth)
    return _finalize(grid[~(bowl | well)], atom_radius, jitter, seed)


def u_channel(arm_separation=8.0, tube_radius=3.0, depth=10.0, margin=4.0, spacing=3.0,
              atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A U-shaped tunnel with both mouths on the top (+z) face -> one channel whose
    two external links open onto the same surface. Tests external-link clustering."""
    half_x = arm_separation / 2.0 + tube_radius + margin
    half_y = tube_radius + margin
    grid = _grid_box(half_x, half_y, 0.0, depth + margin, spacing)
    x, y, z = grid[:, 0], grid[:, 1], grid[:, 2]
    left_arm = (np.hypot(x + arm_separation / 2.0, y) < tube_radius) & (z > depth - depth) & (z < depth)
    right_arm = (np.hypot(x - arm_separation / 2.0, y) < tube_radius) & (z < depth)
    bottom = (np.hypot(z - tube_radius, y) < tube_radius) & (np.abs(x) < arm_separation / 2.0)
    return _finalize(grid[~(left_arm | right_arm | bottom)], atom_radius, jitter, seed)


def edge_cavity(bowl_radius=6.0, depth=5.0, block_half=8.0, spacing=3.0,
                atom_radius=ARGON_VDW_RADIUS, jitter=0.1, seed=0):
    """A bowl carved at a top corner of a finite block, so the cavity sits against
    the convex-hull boundary. Tests hull/OCEAN handling at the periphery."""
    grid = _grid_box(block_half, block_half, -block_half, block_half, spacing)
    corner = np.array([block_half, block_half, block_half])
    carved = np.linalg.norm(grid - corner, axis=1) < bowl_radius
    # also bore a little so it is a concavity, not just a clipped corner
    carved |= np.linalg.norm(grid - (corner - np.array([depth, depth, depth]) / 2.0), axis=1) < bowl_radius * 0.6
    return _finalize(grid[~carved], atom_radius, jitter, seed)


def to_pdb(coords, radii, path, element='AR', resname='DUM', elements=None):
    """Write dummy atoms as PDB HETATM records (for cross-algorithm comparison).

    Standard fixed-column PDB; the element is written in columns 13-16 (atom name)
    and 77-78 (element). Radii are not a PDB field, but mixed radii can be encoded
    by passing per-atom ``elements`` (e.g. noble gases of different vdW radius) so
    a reader re-derives them; otherwise the single ``element`` (default argon) is
    used for every atom.
    """
    coords = np.asarray(coords, dtype=float)
    lines = []
    for i, (x, y, z) in enumerate(coords, start=1):
        elem = (str(elements[i - 1]) if elements is not None else element).upper()
        serial = (i - 1) % 99999 + 1
        resseq = (i - 1) % 9999 + 1
        # Strict PDB columns: name 13-16, x/y/z 31-54, element right-justified 77-78.
        lines.append(
            '%-6s%5d %-4s%1s%3s %1s%4d%1s   %8.3f%8.3f%8.3f%6.2f%6.2f          %2s'
            % ('HETATM', serial, elem, '', resname, 'A', resseq, '', x, y, z, 1.0, 0.0, elem)
        )
    lines.append('END')
    with open(path, 'w') as handle:
        handle.write('\n'.join(lines) + '\n')


def to_molsysmt(coords, radii, elements=None, element='AR', resname='DUM'):
    """Convert dummy atoms into a molsysmt.MolSys molecular system.

    Creates standard PDB HETATM lines in-memory and converts them using molsysmt.convert.
    """
    import molsysmt as msm
    coords = np.asarray(coords, dtype=float)
    lines = []
    for i, (x, y, z) in enumerate(coords, start=1):
        elem = (str(elements[i - 1]) if elements is not None else element).upper()
        serial = (i - 1) % 99999 + 1
        resseq = (i - 1) % 9999 + 1
        lines.append(
            '%-6s%5d %-4s%1s%3s %1s%4d%1s   %8.3f%8.3f%8.3f%6.2f%6.2f          %2s'
            % ('HETATM', serial, elem, '', resname, 'A', resseq, '', x, y, z, 1.0, 0.0, elem)
        )
    lines.append('END')
    pdb_string = '\n'.join(lines) + '\n'
    return msm.convert(pdb_string, to_form='molsysmt.MolSys')


# Decorate all public functions in this module (except helper/converter functions) to support to_molsysmt parameter.
def _molsysmt_builder_decorator(func):
    import functools
    import inspect
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine the caller file path
        frame = inspect.currentframe().f_back
        caller_file = frame.f_code.co_filename if frame else ""
        
        # If called internally from synthetic.py itself, or from a test/devtool context,
        # default to returning coords/radii to support unpacking and internal compilation.
        # Otherwise (interactive Jupyter, scripts, public usage), return molsysmt.MolSys by default!
        is_internal_or_test = (
            "synthetic.py" in caller_file or
            "test_" in caller_file or 
            "build_synthetic_catalog" in caller_file or 
            "conftest" in caller_file
        )
        
        default_to_msm = not is_internal_or_test
        to_msm = kwargs.pop('to_molsysmt', default_to_msm)
        
        res = func(*args, **kwargs)
        if to_msm:
            if len(res) == 3:
                coords, radii, elements = res
            else:
                coords, radii = res
                elements = None
            return to_molsysmt(coords, radii, elements=elements)
        return res
    return wrapper


# Wrap all builder functions dynamically
for _name, _val in list(globals().items()):
    if (callable(_val) and not _name.startswith('_') 
            and _name not in ('to_pdb', 'to_molsysmt', 'first_existing_path', 'path')):
        globals()[_name] = _molsysmt_builder_decorator(_val)
