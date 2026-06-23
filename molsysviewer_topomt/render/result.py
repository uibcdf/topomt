"""Common result contract for TopoMT viewer render operations."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any


def _unique(values):
    output = []
    seen = set()
    for value in values:
        marker = id(value)
        if marker not in seen:
            seen.add(marker)
            output.append(value)
    return tuple(output)


def _layer_tag(layer):
    return getattr(layer, 'tag', None)


def _collect_layers(value, output):
    if value is None:
        return
    if isinstance(value, RenderResult):
        output.extend(value.layers)
        return
    if _layer_tag(value) is not None:
        output.append(value)
        return
    if isinstance(value, Mapping):
        for nested in value.values():
            _collect_layers(nested, output)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _collect_layers(nested, output)


@dataclass(frozen=True)
class RenderResult:
    """Uniform, immutable result returned by primary render operations.

    Renderer-specific payloads live in ``details`` and numeric summaries live in
    ``counts``.
    """

    representation: str
    selected_ids: tuple[Any, ...] = ()
    layers: tuple[Any, ...] = ()
    tags: tuple[str, ...] = ()
    counts: Mapping[str, int] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        counts = dict(self.counts)
        counts.setdefault('n_layers', len(self.layers))
        counts.setdefault('n_selected', len(self.selected_ids))
        object.__setattr__(self, 'selected_ids', tuple(self.selected_ids))
        object.__setattr__(self, 'layers', tuple(self.layers))
        object.__setattr__(self, 'tags', tuple(self.tags))
        object.__setattr__(self, 'warnings', tuple(self.warnings))
        object.__setattr__(self, 'counts', MappingProxyType(counts))
        object.__setattr__(self, 'details', MappingProxyType(dict(self.details)))

    @property
    def is_empty(self) -> bool:
        return not self.layers

    def __bool__(self) -> bool:
        return not self.is_empty


def render_result(
    representation: str,
    raw: Any = None,
    *,
    selected_ids=(),
    warnings=(),
) -> RenderResult:
    """Normalize renderer internals into ``RenderResult``."""
    if isinstance(raw, RenderResult):
        return raw

    layers = []
    details = {}
    counts = {}
    if raw is None:
        pass
    elif isinstance(raw, Mapping):
        details = dict(raw)
        counts = {
            key: value
            for key, value in raw.items()
            if key.startswith('n_') and isinstance(value, int)
        }
        _collect_layers(raw, layers)
    else:
        _collect_layers(raw, layers)

    layers = _unique(layers)
    tags = tuple(
        tag for tag in (_layer_tag(layer) for layer in layers) if tag is not None
    )
    return RenderResult(
        representation=representation,
        selected_ids=tuple(selected_ids or ()),
        layers=layers,
        tags=tags,
        counts=counts,
        warnings=tuple(warnings or ()),
        details=details,
    )


def clear_previous_render_result(view, key: str) -> RenderResult | None:
    """Clear the exact tags owned by a previous direct render operation."""
    registry = getattr(view, '_topomt_render_results', None)
    if not isinstance(registry, dict):
        return None
    previous = registry.pop(key, None)
    if not isinstance(previous, RenderResult):
        return None
    scene_objects = getattr(view, '_scene_objects', {})
    for tag in previous.tags:
        if tag in scene_objects:
            view.shapes.clear(tag=tag, skip_digestion=True)
    return previous


def remember_render_result(view, key: str, result: RenderResult) -> RenderResult:
    """Remember one direct render result for exact replacement on the next call."""
    registry = getattr(view, '_topomt_render_results', None)
    if not isinstance(registry, dict):
        registry = {}
        setattr(view, '_topomt_render_results', registry)
    registry[key] = result
    return result
