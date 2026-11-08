---
summary: Derive a shell opening from the frozen wall and characterize native access.
issue: uibcdf/topomt#145
status: active
opened: 2026-11-08
closed:
severity: medium
verification: inspected
area: [dfnd, docs]
guard:
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
