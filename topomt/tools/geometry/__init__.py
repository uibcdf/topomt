"""General geometric tools."""

from .hulls import convex_hull_metrics
from .meshes import marching_cubes_union
from .planes import clip_mesh_with_plane
from .primitives import triangle_area
from .sampling import union_volume_monte_carlo

__all__ = [
    'triangle_area',
    'convex_hull_metrics',
    'marching_cubes_union',
    'clip_mesh_with_plane',
    'union_volume_monte_carlo',
]
