"""Addon definition for the TopoMT MolSysViewer integration."""

from .runtime import ensure_runtime, record_event


def on_enable(view) -> None:
    runtime = ensure_runtime(view)
    runtime.enabled = True
    record_event(view, "enable", workspace=runtime.workspace)


def on_disable(view) -> None:
    runtime = ensure_runtime(view)
    runtime.enabled = False
    record_event(view, "disable", workspace=runtime.workspace)


def on_context_action(view, action_id: str, payload: dict) -> None:
    runtime = ensure_runtime(view)
    runtime.last_context_action = {"action_id": action_id, "payload": dict(payload)}
    record_event(view, "context_action", action_id=action_id)


_addon_instance = None
_lifecycle_instance = None


def get_lifecycle():
    global _lifecycle_instance
    if _lifecycle_instance is not None:
        return _lifecycle_instance

    from molsysviewer.addons import AddonLifecycleSpec

    _lifecycle_instance = AddonLifecycleSpec(
        on_enable=on_enable,
        on_disable=on_disable,
        on_context_action=on_context_action,
    )
    return _lifecycle_instance


def get_addon():
    global _addon_instance
    if _addon_instance is not None:
        return _addon_instance

    from molsysviewer.addons import (
        AddonContextActionSpec,
        AddonExportHelperSpec,
        AddonPanelSpec,
        AddonShapeProviderSpec,
        AddonSpec,
        AddonWorkspaceSpec,
        AddonWorkbenchSectionSpec,
    )

    _addon_instance = AddonSpec(
        name="topomt",
        package="molsysviewer-topomt",
        version="0.1.0",
        description="TopoMT workspace for pocket and topography analysis in MolSysViewer.",
        workspaces=(
            AddonWorkspaceSpec(
                id="topomt",
                title="TopoMT",
                entry_panel="topography",
                description="Topography-focused workspace for pocket analysis workflows.",
                order=20,
            ),
        ),
        panels=(
            AddonPanelSpec(
                id="topography",
                title="Topography",
                entry="molsysviewer_topomt.panels.topography_panel",
                description="Summary panel with pocket render controls.",
                order=10,
                widget_class="molsysviewer_topomt.panels.topography.TopoMTTopographyPanel",
            ),
            AddonPanelSpec(
                id="pockets",
                title="Pockets",
                entry="molsysviewer_topomt.panels.pockets_panel",
                description="Per-pocket list with individual show/hide controls.",
                order=20,
                widget_class="molsysviewer_topomt.panels.pockets.TopoMTPocketsPanel",
            ),
        ),
        context_actions=(
            AddonContextActionSpec(
                id="focus-topography-feature",
                title="Focus Topography Feature",
                entry="molsysviewer_topomt.context.focus_topography_feature",
                target_kinds=("structure", "shape"),
                group="topography",
                order=10,
            ),
        ),
        workbench_sections=(
            AddonWorkbenchSectionSpec(
                id="topography-summary",
                title="Topography Summary",
                entry="molsysviewer_topomt.workbench.topography_summary",
                target_panel="workbench",
                order=10,
            ),
        ),
        shape_providers=(
            AddonShapeProviderSpec(
                id="topography-pocket-blob",
                title="TopoMT Pocket Blob",
                entry="molsysviewer_topomt.shapes.pocket_blob_provider",
                kinds=("pocket", "blob", "surface"),
                order=10,
            ),
        ),
        export_helpers=(
            AddonExportHelperSpec(
                id="topography-summary-export",
                title="TopoMT Summary Export",
                entry="molsysviewer_topomt.exports.export_topography_summary",
                formats=("json", "html"),
                order=10,
            ),
        ),
        meta={
            "domain": "topography",
            "checkpoint": True,
            "rendering_ready": True,
        },
    )
    return _addon_instance


def __getattr__(name: str):
    if name == "addon" or name == "ADDON":
        return get_addon()
    if name == "lifecycle":
        return get_lifecycle()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
