---
summary: Correct Topography's public result annotations and qualify bounded typing.
issue: uibcdf/topomt#77
status: resolved
opened: 2026-10-01
closed: 2026-11-11
severity: low
verification: reproduced
area: [api, typing]
guard: tests/test_topography_queries.py
normative:
blocked_by: []
supersedes: []
---

# Topography result annotations and bounded typing

## What

The issue's six original diagnostics concern unresolved MolSysMT imports,
unnarrowed dimensionality selectors, grouped sets annotated as lists and the
heterogeneous `info()` mapping. They predate the independent #74 copy fix.

## How

The original bounded invocation was `python -m mypy --follow-imports=skip
topomt/topography/Topography.py`. Recheck the current source and add typed public
consumer examples alongside runtime Mapping/filter/grouping controls.

## Why

Users should be able to inspect the public registry with truthful annotations
without losing its existing set-based semantics. A scoped checker result must
identify its scientific-dependency policy and cannot certify the whole package.

## What was refuted

The #74 copy fix did not introduce the historical typing diagnostics. Converting
sets to lists, blanket ignores or erasing the result to `Any` are not fixes.

## Scope and exclusions

Public registry queries/counts and their typing examples only; scientific
classification, provider results and the installed Python/OS matrix remain
separate. #86 owns CASTp geometry typing and #16 broad qualification.

## Acceptance criteria

Preserve Mapping, filtering and actual grouped sets; narrow selectors and expose
accurate return types, including integer dimensionality keys and integer totals.
Document and execute a bounded checker for the module and public consumer calls.

## Resolution — 2026-11-11

The original six diagnostics reproduce before editing. Following imports for
real type information exposes ten local errors; adding positive consumer
`assert_type` examples produces 23 diagnostics across the two selected files.
The corrected source and those examples now pass mypy 2.4.1 with the explicit
configuration `devtools/mypy_topography.ini`.

Overloads distinguish ungrouped/grouped results and object/ID sets, retaining a
safe union for runtime flags. `TopographyInfo` describes the four count fields,
including integer dimensionality keys and the integer total. Grouped IDs are
built as typed sets before optional object projection. Index-key casts preserve
actual dictionary lookup semantics, including numeric-equivalent keys and the
existing TypeError for unhashable keys. Concrete relation-method casts describe
already validated dimensional roles without imposing a new runtime class rule.
Remove the local postponed-annotation import and quote only the legitimate
within-class forward reference, preserving Python 3.11 syntax.

The **24 query controls pass before and after**, including Mapping identity,
all filters, grouped sets, neutral shape, integer counts, empty and invalid
queries, NumPy/float/bool dimension-key equivalence and detached ID-set mutation.
The broader registry/copy/context/binding/dispatcher selection passes **84
tests**. `add_new_feature`'s return documentation now describes its actual
generated-ID/None behavior rather than promising a feature object.

The bounded checker follows imports silently, reports selected module/consumer
errors and explicitly excepts unresolved MolSysMT/PyUnitWizard typing. It does
not erase local errors or certify every imported implementation/unannotated
method body.

Later #77 comments also retained native typing debt. That independently scoped
work is now owned by [#189](https://github.com/uibcdf/topomt/issues/189) and
[its report](../pending_bugs/native_dfnd_typing.md), with a current 56-diagnostic
four-file check. Those files are unchanged in this batch. #86 retains CASTp;
#16/#58 retain full scientific/installed/CI qualification. See
[the batch receipt](../evidence/api_maintenance_2026_11_11.json).
