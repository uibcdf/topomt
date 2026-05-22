# DFND Dynamic Topology

This document defines the DFND-native strategy for tracking molecular
topography along molecular dynamics trajectories.

The goal is not to import historical CASTp notes into DFND. The goal is to
rewrite the useful dynamic-topography ideas in the language of DFND: a
Delaunay flow network whose nodes, faces, gates, and connected components can
be followed over time.

## 1. Core Idea

DFND represents empty space as a graph:

- nodes are Delaunay tetrahedra;
- edges are shared triangular faces;
- node capacity is tetrahedron habitability, `R_residence`;
- edge capacity is face permeability, `R_gate`;
- voids, surface concavities, pockets, and channels are derived connected components and
  boundary structures of this graph.

For a trajectory, the coordinates change with time, but many graph elements
retain an internal molecular identity:

- a tetrahedron can be identified by the four atom indices that define it;
- a face can be identified by the three atom indices that define it;
- an external link can be described as a connected set of permeable boundary faces;
- a pocket can be described as a connected component of tetrahedra and faces,
  plus the lining atoms and residues that stabilize its identity.

This gives DFND a natural route to dynamic pocket tracking that does not rely
only on spatial shape matching or grid overlap.

## 2. Static Versus Dynamic Objects

DFND should distinguish an instantaneous topography from a dynamic feature.

An instantaneous feature is the result of one frame:

- `Void(frame=k)`;
- `SurfaceConcavity(frame=k)`;
- `Pocket(frame=k)`;
- `Channel(frame=k)`.

`ExternalLink(frame=k)` and derived `Mouth(frame=k)` descriptors can be
attached to these domains/features, but they are not primary concavity-domain
families.

A dynamic feature is an object that links instantaneous features across frames:

```python
DynamicFeature(
    dynamic_feature_id='dyn_pocket_7',
    feature_type='pocket',
    instances_by_frame={
        0: 'pocket_3',
        1: 'pocket_2',
        2: 'pocket_2',
    },
    events=[
        {'frame': 0, 'type': 'birth'},
        {'frame': 2, 'type': 'external_link_opening'},
    ],
    metrics_time_series={
        'volume': [210.1, 225.4, 219.7],
        'n_external_links': [0, 1, 1],
        'minimum_gate_radius': [0.9, 1.5, 1.4],
    },
)
```

The static feature remains the per-frame result. The dynamic feature is the
temporal identity that collects instances, events, and time series.

## 3. Preferred Tracking Hierarchy

DFND should use a hierarchy of identity evidence.

### 3.1. Stable Internal Identity

When the Delaunay element remains present, identity is direct:

- same tetrahedron atom quadruplet means same network node;
- same face atom triplet means same network edge or gate;
- time series such as `R_residence(t)` and `R_gate(t)` are attached directly to
  those internal identifiers.

This is the strongest DFND advantage. A pocket can move, deform, or rotate
with the protein without requiring a global structural alignment.

### 3.2. Component-Level Identity

Pockets, voids, and channels are not single tetrahedra; they are components.
Their frame-to-frame identity should be inferred from a composite score:

- overlap of tetrahedron identifiers;
- overlap of face identifiers;
- Jaccard similarity of lining atoms and residues;
- similarity of external-link atom sets;
- continuity of connected-component neighborhood;
- continuity of centroid and volume, used as secondary evidence.

Coordinates should help resolve ambiguity, but they should not be the primary
identity model when graph identifiers are available.

### 3.3. Fallback When the Triangulation Changes

Large conformational changes can flip Delaunay tetrahedra. When direct
tetrahedron identity is unstable, DFND should fall back to more robust
molecular descriptors:

- lining atoms;
- lining residues;
- external-link atoms;
- nearby gatekeeper faces;
- pocket center and volume;
- local contact environment.

This fallback keeps the dynamic analysis usable without pretending that the
reference triangulation is invariant under all motions.

## 4. Dynamic State Variables

For each tracked tetrahedron:

- `R_residence(t)`: whether the probe can inhabit the node;
- node state over time: `dry`, `wet`, `COAST`, or `OCEAN`;
- local volume or tetrahedron volume;
- chemical labels inherited from the four atoms.

For each tracked face:

- `R_gate(t)`: whether the probe can pass through the face;
- gate state over time: closed, marginal, or open;
- variance and threshold-crossing frequency;
- atoms and residues acting as the gatekeepers.

For each tracked feature:

- volume time series;
- number of external links;
- external-link area time series;
- minimum gate radius;
- accessibility state;
- connected-component size;
- lining atom and residue persistence;
- transitions between `void`, `pocket`, and `channel`.

## 5. Events

DFND should expose explicit topological events.

Basic identity events:

- `birth`: a feature appears with no clear precursor;
- `death`: a feature disappears with no clear successor;
- `continuation`: a feature maps cleanly to a successor;
- `split`: one feature maps to multiple successors;
- `merge`: multiple features map to one successor.

Accessibility events:

- `external_link_opening`: a boundary contact cluster becomes permeable;
- `external_link_closure`: an external link becomes non-permeable;
- `void_to_pocket`: a buried component gains solvent access and has a wet-open interior;
- `void_to_surface_concavity`: a buried component gains solvent access but remains all wet-coast;
- `pocket_to_void`: an accessible component loses solvent access;
- `pocket_to_channel`: a second independent external link appears;
- `channel_to_pocket`: one channel external link closes.

Gate events:

- `gate_opening`: `R_gate(t)` crosses above `R_probe`;
- `gate_closure`: `R_gate(t)` crosses below `R_probe`;
- `marginal_gate`: `R_gate(t)` stays within a tolerance band around
  `R_probe`;
- `gate_breathing`: repeated opening and closing of the same face or external link.

## 6. Temporal Metrics

Feature-level metrics:

- lifetime in frames and physical time;
- persistence ratio;
- volume mean, variance, and extrema;
- accessibility ratio;
- external-link openness ratio;
- number of split and merge events;
- number of type transitions;
- topological stability score.

Gate-level metrics:

- open probability;
- closed probability;
- marginal probability;
- mean and variance of `R_gate(t)`;
- first opening time;
- residence time in open episodes.

Network-level metrics:

- temporal connectivity matrix between tetrahedra;
- probability that two nodes belong to the same component;
- component stability heatmap;
- dynamic bottleneck map;
- graph communities that persist across the trajectory.

## 7. Temporal Connectivity Matrix

For a trajectory with `F` frames, DFND can define a connectivity probability:

```text
M[i, j] = number of frames where nodes i and j are connected / F
```

Interpretation:

- `M[i, j]` close to 1 means stable connectivity;
- `M[i, j]` close to 0 means stable separation;
- intermediate values indicate breathing, gating, or conformational switching.

This matrix is one of the cleanest ways to summarize dynamic pocket topology.
It also avoids voxel grids and global structural fitting.

## 8. Matching Strategy Between Frames

A pragmatic first implementation can use this order:

1. Generate DFND topography for each frame.
2. Build candidate matches between features in consecutive frames.
3. Score candidates using graph overlap, lining atoms, external links, and geometry.
4. Resolve one-to-one continuations with bipartite matching.
5. Detect unmatched features as births or deaths.
6. Detect one-to-many and many-to-one mappings as splits or merges.
7. Build `DynamicFeature` records.
8. Compute time series and event summaries.

The matching score should be explicit:

```text
S(F, G) =
    w_graph * graph_overlap(F, G)
  + w_lining * lining_similarity(F, G)
  + w_external_link * external_link_similarity(F, G)
  + w_geometry * geometry_similarity(F, G)
```

The default should favor graph and lining evidence over centroid/shape
evidence.

## 9. Smoothing and Flickering

MD trajectories can produce short-lived numerical or physical flickering:

- one-frame external-link openings;
- marginal gates oscillating around `R_probe`;
- micro-splits of a component;
- transient one-tetrahedron features.

DFND should support optional temporal smoothing:

- minimum event duration;
- majority filter over a time window;
- tolerance band for marginal gates;
- minimum persistence threshold for reported dynamic features.

These filters must be explicit parameters. They should never be hidden inside
the core static detector.

## 10. Relationship to Pharmacophores

Dynamic pharmacophores are a downstream application, not the foundation of the
dynamic DFND model.

The foundation is the dynamic graph:

- nodes and faces tracked over time;
- void, surface-concavity, pocket, and channel domains tracked as dynamic features;
- events and metrics extracted from graph evolution.

Once this graph is available, pharmacophoric labels can be overlaid on stable
`wet` and `COAST` nodes to identify persistent interaction hotspots.

## 11. Minimal Implementation Target

The first useful implementation should not try to solve every dynamic problem.
It should provide:

- per-frame DFND execution;
- stable identifiers for tetrahedra and faces;
- feature matching between consecutive frames;
- `DynamicFeature` records;
- lifetime and persistence metrics;
- volume and external-link time series;
- gate opening and closure events.

This would already make DFND meaningfully different from static pocket
detectors and from grid-based dynamic occupancy methods.

## 12. Open Questions

- Should the first dynamic implementation use a fixed reference triangulation,
  frame-wise retriangulation, or both modes?
- How should we define graph overlap when tetrahedra flip but lining residues
  remain stable?
- What tolerance band should define a marginal gate around `R_probe`?
- Should external links and derived mouths be tracked as face clusters, as atom sets, or both?
- How should explicit water occupancy be integrated as validation rather than
  as a core geometric criterion?
