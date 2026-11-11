"""Preserve observable registry/query behavior while refining its types."""

from collections.abc import Mapping

import numpy as np
import pytest

from topomt import Topography
from topomt.features import Feature0D, Mouth, Percolating, Pocket


@pytest.fixture
def registry():
    return Topography(
        features=[
            Pocket(feature_id='POC-1'),
            Mouth(feature_id='MOU-1'),
            Percolating(feature_id='PRC-1'),
            Feature0D(feature_id='F0D-1', feature_type='point'),
        ]
    )


@pytest.mark.parametrize(
    'by,value,expected',
    [
        (None, None, {'POC-1', 'MOU-1', 'PRC-1', 'F0D-1'}),
        ('id', 'POC-1', {'POC-1'}),
        ('id', ['POC-1', 'missing', 'PRC-1'], {'POC-1', 'PRC-1'}),
        ('id', ('MOU-1', 'MOU-1'), {'MOU-1'}),
        ('id', {'PRC-1'}, {'PRC-1'}),
        ('id', None, set()),
        ('type', 'pocket', {'POC-1'}),
        ('shape', 'neutral', {'PRC-1'}),
        ('dimensionality', 0, {'F0D-1'}),
        ('dimensionality', 2, {'POC-1', 'PRC-1'}),
        ('dimensionality', np.int64(2), {'POC-1', 'PRC-1'}),
        ('dimensionality', 2.0, {'POC-1', 'PRC-1'}),
        ('dimensionality', True, {'MOU-1'}),
        ('dimensionality', '2', set()),
        ('type', 'missing', set()),
        ('shape', 'missing', set()),
    ],
)
def test_filters_keep_mapping_identity_and_set_results(registry, by, value, expected):
    assert isinstance(registry, Mapping)
    assert dict(registry) == registry.features
    assert registry.get_features(by=by, value=value, as_feature_ids=True) == expected
    matches = registry.get_features(by=by, value=value)
    assert type(matches) is set
    assert matches == {registry[key] for key in expected}
    assert all(feature is registry[feature.feature_id] for feature in matches)


@pytest.mark.parametrize('grouped_by', ['type', 'shape', 'dimensionality'])
def test_grouped_queries_return_independent_sets_with_original_keys(
    registry, grouped_by
):
    groups = registry.get_features(grouped_by=grouped_by)
    identifiers = registry.get_features(grouped_by=grouped_by, as_feature_ids=True)
    for key, members in groups.items():
        assert type(key) is (int if grouped_by == 'dimensionality' else str)
        assert type(members) is set
        assert type(identifiers[key]) is set
        assert {feature.feature_id for feature in members} == identifiers[key]
    assert set().union(*identifiers.values()) == set(registry)
    for members in identifiers.values():
        members.clear()
    assert len(registry) == 4
    assert registry.get_features(by='type', value='pocket', as_feature_ids=True) == {
        'POC-1'
    }


def test_info_preserves_integer_counts_and_dimensionality_keys(registry):
    assert registry.info() == {
        'by_type': {'pocket': 1, 'mouth': 1, 'percolating': 1, 'point': 1},
        'by_shape': {
            'concavity': 1,
            'convexity': 0,
            'mixed': 0,
            'boundary': 1,
            'point': 1,
            'neutral': 1,
        },
        'by_dimensionality': {0: 1, 1: 1, 2: 2},
        'total': 4,
    }


@pytest.mark.parametrize('by', ['type', 'shape', 'dimensionality'])
def test_unhashable_filter_values_retain_their_type_error(registry, by):
    with pytest.raises(TypeError, match='unhashable'):
        registry.get_features(by=by, value=[])


def test_empty_and_invalid_query_behavior_is_preserved(registry):
    empty = Topography()
    assert empty.get_features() == set()
    assert empty.get_features(grouped_by='type') == {}
    assert empty.get_features(grouped_by='unknown') == {}
    assert empty.info()['by_dimensionality'] == {0: 0, 1: 0, 2: 0}
    assert empty.info()['total'] == 0
    with pytest.raises(ValueError, match="Unknown 'grouped_by'"):
        registry.get_features(grouped_by='unknown')
    with pytest.raises(ValueError, match="Unknown 'by'"):
        registry.get_features(by='unknown')
