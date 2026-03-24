from __future__ import annotations
from typing import Any

def digest_cluster_method(cluster_method: str, caller: str | None = None) -> str:
    """
    Digest the 'cluster_method' argument.
    """
    valid_methods = {'single', 'complete', 'average', 'weighted', 'centroid', 'median', 'ward'}
    if isinstance(cluster_method, str) and cluster_method.lower() in valid_methods:
        return cluster_method.lower()
    return 'average'
