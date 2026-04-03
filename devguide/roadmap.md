# TopoMT Roadmap

## Guiding principle

The project should first become reliable for the conventional engines and the
shared `Topography` API. Experimental directions should not define the whole
repository roadmap.

## Phase 1

Phase 1 was the initial integration of conventional algorithms under a unified
API.

The conceptual result of Phase 1 is valid:

- a shared `get_topography()` entry point;
- multiple engines behind a common interface;
- feature-oriented output through `Topography`.

## Phase 2

Current phase: stabilize the non-DFND core.

### Goals

- repair structural inconsistencies in feature and topography classes;
- normalize engine contracts;
- ensure reliable local-to-global atom-index mapping;
- improve test coverage for the prioritized engines;
- align units and dependency behavior with MolSysSuite.

### Recorded checkpoint

The `0.1.0` checkpoint is the first milestone where TopoMT reproduces the
direct fpocket binary output for the currently supported reference PDB systems.

For the validated systems, parity has been confirmed for:

- pocket count;
- pocket ranking and ids;
- atom membership per pocket;
- `Pocket Score`;
- `Drug Score`.

The current validated systems are:

- `1TCD.pdb`
- `1GG0.pdb`
- `1N57.pdb`
- `2GI9.pdb`
- `2H05.pdb`
- `3LKF.pdb`
- `E15ALA.pdb`

That original `0.1.0` wrapper-backed checkpoint should now be read as a
historical milestone rather than as the full current `fpocket4` state.

Since then:

- the native `fpocket4` path has reached exact final parity against the audited
  local fpocket source build on the full currently audited PDB set, including
  `1ATP.pdb`, `1CEN.pdb`, `1YCR.pdb`, and the large-system case `2HGR.pdb`;
- and wrapper-based parity claims are now known to depend on which fpocket
  binary/build is actually used.

### Scope

- `Topography`
- `Pocket`, `Mouth`, and related feature classes
- `pocketeer`
- `alphaspace2`
- `fpocket4`
- `pycasta`

### Non-goals

- DFND productionization
- advanced scoring models
- frontend-heavy visualization work

### Cross-cutting future note

In parallel with stabilization, TopoMT should keep a future-oriented record of
which pocket engines may later support:

- CPU-pool parallelization;
- distributed execution;
- GPU offloading.

This should be evaluated for:

- native implementations;
- wrapper-backed third-party engines;
- and future algorithms that enter the repository later.

This note is intentionally broader than `fpocket4`: `alphaspace2` and future
engines should also be reviewed under the same scalability lens.

See [engine_acceleration_plan.md](engine_acceleration_plan.md).

## Phase 3

Next phase after stabilization: reference-driven review of the prioritized
engines.

### Goals

- inspect the upstream or reference repositories for the selected tools;
- compare TopoMT behavior against those references;
- separate wrapper-backed integrations from native method targets;
- define native reimplementation plans for the prioritized methods;
- identify missing descriptors and missing tests;
- when a paper and the public repository diverge, document explicitly whether
  the first TopoMT target is repository parity, paper parity, or both in
  staged form;
- verify that `fpocket4` produces the same results from canonical `bcif.gz`
  inputs as from the corresponding original `pdb` inputs.

### Expected output

- a clearer split between `methods/` and `wrappers/`;
- native implementation plans for `fpocket4` and `alphaspace2`;
- a formalized native contract for `pycasta`, including the current audit of
  repository-versus-paper drift;
- a more faithful long-term integration layer;
- clearer documentation of engine-specific assumptions;
- stronger regression tests.

## Phase 4

MolSysViewer integration.

### Goals

- define a stable viewer-facing serialization for topographic features;
- implement the first version of `molsysviewer_topomt`;
- reuse existing MolSysViewer shapes for pocket surfaces and pocket blobs.

Current note:

- the `molsysviewer_topomt` package is now beyond scaffold level:
  it already provides addon registration, payload normalization, conservative
  pocket rendering through existing MolSysViewer shapes, selective pocket
  attachment helpers, and a first standalone-oriented helper layer for
  exporting or launching a MolSysViewer host with a pre-rendered TopoMT
  overlay;
- richer panel/workbench UI and tighter interactive scene operations are still
  pending.

### Constraint

The addon should come after the topographic data model is stable enough to be a
safe dependency.

## Postponed track

DFND remains a dedicated postponed track.

This track already has substantial design documentation under `devguide/DFND/`,
but it should not block the stabilization of the main non-DFND library path.

The current reference entry points for that track are:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md)
- [DFND/checkpoint.md](DFND/checkpoint.md)
