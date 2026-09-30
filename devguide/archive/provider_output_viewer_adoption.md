---
summary: Adopt original provider pocket outputs in the MolSysViewer addon.
issue: uibcdf/topomt#66
status: resolved
opened: 2026-09-30
closed: 2026-09-30
severity: medium
verification: inspected
area: [third_party, viewer]
guard: tests/test_provider_output_viewer.py
normative:
blocked_by: []
supersedes: []
---

# Provider output viewer adoption

## What

The user prioritizes MolSysViewer addon adoption after #65. DockingMT and
PharmacophoreMT adoption remain deferred. The addon needs an explicit path for
ProviderOutput records, separate from canonical Topography state.

## How

Attach provider outputs in a per-view namespace, render declared sphere/site or
membership geometry, expose pocket controls, and clear only owned layers through
public shape APIs. Existing tests need test-owned transport capture because the
host retired its private message history. Repeated rendering currently checks
string tags against tuple-key private scene state and leaves duplicate shapes.

## Why

The pilot needs inspectable original-provider pockets in the viewer. Its current
structure-selection notebook leaves model choice to scientists; public fixtures
establish infrastructure evidence without selecting a scientific receptor.

## What was refuted

- Provider labels do not establish canonical DFND feature admission.
- Point membership and display markers do not establish a closed region.
- Missing private test history does not independently prove a failed first render.
- The shape cleanup defect belongs to this TopoMT integration, not a viewer fork.

## Scope and exclusions

Only the TopoMT-owned addon, tests and documentation. Preserve Topography APIs
and unrelated scene objects. No DockingMT/PharmacophoreMT adoption, confidential
pilot-asset publication, live CASTp certification or DFND consolidation.

## Acceptance criteria

Test-first `tests/test_provider_output_viewer.py` must verify real provider
evidence, explicit units, run/source identities, independent overlays, repeated
render and clear, honest absent geometry, original-pocket panel actions and
installed original engines. Existing addon tests must pass using current public
scene access and test-owned message capture. Update the active checkpoints and
record scoped and hosted evidence using the required receptors.

## Resolution evidence

Implemented explicit provider attachment, declared sphere/point rendering,
per-run cleanup and pocket/summary panel controls, preserving canonical
Topography state. Panels refresh after frontend mounting and source changes.
Public shape access and object identity fix repeated-render cleanup and protect
unrelated replacement shapes. Test-owned message capture removes reliance on
the retired viewer history without changing production MolSysViewer code.

- Final shared guard, provider-output, complete addon and import selection:
  **229 passed, six skipped** for three absent optional Python engines in two
  modules; two pre-existing H5MSM deprecation warnings remain visible.
- Final installed-original-engine consumer/comparison selector: **33 passed**,
  including original fpocket CLI with a loaded source receptor and all three
  Python engines; six upstream AlphaSpace2 undefined-ratio warnings preserved.
- Complete Ruff lint/format and six-file scoped mypy passed. Changed guides
  render with warnings treated as errors; public HTML retains the 11 existing
  diagnostics in #64.
- The public-export assertion now includes the already introduced
  `get_provider_output`; the initial broader selector exposed that stale
  expectation and the corrected final selector passes.

Exact publication and hosted evidence are linked in #66. The previous scientific
CI failed, with gh-run-receptor identifying missing fpocket in all six test jobs;
this bounded slice does not claim a green full matrix or browser certification.
The user requested a pause after initial third-party/viewer integration. That
pause is recorded in the current checkpoints; remaining #19 fidelity and live
CASTp availability, richer viewer controls, and future consumer adoption are
not included in this resolution.
