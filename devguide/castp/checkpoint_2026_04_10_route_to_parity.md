# CASTp Checkpoint 2026-04-10: Route To Parity

## Purpose

This document summarizes where the native CASTp implementation stands after the
first expanded parity battery on the local oracle systems, and what the most
probable route to parity now looks like.

It should be read together with:

- [native_parity_matrix_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/native_parity_matrix_2026_04_10.md)
- [checkpoint_2026_04_10.md](/home/diego/repos@uibcdf/topomt/devguide/castp/checkpoint_2026_04_10.md)

## The short version

The native CASTp path is no longer failing everywhere in a vague or global way.
It now shows a very specific profile:

- `voids` are comparatively strong
- `pockets` are undercalled
- `channels` are overcalled
- `branched_channel` is overcalled even more strongly
- `mouths` remain the main unresolved layer

So the next route to parity should not be "rewrite everything again". It should
be:

1. preserve the current weighted geometry and void construction
2. focus on the partition and grouping of mouth openings
3. only then revisit the final `pocket/channel/branched_channel` taxonomy

## Battery summary

Measured battery:

- `21` completed systems
- `1` input-path failure: `1crn`

Aggregate exact matches:

- `void`: `295 / 306`
- open features (`pocket + channel + branched_channel`): `124 / 405`

This is the clearest global conclusion from the expanded battery:

- the native path already captures much of the closed-feature structure
- but it still fragments open features too aggressively

## By feature family

### `void`

This is the strongest part of the native implementation.

Evidence:

- aggregate exact parity is high relative to the rest of the method
- many systems recover all or almost all oracle `voids`
- several red systems on open features still have exact `void` recovery

Interpretation:

- the weighted geometric substrate is not fundamentally broken
- the complement-style region detection is not the dominant current problem
- the remaining `void` mismatches are probably residual/local, not the central
  architectural blocker

Conclusion:

- do not treat `void` construction as the main thing to redesign next

### `pocket`

`pocket` is systematically undercalled.

Repeated pattern:

- the oracle labels many open features as `pocket`
- the native method often re-labels them as `channel` or `branched_channel`

Interpretation:

- in many cases the region itself is not completely lost
- what is wrong is the mouth/opening interpretation attached to that region

Conclusion:

- the dominant problem is not simply "native fails to find pockets"
- it is "native promotes too many pockets into higher-open-mouth classes"

### `channel`

`channel` is overcalled.

Repeated pattern:

- systems with few oracle `channel` features often produce many native
  `channel` features

Interpretation:

- the native method tends to split or count openings too aggressively
- a one-mouth oracle `pocket` can become a native two-mouth `channel`

Conclusion:

- `channel` overcalling is one of the clearest observable signatures of the
  remaining mismatch

### `branched_channel`

`branched_channel` now exists as a real native feature type, which is correct.
But it is also strongly overcalled.

This is important:

- adding `branched_channel` was the right move
- the issue is not that the type should not exist
- the issue is that the path reaches `n_mouths >= 3` too often

Interpretation:

- this is the same underlying failure as above, amplified
- mouth partitioning appears too fine-grained

Conclusion:

- keep `branched_channel`
- do not trust the current mouth-driven branching frequency

### `mouths`

This is the main unresolved layer.

The current evidence points here more strongly than anywhere else.

What is already fixed:

- the weighted triangulation now preserves tetrahedron orientation
- direct union of mouth faces by shared shape edge was removed
- the current clustering only uses `Fnext`-style open-edge connectivity

What remains wrong:

- CASTp 3.0 still groups some openings differently from the native method
- this difference propagates directly into `pocket/channel/branched_channel`
  mismatches

Conclusion:

- the route to parity now runs through mouth partitioning, not through a full
  restart of geometry or void logic

## Systems that are especially informative

The following systems are especially useful for the next round because they
show the repeated pattern "voids are fine, open features are not":

- `1stp`
- `1rop`
- `2pk4`
- `1ubq`
- `2lyz`
- `1lyz`
- `2cba`
- `3ks3`
- `1ake`

These are better route-to-parity targets than immediately jumping to the
largest or noisiest systems.

## Practical route forward

### Stage 1: preserve what is already strong

Do not destabilize:

- weighted Delaunay geometry
- oriented weighted tetrahedra
- current `void` construction
- native `branched_channel` support

### Stage 2: focus on mouths as the main parity bottleneck

The next technical question should be:

> Which mouth-grouping rule used by CASTp 3.0 merges or suppresses openings
> that the current native implementation still leaves separate?

This is now better motivated than any broad rewrite.

### Stage 3: use small red cases first

Recommended order:

1. `1stp`
2. `1rop`
3. `2pk4`
4. `1ubq`
5. `2lyz`

These should be used to answer the mouth-partition question before spending
time on large systems.

### Stage 4: only then revisit final taxonomy

If mouth grouping improves, then:

- many false `channel` calls may collapse back to `pocket`
- many false `branched_channel` calls may collapse back to `channel` or `pocket`

So the taxonomy layer should be revisited after the mouth layer, not before it.

## Bottom line

The native CASTp path is no longer in a diffuse exploratory state.

The battery now supports a much narrower roadmap:

- `voids` are comparatively healthy
- open-feature taxonomy is the weak point
- and the weak point is most likely driven by mouth grouping, not by the whole
  geometry or complement construction

That is the current route to parity.
