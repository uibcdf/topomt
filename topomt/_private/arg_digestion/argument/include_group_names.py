from topomt._private.smonitor import ArgumentError


def digest_include_group_names(include_group_names, caller=None):
    if include_group_names is None:
        return None

    if isinstance(include_group_names, (list, tuple, set)) and all(
        isinstance(item, str) for item in include_group_names
    ):
        return list(include_group_names)

    raise ArgumentError(
        arg_name='include_group_names',
        value=include_group_names,
        caller=caller,
        reason='include_group_names must be None or a collection of strings.',
    )
