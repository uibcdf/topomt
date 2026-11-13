"""Check the complete monotone-sector cover for one ball clipped by a box.

Trusted geometric theorem: in an orthant relative to the one ball's center,
outward coordinate motion increases squared distance. Each nonempty free
sector joins its farthest corner. All pair intersections are checked: a finite
relatively closed cover by path-connected pieces has the components of its
full intersection graph. See the developer P1 feasibility checkpoint.
"""

from itertools import combinations, product
from typing import Any

from ..model import Box, Model, _record, decode_point, encode_point, point
from .geometry import point_is_free, segment_is_free


def check(model: Model, certificate: dict[str, Any]) -> dict[str, Any]:
    """Validate full sector and incidence coverage without producer search."""
    if len(model.atoms) != 1 or not isinstance(model.domain, Box):
        raise ValueError('Topology checking requires exactly one ball and a box')
    atom = model.atoms[0]
    rows = certificate['pieces']
    if not isinstance(rows, list) or not 1 <= len(rows) <= 8:
        raise ValueError('Invalid monotone-sector cover')
    expected_ids = []
    cells = {}
    roots = {}
    free = set()
    # Enumerate signs from the model, independently of submitted rows. Omit
    # zero-width half-intervals when the center is on/outside the box.
    for bits in product((0, 1), repeat=3):
        lower, upper, corner = [], [], []
        for axis, bit in enumerate(bits):
            lo, hi = model.domain.lower[axis], model.domain.upper[axis]
            c = atom.center[axis]
            if (bit == 0 and c <= lo) or (bit == 1 and c >= hi):
                break
            lower.append(max(lo, c) if bit else lo)
            upper.append(hi if bit else min(hi, c))
            corner.append(hi if bit else lo)
        else:
            name = ''.join(str(b) for b in bits)
            expected_ids.append(name)
            cells[name] = (point(lower), point(upper))
            roots[name] = point(corner)
    if [r.get('id') if isinstance(r, dict) else None for r in rows] != expected_ids:
        raise ValueError('Sector coverage is missing, duplicated or reordered')
    for row in rows:
        _record(row, {'id', 'lower', 'upper', 'corner', 'free_set_state'})
        name = row['id']
        if (
            decode_point(row['lower']) != cells[name][0]
            or decode_point(row['upper']) != cells[name][1]
            or decode_point(row['corner']) != roots[name]
        ):
            raise ValueError('Sector support or farthest corner is incorrect')
        state = 'nonempty' if point_is_free(model, roots[name]) else 'empty'
        if row['free_set_state'] != state:
            raise ValueError('Sector nonempty/covered claim is incorrect')
        if state == 'nonempty':
            free.add(name)
    joins = certificate['joins']
    expected_pairs = list(combinations(expected_ids, 2))
    if not isinstance(joins, list) or len(joins) != len(expected_pairs):
        raise ValueError('Pair intersection coverage is incomplete')
    classes = [{name} for name in sorted(free)]
    for join, (a, b) in zip(joins, expected_pairs):
        _record(join, {'pieces', 'witness', 'free_set_state'})
        if join['pieces'] != [a, b]:
            raise ValueError('Pair intersection identities differ')
        farthest = []
        for i, c in enumerate(atom.center):
            lo = max(cells[a][0][i], cells[b][0][i])
            hi = min(cells[a][1][i], cells[b][1][i])
            # Intersections may be lower dimensional; do not drop a seam
            # or try to represent it as a full-dimensional Box.
            farthest.append(hi if abs(hi - c) >= abs(lo - c) else lo)
        witness = point(farthest)
        if decode_point(join['witness']) != witness:
            raise ValueError('Intersection witness is not its farthest point')
        state = 'nonempty' if point_is_free(model, witness) else 'empty'
        if join['free_set_state'] != state:
            raise ValueError('Pair intersection availability is incorrect')
        if state == 'nonempty':
            if not all(segment_is_free(model, roots[p], witness) for p in (a, b)):
                raise ValueError('Intersection paths are unproved')
            merged = {a, b}
            separate = []
            for group in classes:
                if group.intersection((a, b)):
                    merged |= group
                else:
                    separate.append(group)
            classes = separate + [merged]
    components = sorted(sorted(group) for group in classes)
    if certificate['components'] != components:
        raise ValueError('Claimed component partition differs from checked incidences')
    return {
        'topology_complete': True,
        'topology_status': 'resolved',
        'topology_scope': 'single-ball-axis-box/1',
        'n_components': len(components),
        'regions': [
            {
                'id': f'r{i}',
                'piece_ids': list(group),
                'representative': encode_point(roots[group[0]]),
            }
            for i, group in enumerate(components)
        ],
        'length_unit': 'nm',
        'boundary_incidence_status': 'not_computed',
        'volume_status': 'not_computed',
        'precision_status': 'not_requested',
    }
