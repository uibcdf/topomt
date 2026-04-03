# Integration with MolSysSuite

## Purpose

TopoMT is not intended to behave as an isolated library.

It belongs to the MolSysSuite ecosystem and should follow the shared contracts
used by the surrounding packages.

## `molsysmt`

`molsysmt` provides the molecular-system layer used by TopoMT.

Relevant expectations:

- molecular systems may come in multiple forms;
- selection and conversion should be delegated to `molsysmt`;
- coordinates should be treated canonically in nanometers;
- public APIs should fit the broader ecosystem style.

For TopoMT, this means:

- use `molsysmt` for atom selection;
- preserve correct atom indices after internal filtering;
- avoid reimplementing system-conversion logic locally.
- when TopoMT discovers a reusable molecular-system primitive, propose it to
  `molsysmt` instead of letting TopoMT accumulate a parallel systems layer.

## `pyunitwizard`

`pyunitwizard` defines the units contract.

Relevant expectations:

- user-facing quantities may come in different unit backends or forms;
- internal kernels should standardize to canonical units;
- standard units should be configured explicitly;
- fast-track conversions are useful for high-frequency paths.

For TopoMT, this means:

- standardize length-heavy geometry to nanometers;
- avoid direct backend-specific unit logic in scientific code;
- configure the library-level standard units explicitly;
- use raw magnitudes internally when performance matters.

Practical boundary rule:

- TopoMT core objects and native method outputs should preserve physical
  quantities on geometry-bearing feature fields such as centers, radii, and
  volumes;
- consumer boundaries that serialize or forward those values into other tools
  should normalize to canonical magnitudes only at that boundary layer.

Current example:

- `molsysviewer_topomt` keeps TopoMT features quantity-backed in the core, but
  normalizes viewer payloads to canonical `nm` / `nm**3` magnitudes and then
  rewraps those values as needed by MolSysViewer shape helpers.

## `argdigest`

`argdigest` provides input normalization for public functions.

Relevant expectations:

- public entry points should express their input contracts through digestion;
- optional caller-specific semantics should live in digesters, not in ad-hoc
  downstream code;
- digestion should remain bypassable through `skip_digestion` for trusted
  internal calls.

For TopoMT, this means:

- `get_topography()` is the correct place for public argument digestion;
- additional public APIs should follow the same model;
- digesters should be expanded as the public surface becomes clearer.

## `depdigest`

`depdigest` provides the optional-dependency policy.

Relevant expectations:

- soft dependencies must be imported lazily;
- dependency metadata should be centralized;
- runtime checks should happen at the point of use.

For TopoMT, this means:

- geometry or visualization extras should not be imported at module load time;
- optional backends such as `scikit-image` or future SASA tools should be
  mediated by `depdigest`;
- hidden undeclared soft dependencies should be avoided.

## `smonitor`

`smonitor` provides diagnostics and execution breadcrumbs.

Relevant expectations:

- public APIs should emit useful signals;
- error and warning categories should be catalog-driven;
- diagnostics should support ecosystem-level introspection.

For TopoMT, this means:

- main workflows should expose meaningful signals;
- error reporting should become more systematic across engines;
- the catalog should grow with the actual public workflows.

## `molsysviewer`

`molsysviewer` is the natural visualization target for TopoMT.

This integration is not the current phase, but it strongly affects design
choices made now.

In practical terms, TopoMT should aim to provide viewer-friendly feature data:

- canonical `atom_indices` for surface-based rendering;
- optional centers and radii for blob-based rendering;
- stable feature identifiers and source metadata;
- feature typing compatible with grouped layer visualization.

This also matters for DFND, even if DFND is postponed.

If DFND later returns richer channel, void, or dry-network structures, those
outputs should still be normalized in a way that remains compatible with the
same ecosystem contracts described in `devguide/DFND/`, especially the
architectural material in:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md)

## Practical design rule

Whenever a TopoMT implementation decision conflicts with an established
MolSysSuite convention, the default should be to follow the ecosystem contract
unless there is a strong and documented reason not to.

Related project rule:

- reusable molecular-system primitives discovered during TopoMT development
  should be documented and proposed upstream to `molsysmt`;
- TopoMT should keep only the temporary local implementation needed to avoid
  blocking engine work, and should prefer replacing it later with the
  ecosystem implementation.
