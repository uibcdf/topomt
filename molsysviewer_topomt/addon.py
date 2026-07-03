"""Addon definition for the TopoMT MolSysViewer integration."""

from .index_spaces import MOLECULAR_SYSTEM
from .index_spaces import atom_indices as indices_in_space
from .runtime import ensure_runtime, record_event
from .simplex_selection import ACTION_ID as _SIMPLEX_ACTION_ID


def on_enable(view) -> None:
    runtime = ensure_runtime(view)
    runtime.enabled = True
    record_event(view, 'enable', workspace=runtime.workspace)


def on_disable(view) -> None:
    runtime = ensure_runtime(view)
    runtime.enabled = False
    record_event(view, 'disable', workspace=runtime.workspace)


def on_context_action(view, action_id: str, payload: dict) -> None:
    runtime = ensure_runtime(view)
    runtime.last_context_action = {'action_id': action_id, 'payload': dict(payload)}
    record_event(view, 'context_action', action_id=action_id)

    if action_id == 'dfnd-tetrahedron-info':
        from .context import inspect_dfnd_tetrahedra

        inspect_dfnd_tetrahedra(view, payload)

    elif action_id == _SIMPLEX_ACTION_ID:
        # Dynamic-item clicks carry the resolved simplex under addon_action_payload.
        simplex = payload.get('addon_action_payload') or {}
        _handle_simplex_selection(view, runtime, dict(simplex))


def on_active_selection_changed(view, selection):
    """Push hook: map the current atom selection to DFND simplices and return the
    context-menu items the host should show (under the add-on's section). Also
    populates ``runtime.active_simplex_selection`` when the selection IS exactly an
    edge/face/tetrahedron, so direct shape clicks are inspectable too (not only
    menu-driven selections)."""
    from .simplex_selection import resolve_simplices

    runtime = ensure_runtime(view)
    topo = getattr(runtime, 'topography', None)
    if topo is None or getattr(topo, 'dfnd', None) is None:
        return []
    selection = selection or {}
    if selection.get('atom_index_space', MOLECULAR_SYSTEM) != MOLECULAR_SYSTEM:
        return []
    atom_indices = indices_in_space(
        selection.get('atom_indices'), space=MOLECULAR_SYSTEM
    )
    try:
        items = resolve_simplices(topo, atom_indices)
    except Exception:
        items = []

    # Inspect API: remember the unique exact simplex if there is one; clear when
    # the selection no longer forms a single simplex.
    exact = next(
        (
            item['payload']
            for item in items
            if item.get('payload', {}).get('kind') in ('edge', 'face', 'tetrahedron')
        ),
        None,
    )
    runtime.active_simplex_selection = dict(exact) if exact else None
    return items


def _handle_simplex_selection(view, runtime, payload):
    """Select the simplex's atoms in the *native* active selection (so it highlights
    exactly like clicking that simplex) and remember it for inspection."""
    # Remember the resolved simplex so the inspection API can report it.
    runtime.active_simplex_selection = dict(payload)

    if payload.get('atom_index_space', MOLECULAR_SYSTEM) != MOLECULAR_SYSTEM:
        raise ValueError('DFND simplex payloads must use molecular_system atom indices')
    atoms = indices_in_space(payload.get('atom_indices'), space=MOLECULAR_SYSTEM)
    if not atoms:
        return

    # The op expects frontend-local atom indices; remap when the view does.
    local = atoms
    mapper = getattr(view, '_index_mapper', None)
    if mapper is not None:
        try:
            local = list(mapper.to_local_atoms(atoms))
        except Exception:
            local = atoms

    try:
        view._send({'op': 'set_active_selection', 'atom_indices': list(local)})
        view._last_active_selection_event = {
            'event': 'interaction_active_selection_changed',
            'source_kind': 'element',
            'element_level': 'atom',
            'target_level': 'none',
            'items': [],
            'atom_indices': list(atoms),
            'atom_index_space': MOLECULAR_SYSTEM,
            'group_indices': [],
            'component_indices': [],
            'chain_indices': [],
            'molecule_indices': [],
            'entity_indices': [],
            'count_atoms': len(atoms),
            'count_groups': 0,
            'count_shapes': 0,
            'count_annotations': 0,
        }
    except Exception:
        pass


_addon_instance = None
_lifecycle_instance = None


def _accepts_keyword(callable_obj, keyword: str) -> bool:
    import inspect

    try:
        return keyword in inspect.signature(callable_obj).parameters
    except (TypeError, ValueError):
        return False


def get_lifecycle():
    global _lifecycle_instance
    if _lifecycle_instance is not None:
        return _lifecycle_instance

    from molsysviewer.addons import AddonLifecycleSpec

    kwargs = {
        'on_enable': on_enable,
        'on_disable': on_disable,
        'on_context_action': on_context_action,
    }
    if _accepts_keyword(AddonLifecycleSpec, 'on_active_selection_changed'):
        kwargs['on_active_selection_changed'] = on_active_selection_changed

    _lifecycle_instance = AddonLifecycleSpec(**kwargs)
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
        AddonSectionSpec,
        AddonWorkspaceSpec,
    )

    from .runtime import create_topomt_state

    addon_kwargs = {
        'name': 'topomt',
        'package': 'molsysviewer-topomt',
        'version': '0.1.0',
        'description': 'TopoMT workspace for pocket and topography analysis in MolSysViewer.',
    }
    if _accepts_keyword(AddonSpec, 'state_factory'):
        addon_kwargs['state_factory'] = create_topomt_state

    _addon_instance = AddonSpec(
        **addon_kwargs,
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
                description='Summary panel with pocket render controls.',
                order=10,
                widget_class='molsysviewer_topomt.panels.topography.TopoMTTopographyPanel',
            ),
            AddonPanelSpec(
                id='pockets',
                title='Pockets',
                entry='molsysviewer_topomt.panels.pockets_panel',
                description='Per-pocket list with individual show/hide controls.',
                order=20,
                widget_class='molsysviewer_topomt.panels.pockets.TopoMTPocketsPanel',
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
            AddonContextActionSpec(
                id='dfnd-tetrahedron-info',
                title='Ficha de diagnóstico (consola)',
                entry='molsysviewer_topomt.context.inspect_dfnd_tetrahedra',
                target_kinds=('shape',),
                group='topography',
                order=20,
            ),
        ),
        addon_sections=(
            AddonSectionSpec(
                id='topography-summary',
                title='Topography Summary',
                entry='molsysviewer_topomt.workbench.topography_summary',
                target_panel='addons',
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
            'rendering_ready': True,
        },
    )
    return _addon_instance


def __getattr__(name: str):
    if name == 'addon' or name == 'ADDON':
        return get_addon()
    if name == 'lifecycle':
        return get_lifecycle()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
