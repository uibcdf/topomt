# Pending TopoMT Proposals

This directory holds open, issue-backed proposals that may change TopoMT.
Read [the reporting protocol](../reporting_protocol.md) and open the owning
GitHub issue before creating a record from
[`templates/report.md`](../templates/report.md).

## What Belongs Here

Use this directory for proposals concerning TopoMT or `molsysviewer_topomt` that
are not yet accepted contracts or executable backlog items, including:

- new scientific capabilities or algorithms;
- substantial API or object-model changes;
- cross-cutting refactors whose direction is not decided;
- performance strategies that require profiling or dependency decisions;
- exploratory integration designs.

Do not use this directory for:

- confirmed defects: add them to the active code-review backlog or issue tracker;
- accepted architecture: document it in the relevant authoritative `devguide/`
  contract;
- implementation checkpoints: place them with the relevant subsystem;
- broad option catalogs and plans: keep them outside the issue-backed queues
  until split into independently closable themes;
- improvements that belong in a sibling MolSysSuite repository: open the
  owning issue in that repository and follow its reporting protocol.

## Proposal Lifecycle

Every queued proposal has the common front matter, including its owning
`uibcdf/topomt#<number>` issue and an open status. The generated list below
is maintained with `python devtools/devguide_index.py`.

A pending proposal should state the problem, scientific or user value,
alternatives, risks, dependencies, validation plan, and decision questions. It
must not present unmeasured performance claims or speculative implementation
choices as established facts.

After evaluation, record the decision and its guard or normative rule, move
the report to `devguide/archive/`, regenerate indexes, and close the issue.
Archive every resolved, withdrawn, or superseded report; never delete one.

## Open reports

<!-- generated: devguide_index -->

### Active (7)

- [`dfnd_tube_all_atom_receiving.md`](dfnd_tube_all_atom_receiving.md) — [#181](https://github.com/uibcdf/topomt/issues/181) — Reconcile local tube candidates with independently empty all-atom carriers. *(active, measured)*
- [`dfnd_tube_boundary_budget.md`](dfnd_tube_boundary_budget.md) — [#180](https://github.com/uibcdf/topomt/issues/180) — Resolve bounded physical boundary receiving on the frozen straight tubes. *(active, measured)*
- [`integrate_hole.md`](integrate_hole.md) — [#192](https://github.com/uibcdf/topomt/issues/192) — Integrate original HOLE with source-bound results and scientific attribution. *(active, inspected)*
- [`integrate_pisa.md`](integrate_pisa.md) — [#194](https://github.com/uibcdf/topomt/issues/194) — Integrate original PISA with source-bound results and scientific attribution. *(active, inspected)*
- [`integrate_povme.md`](integrate_povme.md) — [#193](https://github.com/uibcdf/topomt/issues/193) — Integrate original POVME with source-bound results and scientific attribution. *(active, inspected)*
- [`review_python_ecosystem_policy_adoption.md`](review_python_ecosystem_policy_adoption.md) — [#56](https://github.com/uibcdf/topomt/issues/56) — Review TopoMT Python ecosystem policy adoption. *(active, measured)*
- [`wide_tube_boundary_numerics.md`](wide_tube_boundary_numerics.md) — [#184](https://github.com/uibcdf/topomt/issues/184) — Resolve wide-tube physical boundary ordering within the numerical margin. *(active, measured)*

### Partial (5)

- [`castp3_terminal_oxygen_policy.md`](castp3_terminal_oxygen_policy.md) — [#84](https://github.com/uibcdf/topomt/issues/84) — Determine terminal-oxygen radius and inclusion policy before extending the empirical CASTp profile. *(partial, measured)*
- [`dfnd_reference_validation_panel.md`](dfnd_reference_validation_panel.md) — [#76](https://github.com/uibcdf/topomt/issues/76) — Reconcile DFND synthetic reference assumptions and freeze independent validation evidence. *(partial, measured)*
- [`noarch_distribution_adoption.md`](noarch_distribution_adoption.md) — [#78](https://github.com/uibcdf/topomt/issues/78) — Adopt the distribution policy and a guarded single-file noarch publication route. *(partial, measured)*
- [`topography_context_and_support.md`](topography_context_and_support.md) — [#60](https://github.com/uibcdf/topomt/issues/60) — Adopt explicit Topography analysis context and spatial support. *(partial, measured)*
- [`track_python_matrix_evidence.md`](track_python_matrix_evidence.md) — [#16](https://github.com/uibcdf/topomt/issues/16) — Track TopoMT Python matrix evidence before a support or release claim. *(partial, measured)*

### Open (17)

- [`annotation_future_import_policy.md`](annotation_future_import_policy.md) — [#57](https://github.com/uibcdf/topomt/issues/57) — Decide TopoMT's future-annotation import rule for Python 3.11–3.13. *(open, inspected)*
- [`benchlab_six_case_review.md`](benchlab_six_case_review.md) — [#187](https://github.com/uibcdf/topomt/issues/187) — Review the six initial BenchLab units after establishing dumbbell. *(open, asserted)*
- [`castpfold_pending_jobs.md`](castpfold_pending_jobs.md) — [#168](https://github.com/uibcdf/topomt/issues/168) — Resolve the disposition of retained pending CASTpFold synthetic jobs without resubmitting. *(open, inspected)*
- [`caver_tetrahedron_applicability.md`](caver_tetrahedron_applicability.md) — [#155](https://github.com/uibcdf/topomt/issues/155) — Investigate the retained CAVER four-atom failure and supported input scope. *(open, inspected)*
- [`dfnd_component_count_diagnosis.md`](dfnd_component_count_diagnosis.md) — [#188](https://github.com/uibcdf/topomt/issues/188) — Review the historical dumbbell component-count monotonicity diagnosis. *(open, inspected)*
- [`docs_action_runtime_refresh.md`](docs_action_runtime_refresh.md) — [#177](https://github.com/uibcdf/topomt/issues/177) — Refresh deprecated Action runtimes in the documentation workflow at a grouped checkpoint. *(open, inspected)*
- [`dogsite_assessment.md`](dogsite_assessment.md) — [#160](https://github.com/uibcdf/topomt/issues/160) — Assess DoGSite3 service access and pocket/subpocket output semantics. *(open, inspected)*
- [`fpocket_family_review.md`](fpocket_family_review.md) — [#162](https://github.com/uibcdf/topomt/issues/162) — Assess fpocketR, Scipion fpocket and P2C scientific and workflow contributions. *(open, inspected)*
- [`grid_comparison_review.md`](grid_comparison_review.md) — [#158](https://github.com/uibcdf/topomt/issues/158) — Define eligible grid-based comparison questions for pyKVFinder, GHECOM and LIGSITE. *(open, inspected)*
- [`historical_tool_triage.md`](historical_tool_triage.md) — [#163](https://github.com/uibcdf/topomt/issues/163) — Qualify the identity and comparison scope of four historical tool candidates. *(open, inspected)*
- [`interface_reference_review.md`](interface_reference_review.md) — [#165](https://github.com/uibcdf/topomt/issues/165) — Assess PISA and PePrMint interface definitions and comparison eligibility. *(open, inspected)*
- [`mole_tetrahedron_applicability.md`](mole_tetrahedron_applicability.md) — [#156](https://github.com/uibcdf/topomt/issues/156) — Investigate the retained MOLE four-atom complex failure and input scope. *(open, inspected)*
- [`molecular_dataset_review.md`](molecular_dataset_review.md) — [#166](https://github.com/uibcdf/topomt/issues/166) — Qualify PocketPicker and COACH420 dataset provenance before molecular benchmark selection. *(open, inspected)*
- [`related_application_review.md`](related_application_review.md) — [#164](https://github.com/uibcdf/topomt/issues/164) — Assess topography API and user-workflow lessons from MolModa, Pocket2Mol and SurfDock. *(open, inspected)*
- [`specialist_pore_review.md`](specialist_pore_review.md) — [#161](https://github.com/uibcdf/topomt/issues/161) — Assess HOLE and CHAP as specialized pore-profile comparison references. *(open, inspected)*
- [`volume_reference_review.md`](volume_reference_review.md) — [#159](https://github.com/uibcdf/topomt/issues/159) — Assess POVME, MoloVol and PyVOL as scoped region and volume references. *(open, inspected)*
- [`zeopp_assessment.md`](zeopp_assessment.md) — [#167](https://github.com/uibcdf/topomt/issues/167) — Assess Zeo++ periodic accessibility definitions and source acquisition before comparison. *(open, inspected)*

<!-- /generated -->
