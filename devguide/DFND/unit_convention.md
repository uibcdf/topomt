# DFND unit convention

Status: settled. DFND now uses nanometres as the internal kernel unit and as
its raw-record unit. Public TopoMT features still expose physical values as
PyUnitWizard quantities.

## The convention

- **Internal kernel and raw DFND records: nanometre.** Coordinates, radii,
  `R_residence`, `R_gate`, `probe_radius`, tolerances, `epsilon`, raw centers,
  raw areas, and raw volumes are stored as bare numerical values in `nm`,
  `nm**2`, and `nm**3` as appropriate.
- **Raw schema is explicit.** Raw DFND dictionaries carry
  `schema_version = 'dfnd.raw.nm.v1'` and a `units` mapping. Consumers must not
  infer angstroms from field names or historical notebooks.
- **Public TopoMT features: quantities.** Values promoted to `Topography`
  features are PyUnitWizard quantities in suite-standard units (`nm`, `nm**2`,
  `nm**3`). Consumers must read them through `puw.get_value(...)`.
- **Human presentation: angstroms are allowed after conversion.** Viewer labels,
  hover text, and diagnostic cards may display `Å`, `Å²`, and `Å³` because this
  is the cavity-analysis idiom. They must convert explicitly from raw nm values
  before formatting.

## Input policy

Public APIs should not rely on bare floats for physical lengths. The preferred
form is a PyUnitWizard quantity, for example
`probe_radius=puw.quantity(1.4, 'angstroms')` or
`probe_radius=puw.quantity(0.14, 'nm')`.

Compatibility facades still accept legacy bare floats in selected places:

- `dfnd()` / `dfnd_to_topography()` / public `get_topography(..., method='dfnd')`
  interpret bare `probe_radius`, `epsilon`, `residence_tolerance`, and
  `permeability_tolerance` as angstroms, emit a `FutureWarning`, and normalize
  them to nm.
- `DFNDData.at_probe()` follows the same public compatibility rule for a bare
  `probe_radius`: warn, interpret as angstroms, normalize to nm.
- `DelaunayFlowNetwork.get_topography()` keeps the lower-level legacy bare-float
  convention for direct calls.
- `DelaunayFlowNetwork.from_arrays()` is a synthetic/toy-system helper. Bare
  coordinates, radii, and `epsilon` are interpreted as angstroms and converted to
  nm internally.
- `DFNDQuery` and `DFNDMeshConfig` store normalized nm values and accept
  PyUnitWizard quantities directly. Direct bare-float construction is an
  internal/programmatic compatibility path and represents normalized nm values.

## Why nm internally

Using nm internally aligns DFND with MolSysSuite storage and with the
molsysviewer transport boundary. It also removes repeated conversions between
MolSysMT, raw records, public features, and viewer payloads. The domain still
uses angstroms in presentation and examples; that is a formatting concern, not a
kernel-unit contract.

## Rules for new code

- Store DFND raw lengths/coordinates in nm, areas in `nm**2`, and volumes in
  `nm**3`.
- Promote public feature values as PyUnitWizard quantities.
- Require or strongly prefer quantities for public length arguments; treat bare
  floats as legacy compatibility only.
- If a human-facing string says `Å`, `Å²`, or `Å³`, convert from nm first.
- Do not expose a new bare float physical field unless the raw `units` mapping
  documents it.

`volume_solvent_estimate` is the current deterministic local estimate of empty
volume inside resident tetrahedra after excluding the four local atomic spheres
of each tetrahedron. It is not an analytic sphere-tetrahedron intersection
formula and does not yet include non-local atom intrusions.

Future higher-precision physical metrics should be added with explicit names
rather than overloading existing topological fields.
