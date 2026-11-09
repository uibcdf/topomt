"""Common overlap helpers for feature sets."""

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

from topomt._ackredit import attributed, scientific_call


@attributed('geometry', route='native')
def jaccard_overlap_clusters(
    lining_lists: list[list[int]],
    overlap_cutoff: float,
    total_index: int | None = None,
) -> dict[int, list[int]]:
    """Cluster features by Jaccard distance of their lining-atom sets."""

    if total_index is None:
        total_index = max((max(item) for item in lining_lists if item), default=0) + 1
    if total_index <= 0 or not lining_lists:
        return {}
    if len(lining_lists) == 1:
        return {0: [0]}

    matrix = np.zeros((len(lining_lists), total_index), dtype=int)
    for row_index, lining in enumerate(lining_lists):
        matrix[row_index, np.asarray(lining, int)] = 1

    intersection = matrix @ matrix.T
    union = np.add.outer(matrix.sum(axis=1), matrix.sum(axis=1)) - intersection
    with np.errstate(divide='ignore', invalid='ignore'):
        jaccard = 1.0 - intersection / union
    jaccard[np.isnan(jaccard)] = 1.0

    condensed = scientific_call('scipy', squareform, jaccard, checks=False)
    linkage_matrix = scientific_call('scipy', linkage, condensed, method='average')
    labels = (
        scientific_call(
            'scipy', fcluster, linkage_matrix, t=overlap_cutoff, criterion='distance'
        )
        - 1
    )
    clusters: dict[int, list[int]] = {}
    for feature_index, label in enumerate(labels):
        clusters.setdefault(int(label), []).append(feature_index)

    return clusters
