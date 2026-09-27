---
summary: Restore MolSysViewer TopoMT add-on lifecycle exports.
issue: uibcdf/topomt#55
status: resolved
opened: 2026-09-27
closed: 2026-09-27
severity: medium
verification: measured
area: [integration, reporting]
guard: tests/test_import.py::test_molsysviewer_topomt_exports_lifecycle_hooks
normative:
blocked_by: []
supersedes: []
---

# Bug Report: Missing Lifecycle Exports in `molsysviewer_topomt`

## Description

When MolSysViewer attempted to enable and interact with the TopoMT addon (e.g., during the execution of pocket-related scientific tutorials), an `ImportError` or `AttributeError` was thrown due to missing exports in `molsysviewer_topomt/__init__.py`. Specifically, the lifecycle hooks `on_enable`, `on_disable`, and `on_context_action` defined in `addon.py` were not imported or exported in the package's entry point, which deviated from the conventions observed in other peer integration modules (e.g., `molsysviewer_pharmacophoremt`).

## Proposed/Applied Fix

1. The package entry point, `molsysviewer_topomt/__init__.py`, now lazily
   resolves the hooks from `.addon` through `__getattr__`.

2. Its `__all__` declares them for public package import:
   ```python
   __all__ = [
       ...
       "on_enable",
       "on_disable",
       "on_context_action",
       ...
   ]
   ```

## Status

The package entry point declares the three hooks and resolves them through
`__getattr__`. The focused guard checks that package-level imports refer to
the same functions as the add-on module. It passed on the inspected
`015cb48001e947301b6eb42e8174d17aa7acb1b2` source using
`PYTHONPATH=. python -m pytest tests/test_import.py::test_molsysviewer_topomt_exports_lifecycle_hooks -q`.
This historical record was moved from the pending queue because the export
defect is resolved. Broader scientific pocket behavior is outside its scope.
