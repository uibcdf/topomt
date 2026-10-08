---
summary: Preserve caller files and release memory-profile scratch and tracing.
issue: uibcdf/topomt#95
status: resolved
opened: 2026-10-08
closed: 2026-10-08
severity: medium
verification: reproduced
area: [tooling, governance]
guard: devtools/tests/test_profile_memory_resources.py
normative:
blocked_by: []
supersedes: []
---

# Memory-profile resource lifecycle

## What

At source `1ad2610634b16f9ae1d30ebc29323c09af012593`, the memory profiler
extracts a PDB to the fixed caller-side name `profile_memory_1crn.pdb`. Both
successful and failed measurements overwrite an existing file and leave scratch
behind. A failed `_measure` leaves newly started tracemalloc active.

## How

Python 3.14.7 stdlib-only children import the actual tool with inert scientific
module substitutes and a synthetic local ZIP. Existing caller PDB/report
sentinels demonstrate overwrite/retention without scientific calculations.
Calling the actual `_measure` with a failing build demonstrates retained tracing.
Seven regression cases fail before repair; the caller-tracing control passes.

Managed `TemporaryDirectory` now owns the extracted PDB until the last
measurement completes. A `finally` stops only tracing started by this operation.
The report path, field names, measurement formulas and scientific assertions
remain as before; caller tracing and unrelated files survive failure.

## Why

These are resource-custody defects under uibcdf/molsyssuite#104, independent of
TopoMT scientific maturity. Fixed scratch names can destroy unrelated evidence;
unreleased tracing affects subsequent operations in the same process.

## What was refuted

Caller report output and retained scientific archives are not disposable scratch.
No whole-directory deletion, blanket cache cleanup, scientific algorithm repair
or shared lifecycle framework is needed. Standard Python contexts suffice.

## Scope and exclusions

Local profiling helper and its resource guard only. No runtime API, dependencies,
SDK/policy pins, guide copies, package publication or scientific acceptance.
Selected tests use `--noconftest` to avoid the scientific warmup fixture. No
new package is built and no full scientific matrix is claimed.

## Acceptance criteria and verification

All eight real-tool guards pass: success, measurement failure, malformed archive,
caller output-directory failure and injected cleanup-reporting failure; early
and late tracing failures; caller tracing preservation. Actual managed scratch
disappears while caller sentinels remain. Cleanup error is injected after real
disposal and remains visible; this is not a permissions-failure test. Each
child/fixture is scoped and removed; no shared scientific namespace is replaced.

Seven of eight cases failed against the original source and pass after repair,
directly protecting the three observed mechanisms. The resolved guard is therefore
relevant as well as addressable. Hosted administrative receiving will verify the
exact pushed commit; full scientific/backlog evidence retains its existing owner
and scope under uibcdf/topomt#16 and uibcdf/molsyssuite#104.
