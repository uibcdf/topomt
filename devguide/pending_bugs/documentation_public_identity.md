---
summary: Publish verified TopoMT documentation instead of the old PocketMT site.
issue: uibcdf/topomt#18
status: active
opened: 2026-11-10
closed:
severity: medium
verification: measured
area: [docs, deployment]
guard:
normative:
blocked_by: []
supersedes: []
---

# Public TopoMT documentation identity

## What

The public home identifies as PocketMT and BenchLab returns 404. Pages serves
the historical `gh-pages` branch at `f91fe8438c74f083fd605ba44d3c5a3e2595be7e`.
The current documentation workflow has no executions in its returned inventory.

## How

Prepare a source-identified Pages artifact with the official upload/deploy
route, then independently verify the served build manifest and case downloads.
The old branch remains retained. No package publication or force push is needed.
`devtools/docs_site.py` guards required pages, project identity and local file/
anchor targets before writing a source/byte manifest. Its regression started
with a missing module; five checks then passed. A second red regression exposed
theme-template HTML being mistaken for rendered pages; static templates now
remain hashed assets outside the page-navigation inventory.

## Why

A successful local build is not a served TopoMT site. Readers need the actual
DFND book and BenchLab rather than another project identity or false public
package/support badges.

## What was refuted

The scientific content was not absent from source. The serving route was stale.
Retained notebook outputs need no original engine execution during publication.

## Scope and exclusions

The source candidate replaces the old home with honest development guidance,
retains its notebook under `docs/freezer/`, repairs API/navigation/source links
and preserves frozen BenchLab bytes. Fresh local HTML gives zero warnings,
80 rendered pages and 6,620 valid local links. Local PlantUML uses the existing
cached Conda jar with a 256 MiB JVM limit; the hosted environment declares the
actual PlantUML runtime. Twenty-three documentation/CI/reporting checks pass.
The local candidate includes reviewed worktree changes relative to `2bc5149`;
it is not an exact-source public artifact. Remote candidate receiving is pending.

Native gh status/log inspection is used because gh-run-receptor is not installed;
this is its documented fallback, not a claim of receptor execution. Scientific
changes, #175 notebook work and installed/matrix qualification retain their owners.

## Acceptance criteria

Publish from the committed candidate, verify the official run/attempt and served
`build.json` source identity, case pages, notebooks and download byte hashes.
Observe normal browser rendering. Close only after this independent public
receiving; retain failed attempts and recovery identity if needed.
