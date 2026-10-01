"""Owned array storage for reusable geometric snapshots."""

import copy
from typing import Any, Self

import numpy as np


def immutable_array(array: np.ndarray) -> np.ndarray:
    """Return an array backed by immutable storage with independent metadata.

    Parameters
    ----------
    array : numpy.ndarray
        Values, dtype and shape to preserve. Object-containing dtypes are
        unsupported because their elements may refer to mutable Python objects.

    Returns
    -------
    numpy.ndarray
        A C-contiguous read-only snapshot. Writable or externally mutable
        storage is copied once. Existing immutable bytes storage is shared.
        Shape metadata is independent in either case.

    Raises
    ------
    TypeError
        If the dtype contains Python objects.

    Examples
    --------
    >>> values = np.array([1., 2.])
    >>> saved = immutable_array(values)
    >>> values[0] = 9.
    >>> saved.tolist()
    [1.0, 2.0]
    """
    if array.dtype.hasobject:
        raise TypeError('Immutable array snapshots do not support object dtypes.')
    base = array
    while isinstance(base, np.ndarray) and base.base is not None:
        base = base.base
    if isinstance(base, bytes) and array.flags.c_contiguous:
        return array.view()
    return np.frombuffer(array.tobytes(order='C'), dtype=array.dtype).reshape(
        array.shape
    )


class _GeometrySnapshot:
    """Private ownership machinery behind supported mesh/network operations."""

    def __getattribute__(self, name: str) -> Any:
        value = object.__getattribute__(self, name)
        if isinstance(value, np.ndarray) and vars(self).get('_geometry_frozen', False):
            # Views share immutable bytes but cannot change canonical shape metadata.
            return value.view()
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        if not name.startswith('_') and vars(self).get('_geometry_frozen', False):
            raise AttributeError(
                'Geometry is read-only; build a new mesh or network for changed input.'
            )
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if not name.startswith('_') and vars(self).get('_geometry_frozen', False):
            raise AttributeError('Geometry is read-only; build a new mesh or network.')
        object.__delattr__(self, name)

    def _freeze_arrays(self) -> None:
        for name, value in list(vars(self).items()):
            if isinstance(value, np.ndarray):
                object.__setattr__(self, name, immutable_array(value))
        object.__setattr__(self, '_geometry_frozen', True)

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        copied = type(self).__new__(type(self))
        memo[id(self)] = copied
        frozen = vars(self).get('_geometry_frozen', False)
        for name, value in vars(self).items():
            if frozen and isinstance(value, np.ndarray):
                copied_value = memo.setdefault(id(value), immutable_array(value))
            else:
                copied_value = copy.deepcopy(value, memo)
            object.__setattr__(copied, name, copied_value)
        return copied

    def __setstate__(self, state: dict[str, Any]) -> None:
        # NumPy pickle reconstruction creates writable buffers by default.
        vars(self).update(state)
        if state.get('_geometry_frozen', False):
            self._freeze_arrays()
