---
summary: Define the DFND-grounded public Topography conceptual contract and bounded adoption gates.
issue: uibcdf/topomt#59
status: resolved
opened: 2026-09-30
closed: 2026-09-30
severity: high
verification: inspected
area: [architecture, topography, dfnd]
guard:
normative: devguide/topography_conceptual_contract.md
blocked_by: []
supersedes: []
---

# Define the Topography conceptual contract

## What

Establish a public semantic architecture grounded in DFND, with explicit spatial
support, identity, classification, molecular participants, typed relations,
contextual evaluations and provenance. Provider admission preserves original
semantics and declares capabilities rather than asserting equivalence by name.

## How

The normative decision is `devguide/topography_conceptual_contract.md`.
`devguide/topography_implementation_route.md` records current code evidence and
bounded runtime gates owned by #60–#63. The architecture entry point and relevant
DFND public-contract references direct contributors to this decision.

## Why

The implemented kernel/catalog and mesh/query split provides a strong native
foundation. Public features currently receive dynamic descriptors; the
Topography hierarchy restricts containment to 0D/1D children of 2D features.
These are not yet complete contextual support/relation/evaluation contracts.

The native interface route counts dry banks, which can fuse across a tight
molecular dimer. AlphaSpace2 contact-weighted occupied space differs from an
explicit geometric intersection. CASTp mouth rows can aggregate several
openings. These cases make implicit public normalization scientifically unsafe.

## What was refuted

- Molecular participants are not geometric dry banks.
- An A–B relation without realized support is not a localized interface feature.
- Equal atom sets or pocket labels do not prove equal geometric support.
- Provider classification or occupancy names do not establish native canonical
  predicates or equivalent measurement definitions.
- A raw native motif attribute is not validated public subregion promotion.
- Older checkpoints do not prove that the current product matrix is green.

## Scope and exclusions

This issue closes the conceptual contract, its discoverability and adoption
gates. It does not implement runtime types, change function signatures or
defaults, move other components' responsibilities, or validate scientific
algorithms. Those outcomes belong to the named implementation and existing
provider/scientific issues.

## Acceptance criteria

- Normative contract covers the semantic entities, namespace boundary,
  identity/context, ownership/invalidation, promotion, interfaces, evaluations,
  provider capability and compatibility obligations.
- Adversarial scenarios cover tight dimers, buried/bare interfaces, shared
  memberships, subregions, support identity, occupancy definitions and missing
  capabilities.
- Architecture entry points distinguish implemented foundations from pending
  runtime adoption, with #60–#63 as independently closable gates.
- Report indexes, local document references and documentation rendering are
  checked before publication; preserve any pre-existing documentation warnings.

## Resolution and evidence

The conceptual contract and issue-owned route are complete. Runtime adoption
remains open in #60–#63. The decision adds documentation only and changes no
Python implementation, call signature, default, scientific output or matrix
support claim.

Validation uses the Python 3.13 development environment: both existing reporting
tests pass with `--receptor=llm`; Ruff lint and format checks pass (368 files).
All 157 local references checked across the ten internal contract/entry-point
documents resolve. The two new documents render with Sphinx/MyST under `-W`
without diagnostics.

The public documentation builds through `make html` using the existing temporary
provider-validation environment to supply its declared PlantUML extension.
Its complete build emits 11 diagnostics in existing content, including one
ERROR-level transition diagnostic despite exit zero. Source markup/reference
defects are recorded in #64; the absent PlantUML executable is an environment
limitation. No clean complete-documentation or green product-matrix claim is
made. No scientific tests are required for this documentation-only decision.
