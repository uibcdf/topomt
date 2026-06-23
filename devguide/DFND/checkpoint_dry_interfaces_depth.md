# DFND Checkpoint: Dry Interfaces and Face Depth

Date: 2026-05-21

## Scope

This checkpoint records the first implemented characterization layer on top of
the dry complement of the DFND transit/residence graph.

The previous dry-graph checkpoint established dry components as connected
components of non-resident tetrahedra joined through shared non-permeable
faces. This checkpoint adds two derived records:

- `dry_interfaces`: explicit boundary faces where a dry component touches the
  hull/OCEAN, a resident/transit tetrahedron, or another dry component through
  a permeable contact.
- `face_depth`: graph distance inside each dry component, measured from dry
  tetrahedra that own at least one dry-interface face and propagated through
  dry edges.

## Implemented Semantics

A dry edge remains strict: two dry tetrahedra are connected inside the same dry
component only when their shared finite face is non-permeable from both sides.
This keeps the dry graph tied to barrier connectivity rather than probe
transit.

A dry interface is not a dry edge. It is a boundary/contact record for a dry
component. The current implementation emits one interface record for each dry
tetrahedron face that is not an internal dry non-permeable face.

The current `interface_kind` values are:

- `hull_permeable`: dry face on the convex hull whose gate is permeable; this
  touches OCEAN under the current graph abstraction.
- `hull_blocked`: dry face on the convex hull whose gate is non-permeable.
- `dry_permeable_contact`: dry-dry shared face that is permeable and therefore
  does not belong to the dry-edge graph.
- `transit_contact`: dry face touching a resident/transit neighbor with at
  least two permeable contacts.
- `resident_wall`: dry face touching a resident neighbor that is not classified
  as a transit-like connector by local permeable-contact count.

`touches_ocean` is intentionally stricter than `touches_hull`: it is true only
for hull faces that are also permeable.

## Face Depth

`face_depth` is a topological depth, not a Euclidean burial depth. It is computed
per dry component:

1. Boundary nodes are the dry tetrahedra that own at least one dry-interface
   face.
2. Boundary nodes receive depth `0`.
3. Depth then propagates by breadth-first search through dry edges.
4. Nodes unreachable from the interface seed set keep depth `None`.

Each dry component now records:

- `dry_interface_ids`;
- `dry_boundary_tetrahedron_ids`;
- `face_depth_by_tetrahedron`;
- `face_depth_min`;
- `face_depth_max`;
- `face_depth_mean`.

## Tests

The active graph-contract tests now cover:

- dry interfaces reference existing component ids and global face ids;
- dry interfaces are exposed consistently through both `raw['dry_interfaces']`
  and `dry['interfaces']`;
- dry boundary tetrahedra have depth `0`;
- face-depth values are consistent with dry-edge BFS propagation;
- singleton dry components with interfaces have depth `0`.

## Interpretation

This is still a structural layer, not a finalized convexity-feature detector.
It gives DFND a concrete dry complement suitable for later `DryMotif`, rim,
wall, separator, lining, and buried-core characterization without forcing those
motif names into the public v1 feature taxonomy yet.

## Remaining Work

The next dry-network steps are:

- decide which dry-interface kinds should be promoted to public metadata;
- decide whether face depth should be computed from all interfaces or only from
  OCEAN-facing/permeable interfaces for specific analyses;
- define dry motif candidates using `dry_components`, `dry_edges`,
  `dry_interfaces`, and `face_depth`;
- keep validating the behavior on real small molecular systems before exposing
  dry-derived features as stable public API.
