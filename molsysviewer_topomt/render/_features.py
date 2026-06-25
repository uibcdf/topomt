"""show_features: the feature-layer renderer.

Dispatch each TopoMT feature by its catalog ``feature_type`` to a sensible default
grounded representation, delegating to the component renderer. The named feature layer
*composes* the grounded primitives; it carries no geometry of its own (see
devguide/DFND/viewer_grounded_named_split.md). Per-feature-type style overrides expose
each type's richer vocabulary (e.g. a groove as walls / width_profile).
"""

from typing import Any

from ._common import _resolve_topography
from ._components import show_dfnd_components
from .result import RenderResult, clear_previous_render_result, remember_render_result

# feature_type -> default grounded representation (a component-renderer primitive). A
# 1-mouth concavity (pocket / open_concavity / groove) reads as a volumetric envelope;
# a through passage (channel) as a tube; a fully exposed region as a cloud. Names live
# only in this table; the representations it maps to are grounded.
_DEFAULT_REPRESENTATION_BY_FEATURE_TYPE = {
    'void': 'envelope',
    'pocket': 'envelope',
    'open_concavity': 'envelope',
    'groove': 'envelope',
    'channel': 'tube',
    'branched_channel': 'tube',
    'percolating': 'cloud',
}


def _feature_operation_key(tag_prefix: str) -> str:
    return f'features:{tag_prefix}'


def _feature_result(view, tag_prefix: str):
    registry = getattr(view, '_topomt_render_results', None)
    if not isinstance(registry, dict):
        return None
    result = registry.get(_feature_operation_key(tag_prefix))
    return result if isinstance(result, RenderResult) else None


def _call_layer_method(result: RenderResult | None, method_name: str) -> bool:
    if result is None:
        return False
    called = False
    for layer in result.layers:
        method = getattr(layer, method_name, None)
        if method is None:
            continue
        method(skip_digestion=True)
        called = True
    return called


def _representation_result(view, tag_prefix: str, representation: str):
    """The per-representation render unit (its own RenderResult), or ``None``."""
    aggregate = _feature_result(view, tag_prefix)
    if aggregate is None:
        return None
    return aggregate.details.get('by_representation', {}).get(representation)


def clear_feature_representations(
    view, *, tag_prefix: str = 'topomt-feature', representation: str | None = None
) -> bool:
    """Delete the feature-render group created by ``show_features``.

    Addressed by the logical ``tag_prefix``; by default all representation views under
    that call are removed together. Pass ``representation`` to delete only that one
    representation's view.
    """
    if representation is not None:
        key = f'components:{tag_prefix}:{representation}'
        return clear_previous_render_result(view, key) is not None
    return clear_previous_render_result(view, _feature_operation_key(tag_prefix)) is not None


def hide_feature_representations(
    view, *, tag_prefix: str = 'topomt-feature', representation: str | None = None
) -> bool:
    """Hide the ``show_features`` group (or a single ``representation`` view) without
    deleting it."""
    if representation is not None:
        return _call_layer_method(
            _representation_result(view, tag_prefix, representation), 'hide'
        )
    return _call_layer_method(_feature_result(view, tag_prefix), 'hide')


def show_feature_representations(
    view, *, tag_prefix: str = 'topomt-feature', representation: str | None = None
) -> bool:
    """Show a previously hidden ``show_features`` group (or a single ``representation``
    view)."""
    if representation is not None:
        return _call_layer_method(
            _representation_result(view, tag_prefix, representation), 'show'
        )
    return _call_layer_method(_feature_result(view, tag_prefix), 'show')


def show_features(
    view,
    topography=None,
    *,
    feature_types=None,
    styles=None,
    tag_prefix: str = 'topomt-feature',
    replace: bool = True,
    **kwargs: Any,
):
    """Render TopoMT features by catalog ``feature_type``.

    Each feature type is mapped to a default grounded representation and delegated to
    ``show_dfnd_components``. By default, a new call replaces the previous
    ``show_features`` group with the same ``tag_prefix`` so notebooks do not accumulate
    stale styles. Pass ``replace=False`` and/or a different ``tag_prefix`` to compare
    multiple feature representations side by side.

    Parameters
    ----------
    feature_types : iterable of str, optional
        Restrict to these feature types (default: all renderable wet types).
    styles : dict of str to str, optional
        Per-feature-type representation override, e.g.
        ``{'groove': 'groove_walls', 'channel': 'channel_lumen'}`` -- the way a feature
        type's richer style vocabulary is reached.
    tag_prefix : str
        Logical feature-render group prefix.
    replace : bool, default True
        If True, delete the previous feature-render group with this ``tag_prefix``
        before drawing the new one.

    Returns
    -------
    RenderResult
        Aggregate result for all representation groups emitted by this call.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')

    if replace:
        clear_previous_render_result(view, _feature_operation_key(tag_prefix))

    styles = dict(styles or {})
    selected = None if feature_types is None else set(feature_types)

    groups: dict[str, list[str]] = {}
    selected_feature_ids = []
    selected_component_ids = []
    for feature_id in topography:
        feature = topography[feature_id]
        feature_type = getattr(feature, 'feature_type', None)
        if feature_type not in _DEFAULT_REPRESENTATION_BY_FEATURE_TYPE:
            continue
        if selected is not None and feature_type not in selected:
            continue
        component_id = getattr(feature, 'component_id', None)
        if component_id is None:
            continue
        representation = styles.get(
            feature_type, _DEFAULT_REPRESENTATION_BY_FEATURE_TYPE[feature_type]
        )
        groups.setdefault(representation, []).append(component_id)
        selected_feature_ids.append(feature_id)
        selected_component_ids.append(component_id)

    # Each representation is a clean, self-contained render unit -- its own tag
    # (`{tag_prefix}:{representation}`) and its own RenderResult (a "view per
    # representation"). The aggregate below is the *collection* over them, so each
    # representation can be inspected / hidden / cleared independently (and the
    # group-vs-feature ordering question dissolves -- each unit is coherent).
    by_representation: dict[str, RenderResult] = {}
    for representation, component_ids in groups.items():
        result = show_dfnd_components(
            view,
            topography,
            representation=representation,
            component_ids=component_ids,
            component_types=None,  # select by the explicit component_ids, not the bucket
            tag_prefix=f'{tag_prefix}:{representation}',
            **kwargs,
        )
        if result is not None:
            by_representation[representation] = result

    results = list(by_representation.values())
    layers = tuple(layer for result in results for layer in result.layers)
    tags = tuple(tag for result in results for tag in result.tags)
    rendered_component_set = {
        component_id
        for result in results
        for component_id in result.rendered_ids
    }
    # rendered_ids in FEATURE order (selected_component_ids), not group order
    rendered_ids = tuple(
        component_id
        for component_id in selected_component_ids
        if component_id in rendered_component_set
    )
    aggregate = RenderResult(
        representation='features',
        selected_ids=tuple(selected_feature_ids),
        rendered_ids=rendered_ids,
        layers=layers,
        tags=tags,
        counts={
            'n_groups': len(results),
            'n_components': len(selected_component_ids),
        },
        details={
            'component_ids': tuple(selected_component_ids),
            'groups': tuple(by_representation),
            'by_representation': by_representation,
            'results': tuple(results),
        },
    )
    return remember_render_result(view, _feature_operation_key(tag_prefix), aggregate)
