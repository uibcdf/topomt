"""Tetrahedron-oriented helpers."""

from collections.abc import Sequence

import numpy as np


def analytic_tetra_volume(
    tetra_positions: np.ndarray,
    indices: Sequence[int] | Sequence[Sequence[int]],
) -> float:
    """Compute the exact total volume of selected tetrahedra."""

    tets = tetra_positions[np.asarray(indices, dtype=int)]

    if tets.ndim != 3 or tets.shape[-2:] != (4, 3):
        raise ValueError(f'Invalid shape for tetrahedra: {tets.shape}. Expected (N, 4, 3).')

    a, b, c, d = tets[:, 0], tets[:, 1], tets[:, 2], tets[:, 3]
    volume = np.abs(np.einsum('ij,ij->i', a - d, np.cross(b - d, c - d))) / 6.0
    return float(volume.sum())
