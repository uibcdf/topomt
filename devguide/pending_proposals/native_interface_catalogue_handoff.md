---
summary: Review and hand off a native BindingMT interface catalogue with explicit MolSysMT and TopoMT ownership.
issue: uibcdf/topomt#197
status: open
opened: 2026-11-12
closed:
verification: inspected
area: [architecture, interoperability, documentation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Native interface catalogue contribution and owner handoff

## What

The maintainer requests a reviewed, detailed native-characterization plan in
TopoMT devguide, then a substantive response in BindingMT #112 linking its exact
published revision. The broad
[catalogue plan](../binding_interface_native_catalogue_plan.md) lives outside
this queue. BindingMT #112 owns the scientific roadmap; MolSysSuite #195 owns
shared agreements. This issue owns TopoMT's bounded contribution and review.

## How

Extend the reviewed BindingInterface model and its implementation plan with a
native contacts milestone, then SASA/burial and separately qualified chemical,
topographic and later families. Reuse MolSysMT public tools, keep binding-domain
operations in BindingMT and preserve TopoMT's topographic supports/relations.
Close explicit source/state/environment, quantity, numerical, attribution,
calculation/composition and acceptance contracts. Preserve PISA receiving as an
independent route with an explicit scheduling disposition.

## Why

The original saved-PISA pilot provides concrete interoperability evidence but
does not define the native catalogue or require PISA for ordinary characterization.
The maintained plan gives new contributors an inspectable scientific direction,
owner boundaries, initial scope, independent controls and issue-board follow-up.

## What was refuted

- Making an external provider the mandatory source or scientific definition of
  ordinary BindingMT interface characterization.
- Moving generic molecular kernels into BindingMT or binding-domain ownership
  into TopoMT merely because an adapter currently resides there.
- Treating tabulated residue buried area as conformational interface burial.
- Equating contact support, buried-area contributions and continuous topography.
- Claiming general superiority, a runtime API or shared acceptance from a plan.

## Scope and exclusions

Documentation, owner feedback and publication only. Preserve the human version
edit, original artifacts, existing adapters and current DFND synthetic sequence.
No sibling worktree/environment change, native calculation, new engine/model,
protein campaign, package/tag/release or manual hosted CI is commissioned.
Source/native/installed qualification and actual consumer adoption remain separate.

## Acceptance criteria

- Publish the reviewed complete plan, local navigation and issue-backed ownership.
- Run relevant documentation/report checks and record their actual scope.
- Link an exact committed source from BindingMT #112 and MolSysSuite #195, with
  independent readback of the published document and responses.
- Record owner acceptance/deferment and concrete TopoMT follow-ups before closing
  this review issue; existing #60/#61/#62 gates retain their scientific scope.

## Delivery state

Revision 1 is published and shared for owner review. It includes explicit
initial chemistry/environment restrictions, a descriptive candidate catalogue,
contact/surface recipes, numerical edge cases, resource and attribution rules,
independently useful increments and issue-backed owner actions. Runtime
implementation and owner adoption remain pending; `inspected` is not executed
native receiving.

- [Published complete plan](https://github.com/uibcdf/topomt/blob/a13b9b2725bd8a4edd851441d1a5a53720e0f3ea/devguide/binding_interface_native_catalogue_plan.md),
  source `a13b9b2725bd8a4edd851441d1a5a53720e0f3ea`, Git blob
  `722d7ea7f2b37cf257b7be0044b81a83433f3e26` independently read back exactly.
- [BindingMT #112 response](https://github.com/uibcdf/bindingmt/issues/112#issuecomment-6836773833),
  [MolSysSuite #195 handoff](https://github.com/uibcdf/molsyssuite/issues/195#issuecomment-6836783376)
  and [TopoMT #197 delivery](https://github.com/uibcdf/topomt/issues/197#issuecomment-6836788574):
  each independently read back with its complete body matching the prepared text.
- The initial document commit `90e154b` remains historical. Before sharing, the
  final review received BindingMT's newly updated work plan at `d69315d` and
  retained derived-footprint persistence, aligned maps and crossed original-
  outcome/asset/current-use controls. Both publication commits carry `[skip ci]`.

The writing/publication portion is delivered. Keep #197 open for owner-review
disposition and scoped TopoMT follow-ups; BindingMT #112 and MolSysSuite #195
retain scientific implementation and shared agreement respectively. No response
or accepted new shared contract is inferred from publication.

Maintainer refinement on 2026-11-12: regional physicochemistry is also a
standalone TopoMT responsibility. The dedicated issue
[#198](https://github.com/uibcdf/topomt/issues/198) and
[local staged proposal](topographic_physicochemistry.md) own that work. Catalogue
revision 2 makes this complementary boundary explicit without withdrawing the
published BindingMT contribution or changing its historical source.

Local documentation validation (2026-11-12):

- `python devtools/devguide_index.py --check`: generated lifecycle indexes current.
- `python devtools/comparative_findings.py --check`: offline consistency passes;
  no comparative claim/card is created or resolved.
- `git diff --check` and a bounded Markdown check: five documents, 154 local
  path links, balanced code fences and no trailing whitespace.
- `python -m pytest --noconftest --receptor=llm tests/test_reporting_protocol.py`:
  two tests passed. This administrative selection deliberately excludes the
  scientific conftest/warmup; it is not a full-suite or scientific qualification.
  One allowed logical CPU, low priority, one-thread settings and a 4 GiB address
  limit were used; elapsed 0.80 s and peak RSS 51,260 KiB.

Resource inspection found about 52.7 GiB available of 60.5 GiB physical RAM and
zero recent memory-pressure averages. Slurm commands exist but a single five-
second partition probe timed out. No job or scientific computation was started.
Only the bounded administrative checks above ran directly.

The suite preflight fetched references and preserved sibling worktrees. TopoMT
received three already-published official guide commits through a fast-forward
to `1128000`; the human version edit retained its original SHA-256. Source
inspection remains pinned to the plan's stated revisions, independently of
other clones' behind/dirty states. Official component labels were verified with
MolSysSuite tools at `a491eb61111870ba83b0e16bab8b5f476e1db68a`.

Before opening these owner issues, full state=all REST inventories were acquired
through both pages for each repository: 153 entries / 145 issues for TopoMT,
193 entries / 181 issues for MolSysSuite, excluding pull requests. An initial
bounded connector search returned only 100 and was not used as an absence proof.
The first CLI formatting attempt and incomplete/stale local tool acquisition
failed before changes; corrected acquisition used complete published modules.
These were preparation failures, not failed scientific or validation outcomes.
