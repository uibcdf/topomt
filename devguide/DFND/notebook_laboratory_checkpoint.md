# DFND notebook laboratory checkpoint

## Active direction

**2026-11-08 refinement:** the maintainer requests deeper study of the existing
three units before adding a tube. Follow [the three-case deepening plan](three_case_deepening.md).
Audit the actual public `Topography` projection, resolve the historical 0.2 Å
wall reference, then study physical mouth/path connectivity, volume accuracy,
native dry structures and robustness. Earlier suggestions below to move next
to a tube are deferred by this decision; initial passing anchors are not the
completion rule. #146 owns the bounded public audit, #148 the 0.2 Å cover;
#75/#76/#60 retain their broader numerical/scientific/public-support gates.

The user refined the publication target on 2026-11-07: a
[study and benchmark area](study_zone.md), with one named unit per system,
DFND observations and original third-party comparisons. Case identities use
descriptive names without numbering. The same reviewed sources should serve
documentation integration and a future standalone site. This extends the
existing laboratory rather than creating a second evidence collection.

On 2026-11-07 the user explicitly resumed native DFND development, following a
fresh reading of code/devguide and the MOLE comparison. The working order is
**one synthetic case at a time, then proteins after the synthetic phase**.
This supersedes the previous two-example pause and real-system-first ordering.
The priority is characterization-driven development: an understood case motivates
the next bounded change, followed by regression checks of adopted earlier cases.

The user selected case-by-case native-method development and validation on
2026-10-01. The selected-frame context groundwork is delivered; extending the
public support architecture is no longer the immediate next task. DFND's richer
residence, transit, region, gate, exterior-link and dry-network information is
the object of study. Pocket outputs are one comparison lens.

Each study unit contains Jupyter notebooks that can serve the public documentation,
benchmark compendium and method demonstrations. The current sources live in
`docs/content/benchlab/synthetic/<case>/`; the existing MyST-NB/Sphinx documentation path
renders reviewed outputs with execution off. No separate website deployment or
new provider integration is part of this first slice.

BenchLab is a top-level documentation section, with Synthetic systems and the
planned Molecular systems collection. The initial relocation kept each notebook
as `index.ipynb` with its original versioned artifact directory; #134 below
records the subsequent split of the tetrahedron unit. The 2026-11-07
relocation under #133 preserves scientific cells, reviewed outputs and artifact
bytes; earlier Showcase addresses retain relocation links. Source layout changes
do not constitute another scientific execution or qualification.

### Current sequence and completion rule

1. Re-anchor the regular tetrahedron: independent residence/gate values,
   threshold regimes, exterior contacts, volume definitions and reporting.
2. Retain the sampled closed shell as the sealed negative control for access;
   its certificate proves an origin-containing bounded region, not every cavity
   or an exact empty volume.
3. Study a shell with an opening. Freeze the altered atomic-ball input and an
   independent all-atom access witness before examining DFND. A certified path
   establishes access; exactly one physical mouth requires additional evidence.
   Derive the opening from the frozen shell coordinates and preserve atom
   correspondence: regenerating jitter after deleting atoms changes the wall
   too, even with the same seed.
4. Continue with a tube and two chambers with a neck, then the remaining
   synthetic cases/variants for fragmentation, thresholds, unequal radii,
   degeneracy, dry boundaries, relief and interfaces as their questions arise.

For each case retain a versioned input, reference assumptions, fixed tolerances,
reviewed plots/raw supports, conclusions and meaningful regression guards.
Separate physical topology changes, local-model limitations, numerical defects,
reporting behaviour and unresolved references. An unresolved reference is not a
closed scientific case; a changed catalog expectation requires justification.
Review necessary variants before advancing rather than tuning to one example.

The synthetic phase completes when the selected case inventory and necessary
variants have reviewed dispositions and the claims needed for the protein phase
have passed their explicit gates. A catalog count or an all-green engineering
suite alone does not complete it. Protein annotations/generalization follow
this phase. Optional peer comparisons retain their own input domains and do
not gate progress on the native independent references.

The current 73-entry catalog is the initial inventory to reconcile case by case.
It includes the three surface morphology geometries and a disclosed historical
PDB alias: `pathological_thin_tube` has the same stored coordinates as
`pathological_thin_tube_r25`, with different encoding and preserved bytes.
The new entries have not received a new DFND characterization by registration.
The two adopted public controls use their own distinct frozen inputs. Record
unstudied entries and variants explicitly rather than treating the five initial
study themes as completion of the synthetic catalogue.

### Receiving check at resumption

At source `4229f60facfe64ce15310395e8efb588b43271b5`, the two adopted reference
modules passed **10 tests in 1.92 s** in the shared Python 3.14.10 workspace
with Pytest Receptor. Actual PyUnitWizard imports provide QuantityRecord; no
installation or historical temporary-prefix workaround was needed. This checks
the existing analytic/input/notebook guards without rerunning notebooks or
providers, overwriting frozen observations, or changing the engine. It does
not qualify new cases, volume precision, all synthetic cases or proteins.

## Delivered first case

### Three-case public receiving and 0.2 Å reference — 2026-11-08

Under the new deepening priority, #146 follows the actual public dispatcher on
the three unchanged atomic inputs. MolSysMT receives dummy topology from PDB,
then restores full-precision JSON coordinates; every vdW radius is checked
against the explicit frozen array. The opening selects parent atoms 6–71 from
the parent input. The received geometry/radii/map, catalog refinements, actual
Python classes, type/shape/dimensionality filters, Mouth relations, contextual
support identity, reporting suppression and valid empty outputs are guarded
under nm/ps and pm/fs policies. These controls use no mocked native engine.

The public results are `Percolating`/`Void`/empty for the tetrahedron;
`Channel` with ten `Mouth` children / `Void` / empty for the closed shell; and
`Pocket` with one `Mouth` / `Void` / empty for the opening. A public Mouth is
currently a discrete native contact cluster, not an independently validated
physical opening. Dry components remain under `topography.dfnd`; their public
convexity/interface promotion is not implemented. Complete neutral support and
classification provenance adoption remain #60.

#147 repairs three missing native length digesters discovered by real public
receiving, including argument-specific errors for invalid inputs. Explicit
quantities and finite nonnegative domains are checked without suppressing
missing-digester warnings. Legacy bare-number angstrom conversion and native
deprecation remain observable; no physical query or scientific kernel changes.

#148 strengthens the historical 0.2 Å closed-shell reference independently:
140 hull faces have a complete dyadic subdivision cover of 1037 leaf triangles.
Each leaf lies inside one original atom ball expanded by the probe, with
minimum vertex safety margin 0.000051742 Å against a 0.000001 Å requirement.
Convexity covers each full leaf; complete prefix-free four-way trees certify
the whole wall. The origin remains strictly interior and free. This resolves
origin enclosure at that probe, consistent with the existing native/public
Void. It does not establish an exact global cavity count or volume. The new
offline verifier never imports/calls DFND and rejects incomplete/wrong covers.

Protocol commit `3206fc6` precedes recorded public receiving and the retained
wall certificate; initial receiving tests, geometric preflight and historical
native labels were already known. This is retrospective characterization,
not blind validation. All 145 earlier scientific artifacts/notebooks retain
their protocol hashes. New case-local public pages/records and the independent
wall certificate extend rather than overwrite them. The original weaker bounds
and their inconclusive notebook outputs remain accurate historical records.

Next work stays on physical mouth-patch connectivity and compatible continuous
paths, then the tetrahedron analytic volume and #75 uncertainty/convergence
contract. Consult the deepening plan for explicit acceptance evidence. The tube,
other geometries and proteins remain deferred; #75/#76/#60 stay open.

### Effective-radius follow-up — 2026-11-08

Under #143, the [public input-model follow-up](../../docs/content/benchlab/synthetic/regular_tetrahedron/atomic_models.md)
resolves the GHECOM/CAVER assignments that were unknown at #141's checkpoint.
The four-row protocol and original-reader Java caller were committed at
`6808516` before execution; all 91 earlier notebook/data files retain their hashes.

Original GHECOM assigns 1.87 Å to all four DUM/C atoms, and original CAVER's
default reader assigns 1.70 Å. A separate variant changes only the name fields
from `C   ` to ` C  `; neither numerical assignment changes. GHECOM's included
table uses a 1.87 Å generic fallback even though an illustrative code comment
shows an older 1.50 Å value. Raw export, actual table and executable, rather
than that comment, establish the assignment. CAVER's default public-reader
constructor and flag were verified in original bytecode and invoked directly;
no tunnel calculation or copied radius logic is part of its audit.

These input models have different independent tetrahedron regimes. With GHECOM's
1.87 Å balls and rounded PDB coordinates, face clearance is 1.190229 Å and
residence clearance 1.375863 Å: a 1.2 Å ball fits inside but not through a face;
1.4 Å does not fit inside the finite cell. With CAVER's 1.70 Å assignment the
rounded-reference clearances are 1.360229/1.545863 Å, matching the earlier
nonmarginal native regimes. These are independent ball-model implications,
not detector predictions, new accepted cavities or proof of operator equality.

`artifacts/radius_audit_v1/` retains the protocol, separate aligned PDB,
quantity-aware report, original-reader capsules and receipts. The ordinary
engine-free guards verify raw radii/coordinates under nm/ps and pm/fs policies.
The original-reader run used one OS CPU, serial commands, 4 GiB address-space
ceiling and a 128 MiB Java heap; measured peak process RSS was about 151 MiB.
Neither frozen comparison notebook nor its original observations are rewritten.

The first audit receiver failed on GHECOM's nonnumeric REMARK metadata after
the original program successfully wrote its radius export. That attempt is
retained; [MolSysMT #654](https://github.com/uibcdf/molsysmt/issues/654) owns the
compatibility/diagnostic question. The corrected receiver reuses TopoMT's existing
provider-point reader for the geometric export and MolSysMT for standard input
coordinates. No sibling or original scientific code changed. #75/#76, #223,
installed/full-matrix gates and the next certified-shell study remain separate.

### Original comparison stage — 2026-11-08

Issue #141 adds `comparisons.ipynb`, executed in a fresh Python 3.14 kernel from
retained evidence, with two reviewed figures. It verifies input/model/protocol
hashes, reconstructs accepted outputs through the public source-bound readers
and inspects failed originals without engines, servers or overwriting artifacts.
All earlier system/native/historical notebook and evidence bytes remain unchanged.

The fourteen-row original protocol was committed at `59bc96c` before new detector
execution. Native radii 1.7 Å differ from original pyKVFinder fallback 1.66 Å and
maintained MOLE default 1.61 Å. PDB rounding crosses 1.4 Å face clearance for the
1.66 Å atomic-ball model; this independent implication is not a detector prediction.
Effective GHECOM/CAVER DUM assignments remain unknown rather than assumed equal.

GHECOM completes empty at defaults; its 0.4 Å-grid control reports one region
(263 points) at small probe 1.2 Å and zero at 1.4/1.7 Å. pyKVFinder completes
empty at defaults, but all three zero-cutoff controls export inconsistent
descriptor/grid labels. CAVER logs an origin/shell failure and missing tunnels;
MOLE reads four atoms then fails with a null reference. Their later controls are
skipped after failed standards, with no invented cavity/channel counts. P2Rank
is not selected for this dummy nonprotein system. Historical first-four/CASTp
observations are read separately; no CASTp job is polled or submitted.

A separately declared diagnostic (`a8065a7`) changes only pyKVFinder's volume
cutoff to one 0.2 Å voxel. All three runs then complete with one region, including
substantial support outside the atomic-centre hull. This supports cutoff
dependence and demonstrates why an original cavity label does not identify the
same finite-cell object as DFND. No count, volume or performance ranking follows.
The first driver attempt and its erroneous control stopping are preserved as
history; the corrected full planned set is explicit. #142 fixes the observed
invalid-result completed-receipt defect with analytical workflow regressions.

`artifacts/comparisons_v1/` retains all protocols, actual submitted PDBs,
original/failed bundles, source-bound receipts, diagnostic history, figures and
quantity-aware report. The case-specific serial reproduction tool accepts local
engine paths only and refuses to overwrite a result directory. Measured driver
peak RSS is below 268 MiB with a single OS CPU; brief overlap of the two bounded
drivers prevents interpreting their wall times as serial performance evidence.

The study/reference selection passes 26 cases, including source-bound engine-free
recovery under nm/ps and pm/fs policies. It does not modify a DFND scientific
kernel or complete #75/#76, the synthetic panel, installed delivery or proteins.
The next native unit remains the certified shell and its opening, following the
case-by-case reference gates above; unknown peer assignments do not supply new
independent truth or require tuning native geometry to a peer count.

Follow-up on 2026-11-08: after explicit maintainer authorization, the pyKVFinder
zero-cutoff reproduction and separately declared diagnostic were published as
[upstream #223](https://github.com/LBC-LNBio/pyKVFinder/issues/223). Exact posted
title/body were read back and verified. This hands off the suspected original
limitation; it does not claim an upstream fix or change the frozen comparison
artifacts, source kernel or the next native study.

### Split system and native study — 2026-11-07

The tetrahedron now has a short `index.md`, independent `system.ipynb` and native
`dfnd.ipynb`. They execute in separate fresh Python 3.14 kernels and share only
frozen input/reference files. Five system and ten native code cells execute
successfully, with two figures each. Independent/reference assertions, the three
nonmarginal probes, 81-point sweep and a reporting-filter control pass. The latter
retains a one-node raw void while `min_size=2` hides its compatibility projection.

New records and standalone figures live in `artifacts/native_study_v1/` within
the case directory. The historical combined notebook is retained byte-for-byte
as `historical.ipynb`, together with its unchanged original artifacts. A new
comparison notebook was pending at that increment; #141 adds the stage below.
No original provider or server was executed by #134. The following historical paragraphs
retain their earlier producer/evidence scope rather than describing a new run.

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

## Third adopted unit: exact shell opening — 2026-11-08

Issue #145 adds `shell_with_opening` as an exact subset of the adopted closed
wall. A strict 35-degree cap around +Y removes parent atom IDs 0–5, retaining
the remaining 66 coordinates/radii exactly. PDB rows retain serial/residue IDs
7–72. The public advanced constructor receives parent IDs through `atom_indices`;
raw local array offsets and mapped IDs are checked separately. Carrier-cell IDs
cannot be equated between the two retriangulated inputs.

The input/protocol commit `b6fe6e2` and independent system/reference commit
`2ca133d` precede first child native execution. Five independent-system code
cells establish an all-atom +Y ray clearance 1.819726044 Å, with conservative
cap bound 1.665782356 Å: both exceed the selected 1.4 Å probe. The same-probe
parent remains independently enclosed. The child's maximum hull-triangle
circumcover radius is 3.710130644 Å; 3 Å expanded balls cover that wall while
the origin remains free (clearance 4.168062464 Å). At 5 Å, the enclosing-ball
bound covers every finite-hull point. Bounds remain sufficient, with explicit
unresolved intervals rather than exact physical transition claims.

The separate native notebook has five code cells. At 1.4 Å the parent is a
central `void` with 33 resident cells and zero exterior links; the child is a
`pocket` with 35 resident cells and one exterior-link cluster. That cluster
uses new child hull face [6, 7, 8] in parent IDs, with native gate 2.010130644 Å
and geometric triangle area 16.148007904 Å². Unchanged parent hull triangles
remain covered by retained vertex balls at this probe, providing an independent
contact-location constraint. This is not a free aperture-area measurement or
an independently established physical mouth count.

At 3 Å the central child `void` has nine resident cells and no exterior link;
at 5 Å no resident wet component remains. The original 49-point probe sweep
retains nested resident availability and checks independently certified ranges,
leaving the remaining intervals unresolved. `min_size=36`, selected from total
central `n_nodes+1`, hides the child pocket while retaining its raw component,
support, parent mapping and physical result key. No native contradiction or
scientific-kernel fix was needed.

The short case index, quantity-aware records, four reviewed standalone figures
and execution receipt are versioned. Both notebooks run in fresh kernels
without original-provider execution, server requests or artifact writes. All
parent scientific artifacts/notebook bytes retain their protocol hashes.
Ordinary guards include independent geometry, rigid motion, explicit units
under nm/ps and pm/fs, live matched controls, mapped faces and reviewed records.
This is characterized source-workspace evidence, not a held-out blind panel,
volume qualification, general graph-path proof or installed/matrix qualification.

The next geometric question is a tube with independently justified passage and
bottleneck controls. Original comparisons for the opening can follow separately,
with their own atomic-model audit. #75/#76, the remaining synthetic inventory
and later molecular studies retain their gates.

## Second adopted reference and multi-provider comparisons

### Current independent system/native study — 2026-11-08

Issue #144 delivers a short closed-shell `index.md`, independent `system.ipynb`
and `dfnd.ipynb`, and the unchanged original `historical.ipynb`. All nine old
input/provider/report files and original notebook bytes retain their protocol
hashes. No original provider or CASTp job is executed or polled by these stages.

The protocol was frozen at `3a784df`, before the new staged native controls.
An existing 1.4 Å receiving regression and historical outcomes were already
known; this is characterization, not a blind evaluation panel. The independent
reference and its initial system notebook were committed at `3172ac9` before
fresh native observation. It provides three separately justified controls:

- 0.05 Å: a fixed straight ray has minimum all-atom clearance 0.095285334 Å,
  certifying access from the free origin to the exterior on the same atomic wall.
- 1.4 Å: the original covered-hull-triangle/free-origin certificate proves at
  least one enclosed probe-center component containing the origin.
- 5 Å: an enclosing-ball/convex-combination bound proves every finite-hull point
  covered by probe-expanded atomic balls, excluding finite resident support.

The older 0.2 Å anchor remains in the sweep with an explicitly inconclusive
reference disposition. A negative sufficient coverage margin does not prove a
leak, and unsuccessful fixed-candidate ray search does not prove closure. The
new small probe is a declared additional query, not a regenerated input or
tolerance fitted to native output. Certificate bounds are not exact topology
transition radii.

Fresh native observation agrees with the three justified claims: the 0.05 Å
central component has 128 resident cells and ten exterior-link clusters (current
family `channel`); the 1.4 Å central `void` has 33 resident cells and no exterior
link; the 5 Å query has no resident wet component. Ten contact clusters do not
establish ten independently certified mouths. The 49-point original sweep
exposes current states and nested resident-cell availability without asserting
monotone component counts. A `min_size=34` control hides the reported void while
retaining its raw support and physical result key.

`artifacts/native_study_v1/` retains the protocol, independent reference,
quantity-aware native observations, four reviewed standalone figures and an
execution receipt. Both notebooks run in separate fresh kernels, read shared
frozen inputs/reference files, and leave artifacts untouched on ordinary reruns.
Complete reports are folded for reading; a final fresh replay verifies identical
numerical records and all four figure bytes. No native scientific code changes
were needed for these controls.

This bounded notebook/reference extension does not complete #75/#76, the full
synthetic inventory, protein characterization or installed/matrix gates. The
0.2 Å enclosure remains unresolved at the stated reference scope. The next
geometric variant should derive an opening from this exact wall, preserve atom
correspondence and establish an independent access witness at the selected probe
before observing DFND.

### Historical combined study

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

## Previous pause and remaining gates

The user had paused after these two examples and their original-provider
comparisons. That scheduling boundary was superseded by the explicit
2026-11-07 resumption above. Obtaining and interpreting the two existing
CASTpFold jobs remains unresolved, independently of native development. Resume
those job IDs before any new submission and preserve input/radius-model limits.

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
