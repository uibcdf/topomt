# DFND Residence, Transit, and Contact Contract

Current scope note — 2026-11-09, #173: retain the implemented graph predicates
in this contract while reading physical-transit language as historical rationale.
The [theory review](core_theory_review_2026_11_06.md) and
[public conditional properties](../../docs/content/dfnd/appendices/mathematical_properties.md)
state why exact existential nonresidence cannot certify physical pass-through.
That scientific decision remains #76. Incidence admission and tolerance wording
below are reconciled with current source, without changing runtime policy.

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
`residence_tolerance` (a length band, default `0.0`, user-controllable) widens
the threshold. It can be varied in declared sensitivity studies; it is not a
calibrated model of structural flexibility or coordinate uncertainty.
Marginal tetrahedra (within the slack of the threshold) are counted resident but
still flagged in raw records.

### 2.2. Face State

```text
capacity_pass(F) = R_gate(F) >= R_probe - epsilon - permeability_tolerance
admitted(T, F) = capacity_pass(F) and (
    gate_intrusion_policy == 'flag_only' or not intrusion_suspect(T, F))
non_permeable(T, F) = not admitted(T, F)
marginal_face(F) = abs(R_gate(F) - R_probe) <= epsilon + permeability_tolerance
```

Policy is **generous toward permeability** (same rationale as residence): the
numerical `epsilon` favours permeable, and `permeability_tolerance` (a length
band, default `0.0`, user-controllable) widens it further.
The capacity predicate is shared, but `block_suspect` additionally blocks an
owner incidence according to its opposite-apex flag. Internal edges require
both incidences admitted; marginality remains recorded even if policy blocks
one. Both tolerances are query parameters of
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
- `transit_connector`: nonresident node admitted by the selected multiple-contact
  policy. This is graph connectivity; continuous all-atom passage remains unproved.
- `terminal_contact`: the probe can touch or enter from one side, but cannot
  cross through because there is no second permeable contact.
- `non_transit`: no residence and no passage.

## 4. Transit Graph

The transit graph is the primary discrete connectivity graph.

Nodes:

```text
transit_node(T) = transit_state in {resident_transit, transit_connector}
```

Edges:

```text
transit_edge(T_i, T_j) =
    T_i and T_j are transit_nodes
    and both owner incidences of their shared finite face are admitted
```

Face capacity is unique; owner admission can differ under `block_suspect`.
This is the canonical two-sided transit-edge predicate. Implementations must not
apply a second threshold to `R_gate` after the shared face has been classified.
A marginal face admitted by the generous permeability policy remains flagged as
marginal and creates a transit edge when both incident tetrahedra are transit
nodes.

For reporting:

```text
gate_margin = R_gate - R_probe
effective_gate_margin = R_gate - (R_probe - epsilon - permeability_tolerance)
```

The physical margin may be slightly negative for a generously admitted face;
the effective-policy margin is non-negative for a permeable face. Neither value
is silently truncated.

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

A current raw `ResidenceRegion` record aggregates the resident nodes of one
`Component`, with its connectors retained separately. The implementation emits
one such record per transit component with resident content. It does not split
that resident subset into connected components of the resident-only subgraph.
Several resident-only connected subsets can therefore share one aggregate
through transit connectors. Do not infer their count from the raw record count.

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

**Native wall-count override (checked first):** a resident component with
**`n_wall_faces == 0`** is classified `percolating`, regardless of access.
This counts complete carrier faces under the discrete owner-admission rules;
it does not mean every boundary point is physically free. The earlier
fully-permeable/porous interpretation and unqualified one-link consequence are
historical rationale, not a physical guarantee or an additional classifier
predicate. The four physical patches versus one native link on the frozen
tetrahedron illustrate the distinction; #151 owns physical refinement. Otherwise
the access × residence table applies. No runtime classification is changed.

| Access | Residence | Raw label | v1 interpretation |
|---:|---|---|---|
| 0 | yes | `void` | closed resident cavity |
| 0 | no | `degenerate_subprobe` | raw/filter label |
| 1 | yes | `pocket` | one-mouth resident concavity (with walls) |
| 1 | no | `surface_concavity` | one-mouth non-resident contact/dent |
| >=2 | yes | `channel` | multi-mouth resident component (maps to the public `Channel`) |
| >=2 | no | `nonresident_passage` | provisional pass-through contact |
| any | yes, **0 native walls** | `percolating` | native wall-count override (shape_type `neutral`), not physical patch topology |

`has_open_interior` is a descriptor, not the family gate. The graph substrate
must no longer be restricted to resident nodes only. The exact
`surface_concavity` and pocket boundary remains a validation item.

## 8. Dry Banks and Local Nonresidence Diagnostics

The bank node set is the complement of finite transit, excluding enabled
connectors. Its face adjacency requires both nonpermeable owner incidences;
edge/vertex modes are different groupings. The historical three-role inventory
below describes local nonresidence diagnostics, not bank membership:

```text
non_resident terminal_contact nodes
non_resident non_transit nodes
non_resident transit_connector nodes
```

Raw per-cell residence/transit roles preserve this distinction. A connector can
therefore be locally nonresident while belonging to transit-component support
and to no bank. Local diagnostic labels must not be counted as extra bank nodes.

## 9. Required Toys

The toy set must include:

- `toy_wet_sealed_regular_tetrahedron`: resident but all faces non-permeable;
- `toy_dry_open_cut`: two resident regions connected only through a
  non-resident transit connector;
- `toy_terminal_dry_coast`: non-resident with exactly one permeable contact;
- `toy_two_atom_gate`: active gate constrained by two atoms instead of three.

These toys are required before treating the v1 graph semantics as stable.
