from collections import namedtuple

import numpy as np

from ..._private.jit import lazy_njit


SolventVolumeResult = namedtuple(
    'SolventVolumeResult',
    ['volume', 'empty_fraction', 'occupied_fraction', 'n_samples'],
)


def tetrahedron_volume(vertices) -> float:
    """Return the Euclidean volume of a tetrahedron."""
    vertices = np.asarray(vertices, dtype=float)
    if vertices.shape != (4, 3):
        raise ValueError('vertices must have shape (4, 3)')
    matrix = np.column_stack(
        [vertices[1] - vertices[0], vertices[2] - vertices[0], vertices[3] - vertices[0]]
    )
    return abs(float(np.linalg.det(matrix))) / 6.0


def _simplex_lattice_weights(resolution: int, alpha: float = 0.5) -> np.ndarray:
    """Return deterministic interior barycentric samples for a tetrahedron.

    The half-cell shift avoids sampling exactly on atoms at tetrahedron vertices.
    This is a stable first estimator, not an analytic solvent-volume formula.
    """
    if resolution < 1:
        raise ValueError('resolution must be >= 1')
    weights = []
    denominator = float(resolution + 4.0 * alpha)
    for i in range(resolution + 1):
        for j in range(resolution + 1 - i):
            for k in range(resolution + 1 - i - j):
                l = resolution - i - j - k
                weights.append(
                    [
                        (i + alpha) / denominator,
                        (j + alpha) / denominator,
                        (k + alpha) / denominator,
                        (l + alpha) / denominator,
                    ]
                )
    return np.asarray(weights, dtype=float)


_WEIGHT_CACHE: dict[int, np.ndarray] = {}


def tetrahedron_solvent_volume_estimate(
    vertices,
    radii,
    resolution: int = 8,
    epsilon: float = 1e-9,
) -> SolventVolumeResult:
    """Estimate empty volume inside a tetrahedron after local atom exclusion.

    The estimator samples deterministic barycentric points inside the tetrahedron
    and counts the fraction that is outside the four local atomic spheres. It is
    deliberately named as an estimate because it does not yet subtract exact
    sphere-tetrahedron intersections and does not include non-local atom
    intrusions.
    """
    vertices = np.asarray(vertices, dtype=float)
    radii = np.asarray(radii, dtype=float)
    if vertices.shape != (4, 3):
        raise ValueError('vertices must have shape (4, 3)')
    if radii.shape != (4,):
        raise ValueError('radii must have shape (4,)')

    volume = tetrahedron_volume(vertices)
    if volume <= epsilon:
        return SolventVolumeResult(0.0, 0.0, 1.0, 0)

    weights = _WEIGHT_CACHE.get(resolution)
    if weights is None:
        weights = _simplex_lattice_weights(resolution)
        _WEIGHT_CACHE[resolution] = weights

    points = weights @ vertices
    distances = np.linalg.norm(points[:, None, :] - vertices[None, :, :], axis=2)
    occupied = np.any(distances <= radii[None, :] + epsilon, axis=1)
    occupied_fraction = float(np.count_nonzero(occupied)) / float(len(points))
    empty_fraction = 1.0 - occupied_fraction
    return SolventVolumeResult(
        volume * empty_fraction,
        empty_fraction,
        occupied_fraction,
        int(len(points)),
    )


def tetrahedron_solvent_volume_estimate_batch(
    vertices,
    radii,
    resolution: int = 8,
    epsilon: float = 1e-9,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Estimate solvent volumes for a batch of tetrahedra."""
    vertices = np.asarray(vertices, dtype=float)
    radii = np.asarray(radii, dtype=float)
    if vertices.ndim != 3 or vertices.shape[1:] != (4, 3):
        raise ValueError('vertices must have shape (n_tetrahedra, 4, 3)')
    if radii.shape != vertices.shape[:2]:
        raise ValueError('radii must have shape (n_tetrahedra, 4)')

    volumes = np.zeros(vertices.shape[0], dtype=float)
    empty_fractions = np.zeros(vertices.shape[0], dtype=float)
    occupied_fractions = np.zeros(vertices.shape[0], dtype=float)
    n_samples = np.zeros(vertices.shape[0], dtype=int)
    for index in range(vertices.shape[0]):
        result = tetrahedron_solvent_volume_estimate(
            vertices[index],
            radii[index],
            resolution=resolution,
            epsilon=epsilon,
        )
        volumes[index] = result.volume
        empty_fractions[index] = result.empty_fraction
        occupied_fractions[index] = result.occupied_fraction
        n_samples[index] = result.n_samples
    return volumes, empty_fractions, occupied_fractions, n_samples


# --- Empty (solvent) volume by seeded Monte Carlo ---------------------------
#
# Empty (solvent) volume of a region is
#   vol(region) - vol(region ∩ union(atom balls)),
# the free space a solvent/ligand could occupy. Seeded Monte Carlo is used
# because in proteins the van der Waals spheres overlap pervasively (a covalent
# bond puts each atom's centre inside its neighbour's sphere) and non-local
# intruder atoms reach into a tetrahedron -- a sample is empty iff it lies
# outside *every* ball, so overlap and non-local intrusion are handled natively
# with no double subtraction. The error is the honest statistical half-width
# (~2 standard errors, ~95%); a fixed seed makes it reproducible. The analytic
# closed-form cases in tests are the oracle. See metrics_contract.md.

PreciseVolumeResult = namedtuple('PreciseVolumeResult', ['volume', 'error'])


def _cell_volumes(cells: np.ndarray) -> np.ndarray:
    """Volumes of a batch of tetrahedra ``(K, 4, 3)`` -> ``(K,)``."""
    a = cells[:, 1] - cells[:, 0]
    b = cells[:, 2] - cells[:, 0]
    c = cells[:, 3] - cells[:, 0]
    return np.abs(np.einsum('ki,ki->k', a, np.cross(b, c))) / 6.0


def _sample_simplex(rng, vertices: np.ndarray, n_samples: int) -> np.ndarray:
    """``n_samples`` points drawn uniformly inside a tetrahedron ``(4, 3)``."""
    if n_samples <= 0:
        return np.empty((0, 3))
    u = rng.random((n_samples, 3))
    u.sort(axis=1)
    bary = np.column_stack(
        [u[:, 0], u[:, 1] - u[:, 0], u[:, 2] - u[:, 1], 1.0 - u[:, 2]]
    )
    return bary @ vertices


def _empty_fraction(points: np.ndarray, centers: np.ndarray, radii: np.ndarray) -> float:
    """Fraction of ``points`` lying outside *every* ball."""
    if centers.shape[0] == 0:
        return 1.0
    squared = np.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2)
    inside_any = np.any(squared <= radii[None, :] ** 2, axis=1)
    return float(np.mean(~inside_any))


def _mc_result(total: float, fraction: float, n_samples: int) -> PreciseVolumeResult:
    volume = total * fraction
    std_err = total * np.sqrt(max(fraction * (1.0 - fraction), 0.0) / max(n_samples, 1))
    return PreciseVolumeResult(volume, 2.0 * std_err)


def tetrahedron_empty_volume(
    vertices,
    atom_positions,
    atom_radii,
    *,
    n_samples: int = 20000,
    seed: int = 0,
) -> PreciseVolumeResult:
    """Empty volume inside one tetrahedron by seeded Monte Carlo.

    ``atom_positions`` / ``atom_radii`` must include the four vertex atoms *and*
    any non-local intruders. ``error`` is ~2 standard errors (≈95% CI
    half-width); a fixed ``seed`` makes the result reproducible.
    """
    vertices = np.asarray(vertices, dtype=float)
    centers = np.asarray(atom_positions, dtype=float).reshape(-1, 3)
    radii = np.asarray(atom_radii, dtype=float).reshape(-1)
    total = float(_cell_volumes(vertices[None])[0])
    if total <= 0.0:
        return PreciseVolumeResult(0.0, 0.0)
    rng = np.random.default_rng(seed)
    points = _sample_simplex(rng, vertices, n_samples)
    return _mc_result(total, _empty_fraction(points, centers, radii), n_samples)


def region_empty_volume(
    tetrahedra,
    atom_positions,
    atom_radii,
    *,
    n_samples: int = 40000,
    seed: int = 0,
) -> PreciseVolumeResult:
    """Empty volume of a union of tetrahedra ``(K, 4, 3)`` by seeded Monte Carlo.

    Samples are spread across the tetrahedra in proportion to their volume (so
    the estimate is uniform over the region) and tested against every ball. This
    is the component-level aggregation (e.g. resident, or resident+transit).
    """
    tetrahedra = np.asarray(tetrahedra, dtype=float).reshape(-1, 4, 3)
    centers = np.asarray(atom_positions, dtype=float).reshape(-1, 3)
    radii = np.asarray(atom_radii, dtype=float).reshape(-1)
    volumes = _cell_volumes(tetrahedra)
    total = float(volumes.sum())
    if total <= 0.0:
        return PreciseVolumeResult(0.0, 0.0)
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(n_samples, volumes / total)
    chunks = [
        _sample_simplex(rng, tetrahedra[k], int(counts[k]))
        for k in np.nonzero(counts)[0]
    ]
    points = np.concatenate(chunks) if chunks else np.empty((0, 3))
    return _mc_result(total, _empty_fraction(points, centers, radii), n_samples)


# --- Voxel occupancy grid (the 3D shape of the empty space) ------------------
#
# A different output from the scalar volume: a boolean grid marking the empty
# voxels of a region (centre inside some region tetrahedron AND outside every
# ball). It gives the *shape* of the void -- for visualization, marching-cubes
# surfaces, diffusion, or shape descriptors -- and its voxel count is an
# independent (discretization-limited) cross-check of the Monte Carlo volume.

OccupancyGridResult = namedtuple(
    'OccupancyGridResult', ['volume', 'grid', 'origin', 'spacing']
)


def _points_in_tetra(points: np.ndarray, tet: np.ndarray) -> np.ndarray:
    """Boolean mask of which ``points`` (N, 3) lie inside tetrahedron ``tet``."""
    basis = np.stack([tet[0] - tet[3], tet[1] - tet[3], tet[2] - tet[3]], axis=1)
    try:
        inverse = np.linalg.inv(basis)
    except np.linalg.LinAlgError:
        return np.zeros(points.shape[0], dtype=bool)
    bary = (points - tet[3]) @ inverse.T  # first three barycentric coordinates
    last = 1.0 - bary.sum(axis=1)
    return np.all(bary >= -1e-9, axis=1) & (last >= -1e-9)


def region_occupancy_grid(
    tetrahedra,
    atom_positions,
    atom_radii,
    *,
    spacing: float = 0.05,
) -> OccupancyGridResult:
    """Voxel occupancy grid of the empty space of a union of tetrahedra.

    A voxel is empty iff its centre lies inside some region tetrahedron *and*
    outside every ball. Returns the empty ``volume`` (voxel count x voxel volume),
    the boolean ``grid`` (the shape), the world-space ``origin`` of voxel (0,0,0),
    and the ``spacing``. ``spacing`` is in the same length unit as the
    coordinates (nm internally).
    """
    tetrahedra = np.asarray(tetrahedra, dtype=float).reshape(-1, 4, 3)
    centers = np.asarray(atom_positions, dtype=float).reshape(-1, 3)
    radii = np.asarray(atom_radii, dtype=float).reshape(-1)
    points = tetrahedra.reshape(-1, 3)
    origin = points.min(axis=0)
    dims = np.ceil((points.max(axis=0) - origin) / spacing).astype(int) + 1

    in_region = np.zeros(tuple(int(d) for d in dims), dtype=bool)
    for tet in tetrahedra:
        low = np.maximum(np.floor((tet.min(axis=0) - origin) / spacing).astype(int), 0)
        high = np.minimum(
            np.ceil((tet.max(axis=0) - origin) / spacing).astype(int), dims - 1
        )
        if np.any(high < low):
            continue
        grids = np.meshgrid(
            np.arange(low[0], high[0] + 1),
            np.arange(low[1], high[1] + 1),
            np.arange(low[2], high[2] + 1),
            indexing='ij',
        )
        index = np.stack(grids, axis=-1)  # (..., 3) voxel indices
        voxel_centers = origin + (index + 0.5) * spacing
        inside = _points_in_tetra(voxel_centers.reshape(-1, 3), tet)
        block = in_region[low[0] : high[0] + 1, low[1] : high[1] + 1, low[2] : high[2] + 1]
        in_region[low[0] : high[0] + 1, low[1] : high[1] + 1, low[2] : high[2] + 1] = (
            block | inside.reshape(block.shape)
        )

    index = np.argwhere(in_region)
    grid = np.zeros_like(in_region)
    if index.size:
        voxel_centers = origin + (index + 0.5) * spacing
        if centers.shape[0]:
            squared = np.sum(
                (voxel_centers[:, None, :] - centers[None, :, :]) ** 2, axis=2
            )
            inside_ball = np.any(squared <= radii[None, :] ** 2, axis=1)
        else:
            inside_ball = np.zeros(index.shape[0], dtype=bool)
        kept = index[~inside_ball]
        grid[kept[:, 0], kept[:, 1], kept[:, 2]] = True

    volume = float(grid.sum()) * spacing**3
    return OccupancyGridResult(volume, grid, origin, float(spacing))


# --- Deterministic slice quadrature (step 1 of the exact route) --------------
#
# vol(ball ∩ tetrahedron) by integrating exact 2D cross-sections along z:
# at height z the tetrahedron cross-section is a convex polygon and the ball
# cross-section is a disk; their intersection area is computed in closed form,
# then integrated with Gauss-Legendre in z. Deterministic and exact in the
# cross-section; the only error is the 1D quadrature. The building block of the
# overlapping-union exact volume (ARVO-class) -- see metrics_contract.md.


def _disk_polygon_area(polygon: np.ndarray, radius: float) -> float:
    """Area of (disk of ``radius`` centred at the origin) ∩ convex polygon (CCW)."""
    if radius <= 0.0 or polygon.shape[0] < 3:
        return 0.0
    r2 = radius * radius
    total = 0.0
    n = polygon.shape[0]
    for i in range(n):
        total += _edge_term(polygon[i], polygon[(i + 1) % n], radius, r2)
    return abs(total)


def _edge_term(a: np.ndarray, b: np.ndarray, radius: float, r2: float) -> float:
    """Signed area contribution of directed edge ``a -> b`` (origin-centred disk)."""
    da2 = float(a @ a)
    db2 = float(b @ b)
    a_in = da2 <= r2
    b_in = b @ b <= r2
    if a_in and b_in:
        return 0.5 * float(a[0] * b[1] - a[1] * b[0])
    # segment-circle intersections (parametric t in [0,1])
    d = b - a
    A = float(d @ d)
    B = 2.0 * float(a @ d)
    C = da2 - r2
    disc = B * B - 4.0 * A * C
    hits = []
    if A > 0.0 and disc > 0.0:
        sq = np.sqrt(disc)
        for t in ((-B - sq) / (2 * A), (-B + sq) / (2 * A)):
            if 0.0 <= t <= 1.0:
                hits.append(a + t * d)

    def sector(u, v):
        ang = np.arctan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
        return 0.5 * r2 * float(ang)

    def tri(u, v):
        return 0.5 * float(u[0] * v[1] - u[1] * v[0])

    if not a_in and not b_in:
        if len(hits) < 2:
            return sector(a, b)
        p, q = hits[0], hits[1]
        return sector(a, p) + tri(p, q) + sector(q, b)
    if a_in and not b_in:
        p = hits[0] if hits else b
        return tri(a, p) + sector(p, b)
    p = hits[-1] if hits else a
    return sector(a, p) + tri(p, b)


def _tet_plane_polygon(tet: np.ndarray, z: float) -> np.ndarray:
    """Convex cross-section polygon (in xy) of ``tet`` cut by the plane Z=``z``."""
    edges = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    points = []
    for i, j in edges:
        zi, zj = tet[i, 2], tet[j, 2]
        if (zi - z) * (zj - z) < 0.0:
            s = (z - zi) / (zj - zi)
            points.append((tet[i] + s * (tet[j] - tet[i]))[:2])
    if len(points) < 3:
        return np.empty((0, 2))
    points = np.array(points)
    centroid = points.mean(axis=0)
    order = np.argsort(np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0]))
    return points[order]


def ball_tetrahedron_volume(
    vertices, center, radius, *, n_quad: int = 24
) -> float:
    """Deterministic ``vol(ball ∩ tetrahedron)`` by exact-slice Gauss quadrature.

    The z-range is split at every breakpoint where the integrand loses smoothness
    -- the tetrahedron vertex heights (cross-section topology changes) and
    ``center_z ± radius`` (the disk appears/vanishes) -- and Gauss-Legendre is
    applied within each smooth sub-interval.
    """
    vertices = np.asarray(vertices, dtype=float)
    center = np.asarray(center, dtype=float).reshape(3)
    radius = float(radius)
    z_low = max(float(vertices[:, 2].min()), center[2] - radius)
    z_high = min(float(vertices[:, 2].max()), center[2] + radius)
    if z_high <= z_low:
        return 0.0
    breaks = {z_low, z_high}
    for value in (*vertices[:, 2], center[2] - radius, center[2] + radius):
        if z_low < value < z_high:
            breaks.add(float(value))
    knots = sorted(breaks)

    nodes, weights = np.polynomial.legendre.leggauss(n_quad)
    r2 = radius * radius
    total = 0.0
    for lower, upper in zip(knots[:-1], knots[1:], strict=True):
        half = 0.5 * (upper - lower)
        mid = 0.5 * (upper + lower)
        for node, weight in zip(nodes, weights, strict=True):
            z = mid + half * node
            polygon = _tet_plane_polygon(vertices, z)
            if polygon.shape[0] < 3:
                continue
            disk_r = np.sqrt(max(r2 - (z - center[2]) ** 2, 0.0))
            total += weight * half * _disk_polygon_area(polygon - center[:2], disk_r)
    return float(total)


# --- Deterministic exact empty volume with overlap, via nested quadrature ----
#
# vol(tet \ union(balls)) by integrating the empty length along x over a (z, y)
# Gauss grid: at each (z, y) the tetrahedron gives an x-span and each ball gives
# an x-interval; the empty length is the span minus the *union* of those
# intervals (a trivial 1D merge -- so overlap and non-local intruders are handled
# natively, with no 2D circle geometry). Deterministic; the only error is the 2D
# quadrature, controlled by breakpoint splitting + Gauss order. This is the
# overlapping-union exact route (the ARVO-class goal) reduced to 1D primitives.


# The hot loop is a numba kernel (lazy-compiled, cached) with a pure-Python
# fallback when numba is absent. Written in njit-compatible style: scalar loops,
# preallocated arrays, no Python lists in the inner loop.

_TET_EDGES = np.array([[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]])


@lazy_njit(cache=True)
def _njit_cross_section(tet, z, poly):
    """Fill ``poly`` (>=4, 2) with the ordered Z=z cross-section; return its size."""
    pts = np.empty((4, 2))
    count = 0
    for e in range(6):
        i = _TET_EDGES[e, 0]
        j = _TET_EDGES[e, 1]
        zi = tet[i, 2]
        zj = tet[j, 2]
        if (zi - z) * (zj - z) < 0.0:
            s = (z - zi) / (zj - zi)
            pts[count, 0] = tet[i, 0] + s * (tet[j, 0] - tet[i, 0])
            pts[count, 1] = tet[i, 1] + s * (tet[j, 1] - tet[i, 1])
            count += 1
    if count < 3:
        return 0
    cx = 0.0
    cy = 0.0
    for k in range(count):
        cx += pts[k, 0]
        cy += pts[k, 1]
    cx /= count
    cy /= count
    angle = np.empty(count)
    for k in range(count):
        angle[k] = np.arctan2(pts[k, 1] - cy, pts[k, 0] - cx)
    order = np.argsort(angle)
    for k in range(count):
        poly[k, 0] = pts[order[k], 0]
        poly[k, 1] = pts[order[k], 1]
    return count


@lazy_njit(cache=True)
def _njit_hspan(poly, npoly, y):
    """``(found, x_lo, x_hi)`` for the line Y=y across the convex polygon."""
    x_min = 1.0e300
    x_max = -1.0e300
    found = 0
    for k in range(npoly):
        ay = poly[k, 1]
        by = poly[(k + 1) % npoly, 1]
        if (ay - y) * (by - y) <= 0.0 and ay != by:
            ax = poly[k, 0]
            bx = poly[(k + 1) % npoly, 0]
            s = (y - ay) / (by - ay)
            x = ax + s * (bx - ax)
            if x < x_min:
                x_min = x
            if x > x_max:
                x_max = x
            found += 1
    return found, x_min, x_max


@lazy_njit(cache=True)
def _njit_covered(lo, hi, n, x_lo, x_hi):
    """Length of the union of the first ``n`` intervals clipped to [x_lo, x_hi].

    Sorts the (small) interval set in place with insertion sort and merges in one
    pass -- no allocation and no general sort, the inner-loop hot spot.
    """
    if n == 0:
        return 0.0
    # insertion sort the first n intervals by lower bound, in place
    for i in range(1, n):
        key_lo = lo[i]
        key_hi = hi[i]
        j = i - 1
        while j >= 0 and lo[j] > key_lo:
            lo[j + 1] = lo[j]
            hi[j + 1] = hi[j]
            j -= 1
        lo[j + 1] = key_lo
        hi[j + 1] = key_hi
    total = 0.0
    cur_lo = 0.0
    cur_hi = 0.0
    has = False
    for i in range(n):
        a = lo[i]
        b = hi[i]
        if a < x_lo:
            a = x_lo
        if b > x_hi:
            b = x_hi
        if b <= a:
            continue
        if not has:
            cur_lo = a
            cur_hi = b
            has = True
        elif a > cur_hi:
            total += cur_hi - cur_lo
            cur_lo = a
            cur_hi = b
        elif b > cur_hi:
            cur_hi = b
    if has:
        total += cur_hi - cur_lo
    return total


@lazy_njit(cache=True)
def _njit_slice_area(poly, npoly, centers, radii, z, nodes, weights):
    """Empty area of the cross-section at height ``z`` (y-integration).

    The disks that the plane Z=z actually cuts are computed once here (their
    centres and radii), so the inner y-loop iterates only the active disks and
    never recomputes the z-dependent disk radius.
    """
    m_atoms = centers.shape[0]
    n_quad = nodes.shape[0]
    y_low = poly[0, 1]
    y_high = poly[0, 1]
    for k in range(1, npoly):
        if poly[k, 1] < y_low:
            y_low = poly[k, 1]
        if poly[k, 1] > y_high:
            y_high = poly[k, 1]
    if y_high <= y_low:
        return 0.0
    # active disks at this z (centre x/y and disk radius), computed once
    active_cx = np.empty(m_atoms + 1)
    active_cy = np.empty(m_atoms + 1)
    active_r = np.empty(m_atoms + 1)
    n_active = 0
    for i in range(m_atoms):
        dr2 = radii[i] * radii[i] - (z - centers[i, 2]) ** 2
        if dr2 > 0.0:
            active_cx[n_active] = centers[i, 0]
            active_cy[n_active] = centers[i, 1]
            active_r[n_active] = np.sqrt(dr2)
            n_active += 1
    knots = np.empty(npoly + 2 * n_active + 2)
    nk = 0
    knots[nk] = y_low
    nk += 1
    knots[nk] = y_high
    nk += 1
    for k in range(npoly):
        v = poly[k, 1]
        if y_low < v < y_high:
            knots[nk] = v
            nk += 1
    for i in range(n_active):
        v1 = active_cy[i] - active_r[i]
        v2 = active_cy[i] + active_r[i]
        if y_low < v1 < y_high:
            knots[nk] = v1
            nk += 1
        if y_low < v2 < y_high:
            knots[nk] = v2
            nk += 1
    knots = np.sort(knots[:nk])
    interval_lo = np.empty(n_active + 1)
    interval_hi = np.empty(n_active + 1)
    area = 0.0
    for s in range(nk - 1):
        y_lower = knots[s]
        y_upper = knots[s + 1]
        if y_upper <= y_lower:
            continue
        half = 0.5 * (y_upper - y_lower)
        mid = 0.5 * (y_upper + y_lower)
        for g in range(n_quad):
            y = mid + half * nodes[g]
            found, x_lo, x_hi = _njit_hspan(poly, npoly, y)
            if found < 2:
                continue
            ni = 0
            for i in range(n_active):
                w2 = active_r[i] * active_r[i] - (y - active_cy[i]) ** 2
                if w2 <= 0.0:
                    continue
                hw = np.sqrt(w2)
                interval_lo[ni] = active_cx[i] - hw
                interval_hi[ni] = active_cx[i] + hw
                ni += 1
            covered = _njit_covered(interval_lo, interval_hi, ni, x_lo, x_hi)
            area += weights[g] * half * ((x_hi - x_lo) - covered)
    return area


@lazy_njit(cache=True)
def _njit_tet_exact(tet, centers, radii, nodes, weights):
    """``vol(tet \\ union(balls))`` by breakpoint-split nested (z, y) quadrature."""
    m_atoms = centers.shape[0]
    n_quad = nodes.shape[0]
    z_low = tet[0, 2]
    z_high = tet[0, 2]
    for i in range(1, 4):
        if tet[i, 2] < z_low:
            z_low = tet[i, 2]
        if tet[i, 2] > z_high:
            z_high = tet[i, 2]
    if z_high <= z_low:
        return 0.0
    knots = np.empty(4 + 2 * m_atoms + 2)
    nk = 0
    knots[nk] = z_low
    nk += 1
    knots[nk] = z_high
    nk += 1
    for i in range(4):
        v = tet[i, 2]
        if z_low < v < z_high:
            knots[nk] = v
            nk += 1
    for i in range(m_atoms):
        v1 = centers[i, 2] - radii[i]
        v2 = centers[i, 2] + radii[i]
        if z_low < v1 < z_high:
            knots[nk] = v1
            nk += 1
        if z_low < v2 < z_high:
            knots[nk] = v2
            nk += 1
    knots = np.sort(knots[:nk])
    poly = np.empty((4, 2))
    total = 0.0
    for s in range(nk - 1):
        z_lower = knots[s]
        z_upper = knots[s + 1]
        if z_upper <= z_lower:
            continue
        half = 0.5 * (z_upper - z_lower)
        mid = 0.5 * (z_upper + z_lower)
        for g in range(n_quad):
            z = mid + half * nodes[g]
            npoly = _njit_cross_section(tet, z, poly)
            if npoly < 3:
                continue
            area = _njit_slice_area(poly, npoly, centers, radii, z, nodes, weights)
            total += weights[g] * half * area
    return total


def tetrahedron_empty_volume_exact(
    vertices, atom_positions, atom_radii, *, n_quad: int = 24
) -> float:
    """Deterministic ``vol(tet \\ union(balls))`` by nested (z, y) quadrature.

    ``atom_positions`` / ``atom_radii`` include the four vertex atoms and any
    non-local intruders. Overlap is handled exactly by the 1D interval union.
    The hot loop is numba-accelerated (``_njit_tet_exact``) when numba is present.
    """
    tet = np.ascontiguousarray(np.asarray(vertices, dtype=np.float64))
    centers = np.ascontiguousarray(np.asarray(atom_positions, dtype=np.float64).reshape(-1, 3))
    radii = np.ascontiguousarray(np.asarray(atom_radii, dtype=np.float64).reshape(-1))
    nodes, weights = np.polynomial.legendre.leggauss(n_quad)
    return float(_njit_tet_exact(tet, centers, radii, nodes, weights))


def region_empty_volume_exact(
    tetrahedra, atom_positions, atom_radii, *, n_quad: int = 24
) -> float:
    """Deterministic exact empty volume of a union of tetrahedra (sum per tet).

    Each tetrahedron is evaluated against only the balls that can reach it (those
    whose ball intersects its bounding box) -- a ball that does not reach the tet
    contributes nothing, so this pruning is exact and avoids testing every sample
    line against every atom in the component.
    """
    tetrahedra = np.asarray(tetrahedra, dtype=float).reshape(-1, 4, 3)
    centers = np.asarray(atom_positions, dtype=float).reshape(-1, 3)
    radii = np.asarray(atom_radii, dtype=float).reshape(-1)
    total = 0.0
    for tet in tetrahedra:
        low = tet.min(axis=0)
        high = tet.max(axis=0)
        clamped = np.clip(centers, low, high)
        reaches = np.sum((centers - clamped) ** 2, axis=1) <= radii**2
        total += tetrahedron_empty_volume_exact(
            tet, centers[reaches], radii[reaches], n_quad=n_quad
        )
    return float(total)
