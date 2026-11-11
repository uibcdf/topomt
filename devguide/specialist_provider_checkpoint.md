# HOLE, POVME and PISA source checkpoint

Date: 2026-11-11. Integration owners: #192, #193 and #194. The maintainer
selected these three external engines and clarified the adapter-only boundary:
their scientific algorithms stay in external projects. Compatibility forks are
separate repositories, not native implementations copied into TopoMT.

## Exact sources and acquisition

| Engine | Source identity | Observed boundary |
| --- | --- | --- |
| HOLE | `osmart/hole2@a8eaf6121ba66625446933f4acd7d6aa336dbb47`, clean `~/repos@others/hole2`; program 2.3.1 | Apache-2.0 original executable, explicit spherical steering/radius model. |
| POVME | Modern `durrantlab/POVME@8a9f1973c25eb52e36e0d7b20183bf896cb66729`; compatibility fork `uibcdf/POVME@0c55f591dea3156e1ca76a486cf1f71d56c3a192`, branch `compatibility/python314-serial` | Version `2.2.2+uibcdf.1`, separate clean `~/repos@others/POVME-uibcdf`; original consultation checkout remains unchanged. Modern source differs from the historical tag called 2.2.2. |
| pymolecule | Original `durrantlab/pymolecule@614a95a0b792f83fbee77e4c7eed7d5ce046dee1`, clean detached `~/repos@others/pymolecule` | Original POVME dependency source, version 0.0.1. |
| PISA | `PDBe-KB/pisa@6d6f7d09ea5bf0f3f8a1602dd56fa896e6aca401`, clean `~/repos@others/pisa`; program 2.1.2 | Externally acquired executable and SRS/MolRef/PISA resources; supplied-assembly `--as-is` analysis. [Availability/licence review](pisa/license_review.md) keeps intended local use/free academic acquisition distinct from unconfirmed standalone redistribution terms. |

The POVME fork changes packaging, version metadata, optional Ray bootstrap and
bounded worker defaults. Fourteen scientific/support Python modules and three
original serial task methods retain their source bytes, guarded by separate
SHA-256 inventories and five compatibility tests in the fork. Pydantic/Loguru
keep their original minimums without unverified upper limits. README/LICENSE
explicitly grant GPLv3-or-later; fork metadata follows that grant rather than
the contradictory Apache field. The historical Pixi lock remains archived
outside its active root. Pixi solving and Ray execution are unqualified.

The original HOLE source was copied to a task-owned build directory and built
serially with the supplied Conda Fortran compiler and legacy compatibility
flags. Build: 163.14 s, peak child RSS 735116 KiB. Original PISA's compile script
ran in a separate copy with tracked precompiled headers excluded; scientific
source remained unchanged. Build: 34.16 s, peak child RSS 121348 KiB. No engine
source, executable or PISA runtime dataset is added to the TopoMT package.

## Scientific/result contracts

- [HOLE](hole/overview.md): one original path in `channels`, sampled and
  midpoint profiles separately, signed distances/clearances, original minimum,
  rounded sphere centers and no artificial end extensions or swept-volume claim.
- [POVME](povme/overview.md): one analyzed frame/ROI in `regions`, including
  evaluated zero. Preserve original volume, hull/cutoff/connectivity settings,
  and reported versus unavailable point support. No automatic cavity detection.
- [PISA](pisa/overview.md): pairwise `interfaces`, two participant sides,
  original contact groups and exact contact-atom source mapping, plus the
  supplied-assembly summary. Other-contact atoms and buried-area atoms differ.
  No biological classification or assembly prediction is inferred.

Each route uses ArgDigest option/group admission, selected-command DepDigest
checks, SMonitor failures, fixed physical protocol units through PyUnitWizard,
and the shared source/frame/selection/reference-chemistry capture. The readers
validate captured inputs, original query/result consistency and source mapping;
they never reopen producer-machine resource paths. These checks establish
integrity and consistency, not authentication of a producer's declarations.

## Original execution and retained evidence

The seven initial original gates passed in **11.10 s**, runner wall 12.706 s,
peak parent RSS 291868 KiB. They cover two HOLE radius resources (custom uniform
argon control and recognized AMBER carbon control), PISA contacting/separated
synthetic four-residue chains, and POVME positive/zero/outside-ROI branches.
Direct public-engine calls agree with the adapters on these controls. Saved
reading retains detached original bibliography and needs no engine execution.

HOLE's 77-atom control retains 67 sampled and 66 midpoint evaluations; 200
artificial visualization rows and the repeated origin are excluded from path
geometry. PISA's positive control reports 125.73203716 Å², 24 other contacts,
28 contact atoms and 20 buried-area atoms. These sets are deliberately distinct.
POVME's positive control reports 330 Å³. An original outside-ROI early return
reports volume without writing the surviving-point PDB; availability remains
explicit rather than becoming empty geometry.

POVME's measured worker uses Python 3.14.10, NumPy 2.5.4, SciPy 1.18.1,
Pydantic 2.14.3 and Loguru 0.7.3, without Ray. A direct small calculation took
0.050 s after imports, peak worker RSS 85664 KiB. These are bounded receipts,
not representative performance or accuracy benchmarks.

Raw controls and source-bound bundles live in `tests/data/original_local/hole/`,
`povme/` and `pisa/`. Their READMEs describe inputs, resource models and limits.
`tests/test_specialist_original_execution.py` is the explicit installed/source
gate; requested missing commands fail. Protocol/recovery/optional-recorder
controls remain separately labelled and cannot replace original execution.

The declared original gate uses `TOPOMT_HOLE_CMD`, `TOPOMT_PISA_CMD`,
`TOPOMT_PISA_HOME`, `TOPOMT_POVME_ROOT` and `TOPOMT_PYMOLECULE_ROOT`. An optional
`TOPOMT_SPECIALIST_EVIDENCE_DIR` retains fresh captures. Execute sequentially,
with one numeric thread and a conservative memory/time limit. Task receipts
remain in `.cache/hole-povme-pisa/`; the committed fixtures/checks retain durable
evidence after that cache is removed.

## Attribution and remaining scope

The original HOLE banner requests Smart/Goodfellow/Wallace 1993. Its recognized
AMBER resource additionally credits Weiner et al. 1984, with the original
resource's incorrect page ending corrected against publisher/Crossref metadata.
Custom radii do not earn that data reference. POVME requests its 2011 and 2014
papers; the executed compatibility fork has its own version and software URL.
PISA credits the 2007 original and 2026 enhanced-interface descriptions. Full
offline records were verified against primary articles and Crossref. Saved
reading earns no new execution credit. Optional absence/failure preserves the
scientific result and host-owned bibliography.

## Final source validation — 2026-11-11

The coherent five-module specialist selection passed **87 tests in 34.18 s**
(runner wall 35.617 s, peak parent RSS 296652 KiB). Thirteen designated gates
execute the actual external engines: the seven successful direct/adapter
controls, three original failures and three fresh executions with Ackredit
genuinely blocked. Failed captures retain the attempted executable/interpreter,
controls and diagnostics without awarding completion credit. Recovery tests
exercise non-default unit policies, source/input/query conflicts and fresh
readers blocking engine, dependency and recorder imports. Explicitly labelled
replay controls test optional recorder failure without claiming new original
execution. Numeric type/unit corruption and an unbacked NPY allocation request
are rejected by saved readers.

The selected existing-provider/governance regression passed **401 tests in
29.67 s** (wall 31.203 s, peak parent RSS 353372 KiB), including MoloVol, MOLE,
saved workflows, shared persistence, dispatch, attribution, environment and
report/finding checks. Ruff lint/format and scoped Mypy passed; the latter checks
26 source files at Python 3.11 and 3.14 static targets, not two runtime matrices.
Four existing MoloVol original/direct gates additionally passed in 23.03 s
(wall 24.563 s, peak parent RSS 289964 KiB). Their first sandboxed attempt
failed to bind Xvfb's own temporary sockets; the bounded repeat outside that
restriction passed, without changing host permissions or other users' displays.
All runs used one CPU/numeric thread with 6 GiB address-space and 120 CPU-second
ceilings. Available memory exceeded 54 GiB with zero sampled swap I/O and zero
memory pressure; resources were not assumed reserved. `sbatch` was present but
there was no allocation; these bounded checks ran directly on the shared host.

Live readback covered all ten registered finding cards and ten linked issues;
the normalized snapshot passed the lifecycle checker. The new
`povme-empty-initial-region` card stays `needs_review`, linked from the review
queue, method summary and open #195 / UIBCDF/POVME#1. The independent empty-domain
argument does not establish a matched DFND comparison or provider correction.
This operational observation is not a present-tense geometric inferiority claim.

The 392 frozen study/history/human-version files match their pre-task hashes.
The human `topomt/_version.py` edit is preserved and excluded from commits.
Full suite, coverage, supported-runtime/platform matrix, installed/public package
qualification and hosted documentation deployment remain under #19/#101/#16;
these focused checks do not clear them. The source documentation build and
closure receipts are recorded separately after the committed candidate exists.

Broader reviews remain #161 (HOLE/CHAP), #159 (POVME/PyVOL) and #165
(PISA/PePrMint, including unresolved standalone redistribution clarification).
Original field/route fidelity remains #19; installed/public delivery and the
support matrix remain #101/#16. Full-suite/coverage/hosted CI evidence is not
established by these focused source gates. Incremental commits use `[skip ci]`.
No coordinates were submitted remotely, no new BenchLab comparison or native
DFND protein characterization was performed, and the existing frozen study
bytes and human version edit remain outside this delivery.
