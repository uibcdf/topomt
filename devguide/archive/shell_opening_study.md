---
summary: Derive a shell opening from the frozen wall and characterize native access.
issue: uibcdf/topomt#145
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [dfnd, docs]
guard: tests/test_shell_opening_study.py::test_live_opening_controls_and_parent_identity_under_explicit_units
normative:
blocked_by: []
supersedes: []
---

# Shell with an opening

## What

Add a named BenchLab unit derived from the adopted 72-ball closed shell.
Delete the six parent atoms within a 35-degree positive-Y polar cap; retain
all other coordinates/radii exactly and preserve local-to-parent atom identity.

## How

Freeze input, derivation, query and reference before new native observation.
The retained 66-ball input has a +Y all-atom ray clearance 1.819726 Å, certifying
access at probe 1.4 Å. A 3 Å probe leaves a free origin inside a covered hull;
5 Å covers the whole finite hull. Compare the closed parent and opened child
at identical 1.4 Å query settings. Inspect raw/public supports, use the public
atom_indices argument to retain parent IDs, and map contact faces back to that
namespace. Unchanged parent hull triangles remain covered at this probe, so
new exterior contacts must lie on newly exposed child hull faces.

Run independent system and DFND notebooks in separate fresh kernels. Keep
references and physical meaning separate from labels/counts. Reuse the existing
native APIs and dimensional codec; no new generator call or scientific kernel
implementation is needed for preparing the case.

## Why

Regenerating jitter while deleting a cap changes the wall as well as its opening.
This matched pair isolates atom deletion, with an independent positive path
and a separately certified parent negative control.

## What was refuted

A single deleted cap or one ray does not prove exactly one physical mouth.
Neither cavity counts, native family names nor peer agreement are independent
truth. Parent and child tetrahedron IDs cannot be equated after retriangulation;
only atom correspondence is preserved.

## Scope and exclusions

One new source-derived case and its three independently justified probe controls.
Parent/tetrahedron artifacts, generators, third-party engines, server jobs,
protein studies, volume precision #75 and the wider panel #76 stay separate.
Any native contradiction must receive its own reproduced defect rather than a
reference or query adjustment fitted to the output.

## Acceptance criteria

Versioned input/PDB subset, parent mapping, pre-native independent reference,
two executed notebooks with reviewed figures/records, provenance and geometry
guards (including units and rigid motion), raw contact/support analysis, public
navigation and rendered documentation. Qualification remains source/workspace
and case-scoped; this is no full synthetic/matrix/installed release claim.

## Resolution

The input, cap rule, parent identities and native query were committed at
`b6fe6e2`. The separately executed system notebook and independent reference
were committed at `2ca133d` before the first child native execution. The
66-ball input is an exact subset: parent IDs 0–5 are removed, all retained
coordinates/radii/order remain unchanged and exchange PDB rows preserve
serial/residue IDs 7–72. All twenty parent scientific artifacts/notebooks retain
their frozen hashes. Parent Markdown gains only a link to this new unit.

The system reference computes +Y all-atom ray clearance 1.819726044 Å and
conservative cap clearance lower bound 1.665782356 Å; both certify access
at 1.4 Å. The original parent wall remains independently enclosed at that
same probe. At 3 Å, child hull triangles are covered by expanded vertex balls
while the origin remains free; at 5 Å the enclosing-ball/convex-combination
bound covers the whole finite hull. The bounds leave explicit unresolved
intervals, rather than claiming exact topology-transition radii.

DFND agrees at the justified scopes. The same-probe parent is a central `void`
with 33 resident cells and no exterior link. The 1.4 Å child is a `pocket`
with 35 resident cells and one exterior-link cluster. That link uses newly
exposed hull face [6, 7, 8] in parent IDs; unchanged parent hull faces remain
covered at the probe. Native gate 2.010130644 Å and geometric triangle area
16.148007904 Å² retain their explicit dimensional meaning. Neither the area
nor the cluster count establishes physical mouth area/cardinality.

At 3 Å the central child `void` has nine resident cells and no exterior link;
at 5 Å there is no resident wet component. The 49-point inherited sweep checks
nested resident availability and agreement only in independently certified
ranges. Its apparent native transition between 2.0 and 2.1 Å is not an exact
physical reference. At `min_size=36`, chosen as central total `n_nodes+1`, the
public pocket projection disappears while the raw support, atom mapping,
component identity and physical result key remain unchanged.

The named case index, independent system/native notebooks (five code cells
each), quantity-aware records, four reviewed standalone figures and execution
receipt are versioned. The guard executes the existing public advanced
constructor/query under both nm/ps and pm/fs unit policies, checks the matched
parent/child controls and verifies raw parent identity and contact location.
Other module tests protect independent geometry, rigid motion, exact subset,
historical bytes, reviewed displays and receipt hashes. Both notebooks leave
artifacts untouched on ordinary execution and run no provider/server.

Verification: 55 selected current/prior-case, original-evidence and governance
tests pass on shared Python 3.14.10. Repository-wide Ruff passes (544 files
formatted), focused mypy passes and full Sphinx HTML builds with the same
twelve pre-existing warnings and no new warning. Three case pages, folded
reports, navigation and all ten new downloads are checked; downloaded bytes
match their reviewed source artifacts. No new runtime/dependency/optional-engine
boundary is introduced: existing native APIs and PyUnitWizard QuantityRecord
are reused, with no source-kernel or sibling implementation change.

The fresh system/native kernel runs took approximately 3.04/5.50 seconds.
Maximum observed kernel-process RSS was 153636/222816 KiB. Each inherited
one-CPU affinity, one numerical worker, 6 GiB process address-space ceiling,
90-second process CPU budget and 60-second cell timeout. HTML used one CPU
and a 120-second process CPU budget; observed peak process RSS was 275884 KiB.
The shared host/scheduler state was checked, no memory pressure or active
swapping was observed, and free resources were not treated as reserved. These
are technical execution receipts, not comparative performance measurements.

All required scientific evidence is versioned. Task-owned builders, logs and
rendered preview remain in ignored `.cache/shell-opening-study/` for review;
the redundant copied docs source can be removed after publication. No shared
environment, original-engine checkout or unrelated process was changed. The
pre-existing human version-file edit remains intact and is included honestly
in the native source fingerprint.

This resolves the staged shell-opening unit only. No native defect or kernel
fix was needed. #75/#76, unresolved sweep intervals, exact global cavity/mouth
counts, general graph-path validity, remaining synthetic cases, proteins and
full suite/matrix/installed gates (#16/#19/#81) remain separate. Incremental
commits use the maintainer-authorized `[skip ci]` route. The next geometric
question is a tube with independently controlled passage and bottlenecks;
new original comparisons retain their own atomic-model admission.
