"""Canonical gap audit for the native CASTp implementation."""

# Canonical Gap Audit

Date: 2026-04-16

## Purpose

This document consolidates the current rigorous audit of the native CASTp
implementation against:

- the original MKALF / CAST code in `../Alphashape/castp/alpha-4.1-src/mkalf`
- the 1998 CAST papers in `~/castp/On_1998.pdf` and
  `~/castp/Anatomy_1998.pdf`

The goal is not to explain parity results case by case, but to state as clearly
as possible:

1. what the canonical algorithm actually requires
2. what our current code still does differently
3. the full current list of plausible canonical gaps

This is the baseline for the next implementation round.

## Canonical Contract

The canonical contract supported jointly by the papers and by MKALF is:

- pockets and cavities are defined on the weighted Delaunay / alpha-shape
  substrate
- the spectrum is built from `rho` events only
- `mu1` and `mu2` are derived after spectrum construction and then govern
  attached-face membership and interior status
- pockets are not built by simple connected components of "empty tetrahedra";
  they are built by rank-driven insertion, depth / sink propagation, and
  delayed insertion through sinks
- mouths are not grouped by naive shared-edge adjacency; they are grouped by
  the `Fnext` walk around open edges
- pocket reporting distinguishes:
  - tetrahedra in the pocket
  - regular mouth triangles / edges / vertices
  - interior triangles / edges / vertices
  - atoms lining the pocket and atoms on the mouth rim

The papers give the public conceptual contract:

- CAST is based on alpha shapes and discrete flow
- pockets are regions of the complement with limited accessibility from the
  outside
- mouth openings are explicit geometric objects
- pocket and mouth atoms are part of the reported result

MKALF then fixes the operational semantics.

## What We Already Brought Closer To Canonical

The following fronts are no longer considered primary gaps:

- `mu` is no longer inserted into the spectrum
- solvent inflation is aligned with the historical workflow
- `rho0 = -weight` is aligned with the weighted historical code
- mouth grouping no longer uses direct shape-edge union
- mouths now use oriented pocket-side faces and an `Fnext`-style walk
- mouth-face outward orientation is now explicit relative to `rank2`
- vertex reporting no longer comes only from boundary faces; it now tracks the
  historical `rV` idea more closely
- several former "red" systems (`1UBQ`, `2CBA`, `1TCD`) are now at least as
  close to canonical MKALF as the server output, so they are no longer good
  primary bug drivers

These improvements matter because the remaining gaps are now narrower and more
structural.

## Main Canonical Differences Still Present

### 1. Triangulation substrate is still not DELCX / SoS

Canonical:

- MKALF sits on DELCX and symbolic perturbation / exact predicates.

Current native code:

- `WeightedDelaunayMesh` is built from a lifted convex hull with `scipy` /
  `Qhull`.

What this means:

- even with identical atoms, coordinates, radii, and fixed-point input, we can
  still get a different regular triangulation
- local adjacency, attachedness, and flow can therefore diverge

Current status:

- this is real, but it is not the whole story
- in some audited cases the tetrahedra that matter are present in both MKALF and
  TopoMT, so residuals survive even when the key local tetrahedra are shared

Conclusion:

- triangulation remains a genuine canonical gap
- but it is not sufficient by itself to explain all remaining divergences

### 2. Spectrum semantics are still not fully demonstrated to match MKALF

Canonical:

- `spectrum.c` builds the spectrum from `rho` events only
- ordering is not a plain float sort; it follows the exact ratio comparisons
  used by MKALF

Current native code:

- we have introduced `ExactRatio` and now rank `rho` events more faithfully than
  before
- but full equivalence to the historical ordering is not yet proven

Why this still matters:

- `base_rank`
- simplex / face / edge / vertex `rho` ranks
- and therefore all `alf_is_in_complex(...)` style decisions
  depend on this scale

Conclusion:

- this remains a primary canonical front
- the direction is correct, but equivalence is not yet closed

### 3. Attached-face semantics still rely on reconstructed proxies

Canonical:

- `alf_is_in_complex` and `alf_is_interior` use the historical `rho`, `mu1`,
  `mu2` tables
- attachedness is defined by `rho == 0` and then membership depends on `mu1`

Current native code:

- face / edge / vertex `mu1` and `mu2` are reconstructed from the Python mesh
- this is much closer than before, but still a reconstruction, not a literal
  port of the historical rank machinery

Why this matters:

- open-vs-closed boundary decisions
- pocket unions across faces
- mouth-edge openness
- interior-vs-regular reporting

Conclusion:

- this remains one of the central plausible causes of residual mismatch

### 4. Pocket construction still compresses the historical workflow

Canonical:

- `alf_init_pockets(rank1, rank2, do_wrap)` scans the master list by rank
- uses `depth` / `wrapping_depth`
- delays tetrahedra by sink
- unions tetrahedra only through faces not in the `rank1` complex

Current native code:

- `_build_rank_driven_components()` does follow the same general logic
- but it still wraps the original machinery into a more compact Python
  reconstruction
- the explicit preselection of pocket tetrahedra through an "empty simplex mask"
  has now been removed from the pocket admission step

This is suspicious because:

- the historical algorithm is not phrased as "build components from an empty
  simplex mask"
- it is phrased as rank-driven insertion plus sink logic

Conclusion:

- even if the current component builder is much closer than earlier versions,
  this area is still not proven canonical
- the remaining open question is now the literal fidelity of the rank-driven
  insertion and delay-stack machinery

### 5. Hidden-triangle / flow predicates are closer, but not fully closed

Canonical:

- `hidden_triangle()` in `voids.c` combines:
  - attachedness (`rho == 0`)
  - `mu1` vs tetrahedron `rho`
  - and `alf_hidden2(...)`

Current native code:

- `_hidden_triangle()` follows the same branch structure
- `hidden1` and `hidden2` are now evaluated with exact fixed-point determinant
  predicates rather than floating-point geometry
- but the full DELCX / SoS predicate environment is still not present

What remains open:

- full DELCX / symbolic perturbation semantics
- exact agreement of "problem tetrahedra" handling
- proof that all remaining attachedness decisions match the historical code on a
  representative case set

Conclusion:

- this is still a live canonical gap, especially for small residuals

### 6. Mouth seeding and mouth membership are still not a literal port

Canonical:

- `alf_scan_pocket_f1()` defines the regular mouth triangles for the current
  pocket structure
- `alf_init_mouths()` starts from those seeds and uses oriented edge-facets plus
  `Fnext`

Current native code:

- `_component_boundary_faces()` derives mouth faces from component boundaries
  plus blocked / exterior neighbors
- `cluster_mouth_faces()` then applies an `Fnext`-style walk

This is improved, but still not identical to the historical pipeline because:

- seed selection is ours, not literally `alf_scan_pocket_f1`
- mouth membership still depends on our component reconstruction upstream

Conclusion:

- mouth grouping is no longer the crude heuristic it was
- but mouth seeding still remains a plausible gap

### 7. Reporting semantics for `iV/rV`, `iE/rE`, `iF/rF` are only partially mirrored

Canonical:

- MKALF explicitly distinguishes:
  - interior vertices / edges / faces
  - regular mouth vertices / edges / faces

Current native code:

- the final `Topography`-side records do not yet expose the full historical
  face/edge/vertex partition
- `boundary_atom_indices` is closer to `rV`, but we still do not materialize the
  full intermediate reporting structure that MKALF computes

Why this matters:

- some residuals may be reporting mismatches rather than pocket-topology
  mismatches
- CASTp 3.0 may also enrich or reinterpret these outputs further

Conclusion:

- this is a real but secondary canonical gap

### 8. The native implementation still uses CASTp-specific feature typing on top of MKALF-like geometry

Canonical:

- MKALF gives pocket sets and mouth counts
- CAST / CASTp then report pockets, channels, and branched channels by mouth
  structure

Current native code:

- final typing is:
  - `1 -> pocket`
  - `2 -> channel`
  - `>= 3 -> branched_channel`

This is plausible and often correct, but we still do not have evidence that
CASTp 3.0 applies no further normalization on:

- tiny openings
- merged neighboring openings
- or reporting thresholds

Conclusion:

- this is not the first place to look for big canonical errors
- but it remains open at the MKALF-vs-CASTp3 boundary

## Full Current Hypothesis List

Ordered from highest-value canonical fronts to lower-priority ones.

1. The regular triangulation substrate still differs from DELCX / SoS in ways
   that matter for some systems.
2. The exact ordering and rank assignment of `rho` events is still not fully
   equivalent to MKALF.
3. The reconstructed `mu1/mu2` tables for attached simplices are not yet
   guaranteed to match the historical tables.
4. `_hidden_triangle()` may still differ from the historical flow behavior in
   degenerate or near-degenerate cases even though the underlying `hidden1` /
   `hidden2` predicates are now exact.
5. `_component_boundary_faces()` may still not reproduce `alf_scan_pocket_f1()`
   exactly.
6. `cluster_mouth_faces()` is closer to `alf_init_mouths()`, but still depends
   on upstream seed selection and our own mesh representation.
7. Final reporting of regular/interior vertices and mouth atoms is only a
   partial mirror of MKALF reporting.
8. Some residual server mismatches are not defects of the native code at all,
    but real `MKALF 4.1 vs CASTp 3.0` differences.

## What We Should Not Misdiagnose Anymore

The following are no longer good primary explanations:

- `mu` missing from the spectrum
- solvent inflation
- `rho0`
- `rank2 = max_rank` for pocket construction
- wrapping-depth semantics inside the non-wrapping pocket path
- naive mouth union by shape edges
- hull-edge `mu2` zeroing happening in the wrong phase of `edge_mus`
- mouth seeds filtered by extra depth logic instead of literal `f1` selection
- `Fnext` walk not stopping when the next tetrahedron was outside the `rank2`
  shape
- `1UBQ` as a clean native-bug case
- `2CBA` as a clean native-bug case
- `1TCD` as a clean native-bug case

These fronts were useful earlier, but the audit no longer supports keeping
them near the top of the list.

## Recommended Next Work Pattern

The next iteration should not proceed by local patching. It should proceed by
closing the canonical fronts in this order:

1. spectrum / rank semantics
2. exact predicate layer and attached-simplex ranks
3. mouth seed equivalence to `alf_scan_pocket_f1`
4. reporting equivalence for `iV/rV`, `iE/rE`, `iF/rF`
5. only then re-open case-by-case analysis on the best diagnostic systems

Case selection after this audit:

- `3PTB`: still useful
- `4CHA`: good stress case, not clean
- `1AKE`: mixed control

Cases currently better interpreted as `MKALF-vs-CASTp3` or at least not clean
native-bug drivers:

- `1UBQ`
- `2CBA`
- `1TCD`

## Bottom Line

The remaining gap is no longer well described as "our mouths are wrong" or
"our pockets are fragmented." Those were earlier symptoms. The deeper current
picture is:

- we are already much closer to MKALF than before
- but several layers of the historical algorithm are still represented through
  Python reconstructions rather than literal canonical machinery
- the largest remaining fronts are now structural:
  triangulation, rank semantics, attached-simplex tables, and master-list style
  pocket construction

That is the working hypothesis set for the next round.
