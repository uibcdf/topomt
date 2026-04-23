"""Rigorous audit of the native CASTp path against papers and MKALF."""

# Canonical Algorithm Audit 2026-04-17

## Purpose

This note is a slow, concept-first audit of the native CASTp implementation
against:

- the public algorithmic contract in the 1998 CAST papers
- the operational semantics fixed by MKALF 4.1

The purpose is not to discuss parity on individual systems. The purpose is to
state, as scrupulously as possible, which parts of our code already follow the
canonical algorithm and which parts still do **not** demonstrably do so.

## Scope

This audit is about the algorithm itself:

- triangulation substrate
- rank semantics
- pocket / cavity construction
- mouth construction
- reporting semantics

It is **not** a case-by-case parity report.

## What the papers fix conceptually

The 1998 papers fix the public contract clearly enough on the following points:

1. CAST works on a weighted Delaunay / alpha-shape substrate.
2. Pockets are regions in the complement with limited accessibility from the
   outside.
3. The construction uses discrete flow, not just static connected components of
   empty simplices.
4. Pockets, cavities, and mouth openings are explicit geometric objects.
5. CAST reports atoms lining pockets, mouth openings, and buried cavities.
6. CAST reports geometric measurements of pockets / cavities and of mouth
   openings.

What the papers do **not** fully determine is the exact low-level operational
machinery:

- the detailed ordering semantics of the spectrum
- the exact `mu1` / `mu2` propagation rules
- the exact edge-facet combinatorics of `Fnext`
- the literal master-list workflow
- the full internal reporting partition (`iV/rV`, `iE/rE`, `iF/rF`)

For those, MKALF is the executable specification, as long as it does not
contradict the public theory. So the correct discipline is:

- papers define the conceptual contract
- MKALF defines the operational contract

## What is now conceptually aligned enough

The following fronts should no longer be treated as leading conceptual gaps.

### 1. Solvent inflation

This agrees with the historical workflow and with the CAST papers' use of a
probe sphere to define the molecular surface.

### 2. `rho0` / weighted vertex size

The native `rho0 = -weight` convention agrees with weighted MKALF.

### 3. `mu` is not inserted into the spectrum

This is now aligned with `spectrum.c` and with the conceptual separation:

- `rho` creates the spectrum
- `mu1` / `mu2` are derived afterwards

### 4. Pockets are no longer admitted by a precomputed empty-mask shortcut

The pocket construction now scans tetrahedron rho events by rank and uses
sink/depth logic, which is conceptually much closer to `alf_init_pockets()`.

### 5. Pocket depth semantics are now aligned with the non-wrapping path

The native pocket depth computation now follows the max-rho sink semantics of
historical `compute_tetra_depth()`, instead of incorrectly reusing wrapping
logic.

### 6. Hidden predicates are no longer plainly floating-point heuristics

`hidden1` / `hidden2` now use exact fixed-point determinant machinery, which is
 conceptually much closer to the weighted predicate layer required by MKALF.

### 7. Mouth construction is no longer based on naive shared-edge adjacency

The mouth path now uses:

- explicit mouth-face seeds
- outward orientation
- `Enext`
- `Fnext`-style walks around open edges

That is conceptually consistent with both the papers and MKALF.

## Remaining conceptual gaps

What follows is the current list of points where our code still does **not**
yet demonstrably do 100% the same thing as the canonical CAST algorithm.

These are listed from most structural to more secondary.

### 1. Triangulation substrate is still not canonical

Canonical CAST / MKALF uses:

- DELCX
- exact predicates
- symbolic perturbation / SoS

Our native path still uses:

- `WeightedDelaunayMesh`
- built from a lifted convex-hull route with `scipy` / `Qhull`

This is not a cosmetic difference. It means the actual regular triangulation is
not guaranteed to be the same as the historical one, even with the same atoms,
coordinates, and radii.

Why this is conceptually important:

- all later topology is built on this triangulation
- local adjacency can change
- attachedness and hiddenness can change
- sink / depth structure can change
- mouth topology can change

Current judgement:

- this remains a **primary conceptual gap**
- and it is still the strongest single reason we cannot yet claim literal
  identity with MKALF

### 2. Exact rank semantics are closer, but not yet proven identical

The native code now builds exact `rho` event ratios for:

- tetrahedra
- faces
- edges
- vertices

and groups equal ratios before assigning ranks.

That is conceptually the right direction, but the following points remain open:

1. the exact event ordering is still represented downstream only through
   `spectrum_values` as floats plus assigned integer ranks
2. helper thresholds such as `_rank_of_value(...)` and `_probe_rank(...)` still
   recover ranks from float values via `searchsorted`
3. we have not yet proved that this reproduces all historically relevant rank
   separations of MKALF in medium and difficult cases

Conceptual implication:

- even if our exact ratio grouping is much better than before, the full rank
  scale is still not demonstrated identical to MKALF's operational one

Current judgement:

- still a **primary conceptual gap**

### 3. `mu1` / `mu2` are still reconstructed, not ported literally

Conceptually, our code now respects the correct semantics:

- `rho != 0 -> rho <= rank`
- `rho == 0 -> mu1 <= rank`
- `interior -> mu2 <= rank`

and the propagation direction is the right one:

- tetra -> triangle
- triangle -> edge
- edge -> vertex

But the implementation is still a Python reconstruction over our own mesh
representation and our own rank tables.

What is still not literally identical:

- the historical face/edge/vertex indexing machinery
- the exact interaction between attachedness and the master list
- the full predicate environment in which `mu1` / `mu2` are generated

Conceptual implication:

- membership and interior decisions may still diverge, even if the branch logic
  now looks historically correct

Current judgement:

- still a **primary conceptual gap**

### 4. Pocket construction still compresses MKALF's full state machine

The pocket builder is now much closer to `alf_init_pockets()` than it used to
be. However, it still compresses several historical structures into a more
compact Python routine:

- union-find parents
- delayed stacks by sink
- retained / outside simplex bookkeeping
- direct iteration helpers over our Python master-list mirror

This is not automatically wrong, but it means we still do not have a literal
state-for-state port of the original pocket-construction workflow.

The key conceptual point is:

- the algorithm is now much closer to canonical
- but we have not yet proved that our compressed state machine is equivalent to
  MKALF's one

Current judgement:

- still a **meaningful conceptual gap**
- below triangulation / rank / `mu` in priority

### 5. Mouth seeding is close, but still not literally `alf_scan_pocket_f1()`

Our current `_component_boundary_faces()` uses the correct conceptual rule:

- triangle not in complex at `rank1`
- opposite tetrahedron absent or outside the current pocket

This is the right rule. However, the seed set is still derived through our own
component representation and neighbor interpretation, not by a literal scan over
historical `TrIndex` structures.

Conceptual implication:

- the rule is right
- but the exact seed set is not yet formally proven identical to MKALF

Current judgement:

- still open
- but no longer one of the most worrying gaps

### 6. The `Fnext` path is now structurally close, but still not a literal edge-facet implementation

The mouths path has improved a lot. We now have:

- `MouthFaceRecord`
- `EdgeFacetRecord`
- explicit outward mouth orientation
- explicit `Enext`
- explicit `Fnext`
- triangle identity preserved through the walk
- input canonicalization that fills triangle identity whenever the mesh can
  resolve it

This is conceptually much closer to MKALF than the old code.

But one conceptual difference remains:

- the walk still operates over a Python reconstruction of edge-facets on top of
  tetrahedron-local face ownership
- not over the original `trist` edge-facet structure itself

This matters because:

- `TrIndex`
- `Fnext`
- `Enext`
- `Sym`

are primitive in MKALF, while in our code they are still emulated.

Current judgement:

- still open
- but now a **fine** conceptual gap, not the large one it was before

### 7. Reporting semantics are still conceptually incomplete

This is one place where the audit should be strict.

The CAST papers and MKALF reporting logic imply explicit treatment of:

- atoms lining pockets
- atoms lining mouth openings
- interior vs regular vertices / edges / faces
- pocket / cavity geometry
- mouth geometry including area and circumference

Our current feature records still do **not** fully reproduce that reporting
layer.

Examples of current incompleteness:

- we do not expose the full `iV/rV`, `iE/rE`, `iF/rF` partition
- mouth records carry area, but not the full historical mouth geometry contract
  such as circumference
- our feature records are still `TopoMT`-style records, not a literal mirror of
  MKALF's reporting state

This is not only presentation. It is part of the canonical CAST output model.

Current judgement:

- still a **real conceptual gap**
- secondary for pocket topology, primary for full CAST fidelity claims

### 8. Non-canonical fallback paths still exist in the codebase

There are still fallback branches intended for tests, legacy callers, or
reduced-data execution paths. Examples:

- fallback mouth clustering by simple shared-edge adjacency
- fallback identity by `face_atoms`
- compatibility paths when the full mesh-side identity layer is absent

These are useful engineering fallbacks, but they are not part of the canonical
CAST algorithm.

As long as they remain isolated from the real native path, they are acceptable.
But conceptually they should still be counted as:

- non-canonical code paths that exist in the implementation

Current judgement:

- lower-priority conceptual gap
- worth keeping in mind during future cleanup

## Summary judgement

### What is conceptually closest now

The following layers are now close enough that they should no longer dominate
our concern:

- solvent inflation
- `rho0`
- no-`mu` spectrum construction
- non-wrapping pocket depth semantics
- rank-driven pocket admission
- the overall mouth-construction architecture

### What still prevents a strict fidelity claim

If we ask, strictly:

> Are we already doing conceptually 100% the same thing as canonical CAST?

the answer is still **no**, mainly because of these fronts:

1. DELCX / SoS triangulation is still not our substrate
2. exact rank semantics are still not fully demonstrated identical
3. `mu1` / `mu2` are still reconstructed, not literally generated by the
   historical machinery
4. pocket construction is still a compressed Python state machine
5. reporting semantics are still incomplete

### Ranking of remaining conceptual gaps

If we rank what still matters most conceptually, the order is now:

1. triangulation / SoS substrate
2. exact rank semantics
3. literal `mu1` / `mu2` semantics
4. literal pocket construction state machine
5. reporting semantics
6. literal mouth seeding / edge-facet combinatorics
7. fallback non-canonical auxiliary paths

## Recommended discipline for the next phase

The correct discipline from here is:

1. do not optimize against case residuals first
2. close conceptual gaps from the list above
3. only then return to case-based parity to separate:
   - `TopoMT vs MKALF`
   - from `MKALF vs CASTp 3.0`

This is the right order because at this point the main risk is no longer "wrong
geometry everywhere", but rather claiming canonical fidelity while still having
some structural layers that are only approximations or compressed
reconstructions of the original algorithm.
