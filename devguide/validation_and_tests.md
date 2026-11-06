# Validation and tests

Validation distinguishes molecular-source integrity, original-provider fidelity,
TopoMT's own algorithms, consumer integration and installed-package delivery. A passing
selection proves its recorded inputs and assertions; it does not establish an unexecuted
provider, biological interpretation or platform matrix. Use [status](status.md), the
[provider handoff plan](provider_handoff_plan.md) and the owning issue to choose work
before expanding a test battery.

Routine local development uses Python **3.14**. The required source and installed matrix
covers Python **3.11–3.14**; qualification and public claims remain under
[#16](https://github.com/uibcdf/topomt/issues/16). The Python 3.13 docs workflow and old
checkpoint environments retain their own scope.

## Before the first test on a new machine

Follow [packaging and environments](packaging_and_environments.md), then verify the
interpreter that will run pytest:

~~~bash
python -c 'import sys; assert sys.version_info[:2] == (3, 14); print(sys.executable, sys.prefix)'
python -m pip check
python -c 'from importlib.metadata import version; print("pytest-receptor", version("pytest-receptor"))'
~~~

Verify editable import origins from outside the checkout as described there. If
reproducing a registered CI context, also execute its complete source acquisition and
`check_dependency_routes.py --context ...` check. The current working directory can
otherwise conceal a wrong installation.

Published Pytest Receptor reports local agent runs with `--receptor=llm` and hosted runs
with `--receptor=ci`. The main CI governance lane currently pins 1.2.0; other retained
lanes/environments can carry older explicit pins. Preserve a reproduction's actual
reporter version and outcome rather than treating those pins as interchangeable.

From the TopoMT root, a small initial selection exercises the reporting contract and
original-provider argument dispatch:

~~~bash
python -m pytest --receptor=llm \
  tests/test_reporting_protocol.py tests/test_provider_dispatch_arguments.py
~~~

This is an environment/contract starting point, not the complete scientific suite or a
guarantee that later tests will pass. Capture a fresh baseline before attributing an
existing failure to a new change.

## Test map

| Boundary | Starting locations | Interpretation |
| --- | --- | --- |
| `Topography`, registries and source context | [test_topography.py](../tests/test_topography.py), [test_topography_registry.py](../tests/test_topography_registry.py), [test_topography_input_context.py](../tests/test_topography_input_context.py) | Object, identity, selection/frame and source-context invariants |
| Original-provider dispatch and records | [test_provider_dispatch_arguments.py](../tests/test_provider_dispatch_arguments.py), [test_provider_output.py](../tests/test_provider_output.py), [test_provider_pocket_outputs.py](../tests/test_provider_pocket_outputs.py) | Admission, provenance, source indices, attributed measurements and available geometry |
| Original-provider adapters and saved readers | [tests/methods/](../tests/methods/) and [test_installed_engines.py](../tests/methods/test_installed_engines.py) | Selected real CLI/library/file execution and recovery, independently of native reproduction |
| Prepared public PharmacophoreMT receiving | `test_pharmacophore_handoff.py` in [fpocket4](../tests/methods/fpocket4/test_pharmacophore_handoff.py), [Pocketeer](../tests/methods/pocketeer/test_pharmacophore_handoff.py), [AlphaSpace2](../tests/methods/alphaspace2/test_pharmacophore_handoff.py) and [pyCASTA](../tests/methods/pycasta/test_pharmacophore_handoff.py) | Explicit source-bound query recipes and native model roundtrip; no affinity or binding-site admission |
| DFND and common geometry | `tests/test_dfnd_*.py`, [test_delaunay_mesh.py](../tests/test_delaunay_mesh.py), [test_weighted_delaunay_mesh.py](../tests/test_weighted_delaunay_mesh.py), `tests/test_tools_*.py` | Declared algorithmic/numerical contracts, pathological inputs and bounded real-system behavior |
| Native/upstream comparisons | Provider `test_parity.py` modules and dated native checkpoints | Bounded semantic comparison against the recorded original, separate from adapter fidelity |
| Viewer integration | [test_provider_output_viewer.py](../tests/test_provider_output_viewer.py), [test_molsysviewer_topomt_addon.py](../tests/test_molsysviewer_topomt_addon.py) | Data/conversion/addon contracts; headless checks do not establish live GUI behavior |
| Declarations, environments and distribution | [devtools/tests/](../devtools/tests/), [test_dependency_contract.py](../tests/test_dependency_contract.py), [test_reporting_protocol.py](../tests/test_reporting_protocol.py) | Administrative consistency, source/context rules and artifact resource checks |

Use actual filenames when selecting individual modules. For example, wrapper modules are
named `test_wrapper_pocketeer.py`, `test_wrapper_alphaspace2.py` and
`test_wrapper_pycasta.py`; no generic `test_wrapper.py` exists in those folders.

## Ordinary development checks

Write a failing regression or feature test first when changing executable behavior. Run
the relevant successful and invalid-input cases, then broaden only as the changed
boundary requires. Root instructions require the complete suite before a PR:

~~~bash
python -m pytest --receptor=llm tests/
~~~

`pytest.ini` adds doctest-module collection and quiet output. The shared
`tests/conftest.py` also supplies fixtures and a best-effort MolSysMT cache warmup. A
command using `--noconftest` is a different, explicitly bounded selection; it is not an
equivalent replacement for this full run.

For Python changes, run the repository's Ruff checks and applicable local type checks.
Select type-check targets around the changed API and record their scope; a small mypy
selection does not establish whole-repository typing.

~~~bash
ruff check .
ruff format --check .
~~~

Start a new host's scientific baseline serially. Parallel execution has a [documented
Numba/cache history](test_parallel_flakiness_2026_06_14.md); a warm cache or passing
controller hook does not excuse hiding a reproduced failure.

## Reporting and declaration checks

These commands use the clean administrative SDK described in the environment guide. They
inspect current declarations without running the scientific matrix:

~~~bash
python devtools/devguide_index.py --check
python devtools/check_dependency_routes.py --declared-only
python devtools/broadcast_requirements.py --check
python -m pytest --noconftest --receptor=llm \
  devtools/tests/test_distribution_contract.py tests/test_reporting_protocol.py
~~~

For all administrative guards, the main CI workflow additionally runs `python -m
unittest discover -s devtools/tests -p 'test_*.py'`. Read the selected tests'
prerequisites before using this broader operation as a local gate. Generated queue
indexes have their own lifecycle in [reporting_protocol.md](reporting_protocol.md). Do
not rewrite outcomes or archive a record solely because its selector is addressable.

## Optional engines and explicit receiving controls

The [external-engine guide](../docs/content/user/third_party_engines.md) owns
installation routes and method/backend selection. Missing originals do not select a
native substitute. Adapter/wrapper tests and native parity tests answer different
questions: a package, executable or input-conversion change can break original receiving
while a local numerical algorithm is unchanged.

Ordinary tests may skip an unavailable optional engine or upstream fixture. Record those
skips. Designated installed-engine gates must instead reject an absent, shadowed or
unexecuted original. Some native parity modules still use local upstream mirrors or
external datasets; inspect their fixture paths and record the exact reference revision
before rerunning them on another host.

Prepared consumer tests are opt-in. `TOPOMT_PREPARED_RECEPTOR` must identify the
checksum-qualified H5MSM seed from the provider checkpoints. fpocket additionally
requires `TOPOMT_FPOCKET_CMD` to identify the actual executable. Pocketeer,
AlphaSpace2 and pyCASTA prepared fixtures require their real, unshadowed installed original
distributions. With an explicit opt-in, wrong identities or seed hashes fail rather than
qualifying a skipped replacement.

The developer recorders `qualify_fpocket_handoff`, `qualify_pocketeer_handoff`,
`qualify_alphaspace2_handoff`, `qualify_pycasta_handoff` and
`qualify_pharmacophore_handoff` orchestrate public
owner tools. Their bounded source profiles and explicit query parameters are documented
in each provider checkpoint. They do not prepare missing chemistry, infer pharmacophoric
importance from pocket rank, expand lining membership to make recognition positive, or
certify an exact closed region. MolSysMT/PharmacophoreMT recognition failures remain
errors from their owners.

## Exact installed qualification

Execute an installed-candidate test from outside all source checkouts, with an approved
detached harness and verified runtime imports. Retain the actual wheel/package bytes and
digest, producer commit, generated metadata/version, resource inventory, dependency
inputs and before/after origin/file checks. A source overlay over an older installed
wheel is source evidence.

A receipt must retain its actual collected, executed, passed, failed and skipped cases.
Collection alone, a green administrative check, a source-only pilot or a narrow
installed selection does not establish the full required matrix. The [noarch
distribution route](../devtools/conda-build/README.md) defines the separate
candidate/publication gates. Original-provider checkpoints retain bounded receiving
evidence under #101; full source/backlog and qualification obligations retain
#16/#58/#81.

For GitHub Actions, use the [GH Run Receptor guide](../GH_RUN_RECEPTOR_GUIDE.md) and its
authoritative native fallback to confirm the actual jobs and test steps ran for the
relevant commit. A recovery probe's success is not scientific matrix execution. Keep
missing gates with their owning issue and recovery step.

## Documentation and scientific limits

After user-facing documentation changes, build HTML using the selected docs interpreter
and dependencies:

~~~bash
make -C docs html
~~~

The configured notebook execution mode is off; this command does not rerun all showcase
experiments. Inspect and record warnings, especially new broken links, rather than
treating a zero builder exit as a clean documentation result.

DFND engineering invariants, deterministic volume estimates and historical native
comparisons retain their stated numerical limits. They do not prove biological pocket
quality, superiority over another method, analytic volume precision, dynamic topology or
general provider equivalence. Current work priority comes from the maintained
status/plan and owner decision; this page does not resume paused native research.
