"""Tests for pocket ranking helpers in topomt.tools.features."""

import pytest

from topomt.tools.features.pockets import simple_ranking


def test_simple_ranking_combines_volume_and_pocket_size():

    scores = simple_ranking(
        volumes=[10.0, 3.0],
        pockets=[[0, 1], [2, 3, 4]],
        alpha=1.0,
        beta=0.5,
    )

    assert scores == [11.0, 4.5]

def test_simple_ranking_rejects_mismatched_sequences():

    with pytest.raises(ValueError, match='same length'):
        simple_ranking(volumes=[10.0, 3.0], pockets=[[0, 1]])
