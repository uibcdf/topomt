# TopoMT Developer Guide

This directory collects the development-facing documentation for TopoMT.
Its purpose is to explain the current architecture, the real project status,
and the next engineering steps.

## Main documents

- [status.md](status.md)
  Current status of the project, including what is stable, what is in
  progress, and what is postponed.

- [architecture.md](architecture.md)
  High-level design of `Topography`, `Feature` objects, detection engines, and
  the expected internal contracts.

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

- [engine_acceleration_plan.md](engine_acceleration_plan.md)
  Cross-cutting future plan for CPU-pool parallelization, distributed
  execution, and GPU evaluation across pocket engines.

- [tools_architecture.md](tools_architecture.md)
  Proposed internal architecture for `topomt.tools`, including the separation
  between general geometry, tessellation-specific helpers, feature-oriented
  characterization, and lightweight visualization utilities.

- [fpocket4/scalable_options.md](fpocket4/scalable_options.md)
  Specific design options for a future `fpocket4`
  `implementation='topomt-scalable'` path.

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
  Scope note for the upcoming `pocketeer` parity implementation, linking to the upstream documentation and the local mirror repository.
- [pycasta/contract.md](pycasta/contract.md)
  Active contract for the upcoming native `pycasta` implementation, including
  the upstream repository, the paper source, and the current
  repository-versus-paper audit notes.
- [castp/contract.md](castp/contract.md)
  Contract for CASTp fidelity work, including the canonical `1.4 Å` probe
  default, the server-export oracle, and the requirements for future native
  parity.
- [CASTp/implementation.md](CASTp/implementation.md)
  From-scratch technical implementation plan for a faithful native CASTp path,
  explicitly separated from DFND semantics and from the current prototype.
- [proposal_improvement/](proposal_improvement/)
  Collected cross-repository improvement proposals for MolSysSuite sibling
  packages identified while implementing TopoMT.

- [native_methods_plan.md](native_methods_plan.md)
  Native reimplementation plan for the prioritized engines and the intended
  separation between `methods/` and `wrappers/`.

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

Cross-project improvement proposals are grouped separately from engine notes:

- [proposal_improvement/](proposal_improvement/)
  Draft proposals for `molsysmt`, `molsysviewer`, `smonitor`,
  `pyunitwizard`, `argdigest`, `depdigest`, and related sibling libraries.

## DFND

The DFND material is grouped under the dedicated `DFND/` subdirectory. The most useful entry point is `Overview.md`; the canonical abstract contract is `abstract_contract.md`:

- [DFND/Overview.md](DFND/Overview.md)
- [DFND/checkpoint.md](DFND/checkpoint.md)
- [DFND/implementation_status.md](DFND/implementation_status.md)
- [DFND/api_contract_v1.md](DFND/api_contract_v1.md)
- [DFND/Technical_Design.md](DFND/Technical_Design.md)
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
- [DFND/domain_motifs.md](DFND/domain_motifs.md)
- [DFND/dry_network_and_convexity.md](DFND/dry_network_and_convexity.md)
- [DFND/residence_transit_contract.md](DFND/residence_transit_contract.md)
- [DFND/numerical_policy.md](DFND/numerical_policy.md)
- [DFND/metrics_contract.md](DFND/metrics_contract.md)
- [DFND/input_policy.md](DFND/input_policy.md)
- [DFND/Implementation_Route.md](DFND/Implementation_Route.md)
- [DFND/object_model.md](DFND/object_model.md)
- [DFND/roadmap.md](DFND/roadmap.md)
- [DFND/synthetic_benchmarks.md](DFND/synthetic_benchmarks.md)
- [DFND/synthetic_review_guide.md](DFND/synthetic_review_guide.md)
- [DFND/pathological_systems.md](DFND/pathological_systems.md)
- [DFND/interfaces.md](DFND/interfaces.md)
- [DFND/dynamic_topology.md](DFND/dynamic_topology.md)
- [DFND/4D_and_pharmacophores.md](DFND/4D_and_pharmacophores.md)

DFND is the native TopoMT method direction and is now an active implementation-hardening track. It is not production-ready yet, but it has executable code, raw records, `Topography` integration, real-system smoke/monotonicity checks, and first dry-motif candidate records. The main `devguide/` should describe the whole project, not only DFND.

When DFND is mentioned from the main developer guide, it should normally be in
one of these roles:

- as the native TopoMT method direction;
- as an implementation-hardening track;
- as a source of richer domain and feature semantics for voids, surface concavities, pockets, channels, external links, derived mouths, dry networks, motifs, and dynamics.
