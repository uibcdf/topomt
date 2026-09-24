import re
from typing import Iterable


def sort_feature_ids(feature_ids: Iterable[str]) -> list[str]:
    """Return a list of feature IDs sorted numerically by their index.

    This function correctly orders strings like 'POC-1', 'POC-10', 'POC-2',
    or mixed types like 'VOI-3', 'CHA-101', etc.

    Parameters
    ----------
    feature_ids : iterable of str
        Feature identifiers (e.g., ['POC-1', 'POC-10', 'POC-2']).

    Returns
    -------
    list of str
        Sorted list of feature identifiers according to their numeric index.

    Notes
    -----
    - Sorting is performed within each prefix (e.g., 'POC', 'VOI', 'CHA').
    - The numeric component is extracted using a regular expression.
    - Strings without a numeric component are sorted alphabetically at the end.

    Examples
    --------
    >>> sort_feature_ids(['POC-10', 'POC-2', 'POC-1'])
    ['POC-1', 'POC-2', 'POC-10']

    >>> sort_feature_ids(['VOI-3', 'POC-2', 'POC-10', 'CHA-1'])
    ['CHA-1', 'POC-2', 'POC-10', 'VOI-3']
    """

    def sort_key(fid: str):
        # Extrae prefijo (no dígitos) y número (dígitos)
        match = re.match(r'([A-Za-z_]+)[^\d]*(\d+)?', fid)
        if not match:
            return ('', float('inf'))
        prefix, num = match.groups()
        index = int(num) if num is not None else float('inf')
        return (prefix, index)

    return sorted(feature_ids, key=sort_key)
