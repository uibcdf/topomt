# ADR: Separate Third-Party Providers From Native TopoMT Methods

## Status

Accepted and implemented

## Context

TopoMT used to mix several distinct concerns inside the legacy `methods/` and
`wrappers/` trees:

- native TopoMT methods;
- external method integrations;
- backend-specific access paths for those external methods;
- file-loading logic that sometimes belongs conceptually to an external
  provider rather than to a generic I/O layer.

This creates a structural ambiguity around two different axes:

1. **Method ownership**
   Is the method native to TopoMT, or is it a third-party technology that
   TopoMT integrates?
2. **Access backend**
   Is the method accessed through a local native reimplementation, a Python
   library wrapper, an installed CLI tool, a remote server, or precomputed
   files?

Examples in the current codebase:

- `topomt.third_party.fpocket._native_impl` mixes wrapper-backed and local variants behind the
  same public entrypoint.
- `topomt.get_topography()` dispatches both by provider identity and by
  `implementation`.
- the old wrapper tree contained integrations that conceptually
  belonged to the corresponding external provider package.
- `topomt.io.load_CASTp()` is a valid public loader, but the underlying format
  belongs to the CASTp family of technologies rather than to a provider-neutral
  I/O subsystem.

At the same time, TopoMT is expected to evolve toward a genuinely native
topographic characterization line, with **DFND** as the central future method.
This implies that native TopoMT methods should have a dedicated architectural
space and should not remain mixed with third-party integrations.

## Decision

### 1. Reserve a native TopoMT namespace for native methods

The native TopoMT method line now lives directly under `topomt/dfnd/`.

Initial example:

- `topomt.dfnd`

Third-party technologies such as CASTp, fpocket, Pocketeer, or pyCASTA should
no longer be considered members of a native-method namespace in the
long-term architecture.

### 2. Introduce `topomt/third_party/`

A new package, `topomt/third_party/`, will host all integrations with external
technologies.

Examples:

- `topomt.third_party.castp`
- `topomt.third_party.fpocket`
- `topomt.third_party.pocketeer`
- `topomt.third_party.pycasta`

This package should represent the **provider identity** of the external method.

### 3. Organize each provider by backend of access

Inside each provider package, modules should be organized according to the
backend used to access that provider:

- `api.py`
- `files.py`
- `server.py`
- `library.py`
- `cli.py`
- `native.py`
- `topomt.py`
- `models.py`
- `_common.py`

Not every provider will need every backend module.

Intended meanings:

- `api.py`
  Stable provider-level public facade.
- `files.py`
  Parsing and loading of persisted provider results.
- `server.py`
  Submit/poll/download workflows against remote web services.
- `library.py`
  Integration with an importable upstream Python package.
- `cli.py`
  Integration with an installed executable or command-line tool.
- `native.py`
  Local reimplementation of the provider method intended to reproduce the
  original method semantics as closely as practical.
- `topomt.py`
  TopoMT-specific reinterpretation or corrected variant when TopoMT
  intentionally diverges from the original upstream semantics.
- `models.py`
  Provider-specific dataclasses or internal interchange structures.
- `_common.py`
  Internal utilities shared within the provider package.

### 4. Keep `topomt/io/` as a stable loading namespace

The `topomt/io/` package will not be removed.

Its role will be:

- to remain the user-facing namespace for file-oriented loading;
- to provide sugar functions that delegate to provider-specific parsers in
  `topomt.third_party.*.files`;
- to keep room for genuinely TopoMT-native loaders when applicable.

Examples:

- `topomt.io.load_CASTp(...)` may delegate to
  `topomt.third_party.castp.files.load_topography(...)`
- `topomt.io.load_CASTpFold(...)` may delegate to the corresponding CASTp
  family file loader

This allows users to think in either of two valid ways:

- "I want to load this file format"
- "I want to work with this provider"

### 5. Keep `topomt.get_topography()` as a high-level dispatcher

`topomt.get_topography()` remains valuable as a high-level user-facing entry
point.

However, its role should change:

- it should dispatch to native TopoMT methods under `topomt.dfnd.*`;
- it should dispatch to third-party providers through
  `topomt.third_party.<provider>.api`;
- it should gradually stop owning backend-specific branching logic directly.

The long-term intent is that `get_topography()` becomes a thin compatibility
layer and a convenient umbrella entrypoint, not the place where all provider
and backend semantics are defined.

## Proposed Directory Structure

```text
topomt/
  dfnd/
    __init__.py
    api.py
    ...

  third_party/
    __init__.py

    castp/
      __init__.py
      api.py
      files.py
      native.py
      models.py
      _common.py

    fpocket/
      __init__.py
      api.py
      cli.py
      files.py
      native.py
      topomt.py
      models.py
      _common.py

    pocketeer/
      __init__.py
      api.py
      library.py
      native.py
      models.py
      _common.py

    pycasta/
      __init__.py
      api.py
      library.py
      native.py
      models.py
      _common.py

  io/
    __init__.py
    load_CASTp.py
    load_CASTpFold.py
    ...
```

## Public API Direction

### Preferred provider-level API

The desired user-facing pattern is:

```python
tmt.third_party.castp.get_topography(molecular_system, backend='native')
tmt.third_party.castp.get_topography(molecular_system, backend='server', server='castpfold')
tmt.third_party.fpocket.get_topography(molecular_system, backend='cli')
tmt.third_party.castp.load_topography(zip_file='1tcd.zip')
```

This keeps the provider identity explicit while allowing backend choice through
`backend=...`.

### Explicit backend access

Provider packages may also expose backend modules for users who want direct
control:

```python
tmt.third_party.castp.servers.castpfold.get_topography(...)
tmt.third_party.castp.files.load_topography(...)
tmt.third_party.fpocket.cli.get_topography(...)
```

### API facade responsibilities

Each provider `api.py` should expose a stable minimal facade. Typical functions:

```python
def get_topography(molecular_system, backend='native', **kwargs): ...
def get_pockets(molecular_system, backend='native', **kwargs): ...
def load_topography(*, zip_file=None, dir_path=None, molecular_system=None, **kwargs): ...
```

Not every provider needs every function, but this should be the default shape
when applicable.

## Naming Rules

### `native`

Use `native.py` when TopoMT locally reimplements an external provider method
with the goal of reproducing that external method as closely as practical.

Examples:

- `topomt.third_party.castp.native`
- `topomt.third_party.fpocket.native`

### `topomt`

Use `topomt.py` only when TopoMT intentionally diverges from the original
third-party semantics and wants to expose a TopoMT-maintained reinterpretation
of that method family.

Example:

- `topomt.third_party.fpocket.topomt`

### `server`

Use `server.py` for remote job submission and retrieval workflows.

Example:

- `topomt.third_party.castp.servers.castpfold`

### `files`

Use `files.py` for all persisted result loading and parsing logic. Server-backed
modules should delegate to `files.py` after downloading artifacts whenever
possible, rather than parsing those artifacts themselves.

## Mapping From Current Structure

The current code suggests the following conceptual migration targets.

### CASTp

Current:

- `topomt.third_party.castp._native_impl`
- `topomt.third_party.castp.core.castp_core`
- `topomt.io.load_CASTp`

Target:

- `topomt.third_party.castp.native`
- `topomt.third_party.castp.castp_core` or internal equivalent
- `topomt.third_party.castp.files`
- `topomt.io.load_CASTp` as sugar delegating to `third_party.castp.files`

### CASTpFold

Current:

- `topomt.third_party.castp.servers.castpfold`

Target:

- `topomt.third_party.castpfold.server`
- `topomt.third_party.castpfold.files`

### fpocket

Current:

- `topomt.third_party.fpocket._native_impl`
- `topomt.third_party.fpocket._legacy_cli`
- `topomt.third_party.fpocket.parser`
- `topomt.third_party.fpocket.runner`
- `topomt.third_party.fpocket.model`

Target:

- `topomt.third_party.fpocket.native`
- `topomt.third_party.fpocket.topomt`
- `topomt.third_party.fpocket.cli`
- `topomt.third_party.fpocket.files`
- `topomt.third_party.fpocket.models`

### Pocketeer

Current:

- `topomt.third_party.pocketeer._native_impl`
- `topomt.third_party.pocketeer.library`

Target:

- `topomt.third_party.pocketeer.native`
- `topomt.third_party.pocketeer.library`

### pyCASTA

Current:

- `topomt.third_party.pycasta._native_impl`
- `topomt.third_party.pycasta.library`

Target:

- `topomt.third_party.pycasta.native`
- `topomt.third_party.pycasta.library`

## Compatibility Strategy

The migration should not be done as a big-bang rewrite.

Instead, TopoMT should proceed in phases:

### Phase 1: Introduce `third_party/`

- Create the new package and provider facades.
- Rehome provider code under `third_party/`.
- Delegate new provider APIs to the migrated implementations.

### Phase 2: Rewire high-level dispatch

- Make `topomt.get_topography()` dispatch to
  `topomt.third_party.<provider>.api` or `topomt.dfnd.api`.
- Minimize backend-specific branching inside `get_topography()`.

### Phase 3: Migrate tests and docs

- Update tests to prefer `topomt.third_party.*`.
- Update developer docs to describe the new structure.
- Keep compatibility tests only as long as the migration is incomplete.

### Phase 4: Remove legacy provider paths

- Remove obsolete `methods/` and `wrappers/` provider paths once the runtime,
  tests, and docs have been migrated.

## Consequences

### Positive

- Clear distinction between native TopoMT methods and external providers.
- Better scalability for server, file, library, and CLI workflows.
- Cleaner provider-centric public API.
- Easier documentation and testing organization.
- Better fit for the long-term DFND-centered architecture.

### Costs

- Requires compatibility shims during migration.
- Requires changes in internal imports, tests, and docs.
- Requires a stable naming policy for `native` versus `topomt`.

## Immediate Implementation Guidance

The recommended first implementation step is not to migrate all providers at
once.

Instead:

1. create `topomt.third_party`;
2. migrate one or two provider families first;
3. validate the API pattern;
4. then apply the same pattern to the remaining providers.

Good pilot candidates:

- `castp`
- `castpfold`

These already show the main structural ingredients:

- provider-specific file parsing;
- remote server integration;
- coupling to `io/`;
- common conversion to `Topography`.

## Notes

- This ADR does **not** require removing `io/`.
- This ADR does **not** require removing `get_topography()`.
- This ADR does **not** require immediate deprecation of old imports.
- This ADR is about clarifying ownership and access semantics before performing
  code motion.
