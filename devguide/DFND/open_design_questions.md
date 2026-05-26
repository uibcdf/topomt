# DFND Open Design Questions

This temporary document lists the remaining DFND design details that should be
resolved before or during implementation. It exists to avoid losing decisions
while the abstract corpus is being stabilized.

Priority for the next discussion round:

```text
1, 2, 8, 9, 18, 20, 22, 23
```

## 1. External-Link Connectivity

Status: **decided for the first implementation**.

Canonical policy:

```text
Two boundary/hull permeable faces belong to the same external_link if they
share an edge and belong to the same component.
```

Use `face-edge connectivity` by default. Do not use `face-vertex connectivity`
as the first policy because it can merge two openings that touch only at one
atom. `tolerant/rim connectivity` remains experimental.

## 2. Marginal-State Resolution

Status: **decided for the first implementation**.

Use explicit open/closed/marginal predicates:

```text
x > threshold + eps      -> open or wet
x < threshold - eps      -> closed or dry
abs(x - threshold) <= eps -> marginal
```

Stable graph-construction policy is conservative:

```text
marginal R_residence -> dry for graph construction, flagged as marginal
marginal R_gate     -> non-permeable for graph construction, flagged as marginal
```

Raw records must preserve the original value, threshold, effective epsilon, and
`marginal` flag.

Open refinement: `eps` may later be input-aware. Candidate sources include PDB
coordinate precision, experimental resolution, and B-factor-derived uncertainty.
These refinements must be explicit policy parameters, not hidden behavior.

## 3. Wet-Sealed Treatment

Decision: a `wet_sealed` node has no permeable finite faces. It therefore cannot have direct external links and cannot participate in an accessible transit path under v1 local rules.

```text
wet_sealed + has_residence + zero external links -> void singleton
wet_sealed + external_links -> invalid under the local DFN contract
```

If future non-local merging changes this, it must be introduced as an explicit operation, not as a silent exception.

## 4. Dry-Open Treatment

Decide whether `dry_open` remains only in raw diagnostics or feeds candidate
motifs such as thin passages or inconsistency markers.

## 5. Minimal Components

Define reporting policy for:

```text
one-node components
near-zero-volume components
single-face external links
tiny dry components
```

Core classification should preserve them; filtering should be reporting-only.

## 6. Fragmented Molecular Systems

Decide when one global `OCEAN` is sufficient and when fragment-specific exterior
contexts may be needed.

## 7. Component Identity

Define stable identifiers:

```text
id
external_link_id
motif_id
```

Likely based on atom quadruplets/triplets and frame/context.

## 8. Data Model

Status: **decided for the first implementation**.

Core/raw model:

```text
DelaunayMesh
DelaunayFlowNetwork
Component
ExternalLink
Motif
DryComponent
RawDFNDRecord
```

`Motif` is included from the start as a record type, even if most motif
instances are experimental. This does not block the canonical component pipeline.

`TopographyFeature` belongs to the output/enrichment layer rather than the core
DFN construction layer.

## 9. ExternalLink / Mouth API

Status: **decided for the first implementation**.

Canonical policy:

```text
ExternalLink = primary DFN object
Mouth        = optional geometric descriptor derived from ExternalLink
```

`Mouth` should not be an alias of `ExternalLink`. `ExternalLink` is a network
object; `Mouth` is an a posteriori geometric characterization useful for areas,
visualization, and compatibility with community terminology.

First implementation should prioritize `ExternalLink` records and attach mouth
descriptors only when geometric realization is requested.

## 10. Minimal Component Motifs

Decide whether the first implementation reports only:

```text
topological_depth
capacity_profile
external-link paths
```

or also `throat_candidate` and `chamber_candidate`.

## 11. Topological Depth in Void Components

For `void`, there is no `external_link`. Decide whether depth is:

```text
not_applicable
computed from nearest dry/wet boundary
computed from synthetic seed
```

Initial preference: `not_applicable`.

## 12. Weighted Depth

Decide whether to postpone or prototype weighted depth:

```text
cost = 1
cost = 1 / R_gate
cost = edge length
cost = resistance(R_gate, R_residence)
```

## 13. Bottleneck Definition

Define the first `bottleneck` descriptor:

```text
minimum R_gate along selected path
minimum path capacity
min-cut candidate
```

## 14. Throat Definition

Keep as `throat_candidate` until deciding whether it is defined by:

```text
local minima
cut sets
persistence
geometric realization
```

## 15. Chamber Definition

Keep as `chamber_candidate` until deciding whether it is defined by:

```text
high R_residence
depth basin
capacity basin
reduced graph
```

## 16. Dry Graph Motifs

Think through rules for:

```text
dry_core_candidate
protrusion_candidate
ridge_candidate
wall_candidate
separator_candidate
lining_region
```

Currently only dry graph and dry/wet interface are canonical.

## 17. Dry/Wet Interface Ownership

Define ownership of atoms/residues for:

```text
component lining
external_link lining
dry wall
separator
```

## 18. Minimal Metrics

Status: **decided for the first implementation**.

Minimal component metrics:

```text
id
family
n_nodes
n_edges
n_external_links
volume_topological
min/mean/max R_residence
min/mean/max R_gate
topological_depth_max, if applicable
flags
```

Minimal `ExternalLink` metrics:

```text
external_link_id
n_faces
external_link_area_geometric
min/mean/max R_gate
atom_ids
face_ids
flags
```

## 19. Confidence Flags

Concretize assignment rules for:

```text
canonical
marginal
degenerate
low_confidence
experimental
derived
```

## 20. Public Names

Status: **decided for the first implementation**.

Core/raw names:

```text
Component
Void
SurfaceConcavity
Pocket
Channel
ExternalLink
DryComponent
DryInterface
Motif
DryMotif
```

Public Topography names:

```text
TopographyFeature
ConcavityFeature
ConvexityFeature
BoundaryFeature
MixedFeature
Void
SurfaceConcavity
Pocket
Channel
MouthDescriptor
RimDescriptor
```

Use `ExternalLink`, not `ExteriorLink`, because the concept is already defined
as a link between a component and `OCEAN`.

## 21. Compatibility With Current topomt.features

Check whether the current feature model already has or needs:

```text
SurfaceConcavity
ExternalLink
DryComponent
Protrusion
Wall
```

## 22. Raw Record Contract

Status: **decided for the first implementation**.

Minimum reproducibility fields:

```text
probe_radius
radii_model
threshold_policy
epsilon_length
epsilon_relative
coordinates_source
atom_ids
tetrahedron_ids
face_ids
R_residence
R_gate
wet/dry
permeable/non-permeable/marginal
local_class
id
family
external_link_id
dry_component_id
dry_interface_id
dry_depth
dry_interface_signature
flags
```

## 23. Toy Validation Systems

Status: **decided for the first implementation**.

First toy validation set:

```text
toy_void
toy_surface_concavity
toy_pocket
toy_channel
toy_two_external_links_touching_vertex_only
toy_wet_sealed
toy_dry_open
toy_marginal_gate
```

These toy systems should be implemented before real benchmarks so that the core
semantics can be tested without biological or PDB-processing ambiguity.

## 24. Alpha-Sphere Relationship

Decide whether alpha-spheres are exposed as:

```text
derived visualization only
optional descriptors
never part of core DFND
```

Current policy: not part of core DFND.

## 25. Promotion Strategy

Define how a descriptor moves from experimental to canonical:

```text
documented definition
tests
toy cases
real cases
stability under tolerance
dynamic behavior if relevant
```


## 26. External Feedback Follow-up

Status: **decided as pre-implementation hardening tasks**.

Required before relying on the affected classifications:

```text
validate wet_coast / wet_sealed realizability
audit unequal-radii R_gate model
keep surface_concavity provisional until validated
separate multi_external_link from biological channel/tunnel/pore labels
keep volume_topological as raw/debug, not physical solvent volume
add volume_solvent_estimate before serious volume comparison
```


## 27. Residence and Transit Separation

Status: **decided for the first implementation**.

Canonical v1 policy:

```text
resident node -> transit_state = resident_transit
non_resident + >=2 permeable contacts -> transit_state = transit_connector
non_resident + 1 permeable contact -> transit_state = terminal_contact
non_resident + 0 permeable contacts -> transit_state = non_transit
```

Primary movement components are `Component` records. Resident content inside
those components is stored separately as `ResidenceRegion` records. A `Component`
is the connected transit graph piece together with its residence regions,
external links, and metadata (its topographic interpretation).


## Access x Residence Classifier

Decision: the primary family classifier is `n_external_links x has_residence`. `wet_open` is retired as a family gate and reported only as `has_open_interior`.

Open validation items: practical utility of `surface_concavity`, reporting policy for `nonresident_passage`, and morphology criteria before promoting `multi_external_link` to tunnel or pore terminology.
