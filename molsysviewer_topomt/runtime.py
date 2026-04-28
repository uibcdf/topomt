"""Runtime state for the TopoMT MolSysViewer addon."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TopoMTAddonRuntime:
    enabled: bool = False
    workspace: str = "topomt"
    topography: Any = None
    tag_prefix: str = "topomt-pocket"
    last_context_action: Any = None
    event_log: list = field(default_factory=list)


def ensure_runtime(view: Any) -> TopoMTAddonRuntime:
    runtime = getattr(view, "_topomt_addon_runtime", None)
    if not isinstance(runtime, TopoMTAddonRuntime):
        runtime = TopoMTAddonRuntime()
        view._topomt_addon_runtime = runtime
    return runtime


def record_event(view: Any, event_name: str, **kwargs: Any) -> None:
    runtime = ensure_runtime(view)
    runtime.event_log.append({"event": event_name, **kwargs})
