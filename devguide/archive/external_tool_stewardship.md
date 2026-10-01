---
summary: Centralize external-tool discovery and integrated-provider stewardship.
issue: uibcdf/topomt#67
status: resolved
opened: 2026-10-01
closed: 2026-10-01
severity: low
verification: inspected
area: [documentation, integrations]
guard:
normative: devguide/external_tools_catalog.md#maintenance-rule
blocked_by: []
supersedes: [uibcdf/topomt#8]
---

# External-tool catalogue and integrated-provider stewardship

## What

Establish a maintained catalogue and permanent provider overviews/discussions,
while retaining independently closable bugs and validation phases.

## How

Migrate every distinct reference from #8, add the 2026-09-30 researched candidates,
reuse existing provider directories and link detailed inventories/checkpoints.
Create six discussions and route historical intake to the maintained index.

## Why

Issue #8 mixed integrations, candidates, related applications and comparisons,
with duplicate references. Native and original status need separate evidence;
pyCASTA #53 remains an open local regression despite initial original delivery.

## What was refuted

A provider is not complete merely because its initial consumer output works.
A permanently reopened issue is not a useful substitute for a versioned profile.
Old parity checkpoints are not current, universal equivalence certificates.

## Scope and exclusions

Documentation and navigation only. No engine, dependency, viewer, DFND or CI
implementation changes. No automated monitoring or scientific recertification.

## Acceptance criteria

All retained references and five overviews are reachable from the catalogue.
Six discussions link to the maintained records; #8 and owning work issues link
back. Local links, rendered documents and reporting/index checks pass. Resolve
under the catalogue maintenance rule and archive this report.

## Delivery checkpoint (2026-10-01)

The catalogue, five overviews and navigation are implemented. All 21 distinct
historical URLs from #8 are retained; six new documents have resolving local
targets. Seven scoped Sphinx pages render with warnings treated as errors and
no diagnostics. The public incremental HTML build succeeds in the existing
temporary provider-validation environment with eight existing diagnostics under
#64; the shared development environment lacks sphinxcontrib-plantuml, which is
already declared in docs_env.yaml. No environment installation was performed.
Ruff lint/format pass and both reporting-protocol tests pass with Pytest Receptor.

Six discussion opening posts are prepared. Publication awaits the user-created
External tools category: GitHub's GraphQL API exposes discussion creation but no
category-creation mutation. Keep this issue open until publication, reverse links
and historical-intake routing are verified. No scientific test was rerun as part
of this documentation change.

Before publication, origin/main advanced to 1aa25c4 (shared optional-engine
contract and published DepDigest migration). Merge f7ab6d2 preserves those
changes. Ruff/index checks still pass. An additional reporting/availability
selection yielded three passes and five failures: the new availability tests
imported editable DepDigest 0.10.1+15.g78a9106, below the merged >=0.12.0
requirement, and could not address checker.shutil. Both the shared environment
and earlier provider-validation environment import that older checkout. This
is not passing availability evidence for the merged boundary; its correctly
installed published-provider evidence remains in the owning #56 review.

## Resolution (2026-10-01)

The user created External Tools as an open-ended category; GraphQL confirmed
isAnswerable=false. Discussions #68–#73 now provide one catalogue conversation
and one permanent conversation per integrated provider. All opening posts link
the maintained records; each overview and the catalogue link back. Issue #8's
historical comments remain intact and its superseded record names the new
research destination. Native regressions and descriptor issues are not closed
or replaced by this organization outcome. Final local/index/render checks and
publication evidence are recorded in #67; full installed-engine/CI certification
is outside this bounded organization gate.
