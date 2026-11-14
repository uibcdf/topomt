# Measured reference-validator panel: six BenchLab systems

Owner [#76](https://github.com/uibcdf/topomt/issues/76); first native consumer #181.
Producer/protocol: `2b21cb2ee63093734ff71f1f70bd4ede7a53ebbb`.
Date: 2026-11-13. The maintainer requested current-validator execution and a
scientific/resource report for every existing synthetic BenchLab system.

Subsequent topology delivery: the
[power-cell receiving](reference_validator_power_cell_construction.md) at
`bb308ba` supplies complete original tetrahedron counts `1/1/0` and free hull
patches `4/0/0`. This checkpoint and its archive retain the earlier `2b21cb2`
query-run results and resource measurements, without retroactive qualification.
The initial narrow-tube attempt of the new route remains historical. Its later
`fd3eeb7` complete proof and `92679fc` saved receiving establish one region/two
free hull patches for the original narrow 1.4 Å Model. The same construction
now has complete topology for four of the nineteen original profiles; fifteen
await its receiving. Other original cases and per-region precision retain
their later gates. The measured table below remains the original query run.

## Actual delivery

The [BenchLab report](../../docs/content/benchlab/synthetic/reference_validator_report.md)
covers all six original inputs and nineteen probes, without changing their
bytes or invoking native DFND/providers. A fresh sequential process per system
records wall time, CPU time, peak RSS and source/hull/per-probe phases. All
cases completed; no resource stop, skipped profile or unavailable result is
replaced by an empty physical answer.

| System | Probe profiles | Wall seconds | CPU seconds | Peak RSS MiB |
| --- | ---: | ---: | ---: | ---: |
| `regular_tetrahedron` | 3 | 2.469 | 2.448 | 51.43 |
| `closed_shell` | 4 | 62.124 | 62.056 | 56.59 |
| `shell_with_opening` | 3 | 37.972 | 37.937 | 55.64 |
| `straight_tube_narrow_dense` | 3 | 2.973 | 2.936 | 52.07 |
| `straight_tube_wide_sparse` | 3 | 13.422 | 13.339 | 53.38 |
| `dumbbell` | 3 | 45.921 | 45.886 | 55.71 |

Total measured batch wall time is 164.953 seconds; summed complete-worker CPU
is 164.602 seconds. These are one-shot Linux samples on shared Intel Xeon
E5-2630 v4 hardware, not equal-task or competitive engine benchmarks. All work
uses one CPU/thread and at most 2 GiB address space. Case caps are 180 CPU/240
wall seconds, with five-second pressure checks; the larger time budget accounts
for repeated exact hull verification on the previously measured shells.
No Slurm or environment change is used.

## What is and is not certified

The common queries use the origin and six fixed rays to exact hull boundary
points. Tetrahedron face rays, the earlier narrow bent interior path and the
named dumbbell chamber anchors/axis add case-specific checks. The complete
sequence produces **305 checked outcomes: 187 accepted proofs and 118 rejected
path candidates**. These are query outcomes, not counts of physical regions.

Each original source hull proof is verified during setup. Its immutable geometry
is shared across probes, while every persisted full Model is independently
read/rechecked. The timing therefore includes that full per-probe geometry check,
but excludes rebuilding the hull producer from scratch. Complete-worker CPU
uses deltas of child **CPU times**; per-worker RSS is the worker's own maximum,
not a subtraction of parent lifetime maxima. Per-phase CPU uses process_time.

For the tetrahedron only, a fresh full partition also operates on the same four
exact source centers' tetrahedron, preserving all spheres/probe/source context.
Both serialized Models and its distinct certificate are retained. The equality
is `conv(the same four centers)`, not volume equality alone or a surrogate box.
At 1.7 Å it proves zero free volume and zero components. Positive tetrahedron
profiles retain conservative volume intervals and unknown complete topology.

**One of nineteen profiles has a complete global count in this run.** The other
eighteen do not. All whole-H one-ball sufficient tests remain unknown; this is
consistent with the distinct tetrahedral cover. No requested precision, general
component inventory, boundary-patch inventory or separation proof is invented.
The earlier complete references retain their stronger source-scoped conclusions.

Notable facts include four free tetrahedron face paths at 1.2 Å, the opened
shell's free +Y hull-reaching ray at 1.4 Å, the narrow tube's bent free path at
1.4 Å despite its occupied origin, wide-tube axial access at 1.4/2.5 Å and
dumbbell chamber connectivity at 1.4 Å. At 2.2 Å the dumbbell anchors remain
free while the tested axis fails; this is not this validator's proof of their
separation. In the closed shell at 0.05 Å, all six axis candidates fail even
though the older thirteen-path reference establishes access elsewhere. The
report explicitly preserves that distinction.

## Evidence, receiving and tests

The [frozen protocol](../../docs/content/benchlab/synthetic/artifacts/reference_validator_panel_v1/protocol.json),
[structured summary](../../docs/content/benchlab/synthetic/artifacts/reference_validator_panel_v1/summary.json),
[raw receipt](../../docs/content/benchlab/synthetic/artifacts/reference_validator_panel_v1/receiving_receipt.json)
and [download](../../docs/content/benchlab/synthetic/artifacts/reference_validator_panel_v1/receiving.zip)
retain measurements, model/proof identities, raw outcomes and logs. The
[archive manifest](../../docs/content/benchlab/synthetic/artifacts/reference_validator_panel_v1/bundle_manifest.json)
binds all included bytes. The ZIP contains all 650 supporting files, the original
receipt, source inputs/proofs/references and the exact standalone checker source.
Saved checking requires no TopoMT, DFND, NumPy or PyUnitWizard installation.
It is not an installed package or a supported public API.

Test-first development reproduced the missing panel driver before implementation.
The 244-test source selection passes, including fresh worker/resource-deferral/
timeout controls and all earlier scientific evidence guards. Mypy checks all
28 validator modules with Python 3.11 syntax/actual 3.14 dependencies. Bundle
guards additionally check every byte/profile/scope/resource, plus isolated
dependency-free tetrahedron and narrow-tube saved replay. All 355 earlier
frozen case files remain unchanged.

The final selection passes **247 tests** (244 source controls plus three retained
bundle/replay guards), in 26.22 seconds with peak RSS 96,184 KiB, one CPU and
2 GiB. Ruff/format, mypy on 28 source modules, report indexes, offline comparative
metadata and 323 local Markdown file targets pass. Published decimal volume
endpoints were checked to round outward from the exact rational bounds.

The complete Sphinx HTML build passes with zero warnings, notebook execution
disabled and one worker (16.08 seconds, child peak RSS 274,808 KiB, 2 GiB cap).
The legacy Python prefix lacks a PlantUML executable; its initial build attempt
stopped on that missing tool. The successful build explicitly uses the existing
`topomt-dev/bin/plantuml` with bounded Java settings, without installing or
changing shared prefixes. The new report's 139 local HTML targets are valid;
all five downloads match their source bytes. This is local rendering, not hosted
deployment, installed-release or complete-environment qualification.
The final report-text update also passes the incremental build (5.02 seconds,
child peak RSS 256,824 KiB); the subsequent twenty-test receiving/governance/
original-artifact selection passes as well.

Full P5 qualification remains open: executing all nineteen selected query sets
does not supply the missing P1/P3 exhaustive mixed-region construction, clipped
subdivision, boundary/separation and P4 per-region precision. Native #181 and
#180/#184/#188 keep their dispositions. No new geometry family, protein phase,
original provider, public-release or comparative-superiority claim follows.
