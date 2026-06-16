"""Small final-boundary adapters from viewer-neutral geometry to MolSysViewer."""

import numpy as np

from topomt import pyunitwizard as puw

from ..geometry import (
    IndexedTriangleGeometry,
    PointGeometry,
    RingGeometry,
    SegmentGeometry,
    SphereGeometry,
    TetrahedraGeometry,
)


def add_point_spheres(view, geometry: PointGeometry, *, radius, **kwargs):
    """Render point geometry as spheres at the final MolSysViewer boundary."""
    kwargs.pop('skip_digestion', None)
    coordinates = np.asarray(geometry.coordinates)
    center = coordinates[0] if len(coordinates) == 1 else coordinates
    if len(coordinates) == 1 and isinstance(kwargs.get('color'), (list, tuple)):
        if len(kwargs['color']) == 1:
            kwargs['color'] = kwargs['color'][0]
    return view.shapes.add_sphere(
        center=puw.quantity(center, geometry.unit),
        radius=radius,
        skip_digestion=True,
        **kwargs,
    )


def add_pocket_blob(view, geometry: SphereGeometry, **kwargs):
    """Render a blob from canonical spheres at the final viewer boundary."""
    kwargs.pop('skip_digestion', None)
    return view.shapes.add_pocket_blob(
        centers=puw.quantity(np.asarray(geometry.centers), geometry.unit),
        radii=puw.quantity(np.asarray(geometry.radii), geometry.unit),
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


def add_channel_tube(view, geometry: SphereGeometry, **kwargs):
    """Render an ordered variable-radius path at the final viewer boundary."""
    kwargs.pop('skip_digestion', None)
    return view.shapes.add_channel_tube(
        centers=puw.quantity(np.asarray(geometry.centers), geometry.unit),
        radii=puw.quantity(np.asarray(geometry.radii), geometry.unit),
        skip_digestion=True,
        **kwargs,
    )


def add_rings(view, geometry: RingGeometry, **kwargs):
    """Render oriented rings at the final viewer boundary."""
    kwargs.pop('skip_digestion', None)
    return view.shapes.add_rings(
        centers=puw.quantity(np.asarray(geometry.centers), geometry.unit),
        normals=geometry.normals,
        radii=puw.quantity(np.asarray(geometry.radii), geometry.unit),
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
