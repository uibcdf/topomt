"""Regression tests for the public topography dispatcher."""

import pytest

from topomt import get_topography


def test_get_topography_unknown_method_lists_supported_aliases():

    with pytest.raises(ValueError) as exc_info:
        get_topography(None, method='not-a-method', skip_digestion=True)

    message = str(exc_info.value)
    assert "'fpocket4'" in message
    assert "'castp3'" in message
