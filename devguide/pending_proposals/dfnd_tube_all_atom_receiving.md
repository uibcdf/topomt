---
summary: Reconcile local tube candidates with independently empty all-atom carriers.
issue: uibcdf/topomt#181
status: active
opened: 2026-11-10
closed:
severity: medium
verification: measured
area: [dfnd, validation, api]
guard:
normative:
blocked_by: []
supersedes: []
---

# Local candidates in the covered tube

## Independent narrow-family reference handoff — 2026-11-14

Under [#76](dfnd_reference_validation_panel.md), the exact reference validator
now receives all three unchanged original narrow-tube Models. Source `d73477c`
completes 1.2/2.5 Å through independently checked identical cell geometry and
recomputed target predicates, preserving the earlier 1.4 Å source evidence.
The [family summary](../evidence/reference_validator_power_cells_v4/family_summary.json)
binds complete **1/1/0 free regions and 2/2/0 free hull patches**, at
1.2/1.4/2.5 Å, and the positive checked continuous paths. The 1.4 Å origin is
blocked while its free region connects the two end patches.

The 2.5 Å target proof is an exhaustive convex-cell cover of the same finite
hull: each checked cell is entirely within its owner's expanded ball. It
independently confirms zero free centers/zero probe-center volume, agreeing
with the older conservative cover. This completeness is supplied by the full
geometric partition and ball convexity; the thirty narrow native-center point
checks below do not acquire that proof merely by being blocked.

This is stronger reference receiving, not a change to native operators or
public promotion. The wide 5 Å profile retains its separate earlier reference
and unresolved public qualification. #181 remains active/`needs_review`: select
and implement the local-candidate versus all-atom physical reporting policy,
with the same original supports, pending targets and method-book review.
The comparative-finding review changes no lifecycle or inferiority claim;
the demonstrated native behavior and its unresolved interpretation are unchanged.

## What

At source b07a20e and probe 2.5 Å the frozen 81-ball tube has three wet graph
components and four public objects: OpenConcavity/Mouth and Groove/Mouth.
An independent sufficient cover proves no strict all-atom free probe center
anywhere in its finite atomic-center convex hull. The cover distance bound is
4.083579632239034 Å, less than the expanded radius 4.38 Å by 0.296420367760966 Å.

## How

Retain `straight_tube_narrow_dense/artifacts/straight_tube_narrow_dense_v1/native_observations.json`, the
original full-precision quantity-aware input, frozen query and independently
replayable passage/model certificate. The negative public target first failed
and remains a strict expected failure under this issue. Inspect responsible
tetrahedra, active-set candidates, nonlocal obstacles and public supports before
selecting an operator or promotion/qualification change.

## Why

A local three/four-atom capacity is not an all-atom physical certificate. A
public morphological finding must communicate that distinction if it survives
inside an independently covered finite carrier. Do not assume a local solver
defect from this result alone. The interpretation remains `needs_review`.

The pending empty-public target is a proposed reporting outcome, contingent on
the qualification policy selected here. The independent oracle concerns the
physical all-atom free set; it does not require the existing local wet bank to
be empty. Reconcile that proposed guard with the explicit policy decision,
without weakening or replacing the independent finite-hull exclusion.

## What was refuted

The catalog name and graph labels are not independent truth. A plotted path,
carrier volume or positive local solvent proxy cannot refute the all-atom cover.
Nor does this empty finite hull exclude the unbounded exterior or establish a
biological failure, comparative inferiority or global optimal bottleneck.

## Scope and exclusions

The exact #178 narrow ball input at 2.5 Å and #183 wide input at 5 Å,
zero physical tolerances, epsilon 1e-6 Å,
with_connectors/flag_only/dryface. No silent change to local capacity definitions,
default scientific policy, input radii or expected reference. #180 separately
owns physical boundary budget; #60/#76 retain broader public/reference work.

## Acceptance criteria

Diagnose supports/candidates and select an explicit all-atom qualification or
reporting policy. Implement any correction test-first and verify the same fixed
control plus adopted earlier cases, units/maps/reuse and source provenance.
Review matching DFND chapters, retain the original observations and reconcile
the card/hub/lifecycle/case/report before closing. Pending diagnosis is not a
present-tense paper claim.

## Additional wide-tube profile — 2026-11-10

Companion #183 adds `straight_tube_wide_sparse` at 5 Å, source
3ad9515019e722c0ccf4ade7a3024de4166e217e: one wet component and a public
OpenConcavity/Mouth survive the independently covered finite hull. The cover
margin is 0.28575699050079173 Å (6.594243009499208 Å bound versus expanded
radius 6.88 Å). This remains needs_review, not a diagnosed local solver error.
The original narrow target stays pending; the new observation extends support
and public-qualification diagnosis without silently adopting empty local banks
as an oracle. At positive probes extra local candidates also need diagnosis:
1.4 Å has two global patches and resolved Channel contacts but ten unknown
associations for other candidates; do not infer side-wall holes or all physical
3D components from them. Wider paths remain #76; budget #180 and numerical
boundary availability #184 are separate. Keep both original evidence profiles.

## Residence-point diagnosis and current public receiving — 2026-11-12

The [six-case review](../../docs/content/benchlab/synthetic/six_case_review.md)
adds 19 actual public profiles at source
`1510e007d96da8a3c569f626a1b263fb59a54533`, with original case/reference/download
bytes preserved. The [protocol](../../docs/content/benchlab/synthetic/artifacts/six_case_review_v1/protocol.json),
[summary](../../docs/content/benchlab/synthetic/artifacts/six_case_review_v1/summary.json)
and [full compressed capture](../../docs/content/benchlab/synthetic/artifacts/six_case_review_v1/receiving.zip)
retain the exact input, maps, local query, current raw/typed/public correspondence,
point diagnostics, actual attribution and execution identities. No native
scientific or promotion code changed.

The causal route is now explicit:

1. `tetrahedron_residence_radius_batch` evaluates its four local atoms. In the
   two excluded tube profiles every recorded resident center is within its
   carrier under the declared barycentric tolerance, and its local clearance
   recomputes with no residual at captured precision.
2. Narrow 2.5 Å has 24 resident centers in WET-1 and six in WET-2. **All 30 are
   blocked by nonlocal atoms.** Tetrahedron 64, source vertices [4,67,76,77],
   has local clearance 7.016483499 Å and all-atom clearance -0.358693175 Å at
   its stored center; source atom 31 is the nearest blocker.
3. Wide 5 Å has one resident center. Tetrahedron 115, source vertices
   [2,45,56,57], has local clearance 5.299843470 Å but all-atom clearance
   -1.575928567 Å; source atom 24 blocks it.
4. Graph admission still uses the declared local capacities/policies. The narrow
   resident banks enter the one-link compatibility family; catalog refinement
   classifies them OpenConcavity and Groove. `dfnd_to_topography` promotes these
   two parents and their MOU-1/MOU-2 links without an all-atom free-carrier test.
   WET-3 is connector-only `surface_concavity` and remains native-only. The wide
   resident bank becomes OpenConcavity/Mouth. Classification confidence does
   not supply the missing physical guarantee.

This diagnoses the stored-point discrepancy, **not** a global completeness or
accuracy proof for the local solver. The original whole-hull cover remains the
independent reason no physical free point can exist in those two controls.
Positive shell/tube/dumbbell profiles contain both clear and blocked stored
centers; their independently established named regions remain valid.

### Qualification decision still required

The next implementation must explicitly distinguish local-candidate reporting
from an admitted all-atom physical guarantee while preserving raw/local supports
and source history. The existing proposed empty-public xfail remains a proposed
policy, not an independent reference for the local bank.

Do not merely remove every tetrahedron whose stored local center collides. A
different point can remain physically free; the diagnostic's authored control
exhibits that distinction. Conversely, a clear center does not establish region
connectivity, mouth attachment, morphology or a valid path. A complete-cover
certificate or another admitted complete qualification needs its own bounded,
recoverable evidence and unresolved state. Coordinate the public support seam
with #60 rather than redefining the local operators silently.

The finding remains `needs_review`, and #181 stays active. No general DFND
failure or paper limitation is established. Point diagnosis is delivered;
qualification policy and its implementation remain this issue's next work.

### Guards and resources

- `tests/test_benchlab_residence_witnesses.py` covers nonlocal blocking,
  alternative clear points, local residuals, source maps, equivalent units,
  numerical/support ambiguity, empty banks, work refusal and both actual public
  exclusion profiles. The module first failed for the missing diagnostic before
  implementation; all eight cases pass at this checkpoint.
- `tests/test_benchlab_six_case_review.py::test_review_receipt_retains_frozen_models_and_actual_public_profiles`
  protects the complete archived capture, model hashes and 19-profile review
  coverage; it does not certify all physical objects.
- One logical CPU, one native worker/thread, 4 GiB address-space ceiling and
  90-second deadline. Actual full capture: 17.02 s, peak 336484 KiB RSS. Earlier
  Slurm discovery was unavailable; memory pressure was zero and about 53 GiB
  available before this small direct run. No shared environment/native rebuild.
