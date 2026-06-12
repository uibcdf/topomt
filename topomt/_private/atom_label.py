import re
from pathlib import Path
from typing import Pattern, Any

def format_to_regex(format: str) -> Pattern[str]:
    """Convert a format-string-like template into a regex with named groups.

    Example
    -------
    "atom_id:{atom_id} / group_id={group_id}"
    → r"^atom_id:(?P<atom_id>.+?)\ / group_id=(?P<group_id>.+?)$"
    """
    parts: list[str] = []
    i = 0
    while i < len(format):
        if format[i] == "{":
            j = format.index("}", i)
            field_name = format[i+1:j].strip()
            # grupo no codicioso con nombre
            parts.append(f"(?P<{field_name}>.+?)")
            i = j + 1
        else:
            parts.append(re.escape(format[i]))
            i += 1
    regex = "^" + "".join(parts) + "$"
    return re.compile(regex)


def atom_label_from_format(format: str, context: dict[str, Any]) -> str:
    """Render a string from a template like '{atom_id}-{atom_name}'."""
    return format.format(**context)

def parse_atom_label(atom_label: str, format: str) -> dict[str, str]:
    """Parse a string using the given template and return the captured fields."""
    pattern = format_to_regex(format)
    m = pattern.match(atom_label)
    if not m:
        raise ValueError(
            f'String {atom_label!r} does not match template {format!r}'
        )
    return m.groupdict()

def parse_list_of_atom_labels(list_of_atom_labels: list[str], format: str, output_type: str = 'list of dicts'):
    """Parse many strings with the same template.

    Parameters
    ----------
    list_of_atom_labels : list[str]
        List of strings to parse.
    format : str
        Template describing the structure of each atom label.
    output_type : str, optional
        Type of output. Options:
        - 'list of dicts' (default): returns a list of dictionaries (one per atom label).
        - 'dict of lists'          : returns a dictionary where each key is a field and values are lists.

    Returns
    -------
    dict[str, list[str]] | list[dict[str, str]]
    """
    pattern = format_to_regex(format)
    results: list[dict[str, str]] = []

    for atom_label in list_of_atom_labels:
        m = pattern.match(atom_label)
        if not m:
            raise ValueError(f"String {atom_label!r} does not match template {format!r}")
        results.append(m.groupdict())

    if output_type == 'list of dicts':
        return results
    elif output_type == 'dict of lists':
        dict_of_lists: dict[str, list[str]] = {}
        for d in results:
            for key, value in d.items():
                dict_of_lists.setdefault(key, []).append(value)
        return dict_of_lists
    else:
        raise ValueError("output_type must be either 'dict of lists' or 'list of dicts'")

