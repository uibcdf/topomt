import numpy as np

from topomt import pyunitwizard as puw

from ...exceptions import ArgumentError

functions_where_boolean = ()


def digest_points(points, caller=None):
    if caller is not None and caller.endswith(functions_where_boolean):
        if isinstance(points, bool):
            return points

    if points is None:
        return None

    if not puw.is_quantity(points):
        if not isinstance(points, np.ndarray):
            points = np.array(points)
        points = puw.quantity(points, 'dimensionless')

    value, unit = puw.get_value_and_unit(points)

    if not puw.check(unit, dimensionality={'[L]': 1}) and not puw.check(
        unit, dimensionality={}
    ):
        raise ArgumentError('points', value=points, caller=caller, message=None)

    if not isinstance(value, np.ndarray):
        value = np.array(value)

    value = value.astype(np.float64)
    shape = value.shape

    if len(shape) == 1 and shape[0] == 3:
        return puw.quantity(value[np.newaxis, :], unit, standardized=True)

    if len(shape) == 2 and shape[1] == 3:
        return puw.quantity(value, unit, standardized=True)

    if len(shape) > 2 and shape[-1] == 3:
        raise ArgumentError(
            'points',
            value=points,
            caller=caller,
            message='The object needs to be 2 dimensional: [n_points, 3]',
        )

    raise ArgumentError('points', value=points, caller=caller, message=None)
