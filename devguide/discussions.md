# Maintaining TopoMT Discussions

Accepted by the principal maintainer on 2026-11-07; implementation and observed
GitHub settings are tracked in [#103](https://github.com/uibcdf/topomt/issues/103).
This applies the [MolSysSuite Discussions policy](https://github.com/uibcdf/molsyssuite/blob/main/devguide/github_discussions.md)
locally. Root [AGENTS.md](../AGENTS.md) makes it required reading for upkeep.

## Ownership and destinations

TopoMT maintainers, currently LMMV and dprada, own category configuration,
resource triage, supported labels and navigation until explicitly delegated.
There is no response-time promise. Contributors may suggest a resource with
only its name, official source and relevance; an audit or benchmark is not
required. Unknown details remain explicitly unknown.

Discussions contain resource descriptions, reviews, questions, scientific
arguments, evidence and the conclusions of those conversations. Keep opening
posts useful and self-contained rather than turning them into bare link lists.
This guide explains how contributors maintain that public space; it does not
require moving every review or finding into devguide. Link existing technical
documents and reproducible system studies where useful. Independently closable
defects, capabilities and validation phases belong in owning issues under the
[reporting protocol](reporting_protocol.md). Link both directions.
Record decisions with date and reason, and an observable revisit condition for
deferral. A listing, label, vote or thread closure does not accept a scientific
claim, public API, dependency or integration.

## Every future action has an owning issue

Maintainer refinement — 2026-11-08: **the issue board is the authoritative work
queue**. Every concrete future action in an opening post, comment or reply must
have a corresponding owning issue: investigation, pending assessment, deferred
implementation, validation, documentation correction or follow-up. Link both
directions and identify which action the issue owns; an unrelated umbrella or a
closed organization ticket does not cover a new review. Search/reuse a suitable
issue before creating another. Split independently closable work when appropriate.

Discussions retain analysis, evidence, questions and dated conclusions. A reference
or exploratory question without a selected action can remain informational;
say so explicitly when triaging, with scope/reason. Do not reword a promised task
as a question to remove it from the queue. Candidate discovery still accepts a
name/source/relevance without requiring an installation or full investigation.

Before completing Discussion upkeep, inspect affected opening posts and all new
comments/replies, list concrete actions, create/reuse their issues and add visible
current follow-up links. Deferred work stays tracked, with its reason and revisit
condition. For a closed task, reconcile the originating current summary and
linked finding state; preserve the original request/results as history. If work
remains, keep/reopen its issue or create an explicit follow-up before closing.

The [dated action-routing audit](discussion_actions.md) maps all 42 conversations
and five comments observed in this adoption. It records responsibility rather than
copying issue open/closed status. Refresh affected rows as work changes; new
conversations/actions need the same triage. No automatic monitoring is promised.
All `needs_review` comparative findings require an open owning issue/local report,
as enforced by [their lifecycle check](comparative_findings.md).

## Categories

Keep these six categories. The first three retain the common names, slugs and
formats, even when empty. All categories have the maintainer ownership above.

| Category / slug | GitHub format | Purpose and follow-up |
| --- | --- | --- |
| Announcements / `announcements` | Announcement | Maintainer updates linking recorded releases, decisions or development milestones. |
| Q&A / `q-a` | Question and answer | Usage, interpretation and public-API questions; useful answers become maintained examples or clarifications where appropriate. Actionable findings use issues. |
| Ideas / `ideas` | Open-ended discussion | Exploratory DFND, scientific, API and workflow questions. Actionable work moves to an owning issue; decisions remain in that issue or a named versioned record. |
| Methods and Tools / `methods-and-tools` | Open-ended discussion | Describe, study and compare algorithms, programs, libraries, wrappers and services: capabilities, limitations, evidence, APIs, usability and performance. Link related technical records and actionable issues. |
| Datasets and Benchmarks / `datasets-and-benchmarks` | Open-ended discussion | Discuss synthetic and molecular collections, geometric references, annotations, metrics, protocols and comparative results. Link reproducible inputs and results in the [study area](DFND/study_zone.md) or other evidence records. |
| Literature and Resources / `literature-and-resources` | Open-ended discussion | Discuss primary papers, reviews and technical resources: relevant findings, arguments, limitations and scientific questions. Link related methods, datasets and any resulting work. |

Use the [resource register](discussion_resources.md) and existing catalogue
discussions as entry points. One resource can cover several phenomena and roles;
do not create categories for each algorithm, feature, provider or DFND case.

The three resource categories have forms in `.github/DISCUSSION_TEMPLATE/`.
The filename must match the observed category slug. Forms require only resource
name/title, official source and relevance; review context is optional. A source
file published on the default branch does not establish that GitHub renders it.
GitHub's [category-form syntax](https://docs.github.com/en/discussions/managing-discussions-for-your-community/syntax-for-discussion-category-forms)
documents the slug and field requirements.

## Opening and following up in each category

| Category | What to include when opening | How to follow up |
| --- | --- | --- |
| Announcements | Maintainer-authored factual update, the affected audience, scope/date and links to the release, decision or recorded milestone. | Correct outdated instructions with a dated update. Concrete follow-up work uses owning issues; an announcement is not a release receipt. |
| Q&A | A clear question, intended result, relevant public-API call and version; add a small shareable example and the observed result where useful. Do not require a full bug investigation to ask. | Mark a useful answer when resolved. File actionable suspected defects in issues and link them; improve examples or documentation for recurring misunderstandings. |
| Ideas | The scientific or user problem, motivation, a possible approach and uncertainties. | Discuss alternatives. Once a bounded change is actionable, find/open the owning issue and link it rather than maintaining an implementation queue here. Record the decision and reason. |
| Methods and Tools | Resource name, official source, scientific object and reason to study it. Add known findings, limitations, version, access and questions using the form. | Reuse the resource thread across reviews and versions. Add dated findings, evidence and conclusions; link associated datasets, papers and system studies. |
| Datasets and Benchmarks | Collection/study name, original or distribution source and evaluation question. Describe known provenance, references, definitions, metrics and limitations. | Qualify inputs and references before interpreting results. Discuss comparative outcomes here with links to reproducible artifacts; record exclusions, failures and independence limits. |
| Literature and Resources | Original title, primary source/DOI and why it matters. State the claim or question that deserves discussion. | Add critical reading, source-reported findings and our interpretations separately. Cross-link related tools and datasets; identify the evidence needed to settle an open question. |

For all categories, search existing conversations first, use a descriptive title
and share only public, authorized material. Automatic forms guide resource intake;
they are not an approval checklist. Maintainers apply supported labels after
reviewing the actual subject. Search results and resource indexes complement each
other; opening a discussion does not require an advance maintainer assignment.

## One maintained conversation per resource

Search the register, discussion titles and related issues before creating a
thread. Reuse the same resource conversation across versions, checkpoints and
research phases. Keep family members together when they share the study object;
split materially different engines, datasets or responsibilities when needed,
explaining the relationship. A wrapper is not an independent detector oracle.

A paper documenting a tool may be cited in its tool thread. Retain a separate
literature conversation when the paper's methods, interpretation or evidence
merit discussion. Existing POVME paper threads #10/#11 retain their identity
and cross-link the tool-family conversation. A benchmark dataset keeps its own
conversation and links relevant methods and papers.

A resource opening post should provide:

1. Official source and known version/revision or dated publication.
2. Scientific object, supported scope and relationship to TopoMT.
3. What we could learn about science, guided use, public APIs or performance.
4. Source-reported limitations, our hypotheses and open questions, distinguished
   from independently reproduced observations.
5. A controlled study question, when justified, and links to relevant cases.
6. Evidence scope, access/licence unknowns and relevant technical records.

Short historical leads may remain Candidate with a specific assessment question.
Do not invent capabilities, versions or limitations to fill fields. Keep the
existing technical catalogues as supporting references, retaining the resource's
description and scientific discussion in its own conversation.

## Labels are independent facets

Categories describe resource type. Maintainers apply labels to the **whole
discussion**, using its source-supported scope. Several values can coexist;
unknowns need no label. Labels do not classify individual comments or every paper
mentioned in an index. Keep mixed index threads unlabelled when a feature label
would incorrectly imply that the whole collection shares that scope.

| Namespace | Initial values | Meaning |
| --- | --- | --- |
| `feature:` | `voids`, `pockets`, `channels`, `pores`, `protrusions`, `interfaces`, `cryptic-pockets` | Scientific objects or questions covered. A pocket label makes no binding or druggability claim. |
| `context:` | `synthetic`, `molecular`, `trajectories` | Input or evaluation context under discussion; trajectory analysis is separate from single-frame geometry. |
| `role:` | `provider`, `comparison`, `related-project` | Existing provider route, intended methodological comparison, or related implementation/workflow. A comparison label does not mean a benchmark was executed. |
| `topic:` | `dfnd`, `api`, `performance` | Explicit native-method, public-interface or measured-performance questions; apply when central to the conversation. |

Preserve existing issue and cross-component labels. Add a new label only for a
recurring, independently useful facet; document its meaning here. Labels such as
validated or superior cannot substitute for scoped evidence and provider contracts.

For example, MOLE's method thread can carry `feature:channels`, `feature:pores`,
`context:molecular`, `role:comparison` and `topic:dfnd` for the questions it covers.
The synthetic collection instead uses `context:synthetic` and `topic:dfnd` in
Datasets and Benchmarks. A dedicated cryptic-pocket reading can use
`feature:cryptic-pockets` and the supported molecular/trajectory contexts without
becoming a tool or dataset conversation.

## Evidence and fair comparisons

Maintain separate study and integration information:

- Candidate: a lead is recorded; technical assessment remains pending.
- Documentary review: specified sources or revisions were inspected. State the
  date and scope; this does not imply installation or execution.
- Comparison planned: a bounded question and protocol have an owning record.
- Comparison recorded: executed inputs, versions, settings, original outputs,
  metrics and limits are available in the linked study. This does not establish
  success, equivalence or general scientific qualification.
- Deferred or not selected: retain a dated reason and concrete revisit condition.

Existing optional-provider routes, local reproductions, canonical Topography
admission and scientific interpretation remain separate evidence boundaries.
Keep substantive review findings and conclusions in the conversation, with
dated updates and links to their evidence. Accepted/deferred/rejected decisions
also retain the owning issue or named versioned record required by common policy;
that requirement does not make every discussion contribution a devguide document.
Use [current status](status.md) for the scientific phase and the issue board for
individual action ownership/scheduling; historical pauses and receipts do not
override later maintainer decisions.

For a comparison, freeze geometry, atom selection, radii, units, preparation,
parameters and software identity. Explain differing feature definitions and
eligible inputs before interpreting counts, volumes, paths or timings. Preserve
failed, unavailable, unsupported and valid-empty outcomes separately. References
independent of DFND and the comparator are required before calling a synthetic
result ground truth. Report preparation, execution and memory scopes explicitly.

## Connecting the system study area

Follow [the study-area design](DFND/study_zone.md): descriptive stable case names,
one versioned study unit per system, independent references and original
third-party observations. Documentation and a future standalone site consume
the same scientific content. Discussions contain the interpretation and debate,
linking those units so their frozen inputs and results can be reproduced. Summarize
relevant results in the thread while retaining artifact identity in the study.

Create a case conversation only for a concrete scientific question, in Datasets
and Benchmarks, linked from the case and relevant resources. Do not create empty
conversations for all catalogue entries. Continue synthetic-first development
under the active laboratory checkpoint before new protein characterization.
Improvements sought from DFND remain hypotheses until independent evidence
supports them.

Operate the comparative findings hub and its advantage/limitation cards under
[the lifecycle instructions](comparative_findings.md). Keep their current state
and dated history separate. A corrected limitation leaves the current view;
update the card, index, lifecycle metadata and affected method/case summaries
with its issue/report closeout. Incomplete reconciliation is `needs_review`.
Preserve historical evidence and require target-specific review before a paper
claim; a resolved issue, stale comment or label is not publication evidence.

## Maintainer upkeep

1. Identify the canonical resource and category; link duplicates without deleting
   useful history. Preserve discussion numbers, URLs, comments and dated scientific
   conclusions. Refresh opening-post navigation and summaries while keeping prior
   conclusions and reasons visible when a later review supersedes them.
2. Apply supported facets and record the review date, scope and missing evidence.
3. Add or refresh the resource-register row and affected catalogue links.
4. File actionable work in an owning issue, following the local report lifecycle
   when detailed analysis is needed. Summarize and cross-link the disposition.
5. Append dated corrections when scheduling or evidence has been superseded.
   Update navigation without silently rewriting historical scientific claims.
6. Run applicable reporting checks, parse and review form fields, check local
   links and render changed Markdown. Independently read back remote categories,
   thread placement, labels and published form bytes. Only UI observation proves
   category formats or rendered-form behavior that the API cannot expose.

Review when upstream changes, study findings, service failures or development
provide a reason. No automatic monitoring or response commitment is established.
Read-only study is distinct from authorization to post, acquire data, contact
authors, submit coordinates or execute/integrate software. Keep public records
within the normal disclosure rules.

## Configuration observation

The bounded migration receipt in #103 records desired settings, observed API
state, source publication and remaining UI evidence separately. The inspected
live GitHub GraphQL schema has thread and label mutations but no category-management
mutation. A maintainer configures category names, descriptions and formats through
the web interface. A guide or form does not configure GitHub; do not recreate
threads to simulate a category change.
