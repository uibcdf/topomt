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

However, it still shows signs of incompleteness:

- placeholder project description;
- empty runtime dependency list;
- metadata that does not yet fully reflect the actual ecosystem contracts.

The repository versioning policy should now be treated as strict `X.Y.Z`
versioning with no tag prefixes or suffixes. Release tags are expected to look
like:

- `0.1.0`
- `0.2.0`
- `1.0.0`

This convention matters because TopoMT is being integrated with other
MolSysSuite repositories and we want release identifiers to remain simple and
predictable.

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

- hard scientific core: `numpy`, `scipy`, `molsysmt`, `pyunitwizard`;
- soft extras and optional integrations: visualization and some geometry tools;
- dependency metadata and packaging metadata are not yet fully aligned.

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
