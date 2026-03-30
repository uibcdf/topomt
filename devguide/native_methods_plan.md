# Native Methods Plan

## Purpose

This document defines how TopoMT should evolve its engine implementations under
the following rule:

- `topomt.methods.*` should contain native TopoMT implementations;
- `topomt.wrappers.*` may integrate external binaries or libraries for import,
  auditing, and parity testing;
- parity against upstream tools is required for validation, but upstream code is
  not a runtime dependency target for `topomt.methods`.

The goal is not to copy upstream source code. The goal is to reproduce the
algorithmic semantics while using TopoMT and MolSysSuite building blocks where
they improve integration and maintainability.

## Shared implementation principles

For native reimplementations of external engines:

- preserve the defining algorithmic semantics of the original method;
- preserve the atom ownership semantics of the detected features;
- keep all coordinates and derived geometry in TopoMT canonical units;
- use `molsysmt` for structure loading, atom selection, format conversion, and
  atom-index mapping;
- use `pyunitwizard` directly for unit normalization at the API boundary and
  before numeric kernels;
- use `argdigest` and `depdigest` through TopoMT project-level adapters and
  configuration, not by importing those libraries directly in public API
  modules;
- use `smonitor` through TopoMT's local integration and catalog, so public
  API entry points and public native method entry points emit project-owned
  signals instead of isolated third-party decorators;
- expose results through `Topography` and `Feature` objects rather than through
  engine-specific containers;
- use wrappers and upstream runs only for parity tests and regression audits.

Implication:

- native methods should not grow local `value + unit` helper layers when
  `pyunitwizard` already covers the use case;
- if a needed quantity operation is missing, the gap should be addressed in
  `pyunitwizard` rather than worked around indefinitely inside TopoMT.
- if a function depends on an optional third-party library to provide its real
  behavior, that dependency should normally be declared with `depdigest`
  instead of ad hoc `try/except ImportError` handling;
- lightweight internal no-op fallbacks may still use `optional_import` when the
  intent is explicitly to keep a non-essential integration silent and inert
  rather than to expose a capability-gated public function.

Implication for dependency handling:

- `depdigest` should guard capability-bearing optional features such as
  visualization helpers, geometry backends, and wrapper-backed adapters;
- `optional_import` should be reserved for soft internal integrations whose
  absence should not present as a user-facing capability contract;
- `smonitor` should be treated as project infrastructure in the same sense:
  signals, warnings, and exceptions should be catalogued under TopoMT rather
  than attached ad hoc only where someone remembered to add a decorator;
- and quantity handling should consistently use TopoMT's configured
  `pyunitwizard`, not a mixture of project-local, `molsysmt`, and direct
  third-party import routes across different modules.
- and the project should keep a real `_depdigest.py` inventory aligned with the
  capabilities it exposes.

Practical note:

- extending `@arg_digest()` from `get_topography()` to public native methods
  should only be done once the public float-parameter semantics are explicit
  and consistent;
- `fpocket4` is now compatible with that rollout;
- `alphaspace2` is not yet, because its public bare-float cutoffs currently
  mean `nm`, while some older generic distance digesters still interpret bare
  numbers as angstroms.

## Shared future acceleration note

Acceleration and scalability should be treated as a cross-cutting future track
for all engine strategies, not only for `fpocket4`.

That future work should explicitly evaluate, engine by engine, whether a method
or part of its workflow can be:

- parallelized across a local CPU core pool;
- distributed across processes or nodes;
- or offloaded to GPU for the geometry-heavy stages.

This future evaluation should apply to:

- native TopoMT engines;
- wrapper-backed third-party engines;
- and future algorithms added later.

`alphaspace2`, for example, has not yet been evaluated systematically under
this lens.

See [engine_acceleration_plan.md](engine_acceleration_plan.md).

## `fpocket4`

### Current state

`topomt.methods.fpocket4` is currently wrapper-backed.

It preserves fpocket semantics well for the validated systems, but it does so
through:

- the external `fpocket` binary;
- parsing of fpocket output files;
- and a wrapper-to-`Topography` adaptation layer.

This is useful and should remain available, but it is not the final target for
`topomt.methods.fpocket4`.

### Upstream semantics that must be preserved

The native reimplementation needs to preserve at least:

- alpha-sphere generation from the Voronoi tessellation;
- alpha-sphere filtering semantics;
- initial clustering semantics;
- clustering refinement and merge behavior;
- pocket dropping criteria for tiny or overly polar pockets;
- pocket reindexing and ranking;
- pocket atom membership;
- primary descriptors such as score, druggability, alpha-sphere counts, and
  pocket volume.

### Useful upstream code landmarks

The main algorithmic landmarks in the upstream repository are:

- `src/fpocket.c`
  orchestration of the search pipeline;
- `src/voronoi.c`
  Voronoi-based vertex generation;
- `src/cluster.c` and `src/clusterlib.c`
  vertex clustering support;
- `src/refine.c`
  pocket refinement, merge, drop, and reindex logic;
- `src/descriptors.c`
  descriptor calculations;
- `src/pscoring.c`
  pocket scoring and druggability scoring.

### Native reimplementation plan

The native `fpocket4` work should be staged like this:

1. Reproduce the alpha-sphere generation and filtering stage natively.
   Before comparing tetrahedrization behavior, make sure the native path
   reproduces the same atom population that upstream `fpocket` sends into its
   geometry stage.
2. Reproduce the initial clustering semantics.
3. Reproduce `apply_clustering()`-style refinement and pocket merge behavior.
4. Reproduce pocket dropping and reindexing.
5. Reproduce pocket atom membership exactly enough for parity tests.
6. Reproduce descriptor calculations needed for the current validated contract.
7. Keep the wrapper layer as an integration path, but treat audited local
   source-build parity as the primary native validation target whenever wrapper
   binaries are known to drift by build.

### Residual geometry-policy issue

`1GG0.pdb` and `3LKF.pdb` currently expose a deterministic residual mismatch
that appears to originate in the tetrahedrization layer itself rather than in
the later pocket-filtering stages.

This should not be treated as an acceptable end state. Instead:

- the ambiguous regions should be detected explicitly;
- the affected systems should remain in the parity battery;
- and the issue should be tracked in
  [pocket_algorithm_issues.md](pocket_algorithm_issues.md).

The current working checkpoint for this diagnosis is recorded in
[fpocket4_native_checkpoint.md](fpocket4_native_checkpoint.md).

### Current anomaly note

`2HGR.pdb` is now a confirmed large-system deep-validation case.

Current reading:

- final native/source parity is already confirmed there;
- both the audited upstream build and the native path are expensive on this
  input;
- so it should continue to be used as a profiling and deep-validation target,
  not as part of the routine battery.

### MolSysSuite leverage points

Useful TopoMT-side tools for the native implementation include:

- `molsysmt` for input handling and atom identity mapping;
- `topomt.alpha_spheres` for alpha-sphere object support where appropriate;
- `pocket_geometry` for geometry support where it matches fpocket semantics;
- `pyunitwizard` for unit-normalized boundaries around the method.

### Cleanup after parity work

The native pocket methods should progressively express receptor preparation
through `molsysmt` selection/filtering helpers rather than through repeated
local purge pipelines.

Progress note:

- `fpocket4` now centralizes selected-receptor construction and atom-metadata
  extraction around shared `molsysmt` helpers;
- `pocketeer`, `castp`, and `pycasta` now also reuse a common heavy-receptor
  preparation helper instead of maintaining their own manual filtering code;
- the remaining debt is now narrower and method-specific, rather than the same
  preparation logic duplicated across several native engines.

Constraint:

- keep the validated method semantics unchanged;
- and treat this as implementation cleanup, not as an opportunity to retune the
  algorithms.

This should apply later to:

- `implementation='native'`
- `implementation='topomt'`
- and, when it exists, `implementation='topomt-scalable'`

## `alphaspace2`

### Current state

`topomt.methods.alphaspace2` is now in an intermediate native-reimplementation
state.

The geometry and pocket-membership layers have already been reworked around the
shared `topomt.alpha_spheres` layer, and the current audited tests reach
upstream parity for alpha generation, pocket counts, and pocket atom ownership
on the current reference systems.

What remains is the higher semantic layer: descriptors, nonpolar-space details,
beta scores, and the rest of the scoring semantics.

The native path now also already includes the basic optional contact layer:

- alpha contact masks from binder coordinates;
- beta contact propagation from child alpha spheres;
- pocket contact propagation and export through `Pocket.is_contact`.

### Upstream semantics that must be preserved

The native reimplementation should reproduce at least:

- alpha-sphere generation through Delaunay/Voronoi construction;
- exact four-atom lining assignment per alpha sphere;
- alpha-sphere radius filtering;
- alpha-space volume calculation from tetrahedra;
- nonpolar-ratio calculation per alpha;
- pocket clustering from alpha spheres with average linkage;
- beta clustering from pocket alphas with complete linkage;
- pocket lining-atom semantics;
- pocket centroid, total space, nonpolar space, and score semantics;
- optional contact and beta-score semantics where feasible.

### Useful upstream code landmarks

The main landmarks in the AlphaSpace2 repository are:

- `alphaspace2/Snapshot.py`
  main workflow orchestration;
- `alphaspace2/functions.py`
  geometry, SASA, grouping, and contact helpers;
- `alphaspace2/Cluster.py`
  semantic accessors for alphas, betas, and pockets;
- `alphaspace2/VinaScoring.py`
  probe-score support for beta scoring.

### Native reimplementation plan

The native `alphaspace2` work should be staged like this:

1. Reproduce `genAlphas()` faithfully:
   - Delaunay simplices;
   - Voronoi vertices;
   - exact lining atoms;
   - alpha radii;
   - alpha-space volumes.
2. Reproduce per-alpha nonpolar ratio with a TopoMT-native SASA route.
3. Reproduce `genPockets()` clustering semantics.
4. Reproduce pocket atom ownership from exact lining atoms.
5. Reproduce `genBetas()` clustering and beta aggregation.
6. Reproduce pocket score semantics from beta scores.
7. Add optional contact and binder-aware behavior after the apo path is stable.

### MolSysSuite leverage points

Useful TopoMT-side tools for the native implementation include:

- `molsysmt` for receptor construction, selection, and atom-index mapping;
- `molsysmt` or other ecosystem geometry routes for SASA-like calculations,
  instead of depending on the exact upstream private MDTraj internals;
- `pyunitwizard` for all unit normalization;
- `Topography` and `Pocket` for normalized output.

## Validation strategy

The validation path should differ from the runtime path.

### Runtime path

- `topomt.methods.*` uses only TopoMT and MolSysSuite dependencies.

### Validation path

- `topomt.wrappers.*` or audit scripts can run upstream binaries or packages;
- parity tests compare native TopoMT outputs against those upstream references;
- failures should be interpreted as semantic gaps in the reimplementation, not
  as evidence that TopoMT should import the upstream code at runtime.

## Immediate next steps

1. Keep `fpocket4` documented as wrapper-backed and transitory in `methods/`.
2. Start a native `fpocket4` plan around alpha-sphere generation and refine
   semantics.
3. Start a native `alphaspace2` plan around `genAlphas()` and exact lining
   atoms.
4. Extend tests so both methods can be measured continuously against their
   upstream references.
