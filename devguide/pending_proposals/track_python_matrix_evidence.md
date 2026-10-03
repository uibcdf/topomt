---
summary: Track TopoMT Python matrix evidence before a support or release claim.
issue: uibcdf/topomt#16
status: partial
opened: 2026-09-08
closed:
verification: measured
area: [governance, ci]
guard:
normative:
blocked_by: []
supersedes: []
---

# Track Python matrix evidence

## What

The original Python 3.11–3.13 policy wiring has been implemented. TopoMT
remains incubating, and its full test matrix is not passing evidence for a
support or release claim. This open record tracks that distinction without
requiring scientific test failures to be fixed during governance work.

## How

At source `015cb48001e947301b6eb42e8174d17aa7acb1b2`, package metadata
declares `>=3.11,<3.14` and Ruff targets `py311`. The policy workflow calls
`check-python-repository.yaml@policy-v1.5.2`. The Ruff workflow runs full
`ruff check .` and `ruff format --check .`. CI configures Python 3.11–3.13,
pins Pytest Receptor `0.6.0`, selects `--receptor=ci`, and installs controlled
suite source revisions including ArgDigest and MolSysMT.

Policy run `36311638223` and Ruff run `36311638009` passed at that source.
CI run `36311638015` failed all six test jobs with
`ModuleNotFoundError: alphaspace2`; GH Run Receptor `1.0.0` reported the
failure. That work belongs to TopoMT's component developers. It remains
visible as an unmet matrix gate before any support or release claim.

## Why

The old issue description still lists missing ArgDigest setup, Ruff cleanup,
and an older reusable workflow revision as current work. Those descriptions
are stale. Keeping only the actual matrix-evidence gate avoids conflating
governance configuration with early scientific implementation.

## What was refuted

Current configuration and successful policy/Ruff runs refute the old claim
that the shared workflow or complete Ruff gates are absent. The failed matrix
does not establish a passing Python support claim.

## Scope and exclusions

This record tracks support and release evidence only. Ecosystem library/tool
adoption is under `uibcdf/topomt#56`; reporting governance is under
`uibcdf/topomt#54`. Scientific fixes remain with the TopoMT team.

## Acceptance criteria

Before a release or unqualified supported-matrix claim, demonstrate passing
installed-package and test evidence for the claimed Python and OS cells under
the current MolSysSuite CI policy, or record an explicit bounded policy
decision where that policy permits one. Do not mark a failing matrix as green.

## 2026-10-01 notebook dependency regression

CI `36874210900`, at `3da03db196c3a679af54152a868024eae187aada`, failed all
six matrix jobs during collection: the new tetrahedron reference test imports
`QuantityRecord`, which was absent from the controlled PyUnitWizard revision
`342babd`. Local validation imported a newer editable revision, so it did not
expose that mismatch. GH Run Receptor identified the failed jobs; native failed
logs established the exact import error. This is a regression introduced by
the notebook tests, not a native DFND calculation failure.

The controlled source pin is advanced to the canonical QuantityRecord feature
commit `23554a7aca31cba144ef248b9771d4668815dd1c`. Its PyUnitWizard source matches
the locally tested checkout; its codec is provisional. The adopted reference
tests exercise record decoding and dimensional quantities without adding a
TopoMT-specific serialization fallback. A passing full matrix remains a separate
gate; the pin correction alone does not establish it.

## 2026-10-01 subsequent matrix evidence

CI run `36887103616` at `88e2164c17b118327ff8fc7383a9b2a4c1e60ed0`
failed. GH Run Receptor reported five cells failing Conda environment setup;
bounded failed-log inspection identified `ENOENT` in setup-micromamba's shell
setup. The macOS/Python 3.11 cell reached pytest and failed
`tests/test_dfnd_morphometrics.py::test_funnel_motif_detects_steady_narrowing`.
These failures are distinct from the corrected QuantityRecord collection error
and from the separately passing local CAST regressions. The full matrix remains
an unmet support gate; no CI or DFND fix is included in the bounded CASTp slice.

## 2026-10-01 b564a85 job evidence

In CI run `36922512390`, the completed Ubuntu/Python 3.13 job `110571755495`
reports seven failures, 984 passes, 85 skips and five expected failures.
GH Run Receptor identified failing test jobs; the native job-log API supplied
the bounded pytest causes while other matrix cells were still running:

- four DFND raw-characterization hash comparisons;
- two fpocket native/wrapper comparisons invoking an unavailable executable;
- the dependency-contract test finding `depdigest` absent from installed metadata.

None of those named failures is in the CASTp selectors. This completed job
does not certify the other cells or a green matrix. The new CASTp radius-profile
slice has separate local evidence; the wider failures remain outside that slice.

## 2026-10-01 9516716 job evidence

In run `36937886645`, the completed Ubuntu/Python 3.13 job `110622317159`
reports seven failures, 1,590 passes, 85 skips and five expected failures.
GH Run Receptor identified failed test jobs; its pending-run report did not
resolve their causes. Native failed-log inspection was unavailable while the
run was active, so the completed job-log API supplied the bounded causes.
They are the same four DFND raw hash comparisons, two unavailable fpocket
executable comparisons and missing `depdigest` installed metadata described
above. No CASTp selector failure is reported. This is evidence for that
completed cell only; the other cells and subsequent source remain uncertified.

## 2026-10-02 completed 387f9b4 matrix evidence

Run `36942562766` completed with all six test cells failing. GH Run Receptor
named dependency metadata and DFND morphometrics failures; its bounded causes
did not describe every failure. Native failed logs establish additional
CASTp connectivity failures in both Ubuntu and macOS Python 3.11/3.12: seventy-two
modern-void setup errors and six geometry-policy failures reach per-atom
`n_bonds`, then NumPy's inconsistent empty-array dimensionality. The Python
3.13 cells instead reach the CASTp tests without that error; Ubuntu reports
1,968 passes and seven wider failures, macOS 1,967 passes and eight failures.

MolSysMT's owning issue `uibcdf/molsysmt#283` is already closed with source
fix `91f157eeb`. TopoMT CI still installs `3bcfaf4`, which predates that fix.
Adopting and validating the corrected controlled provider source is consumer
work here; no downstream bond-query implementation or silent fallback is
appropriate. The local forty-system feature audit uses the working Python
3.13 development environment and does not establish matrix compatibility.
The other failures (DFND, fpocket, dependency metadata and additional older-cell
scientific checks) remain part of this support gate. No passing matrix is claimed.


## Required four-minor adoption — 2026-10-03


## What

The suite maintainer requires Python 3.11–3.14 from every Python member under
uibcdf/molsyssuite#51 and immutable `policy-v1.5.3`. Inspected source `b1969bcc04468ab6e4899062a91a00450458bdb8`
still excluded 3.14. This record separates required adoption from scientific
qualification and public delivery.

## How

Metadata, contributor instructions, required full CI, applicable recipe and
installed-candidate matrices now cover `>=3.11,<3.15`. Routine development
stays on 3.13. Recovery requires successful **executed** Linux full tests on
all four minors before advancing its watermark. PR/internal-push schedules
and all existing scientific assertions/test selection are preserved.

The new 3.14 lane uses the existing controlled-source mechanism, with MolSysMT
`3eb5afd1de087f775b78d7fa45ad69cca3a02d43` and MolSysViewer `ec4c71e574d798b7c8675b7e7e983da878ce9889` (metadata inspected to admit 3.14;
the suite transition records their qualified source pair). Older minors keep
their prior source revisions. Where needed, the 3.14 environment keeps the
3.13 scientific dependency surface and uses published Pytest Receptor 1.1.0.
ElastNetMT's LinDelINT provider migration is owned by uibcdf/lindelint#14.
These source routes remain test evidence, not publicly delivered closure;
replace them after reviewed compatible public packages are independently
installed. Do not bypass Requires-Python.

## Why

Old provider revisions cap Python below 3.14, so changing only the consumer
bound would leave ordinary installation blocked. A three-minor matrix must
not clear the new required four-minor CI debt.

## What is measured and what is assumed

Source metadata, exact provider bounds, existing CI and prior recipe/resource
gates have been inspected. New solver, installation and full-test outcomes
are recorded as obtained; configuration alone proves none of them.

## Alternatives and refuted paths

Metadata overrides and tolerated/skipped scientific failures cannot establish
support. Replacing older-minor dependency generations globally would expand
the compatibility surface unnecessarily; the new route is scoped to 3.14.

## Scope and exclusions

Governance and ecosystem compatibility only. Scientific defects remain with
the owning component team and are neither suppressed nor fixed here. Source
configuration does not authorize public upload or a delivered-support badge.

## Acceptance criteria

- Coherent four-minor metadata/recipe/full-CI/installed-artifact contract.
- Ordinary installed 3.14 import and full relevant tests, or concrete owned
  blockers that preserve actual failure and bounded pending adoption.
- Historical three-minor evidence cannot clear skipped-CI debt.
- Candidate/channel and fresh public clean-install evidence precede admission.

The recovery regression is
`tests/test_ci_backlog.py::test_a_previous_three_minor_matrix_cannot_clear_314_debt`.

### Test-results publisher condition inspected on 2026-10-03

Expanding the matrix exposed an existing malformed mixed expression in the
test-results upload condition. Actionlint reported that surrounding text made the
condition always true. The complete condition is now one GitHub expression,
retaining test-results publication only from Linux/Python 3.13 after failed tests
as well as successful tests, unless the run is cancelled. Python 3.14 cells
run the suite without publishing additional test-results uploads. The separate
coverage report publisher was already correctly scoped to Linux/Python 3.13.
