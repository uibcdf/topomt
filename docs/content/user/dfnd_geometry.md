# DFND geometry and probe queries

A DFND network retains the selected coordinates, atomic radii and local-to-source
atom map used to build its geometry. Coordinates and radii are stored internally
in nanometers. Later edits to the input molecular system do not change that
network's cached geometry or its geometric identity.

Network arrays, its Delaunay mesh arrays and `mesh.atoms` arrays are read-only
views. Direct writes and public attribute replacement are rejected. Use an
explicit array `.copy()` to prepare editable input, then construct a new network
for changed coordinates, atomic radii or atom mappings. Editing that copy does
not update the existing network.

Wrap copied internal arrays in `puw.quantity(values, 'nm')` when rebuilding.
Bare arrays in the synthetic constructor follow its legacy angstrom convention.

For an advanced synthetic workflow:

```python
from topomt import pyunitwizard as puw
from topomt.dfnd import DelaunayFlowNetwork
from topomt.dfnd.data import DFNDData

coordinates = puw.quantity(
    [[1.874, 1.874, 1.874], [1.874, -1.874, -1.874],
     [-1.874, 1.874, -1.874], [-1.874, -1.874, 1.874]],
    'angstroms',
)
radii = puw.quantity([1.7, 1.7, 1.7, 1.7], 'angstroms')
network = DelaunayFlowNetwork.from_coordinates_and_radii(coordinates, radii)
result = network.get_topography(probe_radius=puw.quantity(1.4, 'angstroms'))
data = DFNDData(network, result)

reprobed = data.at_probe(puw.quantity(2.2, 'angstroms'))
assert reprobed.network is data.network
assert reprobed.mesh.delaunay is data.mesh.delaunay
```

Changing the probe creates a new query and decomposition while sharing protected
geometry. Earlier query records remain available. Atomic-radius changes require
rebuilding their dependent clearances and measurements; a different probe alone
does not require rebuilding the Delaunay mesh.

The reusable `topomt.tools.geometry.immutable_array` operation owns read-only
array storage, copying mutable buffers once and sharing existing immutable
buffers. `DelaunayMesh.freeze()` opts a general mesh into protected geometry;
DFND applies it automatically. General meshes remain mutable until frozen.
Deep copies preserve the protection and may safely share immutable numeric
buffers while copying mutable metadata.

Pickle restoration reapplies array protection. It may allocate fresh buffers;
it is not a canonical Topography interchange schema.

This native protection does not make all legacy result dictionaries or feature
fields immutable. The broader Topography context/support contract and behavior
of assigning its `molecular_system` remain under development. A retained live
system reference identifies the source; use the captured mesh coordinates for
historical geometric measurements.

Retaining multiple probe results still costs memory for their separate records,
graphs and components. Retain only the results needed by the workflow; geometry
sharing does not eliminate those per-query allocations.
