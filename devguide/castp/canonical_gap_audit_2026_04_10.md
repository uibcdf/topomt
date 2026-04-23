# CASTp Canonical Gap Audit 2026-04-10

## Purpose

This document records the current audit of the native CASTp path against:

- the historical MKALF / CAST code
- the published CAST / CASTp literature
- and the current CASTp 3.0 server oracle

The goal is not to propose arbitrary fixes.

The goal is to identify:

- which differences from the original code are justified
- which differences are still suspicious
- which differences from the published method remain underdetermined
- and which hypotheses are most plausible before the next implementation pass

This document should be read together with:

- [native_parity_matrix_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/native_parity_matrix_2026_04_10.md)
- [failure_analysis_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/failure_analysis_2026_04_10.md)
- [checkpoint_2026_04_10_route_to_parity.md](/home/diego/repos@uibcdf/topomt/devguide/castp/checkpoint_2026_04_10_route_to_parity.md)

## High-level conclusion

The native implementation is no longer a loose CAST-like prototype.

It already reproduces a large part of the canonical geometry and much of the
closed-region topology correctly. This is visible in the strong `void` parity
across the local battery.

However, the native implementation still does not reproduce the canonical open
feature behavior of CASTp 3.0. The dominant gap is not global geometry. The
dominant gap is the interpretation and grouping of mouths, and therefore the
final `pocket` / `channel` / `branched_channel` taxonomy.

## What we do differently from the original code

### 1. We do not use the original DELCX / SOS triangulation machinery

Current native path:

- builds a weighted triangulation in Python through `WeightedDelaunayMesh`
- reconstructs simplex, face, and edge rank data from that representation

Historical code:

- uses the original DELCX / MKALF machinery with symbolic perturbation and a
  richer combinatorial representation

Assessment:

- this difference is justified architecturally
- it may explain some local residuals
- it does not, by itself, explain the repeated open-feature taxonomic bias

### 2. We reconstruct alpha-complex membership from derived rank tables

Current native path:

- computes `simplex_rho`, face `rho`, `mu1`, `mu2`, hull flags, and edge ranks
- reconstructs predicates such as "triangle in complex at rank"

Historical code:

- queries alpha-complex membership directly through its own internal data model

Assessment:

- this reconstruction is partly successful
- it appears good enough for much of `void` recovery
- it remains a plausible source of error for open-feature behavior, especially
  around attached faces and mouth-boundary interpretation

### 3. Our mouth walk is closer to MKALF than before, but still not literal

Current native path:

- no longer merges mouth faces directly by shared shape edge
- uses an `Fnext`-style walk over open edges
- still represents the walk through a simplified Python edge/face model

Historical code:

- orients mouth triangles outward
- iterates over the three oriented edge-facets
- only walks around edges that are not in the alpha complex at `rank1`
- unions mouths through the exact edge-facet combinatorics of `Fnext`

Assessment:

- removing direct shape-edge union was a correction toward the canonical logic
- but the current implementation is still an approximation of the original
  oriented edge-facet walk
- this remains one of the strongest plausible explanations of the residual gap

### 4. We expose `branched_channel` explicitly

Current native path:

- materializes `branched_channel` as an explicit feature type

Historical / server semantics:

- the server clearly distinguishes multi-mouth open features
- large-battery parity work shows that this type is real and should exist

Assessment:

- this difference is justified
- the problem is not the existence of `branched_channel`
- the problem is that the native path currently produces too many of them

## What we do differently from what is published

The published CAST / CASTp literature gives the right conceptual framework:

- weighted alpha shapes
- discrete flow
- pocket / cavity semantics
- and mouth-based classification of open regions

But the published papers do not fully define all implementation details needed
to reproduce the modern server output.

In particular, the publications do not completely determine:

- the exact grouping rule for mouth triangles
- whether very small or degenerate openings are suppressed or merged
- whether there is a later normalization pass on open features
- how CASTp 3.0 evolved beyond the historical MKALF 4.1 logic

Assessment:

- we are broadly aligned with the published method at the conceptual level
- but publication-level fidelity is not enough to guarantee CASTp 3.0 parity
- some of the remaining behavior must be inferred from the historical code and
  from the server outputs themselves

## What is already justified

The following differences are currently justified and should not be treated as
bugs by default:

- using a Python weighted triangulation substrate instead of reusing DELCX
- encapsulating geometry in `WeightedDelaunayMesh`
- exposing `branched_channel` in the native feature model
- using a modernized software structure instead of a literal port of the old C

These are design choices. They may carry implementation costs, but they are not
themselves evidence of conceptual drift.

## What is still suspicious

The following differences remain suspicious and are the most likely places where
our implementation still departs from the canonical behavior in a meaningful
way.

### 1. Mouth partitioning still appears too fine

This is the strongest repeated signal in the parity battery.

Observed effect:

- oracle `pocket` features become native `channel`
- oracle `channel` features become native `branched_channel`

Interpretation:

- the native path likely splits openings more aggressively than CASTp 3.0

### 2. The current `Fnext` logic may still be missing oriented edge-facet detail

Even after preserving tetrahedron orientation, the current Python walk may still
lack some of the local combinatorial detail used by MKALF.

This is especially plausible in small red cases where the feature region looks
reasonable but the number of mouths is still wrong.

### 3. Our complex-membership reconstruction may still be too permissive or too naive around mouth boundaries

This is plausible for:

- attached triangles
- hull-adjacent transitions
- and edge openness at `rank1`

The fact that `voids` perform much better than open features suggests that this
problem is local and taxonomic, not global.

### 4. CASTp 3.0 likely applies a post-rule beyond historical MKALF

The evidence collected so far strongly suggests that CASTp 3.0 is not simply
MKALF 4.1 exposed through a web server.

So even a more literal MKALF implementation may still fall short unless we also
identify whatever extra normalization CASTp 3.0 is applying to open features.

## What is likely not the dominant problem

These factors may still contribute, but they do not fit the dominant observed
pattern.

### Not mainly a global weighted-geometry failure

If the weighted geometry were globally wrong, `void` parity would not be as
strong and as stable as it currently is.

### Not mainly a total failure of complement / outside handling

Again, the `void` results are too structured and too often exact for that to be
the first explanatory hypothesis.

### Not mainly the absence of a `branched_channel` type

That type now exists and is meaningful. The issue is overproduction, not
absence.

## Best current interpretation

The most coherent current interpretation is:

1. the native path already recovers much of the canonical weighted geometry
2. it already recovers much of the closed-region topology
3. it often recovers the open-feature region approximately correctly
4. but it still partitions or interprets mouths too aggressively
5. which inflates `channel` and `branched_channel`
6. and correspondingly shrinks the `pocket` population

## Consequence for the next implementation phase

The next phase should not be driven by random heuristic edits.

It should be driven by a narrower canonicalization goal:

- reduce non-canonical behavior in the mouth logic
- make the open-feature logic more literal with respect to MKALF where possible
- and isolate which residual mismatches are specifically CASTp-3.0 evolutions

In practice this means:

1. continue narrowing the gap between the native code and the canonical MKALF
   mouth logic
2. identify any remaining non-canonical shortcuts or approximations in our
   current implementation
3. only then move to targeted red-case analysis on a small diagnostic set

## Recommended diagnostic set after canonicalization

The next small-case round should focus on systems where:

- `voids` are already exact or nearly exact
- but the open-feature taxonomy remains poor

Recommended set:

- `1stp`
- `1rop`
- `1ubq`
- `2lyz`
- `2pk4`

Second-line medium cases:

- `2cba`
- `3ks3`
- `1ake`

These are better diagnostic cases than immediately escalating to the largest and
noisiest systems.
