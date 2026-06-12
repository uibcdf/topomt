from .integration import attach_features, attach_topography, new_view


def _resolve_topography(
    molecular_system,
    *,
    topography=None,
    method: str | None = None,
    skip_digestion: bool = False,
    **method_kwargs,
):
    """Return an explicit or freshly computed TopoMT topography."""
    if topography is not None:
        if getattr(topography, '_molsys', None) is None and molecular_system is not None:
            topography._molsys = molecular_system
        return topography

    import topomt as tmt

    resolved_method = method or 'pocketeer'
    return tmt.get_topography(
        molecular_system,
        method=resolved_method,
        skip_digestion=True,
        **method_kwargs,
    )


def build_topography_standalone0_html(
    molecular_system,
    output_filename: str,
    *,
    topography=None,
    method: str | None = None,
    feature_ids=None,
    title: str = 'MolSysViewer Standalone 0 · TopoMT',
    selection='all',
    structure_indices='all',
    syntax: str = 'MolSysMT',
    load_mode: str = 'selection',
    include_controls: bool = True,
    include_popout: bool = False,
    discover_addons: bool = False,
    addon_modules=None,
    apply_project_config: bool = True,
    debug_js: bool | None = None,
    tag_prefix: str = 'topomt-pocket',
    **topography_kwargs,
) -> str:
    """Build a standalone-0 HTML file with a molecular system and TopoMT overlay."""
    resolved_topography = _resolve_topography(
        molecular_system,
        topography=topography,
        method=method,
        skip_digestion=True,
        **topography_kwargs,
    )
    view = new_view(
        resolved_topography,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        load_mode=load_mode,
        show=feature_ids is None,
        tag_prefix=tag_prefix,
        skip_digestion=True,
    )
    if feature_ids is not None:
        attach_features(
            view,
            resolved_topography,
            feature_ids=feature_ids,
            tag_prefix=tag_prefix,
            skip_digestion=True,
        )

    resolved_addon_modules = ['molsysviewer_topomt']
    for module_name in addon_modules or ():
        if module_name not in resolved_addon_modules:
            resolved_addon_modules.append(module_name)

    import molsysviewer
    return molsysviewer.build_standalone0_html(
        view,
        output_filename,
        title=title,
        include_controls=include_controls,
        include_popout=include_popout,
        discover_addons=discover_addons,
        addon_modules=resolved_addon_modules,
        apply_project_config=apply_project_config,
        debug_js=debug_js,
    )


def launch_topography_standalone0(
    molecular_system,
    output_filename: str | None = None,
    *,
    topography=None,
    method: str | None = None,
    feature_ids=None,
    open_browser: bool = True,
    title: str = 'MolSysViewer Standalone 0 · TopoMT',
    selection='all',
    structure_indices='all',
    syntax: str = 'MolSysMT',
    load_mode: str = 'selection',
    include_controls: bool = True,
    include_popout: bool = False,
    discover_addons: bool = False,
    addon_modules=None,
    apply_project_config: bool = True,
    debug_js: bool | None = None,
    tag_prefix: str = 'topomt-pocket',
    **topography_kwargs,
) -> str:
    """Launch a standalone-0 MolSysViewer host with a TopoMT overlay."""
    resolved_topography = _resolve_topography(
        molecular_system,
        topography=topography,
        method=method,
        skip_digestion=True,
        **topography_kwargs,
    )
    view = new_view(
        resolved_topography,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        load_mode=load_mode,
        show=feature_ids is None,
        tag_prefix=tag_prefix,
        skip_digestion=True,
    )
    if feature_ids is not None:
        attach_features(
            view,
            resolved_topography,
            feature_ids=feature_ids,
            tag_prefix=tag_prefix,
            skip_digestion=True,
        )

    resolved_addon_modules = ['molsysviewer_topomt']
    for module_name in addon_modules or ():
        if module_name not in resolved_addon_modules:
            resolved_addon_modules.append(module_name)

    import molsysviewer
    return molsysviewer.launch_standalone0(
        view,
        output_filename=output_filename,
        open_browser=open_browser,
        title=title,
        include_controls=include_controls,
        include_popout=include_popout,
        discover_addons=discover_addons,
        addon_modules=resolved_addon_modules,
        apply_project_config=apply_project_config,
        debug_js=debug_js,
    )
