"""Shared state-refresh protocol for the TopoMT-owned panel widgets."""

from typing import Any

from molsysviewer.addons import AddonPanelWidget

from ..runtime import ensure_runtime


class TopoMTPanelWidget(AddonPanelWidget):
    """Refresh after the frontend mounts and while attached results change."""

    def __init__(self, view: Any = None, **kwargs: Any) -> None:
        super().__init__(view=view, **kwargs)
        self.on_msg(self._route_topomt_query)

    def _route_topomt_query(self, widget: Any, content: Any, buffers: Any) -> None:
        if (
            isinstance(content, dict)
            and content.get('type') == 'query'
            and content.get('id') == 'topomt.state'
        ):
            self.on_mount(self._view)

    def on_mount(self, view: Any) -> None:
        ensure_runtime(view).panel_widgets.add(self)

    def on_unmount(self, view: Any) -> None:
        ensure_runtime(view).panel_widgets.discard(self)
