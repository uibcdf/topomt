"""Python-side rendering helpers for the TopoMT MolSysViewer addon.

Split from a single module into one submodule per ``show_*`` entry point; the
public surface is unchanged (``from molsysviewer_topomt.render import show_*``).
"""

from ._components import (
    carve_voids,
    show_dfnd_components,
    show_dfnd_convexity,
    show_dfnd_labels,
    show_dfnd_legend,
    show_dfnd_pharmacophore,
)
from ._graph import show_dfn_graph
from ._pockets import show_topography_pockets
from ._tetrahedra import show_dfnd_tetrahedra
from .result import RenderResult, render_result

__all__ = [
    'RenderResult',
    'render_result',
    'show_topography_pockets',
    'show_dfnd_tetrahedra',
    'show_dfn_graph',
    'show_dfnd_components',
    'carve_voids',
    'show_dfnd_labels',
    'show_dfnd_convexity',
    'show_dfnd_legend',
    'show_dfnd_pharmacophore',
]
