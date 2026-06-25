"""The physicochemical (druggability) overlay -- the third axis, orthogonal to
topology and to the named features. It maps the **chemical character** of a cavity's
lining (hydrophobic / polar / charged), fed by ``molsysmt.physchem`` (Eisenberg
hydrophobicity + pH7 charge per residue). It is the chemical complement of the
geometric ``accessible_atom_indices`` (which atoms) -- of what character those atoms
are. See devguide/DFND/chemistry_overlay_analysis.md.

This module is the separate overlay **surface**; the rendering implementation still
lives in ``_components`` (delegated to here) and will be consolidated into this module
in a follow-up. The point is that chemistry is a distinct, composable overlay -- never
a feature type or a grounded primitive.
"""


def show_pharmacophore(view, topography=None, **kwargs):
    """Chemistry overlay: an interaction-site glyph at each cavity, typed by the
    **dominant** physicochemical character of its lining (positive / negative /
    hydrophobic / acceptor), from ``molsysmt.physchem``. Applies on top of any
    topology. Returns the layer, or ``None`` when the system has no chemistry (dummy
    atoms)."""
    from ._components import show_dfnd_pharmacophore

    return show_dfnd_pharmacophore(view, topography, **kwargs)


def show_affinity(view, topography=None, **kwargs):
    """Chemistry overlay: the residence spheres coloured per atom by the affinity of
    the lining (hydrophobic / polar / charged), from ``molsysmt.physchem`` -- a
    continuous druggability map. Applies on top of any topology."""
    from ._components import show_dfnd_components

    return show_dfnd_components(
        view, topography, representation='affinity_spheres', **kwargs
    )
