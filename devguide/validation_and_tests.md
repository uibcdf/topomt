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
- [tests/test_dfnd_pockets.py](/home/diego/repos@uibcdf/topomt/tests/test_dfnd_pockets.py)
- [tests/methods/pocketeer/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/pocketeer/test_parity.py)
- [tests/methods/pocketeer/test_wrapper.py](/home/diego/repos@uibcdf/topomt/tests/methods/pocketeer/test_wrapper.py)
- [tests/methods/alphaspace2/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/alphaspace2/test_parity.py)
- [tests/methods/alphaspace2/test_wrapper.py](/home/diego/repos@uibcdf/topomt/tests/methods/alphaspace2/test_wrapper.py)
- [tests/methods/fpocket4/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/fpocket4/test_parity.py)
- [tests/methods/pycasta/test_parity.py](/home/diego/repos@uibcdf/topomt/tests/methods/pycasta/test_parity.py)
- [tests/methods/pycasta/test_wrapper.py](/home/diego/repos@uibcdf/topomt/tests/methods/pycasta/test_wrapper.py)
- [tests/io/test_load_castp.py](/home/diego/repos@uibcdf/topomt/tests/io/test_load_castp.py)

## What is currently covered reasonably

- basic `Topography` behavior;
- basic pocket feature behavior;
- alpha-sphere behavior;
- basic CASTp path checks;
- focused upstream parity for `pocketeer`, `alphaspace2`, `fpocket4`, and a
  growing `pycasta` bounded battery;
- first wrapper smoke/parity coverage for `pocketeer`, `alphaspace2`, and
  `pycasta`, validating the real wrapper-backed execution path in addition to
  the native-method parity suites;
- import smoke tests;
- DFND smoke-like integration checks.

## What is currently weak

- there are no dedicated tests for several prioritized engines;
- geometry-heavy behavior is not deeply validated;
- cross-engine contract consistency is not tested enough;
- environment-sensitive behavior is not clearly separated from code bugs.

## Why wrapper tests are not redundant

Wrapper smoke/parity tests should be treated as a distinct validation layer,
not as duplicates of the native parity suites.

Reason:

- native parity tells us whether `topomt.methods.*` reproduces the algorithmic
  semantics we intend to preserve;
- wrapper parity tells us whether the actual external package or binary, as
  installed or mirrored in a given environment, still behaves as expected when
  routed through TopoMT;
- those are not the same question.

This matters because the wrapper route can surface upstream-environment drift
that native parity alone would miss. The `fpocket4` work already exposed this
kind of problem: different fpocket builds or distributions can disagree at the
final-pocket level even when the audited upstream source build and the native
TopoMT reimplementation agree with each other.

Practical implication:

- keep native parity as the primary algorithmic validation target;
- keep wrapper smoke/parity as the integration validation target for the real
  external executable or package path;
- and document wrapper failures explicitly as possible build/package/environment
  drift before treating them as native-method regressions.

## Known gaps

- [tests/io/test_load_castp.py](/home/diego/repos@uibcdf/topomt/tests/io/test_load_castp.py) is
  effectively empty and should become a real regression suite for the loader.
- There is still uneven direct coverage across the newer `topomt.tools`
  subpackages, and `pycasta` still does not yet cover the full upstream
  benchmark inventory even though its audited bounded battery has already
  grown beyond the original single-case checkpoint.
- The remaining `pycasta` audited outlier is currently `1apu`, as a deliberate
  native-versus-upstream semantic residual (`molsysmt` molecular selection
  versus upstream `ATOM/HETATM` preprocessing).
- `pocketeer` and `fpocket4` now have dedicated focused tests, but their
  heavier parity and deep-validation paths should still be expanded and better
  categorized.
- The repository does not yet expose a clear benchmark battery for comparing
  engines across the same systems.

## Practical testing priority

For the current roadmap, the next validation steps should be:

1. strengthen direct tests for the prioritized non-DFND engines;
2. test local-to-global atom-index mapping explicitly;
3. test feature metadata consistency across engines;
4. expand loader tests for CASTp;
5. keep DFND separate until it returns to active priority.

## Environment caveat

Test results should be interpreted carefully with respect to the declared
supported Python versions.

The repository targets Python 3.10, 3.11, and 3.12. Results obtained in newer
interpreters can still be useful, but they should not be confused with the
official support story.

## Practical interpretation

The test suite is useful enough for iterative development, but not yet broad
enough to serve as a strong release-quality validation envelope.
