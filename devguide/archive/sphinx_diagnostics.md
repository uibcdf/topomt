---
summary: Resolve existing whole-site markup, navigation and diagram-runtime diagnostics.
issue: uibcdf/topomt#64
status: resolved
opened: 2026-09-30
closed: 2026-11-10
severity: medium
verification: measured
area: [docs]
guard: tests/test_docs_site.py::test_pages_producer_treats_build_warnings_as_failures_before_upload
normative:
blocked_by: []
supersedes: []
---

# Whole-site documentation diagnostics

## What

The earlier source build reported eleven diagnostics outside the DFND book.
A zero exit code without warning-fatal mode did not establish a clean build.
The original issue retains the Python 3.13 and later 3.14 observations.

## How

Source `b57d533` replaces the historical root notebook with the current TopoMT
home, retaining the original bytes in `docs/freezer/index_2025.ipynb`. It repairs
the terminal transition, missing API entry, navigation and installation source
link. The intentionally separate AI guidance page declares its orphan status;
no warning category is suppressed. PlantUML is a declared documentation tool,
provided in the hosted environment and selected explicitly for local receiving.
The earlier citation diagnostic is absent at the reviewed source.

The first hosted run [42895119243](https://github.com/uibcdf/topomt/actions/runs/42895119243)
used the reviewed Python 3.14 dependency closure and produced zero warnings.
The next candidate makes warnings fatal with `-W --keep-going`, before artifact
upload, under `set -euo pipefail`. Its regression first failed on the old producer.
Final warning-fatal hosted receiving remains pending for this candidate.

## Why

Readers need preserved navigation and working diagrams, and publication must
fail rather than hide a new broken reference or markup diagnostic.

## What was refuted

The missing local PlantUML command was an environment/runtime issue, not a DFND
algorithm defect. The earlier missing bibliography warning was not reproduced
at the target revision. A successful non-strict build alone is insufficient.

## Scope and exclusions

Markup, references, diagrams and publication's warning gate. Scientific DFND
qualification, reader-route acceptance #175 and source identity #18 are distinct.

## Acceptance criteria

A complete fresh one-worker warning-fatal Sphinx build in the declared docs
route, source-scoped hosted evidence and the producer regression
`tests/test_docs_site.py::test_pages_producer_treats_build_warnings_as_failures_before_upload`.

## Delivered source and public receiving — 2026-11-10

Reader candidate `0af23bc4aeaab3c7c6f088a68867bed613d9612f` passed
[Documentation run 42906050055](https://github.com/uibcdf/topomt/actions/runs/42906050055)
with warnings fatal and zero warnings. Its served `build.json` identifies the
exact source, 83 HTML pages and 7,021 checked local targets. Independent receiving
checked 22 public pages/downloads against the original Pages artifact, including
all three new notebook pages and the complete ZIP. Binary download bytes match;
HTML differs only by independently decoded/verified Cloudflare email protection.
Actual Chrome displayed the served opening notebook and figure (1.51 s,
1,072.5 MiB peak owned browser tree). Earlier desktop/mobile/math and actual
JupyterLab inspection remain valid for their recorded presentation scope.

The [portable receiving receipt](../evidence/benchlab_reader_receiving_2026_11_10.json)
and [publication receipt](../evidence/benchlab_reader_publication_2026_11_10.json)
retain exact identities and limits. The selected panel gives **45 passed**;
scoped Ruff/format, six-file mypy, report/comparative indexes and dependency
declarations pass. This resolves this record's bounded acceptance. Physical
refinement #151, volume #75, broader science #76 and support #60/#61 remain open.
Original frozen notebooks, input files, certificates and provider evidence were
not rewritten. This is source-bound receiving, not a release/full-matrix claim.
