# DFND Abstract Contract

This document closes the current abstract contract for DFND before implementation
hardening. It defines object layers, transformations, invariants, edge cases,
confidence flags, identity rules, and terminology boundaries.

## 1. Object Layers

DFND separates objects by layer.

### 1.1. Geometry Layer

- `DelaunayMesh`: finite Delaunay tetrahedra, finite faces, hull faces, and
  neighbor relations.
- `Tetrahedron`: finite Delaunay simplex defined by four real atom vertices.
- `Face`: finite triangular face defined by three real atom vertices.
- `HullFace`: finite face with Delaunay neighbor `-1`.

### 1.2. Residence and Transit Layer

- `ResidenceState`: resident, non-resident, or marginal, controlled by
  `R_residence`.
- `FaceState`: permeable, non-permeable, or marginal, controlled by `R_gate`.
- `TransitState`: resident transit, transit connector, terminal contact, or
  non-transit, controlled by residence and the number of permeable contacts.

### 1.3. DFN Layer

- `DFN`: Delaunay Flow Network for one probe radius.
- `OCEAN`: virtual wet exterior root. It is not a tetrahedron and has no finite
  geometry.
- `TransitNode`: finite tetrahedron that can participate in probe movement. It
  may be resident or a non-resident transit connector.
- `TransitEdge`: permeable connection between two transit nodes.
- `ExternalEdge`: permeable connection from a transit node to `OCEAN` through a
  hull face.

### 1.4. Decomposition Layer

- `TransitDomain`: connected component after removing `OCEAN` and its incident
  edges from the transit graph.
- `ResidenceRegion`: resident-node subset inside one `TransitDomain`.
- `ConcavityDomain`: topographic interpretation of a `TransitDomain`, its
  residence regions, external links, and metadata.
- `ExternalLink`: connected cluster of external contacts between one
  `ConcavityDomain` and `OCEAN`.

### 1.5. Dry Layer

- `DryNode`: finite dry tetrahedron where the probe cannot reside.
- `DryEdge`: connection between two dry nodes through a non-permeable face.
- `DryComponent`: connected component of the dry graph.
- `DryInterface`: contact record between a dry component and wet domains,
  external links, `OCEAN`, or the hull/exterior context.

### 1.6. Motif Layer

- `DomainMotif`: derived internal structure inside or around a
  `ConcavityDomain`.
- `DryMotif`: candidate motif derived from dry components and dry interfaces.
- `ReducedDomainGraph`: graph produced by domain lumping.
- `DomainMotifGraph`: semantically annotated reduced graph for paths and
  motifs.

### 1.7. Topography Layer

- `TopographyFeature`: general semantic output object.
- `ConcavityFeature`: enriched Topography object derived from a
  `ConcavityDomain`.
- `ConvexityFeature`: future enriched object derived mainly from dry motifs.
- `BoundaryFeature`: future enriched object derived from boundary or interface
  descriptors such as mouths, rims, or necks.
- `MixedFeature`: future enriched object for walls, separators, lining regions,
  and other features that are neither purely concave nor purely convex.
- `Void`, `SurfaceConcavity`, `Pocket`, and `Channel`: public feature families
  derived from the corresponding domain families.
- `Mouth`: geometric descriptor derived from an `ExternalLink`, not a primary
  DFND decomposition object.

## 2. Transformation Pipeline

The abstract pipeline is:

```text
molecular system
-> atom coordinates and radii
-> DelaunayMesh
-> R_residence and R_gate
-> residence, face, and transit states
-> transit graph and dry graph
-> TransitDomain and ResidenceRegion decomposition
-> ConcavityDomain interpretation
-> ExternalLink clustering
-> DryComponent and DryInterface extraction
-> domain and dry motif analysis
-> geometric realization
-> Topography features
```

The primary decomposition must happen before motif analysis and before feature
annotation.

## 3. Canonical Domain Families

Remove `OCEAN` and its incident edges from the transit graph. Each connected
component of the remaining finite transit graph is a `TransitDomain`. A
`ConcavityDomain` is the topographic interpretation of a `TransitDomain` plus
its residence regions and external links.

Let:

```text
L(D) = number of external links from domain D to OCEAN
has_residence(D) = n_resident_nodes(D) >= 1
has_open_interior(D) = any resident node in D has local class wet_open
```

The primary family classifier uses `L(D) x has_residence(D)`:

```text
void_domain(D) = L(D) == 0 and has_residence(D)
degenerate_subprobe_domain(D) = L(D) == 0 and not has_residence(D)

surface_concavity_domain(D) = L(D) == 1 and not has_residence(D)
pocket_domain(D) = L(D) == 1 and has_residence(D)

nonresident_passage_domain(D) = L(D) >= 2 and not has_residence(D)
multi_external_link_domain(D) = L(D) >= 2 and has_residence(D)
```

`degenerate_subprobe_domain` and `nonresident_passage_domain` are raw/reporting
labels in v1, not promoted biological feature names. `channel` may be used as a
convenient public shorthand for a resident `multi_external_link_domain`, but the
raw topological label should remain explicit.

`has_open_interior(D)` must be reported as a descriptor because it captures how
open the resident part is, but it must not decide the family.

The domain family is determined before morphology, dynamics, function, or motif
analysis.

## 4. Raw Objects to Features

Raw DFND objects are graph or interface objects. Features are enriched
topographic objects.

```text
TransitDomain
    transit nodes
    transit edges
    external links

ResidenceRegion
    resident nodes
    resident volume metrics

ConcavityDomain
    transit domain
    residence regions
    external links
    domain family

DryComponent
    dry nodes
    dry edges
    dry interfaces
    dry depth
    dry interface signatures

ConcavityFeature
    domain
    atoms and residues
    metrics
    geometric realizations
    derived mouth descriptors
    motifs
    morphology labels
    dynamic labels
    functional annotations

ConvexityFeature / BoundaryFeature / MixedFeature
    dry motifs or boundary descriptors
    atoms and residues
    metrics
    geometric realizations
    morphology labels
    dynamic labels
    functional annotations
```

The public API may expose simplified feature objects, but raw records must
preserve domain-level, dry-component-level, and interface-level provenance.

## 5. Mouth Status

`Mouth` is not a primitive for primary domain classification.

```text
ExternalLink = DFN primitive
Mouth = geometric realization of an ExternalLink
```

Possible API choices:

- expose `ExternalLink` as the primary record and derive `Mouth` when geometry
  is requested;
- expose `Mouth` as a descriptor object attached to an `ExternalLink`;
- keep `Mouth` as a compatibility alias only after the domain semantics are
  stable.

The first implementation should prioritize `ExternalLink` records.

## 6. Gate, Bottleneck, and Throat

These terms must remain distinct.

- `gate`: face-level passability object, measured by `R_gate`.
- `bottleneck`: minimum-capacity element on a path, region, or motif.
- `throat_candidate`: low-capacity separator between an exterior-side region
  and a deeper region.
- `throat`: a validated `throat_candidate` after scoring, persistence, or
  geometric realization rules are fixed.

Only `gate` is canonical at the geometric primitive level. `bottleneck` and
`throat_candidate` are derived motif descriptors.

## 7. Chamber Status

`Chamber` is not a primary domain family.

Current status:

```text
chamber_candidate = deeper, relatively high-habitability region derived after
                    domain lumping or capacity analysis
```

A chamber becomes canonical only after scoring and stability rules are defined.
Until then, chamber-like objects should be reported as candidate motifs.

The first dry-network contract is defined in [`dry_network_and_convexity.md`](dry_network_and_convexity.md).

## 8. Metrics by Layer

### 8.1. Node and Edge Metrics

- `R_residence` for finite tetrahedra;
- `R_gate` for faces;
- wet/dry state;
- permeable/non-permeable/marginal face state;
- local class: `open`, `coast`, `sealed`;
- combined local class: `wet_open`, `wet_coast`, `wet_sealed`, `dry_open`,
  `dry_coast`, `dry_sealed`.

### 8.2. ExternalLink Metrics

- face ids;
- atom ids;
- area descriptors;
- minimum, maximum, and mean `R_gate`;
- marginal-contact flags;
- derived mouth descriptors when requested.

### 8.3. ConcavityDomain Metrics

- domain family;
- node and edge counts;
- topological volume;
- atom and residue ownership;
- external-link count;
- topological depth descriptors;
- capacity profiles;
- confidence flags.

### 8.4. DomainMotif Metrics

- supporting nodes and edges;
- supporting faces;
- capacity profile;
- path membership;
- geometric realization;
- candidate/validated status.

### 8.5. Dry Metrics

- dry component id;
- dry node and edge counts;
- dry interface ids;
- minimum, mean, and maximum `dry_depth`;
- adjacent concavity domain ids;
- adjacent external link ids;
- OCEAN exposure descriptors;
- local class composition;
- candidate dry motif descriptors.

### 8.6. TopographyFeature Metrics

- domain or dry-motif metrics;
- geometric metrics;
- derived mouth or rim geometry;
- morphology descriptors;
- dynamic descriptors;
- functional annotations.

## 9. Confidence Flags

DFND records should be able to carry confidence flags.

Recommended flags:

- `canonical`: follows the current canonical contract without marginal events;
- `marginal`: one or more decisive comparisons are within tolerance;
- `degenerate`: local geometry is singular or near-singular;
- `low_confidence`: result is retained but should be interpreted cautiously;
- `experimental`: descriptor depends on a non-canonical motif or lumping rule;
- `derived`: descriptor is computed from a canonical object but is not itself a
  primitive.

Flags should be additive, not mutually exclusive.

## 10. Edge Cases

### 10.1. Wet-Sealed Domains

A `wet_sealed` node is resident and has no permeable finite faces. Under the v1 local DFN contract it cannot have direct external links and cannot participate in an accessible transit path.

```text
wet_sealed + zero external links -> void_domain singleton
wet_sealed + external links -> invalid state under v1 local rules
```

If a future non-local merging operation changes this behavior, that operation must be explicit and separately validated.

### 10.2. Dry-Open Nodes

Dry-open nodes are non-resident. If they have at least two permeable contacts,
they are `transit_connector` records in the transit graph. If they have exactly
one permeable contact, they are `terminal_contact` records. They should be
retained in raw diagnostics because they can mark thin passages, contact-only
regions, or numerical edge cases.

### 10.3. Tiny Domains

One-node and near-zero-volume domains should not be silently discarded by core
classification. They should be emitted with size and confidence flags. Filtering
is a reporting policy, not a decomposition rule.

### 10.4. Marginal External Links

External links composed only of marginal faces should be flagged. The stable
classification may choose a deterministic side, but raw records must preserve
marginality.

### 10.5. Fragmented Molecular Systems

The first policy uses one global `OCEAN` for the whole molecular system. A
per-fragment exterior context may be introduced later if fragmented systems show
clear ambiguity.

## 11. Identity and Persistence

Stable identifiers should be based on atom-defined primitives.

Recommended identities:

- tetrahedron id: sorted atom quadruplet;
- face id: sorted atom triplet;
- domain id: stable hash of sorted tetrahedron ids plus frame/context;
- external-link id: stable hash of sorted boundary face ids plus domain id;
- motif id: stable hash of supporting domain id, node ids, edge ids, and motif
  type.

Dynamic identity should be based on overlap and persistence:

- tetrahedron overlap;
- face/external-link overlap;
- atom and residue ownership overlap;
- centroid or volume continuity as secondary evidence;
- motif support overlap for motif persistence.

## 12. Fragmentation and OCEAN Policy

`OCEAN` is global by default.

Rules:

- `OCEAN` is wet by definition;
- `OCEAN` has no `R_residence`, volume, or local permeability class;
- `OCEAN` is removed before `ConcavityDomain` decomposition;
- all external links connect exactly one domain to `OCEAN`;
- multi-fragment systems initially share the same `OCEAN` unless a future
  policy explicitly creates fragment-specific exterior contexts.

## 13. Tolerance Attachment Points

Tolerances must be attached to the objects they affect.

- wet/dry: `R_residence` versus `probe_radius`;
- permeable/non-permeable: `R_gate` versus `probe_radius`;
- external-link clustering: marginal boundary faces and face-connectivity
  policy;
- domain family: `n_external_links` and wet-open presence after marginal
  resolution;
- motif candidates: capacity, depth, and persistence scores.

No hidden tolerance should silently change a domain family without appearing in
raw diagnostics.

## 14. Invariants

Every implementation must preserve these invariants:

- `OCEAN` has no volume.
- `OCEAN` is not a Delaunay tetrahedron.
- `OCEAN` is wet by definition.
- `ConcavityDomain` objects never include `OCEAN`.
- Every finite transit node belongs to exactly one `TransitDomain`.
- Every `ExternalLink` belongs to exactly one `ConcavityDomain`.
- A single connected exterior opening should be one `ExternalLink`, not one per
  boundary face.
- `Mouth` descriptors derive from `ExternalLink` objects.
- Every dry node belongs to exactly one `DryComponent` under the selected dry-connectivity policy.
- `DryInterface` records preserve adjacency between dry components and wet domains, external links, `OCEAN`, or hull context.
- `DryMotif` descriptors do not change concavity-domain classification.
- Transit connectors contribute to movement connectivity but not to resident volume.
- Domain family is determined before motif analysis.
- Domain lumping must not change the primary domain family.
- Filtering tiny domains is a reporting step, not a decomposition step.
- Raw records must preserve marginal and degenerate decisions.

## 15. Community Terminology

DFND keeps common terms where their meaning is stable:

- `void`: enclosed inaccessible domain;
- `pocket`: accessible domain with one external link and an interior wet-open
  region;
- `channel`: public shorthand for an accessible multi-external-link domain;
  tunnel or pore interpretation requires extra morphology/path evidence.

DFND keeps `surface_concavity_domain` as a provisional family for exposed
domains without a wet-open interior. This avoids prematurely calling every
shallow coastal depression a pocket, but the family must be validated with toy
systems or geometric sweeps before it is treated as strongly canonical.

DFND avoids `cavity` as a hypernym because the community often uses cavity for
buried inaccessible cavities. The method uses `concavity_domain` at the
network-decomposition layer and `concavity_feature` only for enriched
Topography objects.
