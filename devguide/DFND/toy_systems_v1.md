# DFND Toy Systems v1

This document defines the minimal synthetic systems required to validate the DFND abstract contract before using real molecular benchmarks.

The toy suite must test geometry, graph connectivity, residence, transit, external-link clustering, and the access x residence classifier independently.

## 1. General Assertions

Every toy should report at least:

```text
n_tetrahedra
n_faces
n_transit_nodes
n_resident_nodes
n_external_links
has_residence
has_open_interior
family
flags
```

`has_residence` and `has_open_interior` must be asserted separately. `wet_open` is a descriptor, not the family gate.

## 2. Toy Void

Purpose: validate an enclosed resident component with no external access.

Expected result:

```text
n_external_links = 0
has_residence = true
family = void
```

Required checks:

- no permeable path to `OCEAN` exists;
- the probe can reside in at least one finite tetrahedron;
- no-link non-resident structures are not classified as voids.

## 3. Toy Wet-Sealed Regular Tetrahedron

Purpose: validate that a resident sealed cell is realizable and classified correctly.

Analytic fixture:

```text
atom 1: ( 1.874,  1.874,  1.874)   radius = 1.7 A
atom 2: ( 1.874, -1.874, -1.874)   radius = 1.7 A
atom 3: (-1.874,  1.874, -1.874)   radius = 1.7 A
atom 4: (-1.874, -1.874,  1.874)   radius = 1.7 A
probe = 1.4 A
```

Expected approximate values:

```text
R_residence ~= 1.55 A
R_gate for each face ~= 1.36 A
```

Expected result:

```text
local_class = wet_sealed
n_external_links = 0
has_residence = true
has_open_interior = false
family = void
```

A `wet_sealed` node with external links is invalid under the v1 local DFN contract because sealed means no permeable finite faces.

## 4. Toy Wet-Coast Pocket With One Link

Implementation status: covered by `tests/test_dfnd_graph_contract.py::test_wet_coast_one_link_domain_is_pocket_not_surface_concavity`.

Purpose: validate the decisive correction from `wet_open` gating to residence gating.

Expected result:

```text
n_external_links = 1
has_residence = true
has_open_interior = false
family = pocket
```

Required checks:

- resident content is sufficient for pocket classification;
- lack of `wet_open` does not force `surface_concavity`;
- local `wet_coast` composition is preserved in raw records.

## 5. Toy Surface Dent With One Link

Implementation status: covered by `tests/test_dfnd_graph_contract.py::test_surface_dent_one_link_has_no_residence`.

Purpose: validate a one-mouth non-resident contact/dent component.

Expected result:

```text
n_external_links = 1
has_residence = false
has_open_interior = false
family = surface_concavity
```

Required checks:

- external access exists;
- absence of resident nodes prevents pocket classification;
- the result is reported as provisional if morphology is not yet validated.

## 6. Toy Pocket

Purpose: validate a one-opening accessible concavity with resident content.

Expected result:

```text
n_external_links = 1
has_residence = true
family = pocket
```

Required checks:

- the external link is one connected face-edge cluster;
- topological depth increases from external-boundary nodes inward;
- dry interfaces support wall or lining candidates without changing the pocket family.

## 7. Toy Multi-External-Link Component

Implementation status: covered by `tests/test_dfnd_graph_contract.py::test_multi_external_link_domain_has_distinct_external_links`.

Purpose: validate a multi-opening resident component.

Expected result:

```text
n_external_links >= 2
has_residence = true
family = multi_external_link
```

Required checks:

- two independent external links are not merged;
- there is a finite transit path between exterior-boundary regions;
- `channel` remains a shorthand until morphology or path analysis is added.

## 8. Toy Nonresident Passage With Two Links

Implementation status: covered by `tests/test_dfnd_graph_contract.py::test_nonresident_passage_two_links_has_no_residence`.

Purpose: validate a pass-through non-resident transit component.

Expected result:

```text
n_external_links >= 2
has_residence = false
family = nonresident_passage
```

Required checks:

- the component is not promoted to public `Channel` by default;
- transit connectors are retained in raw records;
- path descriptors can be computed later without changing the primary label.

## 9. Toy Subprobe Buried No-Residence Component

Implementation status: covered by `tests/test_dfnd_graph_contract.py::test_degenerate_subprobe_domain_has_no_links_and_no_residence`.

Purpose: validate no-link non-resident structures.

Expected result:

```text
n_external_links = 0
has_residence = false
family = degenerate_subprobe
```

Required checks:

- the component is not classified as `void`;
- default reporting may filter it from public features while preserving raw records.

## 10. Toy Dry-Open Cut

Implementation status: covered by `tests/test_dfnd_graph_contract.py::test_dry_open_cut_connector_policy_can_merge_resident_regions`.

Purpose: validate that non-resident transit connectors do not cut the movement graph.

Expected result:

```text
two resident regions connected only through one dry_open transit connector
n_components = 1
```

Required checks:

- dropping the connector would split the component;
- retaining the connector preserves physical transit;
- connector contributes connectivity but not resident volume.

## 11. Toy Terminal Dry-Coast

Purpose: validate one-sided non-resident contact.

Expected result:

```text
has_residence = false
n_permeable_contacts = 1
transit_role = terminal_contact
```

Required checks:

- the node is retained in raw/contact diagnostics;
- it does not create a through-transit edge by itself.

## 12. Toy Two-Atom Gate

Purpose: validate the active-gate edge case where a face opening is constrained by two atoms rather than all three face atoms.

Expected result:

```text
R_gate_face_candidate is checked against active constraints
flags include active_gate_degeneracy or equivalent diagnostic if needed
```

Required checks:

- the face-plane construction remains valid;
- inactive atoms do not make the gate artificially too small or too large;
- final policy is explicit in numerical diagnostics.

## 13. Toy Touching External Links

Implementation status: primitive clustering covered by `tests/test_dfnd_graph_contract.py::test_external_link_clustering_uses_face_edge_connectivity` and `tests/test_dfnd_graph_contract.py::test_external_link_clustering_does_not_merge_vertex_only_contact`.

Purpose: validate that face-edge connectivity does not merge openings that only touch at a vertex.

Expected result:

```text
n_external_links = 2
external_link_connectivity = face_edge_connectivity
```

Required checks:

- face-vertex contact alone is insufficient for one external link;
- switching to an experimental face-vertex policy would be a separate test.

## 14. Implementation Order

Recommended implementation order:

1. `toy_wet_sealed_regular_tetrahedron`.
2. `toy_dry_open_cut`.
3. `toy_wet_coast_pocket_1link`.
4. `toy_surface_dent_1link`.
5. `toy_nonresident_passage_2links`.
6. `toy_subprobe_buried_noresidence`.
7. `toy_touching_external_links`.
8. `toy_two_atom_gate`.

These toys are enough to validate the current abstract contract before real-system benchmarking.
