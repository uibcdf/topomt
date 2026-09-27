---
summary: Review TopoMT Python ecosystem policy adoption.
issue: uibcdf/topomt#56
status: active
opened: 2026-09-27
closed:
verification: measured
area: [governance, tooling]
guard:
normative:
blocked_by: []
supersedes: []
---

# Review Python ecosystem policy adoption

**Reported:** 2026-09-27. Inspected `origin/main` at
`015cb48001e947301b6eb42e8174d17aa7acb1b2` under the MolSysSuite
Python ecosystem policy.

## What

Support-library adoption is **partial**; developer-tool adoption is
**adopted** for the inspected CI and run-inspection routes. This review is
independent of TopoMT's Python-support matrix work in `uibcdf/topomt#16`.

## How

The package declares ArgDigest, DepDigest, SMonitor, and PyUnitWizard as
runtime dependencies. `get_topography()` uses argument digestion and
structured signals; quantity paths use PyUnitWizard. `_pyunitwizard.py`
initializes shared defaults only if no policy is active. DepDigest has a
configuration and optional runtime decorators. However, SMonitor's catalog
still fails to render authored diagnostics under `uibcdf/topomt#15`, and
the AlphaSpace2 optional backend has a boundary that warrants review before
claiming full DepDigest adoption. Keep these component implementation matters
in their member issues and add focused tests when addressed.

Both maintained test Conda environments pin published Pytest Receptor `0.6.0`.
`.github/workflows/CI.yaml` selects `--receptor=ci` without changing test
selection or coverage options. Published GH Run Receptor `1.0.0` inspected
exact-source CI `36311638015`, policy `36311638223`, and Ruff `36311638009`.
The policy and Ruff runs passed; the CI test matrix failed six of six jobs
with `ModuleNotFoundError: alphaspace2` in the test step, which the receptor
reported as failure. This does not make the tool adoption claim false; it
does mean the matrix is not passing release evidence.

Commands for the hosted inspection:

```bash
gh run-receptor inspect 36311638015 --repo uibcdf/topomt --receptor=llm
gh run-receptor inspect 36311638223 --repo uibcdf/topomt --receptor=llm
gh run-receptor inspect 36311638009 --repo uibcdf/topomt --receptor=llm
```

## Why

The central `pending` entries signified that no member-specific review had
been recorded. They did not prove absence of the support libraries or tools.
Separate states keep a known SMonitor defect and optional dependency review
visible while recognizing verified tool use.

## What was refuted

The old `uibcdf/topomt#16` checklist said Ruff used only selected critical
rules and that CI omitted ArgDigest. Current Ruff runs `ruff check .` and
`ruff format --check .`; CI installs exact controlled source dependencies,
including ArgDigest. The remaining CI failure is not evidence that those
governance paths are missing.

## Scope and exclusions

This report owns TopoMT's library and developer-tool applicability review.
Scientific AlphaSpace2 behavior and the SMonitor catalog repair remain local
implementation work. A green full matrix is not claimed here.

## Acceptance criteria

Resolve or bound the SMonitor catalog defect and optional dependency gaps,
verify representative public boundaries, and refresh the central inventory
from exact-source evidence before upgrading support libraries to `adopted`.
Keep developer-tool evidence current if CI environments or run inspection
change.
