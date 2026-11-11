"""Positive public-call examples checked by the bounded mypy configuration."""

from collections.abc import Iterator, Mapping
from typing import assert_type

from topomt.features.BaseFeature import BaseFeature, ShapeType
from topomt.topography.Topography import Topography


def public_queries(topo: Topography, grouping: str | None, identifiers: bool) -> None:
    mapping: Mapping[str, BaseFeature] = topo
    assert_type(mapping['POC-1'], BaseFeature)
    assert_type(topo['POC-1'], BaseFeature)
    assert_type(iter(topo), Iterator[str])
    assert_type(topo.copy(), Topography)
    assert_type(topo.features, dict[str, BaseFeature])

    assert_type(topo.get_features(), set[BaseFeature])
    assert_type(topo.get_features(by='id', value=['POC-1']), set[BaseFeature])
    assert_type(topo.get_features(by='type', value='void'), set[BaseFeature])
    assert_type(topo.get_features(by='dimensionality', value=2), set[BaseFeature])
    assert_type(topo.get_features(as_feature_ids=True), set[str])
    assert_type(topo.get_features(grouped_by='type'), dict[str | int, set[BaseFeature]])
    assert_type(
        topo.get_features(grouped_by='dimensionality', as_feature_ids=True),
        dict[str | int, set[str]],
    )
    assert_type(
        topo.get_features(grouped_by=grouping, as_feature_ids=identifiers),
        set[BaseFeature]
        | set[str]
        | dict[str | int, set[BaseFeature]]
        | dict[str | int, set[str]],
    )

    counts = topo.info()
    assert_type(counts['total'], int)
    assert_type(counts['by_type'], dict[str, int])
    assert_type(counts['by_shape'], dict[ShapeType, int])
    assert_type(counts['by_dimensionality'], dict[int, int])
    assert_type(counts['by_dimensionality'].get(2, 0), int)
