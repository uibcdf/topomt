# TopoMT Developer Guide

This directory collects the development-facing documentation for TopoMT.
Its purpose is to explain the current architecture, the real project status,
and the next engineering steps.

## Main documents

- [castp/checkpoint_2026_10_01_radius_coverage_and_void_panel.md](castp/checkpoint_2026_10_01_radius_coverage_and_void_panel.md)
  All 89 archived radius audits, twenty-system analytical void panel, corrected
  alternate-location identity and explicit OXT/1CGE follow-up limits.

- [castp/checkpoint_2026_10_01_castp3_radius_profile.md](castp/checkpoint_2026_10_01_castp3_radius_profile.md)
  Explicit modern-server radius profile, resolved closed-void residuals and
  thirteen-void/fifty-two-measure panel with independent sphere-center evidence.

- [castp/checkpoint_2026_10_01_modern_void_measurements.md](castp/checkpoint_2026_10_01_modern_void_measurements.md)
  Selected local CASTp reconstruction: historical algorithmic reference,
  pinned modern-result oracle, first closed-void SA/MS milestone and limits.

- [DFND/notebook_laboratory_checkpoint.md](DFND/notebook_laboratory_checkpoint.md)
  Active case-by-case scientific study route, public notebook/benchmark seed,
  first independent tetrahedron reference and original-provider input limits.

- [topography_input_context.md](topography_input_context.md)
  Delivered selected-frame input context under #60: MolSysMT recovery, shared
  protected quantities, original atom mapping, binding rejection and explicit
  legacy-source compatibility. Neutral spatial support remains pending.

- [DFND/checkpoint_geometry_snapshots_2026_10_01.md](DFND/checkpoint_geometry_snapshots_2026_10_01.md)
  Delivered native numeric ownership slice of #60, immutable shared geometry,
  input-change/reprobe guards and measured memory limits. Public context/support
  adoption remains partial.

- [DFND/audit_topography_2026_10_01.md](DFND/audit_topography_2026_10_01.md)
  Current joint DFND/Topography audit, reproduced integrity findings, scientific
  reference review and staged roadmap. DFND/Topography is the selected next
  workstream; the later selected CASTp slice is recorded above and broader
  provider implementation remains paused.

- [archive/topography_shallow_copy_indexes.md](archive/topography_shallow_copy_indexes.md)
  First delivered roadmap slice (#74): independent shallow-copy registry
  indexes and relations, failing-first regression evidence and the payload
  sharing boundary. Native snapshot/cache ownership and context/support (#60)
  remain the next slice.

- [external_tools_catalog.md](external_tools_catalog.md)
  Maintained external-tool catalogue, comparison/candidate watchlist and
  stewardship rule. Permanent provider overviews: [fpocket](fpocket4/overview.md),
  [Pocketeer](pocketeer/overview.md), [AlphaSpace2](alphaspace2/overview.md),
  [pyCASTA](pycasta/overview.md) and [CASTp/CASTpFold](castp/overview.md).

- [provider_pocket_output_checkpoint.md](provider_pocket_output_checkpoint.md)
  Delivered provider-specific outputs and shared pocket access; restart checkpoint
  for the paused broader provider work, independent of DFND consolidation.

- [provider_output_viewer_checkpoint.md](provider_output_viewer_checkpoint.md)
  Delivered original pocket outputs in the TopoMT-owned MolSysViewer addon;
  concrete DockingMT and PharmacophoreMT adoption remains deferred.

- [status.md](status.md)
  Current status of the project, including what is stable, what is in
  progress, and what is postponed.

- [architecture.md](architecture.md)
  High-level design of `Topography`, `Feature` objects, detection engines, and
  the expected internal contracts.

- [topography_conceptual_contract.md](topography_conceptual_contract.md)
  Normative public semantic direction grounded in DFND: spatial support,
  identity, classification, molecular participants, interfaces, contextual
  evaluations, provider admission and provenance. Runtime adoption is pending.

- [topography_implementation_route.md](topography_implementation_route.md)
  Pending public-model adoption gates and compatibility/scientific requirements,
  sequenced with the current joint audit.

- [roadmap.md](roadmap.md)
  Working roadmap for the current development cycle, including the outcome of
  the original phase-1 integration effort.

- [integration_with_molsyssuite.md](integration_with_molsyssuite.md)
  Contracts and expectations for integration with `molsysmt`,
  `pyunitwizard`, `argdigest`, `depdigest`, and `smonitor`.

- [what_should_move_to_molsysmt.md](what_should_move_to_molsysmt.md)
  Criteria and candidate primitives that should live in `molsysmt` rather
  than in TopoMT.

- [gpu_opportunities.md](gpu_opportunities.md)
  Notes on which parts of TopoMT and its ecosystem dependencies are plausible
  GPU targets and why.

- [gpu_and_parallelization_options.md](gpu_and_parallelization_options.md)
  Exploratory acceleration options awaiting measurements and separate decisions.

- [engine_acceleration_plan.md](engine_acceleration_plan.md)
  Cross-cutting future plan for CPU-pool parallelization, distributed
  execution, and GPU evaluation across pocket engines.

- [third_party_results_plan.md](third_party_results_plan.md)
  Active plan to preserve third-party results and reproduce provider
  measurements with traceable comparisons.

- [third_party_results_checkpoint.md](third_party_results_checkpoint.md)
  Paused-work restart sequence, weighted progress, accepted evidence, provider
  coverage, next gates, and the handoff to the later native-method review.

- [third_party_attribute_origins.md](third_party_attribute_origins.md)
  Register of application-specific feature attributes and the shared
  topographic concepts that keep neutral names.

- [tools_architecture.md](tools_architecture.md)
  Proposed internal architecture for `topomt.tools`, including the separation
  between general geometry, tessellation-specific helpers, feature-oriented
  characterization, and lightweight visualization utilities.

- [fpocket4/scalable_options.md](fpocket4/scalable_options.md)
  Specific design options for a future `fpocket4`
  `implementation='topomt-scalable'` path.

- [fpocket4/external_output_inventory.md](fpocket4/external_output_inventory.md)
  Field-level audit of original fpocket output, interpreted units, calculation
  status, and remaining integration gaps.

- [pocketeer/external_output_inventory.md](pocketeer/external_output_inventory.md)
  Field-level audit of Pocketeer's library result, mask snapshot, atom-index
  mapping, and remaining parity checks.

- [alphaspace2/external_output_inventory.md](alphaspace2/external_output_inventory.md)
  Field-level audit of AlphaSpace2's snapshot, pocket and beta descriptors,
  recoverable output, and remaining binder/scoring parity work.

- [pycasta/external_output_inventory.md](pycasta/external_output_inventory.md)
  Field-level audit of pyCASTA's library result, native files, PyUnitWizard
  quantities, and outstanding index-space and validation checks.

- [castp/external_output_inventory.md](castp/external_output_inventory.md)
  Field-level audit of CASTp/CASTpFold ZIP output, reported mouth aggregates,
  source links, and remaining unit and calculation work.

- [viewer_addon_plan.md](viewer_addon_plan.md)
  Initial plan for the future `molsysviewer_topomt` addon.

- [molsysviewer_topomt_checkpoint.md](molsysviewer_topomt_checkpoint.md)
  Checkpoint for the first real `molsysviewer_topomt` addon slice and the
  reasons for pausing the previous priority to start it now.

- [repository_map.md](repository_map.md)
  Practical map of the repository and the role of each major directory.

- [api_surface.md](api_surface.md)
  Description of the current public surface, legacy pieces, and experimental
  areas.

- [engine_references.md](engine_references.md)
  External repositories, binaries, packages, and validation targets used as
  reference points for the supported engines.
- [pocketeer_contract.md](pocketeer_contract.md)
  Scope note for the existing local `pocketeer` implementation and its later
  parity audit, linking to upstream documentation and the local mirror.
- [pycasta/contract.md](pycasta/contract.md)
  Contract for reviewing the existing native `pycasta` implementation, including
  the upstream repository, the paper source, and the current
  repository-versus-paper audit notes.
- [castp/contract.md](castp/contract.md)
  Contract for CASTp fidelity work, including the canonical `1.4 Å` probe
  default, the server-export oracle, and the requirements for future native
  parity.
- [CASTp/implementation.md](CASTp/implementation.md)
  From-scratch technical implementation plan for a faithful native CASTp path,
  explicitly separated from DFND semantics and from the current prototype.
- [pending_proposals/](pending_proposals/)
  Issue-backed proposals that may change TopoMT or
  `molsysviewer_topomt`.
- [reporting_protocol.md](reporting_protocol.md)
  Issue-backed defect and proposal lifecycle, local queue paths, and checks.
- [pending_bugs/](pending_bugs/)
  Open, issue-backed defects.
- [archive/](archive/)
  Permanent resolved, withdrawn, and superseded report records.

- [native_methods_plan.md](native_methods_plan.md)
  Existing local method inventory and the queued review of TopoMT-owned
  fpocket, CASTp, Pocketeer, pyCASTA, and AlphaSpace2 implementations after
  external-result integration.

- [fpocket4/native_checkpoint.md](fpocket4/native_checkpoint.md)
  Current detailed checkpoint for the native `fpocket4` diagnostic and parity
  work against upstream `fpocket`.

- [alphaspace2/native_checkpoint.md](alphaspace2/native_checkpoint.md)
  Current checkpoint for the native `alphaspace2` work and the remaining
  semantic layers needed for the `0.3.0` milestone.

- [pocket_algorithm_issues.md](pocket_algorithm_issues.md)
  Repository of known anomalies, ambiguity cases, residual non-parity issues,
  and other algorithmic problems detected while auditing pocket engines.

- [data_io_and_demos.md](data_io_and_demos.md)
  Notes on bundled data, demo systems, and external-result loaders.

- [validation_and_tests.md](validation_and_tests.md)
  Current test coverage, validation status, and testing priorities.

- [packaging_and_environments.md](packaging_and_environments.md)
  Current packaging state, dependency metadata, and development environments.

- [code_review_2026_06_06.md](code_review_2026_06_06.md)
  Consolidated review of `topomt` and `molsysviewer_topomt`, with confirmed
  defects, architectural risks, correction work packages, and acceptance
  criteria.

- [architecture_review_2026_06_06.md](architecture_review_2026_06_06.md)
  Scientific and software-architecture assessment of TopoMT, DFND, and
  `molsysviewer_topomt`, including strengths, conceptual tensions, target
  directions, and decisions required before structural refactoring.

## Engine directories

Engine-specific notes are now grouped in dedicated subdirectories when a topic
has multiple related checkpoint or contract documents:

- [fpocket4/](fpocket4/)
  Native checkpoint, parity matrix, scalable-path notes, and upstream
  correction drafts.
- [alphaspace2/](alphaspace2/)
  Native checkpoint, continuity notes, and method contract material.
- [pycasta/](pycasta/)
  Contract notes, benchmark inventory, and repository-versus-paper audit work.
- [castp/](castp/)
  Contract notes for CASTp fidelity, exported-file parity, and the native
  reimplementation target.
- [CASTp/](CASTp/)
  Technical implementation notes for rebuilding the native CASTp method from
  the classical discrete-flow workflow.

## Proposal directories

Proposal intake is separated by ownership:

- [pending_proposals/](pending_proposals/)
  Pending proposals whose implementation would change TopoMT or
  `molsysviewer_topomt`.
Requests owned by another MolSysSuite library must be written in that
repository's own issue tracker and developer-guide lifecycle.

## DFND

The DFND material is grouped under `DFND/`. Start with `Overview.md` and the
kernel/catalog decision; the public conceptual contract above defines new
Topography work. The abstract/API documents include earlier implementation
stages and must be read with their later checkpoints and the current catalog:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/taxonomy_architecture_decision.md](DFND/taxonomy_architecture_decision.md)
- [DFND/feature_catalog.md](DFND/feature_catalog.md)
- [DFND/checkpoint_pause_2026_06_25.md](DFND/checkpoint_pause_2026_06_25.md)
- [DFND/checkpoint.md](DFND/checkpoint.md)
- [DFND/implementation_status.md](DFND/implementation_status.md)
- [DFND/checkpoint_identity_provenance_registries_2026_06_06.md](DFND/checkpoint_identity_provenance_registries_2026_06_06.md)
- [DFND/checkpoint_canonical_transit_edges_2026_06_12.md](DFND/checkpoint_canonical_transit_edges_2026_06_12.md)
- [DFND/checkpoint_query_contract_2026_06_14.md](DFND/checkpoint_query_contract_2026_06_14.md)
- [DFND/checkpoint_atom_index_spaces_2026_06_14.md](DFND/checkpoint_atom_index_spaces_2026_06_14.md)
- [DFND/checkpoint_viewer_runtime_ownership_2026_06_14.md](DFND/checkpoint_viewer_runtime_ownership_2026_06_14.md)
- [DFND/checkpoint_render_result_contract_2026_06_14.md](DFND/checkpoint_render_result_contract_2026_06_14.md)
- [DFND/api_contract_v1.md](DFND/api_contract_v1.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md) — original design (historical)
- [DFND/Algorithm.md](DFND/Algorithm.md)
- [DFND/feature_definitions.md](DFND/feature_definitions.md)
- [DFND/abstract_contract.md](DFND/abstract_contract.md)
- [DFND/data_model_v1.md](DFND/data_model_v1.md)
- [DFND/toy_systems_v1.md](DFND/toy_systems_v1.md)
- [DFND/validation_plan.md](DFND/validation_plan.md)
- [DFND/residence_radius_audit.md](DFND/residence_radius_audit.md)
- [DFND/gate_radius_audit.md](DFND/gate_radius_audit.md)
- [DFND/known_limitations.md](DFND/known_limitations.md)
- [DFND/checkpoint_external_feedback_2026_05_20.md](DFND/checkpoint_external_feedback_2026_05_20.md)
- [DFND/checkpoint_real_system_stability.md](DFND/checkpoint_real_system_stability.md)
- [DFND/checkpoint_input_policy_hardening.md](DFND/checkpoint_input_policy_hardening.md)
- [DFND/checkpoint_face_identity_external_links.md](DFND/checkpoint_face_identity_external_links.md)
- [DFND/checkpoint_numerical_threshold_policy.md](DFND/checkpoint_numerical_threshold_policy.md)
- [DFND/checkpoint_dry_graph_basics.md](DFND/checkpoint_dry_graph_basics.md)
- [DFND/checkpoint_dry_interfaces_depth.md](DFND/checkpoint_dry_interfaces_depth.md)
- [DFND/checkpoint_probe_radius_sweep.md](DFND/checkpoint_probe_radius_sweep.md)
- [DFND/checkpoint_quality_snapshot.md](DFND/checkpoint_quality_snapshot.md)
- [DFND/checkpoint_dfnd_hardening_stint.md](DFND/checkpoint_dfnd_hardening_stint.md)
- [DFND/component_motifs.md](DFND/component_motifs.md)
- [DFND/dry_network_and_convexity.md](DFND/dry_network_and_convexity.md)
- [DFND/residence_transit_contract.md](DFND/residence_transit_contract.md)
- [DFND/numerical_policy.md](DFND/numerical_policy.md)
- [DFND/radius_convention_decision.md](DFND/radius_convention_decision.md)
- [DFND/metrics_contract.md](DFND/metrics_contract.md)
- [DFND/input_policy.md](DFND/input_policy.md)
- [DFND/Implementation_Route.md](DFND/Implementation_Route.md)
- [DFND/object_model.md](DFND/object_model.md)
- [DFND/component_visualization.md](DFND/component_visualization.md)
- [DFND/component_visualization_implementation.md](DFND/component_visualization_implementation.md)
- [DFND/roadmap.md](DFND/roadmap.md)
- [DFND/synthetic_benchmarks.md](DFND/synthetic_benchmarks.md)
- [DFND/synthetic_review_guide.md](DFND/synthetic_review_guide.md)
- [DFND/pathological_systems.md](DFND/pathological_systems.md)
- [DFND/interfaces.md](DFND/interfaces.md)
- [DFND/dynamic_topology.md](DFND/dynamic_topology.md)
- [DFND/4D_and_pharmacophores.md](DFND/4D_and_pharmacophores.md)

DFND is the native TopoMT method direction and is now an active
implementation-hardening track. It is not production-ready yet, but it has
executable code, deterministic static identity and contextual provenance, atomic
feature/component registries, `Topography` integration, real-system
smoke/monotonicity checks, and wet/dry motif records. Public dynamic-collection
policy, reporting policy, provisional refinements and biological validation
remain. Pairwise matching and track/event helpers already exist; their presence
does not close those public/scientific gates.
The main `devguide/` should describe the whole project, not only DFND.

When DFND is mentioned from the main developer guide, it should normally be in
one of these roles:

- as the native TopoMT method direction;
- as an implementation-hardening track;
- as the semantic reference for grounded regions, classification, accessibility,
  boundaries, interfaces and feature promotion.
