"""Build a DelaunayMesh or WeightedDelaunayMesh from a molecular system."""

import molsysmt as msm

from ._pyunitwizard import pyunitwizard as puw
from .delaunay_mesh import DelaunayMesh
from .weighted_delaunay_mesh import WeightedDelaunayMesh


def get_delaunay_mesh(molecular_system, selection='all', weighted=False, weights=None):
    """Return a Delaunay-based mesh built from the selected atomic coordinates."""

    molecular_system = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    atom_centers = msm.get(
        molecular_system,
        selection=selection,
        element='atom',
        coordinates=True,
    )[0]

    if not weighted:
        return DelaunayMesh(points=atom_centers)

    if weights is None:
        atom_radii = msm.physchem.get_atomic_radius(
            molecular_system,
            element='atom',
            selection=selection,
            definition='vdw',
            syntax='MolSysMT',
        )
        atom_radii = puw.get_value(atom_radii, to_unit='nm')
        weights = atom_radii * atom_radii

    return WeightedDelaunayMesh(points=atom_centers, weights=weights)
