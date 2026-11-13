# TopoMT developer guide

Start here to join development or receive this checkout on another machine.
The guide separates current contracts and work from dated scientific evidence.
Repository code, manifests and executed receipts remain authoritative for their
respective boundaries.

## First reading

1. Read the [MolSysSuite guide](../MOLSYSSUITE_GUIDE.md),
   [repository instructions](../AGENTS.md) and
   [developer-guide instructions](AGENTS.md).
2. Read [onboarding](onboarding.md) for the architecture, ownership decisions
   and the history needed to interpret the current code.
3. Check [status](status.md) and [the roadmap](roadmap.md) before selecting work.
4. Establish [the development environment](packaging_and_environments.md) and
   follow [validation and tests](validation_and_tests.md).
5. For a machine transfer, follow [the migration handoff](migration_handoff.md)
   before relying on a fresh clone or old temporary artifact paths.

## Find the relevant contract

| Subject | Starting point |
| --- | --- |
| Joint six-case DFND review and next qualification work | [Public 19-profile disposition](../docs/content/benchlab/synthetic/six_case_review.md), [source capture and protocol](../docs/content/benchlab/synthetic/artifacts/six_case_review_v1/README.md) and [local/all-atom diagnosis #181](pending_proposals/dfnd_tube_all_atom_receiving.md); boundary #180/#184 and five-domain #188 remain open. |
| Independent connected-volume reference validator | [Current checkpoint](DFND/reference_validator_checkpoint.md), [physical hull Model, point/path proofs and ten-profile receiving](DFND/reference_validator_hull_sterics_checkpoint.md), [exact hull/clip controls and six-source receiving](DFND/reference_validator_hull_checkpoint.md), [one-ball P1 completeness](DFND/reference_validator_p1_feasibility.md), [analytic precision](DFND/reference_validator_precision_feasibility.md), [detailed plan](DFND/physical_reference_validator_implementation.md), [critical design](DFND/physical_reference_validator_plan.md) and [input/tool inventory](evidence/reference_validator_planning_inventory_v1.json), owned by [reference panel #76](pending_proposals/dfnd_reference_validation_panel.md). Certified-hull steric primitives and ten-profile saved receiving are delivered; general mixed regions/per-region precision remain pending. |
| Public system laboratory | [Topography BenchLab](../docs/content/benchlab/index.md), [synthetic cases](../docs/content/benchlab/synthetic/index.md), [planned molecular collection](../docs/content/benchlab/molecular/index.md), [three-case review / reader-route follow-up #175](archive/benchlab_three_case_reader_route.md) and [completed three-case execution](DFND/history/benchlab_improvement_plan_2026_11_10.md), [finite acceptance ledger](../docs/content/benchlab/synthetic/three_case_disposition.md) and [current laboratory checkpoint](DFND/notebook_laboratory_checkpoint.md) |
| Discussions and scientific resources | [Maintenance instructions](discussions.md), [resource conversations](discussion_resources.md), [tools](external_tools_catalog.md) and [benchmarks](benchmark_catalog.md) |
| Comparative advantages and limitations | [Finding lifecycle, corrections and manuscript review](comparative_findings.md), [metadata register](comparative_findings.toml) and [card template](templates/comparative_finding.md) |
| Actions originating in Discussions | [Action-to-issue rule](discussions.md#every-future-action-has-an-owning-issue) and [dated complete-area routing audit](discussion_actions.md) |
| Public APIs and runtime models | [Architecture](architecture.md), [API surface](api_surface.md) and [repository map](repository_map.md) |
| Accepted Topography semantics and partial implementation | [Conceptual contract](topography_conceptual_contract.md), [implementation route](topography_implementation_route.md) and [input context](topography_input_context.md) |
| Component responsibilities and reusable operations | [MolSysSuite integration](integration_with_molsyssuite.md) and [operations owned by MolSysMT](what_should_move_to_molsysmt.md) |
| Native binding-interface characterization proposal | [Complete catalogue and staged plan](binding_interface_native_catalogue_plan.md), [TopoMT review/handoff #197](pending_proposals/native_interface_catalogue_handoff.md), [BindingMT #112](https://github.com/uibcdf/bindingmt/issues/112) and [shared coordination #195](https://github.com/uibcdf/molsyssuite/issues/195); scientific ownership/adoption remain with the respective components. |
| Physicochemical characterization of topographic regions | [Dedicated proposal and staged plan #198](pending_proposals/topographic_physicochemistry.md), [existing pocket helpers](../topomt/tools/features/pockets/physicochemistry.py) and [historical chemistry overlay](DFND/chemistry_overlay_analysis.md); standalone TopoMT regional analysis complements binding-domain characterization. |
| Original-provider records and consumer receiving | [Provider handoff plan](provider_handoff_plan.md), [output checkpoint](provider_pocket_output_checkpoint.md) and [external-tool catalogue](external_tools_catalog.md) |
| Original-provider expansion before BenchLab resumes | [Implementation sequence and admission gates](external_provider_expansion_plan.md), [completed source record](archive/expand_original_providers.md) |
| MoloVol original local follow-up | [Source, build and execution overview](molovol/overview.md), [user guide](../docs/content/user/molovol.md), [resource #191](https://github.com/uibcdf/topomt/discussions/191) and implementation #190; broader assessment #159 remains separate |
| HOLE, POVME and PISA external adapters | [HOLE](hole/overview.md), [POVME](povme/overview.md), [PISA](pisa/overview.md) and [exact source/execution checkpoint](specialist_provider_checkpoint.md); integration owners #192/#193/#194. [PISA availability/licence review](pisa/license_review.md) keeps unresolved redistribution terms under #165. [POVME empty-initial-region review](pending_bugs/povme_empty_initial_roi.md) remains #195 / UIBCDF/POVME#1. Installed/public qualification is separate. |
| Individual providers | [fpocket](fpocket4/overview.md), [Pocketeer](pocketeer/overview.md), [AlphaSpace2](alphaspace2/overview.md), [pyCASTA](pycasta/overview.md) and [CASTp/CASTpFold](castp/overview.md) |
| New original local providers | [pyKVFinder](pykvfinder/overview.md), [GHECOM](ghecom/overview.md), [CAVER](caver/overview.md), [P2Rank](p2rank/overview.md), [MOLE](mole/overview.md), [four-engine source evidence](original_provider_expansion_checkpoint.md) and [MOLE source evidence](mole/source_checkpoint.md) |
| DFND science and unfinished admission gates | [Study and benchmark area](DFND/study_zone.md), [MOLE comparison](DFND/mole_comparison_2026_11_07.md), [core theoretical reconstruction](DFND/core_theory_review_2026_11_06.md), [development proposal](DFND/development_plan_2026_11_06.md), [review evidence](DFND/review_2026_11_06.md), [overview](DFND/Overview.md), [implementation status](DFND/implementation_status.md) and [feature catalogue](DFND/feature_catalog.md) |
| Public DFND theory and method | [Reader section](../docs/content/dfnd/index.md), [source/evidence checkpoint](DFND/documentation_checkpoint.md) and [retained proposal/review](DFND/documentation_section_plan.md); first delivery [#170](https://github.com/uibcdf/topomt/issues/170), reader/source refinement [#172](https://github.com/uibcdf/topomt/issues/172) |
| DFND approach and presentation audit — resolved | [Archived assessment and F1–F7 disposition](archive/dfnd_approach_and_presentation_audit_2026_11_09.md); [closed correction #173](archive/dfnd_method_book_semantics.md), separate scientific gates retained |
| Viewer boundary | [TopoMT addon checkpoint](molsysviewer_topomt_checkpoint.md) and [provider output viewer checkpoint](provider_output_viewer_checkpoint.md) |
| Tests, environments and package delivery | [Validation](validation_and_tests.md), [environments](packaging_and_environments.md) and [release titles](release_titles.md) |
| Detailed investigations and earlier decisions | [Reference catalogue](reference_catalog.md) |

## Work records

Scientific methods and provider additions follow the
[attribution inventory and maintenance procedure](attribution.md).

Use the [reporting protocol](reporting_protocol.md) and
[report template](templates/report.md) for issue-backed work. The generated
[bug queue](pending_bugs/README.md), [proposal queue](pending_proposals/README.md)
and [archive](archive/README.md) retain their separate lifecycle.

An old checkpoint's “next” action describes that checkpoint's stage. A passing
source test, an installed candidate and public delivery also have different
scopes. Read their dates, producers, inputs and limits before extending a claim
or resuming a scientific workstream.
