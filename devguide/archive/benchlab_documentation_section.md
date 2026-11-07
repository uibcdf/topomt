---
summary: Give system studies a dedicated BenchLab section with synthetic and molecular collections.
issue: uibcdf/topomt#133
status: resolved
opened: 2026-11-07
closed: 2026-11-07
severity: low
verification: inspected
area: [documentation, dfnd]
guard: tests/test_dfnd_regular_tetrahedron_reference.py::test_public_tetrahedron_input_preserves_units_model_and_submitted_bytes
normative: devguide/DFND/study_zone.md
blocked_by: []
supersedes: []
---

# Dedicated BenchLab documentation section

## What

The maintainer selected a first-class documentation section for the system
laboratory, with synthetic and real molecular collections. Showcase and Cookbook
are not the canonical destinations for these scientific study units.

## How

Use `docs/content/benchlab/`, with `synthetic/` and `molecular/` indexes. Each
case has a stable descriptive directory, `index.ipynb` and versioned artifacts.
Move the two existing controls and update navigation, active references and
tests. Keep earlier documentation URLs as relocation pages.

## Why

The collection guides DFND development and original-method comparison one
system at a time, with independently justified references and a future shared
publication source. Synthetic and molecular evidence require separate context.

## What was refuted

Copying the notebooks into another section would create competing study sources.
Moving scientific evidence does not justify changing its inputs, outputs or
reference claims. A Molecular systems index is not a delivered protein benchmark.

## Scope and exclusions

Documentation organization and fixture receiving paths only. No engine change,
notebook rerun, new provider submission, new molecular characterization, hosting
deployment or qualification of #75/#76/#16. Preserve human `_version.py` changes.

## Acceptance criteria

- Main documentation navigation exposes BenchLab and both collections.
- Both controls render from their canonical case directories with downloads.
- Seventeen artifact files retain SHA-256 identities; scientific notebook cells
  and reviewed outputs remain equal to the baseline.
- Old documentation addresses link to the new studies without duplicate notebooks.
- Reference/evidence checks, applicable static checks and documentation builds
  retain their actual executed scope and outcomes.

## Verification

The test-first receiving run fails three existing reference/notebook checks with
FileNotFoundError before the move. The initial full Sphinx build stops importing
`sphinxcontrib.plantuml`, declared in both existing development/docs environment
YAMLs but absent in the shared environment. The maintainer has been asked to
install that existing development dependency; no package was installed by this task.

The maintainer installed the extension and confirmed completion; installed
`sphinxcontrib-plantuml` 0.30 is now usable by Sphinx. The separate executable
renderer remains unavailable in the tool context. Shared development/docs
dependency receiving and the requested development/production environment names
are reported in [MolI #94](https://github.com/uibcdf/moli/issues/94) and
[MolSysSuite #175](https://github.com/uibcdf/molsyssuite/issues/175), linked both
ways. This task does not rename or recreate an environment.

## Delivered structure and checks

BenchLab replaces Showcase in the main documentation navigation. Its synthetic
index links `regular_tetrahedron/index.ipynb` and `closed_shell/index.ipynb`, each
with its existing `artifacts/<case>_v1/` directory. The molecular collection has
an explicit planned status and molecular-specific reference requirements. Four
earlier Showcase HTML addresses retain relocation pages rather than duplicate
scientific sources. Disposable notebook `runs/` folders are ignored locally.

All seventeen versioned artifact SHA-256 values match the baseline. Both
notebooks retain identical scientific code cells, execution counts and outputs;
only their location/name and a Markdown navigation link changed. Active developer
references and five fixture-receiving test modules use the new canonical paths.
The declared guard failed before the move and passed after it.

The selected reference/provider-evidence/CAST geometry/reporting battery passed
**48 tests** in the shared Python 3.14 environment with Pytest Receptor. Ruff
lint/format and mypy passed on the five modified test modules; two existing
NumPy-local annotation gaps in the ProtOr module were made explicit without
changing test values or behavior.

Complete `make html` builds with `-j 1 -E -a` passed against both the unmodified
baseline and the candidate documentation. Owned source copies kept generated API
files out of the checkout; the regular Sphinx configuration and its stored-output
notebook policy were retained. Both fresh builds reported the same twelve
existing warnings, including the unavailable PlantUML command and existing
navigation/reference/style warnings outside BenchLab. No new warning was added;
this is not a warning-free build or proof that the unrelated UML diagram renders.

Rendered verification checks the main BenchLab navigation and all local link,
download and image targets on nine new/compatibility pages: **212 targets**
resolve. This exposed an existing footer link hardcoded as
`contents/about/who.html`; using Sphinx's `pathto` fixes it at arbitrary case
depths. The check failed on the old generated link before that correction.

The report/index checks and publication identities are recorded in #133. Useful
HTML preview and local comparison receipts are retained by TopoMT maintainers
until the next BenchLab documentation review; disposable build/source copies
can be removed after readback. New notebook execution, remote hosting, the full
scientific suite and installed/platform matrices remain separate. Deferred
qualification/CI evidence retains #16/#58/#81; the authorized incremental commit
carries `[skip ci]`.
