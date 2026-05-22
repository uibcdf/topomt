# Native Methods Plan

## Purpose

This document defines how TopoMT should evolve its engine implementations under
the following rule:

- `topomt.dfnd.*` is the native TopoMT method line and DFND is the native TopoMT pocket/topography method;
- `topomt.third_party.*` integrates external binaries, libraries, servers,
  persisted outputs, and parity helpers;
- parity against upstream tools is required for validation, but upstream code is
  not a runtime dependency target for native TopoMT methods.

The goal is not to copy upstream source code. The goal is to reproduce the
algorithmic semantics while using TopoMT and MolSysSuite building blocks where
they improve integration and maintainability.


## DFND native pocket algorithm

The CASTp1/CASTp3 audit established that exact CASTp3/CASTpFold reproduction is not currently a reliable primary target without server internals. The native TopoMT method line is DFND: a TopoMT-owned pocket and topography algorithm with explicit rules and diagnostics.

Initial design checkpoint:

- [topomt_native_pockets_initial_design_2026_05_19.md](topomt_native_pockets_initial_design_2026_05_19.md)

The previous idea of a separate native pocket method outside `topomt.dfnd.*` is superseded. DFND is the native method; CASTp1, CASTp3/CASTpFold, fpocket, and AlphaSpace2 remain benchmarks and references, not hidden specifications.

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

Progress note:

- `fpocket4` already had an explicit wrapper-backed `Topography` path;
- `pocketeer`, `alphaspace2`, and `pycasta` now also have first wrapper-backed
  `Topography` adapters under `topomt.third_party.*`, intended for users who want
  upstream execution semantics without leaving the TopoMT object model;
- those wrapper adapters should remain clearly separated from
  `topomt.dfnd.*`, whose role is still the native TopoMT implementation.

Validation note:

- wrapper smoke/parity tests are required even after native parity exists;
- they validate the actual distributed binary/package route that users may run,
  not only the TopoMT-native reimplementation;
- and they can expose package/build/environment drift, as already happened in
  the broader `fpocket4` audit where wrapper-level behavior depended on which
  fpocket build was being exercised.

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

`topomt.third_party.fpocket._native_impl` is currently wrapper-backed.

It preserves fpocket semantics well for the validated systems, but it does so
through:

- the external `fpocket` binary;
- parsing of fpocket output files;
- and a wrapper-to-`Topography` adaptation layer.

This is useful and should remain available, but it is not the final target for
`topomt.third_party.fpocket._native_impl`.

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
[fpocket4/native_checkpoint.md](fpocket4/native_checkpoint.md).

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
- `topomt.delaunay_mesh` for the shared Delaunay substrate and its
  alpha-sphere-derived view where appropriate;
- `topomt.tools` for shared geometry and characterization support where it
  matches fpocket semantics;
- `pyunitwizard` for unit-normalized boundaries around the method.

### Cleanup after parity work

The native pocket methods should progressively express receptor preparation
through `molsysmt` selection/filtering helpers rather than through repeated
local purge pipelines.

Progress note:

- `fpocket4` now centralizes selected-receptor construction and atom-metadata
  extraction around shared `molsysmt` helpers;
- `pocketeer` and `castp` now also reuse a common heavy-receptor preparation
  helper instead of maintaining their own manual filtering code;
- `pycasta` now uses a dedicated `molsysmt` receptor-preparation path because
  its native contract should stay aligned with molecular selection semantics,
  not with upstream PDB-record (`ATOM/HETATM`) preprocessing quirks;
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

`topomt.third_party.alphaspace2.native` is now in an intermediate native-reimplementation
state.

The geometry and pocket-membership layers have already been reworked around the
shared `topomt.delaunay_mesh.DelaunayMesh` substrate and its alpha-sphere
derived view, and the current audited tests reach upstream parity for alpha
generation, pocket counts, and pocket atom ownership on the current reference
systems.

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

## `pycasta`

### Current state

`pycasta` is now a reviewed prioritized engine, but not yet an implemented
native method in TopoMT.

The current upstream material consists of:

- a public repository at <https://github.com/giorgioluciano/pycasta>;
- a local mirror at `/home/diego/repos@others/pycasta`;
- and the 2025 pyCAST paper at
  <https://doi.org/10.1016/j.csbj.2025.07.054>.

The important current reading is that the paper and the repository do not yet
look fully identical in the strongest methodological claims. The repository
appears to expose a simpler practical workflow than the paper text suggests.

### First validation target

The first TopoMT target should be parity against the effective public
repository workflow, because that is the auditable implementation we can run
and compare directly.

That first target should cover:

- receptor preparation;
- per-atom radii assignment;
- tetrahedralization;
- alpha-complex filtering;
- discrete-flow pocket grouping;
- cluster merging;
- pocket ranking and geometry;
- pocket atom ownership;
- and mouth/dual-set outputs where deterministic.

The stronger paper-level claims should remain a second audit question until we
know whether the missing pieces are:

- implemented elsewhere;
- omitted from the public repository;
- or only described conceptually in the paper.

### Upstream semantics that must be preserved first

The native reimplementation should reproduce at least the repository-observed
semantics of:

- Delaunay-based tetrahedral decomposition of the receptor;
- alpha-complex filtering by circumsphere-radius threshold;
- discrete flow over empty tetrahedra;
- sink-based grouping of tetrahedra into pockets;
- centroid-distance cluster merging;
- volume, depth, representative-point, and ranking calculations;
- mouth geometry and dual-set boundary derivation;
- and pocket atom mapping back to receptor atoms.

### What TopoMT should replace intentionally

The native `pycasta` path should use:

- `molsysmt` for structure loading, receptor/ligand selection, and atom-index
  mapping;
- `pyunitwizard` for all quantity normalization;
- TopoMT project-owned dependency handling and warnings infrastructure.

In particular:

- TopoMT should not depend on Biopandas for the native path;
- and SASA or ligand-validation helpers, when needed later, should be routed
  through `molsysmt`-compatible infrastructure rather than PyMOL-specific
  runtime assumptions.

### Open upstream-audit question

The current repository appears to differ from the paper in at least these
points:

- weighted Delaunay triangulation is described in the paper, but the current
  repository appears to fall back to standard SciPy Delaunay;
- alpha selection via persistent homology is described in the paper, but the
  current repository appears to use config-driven manual alpha values;
- and the public flow proxy appears to be circumsphere-radius-based rather
  than the exact wording used in the paper.

This should be tracked as an explicit audit question, not as an established
claim that the paper is wrong.

## Validation strategy

The validation path should differ from the runtime path.

### Runtime path

- `topomt.dfnd.*` uses only TopoMT and MolSysSuite dependencies.

### Validation path

- `topomt.third_party.*` or audit scripts can run upstream binaries or packages;
- parity tests compare native TopoMT outputs against those upstream references;
- failures should be interpreted as semantic gaps in the reimplementation, not
  as evidence that TopoMT should import the upstream code at runtime.

## Immediate next steps

1. Keep `fpocket4` documented as transitional while its provider structure is refined.
2. Start a native `fpocket4` plan around alpha-sphere generation and refine
   semantics.
3. Start a native `alphaspace2` plan around `genAlphas()` and exact lining
   atoms.
4. Formalize the initial `pycasta` native contract around repository parity
   before deciding whether a second paper-faithful mode or an upstream report
   is needed.
5. Extend tests so all prioritized native methods can be measured continuously
   against their upstream references.
