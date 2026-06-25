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


def show_features(
    view,
    topography=None,
    *,
    feature_types=None,
    styles=None,
    tag_prefix: str = 'topomt-feature',
    **kwargs: Any,
):
    """Render TopoMT features by catalog ``feature_type``, each with a default grounded
    representation, delegating to ``show_dfnd_components``.

    Parameters
    ----------
    feature_types : iterable of str, optional
        Restrict to these feature types (default: all renderable wet types).
    styles : dict of str to str, optional
        Per-feature-type representation override, e.g.
        ``{'groove': 'groove_walls', 'channel': 'channel_lumen'}`` -- the way a feature
        type's richer style vocabulary is reached.
    tag_prefix : str
        Layer tag prefix; each representation group renders under its own tag.

    Returns the list of per-group render results.
    """
    topography = _resolve_topography(view, topography)
    if topography is None:
        raise ValueError('topography is required')

    styles = dict(styles or {})
    selected = None if feature_types is None else set(feature_types)

    # group each feature's component by the representation it should render with
    groups: dict[str, list[str]] = {}
    for feature in topography.values():
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

    results = []
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
        results.append(result)
    return results
