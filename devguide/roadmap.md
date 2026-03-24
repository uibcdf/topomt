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

Current phase: stabilize the non-AFND core.

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

The following historical reference PDBs remain outside this checkpoint because
they currently fail upstream parsing in `molsysmt`:

- `1ATP.pdb`
- `1CEN.pdb`
- `1YCR.pdb`
- `2HGR.pdb`

### Scope

- `Topography`
- `Pocket`, `Mouth`, and related feature classes
- `pocketeer`
- `alphaspace2`
- `fpocket4`
- `pocket_geometry`
- `pycasta`

### Non-goals

- AFND productionization
- advanced scoring models
- frontend-heavy visualization work

## Phase 3

Next phase after stabilization: reference-driven review of the prioritized
engines.

### Goals

- inspect the upstream or reference repositories for the selected tools;
- compare TopoMT behavior against those references;
- refine wrappers and output semantics where needed;
- identify missing descriptors and missing tests.
- verify that `fpocket4` produces the same results from canonical `bcif.gz`
  inputs as from the corresponding original `pdb` inputs.

### Expected output

- a more faithful integration layer;
- clearer documentation of engine-specific assumptions;
- stronger regression tests.

## Phase 4

MolSysViewer integration.

### Goals

- define a stable viewer-facing serialization for topographic features;
- implement the first version of `molsysviewer_topomt`;
- reuse existing MolSysViewer shapes for pocket surfaces and pocket blobs.

### Constraint

The addon should come after the topographic data model is stable enough to be a
safe dependency.

## Postponed track

AFND remains a dedicated postponed track.

This track already has substantial design documentation under `devguide/AFND/`,
but it should not block the stabilization of the main non-AFND library path.

The current reference entry points for that track are:

- [AFND/Overview.md](AFND/Overview.md)
- [AFND/Technical_Design.md](AFND/Technical_Design.md)
- [AFND/checkpoint.md](AFND/checkpoint.md)
