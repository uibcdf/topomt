# CASTp Failure Analysis 2026-04-10

## Purpose

This document is a focused failure analysis of the current native CASTp path.

It is not a changelog. It is an attempt to answer:

- what the native implementation is getting right
- what it is getting wrong
- and what hypotheses best explain the remaining mismatches

It is based on the measured battery summarized in:

- [native_parity_matrix_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/native_parity_matrix_2026_04_10.md)

## Current state by feature family

### 1. `void`

Current state:

- comparatively strong
- often exact
- often exact even when open-feature taxonomy is poor

Why this matters:

- it argues against a global breakdown of the weighted geometry
- it argues against the complement/exterior logic being the dominant current
  failure
- it suggests the native method already captures a large fraction of the
  closed-region structure correctly

Residual `void` mismatches exist, but they do not define the dominant pattern
of failure.

### 2. `pocket`

Current state:

- strongly undercalled

Observed effect:

- many oracle `pocket` features appear in the native result as `channel` or
  `branched_channel`

Interpretation:

- the native method is not necessarily missing the spatial region
- it is often assigning too many mouths to that region

This is one of the most stable signatures in the battery.

### 3. `channel`

Current state:

- overcalled

Observed effect:

- systems with few oracle channels frequently yield multiple native channels

Interpretation:

- the native path is too eager to classify open features as multi-mouth
  openings
- this is likely downstream of mouth partitioning, not an independent problem

### 4. `branched_channel`

Current state:

- correctly supported as a feature type
- but heavily overcalled

This is important because it separates two questions:

1. Should `branched_channel` exist in the native model?
   - yes

2. Is the current native method using it too often?
   - also yes

This again points back to over-fragmented mouth counts.

### 5. `mouth`

Current state:

- this remains the main unresolved layer

The battery suggests that the native path still partitions openings more finely
than CASTp 3.0 does.

This is the most plausible common cause of:

- `pocket` undercalling
- `channel` overcalling
- `branched_channel` overcalling

## Main repeated failure pattern

The dominant repeated pattern is:

1. `voids` are exact or nearly exact
2. open-feature taxonomy is still poor
3. the native method shifts oracle `pocket` features upward into
   `channel` / `branched_channel`

This pattern appears across:

- compact small proteins
- enzymes with deep active-site pockets
- proteases
- cavity-rich systems

So the failure does not look like one single family-specific bug.

## Hypotheses

The following hypotheses are ordered from most plausible to less plausible,
based on the current evidence.

### Hypothesis 1: mouth partitioning is still too fine

This is the leading hypothesis.

Even after removing direct shape-edge union and moving closer to the MKALF
logic, the native method still appears to split openings that CASTp 3.0 treats
as a single mouth.

Why it fits the evidence:

- it explains the systematic shift from `pocket` to `channel`
- it explains the systematic shift from `channel` to `branched_channel`
- it fits small red cases such as `1stp`
- it does not require a global failure in geometry or void detection

### Hypothesis 2: CASTp 3.0 applies an additional mouth-grouping rule beyond MKALF 4.1

This is also very plausible.

Earlier work already showed that CASTp 3.0 is not identical to MKALF 4.1.
The expanded battery reinforces that point.

Possible forms of this additional rule:

- merging nearby mouth components
- suppressing degenerate or tiny openings
- using a post-pass on mouth triangles not visible in the simple MKALF walk
- or a changed interpretation of regular mouth simplices

This hypothesis is consistent with the fact that "more literal MKALF" did not
automatically produce CASTp 3.0 parity.

### Hypothesis 3: the native path still lacks some orientation- or edge-facet-level detail in mouth walks

This remains plausible, though weaker than before.

The weighted mesh orientation problem was real and has now been fixed.
However, it is still possible that the current Python representation does not
fully capture all the edge-facet semantics used by the historical C code.

If true, this would most likely matter in small red mouth-partition cases.

### Hypothesis 4: some open-feature residuals come from CASTp-3.0-specific postprocessing, not from core alpha-shape topology

This is plausible and should remain on the table.

The native path may already be close to the core topological construction while
still missing a later server-side normalization step that affects how pockets
are reported.

That would explain why:

- the feature region can be approximately right
- but the reported final class still differs

### Hypothesis 5: the main problem is the weighted geometry itself

This is currently weak as a leading explanation.

Why it is not favored:

- `void` parity is too good
- many systems show good or at least plausible open-feature regions
- the dominant errors are taxonomic rather than purely geometric

Geometry still matters, but it does not currently look like the first place to
intervene.

## What is likely not the main problem

These are not impossible contributors, but they do not fit the dominant
observed pattern.

### Not mainly a `void` algorithm problem

If `voids` were globally broken, the battery would not show so many cases with
exact `void` parity alongside poor open-feature parity.

### Not mainly a total failure of weighted triangulation

The system-level picture is too structured for that. The failures are not
random; they cluster strongly in mouth-driven taxonomy.

### Not mainly the absence of `branched_channel`

That feature type now exists and is used. The problem is not missing support;
the problem is overproduction.

## Best current explanatory summary

The current native implementation seems to do this:

1. recover much of the weighted topographic geometry correctly
2. recover many `void` features correctly
3. recover many open-feature regions approximately correctly
4. then partition or interpret the mouths too aggressively
5. which inflates `channel` and `branched_channel`
6. and correspondingly shrinks the `pocket` population

This is the most coherent explanation of the battery as a whole.

## Consequence for next work

The next work should be designed around failure mechanism, not around feature
label counts alone.

That means:

- do not immediately redesign void logic
- do not immediately redesign the whole weighted geometry
- do not immediately collapse `branched_channel` support

Instead:

- study a small set of red cases with exact or near-exact `void` recovery
- inspect how oracle mouths must be grouped to recover the oracle taxonomy
- and determine what extra rule CASTp 3.0 is applying that the native path
  still lacks

## Recommended red-case set for the next diagnostic round

Most useful small or medium systems:

- `1stp`
- `1rop`
- `2pk4`
- `1ubq`
- `2lyz`
- `1lyz`
- `2cba`
- `3ks3`
- `1ake`

These are better diagnostic targets than immediately escalating to the largest
or noisiest systems.

## Bottom line

The native CASTp path is not blocked by a totally unknown failure anymore.

The battery supports a relatively specific diagnosis:

- `voids` are comparatively healthy
- open-feature regions are often at least partially present
- the main systematic failure is in mouth-driven open-feature taxonomy
- and the best current explanation is that CASTp 3.0 groups mouths more
  coarsely or more selectively than the current native implementation does

That is the failure analysis as of 2026-04-10.
