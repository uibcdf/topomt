# DFND Domain Motifs

This document defines the internal motif layer of DFND concavity domains.

The goal is to keep the conceptual layering explicit:

1. Delaunay triangulation provides finite tetrahedra, faces, and hull faces.
2. DFN provides wet nodes, permeable edges, `OCEAN`, and `external_links`.
3. DFND decomposition produces `concavity_domains`.
4. Domain analysis derives internal paths, motifs, and geometric descriptors.

`mouth`, `throat`, `bottleneck`, `chamber`, and related terms should not be
used as primary domain-family definitions. They are derived motifs or geometric
realizations inside or around a `concavity_domain`.

## 1. Operations

DFND should distinguish three operations.

### 1.1. Decomposition

Decomposition is the primary operation of DFND.

```text
remove OCEAN from DFN
compute connected components of the remaining finite transit graph
each component is a TransitDomain
interpret TransitDomain plus ResidenceRegions as a concavity_domain
```

This is not treated as auxiliary lumping. It is the core decomposition in
Delaunay Flow Network Decomposition.

### 1.2. External-Link Clustering

External-link clustering groups exterior contacts of one `concavity_domain`.

```text
external_link = connected cluster of permeable boundary or hull contacts
                between a concavity_domain and OCEAN
```

Default connectivity should be face-edge connectivity. Face-vertex connectivity
may be tested later, but it can merge openings that touch only at one atom and
should not be the first policy.

A geometric `mouth` can be derived from an `external_link`, but `mouth` is not
the primitive used for domain-family classification.

### 1.3. Domain Lumping

Domain lumping is a secondary operation inside a `concavity_domain`.

It aggregates nodes, edges, or paths into coarser structures so that internal
motifs can be described robustly.

Possible outputs:

- `depth_regions`;
- `capacity_regions`;
- `chambers`;
- `throat_candidates`;
- `reduced_domain_graph`;
- `domain_motif_graph`.

The purpose of domain lumping is not to replace the primary domain family. Its
purpose is to support paths, motifs, and geometric realizations.

## 2. Canonical and Experimental Parts

Canonical now (**implemented** on each `WetComponent`, see
`topomt/dfnd/components.py`):

- DFND decomposition into components (a `component` is the graph object; its
  `domain` is its atoms — see [`object_model.md`](object_model.md));
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
over-segmented domains.

Candidate operations are reported as descriptors or diagnostics until their
scoring and stability policies are fixed.

## 3. Topological Depth

For a concavity domain `D`, define exterior-boundary nodes as nodes incident to
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

A path is an ordered sequence of DFN nodes and edges inside a concavity domain
or inside a reduced domain graph.

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
- external-link to external-link path in a channel domain;
- chamber to chamber path through a throat candidate.

Paths should keep both graph identifiers and geometric realizations.

## 6. Motifs

A motif is an interpretable substructure derived from a `concavity_domain`.

Candidate motif types:

- `external_mouth`: geometric realization of an `external_link`;
- `throat_candidate`: low-capacity separator between an exterior-side region
  and a deeper region;
- `bottleneck`: lowest-capacity element on a path or between two regions;
- `chamber_candidate`: deeper, relatively high-habitability region;
- `subchamber`: chamber-like region inside a larger domain;
- `branch_region`: node or region where multiple internal paths diverge;
- `dead_end`: terminal branch inside a domain.

Only `external_link` is currently canonical. The other motif names are useful
but should remain candidate descriptors until exact scoring and persistence
rules are validated.

## 7. Reduced Domain Graph

A `reduced_domain_graph` is a graph produced by domain lumping.

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

A `domain_motif_graph` is a semantically annotated reduced domain graph. It is
the preferred representation for high-level paths and motifs once the lumping
policy is selected.

## 8. Geometric Realization

Every graph motif should be traceable back to geometry:

- tetrahedron ids;
- face ids;
- atom ids;
- residue ids;
- coordinates;
- areas or volumes when applicable.

The intended workflow is:

```text
DFN-domain motif first
geometric realization second
```

This avoids forcing ambiguous molecular-surface geometry to define topology.

## 9. Dynamic Interpretation

In trajectories, motif time series can report:

- persistence of external links;
- topological-depth changes;
- capacity-profile changes;
- throat opening or closure;
- chamber persistence;
- branch birth or death;
- domain family transitions.

Examples:

```text
external_link persists but throat candidate narrows
=> gated or breathing pocket domain

new external_link appears
=> pocket_domain to channel_domain transition

deep chamber persists while external link flickers
=> cryptic or transient accessibility
```
