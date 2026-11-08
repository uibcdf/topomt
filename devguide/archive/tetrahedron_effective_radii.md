---
summary: Resolve effective GHECOM and CAVER input radii in the tetrahedron study.
issue: uibcdf/topomt#143
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [dfnd, third-party, docs]
guard: tests/test_tetrahedron_effective_radii.py::test_original_reader_assignments_reconstruct_without_engines
normative:
blocked_by: []
supersedes: []
---

# Tetrahedron effective-radius audit

## What

The #141 comparison deliberately left GHECOM/CAVER effective DUM/C assignments
unknown. Resolve this small input-model question using original code and output,
while retaining every earlier scientific artifact and notebook byte.

## How

Freeze a four-row paired audit: the existing ATOM export and a separate variant
changing atom-name columns only from `C   ` to ` C  `. GHECOM's documented
`-opdbin` export places assigned atomic radii in occupancy; use its unchanged
P-mode executable with original defaults, retaining all files but interpreting
only this input-model export. This is two tiny runs, not a repeated probe sweep.
For CAVER, a small Java caller uses the original public PeriodicTable,
PdbFileFactory and Atom APIs, matching CalculationSettings' one-argument factory
and default removeAltConf=true. It does not run tunnel calculation or reproduce
radius rules. Retain exact jar/table/helper identities and original stdout.

Source inspection predicts GHECOM's generic fallback versus aligned-carbon
pattern sensitivity; these are hypotheses until original outputs verify them.
CAVER's CSV carbon row alone remains insufficient evidence. Its inspected
bytecode confirms the actual default reader route and angstrom conversion.

## Why

Coordinate identity and carbon names do not ensure equal atomic-ball models.
The current uncertainty is input parsing, not evidence of a DFND kernel error.

## What was refuted

No historical output can be changed to match a new alignment. No new geometry,
probe tuning, source change, full comparison sweep or protein study is needed.

## Scope and exclusions

One frozen four-atom case and two original readers, with an explicitly separate
name-alignment diagnostic. TopoMT public adapters/scientific kernels, #75/#76,
installed/full-matrix qualification and pyKVFinder upstream #223 stay separate.

## Acceptance criteria

Versioned protocol/effective-radius report, original captures, source/command
identities and dimensional values. Meaningful engine-free guards preserve the
old case, verify raw assignments and isolate the name-only perturbation. A short
public follow-up explains original observations and independent geometric
implications, without treating a radius match as full method equivalence.

## Resolution

The protocol and original-reader Java caller were frozen at `6808516`. All four
original calls complete: GHECOM 2026/08/17 assigns 1.87 Å to each atom and
CAVER 3.02's default reader assigns 1.70 Å. Atom-name alignment leaves both
numerical assignments unchanged. All 91 prior case notebook/data files pass
their preserved hashes; no original comparison artifact or native code changed.

The assumed 1.50 Å fallback from an illustrative Radius.c comment was refuted:
the actual included table ends in a 1.87 Å fallback. Both the table and original
export establish the current value. This highlights why comments alone do not
qualify an atomic model. The 1.87 Å rounded-PDB ball model has face clearance
1.190229 Å and residence clearance 1.375863 Å. Its independent 1.2/1.4 Å probe
regimes therefore differ from the native 1.70 Å reference before considering
operator differences. No detector prediction or score is inferred from that fact.

The first receiver attempt failed after GHECOM successfully exported radii:
general MolSysMT reading rejected its nonnumeric REMARK fields. The exact first
attempt and failure receipt are retained. MolSysMT #654 owns compatibility and
diagnostic triage for clean source `2325038e8c68157f5c730693ffbb8535f0b45540`;
the existing `component:topomt` label was applied only to that issue after the
canonical read-only label audit. No repository-wide label synchronization or
sibling source edit was performed. The corrected receiver reuses TopoMT's
existing original-provider point reader; standard molecular input coordinates
still use MolSysMT. Its analytical metadata regression failed before that change
and now passes. Scientific radius rules are not copied into TopoMT.

`atomic_models.md` publishes the paired assignments, independent implications,
all five original/initial-attempt capsule downloads and reproducibility route.
`artifacts/radius_audit_v1/` includes quantity-aware report and receipt, exact
actual inputs, original exports/logs and original CAVER table/caller. The serial
paired run took 3.74 seconds, with maximum observed process RSS 154664 KiB;
one OS CPU, 4 GiB address-space ceiling and 128 MiB Java heap were used. These
are receipts, not comparative performance evidence or resource reservations.

Verification: 36 affected audit/reference/notebook/provider-evidence/reporting
cases pass on shared Python 3.14.10. Repository Ruff and focused two-file mypy
pass. Full documentation HTML builds with the same twelve existing warnings,
no new warnings, and all five capsule download paths verified. No full
suite/matrix or installed/public delivery claim is made; #16/#19/#81 retain
those gates. #75/#76, upstream #223 and certified-shell/opening work remain
separate. No new dependency, public provider API or attribution boundary changed.

Temporary resources: exact required inputs, original bytes, capsule manifests
and measurements are versioned. Task-owned compile/inspection/check logs and
the rendered preview remain in ignored `.cache/tetrahedron-radius-audit/` for
maintainer review of this checkpoint; they may be removed after that review.
The redundant copied documentation source can be removed after publication.
Java build classes used a managed temporary directory and were cleaned on both
the failed and completed receiver attempts. Shared environments, original
engine checkouts and unrelated resources were not modified or removed.
