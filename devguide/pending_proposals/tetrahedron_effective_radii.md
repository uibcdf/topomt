---
summary: Resolve effective GHECOM and CAVER input radii in the tetrahedron study.
issue: uibcdf/topomt#143
status: active
opened: 2026-11-08
closed:
severity: medium
verification: inspected
area: [dfnd, third-party, docs]
guard:
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
