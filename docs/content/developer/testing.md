# Testing

The current test suite is useful for development, but still uneven.

## What is covered

There is meaningful coverage for:

- `Topography`
- pocket feature basics
- alpha-spheres
- CASTp integration paths
- import smoke tests

There is also a separate DFND-oriented test file, but DFND is not the current
stabilization priority.

## What is still weak

- direct tests for several prioritized engines;
- deeper geometry validation;
- cross-engine output consistency;
- loader coverage, especially for CASTp file-loading workflows.

## Current testing priority

The current priority is to strengthen tests around the non-DFND engine path and
the common `Topography` contract.

## Optional engine policy

Collection must succeed without Pocketeer, AlphaSpace2, pyCASTA or MDTraj.
Skip a comparison only when its declared optional engine, auxiliary library or
upstream dataset is absent. An installed engine that fails to import an internal
dependency must fail visibly rather than being treated as absent. Unit tests
for portable parsing, atom mapping and argument validation still run.

The dependency regressions exercise collection in a fresh process with engine
imports blocked. They also verify that independent tests run while tests needing
MDTraj skip:

```bash
pytest --receptor=llm tests/test_third_party_dependencies.py
```

Installed-distribution comparisons use a bundled PDB and need no upstream
checkout. Install the engines using the
[user installation instructions](../user/third_party_engines.md), then run this
file in a fresh process so a source checkout cannot shadow an installed package:

```bash
pytest --receptor=llm tests/methods/test_installed_engines.py
```

Missing distributions skip those integration tests. Existing source-checkout
comparisons remain separate and require their upstream datasets. For fpocket,
the CLI comparisons require the executable on PATH or an explicitly configured
command. Passing an installed-engine comparison establishes adapter fidelity
for that input and version; it does not establish native-engine equivalence or
live web-service availability.
