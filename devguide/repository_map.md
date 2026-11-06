# Repository map

Start with [the developer-guide index](index.md) for reading order and
[status](status.md) for current work. This map locates implementation, tests, policy and
evidence so a new developer can find the owning boundary before editing it.

## Runtime implementation

| Path | Responsibility |
| --- | --- |
| [topomt/__init__.py](../topomt/__init__.py) | Public package exports, version and ecosystem initialization |
| [topomt/get_provider_output.py](../topomt/get_provider_output.py) | High-level admission/dispatch for original external-provider results |
| [topomt/get_topography.py](../topomt/get_topography.py) | Public `Topography` construction/dispatch with its existing method contracts |
| [topomt/provider_output.py](../topomt/provider_output.py) and [topomt/third_party/output.py](../topomt/third_party/output.py) | Persisted original run evidence, attributed measurements and detached provider records |
| [topomt/topography/](../topomt/topography/) | `Topography` container, source binding and feature registries |
| [topomt/features/](../topomt/features/) | Feature objects such as pockets, mouths, channels and voids |
| [topomt/third_party/](../topomt/third_party/) | Provider-specific original library/CLI/service/file adapters and separately identified local implementations |
| [topomt/dfnd/](../topomt/dfnd/) | TopoMT's native DFND method and its declared numerical/model contracts |
| [topomt/tools/](../topomt/tools/) | Reusable TopoMT geometry, tessellation and feature-characterization tools |
| [topomt/delaunay_mesh.py](../topomt/delaunay_mesh.py) and [topomt/weighted_delaunay_mesh.py](../topomt/weighted_delaunay_mesh.py) | Delaunay substrates used by the corresponding method/tool routes |
| [topomt/io/](../topomt/io/) | Public external-result loading, including `load_CASTp` |
| [topomt/_private/](../topomt/_private/) | Internal argument digestion, diagnostics and other implementation support |
| [topomt/data/](../topomt/data/) and [topomt/demo.py](../topomt/demo.py) | Bundled reference inputs and demo lookup |
| [molsysviewer_topomt/](../molsysviewer_topomt/) | Separate lazy MolSysViewer addon package shipped with TopoMT |

Root ecosystem configuration includes `_argdigest.py`, `_depdigest.py`, `_smonitor.py`
and `_pyunitwizard.py`. Consult the corresponding synchronized consumer guide before
changing an integration. Their providers own argument contracts, optional-dependency
checks, diagnostic infrastructure and quantity conversion. Molecular
representation/preparation remains MolSysMT's domain; pharmacophore modeling remains
PharmacophoreMT's. The [architecture](architecture.md) and [suite
integration](integration_with_molsyssuite.md) explain these boundaries.

Original-provider records are not interchangeable with canonical DFND feature admission.
A native implementation beside an original adapter is a separate method contract; its
presence does not establish complete upstream equivalence. Use the [provider
architecture decision](third_party_architecture_adr.md), [common output
checkpoint](provider_pocket_output_checkpoint.md) and relevant provider contract when
modifying that boundary.

## Tests and developer tools

[tests/](../tests/) contains source/API tests, extensive DFND and shared-tool batteries,
provider-specific argument/adapter/parity/recovery tests and optional consumer/viewer
integration. [Validation and tests](validation_and_tests.md) provides entry points and
explains source versus installed qualification. Coverage and maturity vary by method and
tested boundary.

[devtools/](../devtools/) contains the current owner CLIs as well as historical helpers.
Its [README](../devtools/README.md) routes maintained environment and distribution
operations. The main current areas are:

- `devguide_index.py` and `devguide_reports.py`: report/index lifecycle checks.
- `check_dependency_routes.py`, `dependency_routes.toml`, `requirements/`: immutable
administrative SDK delegation and reviewed scientific source inputs.
- `environment_tools.toml`, `requirements.yaml`, `broadcast_requirements.py`,
`conda_env_manager.py` and `conda-envs/`: ordinary environment generation and explicit
manager operations, separate from specialized scientific contexts.
- `conda-build/`: package recipe, exact resource inventory and guarded distribution
plans; the example plan is not a real candidate selection.
- `provider_handoff.py`, `qualify_library_handoff.py`, `qualify_*_handoff.py`: developer
orchestration of public MolSysMT, TopoMT and PharmacophoreMT tools.
- `dfnd/`, `castp/` and `fpocket/`: targeted scientific/audit/profiling tools.
- `devtools/tests/`: administrative/distribution/environment-tool guards.

Inspect an older helper's maintained replacement before using it as a setup recipe. The
retired automatic environment-discovery options are documented in [the environment
guide](../devtools/conda-envs/README.md). The working MolSysSuite checkout and TopoMT's
pinned administrative `.molsyssuite` SDK serve different purposes; [packaging and
environments](packaging_and_environments.md) explains both.

## Documentation and evidence

[docs/](../docs/) is the Sphinx/MyST user-facing documentation, including API pages and
examples. [devguide/](.) is the working engineering guide: current status, architecture,
accepted contracts, issue-backed queues, dated decisions and scientific evidence.

Within `devguide/`:

| Location | How to use it |
| --- | --- |
| [index.md](index.md), [status.md](status.md), [roadmap.md](roadmap.md) | Entry points, current priorities and remaining work |
| [pending_bugs/](pending_bugs/README.md), [pending_proposals/](pending_proposals/README.md) | Active issue-backed work, with generated queue indexes |
| [archive/](archive/README.md) | Closed records retained for their resolution/history; not an active task queue |
| [provider_handoff_plan.md](provider_handoff_plan.md) | Current original-provider source-to-consumer direction and acceptance criteria |
| `fpocket4/`, `pocketeer/`, `alphaspace2/`, `pycasta/`, `castp/` | Provider overview, contracts, checkpoints and original-output inventories |
| Provider `evidence/` folders and CASTp `artifacts/` | Durable checksum-bearing experiment data and receipts |
| [DFND/](DFND/Overview.md) | DFND definitions, contracts, research plans, numerical limits and historical checkpoints |
| [reporting_protocol.md](reporting_protocol.md) and [templates/](templates/) | Required report lifecycle and starting template |

Read a provider's current overview before its dated checkpoints. Read archive indexes
for orientation and open an old record to answer a specific historical question.
Proposed research and historical numerical results do not become the current
implementation contract by appearing in the same directory.

Root `AGENTS.md`, `devguide/AGENTS.md` and the read-only synchronized
`MOLSYSSUITE_GUIDE.md` define working instructions and precedence. Root `*_GUIDE.md`
files belong to their named provider repositories; propose shared changes at the owner
and synchronize them through the registered route.

## Metadata and automation

[pyproject.toml](../pyproject.toml) owns package bounds, dependencies, extras and build
backend. [setup.cfg](../setup.cfg) retains coverage and legacy versioneer configuration.
[pytest.ini](../pytest.ini) owns default pytest/doctest selection;
[docs/conf.py](../docs/conf.py) owns the docs builder configuration.

[.github/workflows/](../.github/workflows/) defines source matrix, reporting, policy,
lint, optional-engine, documentation and distribution workflows. Workflow declarations,
exact executed runs and public delivery are separate facts. Follow [validation and
tests](validation_and_tests.md) when interpreting their evidence, and preserve the
original producer and artifact identities in any receiving report.
