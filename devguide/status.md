# TopoMT Status

## Summary

TopoMT is in an active implementation-hardening stage.

The project already contains:

- a coherent `Topography`/`Feature` object model;
- a public orchestrator, `get_topography()`;
- several conventional engine integrations and wrapper-backed routes;
- shared geometry, tessellation, and feature-characterization utilities under `topomt.tools`;
- an active `DelaunayMesh` substrate used by several native paths;
- a native DFND implementation that is now executable, tested at the substrate/API level, and documented through focused checkpoints.

The project is not yet a polished stable product. The main remaining gap is not lack of direction; it is validation depth, performance hardening, and deciding which experimental records become public feature APIs.

## Current Priority

The current selected implementation slice is local CASTp3 closed-void SA/MS
validation under #79. The
[modern CASTp checkpoint](castp/checkpoint_2026_10_01_modern_void_measurements.md)
records exact lining-atom and sixteen-measure agreement for 2PK4, explicit
unit-bearing delivery and the remaining open-pocket/mouth roadmap. Historical
code is an algorithmic reference; pinned modern outputs are the result oracle.
DFND remains the native method, and its two-case notebook laboratory is paused.

The DFND scientific workstream is the
[DFND notebook laboratory](DFND/notebook_laboratory_checkpoint.md): learn and
validate native residence/transit behavior case by case, starting from frozen
synthetic inputs and independent references. The notebooks seed the future
public documentation/benchmark annex. The regular-tetrahedron and sampled
closed-shell cases include original-provider comparisons. The user requested a
pause at this two-case checkpoint; further cases and kernel changes await a later
resume. #76 remains open for the broader
reference panel and #75 for numerical volume precision. Remaining #60 public
support work is pending rather than a prerequisite for these studies.

On 2026-10-01 the user selected joint DFND/Topography work, starting with
[the audit, assessment and staged roadmap](DFND/audit_topography_2026_10_01.md).
The audited local selector passed 312 tests with two skips; additional probes
reproduced shallow-copy index corruption (#74), mutable native-cache ownership
risks (#60) and overstated numerical certainty (#75). Independent reference
validation is tracked in #76. The bounded
[copy correction](archive/topography_shallow_copy_indexes.md) (#74) is now
implemented with failing-first regressions for all five registry operations in
both directions. The next implementation slice is #60's ownership/context/support
contract. Its [native numeric snapshot slice](DFND/checkpoint_geometry_snapshots_2026_10_01.md)
is now delivered: mutable input arrays cannot change historical cached geometry,
native arrays are protected and probes share buffers. Public mutation and
source/context/support gates remain open.

Subsequent progress: [selected-frame input contexts](topography_input_context.md)
now retain recoverable selected MolSysMT topology and structural metadata,
protected quantities and explicit source mappings. Native diagnostics and
`Topography.show()` use this evidence; populated/analysed source rebinding is
rejected. Neutral support, provider context adoption and remaining public
mutation paths keep #60 partial. The original-input compatibility reference can
remain live and is distinct from historical recovery.

Initial [provider pocket delivery](provider_pocket_output_checkpoint.md) (#65)
and [MolSysViewer adoption](provider_output_viewer_checkpoint.md) (#66) are
implemented. Their provisional contracts remain usable while broader provider
implementation is paused. Runtime public-model gates are still open.

The broader [third-party results checkpoint](third_party_results_checkpoint.md)
remains 20/100 verified, with exhaustive fidelity incomplete. Its later local
provider-method audit follows its separate parity gate. Initial consumer adoption
is retained in #66.
Concrete DockingMT and PharmacophoreMT adoption remains deferred.

DFND is the native TopoMT method direction. It should not be forced into strict CASTp, fpocket, AlphaSpace2, Pocketeer, or pycasta parity. Those methods remain valuable as external references, loader or wrapper integrations, and qualitative/quantitative comparison baselines.

The DFND backlog is:

- apply the completed typed mesh/query contract to validation, reporting, and
  future temporal-comparability workflows;
- keep the raw data model traceable and `get_topography(method='dfnd')`
  integrated with `Topography`;
- validate wet/dry components, links, motifs, metrics, and qualitative behavior
  on controlled and real systems;
- add reporting/filter policy before judging cavity quality;
- profile and optimize query/build performance for larger systems.

## What Is Currently Solid

- `get_topography()` routes DFND and the conventional engines through the same top-level API.
- `DelaunayMesh` is the shared geometric substrate for Delaunay/tetrahedral work.
- DFND now has active geometry, graph-contract, input-policy, Topography, solvent-volume, and real-system stability tests.
- DFND supports the build-once/query-many workflow through `DelaunayFlowNetwork`.
- Static component, external-link, and motif identity is deterministic and
  separates local labels, exact support, and contextual provenance.
- Face permeability and wet-graph traversability use one canonical transit-edge
  decision, with explicit physical and effective gate margins.
- Frozen `DFNDMeshConfig` and `DFNDQuery` objects define substrate/query
  provenance, complete re-probing, and reporting-independent result identity.
- DFND diagnostics and the TopoMT viewer addon enforce explicit `mesh_local`
  versus `molecular_system` atom-index boundaries.
- The viewer runtime retains one complete source topography and manages feature
  filters and render groups separately.
- Primary viewer renderers return a common `RenderResult` and every component
  representation supports clean repeated rendering.
- Full-graph and component-graph nodes share one viewer-neutral tetrahedron centre extractor with explicit units and structured identity.
- Standalone selected-feature rendering emits the requested filtered operations, and addon context actions use executable entries without no-op click callbacks.
- `Topography` and DFND `Components` registries have validated mutation and
  registered-ID protection. Topography shallow copies now own independent index
  and relation sets (#74). Native input/cache arrays are protected under #60;
  other public mutation paths and full context/support adoption remain partial.
- `R_residence` and `R_gate` are implemented as clearance primitives with active tests.
- DFND raw records separate topological/debug volumes from `volume_solvent_estimate`.
- DFND promotes void/pocket/channel, percolating regions and provisional
  open-concavity/groove/cleft classifications, with Mouth children where applicable.
  Remaining raw evidence is available through `topography.dfnd`.
- Dry-side records now include dry components, dry edges, dry interfaces, face depth, and first candidate dry motifs.
- Probe-radius sweeps on five small real systems obey the expected monotonicity invariants.

Key DFND checkpoints:

- [DFND/implementation_status.md](DFND/implementation_status.md)
- [DFND/checkpoint_atom_index_spaces_2026_06_14.md](DFND/checkpoint_atom_index_spaces_2026_06_14.md)
- [DFND/checkpoint_viewer_runtime_ownership_2026_06_14.md](DFND/checkpoint_viewer_runtime_ownership_2026_06_14.md)
- [DFND/checkpoint_render_result_contract_2026_06_14.md](DFND/checkpoint_render_result_contract_2026_06_14.md)
- [DFND/checkpoint_viewer_geometry_boundary_2026_06_14.md](DFND/checkpoint_viewer_geometry_boundary_2026_06_14.md)
- [DFND/checkpoint_identity_provenance_registries_2026_06_06.md](DFND/checkpoint_identity_provenance_registries_2026_06_06.md)
- [DFND/checkpoint_dfnd_hardening_stint.md](DFND/checkpoint_dfnd_hardening_stint.md)
- [DFND/checkpoint_probe_radius_sweep.md](DFND/checkpoint_probe_radius_sweep.md)
- [DFND/checkpoint_quality_snapshot.md](DFND/checkpoint_quality_snapshot.md)
- [DFND/checkpoint_dry_interfaces_depth.md](DFND/checkpoint_dry_interfaces_depth.md)
- [DFND/checkpoint_dry_graph_basics.md](DFND/checkpoint_dry_graph_basics.md)
- [DFND/checkpoint_face_identity_external_links.md](DFND/checkpoint_face_identity_external_links.md)
- [DFND/checkpoint_numerical_threshold_policy.md](DFND/checkpoint_numerical_threshold_policy.md)
- [DFND/residence_radius_audit.md](DFND/residence_radius_audit.md)
- [DFND/gate_radius_audit.md](DFND/gate_radius_audit.md)

## Conventional Engine Status

The conventional engines remain important, but they are no longer the only active focus.

- `fpocket4` has strong native/source parity evidence on the audited set, with remaining source-level questions concentrated in raw geometry and build drift rather than final output for the audited local source build.
- `alphaspace2` has native parity coverage for the currently audited reference behavior and a first Vina-aware/contact layer.
- `pocketeer` has a native parity route and wrapper-backed Topography integration.
- `pycasta` has a local algorithm and bounded parity tests, with explicit repository-versus-paper and selection-semantics questions documented. Its native `Topography` adapter currently assigns volume as score; the later audit must compare it with the distinct upstream ranking score. `1a6w` currently fails native pocket-count parity ([#53](https://github.com/uibcdf/topomt/issues/53)).
- CASTp server/file integration is active in the external-result workstream. Strict parity of TopoMT's local CASTp3 algorithm is deferred to the later native review; the existing CASTp prototypes remain reference material for DFND.

## What Is Still Weak

- Public user-facing documentation is still sparse.
- Packaging metadata and release-quality checks remain incomplete.
- Performance is acceptable for small systems but still needs profiling and optimization for larger repeated workflows.
- `volume_solvent_estimate` is deterministic and tested, but it is still an estimator, not a publication-grade CASTp-like analytic volume.
- Tiny void/domain reporting policy is not settled.
- Surface-concavity, nonresident-passage, and dry motif utility must be validated before becoming public feature families.
- Pairwise matching and multi-frame track/event helpers exist. Public dynamic
  collection ownership, compatible-input checks, matching confidence and
  scientific lineage validation remain pending.
- Cross-engine benchmarks are not yet organized into a stable comparison battery.

## Practical Development Rule

Build new topography work on `get_topography()`, `Topography`, `DelaunayMesh`, `topomt.tools`, and DFND raw records. Keep experimental/provisional DFND records traceable, but do not promote them to stable public feature classes until validation supports that decision.
