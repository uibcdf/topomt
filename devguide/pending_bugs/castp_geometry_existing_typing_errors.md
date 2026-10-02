---
summary: Correct the preexisting typing errors in the two CASTp geometry modules without changing scientific behavior.
issue: uibcdf/topomt#86
status: open
opened: 2026-10-01
closed:
severity: low
verification: reproduced
area: [castp, typing]
guard:
normative:
blocked_by: []
supersedes: []
---

# Existing CASTp geometry typing errors

## What

A bounded mypy invocation reports nineteen diagnostics in each CASTp geometry
module, 38 combined. NumPy arrays lack explicit annotations, variadic tuples
are used as fixed-length dictionary keys and rank construction indexes or
converts broadly typed `object` values.

## How

Run `mypy --follow-imports=skip --ignore-missing-imports` on
`topomt/third_party/castp/core/castp_core/geometry.py` and its CASTp3 counterpart.
The published baseline `951671678e02ed01b4c29b0b4b4ab9300b4a2d60` and current
H/OXT source produce the same 38 normalized error messages. Line numbers move
with the added input-policy operations; diagnostic operations do not change.

## Why

Runtime scientific parity and Ruff passes cannot be represented as a clean
geometry typing gate. #77 separately owns the existing Topography annotations.

## What was refuted

The current H/OXT corrections introduce no new diagnostic in this invocation.
Ignoring absent third-party stubs does not remove the local source errors.

## Scope and exclusions

Annotations and narrowing in the two geometry modules. No numerical changes,
scientific definition changes or blanket suppression of checker errors.

## Acceptance criteria

Both modules pass a documented bounded checker with an explicit dependency
stub policy while existing runtime geometry/parity guards remain green.

## 2026-10-02: explicit-definition validation boundary

The wider modern geometry/components/native check reports 40 diagnostics in
this repository, while a matched isolated before/after source comparison gives
43 versus 42 diagnostics (including absent package-export diagnostics), with
no newly added normalized messages. This broader invocation includes component
annotations outside the original nineteen-per-geometry scope. Exact arithmetic
and maintained audit tools pass their bounded check; neither outcome closes the
existing geometry typing theme.
