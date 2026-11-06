"""Validate captured AlphaSpace2 snapshot fields without running its algorithms."""

from typing import Any, NoReturn

import numpy as np

from topomt.third_party._saved_json import read_json

from .output import _output_protocol


def _invalid(field: str) -> NoReturn:
    raise ValueError(f'Invalid AlphaSpace2 saved snapshot: {field}.')


def _number(
    value: Any, field: str, *, nonnegative: bool = False, undefined: bool = False
) -> float:
    if undefined and isinstance(value, dict) and set(value) == {'nonfinite'}:
        marker = value['nonfinite']
        if isinstance(marker, str) and marker in {'nan', 'inf', '-inf'}:
            return float(marker)
    if type(value) not in (int, float):
        _invalid(field)
    try:
        result = float(value)
    except (OverflowError, ValueError):
        _invalid(field)
    if not np.isfinite(result) or nonnegative and result < 0:
        _invalid(field)
    return result


def _numbers(
    value: Any, shape: tuple[int, ...], field: str, *, nonnegative: bool = False
) -> np.ndarray:
    if not isinstance(value, list):
        _invalid(field)
    try:
        array: np.ndarray = np.asarray(value, dtype=object)
        if array.shape == (0,) and shape[0] == 0:
            return np.empty(shape, dtype=float)
        if array.shape != shape or any(type(v) not in (int, float) for v in array.flat):
            _invalid(field + ' shape/type')
        result: np.ndarray = np.asarray(value, dtype=float)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(
            f'Invalid AlphaSpace2 saved numeric array: {field}.'
        ) from error
    if not np.isfinite(result).all() or nonnegative and np.any(result < 0):
        _invalid(field + ' values')
    return result


def _indices(value: Any, limit: int, field: str) -> list[int]:
    if (
        not isinstance(value, list)
        or not value
        or any(type(i) is not int or not 0 <= i < limit for i in value)
        or len(set(value)) != len(value)
    ):
        _invalid(field + ' indices')
    return value


def _groups(value: Any, limit: int, field: str) -> list[list[int]]:
    if not isinstance(value, list):
        _invalid(field)
    return [_indices(group, limit, field) for group in value]


def _partition(groups: list[list[int]], count: int, field: str) -> None:
    if sorted(index for group in groups for index in group) != list(range(count)):
        _invalid(field + ' partition')


def _booleans(value: Any, count: int, field: str) -> None:
    if (
        not isinstance(value, list)
        or len(value) != count
        or any(type(v) is not bool for v in value)
    ):
        _invalid(field)


def _properties(
    state: dict[str, Any], group: str, memberships: list[list[int]]
) -> None:
    name = group + '_properties'
    records = state[name]
    if not isinstance(records, list) or len(records) != len(memberships):
        _invalid(name)
    expected = {
        'index',
        'alpha_indices',
        'space',
        'nonpolar_space',
        'score',
        'occupied_space',
        'occupied_nonpolar_space',
        'occupancy',
        'occupancy_nonpolar',
        'is_contact',
    }
    expected |= {'beta_indices'} if group == 'pocket' else {'scores', 'best_probe_type'}
    for index, record in enumerate(records):
        if (
            not isinstance(record, dict)
            or set(record) != expected
            or type(record['index']) is not int
            or record['index'] != index
        ):
            _invalid(name + ' schema/index')
        if record['alpha_indices'] != memberships[index] or any(
            type(i) is not int for i in record['alpha_indices']
        ):
            _invalid(name + ' alpha membership')
        for key in (
            'space',
            'nonpolar_space',
            'occupied_space',
            'occupied_nonpolar_space',
        ):
            _number(record[key], name + '.' + key, nonnegative=True)
        _number(record['score'], name + '.score')
        for key in ('occupancy', 'occupancy_nonpolar'):
            _number(record[key], name + '.' + key, undefined=True)
        if (
            type(record['is_contact']) is not bool
            or record['is_contact'] != state['_' + group + '_contact'][index]
        ):
            _invalid(name + ' contact')
        if not np.isclose(
            record['space'], state['_' + group + '_space'][index], rtol=1e-6, atol=1e-5
        ):
            _invalid(name + ' duplicated space')
        if group == 'pocket':
            if record['beta_indices'] != state['_pocket_beta_index_list'][index] or any(
                type(i) is not int for i in record['beta_indices']
            ):
                _invalid(name + ' beta membership')
        else:
            scores = state['_beta_scores'][index]
            if isinstance(scores, list):
                _numbers(record['scores'], (9,), name + '.scores')
            else:
                _number(record['scores'], name + '.scores')
            if not np.array_equal(record['scores'], scores):
                _invalid(name + ' duplicated scores')
            if record['best_probe_type'] not in (
                'C',
                'Br',
                'F',
                'Cl',
                'I',
                'OA',
                'SA',
                'N',
                'P',
            ):
                _invalid(name + ' probe type')


def parse_snapshot(
    data: bytes, n_submitted: int, protocol: dict[str, Any]
) -> dict[str, Any]:
    """Validate the declared schema, units, shapes and reference graph.

    Parameters
    ----------
    data : bytes
        Captured schema 1 snapshot, including reported property values.
    n_submitted : int
        Number of receptor PDB rows in the validated source map.
    protocol : dict
        Exact explicit output-unit protocol from the captured run.

    Returns
    -------
    dict
        Original decoded fields without redetection, clustering or scoring.
        Undefined occupancy markers stay encoded in the reported properties.

    Raises
    ------
    ValueError
        If schema, units, numeric fields or indices are inconsistent.
    """
    if (
        not isinstance(protocol, dict)
        or type(protocol.get('schema_version')) is not int
        or protocol != _output_protocol()
    ):
        _invalid('output unit protocol')
    state = read_json(data, provider='AlphaSpace2')
    keys = {
        'schema_version',
        '_alpha_xyz',
        '_alpha_radii',
        '_alpha_space',
        '_alpha_space_nonpolar_ratio',
        '_alpha_lining',
        '_alpha_contact',
        '_beta_xyz',
        '_beta_space',
        '_beta_scores',
        '_beta_contact',
        '_beta_dpocket_index',
        '_beta_alpha_index_list',
        '_pocket_xyz',
        '_pocket_space',
        '_pocket_contact',
        '_pocket_alpha_index_list',
        '_pocket_beta_index_list',
        'atom_names',
        'residue_names',
        'elements',
        'pocket_properties',
        'beta_properties',
    }
    if (
        not isinstance(state, dict)
        or set(state) != keys
        or type(state['schema_version']) is not int
        or state['schema_version'] != 1
    ):
        _invalid('schema')
    for field in ('atom_names', 'residue_names', 'elements'):
        value = state[field]
        if (
            not isinstance(value, list)
            or len(value) != n_submitted
            or any(not isinstance(v, str) or not v for v in value)
        ):
            _invalid(field)
    for field in ('_alpha_xyz', '_beta_xyz', '_pocket_xyz'):
        if not isinstance(state[field], list):
            _invalid(field)
    n_alpha, n_beta, n_pocket = [
        len(state[k]) for k in ('_alpha_xyz', '_beta_xyz', '_pocket_xyz')
    ]
    for prefix, count in [('alpha', n_alpha), ('beta', n_beta), ('pocket', n_pocket)]:
        _numbers(state['_' + prefix + '_xyz'], (count, 3), prefix + ' coordinates')
        _numbers(
            state['_' + prefix + '_space'],
            (count,),
            prefix + ' space',
            nonnegative=True,
        )
        _booleans(state['_' + prefix + '_contact'], count, prefix + ' contact')
    radii = _numbers(state['_alpha_radii'], (n_alpha,), 'alpha radii', nonnegative=True)
    if np.any(radii <= 0):
        _invalid('alpha radii')
    ratios = _numbers(
        state['_alpha_space_nonpolar_ratio'],
        (n_alpha,),
        'alpha nonpolar ratios',
        nonnegative=True,
    )
    if np.any(ratios > 1):
        _invalid('alpha nonpolar ratios')
    lining = state['_alpha_lining']
    if not isinstance(lining, list) or len(lining) != n_alpha:
        _invalid('alpha lining')
    for row in lining:
        _indices(row, n_submitted, 'alpha lining')
        if len(row) != 4:
            _invalid('alpha lining shape')
    if state['_beta_dpocket_index'] is not None:
        _invalid('unsupported trajectory dpocket state')
    scores = state['_beta_scores']
    shape = (
        (n_beta, 9)
        if isinstance(scores, list) and scores and isinstance(scores[0], list)
        else (n_beta,)
    )
    _numbers(scores, shape, 'beta scores')
    beta_alpha = _groups(state['_beta_alpha_index_list'], n_alpha, 'beta alpha')
    pocket_alpha = _groups(state['_pocket_alpha_index_list'], n_alpha, 'pocket alpha')
    pocket_beta = _groups(state['_pocket_beta_index_list'], n_beta, 'pocket beta')
    if (
        len(beta_alpha) != n_beta
        or len(pocket_alpha) != n_pocket
        or len(pocket_beta) != n_pocket
    ):
        _invalid('group counts')
    _partition(beta_alpha, n_alpha, 'beta alpha')
    _partition(pocket_alpha, n_alpha, 'pocket alpha')
    _partition(pocket_beta, n_beta, 'pocket beta')
    for alphas, betas in zip(pocket_alpha, pocket_beta):
        if sorted(a for b in betas for a in beta_alpha[b]) != sorted(alphas):
            _invalid('pocket alpha/beta graph')
    _properties(state, 'beta', beta_alpha)
    _properties(state, 'pocket', pocket_alpha)
    return state
