"""Representative points derived from tetrahedra."""

from collections.abc import Sequence

import numpy as np


def representative_points_from_tetra(
    pockets: Sequence[Sequence[int]],
    tetra_positions: np.ndarray,
) -> list[np.ndarray]:
    """Return one centroid-like representative point per tetrahedron group."""

    representatives = []
    for pocket in pockets:
        if len(pocket) == 0:
            representatives.append(np.zeros(3))
            continue
        coords = tetra_positions[np.asarray(pocket, dtype=int)].reshape(-1, 3)
        representatives.append(coords.mean(axis=0))
    return representatives
