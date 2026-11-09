# Packaging and development environments

Use Python **3.14** for routine development. The required supported range is
**3.11–3.14**, expressed as `>=3.11,<3.15` in package metadata. Interpreter
requirements, a successful environment solve and executed scientific support
are separate facts. Component qualification remains under
[TopoMT #16](https://github.com/uibcdf/topomt/issues/16).

Read [the synchronized suite guide](../MOLSYSSUITE_GUIDE.md) and
[the repository instructions](../AGENTS.md) before choosing an installation
route. This page distinguishes daily source development, registered CI inputs
and exact historical reproduction.

## Authoritative files

| Boundary | Authoritative input |
| --- | --- |
| Python bounds, required packages, extras and build backend | [pyproject.toml](../pyproject.toml) |
| Selected optional capabilities and installation diagnostics | [topomt/_depdigest.py](../topomt/_depdigest.py) and [DepDigest guide](../DEPDIGEST_GUIDE.md) |
| Required Conda runtime and package contents | [recipe](../devtools/conda-build/meta.yaml) and [resource inventory](../devtools/conda-build/resources.toml) |
| Registered source routes, contexts and immutable inputs | [dependency_routes.toml](../devtools/dependency_routes.toml) |
| Ordinary environment generation and explicit manager operations | [environment guide](../devtools/conda-envs/README.md), [environment_tools.toml](../devtools/environment_tools.toml) and [tooling groups](../devtools/requirements.yaml) |
| Current shared-workspace eligibility and recipe | MolSysSuite's [development workspace](https://github.com/uibcdf/molsyssuite/blob/main/devguide/development_workspace.md) and registry |
| Exact receiving experiments | Dated provider checkpoints and their checksum-bearing evidence archives |

The required runtime set is ArgDigest, DepDigest, MolSysMT, Numba, NumPy,
PyUnitWizard, SciPy and SMonitor. Current explicit support-library floors are
`argdigest>=0.17.0` and `depdigest>=0.12.0`; inspect metadata before changing
one. Older notes that refer to a then-unpublished API are historical evidence,
not a current package index or a justification to invent another minimum.

Optional extras include `centerline` (`networkx`), `tools` (`scikit-image` and
`scikit-learn`), and `viewer` (MolSysViewer plus the centerline extra).

Scientific attribution uses optional Ackredit through its public portable
contract (`>=0.9.0`). The development tooling group includes it for real-provider
tests, from the `uibcdf` Conda channel. It is not a required runtime package or
a newly qualified PyPI extra. Read the [attribution inventory](attribution.md)
for source receiving evidence and the separate installed/public boundary.
The `alphaspace2` and `pocketeer` extras provide supporting libraries, MDTraj
and Biotite respectively. They do not install their original pocket engines.
Original fpocket, Pocketeer, AlphaSpace2, pyCASTA and CASTp service/file routes
retain the explicit requirements in the
[external-engine guide](../docs/content/user/third_party_engines.md).
PharmacophoreMT is an optional consumer in developer qualification controls;
it is not a TopoMT runtime requirement. `nglview` is development/test/docs
tooling rather than package or production runtime.

## Daily source development

The common Linux workspace uses `molsyssuite@uibcdf_3.14` for its qualified
cohort. Read the current central profile before assuming TopoMT belongs to that
cohort. The recorded TopoMT integration assessment remains tracked by #16;
installing a local clone or using the named environment does not establish
cohort admission. The suite's deliberate `reinstall` operation can include
TopoMT without expanding that qualified cohort.

From the **working MolSysSuite checkout**, inspect the current profile and
local sources before installation:

```bash
python devtools/scripts/development_environment.py profile
python devtools/scripts/development_environment.py sources --workspace ..
```

Use that checkout's maintained workspace instructions to create the environment,
verify its toolchain and connect the eligible clones. This is distinct from the
immutable administrative SDK below. The suite installer owns the current cohort;
do not maintain a second fixed list in TopoMT. A member awaiting shared-workspace
qualification uses a compatible component-owned Python 3.14 environment and
retains the integration gap in #16.

After provisioning compatible dependencies and activating the intended
interpreter, install the intended TopoMT source from its repository root:

```bash
python -c 'import sys; assert sys.version_info[:2] == (3, 14); print(sys.executable, sys.prefix)'
python -m pip install --no-deps --editable .
python -m pip check
```

Use `--no-build-isolation` when the declared build tools must come from the
selected environment. Preserve existing work before installing: versioningit
can rewrite the tracked `topomt/_version.py`. Inspect `git status` before and
after; do not restore a human edit merely to obtain a clean tree.

Verify actual imports from a neutral directory outside the repository as well:

```bash
python -c 'import topomt, molsysmt, argdigest, depdigest, pyunitwizard, smonitor; print({module.__name__: module.__file__ for module in (topomt, molsysmt, argdigest, depdigest, pyunitwizard, smonitor)})'
```

Confirm that editable origins point to the intended clones. Metadata/version
labels alone do not identify the loaded source. Reinstall after dependency,
entry-point, generated-version or compiled-extension changes as appropriate;
restart Python processes that cached the previous installation.

## Bootstrap the administrative SDK

Local declaration, generation and distribution checks require a separate clean
MolSysSuite checkout at
`8f00e6d9de943b6e4710ea62936e2ebea00fad24`. The loader verifies this exact commit
and the administrative module's actual origin. A moving sibling checkout is
not a substitute. With no pre-existing `.molsyssuite` directory, the portable
bootstrap from the TopoMT root is:

```bash
git clone https://github.com/uibcdf/molsyssuite.git .molsyssuite
git -C .molsyssuite checkout --detach 8f00e6d9de943b6e4710ea62936e2ebea00fad24
export TOPOMT_SUITE_ROOT="$PWD/.molsyssuite"
python -m pip install --target .molsyssuite-tools 'PyYAML>=6' 'Jinja2>=3,<4' 'packaging>=24'
python devtools/check_dependency_routes.py --declared-only
python devtools/broadcast_requirements.py --check
```

Both administrative directories are Git-ignored. If a suitable SDK already
exists elsewhere, set `TOPOMT_SUITE_ROOT` to that checkout instead. Use an
administrative overlay compatible with the Python interpreter invoking it;
recreate it when changing Python. Do not overwrite an existing SDK or change a
colleague's working MolSysSuite clone to satisfy this pin.

For a component-owned environment, the reviewed manager supports an explicit
creation operation; it requires the named Conda executable to be available:

```bash
python devtools/conda_env_manager.py create \
  devtools/conda-envs/development_env.yaml --python-minor 3.14 \
  --manager conda --name topomt-dev
conda activate topomt-dev
```

The name must be unused. Follow the environment guide for an update to an
existing active prefix. Install the intended local sources, run `pip check`,
verify imports and then inspect the actual selected context:

```bash
python devtools/check_dependency_routes.py --context development-3.14
```

A source-free environment declaration or a successful manager exit does not
prove that all scientific APIs used by this branch are available. If an API is
missing, compare the owning checkpoint's reviewed inputs and report the gap to
its component; do not copy its implementation into TopoMT.

## CI and historical environments

The scientific CI matrix has explicit Linux/macOS Python 3.11–3.14 lanes in
[CI.yaml](../.github/workflows/CI.yaml). Its fixed Git inputs and overlay rules
are declared in `dependency_routes.toml`; these are not the same input set as
any subsequent prepared-provider experiment. The specialized test YAML files
and historical `importable_env.yaml` stay outside ordinary environment
generation. The docs deployment workflow currently selects Python 3.13; that
lane is not the routine development baseline.

For an exact CI-context reproduction, follow the selected workflow's complete
acquisition order, including its no-deps source inputs and context preflight.
`--context ci-3.14` checks that registered context, rather than an arbitrary
editable workspace or a later independently frozen receiving profile.
The [validation guide](validation_and_tests.md) explains which checks establish
which claims.

Historical checkpoints may name `/tmp`, `/dev/shm`, former home directories,
local binaries or upstream mirrors. Those paths identify the original host.
On another machine, use the committed archive, immutable source IDs and hashes;
recreate environments and paths, then generate fresh receiving evidence.
Copying a Conda prefix or editing a receipt's paths does not reproduce an
experiment. Preserve original receipts unchanged.

## Build and distribution boundaries

Setuptools and `versioningit~=2.0` in `pyproject.toml` own the build. The
`[versioneer]` section in [setup.cfg](../setup.cfg) is legacy configuration;
it does not replace that backend. The generated version, distribution metadata
and wheel filename must agree. Preserve the known generated-version build
behavior and its failed attempts under
[#78](https://github.com/uibcdf/topomt/issues/78); a dirty development wheel is
not a public release. Build qualification candidates in an isolated checkout
so generation cannot overwrite human work in the development clone.

Public release tags use bare `X.Y.Z`. A development version may include distance,
commit and dirty metadata. Publication/governance wrappers use a separate SDK
pin, `2d32048457c6d37093ae509f5626d00a5cda121b`, documented in the
[guarded noarch route](../devtools/conda-build/README.md). The example release
plan is not a selected release or publication authorization.

Exact candidate files, dependency origins, resource contents, installed tests,
platform/interpreter matrix and actual public delivery retain separate gates.
Use the current inventory instead of copying an old file count into a release
claim. Packaging adoption and public/component evidence remain owned by
#78/#16; a focused provider receipt does not close them.
