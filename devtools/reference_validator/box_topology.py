"""Produce one-ball/axis-box topology certificates for bounded P1 controls.

This analytic construction does not admit multiple obstacles. Its completeness
argument is in the developer feasibility checkpoint. The independent checker
validates coverage and every intersection without importing this producer.
"""

from fractions import Fraction
from itertools import combinations, product
from typing import Any

from .model import Box, Model, encode_point, point
from .verify.geometry import point_is_free


def single_ball_box(model: Model) -> dict[str, Any]:
    """Decompose a box's strict free set outside exactly one expanded ball.

    Parameters
    ----------
    model : Model
        Exact nonperiodic nm model with one ball and an axis-aligned box.

    Returns
    -------
    dict
        Unverified certificate with at most eight monotone pieces, all pair
        intersections and a proposed component partition. A piece denotes its
        closed sector intersected with the strict free set, not a voxel.

    Raises
    ------
    ValueError
        The domain is not an axis box or there is not exactly one ball.

    Examples
    --------
    See ``tests/test_reference_validator_box_topology.py`` for exact corner
    and critical-contact controls; verify the returned record before use.
    """
    if len(model.atoms) != 1 or not isinstance(model.domain, Box):
        raise ValueError('Topology construction requires exactly one ball and a box')
    atom = model.atoms[0]
    axes: list[tuple[tuple[int, Fraction, Fraction, Fraction], ...]] = []
    for lo, c, hi in zip(model.domain.lower, atom.center, model.domain.upper):
        if lo < c < hi:
            axes.append(((0, lo, c, lo), (1, c, hi, hi)))
        elif c <= lo:
            axes.append(((1, lo, hi, hi),))
        else:
            axes.append(((0, lo, hi, lo),))
    pieces: list[dict[str, Any]] = []
    cells = {}
    for entries in product(*axes):
        name = ''.join(str(e[0]) for e in entries)
        lower, upper, corner = (point([e[i] for e in entries]) for i in (1, 2, 3))
        cells[name] = (lower, upper)
        pieces.append(
            {
                'id': name,
                'lower': encode_point(lower),
                'upper': encode_point(upper),
                'corner': encode_point(corner),
                'free_set_state': 'nonempty'
                if point_is_free(model, corner)
                else 'empty',
            }
        )
    neighbors: dict[str, set[str]] = {
        p['id']: set() for p in pieces if p['free_set_state'] == 'nonempty'
    }
    joins = []
    for a, b in combinations(cells, 2):
        join_lower = [max(x, y) for x, y in zip(cells[a][0], cells[b][0])]
        join_upper = [min(x, y) for x, y in zip(cells[a][1], cells[b][1])]
        witness = point(
            [
                hi if (hi - c) ** 2 >= (lo - c) ** 2 else lo
                for lo, c, hi in zip(join_lower, atom.center, join_upper)
            ]
        )
        state = 'nonempty' if point_is_free(model, witness) else 'empty'
        joins.append(
            {
                'pieces': [a, b],
                'witness': encode_point(witness),
                'free_set_state': state,
            }
        )
        if state == 'nonempty':
            neighbors[a].add(b)
            neighbors[b].add(a)
    components = []
    remaining = set(neighbors)
    while remaining:
        seen = set()
        stack = [min(remaining)]
        while stack:
            name = stack.pop()
            if name in seen:
                continue
            seen.add(name)
            stack.extend(neighbors[name] - seen)
        components.append(sorted(seen))
        remaining -= seen
    return {
        'schema': 'topomt.reference-validator.certificate/1',
        'kind': 'single_ball_box_topology',
        'arithmetic': 'rational-exact/1',
        'model_sha256': model.digest,
        'pieces': pieces,
        'joins': joins,
        'components': components,
    }
