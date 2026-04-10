# fpocket corrections

This directory collects technical notes intended for communication with the
upstream `fpocket` project when we identify behaviors that look like bugs,
implementation pitfalls, or scientifically questionable choices in the
reference code.

The purpose of these notes is to keep three concerns separated:

1. Upstream fidelity in `topomt.third_party.fpocket._native_impl` native mode.
2. Potential fixes or pull requests to the original `fpocket` project.
3. Possible TopoMT-specific improvements that should live in a different mode
   such as `implementation='topomt'`.

Each report in this directory should try to document:

- the exact upstream location involved,
- the exact observable behavior,
- how the issue was diagnosed,
- how another developer can reproduce it,
- what evidence we have,
- what practical consequences it has for parity or scientific behavior,
- whether the issue looks like a bug, an ambiguous design choice, or a
  methodological weakness,
- and the smallest code change we would propose upstream.

These notes are intentionally more detailed than a normal issue draft. The aim
is that each report can later be transformed with minimal editing into:

- a GitHub issue,
- a pull request description,
- or both.

That means every report should preferably include:

- a short title candidate,
- a concise "why this matters" section,
- a precise code location,
- a minimal reproduction strategy,
- concrete observed systems or files,
- expected vs observed behavior,
- and a candidate patch sketch.

Current reports:

- `report_truncation.md`: notes on the missing flush/synchronization before
  reading the temporary `qvoronoi` output in `fpocket`.
- `report_bfactors.md`: notes on the current upstream handling of B-factor
  statistics and the consequences for vertex acceptance in `testVvertice()`.

## Future wrapper packaging note

In the future, the TopoMT wrapper should preferably depend on a UIBCDF-built
and UIBCDF-distributed `fpocket` package instead of an arbitrary third-party
binary from the active environment.

This is now justified by direct evidence that different `fpocket` binaries can
produce different final pocket sets on the same input, even when they report
the same major version family.

Before adopting any future UIBCDF-packaged `fpocket` binary as the wrapper
reference, it should be validated explicitly against the audited local source
build and against the known build-drift cases.

At minimum, that validation should include:

- exact pocket-count comparison on:
  - `1GG0.pdb`
  - `1N57.pdb`
  - `3LKF.pdb`
  - `E15ALA.pdb`
- pocket atom-membership comparison on the same systems;
- explicit confirmation that the packaged binary does **not** reproduce the
  build-drift currently seen with the conda-forge/system binary on:
  - `1GG0.pdb`
  - `3LKF.pdb`
  - `E15ALA.pdb`
- explicit confirmation that the packaged binary behaves consistently with the
  audited local source build after the temporary-output synchronization fix
  described in `report_truncation.md`.

Only after passing that validation should the UIBCDF-packaged binary be treated
as the wrapper oracle for parity work.
