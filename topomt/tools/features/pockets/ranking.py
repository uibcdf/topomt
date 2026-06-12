"""Pocket ranking helpers."""

from collections.abc import Sequence


def simple_ranking(
    volumes: Sequence[float],
    pockets: Sequence[Sequence[int]],
    alpha: float = 1.0,
    beta: float = 0.1,
) -> list[float]:
    """Return a simple volume-plus-size ranking score per pocket."""

    if len(volumes) != len(pockets):
        raise ValueError('volumes and pockets must have the same length')

    return [alpha * volume + beta * len(pocket) for volume, pocket in zip(volumes, pockets)]
