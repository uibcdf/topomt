---
summary: Query component-side neighbors separately from legacy residence-side filtering.
issue: uibcdf/topomt#176
status: active
opened: 2026-11-10
closed:
severity: medium
verification: inspected
area: [dfnd, api]
guard:
normative:
blocked_by: []
supersedes: []
---

# Explicit component-side neighbor filtering

## What

The unchanged closed shell at 0.2 Å supplies 95 resident cells and three
nonresident connectors in its wet component. The documented legacy
`graph.neighbors(..., side='dry')` selects nonresident neighbors, including
those wet connectors. Component membership and local residence need separate
selectors. This bounded capability belongs to the three-case public audit
under #76/#60 and preserves the existing residence-side contract.

## How

Add optional `component_side='wet'/'dry'` to the native graph neighbor view.
Derive the side from the captured transit role: resident/connector nodes are
wet; terminal-contact/nontransit nodes belong to banks. Preserve `side` as the
legacy residence filter; both selectors can be intersected. Missing transit
role context in diagnostic legacy records is explicitly unavailable.

## Why

Users need to ask which native bank or wet carrier borders a node without
conflating a nonresident connector with a bank. One shared adjacency array and
bounded per-neighbor lookup keep repeated queries inexpensive. Record selection
does not execute a new scientific calculation or add a bibliography credit.

## What was refuted

The current residence filter is documented and already guarded. Changing its
meaning silently would break compatibility. Native wet/dry membership is not
a claim of physical liquid/solid occupancy or molecular participant identity.

## Scope and exclusions

Explicit native neighbor filtering, documentation and case-backed regression
guards. No segmentation, geometry, radius/probe model, public participant,
interface promotion or persistence format changes. Wider #60/#61 remain open.

## Acceptance criteria

Actual closed-shell connectors are included in wet-component filtering and
remain nonresident in the compatibility filter. Neighbor sides partition the
complete adjacency and preserve reciprocal membership; combined filters select
the intersection. Invalid selections and absent role context are rejected.
Repeated queries do not scan every node. Reconcile the method explanation and
support receipt; archive this bounded report after its guards pass.
