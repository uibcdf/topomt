# Reading a result and recovering its meaning

The public result is a `Topography` registry of findings. Native DFND objects
remain available for deeper inspection without making the mesh or graph part
of every user's routine workflow.

## Two levels of access

```text
Topography
  public features: type, geometry/measurements, relations, source context
  input_context: selected saved input and correspondence
  dfnd
    raw: native records, parameters and explicit unit schema
    mesh: retained geometry, atoms, tetrahedra and faces
    dfn
      query / parameters
      graph: query states and native exterior links
      components: typed wet and dry registry
```

A native component is a graph support with a spatial representation. A motif
is an internal substructure or descriptor. A promoted feature is a public
scientific finding. Dynamic attributes containing raw motif dictionaries do not
alone establish the complete public subregion/support contract.

`get_features(...)` returns a set of matching features. To select one when the
query is known to have a single match, use `next(iter(matches))`; inspect the
count or iterate all matches when multiple findings are possible.

## Trace one finding

The executable [worked example](worked_tetrahedron.md) creates `topography` for
the 1.4 Å tetrahedron probe. Its sealed result can be inspected as follows:

```python
from topomt import pyunitwizard as puw

matches = topography.get_features(by='type', value='void')
assert len(matches) == 1
feature = next(iter(matches))
component = topography.dfnd.dfn.components[feature.component_id]
assert feature.source_id == component.component_key
assert feature.support_key == component.support_key
center_angstroms = puw.get_value(feature.center, to_unit='angstroms')
```

This is a trace from public interpretation to native occurrence/support. It is
not a requirement that users rely on display labels or private implementation
functions. Follow [the API reference](../../api/users/api_users.rst) for callable
details and [the geometry guide](../user/dfnd_geometry.md) for operational context.

## Different identities answer different questions

| Identity | Meaning |
| --- | --- |
| `component_id`, e.g. `WET-1` | A local, rank-derived display selector; rank uses node count. |
| `support_key` | Digest of the exact collection of atom-defined tetrahedra on the same atom-index substrate. |
| `component_key` | Contextual result, side and exact support identity. |
| Feature `source_id` | Link to the promoted native occurrence; parent wet features use their component key. |
| Track/correspondence | Evidence linking occurrences across probes/frames; not inferred from equal display labels. |

Support equality excludes the catalog name. It does not imply equal coordinates
across frames or universal atom identity across independently indexed systems.
Keep the full recoverable support and source mapping, not just a digest.

## Snapshot and source mapping

The captured input context retains selected coordinates, radii, atom order,
frame and radius/hydrogen policies. Numeric geometry is protected and shared
across compatible probe queries. Molecular recovery returns an independent
selected MolSys snapshot when topology is available. Array-only inputs do not
invent molecular topology.

Original molecular-system compatibility references can remain live; use the
saved context to recover what was actually analyzed. Local mesh indices and
original molecular atom indices occupy different spaces. The stored map records
the resolved order, which need not equal a requested selection order.

## Relations and atom roles

Mouths promoted from native links retain their parent component and face support.
Existing parent/child connectors cover their supported dimensional relationships;
they are not a general containment engine for arbitrary chamber features.

An atom can line several regions or banks. Lining, delimiting, probe-accessible
and contacted atom roles differ. A forced one-owner coloring/selection is a
derived view, not canonical exclusive membership.

Mesh neighbors are also not automatically movement neighbors. The current
`dfn.graph.neighbors` helper filters mesh adjacency by residence labels; a
traversable route must respect the actual face `transit_edge` decisions.
Similarly, `permeability_state='permeable'` records post-policy face admission,
but an internal `transit_edge` also needs two finite transit endpoints. Passing
the face test alone need not create an edge in the query graph.

## Attribution and availability

Scientific attribution is available through TopoMT's optional Ackredit
integration; see [scientific attribution](../user/scientific_attribution.md).
Reading a retained result does not re-execute an original provider.

Distinguish a computed empty result, filtered output, unsupported/uncomputed
geometry and execution failure. An absent physical-patch capability has no
implied count of zero. Full neutral support/provenance adoption remains under
development even though the native context and source traces are already useful.
