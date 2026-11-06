"""Strict JSON decoding shared by original-provider saved-result readers."""

import json
from typing import Any, NoReturn


def read_json(data: bytes, *, provider: str) -> Any:
    """Reject duplicate keys and nonfinite constants without altering raw bytes."""

    def invalid(field: str) -> NoReturn:
        raise ValueError(f'Invalid {provider} saved output: {field}.')

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                invalid(f'duplicate JSON key {key}')
            result[key] = value
        return result

    def constant(value):
        invalid(f'nonfinite JSON constant {value}')

    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f'Invalid {provider} saved JSON.') from error
