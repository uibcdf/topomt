**Source continuation — 2026-11-10:** the bounded physical implementation is
received at `4fc2353`; its five controls and seven former missing-view targets
now pass. See [the implementation record](physical_boundary_implementation.md)
and [resolved report](../archive/dfnd_physical_boundary_refinement.md). Earlier
checkpoint statements below are dated evidence, not current capability status.
Wider paths/small-probe shell references remain #76 and volume precision #75.

# Physical-boundary acceptance checkpoint

Date: 2026-11-09. Owner: [#151](https://github.com/uibcdf/topomt/issues/151).
Delivery: executable regression and [concrete contract proposal](boundary_connectivity_contract.md)
before modifying the scientific algorithm. **Runtime refinement is pending.**

## Scope and measured source receiving

Scientific baseline: `bcf833f0ca3a72ef71e9797744992cc5aaaf4a90`, source workspace,
Python 3.14.10 in `molsyssuite@uibcdf_3.14`. This increment changes tests and
documentation only. The earlier uncommitted version-file change is preserved
outside this delivery; it does not change the numerical source under study.

The new `tests/test_dfnd_physical_boundary_contract.py` replays the frozen
tetrahedron, closed-shell and opened-shell certificates, including their
input/protocol validation. It then receives five full-precision inputs/probes
through MolSysMT and `get_topography(method='dfnd')`. Source exterior links and
public Mouth/class counts remain separate from the independently established
physical counts. The opened shell retains the closed-shell parent selection.

| Control | Reference hull patches | Current physical-reporting capability |
| --- | ---: | --- |
| regular_tetrahedron / 1.2 Å | 4 | Candidate raw/public views absent. |
| regular_tetrahedron / 1.4 Å | 0 | Candidate raw view absent; native/public sealed control passes. |
| regular_tetrahedron / 1.7 Å | 0 | Candidate raw view absent; no resident wet component. |
| closed_shell / 0.2 Å | 0 | Candidate raw view absent; enclosure/public control passes. |
| shell_with_opening / 1.4 Å | 1 | Candidate raw/public views absent despite matching legacy Mouth count. |

The initial unmarked regression produced **2 passed / 7 failed**. All failures
were the dedicated `PhysicalBoundaryViewAbsent` exception: five raw observations
and two public positive-contact observations. No physical count was substituted
with a native link or Mouth count to obtain that result.

The seven future-acceptance targets now use `xfail(strict=True,
raises=PhysicalBoundaryViewAbsent)`. Missing capability remains explicitly
pending. Other exceptions and present but incorrect observations fail normally;
passing targets force marker removal/review. These are draft API acceptance
targets, not support/correctness qualification or a scientific fix.

## Executed checks and resource bounds

- Focused panel: **46 passed, 7 xfailed** across the new acceptance tests,
  tetrahedron/opened-shell certificates, closed-shell wall cover and public
  three-case receiving guards. Elapsed wall time 13.07 s; peak RSS 308 MiB.
- The tetrahedron preservation guard verifies all **161** earlier scientific
  files. No frozen input, certificate, notebook or observation bytes change.
- Initial red run: 5.16 s wall time, peak RSS 294 MiB, expected nonzero exit.
- Ruff check/format and local mypy on the new acceptance test pass; the diff
  whitespace check passes.
- Reporting/comparative lifecycle tests: **16 passed**. Regenerated report
  indexes, offline comparative validation and report-index checks pass.
- Sphinx HTML build, one worker: exit 0, 10.23 s, peak RSS 272 MiB. Its nine
  warnings concern unchanged documentation outside this slice (notebook heading
  levels, existing API/toctree omissions and the installation environment link);
  none concerns the three edited case pages. Notebooks were not executed.

Both numerical runs were sequential, pinned to one CPU, with BLAS/OpenMP
threads fixed at one, address space limited to 6 GiB and CPU time to 90 s.
The preflight found about 50 GiB available of 60.5 GiB physical memory, zero
memory PSI and no active swapping in the sampled interval, with other users
active. A four-second Slurm discovery attempt could not open its socket; no
allocation was claimed. This bounded local run remained far below the required
memory reserve. Free resources were not treated as a reservation.

Raw logs/resource receipts are retained locally in
`.cache/dfnd-boundary-contract/`; this committed checkpoint and the executable
tests provide the durable scoped summary. They are not release artifacts.

## Disposition and continuation

The current `tetrahedron-boundary-patches` finding remains **current** and #151
remains **open**. Its retained historical scope is unchanged. The proposed
first implementation adds physical patches and qualified component contacts
alongside legacy links; it preserves catalog classes pending explicit Mouth
promotion review. The record/card/hub must not describe this design milestone
as resolved physical connectivity.

Next under #151: bounded all-atom face-region decomposition and seam decisions,
recoverable support and availability states, path-supported component contacts,
then raw/typed/public receiving with units, atom maps, rigid motion, reporting
and reuse guards. The proposal details the acceptance sequence and unresolved
promotion decision. No new geometry, native protein characterization, provider
execution, external submission, package installation, full-suite, installed
artifact or support-matrix qualification is part of this slice. #60/#76/#75
and the installed/matrix gate #16 retain their separate scopes.
