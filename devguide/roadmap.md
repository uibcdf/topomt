# TopoMT Roadmap

## Guiding Principle

TopoMT should converge toward a reliable native topography framework. External engines remain important references and integration targets, but the native method direction is now DFND.

## Phase 1: Unified API and Conventional Engine Integration

Phase 1 established the shared API direction:

- `get_topography()` as the main entry point;
- multiple engines behind a common interface;
- feature-oriented output through `Topography`;
- wrapper-backed and native paths for several external methods.

This phase is historically valid and remains part of the project foundation.

## Phase 2: DFND Hardening and Topography Integration

Current phase.

### Goals

- harden DFND as the native TopoMT method;
- keep conventional engines available as references, comparison targets, and wrappers;
- preserve clean `Topography` output for stable feature families;
- preserve full DFND raw records for method development and diagnostics;
- keep geometry, units, atom indices, and input policy explicit;
- improve performance enough for repeated probe-radius sweeps and larger systems.

### Current DFND State

DFND now has:

- active `DelaunayFlowNetwork` construction;
- build-once/query-many probe-radius workflows;
- tested `R_residence` and `R_gate` primitives;
- tested face identity and external-link tracing;
- tested access-by-residence domain classification;
- raw records for tetrahedra, faces, transit/concavity domains, residence regions, external links, dry components, dry interfaces, and dry motifs;
- `get_topography(method='dfnd')` integration;
- public compatibility features for voids, pockets, and multi-link domains;
- deterministic `volume_solvent_estimate` with unit tests;
- small real-system stability and monotonicity sweeps.

### Immediate Work

1. Profile and optimize residual query/build costs.
2. Inspect qualitative cavity behavior on the small systems already used for CASTp/CASTpFold work.
3. Decide reporting/filter policy for tiny voids and near-threshold domains.
4. Validate whether provisional families and dry motifs are useful enough for public exposure.
5. Expand real-system benchmarks without forcing strict parity with external engines.

## Phase 3: Validation and Benchmarking

Next phase after the current hardening pass.

### Goals

- build a stable small-system benchmark battery;
- compare DFND against CASTp/CASTpFold, fpocket/fpocket4, AlphaSpace2, Pocketeer, and pycasta;
- categorize differences as bugs, parameter effects, reporting/filter effects, or intended semantic differences;
- evaluate atom ownership, external links, domain counts, dominant-site localization, and volume estimates;
- establish performance envelopes and optional acceleration paths.

## Phase 4: Dynamic Topology

DFND's long-term differentiator is tracking topography through trajectories.

### Goals

- run DFND frame by frame on small trajectories;
- match domains/features across frames;
- report persistence, gate events, external-link changes, volume series, dry/wet transitions, and candidate dynamic pharmacophores.

## Phase 5: MolSysViewer Integration

MolSysViewer integration should become production-facing only after the topographic data model is stable enough.

Current note:

- the `molsysviewer_topomt` scaffold exists and has initial rendering/export helper work;
- richer panel/workbench UI and interactive scene operations remain pending.

## Conventional Engine Maintenance Track

The conventional engines remain maintained in parallel:

- keep wrapper-backed integrations working;
- keep native parity tests for audited reference sets;
- document upstream repository-versus-paper drift explicitly;
- keep CASTp work as reference material and historical algorithmic context, not as the active native-method target.
