---
summary: Expose original provider pocket outputs without DFND prerequisites.
issue: uibcdf/topomt#65
status: resolved
opened: 2026-09-30
closed: 2026-09-30
severity: medium
verification: inspected
area: [third_party, api]
guard: tests/test_provider_pocket_outputs.py
normative:
blocked_by: []
supersedes: []
---

# Original provider pocket outputs

## What

Permanent pocket delivery to MolSysViewer, DockingMT and PharmacophoreMT uses
provider-specific provisional output classes while Topography adoption remains
deferred. The current checkpoint is
[provider_pocket_output_checkpoint.md](../provider_pocket_output_checkpoint.md).

## How

Expose original execution/import via `get_provider_output` and per-provider
`get_output`. Reuse original ProviderRun/ExternalMeasurement evidence through a
private adapter bridge, detach pocket fields and source-frame representations,
and preserve CASTp auxiliary mouth aggregates and original source relationships.

## Why

Consumers and later DFND comparisons need inspectable, recoverable pockets now.
The conceptual model does not require completing DFND's native implementation
or #60–#62 before this capability can work.

## What was refuted

- Completing DFND or all public registry gates first is not a requirement.
- Legacy Pocket/Void/Channel subclasses do not establish canonical admission.
- Atom sets and sites do not establish an exact volumetric region.
- A server fixture does not prove live service availability.

## Scope and exclusions

Original fpocket CLI/files, Pocketeer/AlphaSpace2/pyCASTA libraries and CASTp
server/files. Existing public APIs remain compatible. Local algorithm parity,
independent descriptor calculations, native DFND consolidation, sibling API
adoption and viewer addon repairs retain their own gates.

## Acceptance criteria

`tests/test_provider_pocket_outputs.py` guards source IDs, original fields,
units, detached lifetime, source mapping, geometry availability, original-route
selection and CASTp aggregate relationships. Installed engines validate their
new outputs separately. Document results and applicable hosted evidence before
marking resolved; keep exhaustive #19 parity milestones open.

## Resolution evidence

The output objects and original-route entry points are implemented. The guard
module verifies detached original data, provider-specific fields and units,
source selection maps, membership roles, and CASTp aggregate/source links; it
also exercises installed original engines when available. It protects delivery
of usable original pocket evidence, not exhaustive scientific parity.

- Final guard plus installed-engine comparators: 40 passed in the existing
  temporary validation environment, with six original AlphaSpace2 undefined
  ratio warnings preserved.
- Guard, CASTp regressions and reporting protocol: 42 passed, three optional
  Python engines absent/skipped in the shared environment.
- Earlier broader compatibility/dependency selection: 80 passed, three skipped.
  Its two initial sandbox-only subprocess failures passed outside the sandbox.
- Complete Ruff lint/format and 12-file scoped mypy passed. The changed guide
  documents render with warnings treated as errors. Full public HTML generates
  with the 11 pre-existing diagnostics tracked by #64; the new user section
  emits none.

Hosted evidence and exact publication SHA are linked from #65. No live-service
or green full scientific matrix claim is made. Source-map corrections cover
fpocket selection and CASTp submitted-selection/source-system correspondence.
