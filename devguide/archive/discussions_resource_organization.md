---
summary: Organize resource Discussions with preserved history, facets and maintained guidance.
issue: uibcdf/topomt#103
status: resolved
opened: 2026-11-07
closed: 2026-11-07
severity: low
verification: inspected
area: [documentation, discussions]
guard:
normative: devguide/discussions.md
blocked_by: []
supersedes: []
---

# Discussions resource organization

## What

Implement the maintainer-approved six-category organization, preserving all
eleven existing resource conversations and completing the existing catalogue.
The prior provider-only organization remains recorded under #67.

## How

Configure categories first, then move #92 and append dated navigation updates.
Reuse #68/#69–#73 and the four literature threads; create canonical records for
remaining catalogue families and dataset resources. Publish forms, supported
facets, a resource register and mandatory root/nested AGENTS reading routes.

## Why

Separate scientific discovery, primary literature and evaluation resources while
supporting synthetic case-by-case DFND development and fair comparisons.
Keep evidence scope and integration status independent.

## What was refuted

The live GitHub GraphQL mutation schema supports thread and label operations but
has no category-management mutation. A form or guide cannot configure categories.
The GitHub connector also does not expose Discussions. Use the authenticated
GitHub CLI for supported operations and the maintainer web interface for categories.

## Scope and exclusions

No new engine integration, benchmark execution, dataset acquisition, scientific
qualification, hosting or release. Existing provider and study checkpoints retain
their own authority. Preserve the human-modified `topomt/_version.py`.

## Acceptance criteria

- Six intended categories exist and maintainers confirm the required UI formats.
- All eleven old IDs, URLs, original bodies and comment histories remain.
- Catalogue families and initial datasets have canonical resource conversations.
- Labels, placement, bidirectional navigation and published form bytes are checked.
- Maintained guidance and AGENTS reading routes are committed with applicable
  documentation/reporting checks; UI rendering limits are explicit.

## Observation and delivery

2026-11-07: all eleven discussions and all five categories were read without
pagination gaps. Category creation/renaming was requested from the principal
maintainer. Existing #68/#92 and versioned catalogues remain interim intake
routes while configuration was pending. Owner: LMMV/dprada; the initial
2026-11-14 review trigger was removed after the maintainer reported completion
and the categories were read back.

The maintainer clarified that devguide contains the instructions for maintaining
Discussions. Resource descriptions, substantive reviews, scientific arguments,
evidence and conclusions remain in their conversations. The guide, category
descriptions, forms and opening posts reflect that distinction. Reproducible
system artifacts and actionable decisions retain their normal owning records.

The final API audit found six intended category names/slugs/descriptions, with
Q&A answerable and the other five not answerable. Renaming preserved the old
category IDs. The maintainer reported completing the requested web setup with
the three resource categories open-ended; the API does not expose UI formats.

All eleven old discussion IDs and URLs were preserved. Each original body
remains an exact prefix, followed by a dated organization update; no existing
comment was removed. #92 moved into Datasets and Benchmarks; #10–#13 remain
in Literature and Resources; #68–#73 remain in Methods and Tools.

Twenty-nine new conversations bring the total to forty: twenty-two additional
third-party families (#104–#125), four collections (#126–#129), native DFND
(#130), the literature index (#131) and the start-here post (#132). The resource
register links twenty-eight methods/tools and four collections, including the
five existing provider conversations. Auxiliary CASTp repositories remain linked
under their family rather than acquiring duplicate detector records.

Sixteen feature/context/role/topic labels were created without altering existing
issue labels. New and old thread placement, expected label assignments, original
body preservation and resource-post bytes were independently read back. No
pagination was omitted. Candidate links retain unknown scientific/technical scope;
documentary review and executed comparison are explicitly different.

Three category forms replace the old Reading List form. YAML parsing, unique
field IDs and the three-field required intake were checked; filenames match the
observed slugs. Root and nested AGENTS, the contributor guide, README, category
indexes, tool/benchmark catalogues and provider navigation link the local upkeep
instructions. Guidance defines how to open and follow up in every category.

Checks: the reporting-protocol selection passed both tests; generated indexes
were checked; changed authored contributor Markdown was rendered by strict
isolated Sphinx/MyST and local file targets were checked before remapping links
for that render. Generated indexes were checked for links and by the index
validator, outside the authored-prose render; their existing H1-to-H3 header style
produces MyST style warnings. Exact commit/publication byte readback and final check counts are recorded
in #103 after pushing. These are contributor-document checks, not a full public
documentation build. Live GitHub form rendering was not visually exercised.

The scoped documentation change does not execute the scientific suite, installed
package matrix or remote CI. Those obligations retain #16/#58/#81; incremental
publication uses the authorized `[skip ci]` checkpoint route.
