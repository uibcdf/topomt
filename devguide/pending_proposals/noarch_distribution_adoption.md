---
summary: Adopt the distribution policy and a guarded single-file noarch publication route.
issue: uibcdf/topomt#78
status: partial
opened: 2026-10-01
closed:
verification: measured
area: [governance, distribution, compatibility]
guard: devtools/tests/test_distribution_contract.py
normative: MOLSYSSUITE_GUIDE.md
blocked_by: []
supersedes: []
---

# Noarch distribution adoption

## What

Adopt the suite distribution contract under uibcdf/molsyssuite#45. The maintainer
authorized adapting this publisher now and using `noarch: python`.

## How

The recipe declares one immutable noarch coordinate, preserves required metadata
constraints, uses host build tools and pip without dependency resolution. Thin
build/promotion wrappers reuse the common implementation at `a44e86a4f6a01dcbfe28fde46d886bc5cd4254c2`.
`devtools/conda-build/resources.toml` inventories the embedded version, package
roots and tracked runtime data. The example plan declares every supported source
CI job and its executed tests. A dedicated administrative reusable check inspects
the recipe/resources and publication controls without importing scientific code.

## Why

The old publisher used a moving action ref, interpreter/platform fan-out and
unrestricted manual public uploads. It did not retain the common exact-candidate
producer evidence. Its recipe did not declare noarch. The new route inspects the
exact built file before upload and promotes tested bytes without rebuilding.

## What is measured and what is assumed

Source inspection found pure Python code/data and no tracked bundled native
extension/executable. This migration is configuration and offline governance
work. It does not prove installed platform compatibility, scientific correctness,
credential access or public package availability. Full source CI remains unchanged;
internal direct/skip pushes remain available to dprada and LMMV.

## Alternatives and refuted paths

- A green recovery probe with skipped tests cannot authorize a candidate.
- Noarch does not prove macOS, Linux or Windows support.
- A second build/upload is not exact-file promotion.
- `release_plan.example.toml` does not authorize or select a public release.

## Scope and exclusions

Distribution governance and packaging identity/resources. Scientific algorithm
repairs and complete scientific execution belong to this component's team.

## Remaining adoption and acceptance criteria

- Review runtime environments/source routes against metadata with early negative
  dependency evidence and classify retained extra recipe requirements.
- Review each claimed public installation route without inferring it from config.
- Before a candidate, commit a reviewed actual release plan and immutable build.
- Execute the component-owned installed gate for the actual candidate before
  promotion. The delivered six-cell descriptor retains the complete local suite
  and resource/launcher checks; missing, skipped or failed evidence fails closed.
- Confirm publication access only through an authorized maintainer.
- Register actual candidate/build/installed/public evidence only after execution.

The migration implements the common source route; whole-policy adoption remains
partial until these criteria are met. The common policy and module's negative
guards are the durable reference; the owning issue remains open.

## Administrative verification, 2026-10-01

The common early recipe/resource check passes with the example plan; the common
publication-control audit and actionlint pass for all three local wrappers.
Local reporting/index validation passes. No scientific module was imported for
these checks.

An isolated copy was prepared with the common static-version helper and
`pip wheel --no-deps --no-build-isolation`. The illustrative version was 0.0.0;
no release candidate or publication was selected. The wheel is `py3-none-any`,
contains all 297 declared paths and the matching embedded version. This
checks setuptools packaging only; it does not certify a Conda artifact, public
PyPI availability, installed resource use or any scientific/platform claim.

Central common implementation a44e86a passed native governance run 36898671705
and 249 local administrative tests. Its archive guards separately reject missing
resources, stale embedded versions and native payloads before upload.

The extra recipe requirement nglview was retained at this 2026-10-01 checkpoint; the explicit 2026-10-07 maintainer classification below supersedes that pending decision.

## Installed qualification capability, 2026-10-01

The manual installed wrapper and committed six-cell descriptor are now delivered
through common 42e4de425871c125ef058842075c39e50fc6ac64. No installed scientific gate has been executed.
The workflow verifies the exact downloaded/installed Conda file and resources,
requires ordinary public dependency provenance and runs the whole local test
selection outside source, with import checks inside the pytest interpreter.
It neither uploads nor adds a scientific suite to internal pushes. The real
release plan and actual scientific/installed evidence remain future prerequisites.

## Current resource/source/environment controls — 2026-10-07

Initial owner source `bfbd28f8c3d25a438c7b3d1e526097dd56f63d3c` has 609 tracked
files across `topomt` and `molsysviewer_topomt`, while the old 297-path inventory
omits 312. The current inventory covers both roots, version, data, private
modules and addon; bounded discovery excludes SDK/test namespaces and explicit
package-data includes outside-data reference assets. Eighteen local distribution
guards exercise actual shared recipe/archive/context operations and reject
missing addon/private/data paths, stale versions, route/source drift and false
editable origins. Synthetic administrative archives are not scientific artifacts.

The four wrappers adopt publication SDK `2d32048457c6d37093ae509f5626d00a5cda121b`;
source/helper operations use additive qualified
`8f00e6d9de943b6e4710ea62936e2ebea00fad24` (406 central hosted tests). Installed
Linux/macOS arm64 × Python 3.11–3.14 keeps the whole local suite and requires all
four provenance/science steps. Separate optional qualification SHA preserves
original producer/file/digest identity. The example requires twelve executed
source/admin jobs and selects no real candidate.

General @3 proof describes nineteen routes, twelve exact sources, two unchanged
Git manifests and seven contexts. It preserves the distinct older-minor/Python3.14
MolSysMT and Viewer pins, actual public bootstrap overlays and original scientific
commands/matrix/triggers/recovery. Preflight runs before science using isolated
administrative parser imports; it does not install scientific providers. Missing
Python declarations are bounded inside package metadata without removing native
or optional scientific selections. Python3.14 scientific YAML and the existing
optional-engine contract retain their original bytes. Routine Ruff uses 3.14.

The maintainer explicitly chose to remove unused nglview from package/production
runtime and retain it as development/test/documentation tooling. All eight core
requirements and owner-defined optional extras stay unchanged; no scientific API
minimum is invented. A public selector floor still needs owner evidence if its
actual APIs require a newer provider.

Eight helper guards call the shared operator directly. Its thin broadcaster/manager
is import-inert, validates all outputs before writes, checks drift without writes,
respects complete minor/source restrictions and uses explicit checked manager and
target identity. The owner profile generates five ordinary environments; recipes,
plans, scientific test documents, historical counterpart fixture and Git inputs
are outside generation. Unsafe automatic dev/update/discovery flags are retired
with documented explicit replacements. No actual environment operation is run.

The queried official Conda/PyPI metadata endpoints return 404 and GitHub releases
are empty at observation. Installation guidance now states source-development
prerequisites and separates configured publication from actual public receiving
evidence. These observations are not proof of historical absence.

Local 26 administrative guards, reporting/index tests, declared preflight, drift,
Ruff/format, actionlint, conformance and scoped type checks qualify this control
delta; exact-head hosted evidence is delivered in the owning issue after push.
The initial failing guard run detects the missing inventory/controls; the final
guards protect those mechanisms through actual shared operations. The original
297-path illustrative-wheel evidence remains its dated historical measurement.

Whole adoption remains partial: actual source-free production/dev/docs closure,
complete successful exact-candidate science, real plan/access/build/original
archive/eight-cell installed qualification/same-byte public promotion/receiving
evidence stay in this owner issue and #16. Administrative evidence does not clear
science/recovery debt. No source tag, actual build/upload/promotion or installed
scientific dispatch is selected. The modified primary-clone generated version is
preserved by isolated work. Shared provider #108 is already delivered; no copied
sibling helper or new provider capability is required for this adoption.
