"""Runtime state for the TopoMT MolSysViewer addon."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TopoMTAddonRuntime:
    """Public per-view state namespace for the TopoMT add-on.

    Exposed as ``view.addons.topomt`` (lazy, one instance per view). Holds
    everything the add-on adds to a view: the attached topography, the currently
    active DFND simplex selection, etc. Older code may still read it as
    ``view._topomt_addon_runtime``; it is the *same* object.
    """

    enabled: bool = False
    workspace: str = 'topomt'
    topography: Any = None
    active_feature_ids: tuple[str, ...] | None = None
    render_groups: dict[str, dict[str, Any]] = field(default_factory=dict)
    tag_prefix: str = 'topomt-pocket'
    last_context_action: Any = None
    active_simplex_selection: Any = None
    event_log: list = field(default_factory=list)


def create_topomt_state(view: Any) -> TopoMTAddonRuntime:
    """Factory consumed by ``AddonSpec.state_factory``. Also keeps the legacy
    ``view._topomt_addon_runtime`` attribute pointing at the same instance for
    backward compatibility."""
    state = TopoMTAddonRuntime()
    try:
        view._topomt_addon_runtime = state
    except Exception:
        pass
    return state


def ensure_runtime(view: Any) -> TopoMTAddonRuntime:
    """Return the TopoMT state namespace for ``view``. Prefers the public
    ``view.addons.topomt`` namespace when the add-on is registered (lazy via the
    ``state_factory``); falls back to a legacy ``view._topomt_addon_runtime``
    attribute so test doubles without an addons manager still work."""
    addons = getattr(view, 'addons', None)
    if addons is not None:
        try:
            namespace = getattr(addons, 'topomt', None)
        except Exception:
            namespace = None
        if isinstance(namespace, TopoMTAddonRuntime):
            try:
                view._topomt_addon_runtime = namespace
            except Exception:
                pass
            return namespace

    runtime = getattr(view, '_topomt_addon_runtime', None)
    if not isinstance(runtime, TopoMTAddonRuntime):
        runtime = TopoMTAddonRuntime()
        try:
            view._topomt_addon_runtime = runtime
        except Exception:
            pass
    return runtime


def record_event(view: Any, event_name: str, **kwargs: Any) -> None:
    runtime = ensure_runtime(view)
    runtime.event_log.append({'event': event_name, **kwargs})
