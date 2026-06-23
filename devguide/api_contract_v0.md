# TopoMT Public API Contract v0

Status: active development contract. TopoMT has no external compatibility
commitment yet, so broken, accidental, or unimplemented public symbols are
removed directly instead of being deprecated. Deprecation warnings are reserved
for a later release phase with external users.

## Public Top-Level Surface

The top-level `topomt` package intentionally exports:

- `__version__`, `__print_version__`;
- `pyunitwizard`;
- `config`;
- `demo`;
- `features`;
- `Topography`;
- `DelaunayMesh`;
- `WeightedDelaunayMesh`;
- `get_delaunay_mesh`;
- `get_topography`;
- `io`;
- `third_party`;
- `dfnd`;
- `tools`.

Anything else imported by implementation modules is not public unless it is
listed here and in `topomt.__all__`.

## Removal Policy During v0 Development

- Broken or non-executable API stubs are removed.
- Accidental exports are removed or kept internal.
- Working APIs that are still experimental must be documented as experimental or
  live below a clearly named submodule such as `dfnd` or `third_party`.
- New compatibility/deprecation shims require an explicit reason in devguide.

## Current Cleanup Decision

The legacy top-level `get_pockets()` / `show_pockets()` API was removed. It read
a process-relative `static/keys.txt`, ignored the requested method, and did not
fit the `Topography`-centric API. Pocket-like results should be obtained through
`get_topography(...)` and the returned `Topography` object, or through explicit
provider submodules under `topomt.third_party`.
