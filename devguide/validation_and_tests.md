# Validation and Tests

## Purpose

This document summarizes the current validation surface of the repository and
the main testing priorities.

## Current test tree

The current tests live mainly in:

- [tests/test_topography.py](/home/diego/repos@uibcdf/topomt/tests/test_topography.py)
- [tests/test_alphaspheres.py](/home/diego/repos@uibcdf/topomt/tests/test_alphaspheres.py)
- [tests/test_castp.py](/home/diego/repos@uibcdf/topomt/tests/test_castp.py)
- [tests/test_import.py](/home/diego/repos@uibcdf/topomt/tests/test_import.py)
- [tests/test_afnd_pockets.py](/home/diego/repos@uibcdf/topomt/tests/test_afnd_pockets.py)
- [tests/methods/pocketeer/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/pocketeer/test_parity.py)
- [tests/methods/alphaspace2/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/alphaspace2/test_parity.py)
- [tests/methods/fpocket4/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/fpocket4/test_parity.py)
- [tests/methods/pycasta/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/pycasta/test_parity.py)
- [tests/io/test_load_castp.py](/home/diego/repos@uibcdf/topomt/tests/io/test_load_castp.py)

## What is currently covered reasonably

- basic `Topography` behavior;
- basic pocket feature behavior;
- alpha-sphere behavior;
- basic CASTp path checks;
- focused upstream parity for `pocketeer`, `alphaspace2`, `fpocket4`, and an
  initial `pycasta` case;
- import smoke tests;
- AFND smoke-like integration checks.

## What is currently weak

- there are no dedicated tests for several prioritized engines;
- geometry-heavy behavior is not deeply validated;
- cross-engine contract consistency is not tested enough;
- environment-sensitive behavior is not clearly separated from code bugs.

## Known gaps

- [tests/io/test_load_castp.py](/home/diego/repos@uibcdf/topomt/tests/io/test_load_castp.py) is
  effectively empty and should become a real regression suite for the loader.
- There is still limited direct coverage for `pocket_geometry`, and `pycasta`
  still only has a first small repository-parity case rather than a broader
  audited battery.
- `pocketeer` and `fpocket4` now have dedicated focused tests, but their
  heavier parity and deep-validation paths should still be expanded and better
  categorized.
- The repository does not yet expose a clear benchmark battery for comparing
  engines across the same systems.

## Practical testing priority

For the current roadmap, the next validation steps should be:

1. strengthen direct tests for the prioritized non-AFND engines;
2. test local-to-global atom-index mapping explicitly;
3. test feature metadata consistency across engines;
4. expand loader tests for CASTp;
5. keep AFND separate until it returns to active priority.

## Environment caveat

Test results should be interpreted carefully with respect to the declared
supported Python versions.

The repository targets Python 3.10, 3.11, and 3.12. Results obtained in newer
interpreters can still be useful, but they should not be confused with the
official support story.

## Practical interpretation

The test suite is useful enough for iterative development, but not yet broad
enough to serve as a strong release-quality validation envelope.
