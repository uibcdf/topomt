"""Project-level argument name standardization for ArgDigest."""


def argument_names_standardization(caller, kwargs):
    """Normalize backward-compatible or user-friendly argument aliases."""

    alias_map = {
        'engine': 'method',
        'structure_index': 'structure_indices',
    }

    for old_key, new_key in alias_map.items():
        if old_key in kwargs and new_key not in kwargs:
            kwargs = _replace_key_in_dict(kwargs, old_key, new_key)

    return kwargs


def _replace_key_in_dict(dictionary, old_key, new_key):
    output = {}
    for key in dictionary:
        if key == old_key:
            output[new_key] = dictionary[key]
        else:
            output[key] = dictionary[key]
    return output
