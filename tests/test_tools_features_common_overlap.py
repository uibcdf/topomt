"""Tests for common overlap helpers in topomt.tools.features."""

from topomt.tools.features.common import jaccard_overlap_clusters


def test_jaccard_overlap_clusters_groups_identical_sets_together():

    clusters = jaccard_overlap_clusters(
        [[0, 1, 2], [0, 1, 2], [7, 8]],
        overlap_cutoff=0.1,
    )

    grouped = sorted(sorted(indices) for indices in clusters.values())
    assert grouped == [[0, 1], [2]]


def test_jaccard_overlap_clusters_returns_empty_dict_for_empty_input():

    clusters = jaccard_overlap_clusters([], overlap_cutoff=0.5)

    assert clusters == {}

def test_jaccard_overlap_clusters_returns_single_feature_cluster():

    clusters = jaccard_overlap_clusters([[1, 2]], overlap_cutoff=0.5)

    assert clusters == {0: [0]}
