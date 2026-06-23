# Packaging and Environments

## Purpose

This document summarizes the current state of packaging, dependency metadata,
and environment definitions in the repository.

## Current status

The packaging layer is functional enough for development, but clearly still in
transition.

### `pyproject.toml`

[pyproject.toml](/home/diego/repos@uibcdf/topomt/pyproject.toml) is the main build-system file and
uses `versioningit`.

The runtime dependency list now follows the current import audit:

- core runtime dependencies are imports required by the public load path;
- optional dependencies are lazy, feature-gated, or backend-specific imports;
- metadata still needs to be mirrored in the conda recipe/environment layer.

The operational rule is:

- top-level import on the public load path means a core dependency;
- lazy, gated, or backend-specific import means an optional extra;
- packages with no active imports should not be kept as runtime dependencies.

The current core dependency set is:

- `numpy`;
- `scipy`;
- `molsysmt`;
- `pyunitwizard`;
- `smonitor`;
- `argdigest`;
- `depdigest`.

`networkx` is intentionally not core. It is guarded as the `centerline` extra
because it is imported lazily by the DFND channel-skeleton path. The `viewer`
extra includes `topomt[centerline]`, because the MolSysViewer channel-tube
representation consumes that skeleton.

`pyunitwizard` has one release gate that packaging must not hide: TopoMT now
uses `pyunitwizard.conversion_factor`, but that API is newer than the latest
published `pyunitwizard 0.22.0` release at the time this note was written.
This does not block the development work package, because MolSysSuite
packages are still moving together in editable development environments. It
does mean that a public TopoMT release must set the final `pyunitwizard`
minimum version after PyUnitWizard cuts a release containing
`conversion_factor`.

`depdigest` has the same publication note for conditional optional
dependencies: TopoMT uses `dep_digest(..., when={...})` on scientific
arguments that can be NumPy arrays. A public TopoMT release must set the
final `depdigest` minimum version after DepDigest releases the array-safe
conditional comparison used by that guard.

The repository tag policy should now be treated as strict `X.Y.Z`
versioning with no tag prefixes or suffixes. Release tags are expected to look
like:

- `0.1.0`
- `0.2.0`
- `1.0.0`

This convention matters because TopoMT is being integrated with other
MolSysSuite repositories and we want release identifiers to remain simple and
predictable.

This applies to git tags. Development builds derived from `versioningit` may
still include local metadata such as commit distance or dirty state when the
working tree is not exactly on a release tag.

### `setup.cfg`

[setup.cfg](/home/diego/repos@uibcdf/topomt/setup.cfg) still carries `versioneer`
configuration, which suggests repository drift from an older packaging phase.

This should be documented rather than ignored, because it affects how
developers interpret the packaging state.

## Development environments

The repository includes multiple environment definitions under
[devtools/conda-envs/](/home/diego/repos@uibcdf/topomt/devtools/conda-envs).

These files are useful, but the surrounding tooling in
[devtools/](/home/diego/repos@uibcdf/topomt/devtools) also contains legacy
material and older guidance that no longer reflects the cleanest current
workflow.

The practical reading is:

- environment files are useful references;
- the development-tooling story is not yet fully modernized;
- some `devtools` content is historical rather than authoritative.

## Dependency metadata

[topomt/_depdigest.py](/home/diego/repos@uibcdf/topomt/topomt/_depdigest.py) defines the current
dependency model for TopoMT.

This is important because it already captures the intended hard/soft split more
accurately than `pyproject.toml`.

Current interpretation:

- hard scientific core in `depdigest`: `numpy`, `scipy`, `molsysmt`;
- soft extras and optional integrations: `networkx`, `scikit-image`,
  `scikit-learn`, `mdtraj`, and `biotite`;
- MolSysSuite infrastructure such as `argdigest`, `depdigest`, and `smonitor`
  is declared in packaging metadata, but is not modeled as a feature dependency
  inside `_depdigest.py`;
- dependency metadata and packaging metadata must stay aligned with the conda
  recipe/environment layer.

## Diagnostics and digestion config

The package-level ecosystem configuration is also spread across:

- [topomt/_argdigest.py](/home/diego/repos@uibcdf/topomt/topomt/_argdigest.py)
- [topomt/_smonitor.py](/home/diego/repos@uibcdf/topomt/topomt/_smonitor.py)
- [topomt/_pyunitwizard.py](/home/diego/repos@uibcdf/topomt/topomt/_pyunitwizard.py)

This means that a future cleanup of packaging and environments should not be
treated as a purely packaging-only task. It is also an ecosystem-integration
task.

## Practical conclusion

The repository should eventually document one clear answer to each of these
questions:

- how to install TopoMT for normal use;
- how to create a development environment;
- which dependencies are truly required at runtime;
- which dependencies are optional;
- which build/versioning path is authoritative.

The current document records that these answers are not yet fully consolidated.

## Current checkpoint

The `0.1.0` tag records the first faithful fpocket integration checkpoint for
TopoMT on the currently supported reference PDB systems.
