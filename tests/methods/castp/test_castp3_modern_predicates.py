"""Independent consistency guards for the modern weighted geometry."""

import numpy as np

from topomt.third_party.castp3.core.castp_core.exact import fixed_point_array
from topomt.third_party.castp3.core.castp_core.geometry import (
    _fixed_point_lifted_rows,
    _simplex_exact_ratio,
)


def test_modern_grid_materializes_python_integers_without_three_decimal_truncation():
    result = fixed_point_array(np.asarray([[-1.001, 14.746, 3.00004]]), 5)
    assert result.tolist() == [[-100100, 1474600, 300004]]
    assert all(isinstance(value, int) for value in result.flat)


def test_modern_exact_order_preserves_thin_neighbor_power_order():
    # A five-atom witness from 1CDO: the second circumcenter lies beyond the
    # shared face, so its power radius must exceed the first. The archived
    # PDB decimal coordinates define the input, without historical C truncation.
    points = np.asarray(
        [
            [14.746, 33.922, 60.465],  # HIS ND1
            [18.415, 30.970, 54.632],  # VAL O
            [19.634, 33.696, 51.976],  # GLY O
            [15.773, 34.392, 51.541],  # TRP O
            [16.337, 41.037, 56.320],  # GLU OE2
        ]
    )
    radii = np.asarray([3.04, 2.82, 2.82, 2.82, 2.80])
    lifted = _fixed_point_lifted_rows(points, radii, 5)
    stable = _simplex_exact_ratio(lifted[[0, 3, 2, 1]])
    thin_neighbor = _simplex_exact_ratio(lifted[[4, 0, 2, 1]])
    assert thin_neighbor.compare(stable) > 0
    assert np.isclose(stable.to_float() / 1e10, 19.9178021542, atol=1e-9, rtol=0)
    assert np.isclose(thin_neighbor.to_float() / 1e10, 19.9207043976, atol=1e-8, rtol=0)
