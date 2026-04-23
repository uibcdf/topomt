# CASTp Checkpoint 2026-04-11: Spectrum and Rank Audit

## Purpose

This checkpoint records the result of the next audit round after the
vertex-materialization step.

The goal of this round was not to propose another local fix. The goal was to
verify whether the remaining `1ubq` residual still pointed to:

- mouth logic,
- pocket assembly,
- local reporting,
- or something more basal in the native reconstruction.

The answer is now much clearer:

- the dominant remaining gap uncovered by `1ubq` is in the reconstruction of
  the CAST / MKALF `spectrum` and therefore in the derived rank tables;
- the current native path is assigning plausible geometric `rho` values but
  non-canonical rank positions to some simplices;
- that rank drift then propagates into `base_rank`, `mu1`, `mu2`, and all
  `alf_is_in_complex(...)`-style predicates.

## Short conclusion

The current native residual in `1ubq` is **not** best explained as:

- a missing local union,
- a missing reporting atom,
- or a small mouth-clustering defect.

The dominant issue uncovered in this round is:

- **the native path does not yet reconstruct the historical spectrum/rank
  indexing faithfully**.

This is now the highest-priority canonical gap.

## What was corrected in the audit itself

### 1. The historical `.poc` indices are 1-based relative to the native mesh

Earlier local reasoning around the `1ubq` residual mixed:

- historical MKALF vertex indices from `.poc`
- and native local indices from `WeightedDelaunayMesh`

as if they were on the same base.

That was wrong.

The historical `.poc` vertex IDs are 1-based, while the native mesh uses
0-based local indices. Re-aligning these indices removed a large amount of
false local certainty about which tetrahedra were supposedly corresponding.

This matters because several earlier local hypotheses were formulated around a
misaligned tetrahedron neighborhood.

### 2. The real `1ubq` residual was re-identified correctly

After re-aligning the indices, the residual is:

- oracle `POC-6`: 12 atoms
- native `pocket 2`: 11 atoms
- exact difference: the native pocket is missing atom `299`
- plus one extra tiny native pocket of 4 atoms

So the true residual is smaller and cleaner than the earlier misaligned story.

## Main evidence

### A. `1ubq` oracle vs native pocket comparison

Using mapped system atom indices:

- oracle `POC-6`:
  `[297, 299, 300, 301, 307, 566, 568, 569, 582, 586, 587, 588]`
- native `pocket 2`:
  `[297, 300, 301, 307, 566, 568, 569, 582, 586, 587, 588]`

Only one atom is missing from the near-match pocket:

- `299`

This pocket-level comparison is now aligned correctly.

### B. The missing atom is not present in any tetrahedron of the native pocket component

For the true near-match native pocket:

- the pocket component tetrahedra are:
  `57, 74, 75, 2078, 2081, 2082, 2133, 2930, 2939, 2941, 2944, 2945`
- local atom `299` is not present in any of these tetrahedra

The atom does exist in nearby tetrahedra in the native mesh, but those
tetrahedra are outside the current component.

This confirms that the residual is topological / rank-driven upstream of final
feature reporting.

### C. The lower-threshold hypothesis changed

This audit also corrected another earlier over-strong claim.

It is **not** generally true that:

- `alf_rank(0.0)` should be read as rank `1`

for the native weighted case.

For `1ubq`, the native spectrum gives:

- `base_rank = 5796`
- `rank_of_0 = 5796`

because `0.0` falls in the middle of the weighted spectrum, not below the
first entry.

This means:

- the old idea "the lower threshold should simply be `1`" is not the right
  global correction
- and the manual MKALF printout with `rank 1` should not be treated as the
  canonical oracle for the standard pocket workflow

### D. Historical MKALF with the same native rank pair still contains the missing-atom pocket

The local historical toolchain was run for `1ubq` with:

- `rank1 = 5796`
- `rank2 = 7188`

which is the pair currently used by the native method:

- lower threshold = `base_rank`
- upper threshold = last rank

At that same historical rank pair:

- MKALF still reports a pocket containing the shifted equivalents of the
  missing-atom region
- in particular, the historical pocket block contains tetrahedra equivalent to
  the missing-atom subregion

So the residual is **not** explained by:

- "the native rank pair is different from the historical one"

at least not at the high-level `rank1/rank2` choice.

### E. The decisive discrepancy is in rank assignment, not in raw `rho` values

This is the key result of the round.

For tetrahedra in the historical pocket containing the missing atom:

- the native `rho_value` matches the historical threshold numerically
- but the native `rho_rank` is far too low relative to the historical rank

Examples:

1. Native tetrahedron `(295, 298, 294, 284)`
   - native `rho_value = -3.5529739828632003`
   - native `rho_rank = 4475`
   - historical master list places the corresponding tetrahedron at
     `Rank [5861]`

2. Native tetrahedron `(298, 300, 284, 302)`
   - native `rho_value = -2.8290432054321384`
   - native `rho_rank = 5061`
   - historical master list places the corresponding tetrahedron at
     `Rank [6466]`

This means:

- the geometry value is already close enough
- the rank indexing is not

This is the most important current result.

### F. The native `base_rank` is also inconsistent with the historical filter crossing of `0.0`

From the historical `1ubq` master list:

- last negative threshold: `Rank [7215] = -0.02877626`
- first non-negative threshold: `Rank [7216] = 0.06993881`

Therefore the historical alpha-rank containing `0.0` lies between:

- `7215` and `7216`

But the native geometry currently uses:

- `base_rank = 5796`

So even the current lower alpha threshold in the native path is being read from
the wrong rank scale.

That is consistent with the tetrahedron-rank drift above.

## First correction of the audit itself

One important interpretation from the first version of this audit was wrong and
has already been corrected.

It is **not** true that `spectrum.c` expands the historical `spectrum` by
inserting `mu1` and `mu2` values as extra spectrum events.

What `spectrum.c` actually does is:

- `rho`
  events only are collected, sorted, and stored in `spectrum[1..ranks]`;
- `mu1` and `mu2` are computed **afterwards** as ranks induced by those already
  sorted `rho` events.

This matters because a short-lived code change attempted to add `mu1` and
`mu2` values into the native `spectrum_values`. That change was not canonical
and has been removed.

## What survived that correction

After removing the non-canonical `mu`-in-spectrum change, the native `1ubq`
status remained:

- oracle counts: `void = 3`, `pocket = 9`
- native counts: `void = 3`, `pocket = 4`
- `void` exact matches: `3/3`
- `pocket` exact matches: `0/9`

And the native weighted geometry still reports:

Observed consequence in `1ubq`:

- native spectrum size: `7188`
- historical spectrum size: `8436`
- native zero crossing:
  - last negative rank: `5796`
  - first non-negative rank: `5797`
- historical zero crossing:
  - last negative rank: `7215`
  - first non-negative rank: `7216`

So the native rank axis is still compressed relative to MKALF, but **not**
because `mu` events are missing from the historical spectrum.

## Why the checkpoint still matters

Even after correcting that false lead, the checkpoint result remains useful:

- the dominant residual is still upstream of pocket reporting;
- the native rank axis is still not aligned with the historical one;
- and the next correction should no longer target `mu` insertion into the
  spectrum.

The current leading candidates are now narrower:

- a remaining mismatch in how weighted `rho` events themselves are reproduced;
- or another canonical discrepancy upstream of rank consumption, such as the
  geometric substrate used to build those `rho` values.

## Later correction: `1ubq` residual split into MKALF-vs-CASTp3 and native gaps

The first version of this checkpoint still over-attributed the remaining
`1ubq` red case to native rank reconstruction.

That is no longer the right interpretation.

After a more careful cross-check against:

- the canonical MKALF master list `/tmp/1ubq_protor.dat.ml`,
- a canonical MKALF pocket printout generated with
  `print pockets rank 7216 rank2 8436`,
- the CASTp 3.0 ZIP oracle,
- and the current native output,

the situation is now clearer:

- the native exact-ratio / exact-ordering work **did** substantially improve
  `1ubq`;
- the current native output reaches:
  - `void`: `3/3` exact
  - `pocket`: `8/9` exact
- the remaining near-match native pocket is:
  `[297, 300, 301, 307, 566, 568, 569, 582, 586, 587, 588]`
- the remaining CASTp 3.0 oracle pocket is:
  `[297, 299, 300, 301, 307, 566, 568, 569, 582, 586, 587, 588]`

The crucial finding is that the canonical MKALF pocket printout at:

- `rank1 = 7216`
- `rank2 = 8436`

contains a pocket whose lining-atom set matches the native near-match pocket,
not the CASTp 3.0 oracle pocket. In 1-based indexing, the canonical MKALF
pocket is:

- `{298, 301, 302, 308, 567, 569, 570, 583, 587, 588, 589}`

which corresponds exactly to the native 0-based set:

- `{297, 300, 301, 307, 566, 568, 569, 582, 586, 587, 588}`

and still lacks atom `299` (1-based `300`), just like the native output.

This changes the interpretation of the residual:

- the remaining `1ubq` fine mismatch is **not** best described as a simple
  native implementation bug in local pocket assembly;
- for this case, the current native output is already matching canonical
  MKALF more closely than CASTp 3.0 does;
- therefore the unresolved difference is now best classified as a
  **MKALF-vs-CASTp-3.0 divergence**, not as a confirmed native defect.

This later comparison also clarified two nearby `1ubq` details:

- the extra tiny native pocket
  `{12, 15, 122, 124}`
  matches canonical MKALF `Pocket 4`;
- the short native pocket
  `{300, 307, 309, 582, 586, 591}`
  differs from canonical MKALF `Pocket 7` by one atom, but CASTp 3.0 also
  differs from that same MKALF pocket by one atom in the same local region.

So, for the `1ubq` open-feature neighborhood around `POC-6` / `POC-7`, the
current evidence no longer supports treating the remaining mismatch as a
high-priority native defect.

What still remains valid from this checkpoint:

- native rank reconstruction was a real canonical issue and needed work;
- exact ordering infrastructure was still the right direction;
- and the old `/tmp/1ubq_protor.dat.5796.7188.poc` printout should not be used
  as the canonical oracle, because it was generated with the native rank pair,
  not with the historical MKALF zero cutoff.

## Consequence for previous hypotheses

### Weaker now

These are not eliminated, but they are no longer the best first explanation of
the `1ubq` residual:

- local mouth-clustering defects
- local component-assembly defects
- ad hoc reporting-layer atom loss

### Still relevant, but now downstream

- `Fnext` fidelity
- mouth grouping
- tiny-pocket reporting

These may still matter later, but they should now be treated as **downstream of
the rank reconstruction problem**, not upstream of it.

## Other audited differences that should remain on the radar

This round also reinforces a few other differences from the historical sources
that are not the first priority now, but should not be forgotten.

### 1. `components.py` still uses a pre-filter mask not present in the historical C

The current native path still begins open-feature work through
`_build_empty_simplex_mask()`.

Historical `alf_init_pockets()` does not start from that kind of explicit mask.
It traverses the master list between `rank1+1` and `rank2` and processes
tetrahedra incrementally.

This may still matter once the spectrum/rank reconstruction is fixed.

### 2. `Fnext` and edge-facet semantics are still reconstructed, not literally ported

This remains true.

The current implementation is much closer to MKALF than before, but it is still
not a literal port of the historical data structure.

This should be revisited only after the rank scale is corrected.

### 3. CASTp reporting semantics may still include a later normalization layer

The `Anatomy of protein pockets and cavities` paper emphasizes:

- pocket atoms
- mouth rim atoms
- mouth area / circumference

and distinguishes the topological pocket from the measurement / reporting
layer.

That still leaves open the possibility that CASTp 3.0 applies some reporting
normalization beyond historical MKALF. But this is no longer the first
explanatory hypothesis for the `1ubq` residual.

## Updated priority

The next canonical implementation pass should focus on:

1. reconstructing the spectrum according to `spectrum.c`
2. including the historical `rho`, `mu1`, and `mu2` events in the rank scale
3. recomputing all derived rank tables from that canonical spectrum
4. only then re-evaluating:
   - `1ubq`
   - the short green battery
   - and the medium red cases

## Recommended interpretation for the next iteration

Do **not** treat the current `1ubq` residual as evidence for:

- a local pocket-union patch
- a special-case atom materialization rule
- or a standalone mouth fix

Treat it as evidence that:

- the native rank scale is still not the historical one
- and that this is now the most important remaining canonical defect
