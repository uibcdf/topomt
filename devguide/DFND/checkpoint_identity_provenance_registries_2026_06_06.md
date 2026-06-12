# DFND Checkpoint: Static Identity, Provenance, and Atomic Registries

**Date:** 2026-06-06  
**Status:** implemented and verified

## Scope

This checkpoint records the hardening work that separates local display labels,
exact structural support, contextual provenance, and future temporal identity.
It also records the registry guarantees required to preserve those contracts
under mutation.

## Implemented Advances

### Static identity

DFND now distinguishes:

- `component_index`: local collection position;
- `node_count_rank`: local rank by descending tetrahedron count;
- `component_id`: human-readable local rank label (`WET-1`, `DRY-1`);
- `support_key`: exact atom-defined tetrahedron support;
- `component_key`: exact classified component in one result context;
- `external_link_support_key` and `external_link_key`;
- `motif_support_key` and `motif_key`.

Equal-size components use `support_key`, rather than internal `graph_label`, as
the deterministic ranking tie-breaker. Full tetrahedron or face support remains
recoverable; digests are indexing aids, not replacements for scientific support.

### Contextual provenance

Contextual keys are propagated additively while local IDs remain available for
human-readable selection and compatibility:

- residence regions and external links carry their parent `component_key`;
- dry interfaces carry source and target dry-component keys;
- coast and lining relations carry wet/dry component keys;
- wet and dry motifs carry parent component and motif keys;
- promoted parent features use `component_key` as `source_id`;
- promoted `Mouth` features use `external_link_key` as `source_id` and carry
  `parent_component_key`.

### Typed access and selection

- `Components` resolves components by `component_key`;
- selectors accept `component_keys` and `support_keys` without removing
  `component_ids`;
- `WetComponent.external_link_keys` and `DryComponent.motif_keys` provide direct
  contextual references alongside local IDs.

### Atomic registries

`Topography` and `Components` now enforce unique, immutable registered IDs and
provide explicit atomic add, replace, rename, remove, relation, and copy
semantics. Failed operations do not leave partial indexes or relations.

## Verification

The implementation is covered by focused identity, provenance, selector,
registry, promotion, graph-contract, and wet/dry-adjacency tests. On 2026-06-06:

- focused identity/provenance tests passed;
- the complete DFND test group passed in 12 processes;
- the complete repository suite passed in 12 processes with only configured
  skips and expected failures;
- focused and correctness-critical Ruff checks passed;
- `git diff --check` passed.

## Remaining Work

### Requires decisions before implementation

1. **Dynamic matching and lineage.** Define matching thresholds, confidence,
   split/merge handling, and event semantics before implementing `track_id` and
   lineage graphs.
2. **Residence-state versus transit-membership ownership.** Decide whether wet
   and dry analytical memberships may overlap and how coast/depth attribution
   follows from that decision.
3. **Typed scientific relations.** Decide the relation model beyond parent/child
   and dictionary records, including `mouth_of`, `bounded_by`, `adjacent_to`,
   `derived_from`, and temporal relations.
4. **Cross-system atom identity.** Exact support keys currently assume stable atom
   indices on one substrate.

### Engineering work that does not depend on temporal identity

1. Correct the canonical face-permeability versus graph-traversability mismatch
   (`DFND-001`).
2. Resolve inert or incomplete query parameters and provenance through a typed,
   immutable DFND query contract (`DFND-002`, `DFND-006`, `DFND-007`).
3. Continue viewer runtime, repeated-render, atom-index, and geometry-boundary
   hardening.
4. Complete packaging, isolated-import, documentation-CI, and quality gates.
5. Expand pathological, near-threshold, real-system, and comparison validation.

### Scientific validation still required

- reporting policy for tiny and marginal components;
- biological cavity-quality validation;
- physical mouth and volume metric validation;
- utility and stability of experimental throat, chamber, bottleneck, and dry
  motifs;
- quantitative centerline contract and validation.

## Authoritative References

- [`component_identity_contract.md`](component_identity_contract.md)
- [`object_model.md`](object_model.md)
- [`api_contract_v1.md`](api_contract_v1.md)
- [`implementation_status.md`](implementation_status.md)
- [`dynamic_topology.md`](dynamic_topology.md)
- [`../code_review_2026_06_06.md`](../code_review_2026_06_06.md)
- [`../architecture_review_2026_06_06.md`](../architecture_review_2026_06_06.md)
