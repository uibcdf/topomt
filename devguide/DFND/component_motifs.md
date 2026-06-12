# DFND Component Motifs

This document defines the internal motif layer of DFND wet (concavity) components.

> **Terminology.** A motif is a sub-structure *of a component* (a geometric motif
> over its atomic structure / spatial representation); see
> [`object_model.md`](object_model.md) §2.

The goal is to keep the conceptual layering explicit:

1. Delaunay triangulation provides finite tetrahedra, faces, and hull faces.
2. DFN provides wet nodes, permeable edges, `OCEAN`, and `external_links`.
3. DFND decomposition produces wet `components`.
4. Component analysis derives internal paths, motifs, and geometric descriptors.

`mouth`, `throat`, `bottleneck`, `chamber`, and related terms should not be
used as primary `family` definitions. They are derived motifs or geometric
realizations inside or around a wet `component`.

## 1. Operations

DFND should distinguish three operations.

### 1.1. Decomposition

Decomposition is the primary operation of DFND.

```text
remove OCEAN from DFN
compute connected components of the remaining finite transit graph
each connected component is a Component
enrich the Component with its ResidenceRegions and external links
```

This is not treated as auxiliary lumping. It is the core decomposition in
Delaunay Flow Network Decomposition.

### 1.2. External-Link Clustering

External-link clustering groups exterior contacts of one `component`.

```text
external_link = connected cluster of permeable boundary or hull contacts
                between a component and OCEAN
```

Default connectivity should be face-edge connectivity. Face-vertex connectivity
may be tested later, but it can merge openings that touch only at one atom and
should not be the first policy.

A geometric `mouth` can be derived from an `external_link`, but `mouth` is not
the primitive used for component-family classification.

### 1.3. Component Lumping

Component lumping is a secondary operation inside a `component`.

It aggregates nodes, edges, or paths into coarser structures so that internal
motifs can be described robustly.

Possible outputs:

- `depth_regions`;
- `capacity_regions`;
- `chambers`;
- `throat_candidates`;
- `reduced_component_graph`;
- `component_motif_graph`.

The purpose of component lumping is not to replace the primary component family. Its
purpose is to support paths, motifs, and geometric realizations.

## 2. Canonical and Experimental Parts

Canonical now (**implemented** on each `WetComponent`, see
`topomt/dfnd/components.py`):

- DFND decomposition into components (a `component` is the graph object; its
  spatial representation is its atoms — see [`object_model.md`](object_model.md));
- external-link clustering, realized per component as `external_mouth` motifs;
- unweighted topological depth from exterior-boundary nodes
  (`component.topological_depth`) plus its depth regions
  (`component.depth_regions`, also emitted as `depth_region` motifs).

Candidate or experimental:

- **chamber detection, throat detection, bottleneck ranking** — a **first attempt
  is implemented** (`_attach_capacity_motifs` in `topomt/dfnd/components.py`):
  a capacity merge tree over a component's internal faces (`R_gate`, descending)
  yields `throat_candidates` (join saddles), `chamber_candidates` (the joined
  basins) and a `bottleneck`, each scored by **topological persistence** (peak
  `R_residence` minus join `R_gate`) and gated by `min_persistence`. Validated on
  the dumbbell (one throat at the neck, two chambers; none on a plain void).
  These remain **ranked descriptors**, not a hard classifier, until the scoring /
  persistence policy is validated on real systems.
- weighted depth; capacity-based lumping beyond the above; reduced motif graph.

The same capacity merge tree is the natural seed for the multi-scale segmentation
fix (the "Disease 1" over-segmentation in
[`pathological_systems.md`](pathological_systems.md)): merging basins separated by
low-persistence saddles is exactly the watershed-merge that reunifies
over-segmented components.

Candidate operations are reported as descriptors or diagnostics until their
scoring and stability policies are fixed.

### 2.1. Three distinct persistence axes

DFND uses the word *persistence* in three related but non-interchangeable senses.
They must remain separate in APIs, records, and validation:

1. **Capacity persistence within one query.** A fixed mesh and probe query are
   analyzed across capacity thresholds such as `R_gate`. This supports chamber,
   throat, bottleneck, and watershed-like motif ranking inside one component.
2. **Probe-radius persistence across queries.** Components and motifs are matched
   across a sweep of `R_probe`. This measures scale robustness and can reveal
   events such as birth, split, merge, family change, or disappearance as probe
   size changes. It does not by itself guarantee a correct segmentation of
   subpockets within one component.
3. **Temporal persistence across trajectory frames.** Instantaneous results are
   matched across changing coordinates. This measures lifetime, breathing, and
   dynamic events and is defined in [`dynamic_topology.md`](dynamic_topology.md).

A future hierarchical representation should store the axis and query context of
every relation. Capacity, probe-scale, and temporal trees must not be collapsed
into one generic `TopographicTree` before identity and typed-relation contracts
are fixed.

For segmentation, capacity persistence is the primary within-component tool. A
probe-radius sweep is complementary evidence about robustness and accessibility
at different scales. Temporal persistence is a separate collection-level
analysis.

## 3. Topological Depth

For a concavity component `D`, define exterior-boundary nodes as nodes incident to
at least one `external_link`.

```text
external_boundary_nodes(D) = nodes in D incident to an external_link
```

The first depth definition is unweighted graph distance:

```text
topological_depth(v) = shortest number of internal DFN edges from v
                       to any external_boundary_node(D)
```

Depth layers are sets of nodes with the same topological depth:

```text
depth_layer_k(D) = {v in D | topological_depth(v) = k}
```

Depth regions are connected components induced by one depth layer:

```text
depth_region_k_i = connected component of depth_layer_k(D)
```

This is topological depth, not geometric depth. A later weighted or geometric
depth descriptor may use Euclidean distances, edge lengths, `R_gate`, or a
resistance model.

## 4. Capacity Profiles

DFND has two native local capacity quantities:

```text
node_capacity(v) = R_residence(v)
edge_capacity(e) = R_gate(e)
```

A path capacity can be summarized by the minimum capacity along the path:

```text
path_capacity(P) = min(node_capacity(v), edge_capacity(e) along P)
```

This should first be reported as a profile or ranking. Hard thresholding beyond
`probe_radius` should be avoided until benchmarked.

## 5. Paths

A path is an ordered sequence of DFN nodes and edges inside a concavity component
or inside a reduced component graph.

Useful path anchors include:

- `external_link`;
- exterior-boundary node;
- deepest depth region;
- chamber candidate;
- throat candidate;
- branch point.

Examples:

- external-link to deepest-region path;
- external-link to chamber path;
- external-link to external-link path in a channel component;
- chamber to chamber path through a throat candidate.

Paths should keep both graph identifiers and geometric realizations.

## 6. Motifs

A motif is an interpretable substructure derived from a `component`.

Candidate motif types:

- `external_mouth`: geometric realization of an `external_link`;
- `throat_candidate`: low-capacity separator between an exterior-side region
  and a deeper region;
- `bottleneck`: lowest-capacity element on a path or between two regions;
- `chamber_candidate`: deeper, relatively high-habitability region;
- `subchamber`: chamber-like region inside a larger component;
- `branch_region`: node or region where multiple internal paths diverge;
- `dead_end`: terminal branch inside a component.

Only `external_link` is currently canonical. The other motif names are useful
but should remain candidate descriptors until exact scoring and persistence
rules are validated.

## 7. Motif identity

Every emitted motif carries `parent_component_key`, `motif_support_key`, and
`motif_key`. The support key describes its exact atom-defined face or tetrahedron
support; the contextual key combines that support with the parent component and
`motif_type`. External-mouth motifs additionally carry the source
`external_link_key`. Local motif and external-link IDs remain available for
inspection and compatibility, but are not structural or temporal identity. See
[`component_identity_contract.md`](component_identity_contract.md).

## 8. Reduced Component Graph

A `reduced_component_graph` is a graph produced by component lumping.

Possible nodes:

- external links;
- depth regions;
- chamber candidates;
- throat candidates;
- branch regions.

Possible edges:

- adjacency between reduced regions;
- path relation through original DFN nodes;
- capacity-limited connection;
- depth progression relation.

A `component_motif_graph` is a semantically annotated reduced component graph. It is
the preferred representation for high-level paths and motifs once the lumping
policy is selected.

## 9. Geometric Realization

Every graph motif should be traceable back to geometry:

- tetrahedron ids;
- face ids;
- atom ids;
- residue ids;
- coordinates;
- areas or volumes when applicable.

The intended workflow is:

```text
DFN-component motif first
geometric realization second
```

This avoids forcing ambiguous molecular-surface geometry to define topology.

## 10. Dynamic Interpretation

In trajectories, motif time series can report:

- persistence of external links;
- topological-depth changes;
- capacity-profile changes;
- throat opening or closure;
- chamber persistence;
- branch birth or death;
- component family transitions.

Examples:

```text
external_link persists but throat candidate narrows
=> gated or breathing pocket component

new external_link appears
=> pocket to channel transition

deep chamber persists while external link flickers
=> cryptic or transient accessibility
```
