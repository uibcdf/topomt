"""Small final-boundary adapters from viewer-neutral geometry to MolSysViewer."""

import numpy as np

from topomt import pyunitwizard as puw

from ..geometry import (
    IndexedTriangleGeometry,
    PointGeometry,
    SegmentGeometry,
    SphereGeometry,
    TetrahedraGeometry,
)


def add_point_spheres(view, geometry: PointGeometry, *, radius, **kwargs):
    """Render point geometry as spheres at the final MolSysViewer boundary."""
    kwargs.pop('skip_digestion', None)
    return view.shapes.add_sphere(
        center=puw.quantity(np.asarray(geometry.coordinates), geometry.unit),
        radius=radius,
        skip_digestion=True,
        **kwargs,
    )


def add_sphere_set(view, geometry: SphereGeometry, **kwargs):
    """Render variable-radius spheres at the final MolSysViewer boundary."""
    kwargs.pop('skip_digestion', None)
    return view.shapes.add_set_alpha_spheres(
        centers=puw.quantity(np.asarray(geometry.centers), geometry.unit),
        radii=puw.quantity(np.asarray(geometry.radii), geometry.unit),
        skip_digestion=True,
        **kwargs,
    )


def add_uniform_spheres(view, geometry: SphereGeometry, **kwargs):
    """Render equal-radius spheres at the final MolSysViewer boundary."""
    kwargs.pop('skip_digestion', None)
    if not geometry.radii:
        return None
    if any(radius != geometry.radii[0] for radius in geometry.radii[1:]):
        raise ValueError('add_uniform_spheres requires one common radius.')
    return view.shapes.add_sphere(
        center=puw.quantity(np.asarray(geometry.centers), geometry.unit),
        radius=puw.quantity(geometry.radii[0], geometry.unit),
        skip_digestion=True,
        **kwargs,
    )


def add_segments(view, geometry: SegmentGeometry, *, radius, **kwargs):
    """Render segment geometry as links at the final MolSysViewer boundary."""
    kwargs.pop('skip_digestion', None)
    return view.shapes.add_links(
        coordinate_pairs=puw.quantity(
            np.asarray(geometry.coordinate_pairs), geometry.unit
        ),
        radius=radius,
        skip_digestion=True,
        **kwargs,
    )


def add_tetrahedra(view, geometry: TetrahedraGeometry, **kwargs):
    """Render canonical tetrahedra while preserving mesh-local pick indices."""
    kwargs.pop('skip_digestion', None)
    return view.shapes.add_tetrahedra(
        atom_quads=geometry.atom_quads,
        skip_digestion=True,
        **kwargs,
    )


def add_indexed_triangles(view, geometry: IndexedTriangleGeometry, **kwargs):
    """Render canonical indexed triangles with mesh-local pick triplets."""
    kwargs.pop('skip_digestion', None)
    return view.shapes.add_triangle_faces(
        atom_triplets=geometry.atom_triplets,
        skip_digestion=True,
        **kwargs,
    )
