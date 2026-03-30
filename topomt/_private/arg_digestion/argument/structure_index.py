from .structure_indices import digest_structure_indices


def digest_structure_index(structure_index, caller=None):
    """Digest the deprecated alias `structure_index` using the canonical rule."""

    if structure_index is None:
        return None

    return digest_structure_indices(structure_index, caller=caller)
