---
summary: Validate explicit DFNDQuery objects at the shared public dispatcher.
issue: uibcdf/topomt#179
status: resolved
opened: 2026-11-10
closed: 2026-11-10
severity: low
verification: measured
area: [dfnd, api]
guard: tests/test_dfnd_query_gateway.py::test_valid_explicit_query_is_digested_and_preserves_the_canonical_result
normative:
blocked_by: []
supersedes: []
---

# Explicit DFND query admission

## What

The #178 tube study reaches a valid typed DFNDQuery through get_topography but
emits a missing-digester warning. The inner native route checks its type and
conflicting legacy arguments; the shared gateway lacks its adapter.

## How

Five actual-public regression cases first fail: valid input warns; four invalid
query types reach a monkeypatched forbidden native runner. Add a lazy adapter
for None/DFNDQuery without constructing a new query, changing physical settings
or suppressing diagnostics. Reuse the existing owning ArgumentError.

## Why

Advanced users should be able to provide the already supported configuration
object without a false missing-validation warning. Wrong types should fail at
the gateway before scientific work begins.

## What was refuted

The original study helper's direct boundary_tolerance keyword was a caller
mistake, rejected before native computation. The supported advanced boundary
setting belongs in DFNDQuery. That correction exposed this separate gateway
inconsistency; neither observation proves a scientific-kernel error.

## Scope and exclusions

One typed query adapter, public regression guards and advanced-query explanation.
Existing length/radius keyword work #147/#171 and broader public/neutral support
#60 remain separate. No geometry, defaults, region promotion, external engine,
mesh-config admission or installed-release change.

## Acceptance criteria

Valid typed/None queries have no missing-digester warning and preserve canonical
query/result identities. Invalid types raise argument-specific diagnostics before
native execution. Preserve existing conflicting-legacy-value checks. Name and
run durable guards, applicable lint/scoped typing and documentation/report checks,
then archive and close this bounded defect with source scope.

## Resolution — 2026-11-10

Corrected in source b07a20ed0ee1533cc16a0b6e30ace73c2ab09ac4. The lazy public
adapter retains a valid DFNDQuery object or None and rejects invalid types with
the owning ArgumentError before native execution. Conflicting legacy values
retain their existing inner diagnostics; exact normalized query identity is
unchanged. The method book now shows the supported advanced-query call.

Six gateway guards and the existing query/length/documentation controls pass.
The combined tube/reference/physical/public/query/book/report/finding selection
passes 106 tests; three strict pending tube targets belong to #180/#181 and are
unrelated to this adapter. Full tests, installed delivery, interpreter/platform
qualification and release evidence retain #16; no such qualification is inferred
from this focused run or skip-ci commit. Ruff and scoped typing pass.
