# Algorithm reference

This pseudocode describes the current local/discrete pipeline. It is not a
routine that first computes exact all-atom free space or certified paths.
Names denote operations rather than promised new callable APIs.

## Input and geometry

```text
INPUT: selected single-frame centers, effective radii, source atom map;
       mesh configuration; probe/query policy; reporting settings

validate array shapes, finite coordinates, positive finite radii, atom count
normalize lengths to nm and retain the input context and radius/hydrogen policy
build ordinary 3D Delaunay cells, oriented adjacency and unique face identities
protect the cached numeric geometry

for each cell:
    generate residence candidates on interior/face/edge strata
    validate candidate centers and recompute clearance to its four atoms
    retain the best positive capacity and candidate diagnostics
    estimate local bare empty volume using the four vertex balls

for each unique face:
    generate/validate local gate candidates against its three atoms
    retain gate capacity and support correspondence
scatter shared-face capacities consistently to their cell-face occurrences
for each cell-face incidence:
    inspect that cell's opposite apex against the supporting face plane
    retain its incidence-specific intrusion diagnostic
retain substrate identity and recoverable atom-defined supports
```

The PDB/molecular reader is not reimplemented here: molecular conversion,
selection and radius sourcing belong to MolSysMT. Insufficient geometric rank
or numerical failure must remain distinguishable from an empty analysis result.

## A probe query

```text
resident := residence_capacity >= probe - epsilon - residence_tolerance
capacity_pass[f] := gate_capacity[f] >= probe - epsilon - permeability_tolerance
permeable[T, f] := capacity_pass[f]
if intrusion policy blocks suspected faces:
    permeable[T, f] := capacity_pass[f] and not suspected[T, f]
record margins and local open/coast/sealed classes

if transit policy enables connectors:
    transit := resident or (number_of_permeable_contacts >= 2)
else:
    transit := resident
record nonresident connector/contact/non-transit roles separately

internal edges := shared faces with two transit endpoints and BOTH incidences admitted
exterior edges := admitted hull contacts of transit nodes to virtual OCEAN
components := connected components after removing OCEAN

for each component:
    retain transit, resident and connector supports
    if residence exists, emit one resident aggregate for this transit component
        (not a decomposition of its resident-only induced subgraph)
    collect hull contacts and cluster whole faces by shared atomic edges
    retain exterior-link support, carrier areas and gate summaries
    count nonpermeable boundary wall faces
    derive the topological family through the catalog function

bank nodes := complement of finite transit nodes
group banks by the selected face/edge/vertex adjacency policy
for face adjacency require BOTH incidences nonpermeable and BOTH nodes banks
retain bank interfaces, depth and candidate supports
```

No second strict gate threshold is added when creating an internal edge.
`flag_only` records suspected intrusion without removing it. Default face bank
adjacency requires nonpermeability on both sides; a mixed incidence pair is
neither a wet edge nor a dry face edge. Edge/vertex modes differ.

## Interpretation and promotion

```text
attach typed components and recoverable context/support keys
derive wet/dry lining, depth and boundary descriptors
derive morphology and provisional internal capacity motifs
derive catalog classifications and existing bank-based interface descriptors
retain raw records independently of reporting suppression
apply reporting views such as min_size
promote supported wet families using the refined public class
promote native-link Mouth children for the supported pocket/channel families
attach the complete method-specific result under topography.dfnd
```

Classification delegates to the catalog; raw compatibility family records
remain available. Morphological refinement and public feature type can differ
from a component's coarse family without changing its exact support.
This is a logical-stage summary, not a claim that all derived descriptors are
independent of reporting. Current bank-based interface annotation consumes
compatibility-filtered dry records; see [interfaces](../interfaces.md).

## Advanced operator defaults

These values describe the current source and controls; they are not suggested
physical calibration. Query settings belong to `DFNDQuery`; the following
derived choices have their own scope.

| Operation | Current choice | Control/meaning |
| --- | --- | --- |
| Intrusion suspicion | Opposite apex plane distance at most bare apex radius plus epsilon; degenerate normal also suspect. | Cached per incidence; `gate_intrusion_policy` selects flag-only or blocking. |
| Capacity motifs | Inclusive prominence floor 0.1 nm (1 Å). | Fixed internal default, not a public query argument. |
| Fast empty estimate | Resolution 8, half-shifted barycentric lattice, 165 interior samples. | Fixed in the geometry pass; actual count retained per cell. |
| Prototype interfaces | At least 3 atoms per retained body, smallest retained fraction at least 0.15; largest bank wins shared intermediate labels. | Helper arguments; normal promotion uses defaults, not automatic chain labels. |
| Lineage | `min_jaccard=0.2`, with exact support matches preferred. | Explicit argument of matching/track helpers, not the geometry query. |

Definitions and limits live in [local capacities](../local_capacities.md),
[hierarchy](../hierarchy_and_paths.md), [measurements](../measurements.md),
[interfaces](../interfaces.md) and [scale](../scale_and_dynamics.md).

## Optional downstream operations

New native probe queries can reuse protected geometry. On-demand empty volume
and grids evaluate declared carrier regions. Skeleton, lineage and track
operations consume retained records with their own objectives and limitations.
They do not silently strengthen local graph edges into physical path certificates.

## Required output context

Retain input and source atom correspondence, coordinate/radius model, mesh/query
settings, schema/units, component/link supports, margins/flags, catalog
interpretation and reporting policy. Availability, failure and computed zero
remain distinct. The [worked example](../worked_tetrahedron.md) shows how to
recover that context from an actual promoted result.
