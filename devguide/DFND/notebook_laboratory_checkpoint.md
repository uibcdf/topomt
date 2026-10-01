# DFND notebook laboratory checkpoint

## Active direction

The user selected case-by-case native-method development and validation on
2026-10-01. The selected-frame context groundwork is delivered; extending the
public support architecture is no longer the immediate next task. DFND's richer
residence, transit, region, gate, exterior-link and dry-network information is
the object of study. Pocket outputs are one comparison lens.

Each study is a Jupyter notebook that can later serve the public documentation,
benchmark compendium and method demonstrations. The current sources live in
`docs/content/showcase/dfnd/`; the existing MyST-NB/Sphinx documentation path
renders reviewed outputs with execution off. No separate website deployment or
new provider integration is part of this first slice.

## Delivered first case

`regular_tetrahedron.ipynb` studies four equal-radius atomic balls, edge 5.3 Å,
radius 1.7 Å, no jitter and no periodic boundary. Versioned `input.json` uses
PyUnitWizard QuantityRecord for dimensional values; `input.pdb` is the original
provider submission. The observation report links both by SHA-256.

Independent circumradius formulas establish residence and face clearances; the
finite tetrahedron formula establishes hull volume. Tolerances are fixed before
execution: clearance absolute tolerance 1e-6 Å with zero relative tolerance,
hull-volume relative tolerance 1e-12. These checks do not certify a solvent
volume estimator's precision. The notebook explicitly retains the minimal
component with `min_size=0`.

Probe anchors 1.2, 1.4 and 1.7 Å distinguish a resident percolating cell, a
resident sealed void and no resident wet component. Four permeable exterior
faces form one exterior-link cluster at the first anchor. An 81-point probe
sweep, input geometry figure, independent tests and quantity-aware report make
the observations reviewable. A rigid-motion test additionally protects the
clearance reference.

Original fpocket is invoked through TopoMT's CLI provider route, with default
settings and the exact downloadable PDB. Its outcome remains separate from
native acceptance. The observed fpocket 4.0 run exits with code 1 because its
reader reports no atoms in this dummy HETATM/DUM structure. It is recorded as
`execution_failed`, with no pocket count, rather than interpreted as zero
pockets. This establishes an input-domain limitation for this comparison; it
does not establish native superiority or a provider defect.

The PDB rounds coordinates to 0.001 Å and cannot preserve explicit atom radii.
The notebook measures that discrepancy and reports DFND primitives on the
rounded input with the original explicit radii. The reference remains the
full-precision quantity-aware input; provider radius semantics remain its own.

Local execution used pinned DepDigest 0.12.0 from canonical tag commit
`0da46d9ff31fbe2f92e4e667a32868aebe840b39` in an isolated `/tmp` target. The
active editable sibling is older than TopoMT's declared minimum. No sibling
checkout or Conda environment was changed. Reports record imported versions
and the executable checksum without personal filesystem paths.

## Rules for adding a case

1. Freeze coordinates, radii, query/probe, units, tolerances and reference
   assumptions independently of observed engine output. Give the case a version.
2. Explain which ideal-shape expectations actually follow from the discrete
   union-of-balls model. A sampled shell is not a continuum shell. Generated
   catalog labels and a green implementation test are not independent oracles.
3. Inspect the input and raw results visually. Separate resident regions,
   transit, external links, geometric estimates and public reporting filters.
4. Vary one model/query parameter at a time. Distinguish physical topology
   changes, numerical errors, algorithm errors and unresolved references.
5. Run original providers when their input domains permit it. Preserve exact
   submitted inputs, settings and original outputs when execution completes;
   preserve an explicit unavailable/failed state otherwise. Never silently
   substitute a TopoMT reproduction or require peer agreement.
6. Execute from a fresh kernel. Retain reviewed outputs and a versioned report;
   reruns must not overwrite the frozen input/report. Add meaningful independent
   regression guards for the adopted claims. Verify the public rendered page.
7. Only then change the engine for a reproduced, understood defect. Record what
   the case supports and what remains unresolved, rather than turning plausible
   construction labels into assertions.

## Second adopted reference and multi-provider comparisons

`closed_shell.ipynb` freezes 72 atomic balls near a 6 Å sphere, atom radius
1.7 Å, spacing 2.5 Å, jitter 0.06 and seed 20261001. Its independent certificate
covers every triangle of the convex-hull boundary with the probe-expanded
atomic balls at 1.4 Å; the origin is free and inside the hull. This proves at
least one bounded probe-center region containing the origin, not the exact
global cavity count. The face covering radius is 2.029530723 Å and the margin
is 1.070469277 Å. Native barycentric containment identifies the central finite
cell and its sealed resident component: 33 nodes, no exterior links.

The 49-point sweep and three figures expose raw states and peer representations.
Bare-free-volume bounds concern total free space restricted to the finite hull;
they do not certify closure of the unexpanded balls or the numerical accuracy
of the native estimate (501.680510065 Å³).

Both notebooks invoke original fpocket 4.0, Pocketeer 0.4.0, AlphaSpace2 0.1.2
and pyCASTA 1.0.8 on a disclosed ATOM/DUM compatibility export. Pocketeer
completes with zero pockets for the tetrahedron and one for the shell;
AlphaSpace2 completes with one shell pocket. Original bundles are retained.
fpocket and pyCASTA fail on both inputs; AlphaSpace2 fails on the tetrahedron.
Failed runs retain causes and no pocket counts. pyCASTA reaches an upstream
tuple/dictionary mismatch after its tetrahedron filter eliminates all cells.
fpocket's shell malloc message is not diagnosed as physical memory exhaustion.
The shell's Pocketeer voxel volume (931.75 Å³) and AlphaSpace2 alpha-space
volume (91.023872376 Å³) have different definitions from DFND's estimate.

The [server-input audit](../castp/server_input_contract_2026_10_01.md) records
the existing CASTp clients and current web requirements. CASTp 3.0 rejects both
uploads before returning a job ID. CASTpFold accepts an atom-name-aligned HETATM
export for both cases; its jobs remain `submitted_pending` at the last recorded
poll. This is not a completed CASTp comparison. Cached evidence retains exact
submitted files, dates, settings and identifiers; notebook reruns do not upload.

## Pause boundary and remaining gates

The user requested a pause after these two examples and their original-provider
comparisons. Do not start opening, tube, neck or engine-tuning work automatically.
The local comparison tranche is reviewed; obtaining and interpreting the two
existing CASTpFold jobs remains unresolved. Resume those job IDs before any
new submission, and preserve the input/radius-model limitations.

Issue #76 remains open: these are two independent controls, not the full panel.
Issue #75 remains open: volume precision and uncertainty require their own
validation. Issue #60's remaining public support/provenance work is pending and
does not block this scientific study sequence. Continuous probe navigability,
biological generalization and publication-scale benchmarking are not delivered.

Guards: `tests/test_dfnd_regular_tetrahedron_reference.py`,
`tests/test_dfnd_closed_shell_reference.py` and
`tests/test_dfnd_benchmark_provider_evidence.py`. The executed notebook
is a separately run integration/documentation check; ordinary pytest does not
invoke an optional executable or rerun the entire notebook.

Local verification: 84 reference, evidence, primitive, query, synthetic and
reporting tests pass with Pytest Receptor, including under the exact controlled
PyUnitWizard feature source `23554a7aca31cba144ef248b9771d4668815dd1c` installed
in an isolated target. That pin corrects the first notebook's matrix collection
failure: the older controlled source lacked QuantityRecord. Its codec remains
provisional; public notebook instructions identify this development requirement.
The documentation build succeeds with eight existing warnings. Full matrix
evidence remains under #16 and must be assessed at the published revision.
