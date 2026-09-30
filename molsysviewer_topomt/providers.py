"""MolSysViewer adoption of detached, original-provider pocket results."""

import math
from typing import Any

from topomt.third_party.output import PocketGeometry, ProviderOutput, ProviderRecord

from .geometry import EntityRef, SphereGeometry
from .render.adapters import add_sphere_set
from .render.result import (
    RenderResult,
    clear_previous_render_result,
    remember_render_result,
)
from .runtime import _refresh_panels, ensure_runtime, record_event

_REPRESENTATIONS = ('alpha_spheres', 'beta_sites', 'member_atoms', 'lining_atoms')
_COLORS = {
    'fpocket': 0x0072B2,
    'pocketeer': 0xE69F00,
    'alphaspace2': 0x009E73,
    'pycasta': 0xCC79A7,
    'castp': 0xD55E00,
}


def _resolve_output(view: Any, output: ProviderOutput | None) -> ProviderOutput:
    if output is None:
        runtime = ensure_runtime(view)
        output = runtime.provider_outputs.get(runtime.active_provider_run_id or '')
    if not isinstance(output, ProviderOutput):
        raise ValueError('An original ProviderOutput is required; attach one first')
    return output


def _operation_key(output: ProviderOutput, tag_prefix: str) -> str:
    return f'provider_pockets:{tag_prefix}:{output.run.run_id}'


def _geometry(record: ProviderRecord, representation: str) -> PocketGeometry | None:
    available = record.geometries
    kinds = _REPRESENTATIONS if representation == 'auto' else (representation,)
    geometries = [available[kind] for kind in kinds if kind in available]
    return next(
        (geometry for geometry in geometries if geometry.points_nm),
        geometries[0] if geometries else None,
    )


def show_provider_pockets(
    view: Any,
    output: ProviderOutput | None = None,
    *,
    pocket_ids: list[str] | tuple[str, ...] | None = None,
    representation: str = 'auto',
    tag_prefix: str = 'topomt-provider',
    color: int | None = None,
    alpha: float = 0.35,
    point_radius_nm: float = 0.06,
) -> RenderResult:
    """Render declared provider sites or membership, without inferring a region.

    Parameters
    ----------
    view : MolSysView
        Viewer whose molecular coordinates match the source frame, if loaded.
    output : ProviderOutput, optional
        Original result, or the active output attached to this view.
    pocket_ids : list or tuple of str, optional
        Source IDs. None renders all pockets; an empty sequence clears the group.
    representation : str
        ``auto``, ``alpha_spheres``, ``beta_sites``, ``member_atoms`` or
        ``lining_atoms``. Auto uses the first nonempty available representation.
    tag_prefix : str
        Namespace for this run's layers. Different runs coexist.
    color : int, optional
        RGB color; defaults differ by provider.
    alpha : float
        Display opacity between zero and one.
    point_radius_nm : float
        Display-marker radius for point-only geometry; not a provider measure.

    Returns
    -------
    RenderResult
        Source IDs, owned layers and provider/run/geometry definitions. Missing
        geometry is listed in ``details['unavailable_ids']`` and ``warnings``.

    Raises
    ------
    ValueError
        For absent output, unknown pocket IDs or unsupported display settings.

    Examples
    --------
    >>> rendered = show_provider_pockets(view, output)  # doctest: +SKIP
    """
    output = _resolve_output(view, output)
    if representation not in ('auto', *_REPRESENTATIONS):
        raise ValueError(f'Unsupported provider representation: {representation!r}')
    if not tag_prefix or not math.isfinite(alpha) or not 0 <= alpha <= 1:
        raise ValueError('A tag prefix and opacity between zero and one are required')
    if not math.isfinite(point_radius_nm) or point_radius_nm <= 0:
        raise ValueError('Point marker radius must be finite and positive')
    selected = None if pocket_ids is None else set(pocket_ids)
    if selected is not None and any(not isinstance(value, str) for value in selected):
        raise ValueError('Provider pocket IDs must be strings')
    known = {record.source_id for record in output.pockets}
    if selected is not None and not selected <= known:
        raise ValueError(f'Unknown provider pocket IDs: {sorted(selected - known)}')
    records = tuple(
        record
        for record in output.pockets
        if selected is None or record.source_id in selected
    )
    # Validate the request before clearing any existing display.
    key = _operation_key(output, tag_prefix)
    clear_previous_render_result(view, key)
    rendered = []
    unavailable = []
    empty = []
    layers = []
    try:
        for record in records:
            geometry = _geometry(record, representation)
            if geometry is None:
                unavailable.append(record.source_id)
                continue
            if not geometry.points_nm:
                empty.append(record.source_id)
                continue
            point_markers = geometry.radii_nm is None
            radii = (
                (point_radius_nm,) * len(geometry.points_nm)
                if point_markers
                else geometry.radii_nm or ()
            )
            ref = EntityRef(
                kind='provider_pocket',
                entity_id=record.source_id,
                metadata={'provider': output.provider, 'run_id': output.run.run_id},
            )
            spheres = SphereGeometry(
                geometry.points_nm, radii, 'nm', (ref,) * len(geometry.points_nm)
            )
            tag = (
                f'{tag_prefix}:{output.provider}:{output.run.run_id}:{record.source_id}'
            )
            layer = add_sphere_set(
                view,
                spheres,
                tag=tag,
                color_alpha_spheres=_COLORS.get(output.provider, 0x0072B2)
                if color is None
                else color,
                alpha_alpha_spheres=alpha,
            )
            layers.append(layer)
            rendered.append(
                {
                    'provider': output.provider,
                    'run_id': output.run.run_id,
                    'source_id': record.source_id,
                    'geometry_kind': geometry.kind,
                    'definition': geometry.definition,
                    'mode': 'point_markers' if point_markers else 'reported_spheres',
                    'display_point_radius_nm': point_radius_nm
                    if point_markers
                    else None,
                    'atom_role': record.atom_role,
                    'tag': tag,
                }
            )
    except Exception:
        # A partial failed render must not leave orphaned owned layers.
        for layer in layers:
            view.shapes.clear(tag=layer.tag, skip_digestion=True)
        raise
    result = RenderResult(
        representation='provider_pockets',
        selected_ids=tuple(record.source_id for record in records),
        rendered_ids=tuple(item['source_id'] for item in rendered),
        layers=tuple(layers),
        tags=tuple(layer.tag for layer in layers),
        warnings=tuple(
            f'{source_id}: requested geometry unavailable' for source_id in unavailable
        ),
        counts={
            'n_rendered': len(rendered),
            'n_unavailable': len(unavailable),
            'n_empty': len(empty),
        },
        details={
            'rendered': tuple(rendered),
            'unavailable_ids': tuple(unavailable),
            'empty_ids': tuple(empty),
        },
    )
    return remember_render_result(view, key, result)


def clear_provider_pockets(
    view: Any,
    output: ProviderOutput | None = None,
    *,
    tag_prefix: str = 'topomt-provider',
) -> bool:
    """Clear only one original run's pocket layers, preserving its evidence.

    Parameters
    ----------
    view : MolSysView
        View containing the owned layers.
    output : ProviderOutput, optional
        Original result, or the active attached result.
    tag_prefix : str
        Namespace used when rendering.

    Returns
    -------
    bool
        Whether a previous render result was removed.

    Raises
    ------
    ValueError
        If no original result is available.

    Examples
    --------
    >>> clear_provider_pockets(view, output)  # doctest: +SKIP
    """
    output = _resolve_output(view, output)
    return (
        clear_previous_render_result(view, _operation_key(output, tag_prefix))
        is not None
    )


def attach_provider_output(
    view: Any,
    output: ProviderOutput,
    *,
    pocket_ids: list[str] | tuple[str, ...] | None = None,
    enable_addon: bool = True,
    show: bool = True,
    tag_prefix: str = 'topomt-provider',
    representation: str = 'auto',
    color: int | None = None,
    alpha: float = 0.35,
    point_radius_nm: float = 0.06,
) -> dict[str, Any]:
    """Attach an original result separately from the view's Topography.

    Parameters
    ----------
    view : MolSysView
        View with source-frame molecular coordinates, if loaded.
    output : ProviderOutput
        Detached original provider result retained by identity in addon state.
    pocket_ids : list or tuple of str, optional
        Original source IDs to show. None selects all pocket rows.
    enable_addon : bool
        Enable the registered TopoMT addon in this view.
    show : bool
        Render immediately; False attaches evidence and clears this display group.
    tag_prefix, representation, color, alpha, point_radius_nm
        Display options documented by ``show_provider_pockets``.

    Returns
    -------
    dict
        ``run_id`` and ``rendered`` result; evidence remains under
        ``view.addons.topomt.provider_outputs[run_id]``.

    Raises
    ------
    ValueError
        For an invalid output or render request.

    Examples
    --------
    >>> attach_provider_output(view, output)  # doctest: +SKIP
    """
    from .integration import register_with_molsysviewer

    output = _resolve_output(view, output)
    register_with_molsysviewer()
    if enable_addon:
        view.addons.enable('topomt')
    options: dict[str, Any] = dict(
        tag_prefix=tag_prefix,
        representation=representation,
        color=color,
        alpha=alpha,
        point_radius_nm=point_radius_nm,
    )
    rendered = show_provider_pockets(
        view, output, pocket_ids=pocket_ids if show else [], **options
    )
    runtime = ensure_runtime(view)
    runtime.provider_outputs[output.run.run_id] = output
    runtime.provider_display_options[output.run.run_id] = options
    runtime.active_provider_run_id = output.run.run_id
    record_event(
        view,
        'attach_provider_output',
        provider=output.provider,
        run_id=output.run.run_id,
    )
    _refresh_panels(view)
    return {'run_id': output.run.run_id, 'rendered': rendered}


def _provider_panel_state(runtime: Any) -> dict[str, Any] | None:
    output = runtime.provider_outputs.get(runtime.active_provider_run_id or '')
    if output is None:
        return None
    pockets = []
    for record in output.pockets:
        score = record.fields.get('score')
        if not isinstance(score, (int, float)) or not math.isfinite(score):
            score = None
        pockets.append(
            {
                'feature_id': record.source_id,
                'source_id': record.source_id,
                'score': score,
            }
        )
    return {
        'source_kind': 'provider_output',
        'provider': output.provider,
        'run_id': output.run.run_id,
        'pockets': pockets,
        'n_features': len(pockets),
        'feature_counts': {'reported_pocket': len(pockets)},
        'has_dfnd': False,
        'tag_prefix': runtime.provider_display_options[output.run.run_id]['tag_prefix'],
        'status': 'idle',
        'error': None,
        'warnings': [],
    }


def _handle_provider_panel_action(
    panel: Any, view: Any, action_id: str, payload: dict
) -> bool:
    runtime = ensure_runtime(view)
    state = _provider_panel_state(runtime)
    if state is None:
        return False
    output = runtime.provider_outputs[state['run_id']]
    options = runtime.provider_display_options[state['run_id']]
    try:
        if action_id in {'render_pockets', 'show_all_pockets', 'show_pocket'}:
            pocket_ids = None
            if action_id == 'show_pocket':
                source_id = payload.get('feature_id')
                if not isinstance(source_id, str):
                    raise ValueError('Provider pocket ID is required')
                pocket_ids = [source_id]
            panel.push_state({**state, 'status': 'rendering'})
            result = show_provider_pockets(
                view, output, pocket_ids=pocket_ids, **options
            )
            record_event(
                view,
                'panel_provider_pockets',
                run_id=output.run.run_id,
                n_rendered=result.counts['n_rendered'],
            )
            panel.push_state(
                {**state, 'status': 'done', 'warnings': list(result.warnings)}
            )
        elif action_id == 'clear_pockets':
            clear_provider_pockets(view, output, tag_prefix=options['tag_prefix'])
            panel.push_state(state)
        elif action_id == 'render_tetrahedra':
            panel.push_state(
                {
                    **state,
                    'status': 'error',
                    'error': 'Provider output has no DFND tetrahedra.',
                }
            )
        else:
            return False
    except Exception as exc:
        panel.push_state({**state, 'status': 'error', 'error': str(exc)})
    return True
