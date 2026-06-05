# DFND Feature Definitions

This document defines the feature semantics that should guide the DFND
implementation.

DFND is the native TopoMT method. It is not a CASTp clone, not an fpocket
variant, and not a wrapper around an external detector. Other engines remain
useful as references and validation targets, but DFND owns its own semantics.

> **Object model & terminology.** How these objects are organized
> (`raw / mesh / dfn{ …, components }`) and the `component → feature`
> ladder (with `feature` reserved for the public Topography level and `motif` for
> sub-structures of a component) are defined authoritatively in
> [`object_model.md`](object_model.md). The "domain" rung was retired on
> 2026-05-26 — read any "domain" below as `component` (its spatial representation).

The object-layer invariants and edge-case policies are defined in [`abstract_contract.md`](abstract_contract.md).

## 1. Tessellation Policy

DFND uses standard Delaunay triangulation of atomic centers as its baseline
geometric substrate.

Atomic radii are not ignored. They enter explicitly through the physical
quantities that define DFND:

- tetrahedron habitability, `R_residence`;
- face permeability, `R_gate`.

This separation is intentional:

- Delaunay geometry defines cells and adjacency;
- vdW radii define where a probe can reside and where it can pass;
- graph analysis defines connected topographic features.

Weighted or regular triangulation is not part of the baseline DFND method. It
would alter the cell adjacency using atomic radii before the habitability and
permeability analysis. That may be mathematically valid for other methods, but
in DFND it risks mixing the neutral geometric substrate with the physical probe
model. It should only be reconsidered if future benchmarks show a concrete
failure mode that cannot be solved by `R_residence`, `R_gate`, tolerances, or
feature-level rules.

## 2. Residence, Transit, and DFN Core Graph

`DFN` means **Delaunay Flow Network**.

DFN is not the Delaunay triangulation itself. The triangulation provides finite
tetrahedra, finite faces, hull faces, and adjacency. DFN is the flow graph built
on top of those objects for a selected probe radius.

For a fixed frame and probe radius `R_probe`, DFN uses the transit graph as
the movement backbone. It contains:

- finite resident-transit nodes, where `R_residence(T) >= R_probe`;
- finite non-resident transit connectors, where `R_residence(T) < R_probe` but
  the tetrahedron has at least two permeable contacts;
- finite transit edges through permeable shared faces;
- the virtual exterior node `OCEAN`, wet by definition and without finite
  geometry;
- external edges from finite transit nodes to `OCEAN` through permeable
  boundary or hull faces.

This separates residence from movement. Non-resident transit connectors can
connect two resident regions, but they do not contribute to resident volume.
Dry terminal contacts and non-transit dry nodes remain available as dry-network
and lining/contact metadata.

See [`residence_transit_contract.md`](residence_transit_contract.md) for the
full state contract.

## 3. Local Tetrahedron Permeability Class

DFND uses different words for volumetric cells and interfaces:

- tetrahedra are `wet` or `dry`;
- faces are `permeable` or `non-permeable`;
- finite tetrahedra are locally `open`, `coast`, or `sealed` according to the
  permeability pattern of their finite faces.

Definitions:

```text
tetrahedron_wet(T) = R_residence(T) >= R_probe
tetrahedron_dry(T) = R_residence(T) < R_probe

face_permeable(F) = R_gate(F) >= R_probe
face_non_permeable(F) = R_gate(F) < R_probe
```

Local permeability class for a finite tetrahedron:

```text
open(T) = all finite faces of T are permeable

coast(T) =
    at least one finite face of T is permeable
    and at least one finite face of T is non-permeable

sealed(T) = all finite faces of T are non-permeable
```

`non-coast` should not be used as a primary term. When needed, it is only a
derived category:

```text
non_coast(T) = open(T) or sealed(T)
```

This local permeability class is intentionally independent of whether the
tetrahedron itself is wet or dry. Combining habitability with local
permeability gives useful subtypes:

```text
wet_open(T) = tetrahedron_wet(T) and open(T)
wet_coast(T) = tetrahedron_wet(T) and coast(T)
wet_sealed(T) = tetrahedron_wet(T) and sealed(T)

dry_open(T) = tetrahedron_dry(T) and open(T)
dry_coast(T) = tetrahedron_dry(T) and coast(T)
dry_sealed(T) = tetrahedron_dry(T) and sealed(T)
```

A face should not be called wet or dry. Faces are permeable or non-permeable.
Wet/dry remains useful shorthand for residence state, but raw records should
prefer `residence_state` and `transit_state` to avoid mixing residence with
movement.

Non-resident tetrahedra with exactly one permeable contact are `terminal_contact`
records. Non-resident tetrahedra with two or more permeable contacts are
`transit_connector` records.

## 4. External Links

`external_link` is the DFN-level contact between a finite component and
`OCEAN`.

It is defined without using `mouth` as a primitive:

```text
external_link(C) = a connected cluster of permeable boundary or hull contacts
                   between component C and OCEAN
```

Operationally:

- a boundary or hull face is a finite face whose Delaunay neighbor is `-1`;
- the face contributes to exterior contact only if `R_gate(F) >= R_probe` under
  the selected tolerance policy;
- adjacent permeable boundary faces incident to the same component are
  grouped into one `external_link`;
- a single wide opening made of many boundary faces should count as one
  `external_link`, not many.

`mouth` is a geometric descriptor that may later be attached to an
`external_link`. It should not be the primitive used to classify DFN feature
families.

Component-internal motifs such as depth regions, throats, bottlenecks, chambers,
and reduced motif graphs are discussed in [`component_motifs.md`](component_motifs.md).

## 5. Components

A `component` is the connected component obtained after removing `OCEAN` and its
incident edges from the transit graph — the mathematical **graph** object (a set
of tetrahedron nodes). This is what the DFND *decomposition* produces; wet ones
are emitted in the raw field `wet_components`, dry ones as dry components.

A `ResidenceRegion` is the resident-node content inside a component.

The **spatial representation** of a component is its realization in the molecular
system: its lining atoms, volume, and centre.

A **`feature`** is the public `Topography` object promoted from a component
(`Pocket` / `Void` / `Channel` / `Mouth` / …) after adding metrics, atoms,
residues, derived mouth geometry, morphology, dynamics, and functional
annotations.

DFND avoids using `cavity` as the hypernym because in the broader pocket
community `cavity` often means a buried inaccessible cavity, close to `void`.
See [`object_model.md`](object_model.md) for the full `component → feature`
ladder.

Primary DFND component families:

```text
void
surface_concavity
pocket
channel
percolating
```

### 5.1. Void Component

A `void` is a finite component with no external links to `OCEAN` and at least one resident node.

```text
void(D) = n_external_links(D) == 0 and has_residence(D)
```

Interpretation: an enclosed component where the selected probe can reside but cannot reach the exterior.

A no-link component without residence is not a void in v1. It is reported as a raw `degenerate_subprobe` and can be filtered.

### 5.2. Pocket Component

A `pocket` is a finite component with exactly one external link and at least one resident node.

```text
pocket(D) = n_external_links(D) == 1 and has_residence(D)
```

Interpretation: a one-mouth resident concavity. The component may or may not contain a `wet_open` node. A compact one-mouth component made only of `wet_coast` resident nodes is still a pocket because the probe can reside inside it.

### 5.3. Surface Component

A `surface_concavity` is a finite component with exactly one external link and no resident nodes.

```text
surface_concavity(D) = n_external_links(D) == 1 and not has_residence(D)
```

Interpretation: a one-mouth non-resident contact or dent. This family is topologically well-defined, but its practical value remains a validation item. It should not be described simply as a shallow pocket.

### 5.4. Multi-External-Link Component

A `channel` is a finite component with two or more external links and at least one resident node.

```text
channel(D) = n_external_links(D) >= 2 and has_residence(D)
```

Interpretation: a multi-mouth resident component. `Channel` is a public shorthand, but tunnel, pore, branched channel, or cleft labels require later morphology, path, and geometric analysis.

### 5.5. Nonresident Passage Component

A `nonresident_passage` is a finite component with two or more external links and no resident nodes.

```text
nonresident_passage(D) = n_external_links(D) >= 2 and not has_residence(D)
```

Interpretation: a provisional raw pass-through contact. It should not be promoted to a biological channel without additional evidence.

### 5.6. Percolating Component

A `percolating` component is a resident component with **zero walls**: every boundary face is permeable (`n_wall_faces == 0`). This enclosure override takes precedence over the access × residence table.

```text
percolating(D) = has_residence(D) and n_wall_faces(D) == 0
```

Interpretation: a fully solvent-permeable / exposed wet region — porous, not a concavity. The selected probe resides but the boundary offers no enclosing wall. Mathematically such a component always presents exactly one external link, but that is a consequence, not the criterion, so no `Mouth` child is promoted. At the `Topography` level it becomes a `Percolating` feature with `shape_type` `neutral` (neither concave, convex nor mixed). Added for completeness; rarely encountered when analysing real proteins.

`wet_open` is retained as `has_open_interior`, a descriptor of open resident interior. It must not be used as the primary family discriminator.

The dry/probe-blocking side of DFND is defined separately in [`dry_network_and_convexity.md`](dry_network_and_convexity.md).

## 6. Secondary Classification Axes

The primary DFND component family should be kept separate from secondary labels.

Topological DFND component family:

- `void`;
- `surface_concavity`;
- `pocket`;
- `channel`.

Morphology:

- `groove`;
- `cleft`;
- `shallow_depression`;
- `simple_pocket`;
- `multi_chamber_pocket`;
- `branched_pocket`;
- `simple_channel`;
- `branched_channel`;
- `tunnel`;
- `pore`.

Dynamics:

- `cryptic`;
- `transient`;
- `persistent`;
- `gated`;
- `breathing`.

Function or annotation:

- `ligand_binding`;
- `catalytic`;
- `allosteric`;
- `ion_conducting`.

These axes should be reported as descriptors or annotations, not as mutually
exclusive replacements for the primary DFND component family.

## 7. Compatibility With Community Terminology

DFND keeps community-compatible names where their meaning is stable:

- `void` remains an enclosed inaccessible wet region;
- `pocket` remains an accessible concavity with an interior region;
- `channel` remains an accessible concavity with multiple exterior
  connections.

DFND introduces `surface_concavity` as a neutral family for accessible components without a wet-open interior. This avoids overusing `pocket` for
very shallow depressions and avoids using `groove` as a topological class when
elongation has not yet been measured.

`mouth` remains available as a geometric realization of an `external_link`, but
it is not part of the primary DFND component-family definition.

## 8. Dynamic Interpretation

The same definitions apply per frame in a trajectory. Events are then defined
by changes in components and external links:

- void to pocket: `n_external_links` changes from 0 to 1 while `has_residence` remains true;
- pocket to void: `n_external_links` changes from 1 to 0 while `has_residence` remains true;
- surface concavity to pocket: `has_residence` appears in a one-link component;
- pocket to surface concavity: residence disappears in a one-link component;
- pocket to multi-external-link component: `n_external_links` changes from 1 to 2 or more while residence persists;
- multi-external-link component to pocket: `n_external_links` drops to 1 while residence persists;
- nonresident passage to multi-external-link component: residence appears in a multi-link component;
- split or merge: connected components change their correspondence across frames.

See [`dynamic_topology.md`](dynamic_topology.md) for the temporal model.
See [`dynamic_topology.md`](dynamic_topology.md) for the temporal model.
