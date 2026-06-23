# API Surface

## Purpose

This document describes the practical status of the TopoMT API surface.

The repository contains public entry points, active native methods, wrapper-backed integrations, and experimental/provisional records. Contributors should distinguish stable user-facing feature APIs from raw diagnostic records.

## Current Public Core

The practical public core is centered on the symbols listed in [`api_contract_v0.md`](api_contract_v0.md). Implementation-wise, the core is backed by:

- [topomt/get_topography.py](/home/diego/repos@uibcdf/topomt/topomt/get_topography.py)
- [topomt/topography/Topography.py](/home/diego/repos@uibcdf/topomt/topomt/topography/Topography.py)
- [topomt/features/](/home/diego/repos@uibcdf/topomt/topomt/features)
- [topomt/delaunay_mesh.py](/home/diego/repos@uibcdf/topomt/topomt/delaunay_mesh.py)
- [topomt/tools/](/home/diego/repos@uibcdf/topomt/topomt/tools)

This is the surface new code should normally build on.

## DFND API Status

DFND is the native TopoMT method direction and is now an active hardening track.

Public entry points:

- `topomt.dfnd.dfnd(...)`: raw-first development/diagnostic API;
- `topomt.get_topography(..., method='dfnd')`: normal `Topography` integration.

The `Topography` view currently promotes only stable compatibility domain families to public feature objects:

- `void_domain` -> `Void`;
- `pocket_domain` -> `Pocket`;
- `channel_domain` -> `Channel` shorthand.

The returned `Topography` object also exposes DFND raw/provisional records through convenience attributes:

- `dfnd_records`;
- `dfnd_result`;
- `dfnd_concavity_domains`;
- `dfnd_external_links`;
- `dfnd_dry_components`;
- `dfnd_dry_interfaces`;
- `dfnd_dry_motifs`;
- `dfnd_surface_concavities`;
- `dfnd_nonresident_passages`;
- `dfnd_degenerate_subprobe_domains`.

Those convenience attributes are not independent public feature APIs. They expose records for method development, diagnostics, and validation.

## Conventional Engine API Status

The current conventional engine surface includes:

- `pocketeer`;
- `alphaspace2`;
- `fpocket4` / `fpocket`;
- `pycasta`;
- `castp`, `castp3`, and `castpfold` paths for historical/reference/server work.

These engines remain useful as references, wrappers, and comparison baselines. They should not define DFND semantics.

## Legacy or Transitional Areas

### Removed top-level `get_pockets()` / `show_pockets()`

The broken top-level legacy stub was removed under the v0 API policy. It read a
process-relative `static/keys.txt`, ignored the requested analysis method, and did
not fit the current `Topography`-centric architecture. Pocket-like results should
come from `get_topography(...)` or explicit provider APIs under `topomt.third_party`.

### `third_party/`

[topomt/third_party/](/home/diego/repos@uibcdf/topomt/topomt/third_party) contains provider integrations and backend-specific adapters.

This area is part of the active runtime surface, but provider internals should still be treated as integration code rather than stable user-facing API.

## Shared Utilities

[topomt/tools/](/home/diego/repos@uibcdf/topomt/topomt/tools) contains shared geometry, tessellation, and feature-characterization helpers.

This layer is active and reusable, but individual helpers may still be promoted or reorganized as DFND and the conventional engines converge on shared contracts.

## Practical Rule for Contributors

- Prefer `get_topography()`, `Topography`, `DelaunayMesh`, `topomt.tools`, and DFND raw records for new work.
- Keep stable feature objects separate from provisional records.
- Do not expose provisional DFND families or dry motifs as public features until validation supports that decision.
- Document clearly when a module is experimental, transitional, or stable.
