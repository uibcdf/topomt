---
summary: Add a model-audited original-method comparison stage for the regular tetrahedron.
issue: uibcdf/topomt#141
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [dfnd, third-party, docs]
guard: tests/test_tetrahedron_comparisons.py::test_original_comparison_recovery_is_engine_free_and_retains_spatial_meaning
normative:
blocked_by: []
supersedes: []
---

# Regular tetrahedron original comparisons

## What

Resume the first synthetic BenchLab unit after the original-provider batch and
MOLE follow-up. Add the separate comparison notebook anticipated by #134,
preserving all earlier notebook/input/reference/evidence bytes.

## How

Recheck the adopted references, freeze a versioned protocol before new original
topography executions, then run available selected local routes sequentially
under explicit resource limits. Ordinary notebook execution reads and verifies
the retained evidence without original engines or any service submission.
Separate default observations from predeclared small-system controls, current
execution from historical evidence, and absence/failure/pending from zero output.

The receiving selection passed 18 native/reference/notebook/evidence guards
in 2.32 seconds on Python 3.14.10. The four-ball input still has edge 5.3
angstroms and explicit atomic radii 1.7 angstroms. The PDB encodes neither those
radii nor full-precision coordinates. Original pyKVFinder read_pdb assigns
generic carbon radius 1.66 angstroms to DUM/C; maintained MOLE uses its original
tunnel-specific carbon radius 1.61 angstroms. Matching coordinate files alone
therefore does not match the reference atomic-ball model. Preserve original
defaults and document these differences before interpreting counts.

## Why

The first controlled geometry can reveal input-model and reporting differences
without asserting molecular relevance or tuning DFND to another engine. It also
tests whether the original-provider workflows are useful for reproducible study.

## What was refuted

PDB carbon labels do not impose the native 1.7 angstrom radius on every engine.
A completed empty collection, an input-domain failure and a pending server job
are different observations. A learned protein binding-site prediction does not
supply independent geometric truth for four dummy carbon balls.

## Scope and exclusions

One synthetic input version, a model/input audit, selected original local
observations and their comparison notebook. Historical observations are retained
at their original scope; no remote coordinates are submitted. Native scientific
code, installed/public qualification, solvent-volume precision #75, the full
independent reference panel #76 and protein studies remain separate.

## Acceptance criteria

The frozen protocol, exact original artifacts or diagnostic receipts, effective
input/radius evidence and quantity-aware report are linked from an executed
comparison notebook. Engine-free reading checks integrity, statuses and matching
source context. Meaningful guards cover the radius/rounding distinction and
evidence lifecycle. Reviewed plots and rendered documentation support the stated
interpretations without a cross-method accuracy ranking or superiority claim.

## Resolution

The separate `comparisons.ipynb` executes seven code cells in a fresh Python 3.14
kernel, with two reviewed figures and a quantity-aware comparison report.
All previous notebook/input/native/provider artifact bytes pass their preserved
hashes. Ordinary execution verifies and reconstructs accepted originals only,
without original engines or server contact.

The original fourteen-row protocol was committed at `59bc96c` before executing
the selected local methods. GHECOM reports one 263-point region for its 1.2 Å
small-system control and empty results for standard/1.4/1.7 Å. pyKVFinder is empty
at defaults; its three zero-cutoff controls export inconsistent descriptor/grid
labels. CAVER's original origin/shell diagnostic and MOLE's four-atom null
reference remain failures, not invented empty results. Their four remaining
controls stop according to the protocol. Effective GHECOM/CAVER DUM radii remain
unverified; input-model equality is not asserted.

The original pyKVFinder zero-cutoff export has 1352 volume entries, 1351 of them
zero, while only one label occurs in the PDB. The original warns of 6112 cavities
exceeding label capacity. A separately declared one-voxel positive-cutoff
diagnostic was committed at `a8065a7` before its execution; all three then yield
one consistent region, with extensive support outside the finite atomic-centre
hull. The notebook distinguishes the original labels/objects from DFND's native
residence reference, without a count/volume/performance score.

The initial study-driver stopping bug is fixed and covered by an analytical
workflow guard; its first original files are retained unchanged. The observed
shared receipt-state defect is independently fixed and archived under #142.
The suspected upstream cutoff limitation is retained in
`devguide/pykvfinder/zero_cutoff_diagnostic.md`, with a concrete report awaiting
separate external-publication authorization; the earlier #222 authorization was
for packaging only. This disposition does not block the comparison notebook.

Final relevant source/reference/receipt/parser/MOLE/governance selection: 103
cases passed in 19.12 seconds on Python 3.14.10, one OS CPU. Ruff passes for the
repository and focused mypy passes for four changed source/test files. Full
documentation HTML builds with the same twelve pre-existing warnings and no
new warnings; the rendered comparison has audit tables, original diagnostics
and both figures. Source qualification is bounded: no full suite/matrix,
installed-package or public-delivery claim is made (#16/#19/#81 remain owned).

Temporary resources: required original evidence is committed. Task-owned logs,
timing receipts and the isolated documentation preview remain under the ignored
`.cache/tetrahedron-comparisons/` for review through this checkpoint. Its redundant
initial-attempt copy and copied docs source can be removed after verifying the
committed copies; existing MOLE/third-party tools remain for reproduction, with
their previous owners/retention unchanged. No shared environment or unrelated
temporary directory was modified or removed. Both bounded original drivers
briefly overlapped on the same single CPU; measured peak process RSS stayed below
268 MiB and no memory pressure was observed. Wall times are not serial benchmark
evidence. Native scientific code and #75/#76 remain unchanged.
