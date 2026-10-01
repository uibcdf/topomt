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

DFND also captures an input context shared by the network, its probe results
and the promoted Topography. It preserves requested selection, resolved atom
order, original frame index, radius/hydrogen policies and selected molecular
topology. Public coordinates and radii in the context are protected
PyUnitWizard quantities. Only one selected frame is retained.

For a molecular workflow:

```python
from topomt import get_topography
from topomt.dfnd import synthetic

source = synthetic.tetrahedron().to_molsysmt()
topography = get_topography(source, method='dfnd', structure_indices=0)
context = topography.input_context
saved_selection = context.recover_molecular_system()
original_atom_indices = context.atom_indices
```

The recovered MolSys is an independent, editable copy. It contains selected
atoms in local order `0..N-1` and the saved frame at index 0. `atom_indices`
maps those atoms back to the original input. Requested selection order may
differ from MolSysMT's resolved selection order; the map records the order
actually used by DFND. The opaque `source_id` identifies this captured
occurrence, rather than a universal molecular identity. To translate original
indices explicitly, use
`context.local_atom_indices(indices, source_id=context.source_id)`.

Array-only inputs preserve geometry and mapping without inventing molecular
topology: `recover_molecular_system()` raises `ValueError` for those inputs.
DFND requires a single explicit frame index, either a scalar or a one-element
sequence. Multiple/empty/`'all'` frame requests raise `ValueError`; analyse
frames separately. Geometry is nonperiodic Cartesian, even when recoverable
input metadata contains a box; minimum-image calculations are not performed.

`Topography.molecular_system` and `feature.molecular_system` remain original
input references and can be live. Use the context for historical recovery;
native diagnostic labels and `Topography.show()` do so automatically. Assigning
`molecular_system` on an object containing features, an input context or engine
results raises `ValueError`. Construct a new Topography/analysis for changed
input. Empty objects without results can still bind an input.

This protection does not make all legacy result dictionaries, feature fields
or registry views immutable. Other engine routes currently expose
`input_context=None`; their existing provider-specific outputs remain usable.
The complete public context/spatial-support contract remains under development.
The native MolSysViewer addon has its separate source/index-space contract;
its adoption of historical input contexts is not covered by `Topography.show()`.

Retaining multiple probe results still costs memory for their separate records,
graphs and components. Retain only the results needed by the workflow; geometry
sharing does not eliminate those per-query allocations.
The retained selected topology also costs memory once per input context. The
original compatibility reference can keep a source trajectory alive, even
though the context only captures one frame. Copy/pickle preserve recovery and
array protection; a full Topography/network copy or pickle can also copy/store
its original input reference. No cross-version interchange format is promised.
