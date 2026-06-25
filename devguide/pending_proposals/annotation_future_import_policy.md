# Annotation Future Import Policy

Status: pending
Owner: unassigned
Created: 2026-06-25
Last reviewed: 2026-06-25

## Problem

`AGENTS.md` currently forbids `from __future__ import annotations`, but the codebase
uses it in several modules, including DFND, feature classes, topography code, and
private argument-digestion helpers.

This creates a style-contract mismatch: new contributors following `AGENTS.md`
will remove or avoid the future import, while existing modules use it as normal
practice. The current rationale in `AGENTS.md` also says modern Python already
supports deferred annotation evaluation through PEP 649, but TopoMT still targets
Python 3.10, 3.11, and 3.12, where this is not a practical replacement for the
future import.

## Evidence

Current occurrences include:

- `topomt/dfnd/classify.py`
- `topomt/dfnd/components.py`
- `topomt/dfnd/data.py`
- `topomt/dfnd/families.py`
- `topomt/dfnd/lineage.py`
- `topomt/dfnd/output_status.py`
- `topomt/features/BaseFeature.py`
- `topomt/topography/Topography.py`
- several files under `topomt/_private/arg_digestion/argument/`
- several files under `topomt/_private/smonitor/`
- `topomt/_private/optional_import.py`
- `topomt/third_party/pocketeer/_native_impl.py`

The 2026-06-06 code review already noted the same mismatch.

## Options

### Option A: Allow the future import

Update `AGENTS.md` to permit `from __future__ import annotations` while Python
3.10-3.12 remain supported. This matches current code, keeps runtime annotation
evaluation cheap, and avoids broad mechanical churn.

Tradeoff: type-hint introspection that relies on eager runtime objects must use
`typing.get_type_hints()` or an explicit local policy.

### Option B: Enforce the current rule

Remove `from __future__ import annotations` from all modules and adjust any
annotations that break at import time.

Tradeoff: this is mechanical but broad, risks unnecessary churn, and may force
quoted forward references or import-cycle workarounds. It also requires fixing
the PEP 649 rationale in `AGENTS.md`.

### Option C: Narrow exception

Keep the rule generally, but allow the future import only in modules with forward
references or import-cycle pressure.

Tradeoff: this is more nuanced, but harder to enforce consistently and likely to
drift again.

## Recommendation

Prefer Option A unless there is confirmed runtime annotation introspection that
breaks under postponed evaluation. The current code already relies on the future
import in multiple areas, and Python 3.10-3.12 support makes the prohibition
costlier than the benefit.

If Option A is accepted, update `AGENTS.md` and any shared MolSysSuite coding
guidelines so Ruff/style expectations match the codebase. If Option B is chosen,
treat it as a dedicated mechanical cleanup with tests/import smoke checks.

## Validation Plan

- Audit runtime annotation consumers (`typing.get_type_hints`, pydantic-like
  validation, custom introspection).
- Run import smoke tests for `topomt`, `topomt.dfnd`, and public feature classes.
- Run the focused DFND and viewer tests touched by modules whose annotation policy
  changes.
- Keep `AGENTS.md`, devguide, and actual source practice aligned after the
  decision.

## Decision Questions

1. Do we want `from __future__ import annotations` to be allowed while supporting
   Python 3.10-3.12?
2. Are there runtime annotation consumers in TopoMT that require eager annotation
   objects?
3. Should this policy be synchronized across MolSysSuite repositories?
