"""Addon definition for the first MolSysViewer-TopoMT integration slice."""

from molsysviewer import (
    AddonContextActionSpec,
    AddonExportHelperSpec,
    AddonLifecycleSpec,
    AddonPanelSpec,
    AddonShapeProviderSpec,
    AddonSpec,
    AddonWorkbenchSectionSpec,
    AddonWorkspaceSpec,
)


def on_enable(view) -> None:
    """Attach minimal runtime state to a view when the addon becomes active."""
    runtime = getattr(view, '_topomt_addon_runtime', None)
    if not isinstance(runtime, dict):
        runtime = {}
    runtime.update(
        {
            'enabled': True,
            'workspace': 'topomt',
            'entry_panel': 'topography',
            'panels': ['topography', 'pockets'],
            'workbench_sections': ['topography-summary'],
            'shape_providers': ['topography-pocket-blob'],
            'export_helpers': ['topography-summary-export'],
            'last_context_action': None,
        }
    )
    view._topomt_addon_runtime = runtime


def on_disable(view) -> None:
    """Mark the runtime snapshot as disabled without deleting the history."""
    runtime = getattr(view, '_topomt_addon_runtime', None)
    if isinstance(runtime, dict):
        runtime['enabled'] = False


def on_context_action(view, action_id: str, payload: dict) -> None:
    """Store the last Python-side action until real view operations exist."""
    runtime = getattr(view, '_topomt_addon_runtime', None)
    if not isinstance(runtime, dict):
        runtime = {}
        view._topomt_addon_runtime = runtime
    runtime['last_context_action'] = {
        'action_id': action_id,
        'payload': dict(payload),
    }


lifecycle = AddonLifecycleSpec(
    on_enable=on_enable,
    on_disable=on_disable,
    on_context_action=on_context_action,
)


addon = AddonSpec(
    name='topomt',
    package='molsysviewer-topomt',
    version='0.1.0',
    description='TopoMT workspace scaffold for MolSysViewer.',
    workspaces=(
        AddonWorkspaceSpec(
            id='topomt',
            title='TopoMT',
            entry_panel='topography',
            description='Topography-focused workspace for pocket analysis workflows.',
            order=20,
        ),
    ),
    panels=(
        AddonPanelSpec(
            id='topography',
            title='Topography',
            entry='molsysviewer_topomt.panels.topography_panel',
            description='Checkpoint panel for TopoMT workspace integration.',
            order=10,
        ),
        AddonPanelSpec(
            id='pockets',
            title='Pockets',
            entry='molsysviewer_topomt.panels.pockets_panel',
            description='Pocket-oriented panel placeholder for the first addon slice.',
            order=20,
        ),
    ),
    context_actions=(
        AddonContextActionSpec(
            id='focus-topography-feature',
            title='Focus Topography Feature',
            entry='molsysviewer_topomt.context.focus_topography_feature',
            target_kinds=('structure', 'shape'),
            group='topography',
            order=10,
        ),
    ),
    workbench_sections=(
        AddonWorkbenchSectionSpec(
            id='topography-summary',
            title='Topography Summary',
            entry='molsysviewer_topomt.workbench.topography_summary',
            target_panel='workbench',
            order=10,
        ),
    ),
    shape_providers=(
        AddonShapeProviderSpec(
            id='topography-pocket-blob',
            title='TopoMT Pocket Blob',
            entry='molsysviewer_topomt.shapes.pocket_blob_provider',
            kinds=('pocket', 'blob', 'surface'),
            order=10,
        ),
    ),
    export_helpers=(
        AddonExportHelperSpec(
            id='topography-summary-export',
            title='TopoMT Summary Export',
            entry='molsysviewer_topomt.exports.export_topography_summary',
            formats=('json', 'html'),
            order=10,
        ),
    ),
    meta={
        'domain': 'topography',
        'checkpoint': True,
        'rendering_ready': False,
    },
)

ADDON = addon


def get_addon() -> AddonSpec:
    """Return the add-on spec expected by MolSysViewer."""
    return addon
