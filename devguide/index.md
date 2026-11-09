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
| Public system laboratory | [Topography BenchLab](../docs/content/benchlab/index.md), [synthetic cases](../docs/content/benchlab/synthetic/index.md) and the [planned molecular collection](../docs/content/benchlab/molecular/index.md) |
| Discussions and scientific resources | [Maintenance instructions](discussions.md), [resource conversations](discussion_resources.md), [tools](external_tools_catalog.md) and [benchmarks](benchmark_catalog.md) |
| Comparative advantages and limitations | [Finding lifecycle, corrections and manuscript review](comparative_findings.md), [metadata register](comparative_findings.toml) and [card template](templates/comparative_finding.md) |
| Actions originating in Discussions | [Action-to-issue rule](discussions.md#every-future-action-has-an-owning-issue) and [dated complete-area routing audit](discussion_actions.md) |
| Public APIs and runtime models | [Architecture](architecture.md), [API surface](api_surface.md) and [repository map](repository_map.md) |
| Accepted Topography semantics and partial implementation | [Conceptual contract](topography_conceptual_contract.md), [implementation route](topography_implementation_route.md) and [input context](topography_input_context.md) |
| Component responsibilities and reusable operations | [MolSysSuite integration](integration_with_molsyssuite.md) and [operations owned by MolSysMT](what_should_move_to_molsysmt.md) |
| Original-provider records and consumer receiving | [Provider handoff plan](provider_handoff_plan.md), [output checkpoint](provider_pocket_output_checkpoint.md) and [external-tool catalogue](external_tools_catalog.md) |
| Original-provider expansion before BenchLab resumes | [Implementation sequence and admission gates](external_provider_expansion_plan.md), [completed source record](archive/expand_original_providers.md) |
| Individual providers | [fpocket](fpocket4/overview.md), [Pocketeer](pocketeer/overview.md), [AlphaSpace2](alphaspace2/overview.md), [pyCASTA](pycasta/overview.md) and [CASTp/CASTpFold](castp/overview.md) |
| New original local providers | [pyKVFinder](pykvfinder/overview.md), [GHECOM](ghecom/overview.md), [CAVER](caver/overview.md), [P2Rank](p2rank/overview.md), [MOLE](mole/overview.md), [four-engine source evidence](original_provider_expansion_checkpoint.md) and [MOLE source evidence](mole/source_checkpoint.md) |
| DFND science and unfinished admission gates | [Study and benchmark area](DFND/study_zone.md), [MOLE comparison](DFND/mole_comparison_2026_11_07.md), [core theoretical reconstruction](DFND/core_theory_review_2026_11_06.md), [development proposal](DFND/development_plan_2026_11_06.md), [review evidence](DFND/review_2026_11_06.md), [overview](DFND/Overview.md), [implementation status](DFND/implementation_status.md) and [feature catalogue](DFND/feature_catalog.md) |
| Proposed public DFND theory and method section | [Source-backed chapter plan, reading routes and authoring gates](DFND/documentation_section_plan.md), tracked under [#170](https://github.com/uibcdf/topomt/issues/170); public pages are not yet authored |
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
