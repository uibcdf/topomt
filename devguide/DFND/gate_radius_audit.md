# DFND Gate Radius Audit

Point-in-time conceptual audit recorded on 2026-05-20.

This document audits the DFND face-permeability primitive, currently exposed as
`R_gate`. It is intentionally parallel to [`residence_radius_audit.md`](residence_radius_audit.md): residence asks whether the probe can occupy a local region, while gate permeability asks whether the probe center can cross a shared Delaunay face.

The current `R_gate` implementation combines three-atom and two-atom candidates and now exposes a `GateResult(radius, center, kind)` through `face_gate_radius(...)`. It should still be documented as a local face-gate model with explicit assumptions and validation requirements, not as a fully proven continuous-space bottleneck for every molecular configuration.

---

## 1. Physical Contract

DFND must answer four primitive physical questions before any higher-level
feature classification can be trusted:

```text
Q1. Is a Delaunay face permeable to a probe sphere of radius R_probe?
Q2. Can a probe sphere of radius R_probe reside in a Delaunay tetrahedron?
Q3. What is the maximum radius of a sphere that can permeate a face?
Q4. What is the maximum radius of a sphere that can reside in a tetrahedron?
```

This document is about Q1 and Q3. The companion document
[`residence_radius_audit.md`](residence_radius_audit.md) is about Q2 and Q4.

The permeability answers should be derived from one scalar and its diagnostics:

```text
R_gate(F) = maximum probe radius whose center can cross face F
            under the selected local face-gate model

face_permeable(F, R_probe) = R_gate(F) >= R_probe
```

The current concern is not that `R_gate` is meaningless. The current concern is
that a scalar returned by a local face model must be explicit about what physical
question it answers and what it does not answer. In particular:

```text
R_gate answers local face permeability.
R_gate alone does not prove global continuous-space reachability.
R_gate alone does not include every possible external atom that may intrude into the gate.
```

The minimum acceptable DFND contract is:

| Question | Required answer | Historical issue | Implemented / target answer |
|---|---|---|---|
| Is face `F` permeable to the probe? | Boolean | historical scalar wrapper `check_face_permeability` | implemented `face_gate_radius(F).radius >= R_probe` plus graph-level flags |
| Maximum permeating sphere radius through `F` | Scalar + diagnostics | local face3/pair2 scalar | implemented `GateResult(radius, center, kind)`; still pending fuller branch diagnostics and margin in the primitive |

The rest of this document records what is implemented and what remains pending before exactness claims are appropriate.

---

## 2. What `R_gate` Is Supposed To Answer

For a triangular Delaunay face `F` defined by three atoms, DFND needs a probe-dependent answer to:

```text
Can the probe center cross this face without overlapping the atoms that define the local gate?
```

The local face gate radius is therefore:

```text
R_gate(F) = maximum probe radius whose center can pass through the face gap
            under the selected local face model
```

The graph rule is:

```text
face_permeable(F) = R_gate(F) >= R_probe
```

This is a transit primitive, not a residence primitive. It should not be read as a volume or as a statement that the whole probe sphere is contained in either adjacent tetrahedron.

---

## 3. Current Implementation

The current implementation lives in `topomt/dfnd/core/clearance.py` as `face_gate_radius(...)`. `topomt/dfnd/core/permeability.py::check_face_permeability(...)` is now a scalar compatibility wrapper returning only `GateResult.radius`.

Its main steps are:

```text
1. Project the three atom centers of the face to a 2D coordinate system in the face plane.
2. Compute a three-atom 2D tangency candidate.
3. Accept that candidate only if its radius is positive and its center lies inside the face triangle.
4. Compute two-atom candidates for each atom pair.
5. Accept a two-atom candidate only if it does not overlap the third atom and its center lies inside the face triangle.
6. Return the maximum accepted candidate radius, or 0.0 if none is valid.
```

This is already an active-set strategy:

```text
face3 candidate = gate controlled by the three face atoms
pair2 candidate = gate controlled by two face atoms, with the third atom non-overlapping
```

The tests currently cover:

```text
- equilateral equal-radius analytical gate;
- rigid-transform invariance;
- atom-order invariance;
- an explicit two-atom-limited gate at the face boundary;
- direct inner-branch coverage of the 2D tangency solver.
```

This is a useful baseline. It is not just a naive three-circle tangency call.

---

## 4. Why The Residence Critique Still Has An Analogue Here

The residence audit identified a general active-set issue: a maximum-clearance value is not necessarily controlled by all atoms of the local simplex. The same principle applies to face permeability.

For a face made of three atoms, the active set can be:

```text
three atoms:  the gate is controlled by all three face atoms;
two atoms:    the gate is controlled by a pair of atoms, with the third atom inactive;
one/boundary: degenerate or boundary cases where the local face model fails or is ill-conditioned.
```

The current implementation handles the first two classes in a practical way. That is the main reason `R_gate` is in better shape than the old four-atom-only residence proxy.

However, the conceptual warning remains:

```text
R_gate is a selected local face permeability radius, not a mathematical proof of global continuous-space reachability.
```

A Delaunay face is a graph contact, not a material aperture. The continuous accessible set can intersect, curve around, or be blocked near the face in ways that a three-atom local model cannot fully capture.

---

## 5. The Plane-Of-Centers Issue

An earlier note in `Mathematical_Definitions.md` suggested that with unequal atomic radii the true three-sphere bottleneck might be displaced away from the plane of the three atom centers. After geometric review, this concern should be softened.

For the three spheres whose centers define the face, the plane through the three centers is a mirror-symmetry plane of that three-sphere set. Reflection across the plane fixes each center and maps each sphere to itself, regardless of whether the three radii are equal. Therefore, under the local model that only the three face atoms constrain the gate, the symmetric bottleneck candidate belongs naturally to that plane.

The more important risks are different:

```text
1. The active constraint can be two atoms rather than three.
2. The accepted center must lie in the intended face gap, not in an exterior branch.
3. An atom not belonging to the face can intrude into the local gate region.
4. Sliver or near-degenerate faces can make the local gate numerically unstable.
```

The first two are partly addressed by the current implementation. The third is handled only as a graph-level diagnostic flag. The fourth needs tolerance and stability reporting.

---

## 6. Current Strengths

The current `R_gate` primitive has several good properties:

```text
- It works in the face plane, which is the right local symmetry plane for the three face atoms.
- It validates that the three-atom tangency candidate lies inside the triangular face.
- It considers two-atom-limited gates, avoiding the same mistake as a naive all-atoms tangency-only residence primitive.
- It is invariant under rigid transformations in the current tests.
- It is invariant under atom ordering in the current tests.
- It returns a conservative zero for degenerate or collinear face atoms.
```

For v1, this makes it a reasonable local `R_gate` model.

---

## 7. Remaining Weak Points

### 7.1. Single 2D tangency Branch

The current 2D solver returns one branch of the quadratic solution. For the tested inner Soddy-like branch this is correct. But for arbitrary unequal radii or adversarial geometries, we have not yet proven that this branch always gives the intended local gate candidate.

Safer future behavior:

```text
- enumerate all real positive tangency roots;
- compute their centers;
- reject candidates outside the face triangle or overlapping any face atom;
- keep the best valid local candidate;
- record which branch won.
```

### 7.2. Two-Atom Candidate Is Practical But Not Fully Audited

The two-atom candidate is currently placed along the line between the two atom centers and checked against the third atom and the face triangle.

This captures an important boundary-limited case and is already tested. Still, the exact constrained maximum over a triangular face can have subtle boundary cases. A stronger implementation would treat the face-gate problem as a small active-set optimization over the closed triangle, just as residence should be treated over the closed tetrahedron.

### 7.3. Candidate Diagnostics Are Partly Implemented

`face_gate_radius(...)` returns:

```text
GateResult(radius, center, kind)
```

This solves the previous float-only primitive for the active-set kind and center. Still pending are richer diagnostics such as active atom ids, all rejected candidates, marginal status, and branch id. `check_face_permeability(...)` intentionally remains float-only as a compatibility wrapper.

### 7.4. External-Atom Intrusion Is Not Part Of The Primitive

The local gate uses only the three atoms of the face. An opposite tetrahedron apex, a neighboring bulky atom, or another nearby atom can intrude into the gate region and make a locally permeable face physically suspect.

The current graph layer has an `intrusion_suspect` flag and an optional `block_suspect` policy. That is an acceptable v1 design if documented honestly:

```text
R_gate = local face-gate radius from the three face atoms.
intrusion_suspect = diagnostic that nearby tetrahedral context may invalidate the local gate.
```

The important point is not to silently claim that `R_gate` alone proves global passage.

### 7.5. Tolerance Near Threshold

Permeability is a threshold decision:

```text
R_gate >= R_probe
```

Small coordinate perturbations, alternate locations, radii policy, or nearly collinear faces can move a gate across the threshold. The raw records should distinguish:

```text
permeable
non_permeable
marginal
```

and store the margin:

```text
gate_margin = R_gate - R_probe
```

This is already represented in parts of the graph layer. The primitive returns candidate kind and center, but not yet a margin or marginal-status field.

---

## 8. Recommended Canonical Definition For v1

For v1, keep a local face model:

```text
R_gate_local(F) = max valid clearance candidate over the closed triangular face,
                  using the three face atoms as local constraints.
```

Then define:

```text
R_gate(F) = R_gate_local(F)
```

with explicit diagnostics:

```text
gate_intrusion_suspect(F) = true if adjacent tetrahedral context may block the local gate
```

This keeps the method simple and transparent:

```text
local gate calculation = face-intrinsic primitive
contextual correction  = graph-level diagnostic/policy
```

This is preferable to mixing neighbor atoms directly into the first v1 `R_gate` value, because direct mixing would make the same face have different radii depending on which tetrahedron owns it. The face should have one local gate radius; context can add flags.

---

## 9. Implementation Direction

The current function has evolved from a float-returning helper into a richer primitive. Current implemented result:

```text
GateResult(
    radius,
    center,
    kind,                 # face3, pair2, none
)

Future richer result may add:

GateResultDiagnostics(
    atom_indices,
    all_candidates,
    flags,
    margin,
    branch_id,
)
```

Implemented algorithm, with pending refinements marked explicitly:

```text
1. Build the 2D face coordinate system.
2. Generate the current three-atom tangency candidate. Pending: enumerate all branches.
3. Generate all pair-limited candidates.
4. Pending: optionally generate explicit boundary/vertex fallback candidates for diagnostics.
5. For every candidate, compute clearance against all three face atoms.
6. Keep only candidates inside the closed face triangle and with non-negative clearance.
7. Return the candidate with maximum clearance as `GateResult`.
8. Keep `check_face_permeability(...)` as a compatibility wrapper returning only `GateResult.radius`.
```

This mirrors the residence active-set implementation path, but in 2D and with a much smaller candidate set.

---

## 10. Test Status Before Exactness Claims

The current tests cover the first v1 requirements, but stronger exactness claims still need additional branch and threshold coverage. Status:

```text
gate_face3_regular
    Implemented: equal-radius equilateral triangle with analytical radius.

gate_pair2_boundary
    Implemented: two-atom-limited fixture; keep it.

gate_candidate_diagnostics
    Partly implemented: `GateResult.kind` reports face3, pair2, or none. Rich rejected-candidate diagnostics remain pending.

gate_collinear_degenerate
    Implemented at primitive level: degenerate/collinear face returns zero/none behavior.

gate_intrusion_context
    Implemented at graph-policy level: local R_gate can be flagged with intrusion_suspect and optionally blocked.

gate_unequal_radii_branch_selection
    Pending: unequal radii where multiple positive tangency branches exist; assert the valid in-triangle branch wins.

gate_marginal_threshold
    Pending/richer reporting: R_gate within epsilon of R_probe should be reported as marginal, not silently open/closed.
```

Tests should continue to include the center and active-set kind, not just the final scalar radius.

---

## 11. Documentation Status After Implementation

The main documentation has been updated to reflect this audit. Remaining synchronization points:

```text
Mathematical_Definitions.md
    Keep the current framing: local face model, active-set selection, and external-atom intrusion as contextual risk.

numerical_policy.md
    State that `R_gate` is thresholded with margin/marginal status and should expose candidate diagnostics.

data_model_v1.md
    Keep gate candidate kind, center, margin, and intrusion flags synchronized with code and graph records.

known_limitations.md
    Reference this audit as the canonical gate-radius limitation and mitigation plan.

validation_plan.md
    Keep branch-selection, pair-limited, intrusion, and marginal-threshold gate toys as validation targets.
```

---

## 12. Working Decision

The current `R_gate` implementation is acceptable as the v1 local face-gate primitive because it handles three-atom and two-atom active sets, validates candidate centers against the face triangle, and returns `GateResult(radius, center, kind)`.

DFND should describe it precisely:

```text
R_gate = maximum valid local face clearance among implemented face3 and pair2 candidates
```

Remaining work before stronger exactness claims:

```text
- enumerate all three-atom tangency branches;
- expose richer candidate diagnostics;
- keep contextual intrusion as a graph-level flag/policy;
- add stronger near-threshold and unequal-radii tests.
```

This is a smaller correction than the residence-radius issue. The residence primitive needed a conceptual replacement and now has an active-set implementation. The gate primitive mostly needs fuller branch enumeration, richer diagnostics, and stronger tests.
