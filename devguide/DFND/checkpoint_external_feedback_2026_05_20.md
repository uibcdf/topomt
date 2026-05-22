# DFND External Feedback Checkpoint - 2026-05-20

This checkpoint records the project response to an external conceptual review of
`devguide/DFND` before the first implementation sprint.

The review was useful because it focused on conceptual consistency, physical
interpretability, implementability, and community credibility. The project does
not accept every suggested simplification, but it does accept several concrete
hardening actions.

## 1. Accepted Changes

The following feedback is accepted and should be reflected in the design docs:

- remove or fix stale historical notes that refer to `DFND` as both current and
  previous terminology;
- migrate old `SOLID`/`TRANSIT`/`Surface Shell` vocabulary to the current
  `dry`/`wet`/`dry_interface` terms, or mark it explicitly as historical;
- moderate comparative claims against CASTp, fpocket, MOLE, and related tools;
- avoid stating that DFND contains CASTp or MOLE as formal limiting cases;
- make `combined_class` a derived tetrahedron label, not an independent source
  of truth;
- avoid presenting `volume_topological` as physical solvent volume;
- add an explicit validation plan before publication-level claims;
- keep `DryMotif` as candidate/experimental rather than a public v1 feature.

## 2. Accepted With Project-Specific Position

### 2.1. Scope of v1

The review recommended a much smaller v1. The project keeps the current v1
scope because it is still implementable if the boundary remains raw-record
oriented:

```text
DelaunayMesh
primitive measurements
wet graph
ConcavityDomain
ExternalLink
dry graph
DryComponent
DryInterface
dry_depth
RawDFNDRecord
candidate DomainMotif/DryMotif descriptors
```

Public `ConvexityFeature`, `BoundaryFeature`, and `MixedFeature` objects are not
required for v1, but the conceptual taxonomy remains documented so that the
implementation does not need a later ontology rewrite.

### 2.2. Surface Concavity

`surface_concavity_domain` remains in the corpus but is treated as provisional
until a toy system or geometric sweep demonstrates that the required
configuration is realizable and useful.

The immediate action is not deletion. The immediate action is validation.

### 2.3. Channel Naming

The review correctly points out that `n_external_links >= 2` can identify a
multi-opening wet domain without proving a community-level tunnel or pore.

Project position:

```text
multi_external_link_domain = primary topological condition
channel / tunnel / pore    = morphology or feature interpretation after extra
                             geometric/path analysis
```

The existing `channel_domain` name can remain as a public shorthand, but the
raw record should preserve the more literal external-link count and should not
claim tunnel morphology solely from that count.

### 2.4. Volumes

`volume_topological` remains useful for debugging and graph-level analysis, but
it is not a physical solvent volume and must not be used as a direct CASTp-like
volume comparison.

A publication-facing v1 should add at least one physically meaningful volume
metric, such as `volume_solvent_estimate`, that subtracts atom-occupied portions
or uses an explicit geometric correction.

## 3. Points Requiring Investigation

### 3.1. Realizability of wet_coast and wet_sealed

The review raises a serious geometric question: if a tetrahedron is wet by
`R_residence >= R_probe`, are its faces usually or always permeable under the
current `R_gate` definition?

This affects:

- `wet_coast`;
- `wet_sealed`;
- `surface_concavity_domain`;
- any rule that depends on the presence or absence of `wet_open` nodes.

Required action before relying on these states:

- construct explicit toy examples if they exist;
- run a numerical sweep over synthetic tetrahedra with varied atom radii;
- document whether these states are common, rare, impossible, or only numerical
  edge cases under the current definitions.

### 3.2. R_gate for unequal radii

The review questions whether the current planar face-gate construction is
physically exact for unequal atomic radii.

Required action:

- audit the mathematical definition and code implementation;
- state whether `R_gate` is exact under the adopted DFND geometric model or an
  approximation;
- if approximate, document the expected bias and keep it out of exactness
  claims.

### 3.3. Dry-open and sliver reporting

`dry_open` and singleton dry components are valid raw records, but they can
proliferate in sliver-like geometries. The implementation must keep them in raw
records while providing clear reporting flags and optional downstream filters.

## 4. Rejected Simplifications

The project does not accept these as immediate changes:

- removing the wet/dry/OCEAN/COAST vocabulary;
- deleting the dry conceptual layer;
- deleting the future `ConvexityFeature`, `BoundaryFeature`, and `MixedFeature`
  taxonomy from design documentation;
- collapsing the method permanently to three public families before testing
  `surface_concavity_domain`;
- removing future dynamics, pharmacophore, or mechanical-coupling notes.

These items are kept outside the v1 critical path where appropriate, but they
remain part of the long-term DFND vision.

## 5. Immediate Documentation Actions

- clean historical terminology artifacts;
- update old algorithm sections to current wet/dry terminology;
- moderate novelty and comparison claims;
- clarify `volume_topological` versus physical solvent volume;
- add validation plan documentation;
- add explicit pre-implementation checks for `wet_coast`/`wet_sealed` and
  unequal-radii `R_gate`.


## 6. Geometry Annex Response

A follow-up geometric review corrected two points and introduced one critical
change to the graph semantics.

Accepted corrections:

- the face-plane `R_gate` construction is not invalidated by unequal radii; the
  plane through the three atom centers is a reflection-symmetry plane for the
  three spheres;
- `wet_sealed` is realizable, for example in a compact regular tetrahedron
  where the resident cavity is wider than each face gate;
- `surface_concavity_domain` is more defensible than initially criticized, but
  still needs toy and real-case validation;
- `R_residence` and `R_gate` have no universal ordering. Compact cells can have
  `R_residence > R_gate`; sliver-like cells can have `R_gate > R_residence`.

Critical accepted change:

```text
residence != transit != contact
```

A non-resident tetrahedron with at least two permeable contacts can be a
`transit_connector`: the probe cannot reside there, but it can pass through.
Excluding such a tetrahedron from the movement graph can over-segment pockets
or hide multi-opening domains.

New contract adopted:

- `TransitDomain`: connected component of the transit graph;
- `ResidenceRegion`: resident-node content inside a transit domain;
- `ConcavityDomain`: topographic interpretation of a transit domain plus
  residence regions, external links, and metadata;
- `terminal_contact`: non-resident tetrahedron with exactly one permeable
  contact;
- `transit_connector`: non-resident tetrahedron with at least two permeable
  contacts.

New required toys:

- `toy_wet_sealed_regular_tetrahedron`;
- `toy_dry_open_cut`;
- `toy_terminal_dry_coast`;
- `toy_two_atom_gate`.

## 7. Third Feedback Integration: Access x Residence

Accepted. The family discriminator must be based on two orthogonal axes: access (`n_external_links`) and residence (`n_resident_nodes >= 1`). This replaces the older rule that used `wet_open` as a gate for pockets and channels.

Consequences:

- one-mouth resident domains are `pocket_domain` even if all resident nodes are `wet_coast`;
- `surface_concavity_domain` is reserved for one-mouth non-resident contact/dent domains;
- resident domains with two or more external links are raw `multi_external_link_domain`; `channel` remains a shorthand pending morphology;
- non-resident domains with two or more external links are `nonresident_passage_domain`, a provisional raw label;
- no-link non-resident domains are raw/filter `degenerate_subprobe_domain`, not voids;
- `wet_open` is reported as `has_open_interior`, a descriptor of openness, not a classifier.

This makes `TransitDomain`, `ResidenceRegion`, and `ConcavityDomain` distinct layers: movement is controlled by permeable faces, residence by residence capacity, and interpretation by access plus residence.
