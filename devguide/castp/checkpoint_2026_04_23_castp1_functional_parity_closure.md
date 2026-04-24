# CASTp1 Functional Parity Closure

Date: 2026-04-23

## Decision

CASTp1 is considered functionally closed under the following parity contract:

- `pockets`
- `voids`
- `channels`
- `branched channels`
- `mouths`
- atom composition of each reported feature
- global metrics of each reported feature

Internal equality of triangulation, spectrum, or master-list is no longer the
primary pass/fail criterion as long as those internal differences do not change
the reported CASTp1 features or their metrics.

## What is already demonstrated on the clean CASTp1 benchmark

Against the clean local CASTp1 oracle regenerated from:

- `pdb2alf` with corrected string handling
- `delcx`
- `mkalf`
- `volbl`

the native path is green for:

- radii assignment on all 11 local benchmark systems
- reported `void` features on all 11 local benchmark systems
- reported open features instantiated by the MKALF pocket route on all 11 local
  benchmark systems
- atom composition of those reported features on all 11 local benchmark systems
- global VOLBL metrics on all 11 local benchmark systems within small numerical
  tolerance

In practice, this means the current native CASTp1 path reproduces the feature
objects that matter for use:

- buried features: `void`
- open features from the CASTp1 pocket route

## How `channel` and `branched_channel` fit into CASTp1 closure

For CASTp1, `channel` and `branched_channel` are not an independent geometric
construction separate from the pocket route. They are a reporting taxonomy
derived from the number of mouths of an open feature:

- `n_mouths == 1` -> `pocket`
- `n_mouths == 2` -> `channel`
- `n_mouths >= 3` -> `branched_channel`

The native code follows this rule directly, and this mapping is covered by
native regression tests.

Therefore, for CASTp1 closure, parity of `channel` and `branched_channel`
reduces to parity of:

- open-feature delineation
- mouth delineation and mouth counting
- feature atom composition
- feature metrics

## Important scope note

The current clean CASTp1 benchmark battery is strongest on:

- radii parity
- pocket/void feature recovery
- atom composition
- global VOLBL metrics

It is weaker as a dedicated stress battery for many multi-mouth open features.
So the closure claim is:

- strong for practical CASTp1 functional parity
- not a claim of internal DELCX/SoS bit-for-bit identity
- not yet a claim that the clean CASTp1 battery exhaustively stresses every
  `channel` / `branched_channel` corner case

This is acceptable because the phase goal is functional CASTp1 parity, not
strict internal triangulation identity.

## Residual non-blocking caveat

One internal discrepancy remains localized in `1hiv`:

- same effective vertices
- same reported features
- same practical metrics
- residual `+1` spectrum rank and `+7` master entries
- traced to a single local `2<->3` triangulation flip

This is now classified as a DELCX/SoS strict-fidelity caveat, not a blocker for
CASTp1 functional closure.

## Phase conclusion

CASTp1 can be considered closed under the functional parity contract above.

The next phase should be:

1. freeze or branch the current native CASTp1-faithful path
2. treat CASTp3.0 / CASTpFold as a separate parity target
3. carry forward the known differences in input policy first:
   - radii policy
   - water handling
   - any later server-side reporting differences

## Freeze convention for this repository

The repository currently has version tags:

- `0.1.0`
- `0.2.0`
- `0.3.0`

Therefore the clean freeze tag planned for the CASTp1-closure state should be:

- `0.4.0`

Important note:

- this tag should be created only from a curated clean commit
- it should represent the CASTp1 functional-parity baseline
- CASTp3.0 / CASTpFold work should start after that baseline is fixed in git

The original-build and clean-oracle recipe used to establish this CASTp1 phase
is recorded in:

- `devguide/castp/castp1_original_build.md`

The reproducible local CASTp1 source copy preserved for this phase is:

- `/home/diego/repos@uibcdf/Alphashape/castp/topomt_version`
