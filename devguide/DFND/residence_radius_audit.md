# DFND Residence Radius Audit

Point-in-time conceptual audit recorded on 2026-05-20.

This document records the correction to the first DFND geometry contract: four-atom tangency is only an interior candidate for tetrahedron residence. The DFND primitive must answer the broader question: can a probe reside in this tetrahedral cell?

The distinction matters before DFND is validated on real molecular systems, because residence is one of the two primary axes of the method:

```text
residence = can the probe occupy a local region?
transit   = can the probe move through permeable contacts?
```

If the residence primitive is too narrow, DFND will under-detect resident regions. If it is too broad, DFND will promote contact artifacts into pockets, voids, or channels. The issue is not cosmetic: it affects the primary family classifier.

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

This document is about Q2 and Q4. The companion document
[`gate_radius_audit.md`](gate_radius_audit.md) is about Q1 and Q3.

The residence answers should be derived from one scalar and its diagnostics:

```text
R_residence(T) = maximum probe radius with at least one admissible
                 probe-center position associated with tetrahedron T

tetrahedron_resident(T, R_probe) = R_residence(T) >= R_probe
```

The current concern is that the original implementation conflated this physical
quantity with a narrower candidate:

```text
R_apollonius4(T) = radius of the sphere tangent to the four atoms of T
```

`R_apollonius4` can be a valid candidate for `R_residence`, but it is not by
itself guaranteed to be the answer to Q4. Therefore it cannot automatically be
used to answer Q2 either.

The minimum acceptable DFND contract is:

| Question | Required answer | Historical issue | Implemented / target answer |
|---|---|---|---|
| Can the probe reside in tetrahedron `T`? | Boolean | historical first prototype used only the four-atom candidate | implemented active-set `R_residence(T) >= R_probe` |
| Maximum resident sphere radius in `T` | Scalar + diagnostics | `R_apollonius4` retained as an interior candidate/diagnostic | implemented active-set `R_residence` with candidate kind, center, `R_apollonius4`, and validity flag |

The rest of this document explains why that distinction is necessary and how to
make `R_residence` physically meaningful.

---

## 2. The Original Assumption

The initial mathematical contract used a single habitability radius for tetrahedron residence:

```text
tetrahedron_wet(T) = R_residence(T) >= R_probe
tetrahedron_dry(T) = R_residence(T) < R_probe
```

and described `R_residence` as the largest probe that can fit inside a Delaunay tetrahedron. The implementation then used the 3D tangency problem over the four atoms of the tetrahedron:

```text
find center p and radius R such that
||p - c_i|| = r_i + R    for the 4 atoms of T
```

This gives the sphere tangent to all four atomic spheres. When the solution is positive and geometrically well placed, it is a valid local clearance candidate. However, it is only one candidate for the maximum residence clearance associated with the cell.

The problematic phrase is not "clearance candidate"; it is "the largest probe that can fit inside the tetrahedron". That statement is stronger than what the four-atom tangency solution proves.

---

## 3. What DFND Actually Needs

DFND does not need to know whether the whole probe sphere is contained inside the geometric tetrahedron formed by atom centers. A Delaunay tetrahedron is not a physical box. Its faces are not material walls. It is a cell in a spatial decomposition used to index empty space and connectivity.

The physically useful question is instead:

```text
Does there exist at least one admissible position of the probe center, associated with this Delaunay cell, where the probe does not overlap the molecular atoms?
```

A more precise residence primitive should therefore be called `R_residence` or `R_clearance`:

```text
R_residence(T) = max over admissible center positions x associated with T
                 min over relevant atoms i ( ||x - c_i|| - r_i )
```

A tetrahedron is resident for probe radius `R_probe` when:

```text
R_residence(T) >= R_probe
```

This wording deliberately avoids saying that the whole probe must be contained inside the tetrahedron. The probe may cross Delaunay faces. The faces are used to define graph contacts and transit, not to clip the physical probe volume.

---

## 4. Why Four-Atom tangency Is Not Enough by Itself

The four-atom tangency solution is the stationary candidate where the active constraints are the four atoms of the tetrahedron. That is the natural interior candidate.

But the maximum clearance over a constrained cell-like region can occur in more than one geometric stratum:

```text
interior candidate: controlled by 4 atoms
face candidate:     controlled by 3 atoms, or sometimes 2 atoms
edge candidate:     controlled by 2 atoms
vertex/corner:      controlled by local boundary constraints or degenerate cases
```

This mirrors the issue already found for face permeability. A face gate is not always controlled by the three face atoms simultaneously; in some geometries the limiting pass is controlled by two atoms. The same kind of active-set logic can apply to residence.

Therefore:

```text
R_apollonius4(T) <=? R_residence(T)
```

has no guaranteed equality unless the four-atom candidate is valid and globally maximal under the selected cell-association policy.

The historical first prototype effectively assumed:

```text
R_residence(T) = R_apollonius4(T)
```

That shortcut has been replaced in the current code by active-set enumeration. `R_apollonius4` remains only as the four-atom interior candidate and diagnostic field.

---

## 5. Relationship With CASTp `rho`

CASTp alpha-shape terminology gives a useful comparison. CASTp computes a critical `rho` value for simplices, including tetrahedra. Internally this is represented in our CASTp implementation through fields such as:

```text
simplex_rho_ranks
spectrum_values
base_rank
probe_rank
```

The `rho` of a tetrahedron is a weighted alpha-shape critical value. It controls when the simplex enters the alpha filtration and how the rank-driven pocket, void, mouth, and flow machinery behaves.

That `rho` is related to a tetrahedral clearance scale, but it is not the same contract as DFND `R_residence`:

```text
CASTp rho:      filtration/rank value of a weighted simplex
DFND residence: physical occupancy capacity assigned to a local cell/domain
```

This means two things:

1. DFND should not blindly copy CASTp `rho` and call it residence.
2. DFND should also not call four-atom tangency "the" residence radius without proving that it solves the intended occupancy problem.

The safe conceptual statement is:

```text
The tetrahedron rho used by CASTp and the four-atom tangency candidate used by DFND are both local tetrahedral clearance scales. Neither statement alone settles the DFND residence contract.
```

---

## 6. Consequences for DFND Classification

The current DFND classifier uses access and residence:

```text
L(D)        = number of external links
has_res(D)  = at least one resident node
```

Then:

```text
0 links + residence    -> void_domain
1 link  + residence    -> pocket_domain
>=2 links + residence  -> channel_domain
```

The historical four-atom-only shortcut could underestimate real residence and falsely turn a resident domain into a non-resident one:

```text
pocket_domain                 -> surface_concavity_domain
channel_domain    -> nonresident_passage_domain
void_domain                   -> degenerate_subprobe_domain
```

The historical four-atom-only shortcut could also overestimate real residence and falsely promote a non-resident contact or sliver into a resident feature:

```text
surface_concavity_domain      -> pocket_domain
nonresident_passage_domain    -> channel_domain
degenerate_subprobe_domain    -> void_domain
```

So this audit affects the core taxonomy, not only metrics.

---

## 7. Candidate Correct Definition

The preferred conceptual replacement is:

```text
R_residence(T) = max clearance of a probe-center position associated with T
```

where:

```text
clearance(x) = min_i ( ||x - c_i|| - r_i )
```

The open design point is the admissible domain for `x`.

### Option A: Center Restricted to the Tetrahedron

```text
x in the closed tetrahedron of atom centers
```

Pros:

- Clear and implementable.
- Produces a well-defined per-cell optimization problem.
- Active sets are finite and can be tested systematically.
- Keeps residence attached to the Delaunay cell.

Cons:

- The tetrahedron of centers is not a physical boundary.
- A probe sphere may physically reside in a region whose center lies near a neighboring cell, while the sphere overlaps the current cell.
- This option may still discretize residence too sharply.

### Option B: Center Restricted to the Voronoi/Delaunay Dual Region

```text
x in the dual region associated with the tetrahedron or its Voronoi vertex/cell
```

Pros:

- Closer to Delaunay/Voronoi geometry and alpha-shape logic.
- May align better with CASTp-like critical points.

Cons:

- Harder to define for finite tetrahedron records in a simple data model.
- Weighted and unweighted variants differ.
- Less intuitive for users and toy construction.

### Option C: Residence as Domain-Level, Not Tetrahedron-Level

```text
A domain has residence if any point in the continuous accessible region mapped to the domain can host the probe.
```

Pros:

- Most physically honest.
- Avoids overinterpreting individual tetrahedra.

Cons:

- Harder to compute.
- Weakens the clean node-level DFND records.
- More difficult to use for graph construction and dynamic tracking.

### Working Recommendation

Use Option A for v1 and implement the primitive honestly:

```text
R_residence(T) = max_{x in tetrahedron(T)} clearance(x)
```

This is still a discretized approximation, but it is a much better statement than equating habitability with the single four-atom tangency solution.

---

## 8. Implementation Strategy

The current implementation follows this active-set maximum-clearance strategy over a tetrahedron in `topomt/dfnd/core/clearance.py::tetrahedron_residence_radius`.

For a tetrahedron `T` with four defining atoms, enumerate candidates from the strata of the tetrahedron:

```text
1. Interior candidate
   - 4-atom tangency sphere.
   - Accept only if the center lies inside the tetrahedron and the radius is positive.

2. Face candidates
   - For each tetrahedron face, solve the 2D/face-constrained clearance problem.
   - Include 3-atom tangency candidates.
   - Include 2-atom limiting candidates when the maximum lies on an edge of the face gap or when the 3-atom solution is invalid.
   - Accept only if the center lies on/in the face domain under the chosen tolerance.

3. Edge candidates
   - For each tetrahedron edge, solve the 1D constrained max-clearance problem along the segment.
   - Active constraints can be the two endpoint atoms or another atom whose distance field limits the segment.

4. Vertex candidates
   - Evaluate clearance at the four tetrahedron vertices or at a small set of meaningful boundary points if needed.
   - These are mostly degeneracy safeguards, since atom centers themselves have negative clearance against their own atom radius.
```

Then:

```text
R_residence(T) = max radius among all valid candidates
```

The raw record should store enough diagnostics to avoid hiding uncertainty:

```text
R_residence
residence_candidate_kind       # implemented: interior4, face3, edge2, none
residence_candidate_center
R_apollonius4                  # retained as diagnostic
apollonius4_valid              # center valid, positive radius, non-overlap check
residence_margin = R_residence - R_probe  # graph/reporting layer field
```

This gives us a transparent bridge from the old implementation to the corrected contract.

---

## 9. Numerical and Conceptual Checks

The corrected primitive is now covered by small tests that separate the main possible cases. Additional protein-scale validation is still pending.

Implemented or required toys:

```text
toy_residence_interior4
    Implemented: compact tetrahedron where the 4-atom tangency center is inside and is the maximum.

toy_residence_face_limited
    Implemented: tetrahedron where the best residence point lies on a face and the 4-atom candidate is outside or suboptimal.

toy_residence_edge_limited
    Implemented: tetrahedron/sliver where the best admissible point lies on an edge.

toy_residence_apollonius4_invalid
    Implemented: tetrahedron where the 4-atom solution is positive but its center is not inside the tetrahedron, so it must not be used as the residence radius.

toy_residence_vs_castp_rho
    Pending: compare R_apollonius4, R_residence, and CASTp-like tetrahedron rho on the same small geometry to document similarities and differences.
```

The tests should assert not just the final wet/dry label, but also the winning candidate kind. This will prevent future regressions where the code returns the right label for the wrong reason.

---

## 10. Naming Recommendation

The old habitability language was risky when it suggested that the whole probe sphere must be contained inside the geometric tetrahedron. That is not the physical meaning DFND wants. `R_residence` is acceptable only if it is explicitly defined as an admissible probe-center clearance.

Recommended terminology:

```text
R_apollonius4
    The raw four-atom tangency candidate.

R_residence
    The selected residence radius used for wet/dry classification.

R_clearance
    Optional synonym if we want to emphasize the optimization value rather than the topographic role.
```

For public DFND language:

```text
resident tetrahedron
    A finite Delaunay tetrahedron whose residence radius is at least the probe radius.

non-resident tetrahedron
    A finite Delaunay tetrahedron whose residence radius is below the probe radius, even if some faces are permeable.
```

Avoid:

```text
The probe fits inside the tetrahedron.
```

Prefer:

```text
The tetrahedron has an admissible probe-center position with enough clearance.
```

---

## 11. Documentation Status After Implementation

The consistency pass has been applied to the main DFND documents. The remaining action is to keep implementation details and raw-record fields synchronized as the primitive matures:

```text
Mathematical_Definitions.md
    Keep the corrected R_residence contract explicit. Keep R_apollonius4 as a diagnostic candidate only.

numerical_policy.md
    Ensure wet/dry threshold language always points to active-set R_residence.

residence_transit_contract.md
    Make explicit that residence and transit are independent axes, and that residence is based on R_residence, not necessarily four-atom tangency.

data_model_v1.md
    Keep fields for R_residence, R_apollonius4, candidate kind, and margin synchronized with code.

known_limitations.md
    Reference this audit as a primitive-geometry limitation and mitigation path.

toy_systems_v1.md
    Keep the residence active-set toys listed above as regression targets.
```

---

## 12. Working Decision

The provisional proxy stage is now historical. Current DFND code should be
described as using an active-set residence primitive:

```text
R_residence = max valid clearance over interior4, face3, and edge2 candidates
R_apollonius4 = four-atom interior candidate retained for diagnostics
```

Parity or benchmark interpretation should still report the selected candidate
kind and marginal cases, because near-degenerate tetrahedra can stress the
active-set enumeration and tolerance policy.

The correct route is not to abandon the DFND residence/transit model. The model is still conceptually strong. The correction is narrower:

```text
Keep residence as a primary axis, but compute residence with the right active-set clearance primitive rather than assuming the four-atom tangency candidate is always sufficient.
```
