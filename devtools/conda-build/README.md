# TopoMT guarded noarch distribution

Owning review: uibcdf/topomt#78; suite coordination: uibcdf/molsyssuite#45.

The recipe emits one `noarch: python` coordinate with metadata Python/runtime
bounds and host build tools. The four publication/governance wrappers pin the
accepted SDK `2d32048457c6d37093ae509f5626d00a5cda121b`. Source/context preflight
and optional environment operations separately pin additive SDK
`8f00e6d9de943b6e4710ea62936e2ebea00fad24`. Existing secret mapping is preserved;
access remains unconfirmed. A changed wrapper reference is source adoption, not
an executed candidate or delivered public package.

The resource inventory covers **609 tracked files** across `topomt` and
`molsysviewer_topomt`, including the embedded version, runtime data/reference
assets and the lazy viewer addon. Package discovery admits only these roots;
SDK/tests namespaces cannot become wheel packages. Non-Python reference assets
have explicit package-data selections. No bundled native executable/extension
was found in the current tracked roots; optional engines remain separate.

`release_plan.example.toml` selects illustrative `0.0.0`, not an actual release.
Before a candidate, commit a reviewed real plan and require all twelve exact-head
source/admin jobs and their executed steps, including installed-context preflight,
science, reporting, policy, Conda controls and Ruff. A successful backlog probe,
recipe check or missing/skipped test step cannot authorize publication.

The existing manual installed selection retains the complete local `tests` suite
outside the source checkout. All **eight Linux/macOS arm64 × Python 3.11–3.14**
cells require four steps: exact artifact install, installed-file check, scientific
tests, then a second dependency-provenance check. Select the immutable staged
filename/digest and original producer SHA. An optional separately reviewed
qualification SHA belongs to the corrected validation workflow, never to a
replacement producer/archive identity. Promotion preserves the original file's
bytes and digest; it neither rebuilds nor overwrites an occupied coordinate.

Ordinary environment/source declarations, scientific source matrix, candidate
build, installed artifact matrix and public receiving evidence are separate.
The generalized @3 preflight covers nineteen routes, twelve source records/two
unchanged manifests and seven contexts. Original older-minor/Python3.14 MolSysMT
and Viewer pins and bootstrap overlays remain explicit. There is no inferred
scientific API minimum or optional original-engine promotion to core runtime.

`nglview` is removed from recipe/production runtime by explicit maintainer choice,
retained as development/test/docs tooling. No other required scientific selector
was removed. [Environment tools](../conda-envs/README.md) are optional and do not
add scientific suites to internal pushes or installed tests to routine CI.

Actual source-free environment closure, successful full candidate science,
real plan/access/original archive/installed/public evidence remain partial under
#78/#16. No actual build/upload/promotion or installed-science dispatch was done
for these controls. [Common publication contract](https://github.com/uibcdf/molsyssuite/blob/2d32048457c6d37093ae509f5626d00a5cda121b/devguide/noarch_conda_workflow.md).
