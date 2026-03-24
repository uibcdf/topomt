# Ecosystem Integration

TopoMT is designed to live inside MolSysSuite rather than as an isolated
library.

## MolSysMT

`molsysmt` provides the molecular-system layer used by TopoMT for:

- system conversion;
- atom selection;
- atom-level data access.

## PyUnitWizard

`pyunitwizard` defines the units contract used by TopoMT.

The intended pattern is:

- user-facing quantities may come in different forms;
- internal geometry should be standardized to canonical units;
- high-frequency paths should prefer canonical magnitudes internally.

## ArgDigest, DepDigest, and SMonitor

TopoMT also follows the wider MolSysSuite integration model:

- `argdigest` for public argument normalization;
- `depdigest` for optional dependency management;
- `smonitor` for diagnostics and execution breadcrumbs.

## Why this matters

These ecosystem constraints are not secondary details. They shape:

- how the public API should behave;
- how soft dependencies should be loaded;
- how units should be handled;
- how future viewer integration should be prepared.
