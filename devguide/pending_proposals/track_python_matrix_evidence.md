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
