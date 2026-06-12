"""Regression tests for atom-label parsing helpers."""

import pytest

from topomt._private.atom_label import parse_atom_label


def test_parse_atom_label_reports_invalid_label_and_format():

    with pytest.raises(
        ValueError,
        match=r"String 'CA-10' does not match template 'atom_id:\{atom_id\}'",
    ):
        parse_atom_label('CA-10', 'atom_id:{atom_id}')
