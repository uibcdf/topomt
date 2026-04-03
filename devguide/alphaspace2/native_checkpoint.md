# `alphaspace2` Native Checkpoint

## Purpose

This document records the current state of the native `alphaspace2`
reimplementation and the concrete remaining work needed for the `0.3.0`
milestone.

The goal is to resume later from a precise technical checkpoint rather than
from a vague statement such as "descriptors are still missing".

## Current reading

The native `alphaspace2` work is no longer at the geometry-bootstrap stage.

It already has:

- a native state builder in `topomt.methods.alphaspace2`;
- shared geometry through the new `topomt.delaunay_mesh.DelaunayMesh`
  substrate and its alpha-sphere-derived view;
- native alpha filtering by radius;
- native alpha-space volume calculation;
- native pocket clustering;
- native beta clustering;
- native beta grouping parity on the current apo audited systems;
- native lining-atom ownership recovery;
- native optional binder/contact propagation from alpha spheres to betas and
  pockets;
- and test coverage against the upstream AlphaSpace2 package on the current
  audited examples.

So the remaining work for `0.3.0` is not "make AlphaSpace2 native at all".
It is:

- finish the semantic layers that still remain simplified or zeroed out;
- align the still-missing score-related behavior for the non-apo or
  `adv_atom_types`-aware route;
- and decide how much additional binder/contact surface beyond the current
  optional parity layer belongs in the core milestone.

## End-of-day checkpoint

The work now has a second concrete stage beyond the apo baseline:

- a first native Vina-aware score path is already implemented in
  `topomt.methods.alphaspace2`;
- the small upstream typing/scoring tables are now vendored under
  `topomt/data/alphaspace2/`;
- the native path now accepts either `adv_atom_types` or `pdbqt_file` to
  activate the richer beta-score route;
- the native path now also supports optional binder/contact propagation through
  the public API;
- and this richer path is implemented natively against `molsysmt`, not against
  `mdtraj`.

That last point is deliberate:

- production/native TopoMT code should depend on `molsysmt`;
- `mdtraj` remains acceptable in parity tests only because the upstream
  AlphaSpace2 package itself is built around that representation.
- quantity handling and unit conversion should go through `pyunitwizard`
  directly, not through local helper shims.

At the end of this work session:

- the apo parity tests remain the stable baseline;
- a new focused parity test exists for the upstream `CDK2` example with
  non-zero Vina-aware beta scores;
- a native parity test now exists for upstream-style contact propagation from
  alpha spheres to betas and pockets;
- that `CDK2` test is now green under a small explicit absolute tolerance on
  the real `molsysmt` file-ingestion path;
- and the full current `tests/methods/alphaspace2/test_parity.py` suite is green again.

So the current reading is no longer "the richer score route is still missing".
It is:

- the richer route exists;
- it now has a first passing regression target on a real non-apo example;
- and the remaining question is no longer whether the route works at all, but
  whether the current small-tolerance parity contract is the one we want to
  keep for `0.3.0` as the native `molsysmt`-based reference.

## Current code shape in TopoMT

The native implementation already exposes these main internal layers:

- `_prepare_receptor(...)`
- `_compute_alpha_layer(...)`
- `_cluster_pockets(...)`
- `_cluster_betas(...)`
- `_compute_contact_masks(...)`
- `_build_state(...)`
- `_state_to_pocket_records(...)`

This means the implementation already has a stable internal decomposition that
can be extended, rather than requiring a rewrite from scratch.

## Upstream workflow anchor

The current upstream `Snapshot.run()` path is:

1. `genAlphas(receptor)`
2. `genPockets()`
3. `genBetas()`
4. `genBScore(receptor)`
5. optional `calculateContact(...)`

That gives a clean way to classify the remaining native work.

## What is already validated

Current native tests show parity on the audited AlphaSpace2 examples for:

- alpha-sphere counts;
- alpha radii within tight tolerance;
- total alpha-space volume;
- pocket counts;
- beta counts and beta grouping;
- total beta-space aggregation;
- pocket atom ownership from lining atoms.
- optional boolean contact propagation from alpha spheres to betas and pockets.

The current audited set includes:

- `1GG0.pdb`
- `3LKF.pdb`
- `protein_1c70.pdb`
- `protein_1hvi.pdb`
- `protein_1pro.pdb`
- `1GG0.pdb` contact propagation against the upstream contact stage

This means `genAlphas()`, `genPockets()`, and the current apo `genBetas()`
route are already in a strong position.

## What still looks incomplete

The main remaining gaps are in the higher semantic layers.

### 1. `genBetas()` now looks essentially aligned for the apo audited set

The current audit now shows:

- equal beta counts;
- equal beta grouping;
- equal total beta-space aggregation;
- and equal pocket scores on the current apo audited systems.

That last point does **not** yet mean that the full score route is complete.
It means that on the current apo audited set, upstream also leaves beta scores
at zero, so pocket scores remain zero on both sides.

### 2. `genBScore(receptor)` is now partially reproduced

This area is no longer absent. The native path now has a first implementation
of the richer Vina-aware route.

What still remains is narrower:

- decide whether the current small-tolerance parity contract on `CDK2` is
  sufficient for the `0.3.0` milestone or whether we still want to chase even
  tighter numerical agreement;
- keep the aggregation contract from beta score tensors to pocket scores
  explicit and stable;
- and decide whether `0.3.0` should claim:
  - apo semantic parity first,
  - or full `adv_atom_types`-aware beta-score parity.

### 3. Contact/binder-aware behavior is now partially reproduced

The upstream `Snapshot.run()` supports:

- `calculateContact(...)` when a binder is provided;
- otherwise zero-filled contact arrays.

The native path now reproduces the same basic contract:

- optional binder coordinates mark alpha contacts under the same `1.6 A`
  cutoff;
- beta and pocket contacts are propagated from their child alpha spheres;
- and pocket records now expose the corresponding `is_contact` flag.

This is now implemented through the public native path rather than as a test
only shim.

For `0.3.0`, the remaining question is therefore narrower:

- whether the current binder/contact layer is sufficient as the native
  milestone contract;
- or whether additional binder-aware semantics from the upstream package
  deserve explicit parity tests too.

### 4. Nonpolar-space details still need explicit audit

The native path already computes per-alpha nonpolar ratios, but the full
upstream semantic contract around:

- nonpolar volume;
- pocket-level aggregation;
- and any downstream use in scores or descriptors

still deserves explicit audit rather than assumption.

## Important current clarification about scores

On the currently audited apo systems:

- upstream `genBScore(receptor)` falls back to zero beta-score arrays when the
  receptor does not carry `adv_atom_types`;
- the current native path also produces zero beta scores there;
- so pocket score parity on the current apo audited set is already satisfied,
  but only in that restricted sense.

This means the remaining score work is specifically about the richer
`adv_atom_types`-aware route, not about the apo baseline already under test.

For that richer route, the current checkpoint is:

- the native implementation already produces non-zero beta-score matrices when
  `adv_atom_types` or `pdbqt_file` are provided;
- the upstream `CDK2` example is now the main regression target for this path;
- the current `CDK2` parity test is now green under a small explicit absolute
  tolerance;
- and the remaining gap should now be treated as a numerical-contract problem,
  not as a missing-feature problem.

## MolSysMT precision note

The earlier `molsysmt.convert(path_to_pdb, to_form='molsysmt.MolSys')`
regression encountered during this work has already been fixed upstream.

The remaining `CDK2` residual is **not** treated as a current `molsysmt` bug.

The current diagnosis is:

- upstream AlphaSpace2 uses a receptor path built on `mdtraj`, which stores
  coordinates in `float32`;
- native TopoMT uses `molsysmt`, which preserves receptor coordinates in
  `float64`;
- the resulting coordinate difference is tiny, on the order of `7.6e-06 A` in
  the current `CDK2` case;
- but one highly sensitive local beta/probe score outlier moves beyond
  `3e-3` because several neighboring atoms are nearly tied in distance.

Interpretation:

- `molsysmt` is not introducing a correctness problem here;
- the native path is preserving more precision than the upstream `mdtraj`
  reference;
- and the richer `CDK2` parity test should therefore be interpreted as a
  cross-representation parity check under a very small explicit tolerance, not
  as a bitwise-equivalence target.

## Unit-handling note

The active native `alphaspace2` and shared `DelaunayMesh` path no longer rely
on the old local `get_magnitude(...)` / `get_magnitudes(...)` helpers.

The current policy is:

- quantities should be handled directly with `pyunitwizard`;
- values should enter numeric kernels through `puw.get_value(..., to_unit=...)`;
- and local unit-helper shims should not be reintroduced in new code.

## Recommended `0.3.0` order

The next work should be staged like this:

1. Freeze the current geometry/pocket-membership parity tests and keep them
   green.
2. Freeze beta-grouping and apo score parity tests and keep them green.
3. Decide whether the current `CDK2` tolerance-based parity contract is final
   enough for `0.3.0`, given the confirmed `float32` vs `float64` precision
   difference between the upstream and native receptor-loading paths.
4. Finalize tests for non-zero beta-score aggregation once that path is fully
   grounded.
5. Decide whether the `0.3.0` claim should stop at apo parity plus native
   structure, or extend to the richer Vina-aware route too.
6. Decide whether the current binder/contact parity layer is already enough for
   `0.3.0` or whether more binder-aware semantics should still be added.

## Concrete next-code targets

The most likely upstream files/functions to inspect next are:

- `alphaspace2/Snapshot.py`
  especially `genBetas()` and `genBScore()`
- `alphaspace2/functions.py`
  for helper calculations used by those stages
- `alphaspace2/Cluster.py`
  for the meaning of beta and pocket semantic accessors
- `alphaspace2/VinaScoring.py`
  if the score route really depends on it for the apo milestone

## Testing implications

The next tests should stop being only geometry-oriented.

Priority additions:

- parity tests for beta grouping and beta counts;
- parity tests for beta centers and total beta-space aggregation;
- parity tests for apo pocket score semantics;
- the new focused `CDK2` parity test for the richer `adv_atom_types`-aware
  beta-score path;
- the current binder/contact parity test against upstream boolean contact
  propagation;
- follow-up assertions on pocket-score aggregation for that same route once the
  residual drift is characterized;
- explicit separation between apo-native parity and any future richer
  binder-aware behavior beyond the current contact flags.

## Current milestone interpretation

The practical interpretation today is:

- `fpocket4(native)` is the closed `0.2.0` milestone;
- `alphaspace2` is the active `0.3.0` front;
- and the right question is no longer "can TopoMT generate AlphaSpace2-like
  pockets natively?" but rather "can TopoMT reproduce the remaining semantic
  layers natively enough to stop relying on the wrapper?".
