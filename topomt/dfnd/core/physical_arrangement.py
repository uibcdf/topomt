"""Bounded all-atom connectivity on a declared atomic-center hull.

The analytic circle/triangle arrangement is independent of native face gates.
Lengths in this internal kernel and its records are nanometers. Incomplete or
numerically marginal arrangements have no accepted total count.
"""

from itertools import combinations
from typing import Any

import numpy as np

from topomt._ackredit import attributed


class _Unresolved(ValueError):
    """An arrangement decision has insufficient numerical separation or budget."""


class _Budget:
    def __init__(self, maximum):
        self.maximum = maximum
        self.used = 0

    def tick(self, count=1):
        if self.used + count > self.maximum:
            raise _Unresolved('arrangement work budget exhausted')
        self.used += count


@attributed('geometry', retain=False)
def segment_clearance(
    start: np.ndarray, end: np.ndarray, centers: np.ndarray, radii: np.ndarray
) -> float:
    """Return the all-ball margin along the entire closed segment.

    Parameters
    ----------
    start, end : numpy.ndarray, shape (3,)
        Segment endpoints in nm.
    centers : numpy.ndarray, shape (n, 3)
        All selected atomic centers in nm.
    radii : numpy.ndarray, shape (n,)
        Probe-expanded radii in nm.

    Returns
    -------
    float
        Minimum distance minus expanded radius, in nm.
    """
    direction = np.asarray(end) - start
    length2 = float(direction @ direction)
    parameters = (
        np.clip((centers - start) @ direction / length2, 0.0, 1.0)
        if length2
        else np.zeros(len(centers))
    )
    points = start + parameters[:, None] * direction
    return float(np.min(np.linalg.norm(centers - points, axis=1) - radii))


def _inside(point, triangle, margin=0.0):
    sides = np.roll(triangle, -1, axis=0) - triangle
    offsets = point - triangle
    return bool(
        np.all(sides[:, 0] * offsets[:, 1] - sides[:, 1] * offsets[:, 0] >= -margin)
    )


def _triangle_distance(point, triangle):
    if _inside(point, triangle):
        return 0.0
    sides = np.roll(triangle, -1, axis=0) - triangle
    parameters = np.clip(
        np.sum((point - triangle) * sides, axis=1) / np.sum(sides * sides, axis=1),
        0.0,
        1.0,
    )
    return float(
        np.min(np.linalg.norm(point - triangle - parameters[:, None] * sides, axis=1))
    )


def _value(selector, x, disks):
    if selector['kind'] == 'line':
        a, b = np.asarray(selector['start']), np.asarray(selector['end'])
        return float(a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0]))
    cx, cy, radius = disks[selector['disk']]
    return float(cy + selector['branch'] * np.sqrt(max(0.0, radius**2 - (x - cx) ** 2)))


def _sections(x, triangle, disks, roundoff, decision_margin=0.0):
    """Exact-section interval inventory, with analytic selectors at each end."""
    sides = []
    for a, b in zip(triangle, np.roll(triangle, -1, axis=0), strict=True):
        if abs(b[0] - a[0]) <= roundoff:
            continue
        if min(a[0], b[0]) - roundoff <= x <= max(a[0], b[0]) + roundoff:
            selector = {'kind': 'line', 'start': a.tolist(), 'end': b.tolist()}
            sides.append((_value(selector, x, disks), selector))
    if len(sides) < 2:
        return []
    sides.sort(key=lambda item: item[0])
    bottom, top = sides[0], sides[-1]
    if top[0] - bottom[0] <= roundoff:
        return []
    covered = []
    for index, (cx, cy, radius) in enumerate(disks):
        if abs(x - cx) > radius + roundoff:
            continue
        half = np.sqrt(max(0.0, radius**2 - (x - cx) ** 2))
        if cy + half < bottom[0] - roundoff or cy - half > top[0] + roundoff:
            continue
        lower = {'kind': 'arc', 'disk': index, 'branch': -1}
        upper = {'kind': 'arc', 'disk': index, 'branch': 1}
        lo = (max(bottom[0], cy - half), bottom[1] if bottom[0] >= cy - half else lower)
        hi = (min(top[0], cy + half), top[1] if top[0] <= cy + half else upper)
        covered.append((lo, hi))
    covered.sort(key=lambda pair: pair[0][0])
    cursor = bottom
    free = []
    for lo, hi in covered:
        if (
            decision_margin
            and lo[1] != cursor[1]
            and abs(lo[0] - cursor[0]) <= decision_margin
        ):
            raise _Unresolved('section exclusion overlap within numerical margin')
        if lo[0] > cursor[0] + roundoff:
            free.append((cursor[1], lo[1]))
        if hi[0] > cursor[0]:
            cursor = hi
    if top[0] > cursor[0] + roundoff:
        free.append((cursor[1], top[1]))
    return free


def _critical_sections(triangle, disks, tolerance, roundoff, budget):
    events = list(triangle[:, 0])

    def add(x):
        if triangle[:, 0].min() - roundoff <= x <= triangle[:, 0].max() + roundoff:
            events.append(float(x))
            budget.tick()

    for cx, cy, radius in disks:
        add(cx - radius)
        add(cx + radius)
        center = np.array([cx, cy])
        for a, b in zip(triangle, np.roll(triangle, -1, axis=0), strict=True):
            vector = b - a
            length = np.linalg.norm(vector)
            unit = vector / length
            position = float((center - a) @ unit)
            perpendicular = np.linalg.norm(center - a - position * unit)
            if (
                abs(perpendicular - radius) <= tolerance
                and -tolerance <= position <= length + tolerance
            ):
                raise _Unresolved('circle/edge tangency within numerical margin')
            discriminant = radius**2 - perpendicular**2
            if discriminant <= 0:
                continue
            for parameter in (
                position - np.sqrt(discriminant),
                position + np.sqrt(discriminant),
            ):
                if -roundoff <= parameter <= length + roundoff:
                    add((a + parameter * unit)[0])
    for first, second in combinations(disks, 2):
        budget.tick()
        c1, c2 = np.asarray(first[:2]), np.asarray(second[:2])
        r1, r2 = first[2], second[2]
        distance = np.linalg.norm(c2 - c1)
        if distance < roundoff:
            # Concentric disks are nested; duplicate constraints stay in the input.
            continue
        if distance > r1 + r2 + tolerance or distance < abs(r1 - r2) - tolerance:
            continue
        unit = (c2 - c1) / distance
        along = (r1 * r1 - r2 * r2 + distance * distance) / (2 * distance)
        foot = c1 + along * unit
        if min(abs(distance - r1 - r2), abs(distance - abs(r1 - r2))) <= tolerance:
            if _inside(foot, triangle, tolerance):
                raise _Unresolved('circle/circle tangency within numerical margin')
            continue
        height2 = r1 * r1 - along * along
        if height2 < 0:
            continue
        perpendicular = np.array([-unit[1], unit[0]])
        for point in (
            foot + np.sqrt(height2) * perpendicular,
            foot - np.sqrt(height2) * perpendicular,
        ):
            add(point[0])
    critical = []
    for x in sorted(events):
        if critical and x - critical[-1] <= roundoff:
            continue
        if critical and x - critical[-1] <= tolerance:
            raise _Unresolved('critical-section ordering within numerical margin')
        critical.append(x)
    return critical


def _covered_face(triangle, centers, radii, tolerance, budget):
    """A complete finite union of convex, strictly ball-covered subtriangles."""
    pending = [(triangle, [])]
    leaves = []
    while pending:
        budget.tick()
        cell, path = pending.pop()
        margins = radii - np.max(
            np.linalg.norm(cell[None, :, :] - centers[:, None, :], axis=2), axis=1
        )
        atom = int(np.argmax(margins))
        if margins[atom] > tolerance:
            leaves.append(
                {
                    'triangle': cell.tolist(),
                    'ball_local_index': atom,
                    'cover_margin': float(margins[atom]),
                    'path': path,
                }
            )
            continue
        if len(path) >= 12:
            return None
        midpoint = cell.mean(axis=0)
        if np.min(np.linalg.norm(centers - midpoint, axis=1) - radii) > tolerance:
            return None
        a, b, c = cell
        ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        pending.extend(
            (np.array(child), [*path, child_index])
            for child_index, child in enumerate(
                ([a, ab, ca], [ab, b, bc], [ca, bc, c], [ab, bc, ca])
            )
        )
    return leaves


@attributed('geometry', retain=False)
def decompose_face(
    triangle: np.ndarray,
    centers: np.ndarray,
    expanded_radii: np.ndarray,
    *,
    tolerance: float = 1e-7,
    max_events: int = 100_000,
) -> dict[str, Any]:
    """Decompose a triangle's strict all-ball complement with bounded work.

    Returns recoverable analytic strip selectors, event sections and their
    connectivity. All numeric inputs/outputs use nm. This developer kernel
    does not accept a carrier triangle as free patch support.

    Parameters
    ----------
    triangle : numpy.ndarray, shape (3, 3)
        Carrier vertices in nm.
    centers, expanded_radii : numpy.ndarray
        All selected atomic centers and probe-expanded radii in nm.
    tolerance : float
        Numerical decision margin in nm, independent of physical tolerances.
    max_events : int
        Work ceiling, including tested intersections and cover subdivisions.

    Returns
    -------
    dict
        Resolved analytic cells or an explicit unresolved reason. A computed
        zero retains a complete positive-margin ball cover.
    """
    triangle = np.asarray(triangle, dtype=float)
    centers = np.asarray(centers, dtype=float)
    expanded_radii = np.asarray(expanded_radii, dtype=float)
    result: dict[str, Any] = {
        'status': 'unresolved',
        'regions': None,
        'inventory_complete': False,
        'units': {'length': 'nm', 'coordinates': 'nm'},
        'event_count': 0,
    }
    budget = _Budget(max_events)
    try:
        budget.tick(len(centers))
        if (
            triangle.shape != (3, 3)
            or centers.ndim != 2
            or centers.shape[1] != 3
            or expanded_radii.shape != (len(centers),)
            or not np.isfinite(triangle).all()
            or not np.isfinite(centers).all()
            or not np.isfinite(expanded_radii).all()
            or np.any(expanded_radii <= 0)
            or not np.isfinite(tolerance)
            or tolerance <= 0
        ):
            raise _Unresolved('invalid geometry or numerical margin')
        origin = triangle[0]
        axis = triangle[1] - origin
        length = np.linalg.norm(axis)
        normal = np.cross(axis, triangle[2] - origin)
        area2 = np.linalg.norm(normal)
        if length <= tolerance or area2 <= tolerance * max(length, tolerance):
            raise _Unresolved('degenerate triangle')
        axis = axis / length
        normal = normal / area2
        second = np.cross(normal, axis)
        basis = np.array([axis, second])
        planar = (triangle - origin) @ basis.T
        scale = max(1.0, float(np.max(np.abs(planar))), float(np.max(expanded_radii)))
        roundoff = 256 * np.finfo(float).eps * scale
        result.update(
            frame={
                'origin': origin.tolist(),
                'basis': basis.tolist(),
                'normal': normal.tolist(),
            },
            triangle=planar.tolist(),
            tolerance=tolerance,
            roundoff=roundoff,
        )
        disks = []
        for center, radius in zip(centers, expanded_radii, strict=True):
            # A strictly covering ball proves a complete zero without topology.
            if (
                float(np.max(np.linalg.norm(triangle - center, axis=1)))
                < radius - tolerance
            ):
                result.update(
                    status='resolved',
                    regions=[],
                    inventory_complete=True,
                    covered_by_ball={
                        'center': center.tolist(),
                        'radius': float(radius),
                    },
                )
                return result
            z = float((center - origin) @ normal)
            xy = (center - origin) @ basis.T
            if abs(z) > radius + tolerance:
                continue
            r2 = radius * radius - z * z
            if r2 <= 0:
                if abs(abs(z) - radius) <= tolerance and _inside(xy, planar, tolerance):
                    raise _Unresolved('ball/plane tangency within numerical margin')
                continue
            projected_radius = np.sqrt(r2)
            distance = _triangle_distance(xy, planar)
            if distance > projected_radius + tolerance:
                continue
            if abs(distance - projected_radius) <= tolerance:
                raise _Unresolved('ball/triangle tangency within numerical margin')
            disks.append([float(xy[0]), float(xy[1]), float(projected_radius)])
        critical = _critical_sections(planar, disks, tolerance, roundoff, budget)
        result.update(
            disks=disks, critical_sections=critical, event_count=len(critical)
        )
        if len(critical) > max_events:
            raise _Unresolved('arrangement event budget exhausted')
        cells: list[dict[str, Any]] = []
        parents = []
        slabs = []
        slices = []

        def add_cell(kind, x, interval, span):
            budget.tick()
            lower, upper = interval
            lo = _value(lower, x, disks)
            hi = _value(upper, x, disks)
            if hi - lo <= tolerance:
                raise _Unresolved('free section width within numerical margin')
            point = origin + np.array([x, (lo + hi) / 2]) @ basis
            margin = float(
                np.min(np.linalg.norm(centers - point, axis=1) - expanded_radii)
            )
            if margin <= tolerance:
                raise _Unresolved('free witness within numerical margin')
            index = len(cells)
            parents.append(index)
            cells.append(
                {
                    'kind': kind,
                    'x': x,
                    'x_span': span,
                    'lower': lower,
                    'upper': upper,
                    'witness': point.tolist(),
                    'witness_clearance': margin,
                }
            )
            return index

        def root(index):
            while parents[index] != index:
                parents[index] = parents[parents[index]]
                index = parents[index]
            return index

        for x in critical:
            budget.tick(len(disks) + 1)
            slices.append(
                [
                    add_cell('section', x, interval, [x, x])
                    for interval in _sections(x, planar, disks, roundoff)
                ]
            )
        for left, right in zip(critical[:-1], critical[1:], strict=True):
            budget.tick(len(disks) + 1)
            x = (left + right) / 2
            slabs.append(
                [
                    add_cell('strip', x, interval, [left, right])
                    for interval in _sections(x, planar, disks, roundoff, tolerance)
                ]
            )
        for slab_index, nodes in enumerate(slabs):
            for event_index in (slab_index, slab_index + 1):
                x = critical[event_index]
                for a in nodes:
                    for b in slices[event_index]:
                        budget.tick()
                        lo = max(
                            _value(cells[a]['lower'], x, disks),
                            _value(cells[b]['lower'], x, disks),
                        )
                        hi = min(
                            _value(cells[a]['upper'], x, disks),
                            _value(cells[b]['upper'], x, disks),
                        )
                        if hi - lo > tolerance:
                            parents[root(a)] = root(b)
                        elif hi - lo > roundoff:
                            raise _Unresolved(
                                'event connectivity within numerical margin'
                            )
        grouped: dict[int, list[int]] = {}
        for index in range(len(cells)):
            grouped.setdefault(root(index), []).append(index)
        regions = []
        for nodes in grouped.values():
            witness = max(
                (cells[i] for i in nodes), key=lambda item: item['witness_clearance']
            )
            regions.append(
                {
                    'cells': nodes,
                    'witness': witness['witness'],
                    'witness_clearance': witness['witness_clearance'],
                }
            )
        if not regions:
            cover = _covered_face(triangle, centers, expanded_radii, tolerance, budget)
            if cover is None:
                raise _Unresolved('zero lacks a complete positive-margin cover')
            result['complete_cover'] = cover
        result.update(
            status='resolved', regions=regions, cells=cells, inventory_complete=True
        )
    except _Unresolved as error:
        result.update(
            status='unresolved',
            regions=None,
            inventory_complete=False,
            reason=str(error),
        )
        if 'within numerical margin' in str(error) and triangle.shape == (3, 3):
            try:
                leaves = _covered_face(
                    triangle, centers, expanded_radii, tolerance, budget
                )
                if leaves is not None:
                    result.update(
                        status='resolved',
                        regions=[],
                        inventory_complete=True,
                        complete_cover=leaves,
                        arrangement_fallback=str(error),
                    )
                    result.pop('reason')
            except _Unresolved as exhausted:
                result['reason'] = str(exhausted)
    finally:
        result['work_units'] = budget.used
    return result
