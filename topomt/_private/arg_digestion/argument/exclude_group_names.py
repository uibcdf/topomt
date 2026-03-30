from topomt._private.smonitor import ArgumentError


def digest_exclude_group_names(exclude_group_names, caller=None):
    if exclude_group_names is None:
        return None

    if isinstance(exclude_group_names, (list, tuple, set)) and all(
        isinstance(item, str) for item in exclude_group_names
    ):
        return list(exclude_group_names)

    raise ArgumentError(
        arg_name='exclude_group_names',
        value=exclude_group_names,
        caller=caller,
        reason='exclude_group_names must be None or a collection of strings.',
    )
