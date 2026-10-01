"""Tests for the reusable immutable array storage tool."""

import numpy as np
import pytest


@pytest.mark.parametrize('dtype', [np.float64, np.int64, np.bool_])
def test_immutable_array_owns_storage_and_cannot_be_made_writable(dtype):
    from topomt.tools.geometry.arrays import immutable_array

    original = np.ones((4, 3), dtype=dtype)
    saved = immutable_array(original)
    original[:] = 0
    np.testing.assert_array_equal(saved, np.ones((4, 3), dtype=dtype))
    assert saved.dtype == dtype
    with pytest.raises(ValueError):
        saved[0, 0] = 0
    with pytest.raises(ValueError):
        saved.setflags(write=True)


def test_immutable_array_reuses_immutable_buffers_with_independent_shape_metadata():
    from topomt.tools.geometry.arrays import immutable_array

    original = immutable_array(np.arange(12).reshape(4, 3))
    saved = immutable_array(original)
    assert np.shares_memory(original, saved)
    original.shape = (12,)
    assert saved.shape == (4, 3)


def test_immutable_array_does_not_trust_a_readonly_flag_on_mutable_storage():
    from topomt.tools.geometry.arrays import immutable_array

    original = np.arange(4.0)
    original.setflags(write=False)
    saved = immutable_array(original)
    original.setflags(write=True)
    original[:] = 100
    np.testing.assert_array_equal(saved, np.arange(4.0))


def test_immutable_array_preserves_strided_values_and_handles_empty_arrays():
    from topomt.tools.geometry.arrays import immutable_array

    original = np.arange(12).reshape(4, 3)[:, ::2]
    np.testing.assert_array_equal(immutable_array(original), original)
    assert immutable_array(np.empty((0, 3))).shape == (0, 3)
    with pytest.raises(TypeError, match='object'):
        immutable_array(np.array([[]], dtype=object))
