# DFND Dry Graph Basics Checkpoint

This checkpoint records the first implementation-hardening pass for the DFND dry
graph.

## Scope

This is an engineering checkpoint for raw dry components. It does not promote
convexity, boundary, mixed features, or dry motifs to the public API.

## Current Dry Graph Contract

For a selected probe radius:

- dry nodes are non-resident tetrahedra;
- dry edges connect two dry tetrahedra only through a shared finite face that is
  non-permeable from both tetrahedron-owner records;
- permeable dry-dry shared faces do not create dry graph edges;
- every dry node belongs to exactly one `dry_component` unless filtered by a
  reporting policy;
- `dry.core` is the largest dry component after sorting by size;
- `dry.islands` are the remaining dry components;
- `dry.components` preserves all reported dry components.

## Records Added

Dry component records now include:

- `dry_edges`: source/target tetrahedra, owner face indices, global face id, and
  face atom triple for every dry edge;
- `dry_edge_face_ids`: compact list of the face ids used by dry edges.

## Tests Added

`tests/test_dfnd_graph_contract.py` now checks that:

- dry components cover all and only non-resident tetrahedra;
- dry edges use only non-permeable shared faces;
- permeable shared faces between dry tetrahedra do not connect dry components;
- `core`, `islands`, and `components` remain internally consistent.

## Explicit Non-Scope

Still pending:

- dry interfaces;
- face depth;
- dry-interface signatures;
- dry motifs such as cores, protrusions, ridges, rims, walls, separators, or
  lining regions;
- public `ConvexityFeature`, `BoundaryFeature`, or `MixedFeature` objects.
