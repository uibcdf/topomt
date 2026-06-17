# DFND Component Identity Contract

Recorded on 2026-06-06. This document is the authoritative contract for the
identity, indexing, ranking, and temporal tracking of wet and dry DFND
components.

It complements [`object_model.md`](object_model.md). If older DFND prose calls
`component_id` a stable structural or temporal identifier, this document
supersedes that wording.

## 1. Why the fields are separate

A component participates in several operations that require different notions
of identity:

- locating it in one result;
- presenting it to a user;
- ranking it by a declared metric;
- testing exact equality of its tetrahedral support;
- identifying it within one contextualized DFND result;
- following it through a trajectory with births, deaths, splits, and merges.

No single identifier can answer all these questions without ambiguity.

## 2. Static component fields

| Field | Contract | Scope |
| --- | --- | --- |
| `component_index` | Base-0 position in the current component collection | One result; changes if the collection order changes |
| `node_count_rank` | Base-1 rank by descending number of tetrahedron nodes | One result |
| `size_rank` | Deprecated compatibility alias of `node_count_rank` | One result |
| `component_id` | Human-readable local label derived from side and rank, such as `WET-1` or `DRY-1` | One result |
| `graph_label` | Internal connected-component algorithm label | Internal implementation detail |
| `support_key` | Reproducible identity of the exact tetrahedron support | Same atom-index substrate |
| `component_key` | Reproducible identity of the classified component in one contextualized result | One contextualized result |

The current canonical ranking metric is `n_nodes`, the number of tetrahedra in
the component. Therefore `WET-1` means the wet component with the greatest
`n_nodes`, not necessarily the wet component with the greatest geometric or
solvent-volume estimate.

`component_index` and `node_count_rank` currently differ only by one because
the collection is stored in rank order. They remain separate concepts:
`component_index` is collection position; `node_count_rank` is a metric rank.
Neither is an intrinsic or persistent identity.

## 3. Deterministic ranking

Wet and dry components are ranked independently.

The canonical order is:

```text
descending n_nodes, then ascending support_key
```

Using `support_key` as the tie-breaker makes equal-size ordering deterministic.
`graph_label` must not determine public ordering because it is an internal label
that may change when graph construction changes.

Additional rankings may be exposed with explicit names, for example
`volume_solvent_estimate_rank`. They must not silently change the meaning of
`component_id`, `node_count_rank`, or `WET-1` / `DRY-1`.

Consumers such as visualization may select a different relevance metric, but
must name that metric explicitly.

## 4. Exact structural support

The support of one tetrahedron is the sorted quadruplet of atom indices that
defines it. The support of one component is the sorted collection of those
tetrahedron identities.

Conceptually:

```text
support = sort(sort(atom_indices_of_tetrahedron) for tetrahedron in component)
support_key = deterministic_digest(support)
```

Rules:

- use atom-defined tetrahedron identities, not positional tetrahedron indices;
- do not include wet/dry side, probe radius, frame, family, or ranking;
- preserve or make recoverable the full support, because dynamic matching needs
  overlap of tetrahedra and faces; the digest is an indexing aid, not a
  replacement for the support;
- equality of `support_key` means exact support equality on the same atom-index
  substrate;
- unequal `support_key` values do not imply unrelated temporal components.

Atom indices are the first implementation substrate. Their stability is limited
to molecular systems that preserve the same atom ordering. Cross-system
persistent atom identity remains a separate future concern.

Because side is excluded, the same support can be recognized when a probe sweep
changes its classification from wet to dry or vice versa.

## 5. Contextual component identity

`component_key` identifies one exact support with one classification in one
DFND result:

```text
component_key = deterministic_digest(result_key, side, support_key)
```

`result_key` must identify the substrate and all parameters that can change the
DFND result, including at least the structure/frame identity, method, probe
radius, radii model, selection, hydrogen policy, transit policy, gate-intrusion
policy, and relevant numerical policy.

Consequences:

- equal `component_key` values mean the same exact classified component in the
  same result context;
- a probe-radius change produces a different `component_key`, even when
  `support_key` remains equal;
- a wet/dry transition produces a different `component_key`;
- `component_key` is not temporal identity.

Internal relations and provenance use `component_key`. For compatibility and
human-readable inspection, relation records may also retain their local
`component_id` fields. User-facing selection and labels continue to support
`component_id` within a result.

## 6. External-link and motif identity

External links and motifs separate local labels, exact support, and contextual
identity in the same way as components.

An external link is structurally supported by its connected cluster of hull-face
triplets, using stable atom indices:

```text
external_link_support = sort(sort(face_atom_indices) for face in link)
external_link_support_key = deterministic_digest(external_link_support)
external_link_key = deterministic_digest(parent_component_key, external_link_support_key)
```

A motif declares a `motif_support_key` appropriate to its primitive:

- `external_mouth`: the source external link support key;
- `depth_region`, `chamber_candidate`, and dry regional motifs: exact
  tetrahedron support;
- `throat_candidate`: exact atom-defined face support.

Its contextual identity is:

```text
motif_key = deterministic_digest(parent_component_key, motif_type, motif_support_key)
```

`external_link_id`, `local_link_id`, and `dry_motif_id` remain local labels.
`external_link_key` and `motif_key` identify exact substructures in one contextual
result, but neither is temporal identity. Their full structural support remains
recoverable from the records.

## 7. Dynamic identity

Temporal continuity is inferred, not obtained from exact key equality.

Use:

| Concept | Contract |
| --- | --- |
| `track_id` | Identity of one continuous, unbranched temporal segment |
| `lineage` | Directed graph of tracks and events |
| `parents` / `children` | Relations between tracks at split/merge events |
| `event_type` | `birth`, `death`, `continuation`, `split`, `merge`, or an accessibility event |

A split ends the parent track and starts child tracks. A merge ends the parent
tracks and starts a child track. This avoids assigning one scalar identity to an
N:M relationship.

Matching between consecutive results should use evidence in this order:

1. tetrahedron-support overlap;
2. face-support overlap;
3. lining atom and residue overlap;
4. external-link and connectivity similarity;
5. geometric continuity, such as center and volume, as secondary evidence.

Delaunay flips can change exact tetrahedron support between frames. Therefore
`support_key` and `component_key` must never be used as substitutes for
`track_id` or lineage matching.

## 8. Compatibility and implementation status

Approved target contract:

- keep `component_id` as a local human-readable rank label;
- introduce `node_count_rank`;
- retain `size_rank` temporarily as a deprecated alias;
- keep `component_index` as a local collection position;
- replace `graph_label` as the public ranking tie-breaker with `support_key`;
- introduce `support_key` and `component_key`;
- use structural/contextual keys for external links and motifs;
- implement `track_id` and `lineage` later in a separate dynamic layer.

Implementation status on 2026-06-06:

- static identity is implemented and tested for wet and dry components;
- the numerical substrate has a cached `substrate_key`, and each query exposes a
  contextual `result_key`;
- records and typed components expose `component_index`, `node_count_rank`, the
  compatibility alias `size_rank`, rank-derived `component_id`, `support_key`,
  `component_key`, and recoverable `tetrahedron_support`;
- equal-size ordering uses `support_key`, not `graph_label`;
- promoted wet parent features carry the static identity fields and use
  `component_key` as `source_id`; promoted mouths use their `external_link_key` as
  `source_id`, carry `parent_component_key`, and expose source external-link
  provenance plus `R_gate_*` quantities;
- external links and wet/dry motifs expose exact support keys and contextual keys;
- raw and typed component relations carry contextual component keys additively,
  while local component IDs remain available for compatibility and display;
- component and feature registries are atomic, and components can be resolved by
  `component_key`;
- `track_id` and `lineage` are not implemented.

Dynamic tracking must continue test-first.
