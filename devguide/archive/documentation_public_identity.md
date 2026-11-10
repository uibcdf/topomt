---
summary: Publish verified TopoMT documentation instead of the old PocketMT site.
issue: uibcdf/topomt#18
status: resolved
opened: 2026-11-10
closed: 2026-11-10
severity: medium
verification: measured
area: [docs, deployment]
guard: tests/test_docs_site.py::test_old_identity_and_missing_required_pages_cannot_be_published
normative:
blocked_by: []
supersedes: []
---

# Public TopoMT documentation identity

## Delivered public baseline — 2026-11-10

The official Pages artifact route published source
`b57d533f9d12ffec5cdc6a9215d4b8a8b9d3579d` in successful
[run 42895119243](https://github.com/uibcdf/topomt/actions/runs/42895119243).
The public HTTPS home identifies as TopoMT and BenchLab is reachable. Its
served `build.json` identifies that exact source; eighteen representative
pages/downloads were received independently. JSON/PDB/notebook/figure downloads
match the original artifact bytes. HTML differs only by Cloudflare's verified
email-obfuscation link and decode script; the decoded address and all remaining
HTML match the retained artifact. This transformation is recorded, not silently
treated as byte identity. Chrome verified desktop, narrow-window and worked
example rendering, including equations and figures, with one CPU and monitored
own-process memory below 2 GiB. No private browser profile was used.

The previous `gh-pages` branch remains retained at its original commit. Pages
now serves workflow artifacts; no force push or package release occurred.
The package's canonical documentation URL is the HTTPS `www` host; the old
non-www alias was observed redirecting through HTTP. This source change avoids
advertising that legacy alias without claiming its domain-level rule was fixed.

The first public artifact has 80 HTML pages, 6,620 validated local targets and
zero build warnings in the actual hosted Python 3.14 environment. #175's newer
reader notebooks and download retain their separate qualification/publication
checkpoint. Raw run, artifact, served-response and browser receipts are in
`.cache/benchlab-execution/web/`. Original diagnosis and candidate analysis below
are historical, including their then-pending remote status.

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
