---
summary: Keep comparative findings current when DFND limitations are corrected.
issue: uibcdf/topomt#153
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: high
verification: measured
area: [dfnd, governance, documentation]
guard: tests/test_comparative_findings.py::test_current_limitation_cannot_survive_a_resolved_local_report
normative: devguide/comparative_findings.md
blocked_by: []
supersedes: []
---

# Comparative findings and current limitation lifecycle

## What

Maintain demonstrated advantages, third-party limitations and DFND limitations
with explicit versioned scope and a resolution/review lifecycle. Prevent a
corrected historical limitation from being reused as a current paper claim.

## How

Use the existing Discussions categories, a canonical findings index and one
maintained card per finding. Substantive analysis stays in Discussions and
frozen reproducible evidence in BenchLab. Devguide contains operating rules,
a template and lifecycle/navigation metadata. Connect the root/devguide AGENTS
reading routes and report closeout. Reuse the existing report parser for an
offline consistency check, with optional live GitHub readback reconciliation.

## Why

A dated failure remains true historically even after its fix. Issue closure
alone neither proves resolution nor tells readers whether a limitation persists
in their target version. A current summary, scoped fixing evidence and explicit
manuscript review must distinguish those situations.

## What was refuted

New winner/loser categories, labels or a green bookkeeping check cannot qualify
a scientific advantage. A tiny-input crash outside a tool's established input
scope does not establish algorithmic inferiority. Documentation alone does not
fix #151/#75; consciously retained limits are not falsely marked resolved.

## Scope and exclusions

Local scientific-claim governance and its consistency guard. Preserve historical
artifacts, comment history and the existing six categories. No DFND scientific
runtime change, original-engine execution, new geometry or package qualification.

## Acceptance criteria

Document intake, evidence levels, current and historical states, ownership,
partial fixes, same-scope verification, remote-summary reconciliation, regression
and release scope, persistent limits and pre-paper review. Bootstrap honest
current/resolved/needs-review examples; leave the demonstrated-advantage view
empty until justified. Test stale-current versus resolved-report/live-issue
mismatches and incomplete claimed fixes; read back published navigation/cards.

## Resolution

The accepted workflow is implemented in devguide/comparative_findings.md,
its card and manuscript-review templates, root/devguide AGENTS reading/action
routes, report closeout and Discussion procedures. The maintained hub is
https://github.com/uibcdf/topomt/discussions/154 . Scientific analysis stays in
its addressable cards; reproducible inputs/results remain in BenchLab. The TOML
file is lifecycle/navigation metadata rather than a second scientific narrative.

Stable finding IDs, software/input scope, evidence maturity, owner and review
date separate historical observations from current summaries. Resolutions need
fixing revision, regression guard, resolution scope and verification evidence;
partial fixes, source-only delivery and installed releases stay distinct.
Interrupted reconciliation becomes needs_review with an OPEN owning/follow-up
issue, not an invisible Discussion task. Persisting accepted limits keep their
reason/decision evidence and revisit condition. A manuscript review pins the
actual target profiles, validates applicable evidence and records scoped wording
and exclusions; green metadata or a closed issue alone cannot approve a claim.

Five factual cards bootstrap the register: the #151 physical-boundary limitation,
the scoped #75 precision/uncertainty limitation, resolved source-admission history
#147, and the CAVER/MOLE tiny-input failures needing review. The last two now have
dedicated investigations #155/#156 and matching local reports. Source #75 evidence
is explicitly historical reproduction plus unchanged-file inspection, not a fresh
numerical experiment. Resolved #147 is excluded from current limitations, and
its actual public admission regression still passes. No comparative advantage
is invented; that view remains empty until its evidence criteria are met.

The maintainer then required area-wide issue coverage. All 42 Discussion opening
posts and five comments were audited; there were no replies. Existing issues own
already tracked work; eleven bounded documentary/eligibility tasks #158–#168
cover missing candidate reviews and retained CASTpFold job disposition. The
42-row action map records scope and responsibility without duplicating issue
open/closed state. All opening posts now have visible action routing or explicit
informational disposition (#12/#13). Older integration/pause/candidate wording
is clearly dated, with current provider records linked. Current posting and
comment bodies, six categories, finding labels and owner links were read back.
The issue board is the work queue; a closed organization ticket is not completion
of a later assessment. New/revised actions and replies need the same triage.

Three resource forms now prompt for owning issues without adding intake barriers
or required fields. Source YAML is parsed/checked; GitHub rendered UI behavior
was not independently re-observed. The code/documentation record does not claim
new category configuration or newly qualified engine execution.

The related attribution question exposed missing TopoMT Ackredit runtime use:
only an unused legacy flowcite helper exists. This is queued as #157 with a local
consumer-adoption report, fpocket-first real-provider acceptance and an inventory
of other routes. Ackredit itself was consulted read-only at clean source
4beb850c8ba814e6103b4d303128a1a36eb57610. No provider defect, runtime fix or automatic
fpocket credit is claimed. #56 retains its wider adoption scope.

The repository-specific checker reuses the existing report parser/static guard
validation and runs with devguide_index.py. It rejects current/pending limitations
with closed local reports or supplied live issues, Discussion-only needs_review,
incomplete fixes, stale card/index states and missing advantage/eligibility
metadata. A completed comparison issue can legitimately leave its scoped
advantage current. Tests exercise both negative contradictions and reconciled
states. Optional normalized readback comes from actual GitHub responses; ordinary
pytest and the checker perform no network request. Semantic action triage and
scientific/profile freshness still require the documented human review.

Validation: 31 selected lifecycle, report-protocol and real public length-admission
guards pass on shared Python 3.14.10 (1.47 seconds). Repository Ruff passes (558
formatted files); namespace-aware focused mypy passes for three Python files.
All 33 changed/new Markdown records render without new warnings and local
links pass; existing generated-index heading warnings remain visible. Full public
Sphinx HTML builds with the same twelve existing warnings and verified BenchLab
hub navigation (8.69 seconds, peak RSS 278892 KiB). Later changes are devguide,
forms and tooling only; the built public source remains byte-identical. Tests and
builds used one CPU/numerical worker, 6 GiB process address-space ceilings and
bounded CPU budgets. These are local execution receipts, not performance benchmarks.

No DFND scientific kernel, provider binary, package metadata or shared environment
changes. Existing frozen scientific artifacts and the pre-existing human version
file remain untouched. Raw GitHub, rendering, test/source-audit helper receipts
remain in task-owned ignored cache; remove the duplicate copied docs source after
publication while retaining the HTML preview and required records. Incremental
commits use the maintainer-requested [skip ci]. Full suite, installed candidate,
Python/support matrix and hosted exact-head evidence remain deferred under #16;
the existing checkpoint recovery route retains that work. Open scientific issues
and the newly queued assessments are not closed by this governance delivery.
