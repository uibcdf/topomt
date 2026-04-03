"""Build a DelaunayMesh from a molecular system."""

import molsysmt as msm

from .delaunay_mesh import DelaunayMesh


def get_delaunay_mesh(molecular_system, selection='all'):
    """Return a DelaunayMesh built from the selected atomic coordinates."""

    molecular_system = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    atom_centers = msm.get(
        molecular_system,
        selection=selection,
        element='atom',
        coordinates=True,
    )[0]
    return DelaunayMesh(points=atom_centers)
