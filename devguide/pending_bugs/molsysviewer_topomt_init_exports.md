# Bug Report: Missing Lifecycle Exports in `molsysviewer_topomt`

## Description

When MolSysViewer attempted to enable and interact with the TopoMT addon (e.g., during the execution of pocket-related scientific tutorials), an `ImportError` or `AttributeError` was thrown due to missing exports in `molsysviewer_topomt/__init__.py`. Specifically, the lifecycle hooks `on_enable`, `on_disable`, and `on_context_action` defined in `addon.py` were not imported or exported in the package's entry point, which deviated from the conventions observed in other peer integration modules (e.g., `molsysviewer_pharmacophoremt`).

## Proposed/Applied Fix

1. Modified [__init__.py](file:///home/diego/repos@uibcdf/topomt/molsysviewer_topomt/__init__.py) to import the missing hooks from `.addon`:
   ```python
   from .addon import ADDON, addon, get_addon, lifecycle, on_enable, on_disable, on_context_action
   ```

2. Appended them to `__all__` to make them available for public package import:
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

Successfully modified and validated. All pocket integration workflows now resolve these imports cleanly.
