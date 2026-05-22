# DFND Residence, Transit, and Contact Contract

This document records the core correction introduced after the external
geometric review: DFND must separate probe residence, probe transit, and probe
contact.

The previous simplified reading treated wet tetrahedra as the only nodes of the
flow graph. That can over-segment pockets when a non-resident tetrahedron has
multiple permeable faces and therefore acts as a transit throat.

## 1. Three Separate Questions

DFND answers three local questions with different predicates.

```text
Residence:
    Can the probe reside in this tetrahedron as a local volumetric state?
    Controlled by R_residence.

Transit:
    Can the probe pass through this tetrahedron from one permeable contact to
    another?
    Controlled by the pattern of permeable faces/contacts.

Contact:
    Can the probe touch or enter a boundary direction without crossing through
    the tetrahedron?
    Controlled by one permeable contact without a second exit.
```

A Delaunay tetrahedron is a support cell, not a physical room with planar walls.
`R_residence` is a resident-capacity descriptor. `R_gate` is a passage-capacity
descriptor. They must not be collapsed into one state.

## 2. Primitive States

### 2.1. Residence State

```text
resident(T)     = R_residence(T) >= R_probe
non_resident(T) = R_residence(T) < R_probe
marginal_residence(T) = abs(R_residence(T) - R_probe) <= eps
```

Under the conservative marginal policy, marginal residence is treated as
non-resident for graph construction and flagged in raw records.

### 2.2. Face State

```text
permeable(F)     = R_gate(F) >= R_probe
non_permeable(F) = R_gate(F) < R_probe
marginal_face(F) = abs(R_gate(F) - R_probe) <= eps
```

Under the conservative marginal policy, marginal faces are treated as
non-permeable for graph construction and flagged in raw records.

### 2.3. Permeable Contacts

A permeable contact of a tetrahedron is either:

- a permeable shared finite face to another finite tetrahedron;
- a permeable hull face to `OCEAN`.

Let:

```text
n_permeable_contacts(T) = number of permeable finite or hull contacts of T
```

## 3. Transit State

All resident tetrahedra are transit-capable because the probe can reside there
and can participate in local flow when a permeable contact exists.

Non-resident tetrahedra are split by the number of permeable contacts:

```text
resident(T):
    transit_state = resident_transit

non_resident(T) and n_permeable_contacts(T) >= 2:
    transit_state = transit_connector

non_resident(T) and n_permeable_contacts(T) == 1:
    transit_state = terminal_contact

non_resident(T) and n_permeable_contacts(T) == 0:
    transit_state = non_transit
```

Interpretation:

- `resident_transit`: the probe can reside and can also move through permeable
  contacts.
- `transit_connector`: the probe cannot reside, but can pass through from one
  permeable contact to another. This captures dry-open or dry-transit throats.
- `terminal_contact`: the probe can touch or enter from one side, but cannot
  cross through because there is no second permeable contact.
- `non_transit`: no residence and no passage.

## 4. Transit Graph

The transit graph is the primary movement graph.

Nodes:

```text
transit_node(T) = transit_state in {resident_transit, transit_connector}
```

Edges:

```text
transit_edge(T_i, T_j) =
    T_i and T_j are transit_nodes
    and they share a permeable finite face
```

External edges:

```text
external_transit_edge(T, OCEAN) =
    T is a transit_node
    and T has a permeable hull face
```

This prevents `dry_open` slivers from acting as artificial cuts when they have
at least two permeable contacts.

## 5. TransitDomain

A `TransitDomain` is a connected component of the transit graph after removing
`OCEAN` and its incident edges.

```text
TransitDomain = connected component of finite transit nodes
```

A `TransitDomain` can contain both resident and non-resident transit nodes.
Non-resident transit nodes contribute to connectivity, not to resident volume.

## 6. ResidenceRegion

A `ResidenceRegion` is a connected subset of resident nodes inside one
`TransitDomain`. Connectivity between resident nodes may be direct or may be
mediated by transit connectors, depending on the analysis view.

For v1, store both:

```text
resident_node_ids
transit_connector_node_ids
```

and keep volume metrics separated:

```text
volume_topological_transit
volume_topological_resident
volume_solvent_estimate_resident
```

## 7. ConcavityDomain

A `ConcavityDomain` is the topographic interpretation of one `TransitDomain`
plus its resident content, external links, and metadata.

The primary classifier must use two axes: access and residence.

```text
access = n_external_links in {0, 1, >=2}
has_residence = n_resident_nodes >= 1
has_open_interior = any resident node is wet_open
```

| Access | Residence | Raw label | v1 interpretation |
|---:|---|---|---|
| 0 | yes | `void_domain` | closed resident cavity |
| 0 | no | `degenerate_subprobe_domain` | raw/filter label |
| 1 | yes | `pocket_domain` | one-mouth resident concavity |
| 1 | no | `surface_concavity_domain` | one-mouth non-resident contact/dent |
| >=2 | yes | `multi_external_link_domain` | multi-mouth resident domain; `channel` shorthand |
| >=2 | no | `nonresident_passage_domain` | provisional pass-through contact |

`has_open_interior` is a descriptor, not the family gate. The graph substrate must no longer be restricted to resident nodes only.
The exact `surface_concavity_domain` and pocket boundary remains a validation
item, but the graph substrate should no longer be restricted to resident nodes
only.

## 8. Dry Components After Transit Separation

Dry graph construction remains useful, but it should not steal transit
connectors from the movement graph.

Dry records should preserve:

```text
non_resident terminal_contact nodes
non_resident non_transit nodes
non_resident transit_connector nodes
```

`transit_connector` nodes may appear both in transit-domain provenance and in
dry diagnostics. They should be marked clearly so that dry components do not
hide movement connectivity.

## 9. Required Toys

The toy set must include:

- `toy_wet_sealed_regular_tetrahedron`: resident but all faces non-permeable;
- `toy_dry_open_cut`: two resident regions connected only through a
  non-resident transit connector;
- `toy_terminal_dry_coast`: non-resident with exactly one permeable contact;
- `toy_two_atom_gate`: active gate constrained by two atoms instead of three.

These toys are required before treating the v1 graph semantics as stable.
