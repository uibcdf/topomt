"""VOLBL metric primitives for the native CASTp 1.0 path."""

from dataclasses import dataclass
from functools import lru_cache
from math import acos, asin, fabs, pi, sqrt
from typing import Callable

import numpy as np


EPSILON = 1.0e-5
_FACE_RANK_MAP_CACHE_LIMIT = 16
_FACE_RANK_MAP_CACHE: dict[
    int,
    tuple[object, dict[tuple[int, int, int], tuple[int, int, int]]],
] = {}


@dataclass(frozen=True)
class Shell:
    """Molecular-surface shell contribution for one accessible area patch."""

    area: float
    volume: float


@dataclass(frozen=True)
class Torus:
    """VOLBL torus contribution split across the two incident atoms."""

    area_1: float
    area_2: float
    volume_1: float
    volume_2: float
    volume_mod_1: float
    volume_mod_2: float


@dataclass(frozen=True)
class Patch:
    """VOLBL solvent patch contribution split across three incident atoms."""

    area_1: float
    area_2: float
    area_3: float
    area: float
    volume_1: float
    volume_2: float
    volume_3: float
    volume: float


@dataclass(frozen=True)
class SpaceFillingMeasurements:
    """Global VOLBL space-filling measurements."""

    volume_sa: float
    volume_ms: float
    area_sa: float
    area_ms: float
    length: float
    corners: int


@dataclass(frozen=True)
class VoidMeasurement:
    """VOLBL measurements for one topological void."""

    simplex_indices: tuple[int, ...]
    initial_volume: float
    volume_sa: float
    volume_ms: float
    area_sa: float
    area_ms: float
    length: float
    corners: int


@dataclass(frozen=True)
class VoidMeasurements:
    """Global and per-void VOLBL void measurements."""

    total_volume_sa: float
    total_volume_ms: float
    total_area_sa: float
    total_area_ms: float
    total_length: float
    total_corners: int
    voids: tuple[VoidMeasurement, ...]


@dataclass(frozen=True)
class EnvelopeMeasurements:
    """VOLBL envelope measurements assembled from voids, fringe, and shape."""

    voids: VoidMeasurements
    fringe: SpaceFillingMeasurements
    shape_volume: float
    shape_volume_ms: float


@dataclass(frozen=True)
class VolblMeasurements:
    """Complete global VOLBL measurements sharing one metric context."""

    space_filling: SpaceFillingMeasurements
    voids: VoidMeasurements
    fringe: SpaceFillingMeasurements
    shape_volume: float
    shape_volume_ms: float


def _clamp(value: float, lower: float, upper: float) -> float:
    return min(max(float(value), float(lower)), float(upper))


class VolblMetricContext:
    """Port of the geometric primitives in CASTp 1.0 `volbl/metric.c`."""

    def __init__(
        self,
        coordinates,
        radii,
        weights=None,
        solvent_radius: float = 1.4,
        alpha: float = 0.0,
        hidden0: Callable[[int, int], bool] | None = None,
        hidden1: Callable[[int, int, int], bool] | None = None,
        ccw: Callable[[int, int, int, int], bool] | None = None,
    ) -> None:
        self.coordinates = np.asarray(coordinates, dtype=float)
        self.radii = np.asarray(radii, dtype=float)
        if weights is None:
            weights = self.radii
        self.weights = np.asarray(weights, dtype=float)
        self.solvent_radius = float(solvent_radius)
        self.alpha = float(alpha)
        self.hidden0 = hidden0 or (lambda _i, _j: False)
        self.hidden1 = hidden1 or (lambda _i, _j, _k: False)
        self.ccw = ccw or (lambda _i, _j, _k, _l: True)

    def vector(self, i: int) -> np.ndarray:
        return self.coordinates[int(i)]

    @lru_cache(maxsize=None)
    def ball_radius(self, i: int) -> float:
        r2 = float(np.sign(self.weights[int(i)]) * self.weights[int(i)] ** 2)
        r2 += float(np.sign(self.alpha) * self.alpha**2)
        return sqrt(max(r2, 0.0))

    @lru_cache(maxsize=None)
    def ball_area(self, i: int) -> float:
        radius = float(self.radii[int(i)])
        return 4.0 * pi * radius * radius

    @lru_cache(maxsize=None)
    def ball_volume(self, i: int) -> float:
        return (1.0 / 3.0) * float(self.radii[int(i)]) * self.ball_area(i)

    @lru_cache(maxsize=None)
    def tetrahedron_volume(self, i: int, j: int, k: int, l: int) -> float:
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        v = self.vector(l)
        ax, ay, az = float(t[0] - s[0]), float(t[1] - s[1]), float(t[2] - s[2])
        bx, by, bz = float(u[0] - s[0]), float(u[1] - s[1]), float(u[2] - s[2])
        cx, cy, cz = float(v[0] - s[0]), float(v[1] - s[1]), float(v[2] - s[2])
        determinant = (
            ax * (by * cz - bz * cy)
            - ay * (bx * cz - bz * cx)
            + az * (bx * cy - by * cx)
        )
        return fabs(determinant / 6.0)

    def distance(self, i, j) -> float:
        dx = float(i[0]) - float(j[0])
        dy = float(i[1]) - float(j[1])
        dz = float(i[2]) - float(j[2])
        return sqrt(dx * dx + dy * dy + dz * dz)

    @lru_cache(maxsize=None)
    def center2(self, i: int, j: int) -> np.ndarray:
        s = self.vector(i)
        t = self.vector(j)
        delta = s - t
        aux = float(np.dot(delta, delta))
        i4 = float(np.sign(self.weights[int(i)]) * self.weights[int(i)] ** 2)
        j4 = float(np.sign(self.weights[int(j)]) * self.weights[int(j)] ** 2)
        lambda_i = 0.5 - ((i4 - j4) / (2.0 * aux))
        return lambda_i * s + (1.0 - lambda_i) * t

    @lru_cache(maxsize=None)
    def center3(self, i: int, j: int, k: int) -> np.ndarray:
        i0 = self._lift0(i)
        j0 = self._lift0(j)
        k0 = self._lift0(k)
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        x0, y0, z0 = float(s[0]), float(s[1]), float(s[2])
        x1, y1, z1 = float(t[0]), float(t[1]), float(t[2])
        x2, y2, z2 = float(u[0]), float(u[1]), float(u[2])

        a1 = self._det3(y0, z0, 1.0, y1, z1, 1.0, y2, z2, 1.0)
        a2 = self._det3(z0, x0, 1.0, z1, x1, 1.0, z2, x2, 1.0)
        a3 = self._det3(x0, y0, 1.0, x1, y1, 1.0, x2, y2, 1.0)
        a4 = self._det3(x0, y0, z0, x1, y1, z1, x2, y2, z2)

        d0 = self._det4(
            x0, y0, z0, 1.0,
            x1, y1, z1, 1.0,
            x2, y2, z2, 1.0,
            a1, a2, a3, 0.0,
        )
        dx = self._det4(
            -i0, y0, z0, 1.0,
            -j0, y1, z1, 1.0,
            -k0, y2, z2, 1.0,
            a4, a2, a3, 0.0,
        )
        dy = self._det4(
            x0, -i0, z0, 1.0,
            x1, -j0, z1, 1.0,
            x2, -k0, z2, 1.0,
            a1, a4, a3, 0.0,
        )
        dz = self._det4(
            x0, y0, -i0, 1.0,
            x1, y1, -j0, 1.0,
            x2, y2, -k0, 1.0,
            a1, a2, a4, 0.0,
        )
        return np.asarray([dx / d0, dy / d0, dz / d0], dtype=float)

    @lru_cache(maxsize=None)
    def center4(self, i: int, j: int, k: int, l: int) -> np.ndarray:
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        v = self.vector(l)
        x0, y0, z0 = float(s[0]), float(s[1]), float(s[2])
        x1, y1, z1 = float(t[0]), float(t[1]), float(t[2])
        x2, y2, z2 = float(u[0]), float(u[1]), float(u[2])
        x3, y3, z3 = float(v[0]), float(v[1]), float(v[2])
        i0 = self._lift0(i)
        j0 = self._lift0(j)
        k0 = self._lift0(k)
        l0 = self._lift0(l)

        d0 = self._det4(
            x0, y0, z0, 1.0,
            x1, y1, z1, 1.0,
            x2, y2, z2, 1.0,
            x3, y3, z3, 1.0,
        )
        dx = self._det4(
            -i0, y0, z0, 1.0,
            -j0, y1, z1, 1.0,
            -k0, y2, z2, 1.0,
            -l0, y3, z3, 1.0,
        )
        dy = self._det4(
            x0, -i0, z0, 1.0,
            x1, -j0, z1, 1.0,
            x2, -k0, z2, 1.0,
            x3, -l0, z3, 1.0,
        )
        dz = self._det4(
            x0, y0, -i0, 1.0,
            x1, y1, -j0, 1.0,
            x2, y2, -k0, 1.0,
            x3, y3, -l0, 1.0,
        )
        return np.asarray(
            [
                dx / d0,
                dy / d0,
                dz / d0,
            ],
            dtype=float,
        )

    @lru_cache(maxsize=None)
    def triangle_dual(self, i: int, j: int, k: int) -> np.ndarray:
        center = self.center3(i, j, k)
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        tsx, tsy, tsz = float(t[0] - s[0]), float(t[1] - s[1]), float(t[2] - s[2])
        usx, usy, usz = float(u[0] - s[0]), float(u[1] - s[1]), float(u[2] - s[2])
        nx = tsy * usz - tsz * usy
        ny = tsz * usx - tsx * usz
        nz = tsx * usy - tsy * usx
        dx = float(center[0] - s[0])
        dy = float(center[1] - s[1])
        dz = float(center[2] - s[2])
        s1 = dx * nx + dy * ny + dz * nz
        s2 = nx * nx + ny * ny + nz * nz
        s3 = dx * dx + dy * dy + dz * dz
        radius = float(self.radii[int(i)])
        aux = s1 * s1 - s3 * s2 + radius * radius * s2
        xi = (-s1 + sqrt(max(aux, 0.0))) / s2
        return np.asarray(
            [
                float(center[0]) + xi * nx,
                float(center[1]) + xi * ny,
                float(center[2]) + xi * nz,
            ],
            dtype=float,
        )

    @lru_cache(maxsize=None)
    def cap_height(self, i: int, j: int) -> float:
        center = self.center2(i, j)
        radius = float(self.radii[int(i)])
        distance = self.distance(self.vector(i), center)
        if self.hidden0(int(i), int(j)):
            return radius + distance
        return radius - distance

    @lru_cache(maxsize=None)
    def cap_area(self, i: int, j: int) -> float:
        return 2.0 * pi * float(self.radii[int(i)]) * self.cap_height(i, j)

    @lru_cache(maxsize=None)
    def disk_radius(self, i: int, j: int) -> float:
        height = self.cap_height(i, j)
        radius = float(self.radii[int(i)])
        return sqrt(max(height * (2.0 * radius - height), 0.0))

    @lru_cache(maxsize=None)
    def disk_length(self, i: int, j: int) -> float:
        return 2.0 * pi * self.disk_radius(i, j)

    @lru_cache(maxsize=None)
    def disk_area(self, i: int, j: int) -> float:
        return 0.5 * self.disk_radius(i, j) * self.disk_length(i, j)

    @lru_cache(maxsize=None)
    def segment_height(self, i: int, j: int, k: int) -> float:
        center3 = self.center3(i, j, k)
        center2 = self.center2(i, j)
        disk_radius = self.disk_radius(i, j)
        distance = self.distance(center2, center3)
        if self.hidden1(int(i), int(j), int(k)):
            return min(disk_radius + distance, 2.0 * disk_radius)
        return max(disk_radius - distance, 0.0)

    @lru_cache(maxsize=None)
    def segment_angle(self, i: int, j: int, k: int) -> float:
        pjk = self.triangle_dual(i, j, k)
        pkj = self.triangle_dual(i, k, j)
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        return self.angle_dihedral(s, t, u, pjk) + self.angle_dihedral(s, t, u, pkj)

    @lru_cache(maxsize=None)
    def segment_length(self, i: int, j: int, k: int) -> float:
        return self.segment_angle(i, j, k) * self.disk_length(i, j)

    @lru_cache(maxsize=None)
    def segment_area(self, i: int, j: int, k: int) -> float:
        pjk = self.triangle_dual(i, j, k)
        pkj = self.triangle_dual(i, k, j)
        sector = 0.5 * self.disk_radius(i, j) * self.segment_length(i, j, k)
        height = self.disk_radius(i, j) - self.segment_height(i, j, k)
        triangle = 0.5 * height * self.distance(pjk, pkj)
        return sector - triangle

    @lru_cache(maxsize=None)
    def segment2_angle(self, i: int, j: int, k: int, l: int) -> float:
        pjl = self.triangle_dual(i, j, l)
        pkj = self.triangle_dual(i, k, j)
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        v = self.vector(l)
        return (
            self.angle_dihedral(s, t, u, pkj)
            + self.angle_dihedral(s, t, v, pjl)
            - self.angle_dihedral(s, t, u, v)
        )

    @lru_cache(maxsize=None)
    def segment2_length(self, i: int, j: int, k: int, l: int) -> float:
        return self.segment2_angle(i, j, k, l) * self.disk_length(i, j)

    @lru_cache(maxsize=None)
    def segment2_area(self, i: int, j: int, k: int, l: int) -> float:
        if not self.ccw(int(i), int(j), int(k), int(l)):
            k, l = l, k
        pjl = self.triangle_dual(i, j, l)
        pkj = self.triangle_dual(i, k, j)
        center = self.center4(i, j, k, l)
        h_k = self.segment_height(i, j, k)
        h_l = self.segment_height(i, j, l)
        radius = self.disk_radius(i, j)
        sector = 0.5 * radius * self.segment2_length(i, j, k, l)
        tri_k = 0.5 * (radius - h_k) * self.distance(pkj, center)
        tri_l = 0.5 * (radius - h_l) * self.distance(pjl, center)
        return sector - tri_k - tri_l

    @lru_cache(maxsize=None)
    def cap_volume(self, i: int, j: int) -> float:
        radius = float(self.radii[int(i)])
        sector = (1.0 / 3.0) * radius * self.cap_area(i, j)
        cone = (1.0 / 3.0) * (radius - self.cap_height(i, j)) * self.disk_area(i, j)
        return sector - cone

    @lru_cache(maxsize=None)
    def cap2_area(self, i: int, j: int, k: int) -> float:
        pjk = self.triangle_dual(i, j, k)
        pkj = self.triangle_dual(i, k, j)
        l_j = self.segment_angle(i, j, k)
        l_k = self.segment_angle(i, k, j)
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        phi_jk = 0.5 - self.angle_dihedral(s, pjk, t, u)
        phi_kj = 0.5 - self.angle_dihedral(s, pkj, u, t)
        radius = float(self.radii[int(i)])
        sphere = 0.5 * self.ball_area(i) * (phi_jk + phi_kj)
        side_j = 2.0 * pi * radius * l_j * (radius - self.cap_height(i, j))
        side_k = 2.0 * pi * radius * l_k * (radius - self.cap_height(i, k))
        return sphere - side_j - side_k

    @lru_cache(maxsize=None)
    def cap2_volume(self, i: int, j: int, k: int) -> float:
        radius = float(self.radii[int(i)])
        sector = (1.0 / 3.0) * radius * self.cap2_area(i, j, k)
        side_j = (1.0 / 3.0) * (radius - self.cap_height(i, j)) * self.segment_area(i, j, k)
        side_k = (1.0 / 3.0) * (radius - self.cap_height(i, k)) * self.segment_area(i, k, j)
        return sector - side_j - side_k

    @lru_cache(maxsize=None)
    def cap3_area(self, i: int, j: int, k: int, l: int) -> float:
        if not self.ccw(int(i), int(j), int(k), int(l)):
            k, l = l, k
        pkj = self.triangle_dual(i, k, j)
        plk = self.triangle_dual(i, l, k)
        pjl = self.triangle_dual(i, j, l)
        l_j = self.segment2_angle(i, j, k, l)
        l_k = self.segment2_angle(i, k, l, j)
        l_l = self.segment2_angle(i, l, j, k)
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        v = self.vector(l)
        phi_kj = 0.5 - self.angle_dihedral(s, pkj, u, t)
        phi_lk = 0.5 - self.angle_dihedral(s, plk, v, u)
        phi_jl = 0.5 - self.angle_dihedral(s, pjl, t, v)
        radius = float(self.radii[int(i)])
        sphere = 0.5 * self.ball_area(i) * (phi_kj + phi_lk + phi_jl - 0.5)
        side_j = 2.0 * pi * radius * l_j * (radius - self.cap_height(i, j))
        side_k = 2.0 * pi * radius * l_k * (radius - self.cap_height(i, k))
        side_l = 2.0 * pi * radius * l_l * (radius - self.cap_height(i, l))
        return sphere - side_j - side_k - side_l

    @lru_cache(maxsize=None)
    def cap3_volume(self, i: int, j: int, k: int, l: int) -> float:
        radius = float(self.radii[int(i)])
        sector = (1.0 / 3.0) * radius * self.cap3_area(i, j, k, l)
        side_j = (1.0 / 3.0) * (radius - self.cap_height(i, j)) * self.segment2_area(i, j, k, l)
        side_k = (1.0 / 3.0) * (radius - self.cap_height(i, k)) * self.segment2_area(i, k, j, l)
        side_l = (1.0 / 3.0) * (radius - self.cap_height(i, l)) * self.segment2_area(i, l, j, k)
        return sector - side_j - side_k - side_l

    @lru_cache(maxsize=None)
    def ball2_area(self, i: int, j: int) -> float:
        return self.cap_area(i, j) + self.cap_area(j, i)

    @lru_cache(maxsize=None)
    def ball2_length(self, i: int, j: int) -> float:
        return self.disk_length(i, j)

    @lru_cache(maxsize=None)
    def ball2_volume(self, i: int, j: int) -> float:
        return self.cap_volume(i, j) + self.cap_volume(j, i)

    @lru_cache(maxsize=None)
    def ball3_area(self, i: int, j: int, k: int) -> float:
        return self.cap2_area(i, j, k) + self.cap2_area(j, i, k) + self.cap2_area(k, i, j)

    @lru_cache(maxsize=None)
    def ball3_length(self, i: int, j: int, k: int) -> float:
        return (
            self.segment_length(i, j, k)
            + self.segment_length(i, k, j)
            + self.segment_length(j, k, i)
        )

    @lru_cache(maxsize=None)
    def ball3_volume(self, i: int, j: int, k: int) -> float:
        return self.cap2_volume(i, j, k) + self.cap2_volume(j, i, k) + self.cap2_volume(k, i, j)

    @lru_cache(maxsize=None)
    def ball4_area(self, i: int, j: int, k: int, l: int) -> float:
        return (
            self.cap3_area(i, j, k, l)
            + self.cap3_area(j, i, k, l)
            + self.cap3_area(k, i, j, l)
            + self.cap3_area(l, i, j, k)
        )

    @lru_cache(maxsize=None)
    def ball4_length(self, i: int, j: int, k: int, l: int) -> float:
        return (
            self.segment2_length(i, j, k, l)
            + self.segment2_length(i, k, l, j)
            + self.segment2_length(i, l, j, k)
            + self.segment2_length(j, k, i, l)
            + self.segment2_length(j, l, k, i)
            + self.segment2_length(k, l, i, j)
        )

    @lru_cache(maxsize=None)
    def ball4_volume(self, i: int, j: int, k: int, l: int) -> float:
        return (
            self.cap3_volume(i, j, k, l)
            + self.cap3_volume(j, i, k, l)
            + self.cap3_volume(k, i, j, l)
            + self.cap3_volume(l, i, j, k)
        )

    @lru_cache(maxsize=None)
    def shell(self, i: int, area: float) -> Shell:
        radius = float(self.radii[int(i)])
        vdw_radius = radius - self.solvent_radius
        shell_area = float(area) * vdw_radius * vdw_radius / (radius * radius)
        shell_volume = (float(area) * radius - shell_area * vdw_radius) / 3.0
        return Shell(area=shell_area, volume=shell_volume)

    def angle_dihedral(self, s, t, u, v) -> float:
        sx, sy, sz = float(s[0]), float(s[1]), float(s[2])
        tx, ty, tz = float(t[0]), float(t[1]), float(t[2])
        ux, uy, uz = float(u[0]), float(u[1]), float(u[2])
        vx, vy, vz = float(v[0]), float(v[1]), float(v[2])

        usx, usy, usz = ux - sx, uy - sy, uz - sz
        utx, uty, utz = ux - tx, uy - ty, uz - tz
        vsx, vsy, vsz = vx - sx, vy - sy, vz - sz
        vtx, vty, vtz = vx - tx, vy - ty, vz - tz

        mux = usy * utz - usz * uty
        muy = usz * utx - usx * utz
        muz = usx * uty - usy * utx
        mvx = vsy * vtz - vsz * vty
        mvy = vsz * vtx - vsx * vtz
        mvz = vsx * vty - vsy * vtx

        spu = mux * mux + muy * muy + muz * muz
        spv = mvx * mvx + mvy * mvy + mvz * mvz
        aux = _clamp(
            (mux * mvx + muy * mvy + muz * mvz) / sqrt(spu * spv),
            -1.0,
            1.0,
        )
        return acos(aux) / (2.0 * pi)

    @lru_cache(maxsize=None)
    def angle_solid(self, i: int, j: int, k: int, l: int) -> float:
        s = self.vector(i)
        t = self.vector(j)
        u = self.vector(k)
        v = self.vector(l)
        phi_t = self.angle_dihedral(s, t, v, u)
        phi_u = self.angle_dihedral(s, u, t, v)
        phi_v = self.angle_dihedral(s, v, u, t)
        return 0.5 * (phi_t + phi_u + phi_v) - 0.25

    @lru_cache(maxsize=None)
    def sector_area(self, i: int, j: int, k: int, l: int) -> float:
        return self.angle_solid(i, j, k, l) * self.ball_area(i)

    @lru_cache(maxsize=None)
    def sector_volume(self, i: int, j: int, k: int, l: int) -> float:
        return self.angle_solid(i, j, k, l) * self.ball_volume(i)

    @lru_cache(maxsize=None)
    def wedge_area(self, i: int, j: int, k: int, l: int) -> float:
        return self.angle_dihedral(
            self.vector(i),
            self.vector(j),
            self.vector(k),
            self.vector(l),
        ) * self.ball2_area(i, j)

    @lru_cache(maxsize=None)
    def wedge_length(self, i: int, j: int, k: int, l: int) -> float:
        return self.angle_dihedral(
            self.vector(i),
            self.vector(j),
            self.vector(k),
            self.vector(l),
        ) * self.disk_length(i, j)

    @lru_cache(maxsize=None)
    def wedge_volume(self, i: int, j: int, k: int, l: int) -> float:
        return self.angle_dihedral(
            self.vector(i),
            self.vector(j),
            self.vector(k),
            self.vector(l),
        ) * self.ball2_volume(i, j)

    @lru_cache(maxsize=None)
    def pawn_area(self, i: int, j: int, k: int) -> float:
        return 0.5 * self.ball3_area(i, j, k)

    @lru_cache(maxsize=None)
    def pawn_length(self, i: int, j: int, k: int) -> float:
        return 0.5 * self.ball3_length(i, j, k)

    @lru_cache(maxsize=None)
    def pawn_volume(self, i: int, j: int, k: int) -> float:
        return 0.5 * self.ball3_volume(i, j, k)

    @lru_cache(maxsize=None)
    def patch(self, j: int, k: int, l: int) -> Patch:
        solvent_radius = self.solvent_radius
        solvent_area = 4.0 * pi * solvent_radius * solvent_radius
        solvent_center = self.triangle_dual(j, k, l)
        t = self.vector(j)
        u = self.vector(k)
        v = self.vector(l)
        phi_t = self.angle_dihedral(solvent_center, t, v, u)
        phi_u = self.angle_dihedral(solvent_center, u, t, v)
        phi_v = self.angle_dihedral(solvent_center, v, u, t)
        solid_angle = 0.5 * (phi_t + phi_u + phi_v) - 0.25
        area = solvent_area * solid_angle
        volume = solvent_radius * area / 3.0
        return Patch(
            area_1=area / 3.0,
            area_2=area / 3.0,
            area_3=area / 3.0,
            area=area,
            volume_1=volume / 3.0,
            volume_2=volume / 3.0,
            volume_3=volume / 3.0,
            volume=volume,
        )

    @lru_cache(maxsize=None)
    def torus(self, i: int, j: int, cusp: bool = False) -> Torus:
        solvent_radius = self.solvent_radius
        if solvent_radius == 0.0:
            return Torus(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        radius_i = float(self.radii[int(i)])
        radius_j = float(self.radii[int(j)])
        vdw_i = radius_i - solvent_radius
        vdw_j = radius_j - solvent_radius
        disk_radius = self.disk_radius(i, j)
        distance_ij = self.distance(self.vector(i), self.vector(j))
        d_i = sqrt(max(radius_i * radius_i - disk_radius * disk_radius, 0.0))
        d_j = sqrt(max(radius_j * radius_j - disk_radius * disk_radius, 0.0))

        cos_i = _clamp(disk_radius / radius_i, -1.0, 1.0)
        cos_j = _clamp(disk_radius / radius_j, -1.0, 1.0)
        sin_i = sqrt(max(1.0 - cos_i * cos_i, 0.0))
        sin_j = sqrt(max(1.0 - cos_j * cos_j, 0.0))
        angle_i = acos(cos_i)
        angle_j = acos(cos_j)
        dist_i = solvent_radius * sin_i
        dist_j = solvent_radius * sin_j

        half_ab = half_cusp_area = half_spindle = angle = sin_angle = cos_angle = 0.0
        if disk_radius < solvent_radius:
            cos_angle = _clamp(disk_radius / solvent_radius, -1.0, 1.0)
            sin_angle = sqrt(max(1.0 - cos_angle * cos_angle, 0.0))
            angle = acos(cos_angle)
            half_ab = solvent_radius * sin_angle
            half_cusp_area = 2.0 * pi * solvent_radius * (half_ab - disk_radius * angle)
            half_spindle = self.volume_spindle(
                angle,
                sin_angle,
                cos_angle,
                disk_radius,
                solvent_radius,
            )

        if disk_radius > solvent_radius:
            area_i = 2.0 * pi * solvent_radius * (disk_radius * angle_i - dist_i)
            area_j = 2.0 * pi * solvent_radius * (disk_radius * angle_j - dist_j)
            volume_i = self.volume_torus_fraction(sin_i, disk_radius, solvent_radius, angle_i)
            volume_j = self.volume_torus_fraction(sin_j, disk_radius, solvent_radius, angle_j)
        else:
            area_i = 2.0 * pi * solvent_radius * (
                disk_radius * (angle_i - angle) - (dist_i - half_ab)
            )
            area_j = 2.0 * pi * solvent_radius * (
                disk_radius * (angle_j - angle) - (dist_j - half_ab)
            )
            volume_i = self.volume_cone_frustum(
                vdw_i * cos_i,
                disk_radius,
                solvent_radius * sin_i,
            ) - self.volume_round_cone(
                angle,
                angle_i,
                sin_angle,
                sin_i,
                cos_i,
                disk_radius,
                solvent_radius,
            )
            volume_j = self.volume_cone_frustum(
                vdw_j * cos_j,
                disk_radius,
                solvent_radius * sin_j,
            ) - self.volume_round_cone(
                angle,
                angle_j,
                sin_angle,
                sin_j,
                cos_j,
                disk_radius,
                solvent_radius,
            )
            if not cusp:
                area_i += half_cusp_area
                area_j += half_cusp_area
                volume_i -= half_spindle
                volume_j -= half_spindle

        if self.hidden0(j, i) and not self.hidden0(i, j):
            return self._torus_hidden_j_by_i(
                i,
                j,
                radius_values=(vdw_i, vdw_j, d_i, d_j, distance_ij, disk_radius),
                area_values=(area_i, area_j),
                volume_values=(volume_i, volume_j),
            )
        if self.hidden0(i, j) and not self.hidden0(j, i):
            return self._torus_hidden_i_by_j(
                i,
                j,
                radius_values=(vdw_i, vdw_j, d_i, d_j, distance_ij, disk_radius),
                area_values=(area_i, area_j),
                volume_values=(volume_i, volume_j),
            )

        return self._torus_not_hidden(
            vdw_i=vdw_i,
            vdw_j=vdw_j,
            d_i=d_i,
            distance_ij=distance_ij,
            disk_radius=disk_radius,
            solvent_radius=solvent_radius,
            area_i=area_i,
            area_j=area_j,
            volume_i=volume_i,
            volume_j=volume_j,
            cusp=cusp,
            cusp_values=(angle, half_ab, half_cusp_area, half_spindle),
        )

    @staticmethod
    def volume_cone_frustum(r: float, R: float, h: float) -> float:
        return pi * (R * R + R * r + r * r) * h / 3.0

    @staticmethod
    def volume_round_cone(
        phi1: float,
        phi2: float,
        sin_phi1: float,
        sin_phi2: float,
        cos_phi2: float,
        disk_radius: float,
        solvent_radius: float,
    ) -> float:
        return pi * solvent_radius * (
            (
                disk_radius * disk_radius * sin_phi2
                - solvent_radius * disk_radius * phi2
                - solvent_radius * disk_radius * sin_phi2 * cos_phi2
                + solvent_radius * solvent_radius * (
                    sin_phi2 - sin_phi2 * sin_phi2 * sin_phi2 / 3.0
                )
            )
            - (
                -solvent_radius * disk_radius * phi1
                + solvent_radius * solvent_radius * (
                    sin_phi1 - sin_phi1 * sin_phi1 * sin_phi1 / 3.0
                )
            )
        )

    @staticmethod
    def volume_spindle(
        phi: float,
        sin_phi: float,
        cos_phi: float,
        disk_radius: float,
        solvent_radius: float,
    ) -> float:
        return pi * solvent_radius * (
            disk_radius * disk_radius * sin_phi
            - solvent_radius * disk_radius * phi
            - solvent_radius * disk_radius * sin_phi * cos_phi
            + solvent_radius * solvent_radius * (
                sin_phi - sin_phi * sin_phi * sin_phi / 3.0
            )
        )

    @staticmethod
    def volume_round_pyramid(r: float, h: float) -> float:
        return pi * r * r * h / 3.0

    @staticmethod
    def volume_torus_fraction(
        sin_phi: float,
        disk_radius: float,
        solvent_radius: float,
        angle: float,
    ) -> float:
        return pi * solvent_radius * solvent_radius * (
            disk_radius * angle - 2.0 * solvent_radius * sin_phi / 3.0
        )

    @staticmethod
    def radical_vdw(
        dist_phi: float,
        solvent_radius: float,
        disk_radius: float,
    ) -> tuple[float, float, float, float]:
        sin_phi = dist_phi / solvent_radius
        cos_phi = sqrt(1.0 - sin_phi * sin_phi)
        phi = asin(sin_phi)
        r_phi = disk_radius / cos_phi
        return r_phi, sin_phi, cos_phi, phi

    @staticmethod
    def _det3(
        a00: float,
        a01: float,
        a02: float,
        a10: float,
        a11: float,
        a12: float,
        a20: float,
        a21: float,
        a22: float,
    ) -> float:
        return (
            a00 * (a11 * a22 - a12 * a21)
            - a01 * (a10 * a22 - a12 * a20)
            + a02 * (a10 * a21 - a11 * a20)
        )

    @staticmethod
    def _det4(
        a00: float,
        a01: float,
        a02: float,
        a03: float,
        a10: float,
        a11: float,
        a12: float,
        a13: float,
        a20: float,
        a21: float,
        a22: float,
        a23: float,
        a30: float,
        a31: float,
        a32: float,
        a33: float,
    ) -> float:
        minor0 = VolblMetricContext._det3(
            a11, a12, a13,
            a21, a22, a23,
            a31, a32, a33,
        )
        minor1 = VolblMetricContext._det3(
            a10, a12, a13,
            a20, a22, a23,
            a30, a32, a33,
        )
        minor2 = VolblMetricContext._det3(
            a10, a11, a13,
            a20, a21, a23,
            a30, a31, a33,
        )
        minor3 = VolblMetricContext._det3(
            a10, a11, a12,
            a20, a21, a22,
            a30, a31, a32,
        )
        return a00 * minor0 - a01 * minor1 + a02 * minor2 - a03 * minor3

    def _lift0(self, i: int) -> float:
        point = self.vector(i)
        weight2 = float(np.sign(self.weights[int(i)]) * self.weights[int(i)] ** 2)
        return 0.5 * (weight2 - float(np.dot(point, point)))

    def _torus_hidden_j_by_i(
        self,
        i: int,
        j: int,
        radius_values,
        area_values,
        volume_values,
    ) -> Torus:
        vdw_i, vdw_j, d_i, _d_j, distance_ij, disk_radius = radius_values
        area_i, area_j = area_values
        volume_i, volume_j = volume_values
        solvent_radius = self.solvent_radius
        split = (distance_ij * distance_ij + vdw_i * vdw_i - vdw_j * vdw_j) / (
            2.0 * distance_ij
        )
        dist_phi = d_i - split
        r_phi, sin_phi, cos_phi, phi = self.radical_vdw(
            dist_phi,
            solvent_radius,
            disk_radius,
        )
        area_phi = 2.0 * pi * solvent_radius * (disk_radius * phi - dist_phi)
        volume_phi = self.volume_torus_fraction(
            sin_phi,
            disk_radius,
            solvent_radius,
            phi,
        )
        volume_mod = self.volume_cone_frustum(
            (r_phi - solvent_radius) * cos_phi,
            disk_radius,
            solvent_radius * sin_phi,
        )
        return Torus(
            area_i - area_phi,
            area_phi - area_j,
            volume_i - volume_phi,
            volume_phi - volume_j,
            -volume_mod,
            volume_mod,
        )

    def _torus_hidden_i_by_j(
        self,
        i: int,
        j: int,
        radius_values,
        area_values,
        volume_values,
    ) -> Torus:
        vdw_i, vdw_j, _d_i, d_j, distance_ij, disk_radius = radius_values
        area_i, area_j = area_values
        volume_i, volume_j = volume_values
        solvent_radius = self.solvent_radius
        split = (distance_ij * distance_ij + vdw_j * vdw_j - vdw_i * vdw_i) / (
            2.0 * distance_ij
        )
        dist_phi = d_j - split
        r_phi, sin_phi, cos_phi, phi = self.radical_vdw(
            dist_phi,
            solvent_radius,
            disk_radius,
        )
        area_phi = 2.0 * pi * solvent_radius * (disk_radius * phi - dist_phi)
        volume_phi = self.volume_torus_fraction(
            sin_phi,
            disk_radius,
            solvent_radius,
            phi,
        )
        volume_mod = self.volume_cone_frustum(
            (r_phi - solvent_radius) * cos_phi,
            disk_radius,
            solvent_radius * sin_phi,
        )
        return Torus(
            area_phi - area_i,
            area_j - area_phi,
            volume_phi - volume_i,
            volume_j - volume_phi,
            volume_mod,
            -volume_mod,
        )

    def _torus_not_hidden(
        self,
        vdw_i: float,
        vdw_j: float,
        d_i: float,
        distance_ij: float,
        disk_radius: float,
        solvent_radius: float,
        area_i: float,
        area_j: float,
        volume_i: float,
        volume_j: float,
        cusp: bool,
        cusp_values,
    ) -> Torus:
        angle, half_ab, half_cusp_area, half_spindle = cusp_values
        split = (distance_ij * distance_ij + vdw_i * vdw_i - vdw_j * vdw_j) / (
            2.0 * distance_ij
        )
        dist_phi = fabs(d_i - split)
        r_phi, sin_phi, cos_phi, phi = self.radical_vdw(
            dist_phi,
            solvent_radius,
            disk_radius,
        )

        if disk_radius > solvent_radius:
            area_phi = 2.0 * pi * solvent_radius * (disk_radius * phi - dist_phi)
            volume_mod = self.volume_cone_frustum(
                (r_phi - solvent_radius) * cos_phi,
                disk_radius,
                solvent_radius * sin_phi,
            )
            volume_phi = self.volume_torus_fraction(
                sin_phi,
                disk_radius,
                solvent_radius,
                phi,
            )
            if d_i < split:
                area_phi *= -1.0
                volume_phi *= -1.0
                volume_mod *= -1.0
            return Torus(
                area_i - area_phi,
                area_j + area_phi,
                volume_i - volume_phi,
                volume_j + volume_phi,
                volume_mod,
                -volume_mod,
            )

        if fabs(phi) > fabs(angle):
            volume_phi = self.volume_round_pyramid(disk_radius, half_ab)
            if not cusp:
                area_phi = half_cusp_area
                volume_phi -= half_spindle
            else:
                area_phi = 0.0
        else:
            volume_phi = self.volume_cone_frustum(
                solvent_radius * cos_phi - disk_radius,
                disk_radius,
                solvent_radius * sin_phi,
            )
            if not cusp:
                area_phi = 2.0 * pi * solvent_radius * (
                    dist_phi - disk_radius * phi
                )
                volume_phi -= self.volume_spindle(
                    phi,
                    sin_phi,
                    cos_phi,
                    disk_radius,
                    solvent_radius,
                )
            else:
                area_phi = 0.0

        if d_i < split:
            volume_phi *= -1.0
            area_phi *= -1.0
        return Torus(
            area_i - area_phi,
            area_j + area_phi,
            volume_i - volume_phi,
            volume_j + volume_phi,
            0.0,
            0.0,
        )


def space_filling_measurements(
    geometry,
    input_rank: int,
    *,
    cusp: bool = False,
    _context: VolblMetricContext | None = None,
) -> SpaceFillingMeasurements:
    """Return VOLBL `space_filling_measurements` totals up to `input_rank`."""

    from .geometry import ALF_EDGE, ALF_TETRA, ALF_TRIANGLE, ALF_VERTEX

    context = _context or _metric_context_from_geometry(geometry)
    edge_atoms_by_id = _edge_atoms_by_master_id(geometry)
    face_atoms_by_id = _face_atoms_by_master_id(geometry)
    simplex_atom_indices = np.asarray(geometry.mesh.simplex_atom_indices, dtype=int)

    volume_sa = 0.0
    volume_ms = 0.0
    area_sa = 0.0
    area_ms = 0.0
    length = 0.0
    corners = 0

    master_entries = list(getattr(geometry, 'master_entries'))
    master_rank_offsets = dict(getattr(geometry, 'master_rank_offsets'))

    for rank in range(1, int(input_rank) + 1):
        bounds = master_rank_offsets.get(int(rank))
        if bounds is None:
            continue
        start, end = bounds
        for entry in master_entries[int(start) : int(end)]:
            f_type = int(entry.f_type)
            if f_type == ALF_VERTEX:
                if not bool(entry.is_first):
                    continue
                i = int(entry.index)
                area_i = context.ball_area(i)
                shell_i = context.shell(i, area_i)
                ball_volume_i = context.ball_volume(i)
                volume_sa += ball_volume_i
                volume_ms += ball_volume_i - shell_i.volume
                area_sa += area_i
                area_ms += shell_i.area
            elif f_type == ALF_EDGE:
                if not bool(entry.is_first):
                    continue
                i, j = edge_atoms_by_id[int(entry.index)]
                area_i = context.cap_area(i, j)
                area_j = context.cap_area(j, i)
                shell_i = context.shell(i, area_i)
                shell_j = context.shell(j, area_j)
                torus_ij = context.torus(i, j, cusp=cusp)
                cap_volume_i = context.cap_volume(i, j)
                cap_volume_j = context.cap_volume(j, i)
                ball2_volume_ij = cap_volume_i + cap_volume_j

                volume_sa -= ball2_volume_ij
                volume_ms -= ball2_volume_ij
                volume_ms -= torus_ij.volume_1 + torus_ij.volume_2
                volume_ms += shell_i.volume + shell_j.volume
                length += context.ball2_length(i, j)
                area_sa -= area_i + area_j
                area_ms -= shell_i.area + shell_j.area
                area_ms += torus_ij.area_1 + torus_ij.area_2
            elif f_type == ALF_TRIANGLE:
                if not bool(entry.is_first):
                    continue
                i, j, k = face_atoms_by_id[int(entry.index)]
                area_i = context.cap2_area(i, j, k)
                area_j = context.cap2_area(j, i, k)
                area_k = context.cap2_area(k, i, j)
                cap2_volume_i = context.cap2_volume(i, j, k)
                cap2_volume_j = context.cap2_volume(j, i, k)
                cap2_volume_k = context.cap2_volume(k, i, j)
                ball3_volume_ijk = cap2_volume_i + cap2_volume_j + cap2_volume_k
                shell_i = context.shell(i, area_i)
                shell_j = context.shell(j, area_j)
                shell_k = context.shell(k, area_k)
                torus_ij = context.torus(i, j, cusp=cusp)
                torus_ik = context.torus(i, k, cusp=cusp)
                torus_jk = context.torus(j, k, cusp=cusp)
                segment_angle_ij_k = context.segment_angle(i, j, k)
                segment_angle_ik_j = context.segment_angle(i, k, j)
                segment_angle_jk_i = context.segment_angle(j, k, i)
                patch_ijk = context.patch(i, j, k)

                volume_sa += ball3_volume_ijk
                volume_ms += ball3_volume_ijk
                volume_ms -= 2.0 * patch_ijk.volume
                volume_ms += segment_angle_ij_k * (
                    torus_ij.volume_1 + torus_ij.volume_2
                )
                volume_ms += segment_angle_ik_j * (
                    torus_ik.volume_1 + torus_ik.volume_2
                )
                volume_ms += segment_angle_jk_i * (
                    torus_jk.volume_1 + torus_jk.volume_2
                )
                volume_ms -= shell_i.volume + shell_j.volume + shell_k.volume
                length -= context.ball3_length(i, j, k)
                corners += 2
                area_sa += area_i + area_j + area_k
                area_ms += shell_i.area + shell_j.area + shell_k.area
                area_ms -= segment_angle_ij_k * (
                    torus_ij.area_1 + torus_ij.area_2
                )
                area_ms -= segment_angle_ik_j * (
                    torus_ik.area_1 + torus_ik.area_2
                )
                area_ms -= segment_angle_jk_i * (
                    torus_jk.area_1 + torus_jk.area_2
                )
                area_ms += 2.0 * patch_ijk.area
            elif f_type == ALF_TETRA:
                i, j, k, l = [
                    int(atom_index)
                    for atom_index in simplex_atom_indices[int(entry.index)]
                ]
                cap3_volume_i = context.cap3_volume(i, j, k, l)
                cap3_volume_j = context.cap3_volume(j, i, k, l)
                cap3_volume_k = context.cap3_volume(k, i, j, l)
                cap3_volume_l = context.cap3_volume(l, i, j, k)
                ball4_volume_ijkl = (
                    cap3_volume_i + cap3_volume_j + cap3_volume_k + cap3_volume_l
                )
                area_i = context.cap3_area(i, j, k, l)
                area_j = context.cap3_area(j, i, k, l)
                area_k = context.cap3_area(k, i, j, l)
                area_l = context.cap3_area(l, i, j, k)
                shell_i = context.shell(i, area_i)
                shell_j = context.shell(j, area_j)
                shell_k = context.shell(k, area_k)
                shell_l = context.shell(l, area_l)
                segment2_angle_ij_kl = context.segment2_angle(i, j, k, l)
                segment2_angle_ik_jl = context.segment2_angle(i, k, j, l)
                segment2_angle_il_jk = context.segment2_angle(i, l, j, k)
                segment2_angle_jk_il = context.segment2_angle(j, k, i, l)
                segment2_angle_jl_ik = context.segment2_angle(j, l, i, k)
                segment2_angle_kl_ij = context.segment2_angle(k, l, i, j)
                torus_ij = context.torus(i, j, cusp=cusp)
                torus_ik = context.torus(i, k, cusp=cusp)
                torus_il = context.torus(i, l, cusp=cusp)
                torus_jk = context.torus(j, k, cusp=cusp)
                torus_jl = context.torus(j, l, cusp=cusp)
                torus_kl = context.torus(k, l, cusp=cusp)
                patch_ijk = context.patch(i, j, k)
                patch_ijl = context.patch(i, j, l)
                patch_ikl = context.patch(i, k, l)
                patch_jkl = context.patch(j, k, l)

                volume_sa -= ball4_volume_ijkl
                volume_ms -= ball4_volume_ijkl
                volume_ms += (
                    shell_i.volume
                    + shell_j.volume
                    + shell_k.volume
                    + shell_l.volume
                )
                volume_ms -= segment2_angle_ij_kl * (
                    torus_ij.volume_1 + torus_ij.volume_2
                )
                volume_ms -= segment2_angle_ik_jl * (
                    torus_ik.volume_1 + torus_ik.volume_2
                )
                volume_ms -= segment2_angle_il_jk * (
                    torus_il.volume_1 + torus_il.volume_2
                )
                volume_ms -= segment2_angle_jk_il * (
                    torus_jk.volume_1 + torus_jk.volume_2
                )
                volume_ms -= segment2_angle_jl_ik * (
                    torus_jl.volume_1 + torus_jl.volume_2
                )
                volume_ms -= segment2_angle_kl_ij * (
                    torus_kl.volume_1 + torus_kl.volume_2
                )
                volume_ms += (
                    patch_ijk.volume
                    + patch_ijl.volume
                    + patch_ikl.volume
                    + patch_jkl.volume
                )
                area_sa -= area_i + area_j + area_k + area_l
                area_ms -= (
                    shell_i.area + shell_j.area + shell_k.area + shell_l.area
                )
                area_ms += segment2_angle_ij_kl * (
                    torus_ij.area_1 + torus_ij.area_2
                )
                area_ms += segment2_angle_ik_jl * (
                    torus_ik.area_1 + torus_ik.area_2
                )
                area_ms += segment2_angle_il_jk * (
                    torus_il.area_1 + torus_il.area_2
                )
                area_ms += segment2_angle_jk_il * (
                    torus_jk.area_1 + torus_jk.area_2
                )
                area_ms += segment2_angle_jl_ik * (
                    torus_jl.area_1 + torus_jl.area_2
                )
                area_ms += segment2_angle_kl_ij * (
                    torus_kl.area_1 + torus_kl.area_2
                )
                area_ms -= (
                    patch_ijk.area
                    + patch_ijl.area
                    + patch_ikl.area
                    + patch_jkl.area
                )
                length += context.ball4_length(i, j, k, l)
                corners -= 4

    return SpaceFillingMeasurements(
        volume_sa=float(volume_sa),
        volume_ms=float(volume_ms),
        area_sa=float(area_sa),
        area_ms=float(area_ms),
        length=float(length),
        corners=int(corners),
    )


def voids_measurements(
    geometry,
    input_rank: int,
    *,
    cusp: bool = False,
    _context: VolblMetricContext | None = None,
) -> VoidMeasurements:
    """Return VOLBL `voids_measurements` totals for complement components."""

    from .components import _build_void_components

    void_components, _blocked_nodes = _build_void_components(
        geometry,
        np.zeros(int(geometry.mesh.n_simplices), dtype=bool),
    )
    context = _context or _metric_context_from_geometry(geometry)
    measurements = [
        _measure_void_component(
            geometry,
            context,
            simplex_indices=tuple(int(index) for index in simplex_indices),
            input_rank=int(input_rank),
            cusp=cusp,
        )
        for simplex_indices in void_components.values()
    ]
    measurements.sort(key=lambda item: item.initial_volume)

    return VoidMeasurements(
        total_volume_sa=float(sum(item.volume_sa for item in measurements)),
        total_volume_ms=float(sum(item.volume_ms for item in measurements)),
        total_area_sa=float(sum(item.area_sa for item in measurements)),
        total_area_ms=float(sum(item.area_ms for item in measurements)),
        total_length=float(sum(item.length for item in measurements)),
        total_corners=int(sum(item.corners for item in measurements)),
        voids=tuple(measurements),
    )


def fringe_measurements_cx(
    geometry,
    input_rank: int,
    *,
    cusp: bool = False,
    void_measurements: VoidMeasurements | None = None,
    _context: VolblMetricContext | None = None,
) -> SpaceFillingMeasurements:
    """Return VOLBL `fringe_measurements_cx` totals."""

    context = _context or _metric_context_from_geometry(geometry)
    edge_atoms_by_id = _edge_atoms_by_master_id(geometry)
    face_atoms_by_id = _face_atoms_by_master_id(geometry)
    simplex_atom_indices = np.asarray(geometry.mesh.simplex_atom_indices, dtype=int)
    void_measurements = void_measurements or voids_measurements(
        geometry,
        input_rank,
        cusp=cusp,
        _context=context,
    )

    volume_sa = 0.0
    volume_ms = 0.0
    area_sa = 0.0
    area_ms = 0.0
    length = 0.0
    corners = 0

    master_entries = list(getattr(geometry, 'master_entries'))
    master_rank_offsets = dict(getattr(geometry, 'master_rank_offsets'))

    from .geometry import ALF_EDGE, ALF_TETRA, ALF_TRIANGLE, ALF_VERTEX

    for rank in range(1, int(input_rank) + 1):
        bounds = master_rank_offsets.get(int(rank))
        if bounds is None:
            continue
        start, end = bounds
        for entry in master_entries[int(start) : int(end)]:
            f_type = int(entry.f_type)
            if f_type == ALF_VERTEX:
                if not bool(entry.is_first):
                    continue
                i = int(entry.index)
                if _vertex_is_interior(geometry, i, int(input_rank)):
                    continue
                area_i = context.ball_area(i)
                shell_i = context.shell(i, area_i)
                ball_volume_i = context.ball_volume(i)
                volume_sa -= ball_volume_i
                volume_ms += -ball_volume_i + shell_i.volume
                area_sa -= area_i
                area_ms -= shell_i.area
            elif f_type == ALF_EDGE:
                if not bool(entry.is_first):
                    continue
                i, j = edge_atoms_by_id[int(entry.index)]
                if _edge_is_interior(geometry, i, j, int(input_rank)):
                    continue
                area_i = context.cap_area(i, j)
                area_j = context.cap_area(j, i)
                shell_i = context.shell(i, area_i)
                shell_j = context.shell(j, area_j)
                torus_ij = context.torus(i, j, cusp=cusp)
                cap_volume_i = context.cap_volume(i, j)
                cap_volume_j = context.cap_volume(j, i)
                ball2_volume_ij = cap_volume_i + cap_volume_j
                volume_sa += ball2_volume_ij
                volume_ms += ball2_volume_ij
                volume_ms += torus_ij.volume_1 + torus_ij.volume_2
                volume_ms -= shell_i.volume + shell_j.volume
                length -= context.ball2_length(i, j)
                area_sa += area_i + area_j
                area_ms += shell_i.area + shell_j.area
                area_ms -= torus_ij.area_1 + torus_ij.area_2
            elif f_type == ALF_TRIANGLE:
                if not bool(entry.is_first):
                    continue
                i, j, k = face_atoms_by_id[int(entry.index)]
                if _face_is_interior(geometry, i, j, k, int(input_rank)):
                    continue
                delta = _fringe_triangle_delta(context, i, j, k, cusp=cusp)
                volume_sa += delta.volume_sa
                volume_ms += delta.volume_ms
                area_sa += delta.area_sa
                area_ms += delta.area_ms
                length += delta.length
                corners += delta.corners
            elif f_type == ALF_TETRA:
                i, j, k, l = [
                    int(atom_index)
                    for atom_index in simplex_atom_indices[int(entry.index)]
                ]
                for delta in _complex_tetrahedron_fringe_deltas(
                    geometry,
                    context,
                    (i, j, k, l),
                    input_rank=int(input_rank),
                    cusp=cusp,
                ):
                    volume_sa += delta.volume_sa
                    volume_ms += delta.volume_ms
                    area_sa += delta.area_sa
                    area_ms += delta.area_ms
                    length += delta.length
                    corners += delta.corners

    initial_void_volume = sum(item.initial_volume for item in void_measurements.voids)
    return SpaceFillingMeasurements(
        volume_sa=float(
            -volume_sa - initial_void_volume + void_measurements.total_volume_sa
        ),
        volume_ms=float(
            -volume_ms - initial_void_volume + void_measurements.total_volume_ms
        ),
        area_sa=float(-area_sa - void_measurements.total_area_sa),
        area_ms=float(-area_ms - void_measurements.total_area_ms),
        length=float(-length - void_measurements.total_length),
        corners=int(-corners - void_measurements.total_corners),
    )


def shape_volume(geometry, input_rank: int) -> float:
    """Return VOLBL `shape_volume` for tetrahedra up to `input_rank`."""

    context = _metric_context_from_geometry(geometry)
    simplex_atom_indices = np.asarray(geometry.mesh.simplex_atom_indices, dtype=int)
    master_entries = list(getattr(geometry, 'master_entries'))
    master_rank_offsets = dict(getattr(geometry, 'master_rank_offsets'))

    from .geometry import ALF_TETRA

    volume = 0.0
    for rank in range(1, int(input_rank) + 1):
        bounds = master_rank_offsets.get(int(rank))
        if bounds is None:
            continue
        start, end = bounds
        for entry in master_entries[int(start) : int(end)]:
            if int(entry.f_type) != ALF_TETRA:
                continue
            volume += context.tetrahedron_volume(
                *[
                    int(atom_index)
                    for atom_index in simplex_atom_indices[int(entry.index)]
                ]
            )
    return float(volume)


def envelope_measurements(
    geometry,
    input_rank: int,
    *,
    cusp: bool = False,
) -> EnvelopeMeasurements:
    """Return VOLBL envelope measurements using the dual-complex fringe path."""

    context = _metric_context_from_geometry(geometry)
    void_values = voids_measurements(
        geometry,
        input_rank,
        cusp=cusp,
        _context=context,
    )
    fringe_values = fringe_measurements_cx(
        geometry,
        input_rank,
        cusp=cusp,
        void_measurements=void_values,
        _context=context,
    )
    shape_value = shape_volume(geometry, input_rank)
    return EnvelopeMeasurements(
        voids=void_values,
        fringe=fringe_values,
        shape_volume=float(shape_value),
        shape_volume_ms=float(shape_value),
    )


def volbl_measurements(
    geometry,
    input_rank: int,
    *,
    cusp: bool = False,
) -> VolblMeasurements:
    """Return complete global VOLBL measurements with shared primitive caches."""

    context = _metric_context_from_geometry(geometry)
    space_filling_values = space_filling_measurements(
        geometry,
        input_rank,
        cusp=cusp,
        _context=context,
    )
    void_values = voids_measurements(
        geometry,
        input_rank,
        cusp=cusp,
        _context=context,
    )
    fringe_values = fringe_measurements_cx(
        geometry,
        input_rank,
        cusp=cusp,
        void_measurements=void_values,
        _context=context,
    )
    shape_value = shape_volume(geometry, input_rank)
    return VolblMeasurements(
        space_filling=space_filling_values,
        voids=void_values,
        fringe=fringe_values,
        shape_volume=float(shape_value),
        shape_volume_ms=float(shape_value),
    )


def _measure_void_component(
    geometry,
    context: VolblMetricContext,
    *,
    simplex_indices: tuple[int, ...],
    input_rank: int,
    cusp: bool,
) -> VoidMeasurement:
    simplex_atom_indices = np.asarray(geometry.mesh.simplex_atom_indices, dtype=int)
    volume_sa = 0.0
    for simplex_index in simplex_indices:
        i, j, k, l = [
            int(atom_index)
            for atom_index in simplex_atom_indices[int(simplex_index)]
        ]
        volume_sa += context.tetrahedron_volume(i, j, k, l)

    volume_ms = float(volume_sa)
    area_sa = 0.0
    area_ms = 0.0
    length = 0.0
    corners = 0

    for simplex_index in simplex_indices:
        i, j, k, l = [
            int(atom_index)
            for atom_index in simplex_atom_indices[int(simplex_index)]
        ]
        vertices = (i, j, k, l)
        for vertex_position, vertex_index in enumerate(vertices):
            if not _vertex_in_complex(geometry, vertex_index, int(input_rank)):
                continue
            others = tuple(
                int(vertices[index])
                for index in range(4)
                if index != int(vertex_position)
            )
            delta = _void_tetra_vertex(context, vertex_index, *others)
            volume_sa += delta.volume_sa
            volume_ms += delta.volume_ms
            area_sa += delta.area_sa
            area_ms += delta.area_ms

        for first, second, third, fourth in (
            (i, j, k, l),
            (i, k, j, l),
            (i, l, j, k),
            (j, k, i, l),
            (j, l, i, k),
            (k, l, i, j),
        ):
            if not _edge_in_complex(geometry, first, second, int(input_rank)):
                continue
            delta = _void_tetra_edge(
                context,
                first,
                second,
                third,
                fourth,
                cusp=cusp,
            )
            volume_sa += delta.volume_sa
            volume_ms += delta.volume_ms
            area_sa += delta.area_sa
            area_ms += delta.area_ms
            length += delta.length

        for first, second, third in (
            (i, j, k),
            (j, i, l),
            (k, j, l),
            (i, k, l),
        ):
            if not _face_in_complex(geometry, first, second, third, int(input_rank)):
                continue
            delta = _void_tetra_triangle(
                context,
                first,
                second,
                third,
                cusp=cusp,
            )
            volume_sa += delta.volume_sa
            volume_ms += delta.volume_ms
            area_sa += delta.area_sa
            area_ms += delta.area_ms
            length += delta.length
            corners += delta.corners

    return VoidMeasurement(
        simplex_indices=tuple(sorted(int(index) for index in simplex_indices)),
        initial_volume=float(
            sum(
                context.tetrahedron_volume(
                    *[
                        int(atom_index)
                        for atom_index in simplex_atom_indices[int(simplex_index)]
                    ]
                )
                for simplex_index in simplex_indices
            )
        ),
        volume_sa=float(volume_sa),
        volume_ms=float(volume_ms),
        area_sa=float(area_sa),
        area_ms=float(area_ms),
        length=float(length),
        corners=int(corners),
    )


def _void_tetra_vertex(
    context: VolblMetricContext,
    i: int,
    j: int,
    k: int,
    l: int,
) -> SpaceFillingMeasurements:
    sector_area = context.sector_area(i, j, k, l)
    sector_volume = sector_area * context.ball_radius(i) / 3.0
    shell_i = context.shell(i, sector_area)
    return SpaceFillingMeasurements(
        volume_sa=-sector_volume,
        volume_ms=-sector_volume + shell_i.volume,
        area_sa=sector_area,
        area_ms=shell_i.area,
        length=0.0,
        corners=0,
    )


def _void_tetra_edge(
    context: VolblMetricContext,
    i: int,
    j: int,
    k: int,
    l: int,
    *,
    cusp: bool,
) -> SpaceFillingMeasurements:
    angle_dihedral = context.angle_dihedral(
        context.vector(i),
        context.vector(j),
        context.vector(k),
        context.vector(l),
    )
    cap_volume_ij = context.cap_volume(i, j)
    cap_volume_ji = context.cap_volume(j, i)
    wedge_volume = angle_dihedral * (cap_volume_ij + cap_volume_ji)
    area_i = angle_dihedral * context.cap_area(i, j)
    area_j = angle_dihedral * context.cap_area(j, i)
    shell_i = context.shell(i, area_i)
    shell_j = context.shell(j, area_j)
    torus_ij = context.torus(i, j, cusp=cusp)
    torus_area = angle_dihedral * (torus_ij.area_1 + torus_ij.area_2)
    torus_volume = angle_dihedral * (torus_ij.volume_1 + torus_ij.volume_2)
    return SpaceFillingMeasurements(
        volume_sa=wedge_volume,
        volume_ms=wedge_volume + torus_volume - shell_i.volume - shell_j.volume,
        area_sa=-(area_i + area_j),
        area_ms=-(shell_i.area + shell_j.area) + torus_area,
        length=context.wedge_length(i, j, k, l),
        corners=0,
    )


def _void_tetra_triangle(
    context: VolblMetricContext,
    i: int,
    j: int,
    k: int,
    *,
    cusp: bool,
) -> SpaceFillingMeasurements:
    area_i = 0.5 * context.cap2_area(i, j, k)
    area_j = 0.5 * context.cap2_area(j, i, k)
    area_k = 0.5 * context.cap2_area(k, i, j)
    cap2_volume_i = context.cap2_volume(i, j, k)
    cap2_volume_j = context.cap2_volume(j, i, k)
    cap2_volume_k = context.cap2_volume(k, i, j)
    pawn_volume = 0.5 * (cap2_volume_i + cap2_volume_j + cap2_volume_k)
    shell_i = context.shell(i, area_i)
    shell_j = context.shell(j, area_j)
    shell_k = context.shell(k, area_k)
    torus_ij = context.torus(i, j, cusp=cusp)
    torus_ik = context.torus(i, k, cusp=cusp)
    torus_jk = context.torus(j, k, cusp=cusp)
    patch_ijk = context.patch(i, j, k)
    segment_angle_ij_k = context.segment_angle(i, j, k)
    segment_angle_ik_j = context.segment_angle(i, k, j)
    segment_angle_jk_i = context.segment_angle(j, k, i)
    torus_volume = 0.5 * (
        segment_angle_ij_k * (torus_ij.volume_1 + torus_ij.volume_2)
        + segment_angle_ik_j * (torus_ik.volume_1 + torus_ik.volume_2)
        + segment_angle_jk_i * (torus_jk.volume_1 + torus_jk.volume_2)
    )
    torus_area = 0.5 * (
        segment_angle_ij_k * (torus_ij.area_1 + torus_ij.area_2)
        + segment_angle_ik_j * (torus_ik.area_1 + torus_ik.area_2)
        + segment_angle_jk_i * (torus_jk.area_1 + torus_jk.area_2)
    )
    return SpaceFillingMeasurements(
        volume_sa=-pawn_volume,
        volume_ms=(
            -pawn_volume
            + patch_ijk.volume
            - torus_volume
            + shell_i.volume
            + shell_j.volume
            + shell_k.volume
        ),
        area_sa=area_i + area_j + area_k,
        area_ms=(
            shell_i.area
            + shell_j.area
            + shell_k.area
            - torus_area
            + patch_ijk.area
        ),
        length=-context.pawn_length(i, j, k),
        corners=1,
    )


def _fringe_triangle_delta(
    context: VolblMetricContext,
    i: int,
    j: int,
    k: int,
    *,
    cusp: bool,
) -> SpaceFillingMeasurements:
    area_i = context.cap2_area(i, j, k)
    area_j = context.cap2_area(j, i, k)
    area_k = context.cap2_area(k, i, j)
    cap2_volume_i = context.cap2_volume(i, j, k)
    cap2_volume_j = context.cap2_volume(j, i, k)
    cap2_volume_k = context.cap2_volume(k, i, j)
    ball3_volume = cap2_volume_i + cap2_volume_j + cap2_volume_k
    shell_i = context.shell(i, area_i)
    shell_j = context.shell(j, area_j)
    shell_k = context.shell(k, area_k)
    torus_ij = context.torus(i, j, cusp=cusp)
    torus_ik = context.torus(i, k, cusp=cusp)
    torus_jk = context.torus(j, k, cusp=cusp)
    segment_angle_ij_k = context.segment_angle(i, j, k)
    segment_angle_ik_j = context.segment_angle(i, k, j)
    segment_angle_jk_i = context.segment_angle(j, k, i)
    patch_ijk = context.patch(i, j, k)
    torus_volume = (
        segment_angle_ij_k * (torus_ij.volume_1 + torus_ij.volume_2)
        + segment_angle_ik_j * (torus_ik.volume_1 + torus_ik.volume_2)
        + segment_angle_jk_i * (torus_jk.volume_1 + torus_jk.volume_2)
    )
    torus_area = (
        segment_angle_ij_k * (torus_ij.area_1 + torus_ij.area_2)
        + segment_angle_ik_j * (torus_ik.area_1 + torus_ik.area_2)
        + segment_angle_jk_i * (torus_jk.area_1 + torus_jk.area_2)
    )
    return SpaceFillingMeasurements(
        volume_sa=-ball3_volume,
        volume_ms=(
            -ball3_volume
            + 2.0 * patch_ijk.volume
            - torus_volume
            + shell_i.volume
            + shell_j.volume
            + shell_k.volume
        ),
        area_sa=-(area_i + area_j + area_k),
        area_ms=(
            -(shell_i.area + shell_j.area + shell_k.area)
            + torus_area
            - 2.0 * patch_ijk.area
        ),
        length=context.ball3_length(i, j, k),
        corners=-2,
    )


def _complex_tetrahedron_fringe_deltas(
    geometry,
    context: VolblMetricContext,
    vertices: tuple[int, int, int, int],
    *,
    input_rank: int,
    cusp: bool,
) -> list[SpaceFillingMeasurements]:
    i, j, k, l = vertices
    deltas: list[SpaceFillingMeasurements] = []
    for vertex_position, vertex_index in enumerate(vertices):
        if _vertex_is_interior(geometry, vertex_index, int(input_rank)):
            continue
        others = tuple(
            int(vertices[index])
            for index in range(4)
            if index != int(vertex_position)
        )
        deltas.append(_outside_tetra_vertex(context, vertex_index, *others))

    for first, second, third, fourth in (
        (i, j, k, l),
        (i, k, j, l),
        (i, l, j, k),
        (j, k, i, l),
        (j, l, i, k),
        (k, l, i, j),
    ):
        if _edge_is_interior(geometry, first, second, int(input_rank)):
            continue
        deltas.append(
            _outside_tetra_edge(
                context,
                first,
                second,
                third,
                fourth,
                cusp=cusp,
            )
        )

    for first, second, third in (
        (i, j, k),
        (i, j, l),
        (j, k, l),
        (k, i, l),
    ):
        if _face_is_interior(geometry, first, second, third, int(input_rank)):
            continue
        deltas.append(
            _outside_tetra_triangle(
                context,
                first,
                second,
                third,
                cusp=cusp,
            )
        )
    return deltas


def _outside_tetra_vertex(
    context: VolblMetricContext,
    i: int,
    j: int,
    k: int,
    l: int,
) -> SpaceFillingMeasurements:
    sector_area = context.sector_area(i, j, k, l)
    sector_volume = sector_area * context.ball_radius(i) / 3.0
    shell_i = context.shell(i, sector_area)
    return SpaceFillingMeasurements(
        volume_sa=sector_volume,
        volume_ms=sector_volume - shell_i.volume,
        area_sa=sector_area,
        area_ms=shell_i.area,
        length=0.0,
        corners=0,
    )


def _outside_tetra_edge(
    context: VolblMetricContext,
    i: int,
    j: int,
    k: int,
    l: int,
    *,
    cusp: bool,
) -> SpaceFillingMeasurements:
    angle_dihedral = context.angle_dihedral(
        context.vector(i),
        context.vector(j),
        context.vector(k),
        context.vector(l),
    )
    cap_volume_ij = context.cap_volume(i, j)
    cap_volume_ji = context.cap_volume(j, i)
    wedge_volume = angle_dihedral * (cap_volume_ij + cap_volume_ji)
    area_i = angle_dihedral * context.cap_area(i, j)
    area_j = angle_dihedral * context.cap_area(j, i)
    shell_i = context.shell(i, area_i)
    shell_j = context.shell(j, area_j)
    torus_ij = context.torus(i, j, cusp=cusp)
    torus_area = angle_dihedral * (torus_ij.area_1 + torus_ij.area_2)
    torus_volume = angle_dihedral * (torus_ij.volume_1 + torus_ij.volume_2)
    return SpaceFillingMeasurements(
        volume_sa=-wedge_volume,
        volume_ms=-wedge_volume - torus_volume + shell_i.volume + shell_j.volume,
        area_sa=-(area_i + area_j),
        area_ms=-(shell_i.area + shell_j.area) + torus_area,
        length=context.wedge_length(i, j, k, l),
        corners=0,
    )


def _outside_tetra_triangle(
    context: VolblMetricContext,
    i: int,
    j: int,
    k: int,
    *,
    cusp: bool,
) -> SpaceFillingMeasurements:
    delta = _void_tetra_triangle(context, i, j, k, cusp=cusp)
    return SpaceFillingMeasurements(
        volume_sa=-delta.volume_sa,
        volume_ms=-delta.volume_ms,
        area_sa=delta.area_sa,
        area_ms=delta.area_ms,
        length=delta.length,
        corners=delta.corners,
    )


def _metric_context_from_geometry(geometry) -> VolblMetricContext:
    from .geometry import _weighted_hidden0, _weighted_hidden1

    coordinates = np.asarray(geometry.atom_coordinates, dtype=float)
    radii = np.asarray(geometry.atom_radii, dtype=float)
    weights = radii * radii

    def hidden0(i: int, j: int) -> bool:
        return (
            _weighted_hidden0(
                coordinates[int(i)],
                float(weights[int(i)]),
                coordinates[int(j)],
                float(weights[int(j)]),
            )
            != 0
        )

    def hidden1(i: int, j: int, k: int) -> bool:
        edge_indices = np.asarray([int(i), int(j)], dtype=int)
        return (
            _weighted_hidden1(
                coordinates[edge_indices],
                weights[edge_indices],
                coordinates[int(k)],
                float(weights[int(k)]),
            )
            != 0
        )

    def ccw(i: int, j: int, k: int, l: int) -> bool:
        points = coordinates[np.asarray([int(i), int(j), int(k), int(l)], dtype=int)]
        determinant = float(
            np.linalg.det(
                np.asarray(
                    [
                        points[1] - points[0],
                        points[2] - points[0],
                        points[3] - points[0],
                    ],
                    dtype=float,
                )
            )
        )
        # VOLBL delegates `ccw` to `sos_positive3(i,j,k,l)`.  With the native
        # coordinate order used here, CASTp's positive orientation is the
        # opposite of the direct row-determinant convention below.
        return determinant < 0.0

    return VolblMetricContext(
        coordinates=coordinates,
        radii=radii,
        weights=radii,
        solvent_radius=float(getattr(geometry, 'solvent_radius', 1.4)),
        alpha=float(getattr(geometry, 'alpha', 0.0)),
        hidden0=hidden0,
        hidden1=hidden1,
        ccw=ccw,
    )


def _edge_atoms_by_master_id(geometry) -> dict[int, tuple[int, int]]:
    return {
        int(edge_id): tuple(int(atom_index) for atom_index in edge_atoms)
        for edge_id, edge_atoms in enumerate(sorted(geometry.edge_rho_ranks))
    }


def _face_atoms_by_master_id(geometry) -> dict[int, tuple[int, int, int]]:
    face_atoms_by_id: dict[int, tuple[int, int, int]] = {}
    face_id_by_atoms: dict[tuple[int, int, int], int] = {}
    for _simplex_index, _face_index, face_atoms in geometry.face_records:
        atoms = tuple(int(atom_index) for atom_index in face_atoms)
        face_id = face_id_by_atoms.setdefault(atoms, len(face_id_by_atoms))
        face_atoms_by_id[int(face_id)] = atoms
    return face_atoms_by_id


def _vertex_in_complex(geometry, vertex_index: int, rank: int) -> bool:
    from .geometry import _vertex_is_in_complex_at

    return bool(_vertex_is_in_complex_at(geometry, int(vertex_index), int(rank)))


def _vertex_is_interior(geometry, vertex_index: int, rank: int) -> bool:
    from .geometry import _vertex_is_interior_at

    return bool(_vertex_is_interior_at(geometry, int(vertex_index), int(rank)))


def _edge_in_complex(geometry, i: int, j: int, rank: int) -> bool:
    from .geometry import _edge_is_in_complex_at

    return bool(
        _edge_is_in_complex_at(
            geometry.edge_rho_ranks,
            geometry.edge_mu1_ranks,
            (int(i), int(j)),
            int(rank),
        )
    )


def _edge_is_interior(geometry, i: int, j: int, rank: int) -> bool:
    from .geometry import _rank_table_is_interior

    edge = tuple(sorted((int(i), int(j))))
    return bool(
        _rank_table_is_interior(
            int(geometry.edge_mu2_ranks.get(edge, 0)),
            int(rank),
        )
    )


def _face_in_complex(geometry, i: int, j: int, k: int, rank: int) -> bool:
    from .geometry import _rank_table_is_in_complex

    face_rank_maps = _face_rank_maps_by_atoms(geometry)
    face_key = tuple(sorted((int(i), int(j), int(k))))
    ranks = face_rank_maps.get(face_key)
    if ranks is None:
        return False
    rho_rank, mu1_rank, _mu2_rank = ranks
    return bool(_rank_table_is_in_complex(rho_rank, mu1_rank, int(rank)))


def _face_is_interior(geometry, i: int, j: int, k: int, rank: int) -> bool:
    from .geometry import _rank_table_is_interior

    face_rank_maps = _face_rank_maps_by_atoms(geometry)
    face_key = tuple(sorted((int(i), int(j), int(k))))
    ranks = face_rank_maps.get(face_key)
    if ranks is None:
        return False
    _rho_rank, _mu1_rank, mu2_rank = ranks
    return bool(_rank_table_is_interior(mu2_rank, int(rank)))


def _face_rank_maps_by_atoms(geometry) -> dict[tuple[int, int, int], tuple[int, int, int]]:
    cached = _FACE_RANK_MAP_CACHE.get(id(geometry))
    if cached is not None and cached[0] is geometry:
        return cached[1]

    face_rank_maps: dict[tuple[int, int, int], tuple[int, int, int]] = {}
    for simplex_index, face_index, face_atoms in geometry.face_records:
        face_key = tuple(sorted(int(atom_index) for atom_index in face_atoms))
        if face_key in face_rank_maps:
            continue
        face_rank_maps[face_key] = (
            int(geometry.face_rho_ranks[int(simplex_index), int(face_index)]),
            int(geometry.face_mu1_ranks[int(simplex_index), int(face_index)]),
            int(geometry.face_mu2_ranks[int(simplex_index), int(face_index)]),
        )
    if len(_FACE_RANK_MAP_CACHE) >= _FACE_RANK_MAP_CACHE_LIMIT:
        _FACE_RANK_MAP_CACHE.clear()
    _FACE_RANK_MAP_CACHE[id(geometry)] = (geometry, face_rank_maps)
    return face_rank_maps
