"""Python-side rendering helpers for the TopoMT MolSysViewer addon.

Split from a single module into one submodule per ``show_*`` entry point; the
public surface is unchanged (``from molsysviewer_topomt.render import show_*``).
"""

from ._pockets import show_topography_pockets
from ._tetrahedra import show_dfnd_tetrahedra
from ._graph import show_dfn_graph
from ._components import show_dfnd_components, carve_voids, show_dfnd_labels

__all__ = [
    'show_topography_pockets',
    'show_dfnd_tetrahedra',
    'show_dfn_graph',
    'show_dfnd_components',
    'carve_voids',
    'show_dfnd_labels',
]
