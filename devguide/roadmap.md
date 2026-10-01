# TopoMT Roadmap

## Guiding Principle

Latest scheduling decision (2026-10-01): proceed with
[case-by-case DFND notebook studies](DFND/notebook_laboratory_checkpoint.md).
The sequence is regular tetrahedron, independently reviewed closed shell,
opening, tube and two chambers with a neck. Public notebooks and reproducible
benchmark artifacts grow alongside scientific validation. This supersedes the
immediate public-support implementation sequence below; #60, #75 and #76 retain
their distinct unfinished gates. Historical provider-paused statements do not
describe the active scientific workstream.

TopoMT should converge toward a reliable native topography framework. External engines remain important references and integration targets, but the native method direction is now DFND.

Current scheduling decision (2026-10-01): joint DFND/Topography work is resumed,
starting with [the audit and staged roadmap](DFND/audit_topography_2026_10_01.md).
Initial provider/viewer delivery is complete. Broader provider fidelity,
additional engines and concrete DockingMT/PharmacophoreMT adoption remain paused
or deferred. The dated September sequence below is historical; no DFND runtime
or scientific gate is completed by this planning update.

Implementation progress (2026-10-01): the bounded
[Topography shallow-copy correction](archive/topography_shallow_copy_indexes.md)
(#74) is delivered with regression tests. The next stage-0 slice is native
snapshot/cache ownership under #60, followed by its public context/support
contract. Independent synthetic/reference validation (#76) and numerical
precision (#75) retain their separate acceptance criteria.

Subsequent progress: the [native numeric snapshot slice](DFND/checkpoint_geometry_snapshots_2026_10_01.md)
of #60 is delivered with shared protected geometry, regression guards and memory
measurements. The next slice is source/frame recovery and public context/support
and mutation adoption. #60 remains partial.

Subsequent progress: [selected-frame context recovery](topography_input_context.md)
and source-rebinding guards are delivered. Next: neutral spatial support for
one DFND concavity/Mouth and an incomplete provider, remaining public mutation
migration, and method/source occurrence provenance. Input context alone does not
complete #60 or certify numerical/scientific precision.

Current scheduling decision (2026-09-30): deliver usable original-provider
pockets first through provider-specific provisional outputs and shared consumer
access. See the [current checkpoint](provider_pocket_output_checkpoint.md), #65.
The current adoption slice is [the MolSysViewer addon](provider_output_viewer_checkpoint.md),
#66. DFND consolidation, full Topography runtime gates and concrete DockingMT/
PharmacophoreMT adoption remain deferred. The phases below retain their long-term
architectural direction.

The user has requested a pause after this initial provider/viewer delivery.
Immediate work below is a future resume sequence, not an active instruction.

## Phase 1: Unified API and Conventional Engine Integration

Phase 1 established the shared API direction:

- `get_topography()` as the main entry point;
- multiple engines behind a common interface;
- feature-oriented output through `Topography`;
- wrapper-backed and native paths for several external methods.

This phase is historically valid and remains part of the project foundation.

## Phase 2: DFND Hardening and Topography Integration

Deferred native phase; original-provider pocket delivery currently has priority.

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
- deterministic component, external-link, and motif support/context keys;
- contextual provenance across raw records, typed relations, and promoted features;
- canonical transit edges derived directly from shared-face permeability;
- typed immutable mesh/query configuration with complete re-probing and explicit
  reporting separation;
- explicit and tested mesh-local versus molecular-system atom-index boundaries;
- complete-source viewer runtime ownership with separate feature filters and
  render groups;
- common primary-render `RenderResult` and exact repeated-render lifecycle;
- atomic feature and component registries;
- tested access-by-residence component classification;
- raw records for tetrahedra, faces, wet components, residence regions, external links, dry components, dry interfaces, and dry motifs;
- `get_topography(method='dfnd')` integration;
- public features for stable void, pocket, and channel component families;
- deterministic `volume_solvent_estimate` with unit tests;
- small real-system stability and monotonicity sweeps.

### Immediate Work

Provider outputs in #65 are implemented. Adopt them in the MolSysViewer addon
under #66, then continue original field/route fidelity gates. Broader DFND viewer
geometry work and DFND reporting/filter policy remain deferred. Original results become comparison
inputs without forcing methods with different definitions into strict parity.

The completed static-identity/provenance milestone is recorded in
[`DFND/checkpoint_identity_provenance_registries_2026_06_06.md`](DFND/checkpoint_identity_provenance_registries_2026_06_06.md).

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

### Decision Gate

Before implementation, decide matching evidence and thresholds, confidence
policy, split/merge semantics, and lineage event contracts. Exact contextual
keys are evidence for matching, not temporal identity.

### Goals

- run DFND frame by frame on small trajectories;
- match components/features across frames into unbranched `track_id` segments;
- represent births, deaths, splits, and merges in a lineage graph;
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
