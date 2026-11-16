# Expanded analytic verification panel

Owner [TopoMT #76](https://github.com/uibcdf/topomt/issues/76), selected S8
continuation. Base source: `e7a3052d949f207241e602bea3728d43427aca20`.

The frozen `plan.json` selects all nineteen original numerical profiles and
twenty-five existing analytic controls. Each runs in a fresh process in direct
serial and explicit two-worker configurations. The small tetrahedron 1.4 Å
profile has three fresh repetitions in each mode; larger profiles have one
observation per mode, not repeatable/general scaling evidence.

This is complete **saved-proof verification**: exact Model/certificate reading,
independent complete topology/frontier reconstruction, certified integration,
canonical reduction, saved work and final Model/certificate/result publication.
The original untrusted symbolic certificate contains no accepted volume or
region assignment. All mathematical output is compared with the frozen original.
It does not rerun proposal generation or qualify full nineteen-profile paused
source construction. Those operations retain the earlier S6/S7 source scopes.

One further fresh serial saved read per profile checks every configuration
against the same reference. It independently recomputes geometry/arithmetic
once, after confirming all saved inputs agree and checking their storage hashes.
That shared read is measured once; do not count it as independent repeated runs
or silently charge it separately to both modes. Partial arithmetic has no whole
volume claim. Exact exclusions can use the checked zero-volume shortcut without
launching numerical workers, even in the two-worker configuration.

Every successful monitored command has at most two explicitly allowed CPUs,
2 GiB parent AS, 300/330 CPU-second ceilings and a 420-second external deadline.
Pools use 256 MiB per worker, a total 120 CPU-second allowance divided across
workers, at most two outstanding tasks and at most 512 new pieces per pool.
Host reserves are checked; observed free RAM is not reserved. Five-second group
RSS can miss peaks and double-count shared pages; short tetrahedron runs cannot
resolve pool memory. No Slurm/GPU/multi-machine or new external engine is used.

The current method/source, requests, units and all original frozen inputs remain
unchanged. The receiving keeps native #181/#180/#184/#188, canonical #76/#60,
remaining S1/S3/S5 and broader S8/P6/P7/installed #16 gates separate.

Status: **completed at the selected saved-proof verification scope —
2026-11-16 UTC**. All **92 solve configurations and 44 shared serial reads pass**;
every mathematical field and precision status equals its frozen original.
Thirteen positive original profiles contain sixteen regions; six profiles are
exact zeros. The [complete phase table](table.md) retains all nineteen profiles.

The sum of bounded command elapsed is **3700.203 s** and waited CPU is
**3870.938 s**, including controls and each shared read once. Peak sampled group
RSS is **106.79 MiB**; peak individual-process RSS is **53.66 MiB**. These totals
exclude source freezing, scheduling gaps, packaging and test/build costs.
`receiving_index.json` maps protocols, configuration results, numerical/geometry
phases and resources. The capsule preserves all exact inputs and working JSON
at their repository-relative paths, all 51 source modules and the independent
worker script. Duplicate working trees are removed only after archived byte
verification; external protocols/resource records and raw logs remain visible.

`package_attempt1_execution.json` retains a packaging failure with observed exit
`-24` (SIGXCPU on this Linux host) at its 45-second per-process CPU ceiling.
The first packaging driver unnecessarily rebuilt exact Models to print probe
labels. The revised driver reads the already-validated rational probe fields;
packaging succeeds in 11.473 bounded seconds with unchanged science records.
Both driver versions and the failed raw records are retained. This failure is
not a scientific or precision failure and is excluded from the solve table.

The 19 selected receiving/report/DFND-example tests pass, including fresh reading
from the extracted capsule under Python `-S` and the declared blocked-import
policy. Source/Ruff/mypy/report/Sphinx checks and preservation receipts are in
`source_qualification.json`; `MANIFEST.json` binds this evidence tree. Earlier
source qualification remains reusable only while its exact code hashes match;
this delivery changes no executable validator module. The original 355 frozen
files, earlier evidence trees and human version edit are preserved.

The three small-profile repetitions establish the observed process overhead,
not larger-case repeatability or a general benefit from more CPUs. The
maintainer's resource question is handled as a separate bounded four-worker
assessment gate under #76; **all runs here retain their frozen one/two-CPU
conditions**. The eight-stage plan remains partial at its wider scope.
