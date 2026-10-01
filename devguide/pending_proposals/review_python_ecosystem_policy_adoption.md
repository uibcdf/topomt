---
summary: Review TopoMT Python ecosystem policy adoption.
issue: uibcdf/topomt#56
status: active
opened: 2026-09-27
closed:
verification: measured
area: [governance, tooling]
guard:
normative:
blocked_by: []
supersedes: []
---

# Review Python ecosystem policy adoption

**Reported:** 2026-09-27. Inspected `origin/main` at
`015cb48001e947301b6eb42e8174d17aa7acb1b2` under the MolSysSuite
Python ecosystem policy.

## What

Support-library adoption is **partial**; developer-tool adoption is
**adopted** for the inspected CI and run-inspection routes. This review is
independent of TopoMT's Python-support matrix work in `uibcdf/topomt#16`.

## How

The package declares ArgDigest, DepDigest, SMonitor, and PyUnitWizard as
runtime dependencies. `get_topography()` uses argument digestion and
structured signals; quantity paths use PyUnitWizard. `_pyunitwizard.py`
initializes shared defaults only if no policy is active. DepDigest has a
configuration and optional runtime decorators. However, SMonitor's catalog
still fails to render authored diagnostics under `uibcdf/topomt#15`, and
the AlphaSpace2 optional backend has a boundary that warrants review before
claiming full DepDigest adoption. Keep these component implementation matters
in their member issues and add focused tests when addressed.

Both maintained test Conda environments pin published Pytest Receptor `0.6.0`.
`.github/workflows/CI.yaml` selects `--receptor=ci` without changing test
selection or coverage options. Published GH Run Receptor `1.0.0` inspected
exact-source CI `36311638015`, policy `36311638223`, and Ruff `36311638009`.
The policy and Ruff runs passed; the CI test matrix failed six of six jobs
with `ModuleNotFoundError: alphaspace2` in the test step, which the receptor
reported as failure. This does not make the tool adoption claim false; it
does mean the matrix is not passing release evidence.

Commands for the hosted inspection:

```bash
gh run-receptor inspect 36311638015 --repo uibcdf/topomt --receptor=llm
gh run-receptor inspect 36311638223 --repo uibcdf/topomt --receptor=llm
gh run-receptor inspect 36311638009 --repo uibcdf/topomt --receptor=llm
```

## Why

The central `pending` entries signified that no member-specific review had
been recorded. They did not prove absence of the support libraries or tools.
Separate states keep a known SMonitor defect and optional dependency review
visible while recognizing verified tool use.

## What was refuted

The old `uibcdf/topomt#16` checklist said Ruff used only selected critical
rules and that CI omitted ArgDigest. Current Ruff runs `ruff check .` and
`ruff format --check .`; CI installs exact controlled source dependencies,
including ArgDigest. The remaining CI failure is not evidence that those
governance paths are missing.

## Scope and exclusions

This report owns TopoMT's library and developer-tool applicability review.
Scientific AlphaSpace2 behavior and the SMonitor catalog repair remain local
implementation work. A green full matrix is not claimed here.

## Acceptance criteria

Resolve or bound the SMonitor catalog defect and optional dependency gaps,
verify representative public boundaries, and refresh the central inventory
from exact-source evidence before upgrading support libraries to `adopted`.
Keep developer-tool evidence current if CI environments or run inspection
change.

## Component evidence update: 2026-09-30

Commits `989b46d` and `162038a` repair catalog registration/message-first
diagnostics and the optional original-engine boundaries. The engine adapters
support installed Pocketeer, AlphaSpace2 and isolated pyCASTA scripts; collection
without original engines or MDTraj has explicit regression coverage. The source
selection passed 61 tests, three installed-distribution comparisons and eleven
fpocket 4.2.3 direct-CLI comparisons passed separately, and 29 consumer tests
passed against the DepDigest extension. After integrating remote governance
through `3e67fcb`, 36 import/reporting/dependency/warning tests passed; complete
Ruff lint/format, scoped mypy and generated indexes passed.

DepDigest's executable/installer-route extension is on `main` in `08f8263` and
`457e72a`, tracked by `uibcdf/depdigest#22`; publication as an installable release
and coordinated guide/consumer adoption remain under `uibcdf/molsyssuite#62`.
The full pre-merge local suite had 771 passed, 74 failed, 25 skipped and five
xfailed. One failure is native pyCASTA issue #53 and 73 are viewer-addon
compatibility failures; representatives of every viewer failure group also
fail with unchanged TopoMT HEAD. Support-library adoption remains partial until
the shared release/adoption and public-boundary evidence are reviewed; this
update does not assert a passing hosted Python matrix.

## Published-provider migration: 2026-10-01

The fpocket boundary now delegates command availability to DepDigest 0.12.0,
whose immutable release candidate is
`0da46d9ff31fbe2f92e4e667a32868aebe840b39`. `_depdigest.py` declares fpocket as
a soft executable with its Conda-forge route and no pip route. The guard checks
the supplied `fpocket_cmd`; custom commands do not require the default command.
A private absence sentinel translates only provider-confirmed absence into the
established public `FpocketError` and `ExecutableNotFoundError` code. Provider
internal import errors and filesystem/execution failures preserve their identity;
the original subprocess arguments, working directory and output checks remain.
Local discovery and the broad missing-file classification have been retired.

`pyproject.toml`, the canonical `devtools/requirements.yaml`, generated environment
surfaces and Conda recipe require DepDigest >=0.12.0. Production manifests also
include the already declared hard dependency closure. The controlled DepDigest
pin identifies that same released commit; all other suite pins, the MolSysMT pin,
the supported Python range, specialized scientific packages and receptor pins
are preserved. The legacy broadcasting script would overwrite specialized
profiles, so only the required entries were merged into those existing profiles.
Bootstrap-only setup/build environments acquire no runtime dependency.

Six focused tests in `tests/test_fpocket_availability_contract.py` cover truthful
configuration, absent/custom commands, public exception reconstruction, native
working-directory failures, execution failure causes and provider import errors.
Before implementation the original five-test selection had three failures;
the final six pass against the actual staged 0.12.0 artifact with public SMonitor
0.17.3 on Linux/Python 3.13.15. Its version, off-checkout import origin, exact
staging URL and SHA-256 were checked independently. Seven administrative tests
also pass, full Ruff lint/format over 383 files passes, and scoped mypy passes
for the two changed runtime modules. The initial mypy run caught heterogeneous
dictionary inference; the configuration now declares its actual value types.

The manual `optional_engine_contract.yaml` workflow tests this same six-test
boundary against the exact public artifact on Linux/macOS and all three supported
Python minors. It checks installed version/origin, public Conda URL and digest.
It adds no per-push full-engine requirement or branch-protection check. Standalone
`--noconftest` checks load the real runner/configuration/catalog while isolating
heavy package facades; they do not certify full TopoMT import, actual fpocket
execution, scientific parity, viewer compatibility or the full recovery watermark.
Public installation and hosted workflow results follow once measured.

The broader support-library review remains partial under this issue and #15.
Scientific defects remain with the component development team. MolSysMT and
MolSysViewer execution reviews remain deferred under the shared coordination.

The clean public-channel environment contains Conda DepDigest 0.12.0 `py_0`
with public URL and SHA-256
`03d5aa569bfeb95bdd253a52e68e59094d9af5a6c4c7bc4ba228d3e36cfb30a3`.
Its installed import is inside the new prefix, with no editable provider checkout.
All six availability tests and seven administrative tests pass against this
public artifact on Linux/Python 3.13.15. Provider installed contract and launcher
also pass with the environment PATH. The first launcher invocation used the host
PATH and correctly rejected an outside-prefix launcher; activating the intended
PATH repairs the invocation without changing provider code or assertions.

Hosted workflow [36825125490](https://github.com/uibcdf/topomt/actions/runs/36825125490)
at exact source `1aa25c4346eb0d56c16c5a6453bb600026732c44` is completed/success.
All six actual installed-provider identity and availability-check steps passed
on Linux/macOS and Python 3.11–3.13. This settles the published-provider fpocket
availability migration. It does not close this broad support-library review or
replace complete scientific recovery evidence.


Final compatibility correction: a relative command containing a directory
(e.g. `bin/fpocket` or `./fpocket`) is resolved by subprocess relative to its
execution directory, which may differ from the caller's directory. Three new
cases failed before correction (two valid execution-directory cases and one
false-positive caller-directory case). The runner now gives DepDigest the same
resolved executable path while preserving the original subprocess command and
public error metadata. Bare command names retain PATH discovery. All nine
availability cases and seven administrative tests pass against the clean public
provider; scoped mypy and changed-file Ruff lint/format pass. The final exact
source needs its own focused hosted run; the preceding six-case run remains
historical evidence.

Final focused run [36829466420](https://github.com/uibcdf/topomt/actions/runs/36829466420)
completed/success at `0fbaa32dc74100e8fb04e2c06e7ee29093cd3fc9` after integrating
concurrent catalogue documentation. All six native verification steps succeeded;
logs show nine passed availability cases in every Linux/macOS Python 3.11–3.13
cell. Dispatch 36829387085 targeted the then-remote 7bd47fa after a rejected push
and is not credited with these new cases. No remote work was overwritten.
