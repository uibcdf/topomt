# Operating the comparative-findings register

Maintainer decision: 2026-11-08; implementation is tracked in
[#153](https://github.com/uibcdf/topomt/issues/153). This is TopoMT's local
scientific-record workflow, under [Discussions maintenance](discussions.md)
and the [reporting protocol](reporting_protocol.md).

**A historical observation and a current limitation are different records of
truth.** Preserve the former, maintain the latter, and qualify both by software,
input and scientific scope. A corrected limitation must leave the current view;
a source-only fix must not be advertised as fixed in every installed release.

## Destinations and ownership

- The canonical **Comparative Findings and Limitations** hub is in **Datasets
  and Benchmarks**. It has three views: demonstrated DFND advantages, third-party
  limitations and DFND limitations, with unresolved review/history shown clearly.
  Current entry point: [Discussion #154](https://github.com/uibcdf/topomt/discussions/154).
- One maintained, addressable card per finding contains its scientific analysis,
  conclusion and dated history. Initially cards are top-level comments in the
  hub. Follow-up replies do not replace their current summaries. Reuse a card
  across versions; split materially different claims with an explicit link.
- Methods and Tools conversations link relevant findings about their method.
  A limitation's correction must reach any such maintained summary too.
- BenchLab retains reproducible, versioned systems, protocols, references,
  original observations and figures. Preserve frozen bytes and historical
  notebook results; add linked corrections/current interpretation around them.
- [comparative_findings.toml](comparative_findings.toml) stores navigation and
  lifecycle metadata for checking consistency. It does not replace scientific
  Discussion content. Devguide contains these rules and the
  [card template](templates/comparative_finding.md).
- LMMV and dprada own this register until delegated. Each card names its owner
  and review date. The contributor who changes affected behavior initiates
  reconciliation; the person completing the change checks the whole route.
  There is no automatic monitoring or response-time promise.

Keep the existing six categories. Outcome is an entry state, not a category or
a superiority label. Mixed index threads do not inherit every feature label of
their entries. Use the existing supported facets for specific resource threads.

## Finding identity and required content

Use a stable descriptive ID, such as `tetrahedron-boundary-patches`, independent
of ordering, issue status or whether the result favors DFND. Every card and
metadata row must have a summary, kind, status, owner, review date, canonical
card URL, versioned scope and retained evidence paths. The hub links the card.

The card explains the question, intended users, input/atom selection, coordinate
and radius model, boundary conditions, probe/query/operator, units, versions or
source fingerprints, parameters, independent reference, expected/observed
behavior and the exact conclusion supported. Distinguish a scientific defect,
a definition difference, an input-domain restriction, integration failure,
operational failure and unavailable evidence. Include unknowns rather than
inventing comparability. Reuse original evidence instead of rerunning engines
merely to fill a template.

A demonstrated advantage additionally needs a comparison protocol, independent
reference, eligible matched inputs, scoped metric and actual comparator evidence.
Fair API/usability or performance claims state their own evaluation criteria;
performance needs representative measurements and resource/preparation scope.
A positive DFND result alongside a failed third-party run is insufficient on
its own. Novelty and general superiority require separate supporting analysis.

A third-party limitation marked current needs applicability evidence. An
unexplained four-atom crash remains `needs_review` until its supported input
scope and cause are understood; it is not proof of inferior geometry.
An actionable DFND limitation needs an owning TopoMT issue and local report.
Every `needs_review` entry, including a third-party investigation, also needs
an open owning issue and local report. A Discussion-only review is not a work
queue. Apply [the area-wide action rule](discussions.md#every-future-action-has-an-owning-issue)
to any other concrete pending work. A new action owner may replace a closed
original issue in metadata; retain the original issue and reason in card history.
Candidate discovery and documentary intake need not become defect issues.

## Lifecycle states

All states refer to the **specified software/input profile**, never implicitly
to the latest release. The current view includes `current` and
`documented_limit`; its heading must repeat that version-scoped meaning.

| State | Meaning and permitted interpretation |
| --- | --- |
| `candidate` | Hypothesis or lead. No demonstrated advantage/current defect claim. |
| `needs_review` | Scope, diagnosis, freshness or reconciliation is incomplete. Keep visible in the review queue; exclude from present-tense scientific claims. |
| `current` | Evidence supports the stated finding for its pinned profile. Recheck applicability before reuse for another target. |
| `documented_limit` | A persisting limitation has an explicit accepted reason, decision evidence and revisit condition. It remains a limitation, even if its issue was closed as not planned. |
| `resolved` | Same-scope evidence supports correction, with fixing revision, regression guard, resolution scope and verification evidence. Historical failure remains visible. |
| `superseded` | Another identified finding replaces the formulation. Link `superseded_by`; do not claim that a software fix occurred. |
| `withdrawn` | The interpretation was refuted or invalid. State the reason/evidence; do not present withdrawal as an algorithmic improvement. |

Every state change updates the card's **current summary first** and appends a
dated event with old/new state, reason, exact scope and evidence. Preserve the
original observation in a clearly marked history section. Earlier comments are
historical evidence, not current-status authority. Correct misleading mutable
summaries with dated notes rather than deleting their history.

Issue state is not scientific state. A completed comparison task can leave a
supported, scoped advantage current; its closure is not an unresolved-defect
contradiction. A closed limitation investigation instead needs an explicit
correction, retained-limit or other evidenced disposition, and a pending review
must have an open action owner.

## Intake and maintenance

1. Search the hub, register, method conversations and issues; reuse the stable
   finding. Open the owning issue/report first for an actionable DFND defect.
2. Record the factual observation and its evidence maturity separately from its
   interpretation. Use `candidate` or `needs_review` while scope is uncertain.
3. Add the card, lifecycle row and hub navigation together. Link affected method
   conversations, case pages and owning issue/report in both directions.
4. Record current limitations and unfavorable results as carefully as advantages.
   An empty demonstrated-advantage view is an honest result, not a gap to fill
   with unsupported claims.
5. Revisit when DFND/provider code, dependencies, radii/input preparation, scope,
   reference assumptions or interpretation changes. New evidence can invalidate
   an advantage as well as resolve a limitation. A new release alone proves neither.

## Required workflow when fixing a DFND limitation

1. **Find affected claims before editing behavior.** Search stable IDs, owning
   issue numbers, current cards, method summaries, BenchLab conclusions and
   manuscript drafts. Register a missing relevant finding; link the issue.
2. **Reproduce and repair.** Follow test-first development. Keep the original
   failing evidence. A workaround, skipped test or changed input/definition is
   not automatically a correction of the original claim.
3. **Verify the same scope.** Record the actual fixing commit/profile, diagnostic
   and public behavior, meaningful regression guard and retained verification.
   Identify untested platforms/providers. A passing subset cannot resolve a wider
   claim: split the finding or use `needs_review` while qualifying the remainder.
4. **Update current state in the same delivery.** Set `resolved` only for the
   demonstrated scope. Add `fix_revision`, `regression_guard`,
   `resolution_scope` and `resolution_evidence` to metadata. Put the correction
   and source/release boundary prominently in the current card and append history.
   A pending build or unverified public release remains explicitly unqualified.
5. **Reconcile every maintained representation.** Update the hub view, card,
   register, method summaries, current case prose, issue/report and affected
   scientific draft. Keep old artifacts/notebooks intact and link their corrected
   interpretation. Do not leave a fix only in a commit or a reply beneath an
   unchanged opening summary.
6. **Validate and publish.** Run the offline checks below, publish code and linked
   records, close/archive the owning issue/report with evidence, then read back
   remote issue/card/index state and run the live reconciliation check. Local
   record publication and remote issue closure can require sequential steps;
   the delivery is incomplete until their states agree.
7. **Handle interrupted reconciliation visibly.** Mark affected records
   `needs_review` and record the missing update/recovery action in an open owning
   or follow-up issue/local report. Reopen where appropriate; if the original fix
   is legitimately closed, link a bounded reconciliation issue and retain the
   original issue in history. Keep affected findings out of
   current scientific reuse. Do not leave a still-current claim silently behind
   because remote publication was unavailable or another contributor owns a draft.

Closing an issue as completed does not prove a fix. Closing it as not planned
does not remove a limitation. A consciously retained boundary uses
`documented_limit`, with explicit reason, decision evidence and revisit condition.
If the behavior returns, reopen the same defect where appropriate, return the
finding to review/current only with fresh scoped evidence, and retain its earlier
resolution interval. A genuinely different defect gets its own linked issue.

## Before using any finding in a paper or public argument

Perform a **target-specific review**, even if metadata passes:

1. Pin the manuscript's DFND/provider versions or source/artifact fingerprints,
   scientific model and input/probe scope. Do not interpret a source-only fix as
   delivered in an older released package, or old comparator failure as current.
2. Read the maintained card and dated history, the latest issue/report disposition,
   current method/case summaries and correcting commits. Historical search hits,
   labels, votes and a closed issue are insufficient.
3. Inspect applicable evidence and rerun only what changed or lacks qualification.
   Explain any justified reuse. Verify matched definitions/inputs before an
   advantage claim. `candidate` and `needs_review` cannot support present-tense
   advantage or limitation claims; resolved entries may support explicitly dated
   historical statements, with their correction stated.
4. Save a versioned review alongside the manuscript using the
   [claim-review template](templates/comparative_claim_review.md): date, reviewer, target profile,
   finding IDs, scoped wording, evidence/test receipts, excluded findings with
   reasons and the live readback identity. Repeat after relevant source/provider
   changes and before submission/revision. No paper-ready claim list is generated
   from this register automatically.

If freshness or applicability cannot be established, mark `needs_review` and
exclude or narrow the claim. Demonstrated advantages must be reconsidered if a
comparator improves; resolving a DFND bug does not automatically demonstrate an
advantage over any comparator.

## Consistency checks and live readback

```bash
python devtools/comparative_findings.py --check
python devtools/devguide_index.py --check
python -m pytest --receptor=llm tests/test_comparative_findings.py tests/test_reporting_protocol.py
```

The developer-guide index check also runs the comparative lifecycle check. It
catches a current DFND limitation linked to a closed local report, incomplete
claimed resolutions and missing evidence/eligibility metadata. It reuses the
existing report parser and static pytest-selector validation.

For remote reconciliation, read GitHub directly using connected tools or `gh`
and retain the raw responses. Normalize the readback into this JSON shape:

```json
{
  "captured_at": "UTC timestamp",
  "issues": {"uibcdf/topomt#151": {"state": "OPEN"}},
  "findings": {
    "tetrahedron-boundary-patches": {
      "status": "current",
      "discussion_url": "exact canonical card URL"
    }
  },
  "current_ids": ["tetrahedron-boundary-patches"]
}
```

Include **all registered linked issues and cards**, plus the IDs actually shown
in the hub's current view. Copy observed states, not the expected local values.
Check each card's `Finding ID` / `Lifecycle` header and URL; compare the current
hub listing separately. Keep earlier raw receipts. Then run:

```bash
python devtools/comparative_findings.py --check --snapshot path/to/readback.json
```

A current limitation or pending-review action with a closed live issue, a resolved finding with an open
issue, a card state/URL mismatch or a different current-index list fails the
check. No network requests occur in the checker or ordinary pytest. A partial
snapshot checks only supplied facets; it is not complete reconciliation.
These checks establish bookkeeping consistency, not scientific validity, profile
freshness, exact-source qualification or publication approval. Human review of
scope/evidence and the manuscript record remains mandatory.
