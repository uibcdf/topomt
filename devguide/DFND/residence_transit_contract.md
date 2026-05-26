# DFND Residence, Transit, and Contact Contract

This document records the core correction introduced after the external
geometric review: DFND must separate probe residence, probe transit, and probe
contact.

> **Terminology.** A connected component of the transit graph is a `component`
> (the legacy terms "TransitDomain" and "domain" are now `component`; its atoms are
> its spatial representation); the public object is a `feature`. See
> [`object_model.md`](object_model.md).

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
resident(T)     = R_residence(T) >= R_probe - epsilon - residence_tolerance
non_resident(T) = not resident(T)
marginal_residence(T) = abs(R_residence(T) - R_probe) <= epsilon + residence_tolerance
```

Policy is **generous toward residence**. The numerical `epsilon` is applied in
favour of resident, so the `>=` equality is robust to floating-point error.
`residence_tolerance` (physical, default `0.0`, user-controllable) widens the
threshold further to absorb structural flexibility / coordinate imprecision.
Marginal tetrahedra (within the slack of the threshold) are counted resident but
still flagged in raw records.

### 2.2. Face State

```text
permeable(F)     = R_gate(F) >= R_probe - epsilon - permeability_tolerance
non_permeable(F) = not permeable(F)
marginal_face(F) = abs(R_gate(F) - R_probe) <= epsilon + permeability_tolerance
```

Policy is **generous toward permeability** (same rationale as residence): the
numerical `epsilon` favours permeable, and `permeability_tolerance` (physical,
default `0.0`, user-controllable) widens it further. Marginal faces are counted
permeable but still flagged. Both tolerances are query parameters of
`get_topography(...)` / `dfnd(...)` and are recorded in `raw['parameters']`.

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

## 5. Component

A `Component` is a connected component of the transit graph after removing
`OCEAN` and its incident edges.

```text
Component = connected component of finite transit nodes
```

A `Component` can contain both resident and non-resident transit nodes.
Non-resident transit nodes contribute to connectivity, not to resident volume.

## 6. ResidenceRegion

A `ResidenceRegion` is a connected subset of resident nodes inside one
`Component`. Connectivity between resident nodes may be direct or may be
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

## 7. Component and Feature Classification

A `component` bundles its resident content, external links, lining atoms, and
volume metrics (its graph and spatial representations — there is no separate "domain"; see
[`object_model.md`](object_model.md) §2). A `feature` is the public `Topography`
object (Pocket, Void, Channel) derived from one or more components.

The primary classifier uses two axes (access and residence) plus an **enclosure
override**.

```text
access = n_external_links in {0, 1, >=2}
has_residence = n_resident_nodes >= 1
has_open_interior = any resident node is wet_open
n_wall_faces = non-permeable boundary faces of the component (to OCEAN or another component)
```

**Enclosure override (checked first):** a resident component with **`n_wall_faces == 0`**
is fully permeable / exposed (porous) — not a concavity — and is classified
`percolating`, regardless of access. (Mathematically such a component always has
exactly one external link, but that is a consequence, not the criterion.) Voids
always have walls (0 mouths => all boundary non-permeable), so they are never
percolating. Otherwise the access × residence table applies:

| Access | Residence | Raw label | v1 interpretation |
|---:|---|---|---|
| 0 | yes | `void` | closed resident cavity |
| 0 | no | `degenerate_subprobe` | raw/filter label |
| 1 | yes | `pocket` | one-mouth resident concavity (with walls) |
| 1 | no | `surface_concavity` | one-mouth non-resident contact/dent |
| >=2 | yes | `multi_external_link` | multi-mouth resident component; `channel` shorthand |
| >=2 | no | `nonresident_passage` | provisional pass-through contact |
| any | yes, **0 walls** | `percolating` | fully permeable/exposed resident region (shape_type `neutral`) |

`has_open_interior` is a descriptor, not the family gate. The graph substrate
must no longer be restricted to resident nodes only. The exact
`surface_concavity` and pocket boundary remains a validation item.

## 8. Dry Components After Transit Separation

Dry graph construction remains useful, but it should not steal transit
connectors from the movement graph.

Dry records should preserve:

```text
non_resident terminal_contact nodes
non_resident non_transit nodes
non_resident transit_connector nodes
```

`transit_connector` nodes may appear both in transit-component provenance and in
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
