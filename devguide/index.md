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

- [fpocket4_scalable_options.md](fpocket4_scalable_options.md)
  Specific design options for a future `fpocket4`
  `implementation='topomt-scalable'` path.

- [viewer_addon_plan.md](viewer_addon_plan.md)
  Initial plan for the future `molsysviewer_topomt` addon.

- [repository_map.md](repository_map.md)
  Practical map of the repository and the role of each major directory.

- [api_surface.md](api_surface.md)
  Description of the current public surface, legacy pieces, and experimental
  areas.

- [engine_references.md](engine_references.md)
  External repositories, binaries, packages, and validation targets used as
  reference points for the supported engines.

- [native_methods_plan.md](native_methods_plan.md)
  Native reimplementation plan for the prioritized engines and the intended
  separation between `methods/` and `wrappers/`.

- [fpocket4_native_checkpoint.md](fpocket4_native_checkpoint.md)
  Current detailed checkpoint for the native `fpocket4` diagnostic and parity
  work against upstream `fpocket`.

- [pocket_algorithm_issues.md](pocket_algorithm_issues.md)
  Repository of known anomalies, ambiguity cases, residual non-parity issues,
  and other algorithmic problems detected while auditing pocket engines.

- [data_io_and_demos.md](data_io_and_demos.md)
  Notes on bundled data, demo systems, and external-result loaders.

- [validation_and_tests.md](validation_and_tests.md)
  Current test coverage, validation status, and testing priorities.

- [packaging_and_environments.md](packaging_and_environments.md)
  Current packaging state, dependency metadata, and development environments.

## AFND

The AFND material is intentionally kept in its own subdirectory:

- [AFND/Overview.md](AFND/Overview.md)
- [AFND/checkpoint.md](AFND/checkpoint.md)
- [AFND/Technical_Design.md](AFND/Technical_Design.md)
- [AFND/Algorithm.md](AFND/Algorithm.md)

AFND remains relevant, but it is not the current priority. The main
`devguide/` should describe the whole project, not only AFND.

When AFND is mentioned from the main developer guide, it should normally be in
one of these roles:

- as a postponed architecture track;
- as a documented experimental line of work;
- as a future source of richer feature semantics once the conventional path is
  stable.
