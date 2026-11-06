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
| Public APIs and runtime models | [Architecture](architecture.md), [API surface](api_surface.md) and [repository map](repository_map.md) |
| Accepted Topography semantics and partial implementation | [Conceptual contract](topography_conceptual_contract.md), [implementation route](topography_implementation_route.md) and [input context](topography_input_context.md) |
| Component responsibilities and reusable operations | [MolSysSuite integration](integration_with_molsyssuite.md) and [operations owned by MolSysMT](what_should_move_to_molsysmt.md) |
| Original-provider records and consumer receiving | [Provider handoff plan](provider_handoff_plan.md), [output checkpoint](provider_pocket_output_checkpoint.md) and [external-tool catalogue](external_tools_catalog.md) |
| Individual providers | [fpocket](fpocket4/overview.md), [Pocketeer](pocketeer/overview.md), [AlphaSpace2](alphaspace2/overview.md), [pyCASTA](pycasta/overview.md) and [CASTp/CASTpFold](castp/overview.md) |
| DFND science and unfinished admission gates | [DFND overview](DFND/Overview.md), [implementation status](DFND/implementation_status.md), [feature catalogue](DFND/feature_catalog.md) and [joint audit](DFND/audit_topography_2026_10_01.md) |
| Viewer boundary | [TopoMT addon checkpoint](molsysviewer_topomt_checkpoint.md) and [provider output viewer checkpoint](provider_output_viewer_checkpoint.md) |
| Tests, environments and package delivery | [Validation](validation_and_tests.md), [environments](packaging_and_environments.md) and [release titles](release_titles.md) |
| Detailed investigations and earlier decisions | [Reference catalogue](reference_catalog.md) |

## Work records

Use the [reporting protocol](reporting_protocol.md) and
[report template](templates/report.md) for issue-backed work. The generated
[bug queue](pending_bugs/README.md), [proposal queue](pending_proposals/README.md)
and [archive](archive/README.md) retain their separate lifecycle.

An old checkpoint's “next” action describes that checkpoint's stage. A passing
source test, an installed candidate and public delivery also have different
scopes. Read their dates, producers, inputs and limits before extending a claim
or resuming a scientific workstream.
