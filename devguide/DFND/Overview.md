# Delaunay Flow Network Decomposition (DFND): Overview

DFND is the native TopoMT method direction for molecular topography. It is a
Delaunay-flow method: the molecular system is first represented by a standard
Delaunay tessellation of atomic centers, and pocket-like structures are then
defined by probe habitability, face permeability, and graph connectivity.

DFND is not a CASTp clone, not an fpocket variant, and not an alpha-sphere-first
method. CASTp, fpocket, AlphaSpace2, and related engines remain useful
references and validation pressure, but DFND owns its own semantics.

## 1. Central Question

DFND asks:

```text
How can a probe move through the empty space induced by the molecular geometry?
```

Rather than starting from a pre-defined molecular surface, DFND builds a flow
network over Delaunay tetrahedra:

- tetrahedra are finite volumetric cells;
- faces are possible gates between cells;
- atomic radii define whether a probe can reside in a tetrahedron;
- face geometry defines whether a probe can pass between tetrahedra;
- transit state separates movement from residence;
- graph connectivity defines transit domains, residence regions, concavity
  domains, and their relation to the exterior.

## 2. Core Layers

DFND is easiest to understand as a layered method.

### 2.1. Delaunay Geometry

The baseline substrate is the standard Delaunay triangulation of atomic centers.
Atomic radii are not used as tessellation weights in the baseline method.
Instead, they enter explicitly in physical quantities:

- `R_residence`: tetrahedron habitability;
- `R_gate`: face permeability.

This keeps geometry and probe physics separate.

### 2.2. Wet and Dry Interpretation

For a selected probe radius, the same Delaunay mesh supports two complementary
network views:

- the residence layer, where the probe can reside;
- the transit graph, where the probe can move through permeable contacts;
- the dry graph, where the probe cannot reside and where faces block passage.

The transit side defines transit domains and concavity domains. The residence
layer defines resident content and volume-bearing regions inside those domains.
The dry side defines dry components, dry interfaces, dry depth, and candidate
dry motifs that may later support convexity, boundary, and mixed features.

### 2.3. DFN

`DFN` means **Delaunay Flow Network**.

For a selected probe radius, DFN contains:

- resident-transit tetrahedron nodes;
- non-resident transit connectors with at least two permeable contacts;
- transit edges through permeable shared faces;
- the virtual exterior node `OCEAN`, wet by definition;
- external edges from finite transit nodes to `OCEAN` through permeable hull
  faces.

`OCEAN` is not a tetrahedron. It has no `R_residence`, no volume, and no local
permeability class.

### 2.4. DFND Decomposition

DFND decomposes the finite transit graph into `TransitDomain` objects and then
interprets them as `concavity_domains` after adding residence regions, external
links, and metadata.

```text
remove OCEAN from DFN
compute connected components of the remaining finite transit graph
each component is a TransitDomain
interpret TransitDomain + ResidenceRegions as a concavity_domain
```

This is the core decomposition step of Delaunay Flow Network Decomposition.

### 2.5. External Links

An `external_link` is the DFN-level contact between a `concavity_domain` and
`OCEAN`.

It is a connected cluster of permeable boundary or hull contacts. A geometric
`mouth` can be derived later from an `external_link`, but `mouth` is not the
primitive used to classify domains.

### 2.6. Domain Motifs and Features

After primary decomposition, DFND can analyze internal domain motifs:

- topological depth;
- paths;
- reduced domain graphs;
- throat candidates;
- bottlenecks;
- chamber candidates;
- geometric mouth descriptors.

These motifs do not change the primary domain family. They enrich the domain
and support later Topography features.

A `ConcavityDomain` is derived from a transit graph object. A `DryComponent` is a dry graph
object. A `ConcavityFeature`, `ConvexityFeature`, `BoundaryFeature`, or
`MixedFeature` is an enriched Topography object derived later after adding
metrics, atoms, residues, geometry, motifs, dynamics, and annotations.

## 3. Primary Domain Families

DFND classifies finite transit domains by two independent axes.

- Access: the number of direct external links to `OCEAN`.
- Residence: whether the domain contains at least one resident node, i.e. a
  tetrahedron where the full probe can reside.

The v1 classifier is:

| External links | Has residence | Raw domain label | Public interpretation |
|---:|---|---|---|
| 0 | yes | `void_domain` | closed cavity where the probe fits |
| 0 | no | `degenerate_subprobe_domain` | raw/filter label, not a public feature |
| 1 | yes | `pocket_domain` | one-mouth resident concavity |
| 1 | no | `surface_concavity_domain` | one-mouth non-resident surface contact/dent |
| >=2 | yes | `multi_external_link_domain` | multi-mouth domain; `channel` is shorthand |
| >=2 | no | `nonresident_passage_domain` | provisional raw label for pass-through contact |

`wet_open` is retained as a quality descriptor, not as a family gate:

```text
has_open_interior(D) = any resident node in D is wet_open
```

This distinction matters because compact resident cells can be `wet_coast`: the
probe fits in the room even when one or more windows are narrow. Such a domain
should still be classified as a pocket if it has one external link and
residence.

Public feature names may be simplified to `Void`, `SurfaceConcavity`, `Pocket`,
and `Channel`, but raw records should preserve the domain-level provenance.

## 4. Local Cell Semantics

DFND separates several concepts that are often conflated.

Tetrahedron habitability:

```text
wet: R_residence >= R_probe
dry: R_residence < R_probe
```

Face permeability:

```text
permeable: R_gate >= R_probe
non-permeable: R_gate < R_probe
```

Local finite-tetrahedron class:

```text
open: all finite faces are permeable
coast: mixed permeable and non-permeable finite faces
sealed: all finite faces are non-permeable
```

This gives combined labels such as `wet_open`, `wet_coast`, and `wet_sealed`.
The primary transit graph is built from resident-transit nodes and
non-resident transit connectors connected through permeable faces; local class
labels do not create connectivity by themselves.

## 5. Outputs

A mature DFND run should be able to report:

- `TransitDomain` records;
- `ResidenceRegion` records;
- `ConcavityDomain` records;
- domain family: void, surface concavity, pocket, or channel;
- `ExternalLink` records;
- `DryComponent` records;
- `DryInterface` records;
- dry depth and dry interface signatures;
- derived mouth geometry when requested;
- candidate rim, protrusion, ridge, wall, separator, lining, and dry-core motifs;
- topological volume and other metrics;
- atoms and residues supporting domains, links, and dry interfaces;
- local wet/dry and open/coast/sealed labels;
- topological depth and capacity profiles;
- candidate motifs such as bottlenecks, throats, chambers, and paths;
- confidence flags for marginal, degenerate, low-confidence, experimental, or
  derived records.

## 6. Why DFND Is Useful

DFND is designed to make molecular topography explicit and traceable:

- volume and connectivity are separated;
- exterior access is represented by `OCEAN` and `external_links`;
- shallow exposed concavities are not forced to be pockets;
- channels are defined by multiple external links, not by ad-hoc path guesses;
- domain motifs can be derived after decomposition without changing the primary
  domain family;
- dynamic tracking can use atom-defined tetrahedra and faces rather than shape
  fitting alone;
- dry topology can later be correlated with B-factors, RMSF, GNM/ANM modes,
  hinges, allosteric paths, and mutation-sensitive buried regions.

This makes DFND suitable not only for static pocket detection, but also for
trajectory analysis, cryptic-site tracking, channel gating, domain motif
analysis, dry/wet boundary analysis, future pharmacophore annotation, and future
mechanical coupling.

## 7. Reading Order

For the current abstract corpus, read:

1. [`abstract_contract.md`](abstract_contract.md): object layers, invariants,
   pipeline, edge cases, and terminology boundaries.
2. [`feature_definitions.md`](feature_definitions.md): DFN, external links,
   concavity domains, and domain families.
3. [`domain_motifs.md`](domain_motifs.md): depth, paths, motifs, reduced domain
   graphs, and geometric realizations.
4. [`dry_network_and_convexity.md`](dry_network_and_convexity.md): dry nodes, dry edges, dry components, dry interfaces, and candidate dry motifs.
5. [`residence_transit_contract.md`](residence_transit_contract.md): separation of residence, transit, and contact.
6. [`data_model_v1.md`](data_model_v1.md): minimal raw records and semantic feature boundary for the first implementation.
7. [`toy_systems_v1.md`](toy_systems_v1.md): synthetic systems required before real benchmarks.
8. [`numerical_policy.md`](numerical_policy.md): thresholds, tolerances, and
   marginal states.
9. [`metrics_contract.md`](metrics_contract.md): metric naming and layer-specific
   quantities.
10. [`validation_plan.md`](validation_plan.md): validation layers and credibility boundary before external claims.
11. [`Implementation_Route.md`](Implementation_Route.md): engineering route from
   prototype to hardening.

The implementation is not production-ready yet, but it is no longer only a design corpus. The current code builds a DFND substrate, produces raw records, integrates with `Topography`, runs small real-system stability checks, supports build-once/query-many probe sweeps, and reports first dry-motif candidates. The documentation remains the canonical contract for deciding what should become stable public API.
