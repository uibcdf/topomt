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

Optional original engines are declared in `_depdigest.py` and guarded only at
their library entry points. Imports remain inside those functions. A conditional
guard preserves explicit source-checkout use through `upstream_root`; native,
file and web routes do not depend on the original Python distributions. Missing
libraries and executables have catalog-backed diagnostics with stable codes.
See the [user engine inventory](../user/third_party_engines.md).

The shared executable and explicit installation-route extension is tracked in
[DepDigest #22](https://github.com/uibcdf/depdigest/issues/22); coordinated adoption
belongs to [MolSysSuite #62](https://github.com/uibcdf/molsyssuite/issues/62).
The TopoMT fpocket runner retains its local missing-command translation until the
provider extension is released and adopted. Older DepDigest versions may still
suggest inferred Conda packages for pip-only engines; use the verified commands
in the engine inventory. Do not copy the shared extension into TopoMT or change
the mandatory provider version to an unpublished release.

## Why this matters

These ecosystem constraints are not secondary details. They shape:

- how the public API should behave;
- how soft dependencies should be loaded;
- how units should be handled;
- how future viewer integration should be prepared.
