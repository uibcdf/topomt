# DFND Checkpoint: Canonical Transit Edges

**Date:** 2026-06-12  
**Status:** implemented and verified

## Problem

DFND previously thresholded the same `R_gate` twice with incompatible rules:
faces used the generous permeability policy, while wet-graph edges additionally
required `R_gate > R_probe + epsilon`. A shared face could therefore be recorded
as permeable and contribute to connector classification without connecting its
two transit nodes.

## Decision

DFND uses one canonical face decision:

```text
transit_edge(T_i, T_j) =
    T_i and T_j are transit nodes
    and their shared face is permeable
```

Marginality is diagnostic, not a separate connectivity decision. A marginal
face admitted by the generous permeability policy creates a transit edge when
both incident tetrahedra are transit nodes.

## Implementation

- Removed the second strict `R_gate > R_probe + epsilon` threshold.
- Materialized `transit_edge` on oriented raw face records.
- Migrated component extraction, path-capacity reporting, wet motif adjacency,
  centerline construction, experimental interface graphs, graph rendering, and
  face selectors to the canonical decision.
- Preserved shared-face symmetry: both oriented records have identical `R_gate`,
  permeability, margins, and `transit_edge` state.

## Margin Contract

Every face exposes:

```text
gate_margin = R_gate - R_probe
effective_gate_margin = R_gate - (R_probe - epsilon - permeability_tolerance)
```

A generously admitted marginal face may have negative `gate_margin`, while its
`effective_gate_margin` is non-negative. Values are not silently truncated.

Components expose:

- `path_gate_margin_min`: minimum physical margin over canonical internal transit
  edges;
- `path_effective_gate_margin_min`: minimum effective-policy margin;
- `path_capacity_min`: compatibility alias of `path_gate_margin_min`.

## Verification

Tests cover:

- exact-threshold shared faces connecting resident transit nodes;
- a non-zero `permeability_tolerance` changing graph connectivity;
- preservation of negative physical and positive effective margins;
- the bidirectional invariant between permeable shared faces and transit edges;
- shared-face orientation symmetry;
- existing graph, centerline, wet/dry adjacency, component, and promotion tests.

The complete DFND test group passed in 12 processes on 2026-06-12.

## Remaining Related Work

- Decide whether `path_capacity_min` should eventually be deprecated in favor of
  the two explicit margin names.
- Define a quantitative centerline contract; canonical connectivity alone does
  not validate straight center-to-center probe trajectories.
- Continue pathological and molecular near-threshold validation.
