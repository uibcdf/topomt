# Certified analytic edge-volume receiving, version 1

Owner [TopoMT #76](https://github.com/uibcdf/topomt/issues/76).
[Mathematical construction](../../DFND/reference_validator_edge_integration.md).
[Portable capsule](../../../docs/content/benchlab/synthetic/artifacts/reference_validator_edge_v1/README.md).

## Qualified original numerical scope

All **19 original profiles** of the six synthetic cases now pass their original
k=24 requests: absolute `V(domain)*2^-24` AND relative `2^-24`, for the total
and every region. Thirteen positive profiles contain sixteen positive regions;
six excluded profiles have exact zero volume. Complete original topology and
boundary incidence are retained. Every new interval lies inside its previous
conservative total/per-region enclosure. Inputs, radii, probes, units, frames,
source identities and the 355 frozen files are unchanged.

The reader reconstructs the original power cells, proves complete regional
face assignment and evaluates the exact-cut analytic edge formula with outward
numerical error. Proposals contain no trusted totals or region assignments.
This supplies precision receiving for these fixed numerical Models, not a
native DFND correction or universal public/molecular/platform admission.

## Results and resources

| Original case | Probe (Å) | Regions | Volume (nm³, approx.) | Relative width (approx.) | Worker seconds | Peak RSS (MiB) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `closed_shell` | 0.05 | 1 | 0.391781717 | 3.50e-33 | 113.659 | 41.02 |
| `closed_shell` | 0.2 | 1 | 0.343932389 | 6.93e-34 | 108.708 | 40.85 |
| `closed_shell` | 1.4 | 1 | 0.113003533 | 8.39e-33 | 106.245 | 40.49 |
| `closed_shell` | 5 | 0 | 0 | exact zero | 47.140 | 30.84 |
| `dumbbell` | 1.4 | 3 | 0.506127414 | 3.05e-33 | 148.083 | 43.73 |
| `dumbbell` | 2.2 | 2 | 0.232003479 | 1.25e-32 | 141.403 | 43.64 |
| `dumbbell` | 6 | 0 | 0 | exact zero | 59.096 | 34.39 |
| `regular_tetrahedron` | 1.2 | 1 | 0.000918450981 | 2.69e-34 | 0.110 | 20.56 |
| `regular_tetrahedron` | 1.4 | 1 | 5.0841273e-05 | 5.55e-33 | 0.091 | 20.64 |
| `regular_tetrahedron` | 1.7 | 0 | 0 | exact zero | 0.041 | 20.43 |
| `shell_with_opening` | 1.4 | 1 | 0.119933998 | 6.48e-33 | 90.085 | 38.80 |
| `shell_with_opening` | 3 | 1 | 0.00982842986 | 2.51e-31 | 87.950 | 38.44 |
| `shell_with_opening` | 5 | 0 | 0 | exact zero | 38.558 | 29.20 |
| `straight_tube_narrow_dense` | 1.2 | 1 | 0.0153698025 | 1.51e-31 | 90.405 | 41.63 |
| `straight_tube_narrow_dense` | 1.4 | 1 | 0.00466733155 | 5.80e-31 | 80.867 | 40.90 |
| `straight_tube_narrow_dense` | 2.5 | 0 | 0 | exact zero | 22.390 | 31.69 |
| `straight_tube_wide_sparse` | 1.4 | 1 | 0.549362246 | 2.16e-33 | 97.330 | 41.94 |
| `straight_tube_wide_sparse` | 2.5 | 1 | 0.194638391 | 1.39e-32 | 92.989 | 41.60 |
| `straight_tube_wide_sparse` | 5 | 0 | 0 | exact zero | 29.688 | 32.20 |


Displayed volumes are rounded midpoints and relative widths are approximate;
the exact rational endpoints and original requests are in the capsule. These
are arithmetic enclosures for fixed exact inputs, not experimental uncertainty.
The total and every region pass independently, including the small extra
boundary regions of dumbbell. Region counts are not morphological catalog names.

All original workers run sequentially with one CPU/thread and 2 GiB address
space. The original receiving takes **1354.837 worker wall / 1353.655 CPU
seconds**; bounded process elapsed sums to 1357.359 seconds. Peak worker RSS is
44,784 KiB (43.73 MiB). All five-second host samples preserve the reserve. Each
worker has finite 300/330 CPU-second and 420 wall-second ceilings; these are
safety ceilings, not reserved machine resources or runtime goals.
The worker times include input/Model reading, proposal saving, a new Model read
and full independent topology/volume verification. They do not hide verification
behind a producer-only timing. Originals use a declared 128-bit proposal;
only an unmet request could select a new stronger arithmetic proposal.

## Controls and arithmetic cost

`controls_final/receipt.json` qualifies all sixteen original clipped-cube
k=8/16/24/32 controls, including eight extremely tiny regions. Each region lies
within the independent polynomial sandwich; near-rational cancellation needs
512 bits. `region_controls_final/receipt.json` qualifies all nine earlier
region controls, including the asymmetric three-region Model. Independent
unit controls also cover signed-owner faces, exact 3-4-5 contacts, rational
covariance, literal-zero cases, bad units/topology and maximum 2048-bit atan.

The first original dumbbell attempt reaches its 180 CPU-second budget without
producing a complete certificate; `original/` and `source_attempt_1.zip` retain
it. `cost/` isolates face preparation and the first 32 face integrals using
historical checked labels only for profiling, not for a new physical result.
The Fraction atan implementation dominates that sampled integral cost.
`matched_primitive_cost.json` measures the same 32 pieces unprofiled: median
2.912799 seconds for Fraction arithmetic and 0.299421 for integer dyadic
arithmetic, with compatible certified enclosures. This is a primitive-cost
comparison, not a full-analysis speedup against an unfinished baseline.

A declarative proposal also avoids evaluating the integral in order to prepare
a record which the saved reader must evaluate again. The actual final execution
still checks the complete topology and every numerical contribution. Final
receiving lives under `original_retry/`; all earlier source-scoped attempts,
including the 0.117-second extra-control harness error for a null topology path,
remain retained. That error preceded scientific evaluation and is corrected
by reading the original embedded topology, not by changing geometry.

## Retention and remaining gates

`receiving_index.json` maps original records to checksum-bound capsule members.
Large original certificates are stored once in the ZIP. The working
`certificate_128.json` is byte-identical to the final certificate; the duplicate
alias rule is recorded. Models, verification receipts and resource logs remain
in the evidence tree. `source_retry.json` binds all executable inputs used for
the complete receiving, and source snapshots/drivers preserve reproducibility.
Old notebooks, artifacts, downloads and historical coarse outcomes are retained.

`source_qualification.json` records 200 distinct selected passing tests, with
the three enriched receiving guards rerun after their final assertions. These
cover independent formulas, exact predicates, power cells, hulls, region bounds,
saved reading, resume/performance controls, the DFND worked documentation and
reporting protocol. Repository Ruff/format, the 47-module local mypy route,
report-index and offline comparative-finding checks pass. A strict one-CPU Sphinx
build passes; its rendered report anchor, method-book link and copied archive
digest are checked. This is local rendering, not hosted-site deployment.

The fresh capsule guard uses a separate interpreter with site packages disabled
and explicitly blocks producers/scientific dependencies. It reconstructs the
original tetrahedron, tiny eight-region and asymmetric three-region results.
`closeout_checks.json` confirms all 47 executable source files still match the
original receiving freeze, all 355 original evidence files are unchanged and
the pre-existing human version edit is preserved. `MANIFEST.json` binds this
evidence tree; `execution_drivers.zip` retains the task runners and earlier
attempts. The raw logs, including failures, retain their original bytes.

The eight-stage performance plan stays partial. S4's original serial precision
gate is now delivered; S1/S3 instrumentation/invariant follow-up, conditional
compiled work, full parallel fault/resume qualification and public/installed/
platform admission retain their gates. #76 remains open for that work and common
native receiving under #60. Native #181/#180/#184/#188 are not resolved by a
stronger reference. No new BenchLab family, protein or original provider run is
selected. The checker executes no original external engine or scientific
floating backend; optional production attribution/API adoption remains at P6.
