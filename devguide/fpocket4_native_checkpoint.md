# `fpocket4` Native Checkpoint

## Purpose

This document records the current diagnostic checkpoint for the native
reimplementation of `fpocket4`.

Its goal is to make it easy to resume work later without having to reconstruct
the current understanding from terminal history.

## Current scope

This checkpoint is about the native path in:

- `topomt.methods.fpocket4`
- `topomt.alpha_spheres`

and its parity relationship with the upstream `fpocket` binary.

It does not describe the wrapper-backed path in full detail. The wrapper-backed
path remains important for integration, but it is no longer a universal parity
oracle because wrapper behavior depends on which fpocket binary/build is
actually executed.

## What is already established

### 1. Wrapper-backed parity depends on the fpocket binary build

The wrapper-backed `fpocket4` route remains the faithful integration path for
the fpocket binary that is actually executed.

However, it is now established that different fpocket builds can produce
different final pocket sets on the same input. So wrapper parity is not a
single universal oracle unless the fpocket binary is fixed and identified
explicitly.

Practical consequence:

- the fidelity-oriented recommendation is now `implementation='native'`;
- `implementation='topomt'` should be treated as the explicit corrected
  TopoMT-side variant;
- and `implementation='wrapper'` should be reserved for external-binary
  integration, comparison, or audit workflows.

### 2. Input atom selection is now aligned with upstream

The native `fpocket4` receptor-preparation path now reproduces the same heavy
atom population that upstream `fpocket` sends into its geometry stage on the
audited representative systems.

This was important because earlier geometry comparisons were being distorted by
 atom-population mismatch.

Representative cases where this is now aligned:

- `1ATP.pdb`
- `1GG0.pdb`
- `3LKF.pdb`
- `E15ALA.pdb`

### 3. The remaining geometry mismatch is mostly a native super-set

After correcting the upstream raw-index remapping, the raw tetrahedron
comparison became much cleaner.

The dominant pattern is now:

- upstream raw tetrahedra are almost entirely contained in the native raw
  `AlphaSpheres` result;
- the native route still generates a small but systematic super-set of extra
  tetrahedra.

Current corrected raw comparisons on the bundled fpocket sample systems:

- `1ATP`: `native_only=11`, `upstream_only=1`
- `1CEN`: `66`, `1`
- `1GG0`: `228`, `1`
- `1N57`: `28`, `0`
- `1YCR`: `226`, `1`
- `2GI9`: `7`, `1`
- `2H05`: `55`, `0`
- `3LKF`: `209`, `0`
- `E15ALA`: `211`, `0`

This means that the residual discrepancy is no longer best described as "the
native path misses upstream tetrahedra". It is better described as "the native
path produces a deterministic extra set of tetrahedra in some regions".

### 4. The discrepancy is local and deterministic

The `native_only` tetrahedra are not scattered randomly through the structure.
They cluster in a small number of local regions.

This has been observed clearly in:

- `1GG0`
- `3LKF`

That makes the issue look like a deterministic local tetrahedrization-policy
difference rather than a global algorithm failure.

### 5. The discrepancy is not explained by simple SciPy flag tuning

The following `scipy.spatial.Delaunay` experiments did not change the
tetrahedron set in the anomaly systems:

- explicit `qhull_options` variants around `Qbb`, `Qc`, `Qz`, `Qt`, `Qx`, and
  `Q12`
- input-atom order permutations
- tiny coordinate jiggles

So the current evidence does not support the idea that parity can be recovered
just by passing a better-visible combination of Qhull flags to SciPy.

### 6. Native/source parity is now exact on the main audited systems

Using the current audited local fpocket build compiled from
`../../repos@others/fpocket` with the temporary-output synchronization fix
applied in the diagnostic copy, the native TopoMT implementation now matches
the parsed fpocket output exactly on the main audited systems:

- `1ATP.pdb`
- `1CEN.pdb`
- `1GG0.pdb`
- `1N57.pdb`
- `1YCR.pdb`
- `2GI9.pdb`
- `2H05.pdb`
- `2HGR.pdb`
- `3LKF.pdb`
- `E15ALA.pdb`

## Current interpretation

The best current explanation is now split into two layers:

- at the raw geometry level, the upstream embedded Qhull path and the
  SciPy-backed route do not implement the same effective tetrahedrization
  semantics in all local regions;
- that raw difference is deterministic and becomes visible only in some local
  neighborhoods;
- but at the final pocket-output level, the current native path now reproduces
  the audited local fpocket source build exactly on the main audited systems.

The working interpretation is not:

- "the native route is wrong in general"

but rather:

- "the native route still produces a deterministic super-set of raw tetrahedra
  in some local regions relative to the upstream embedded geometry backend, but
  the remaining wrapper-vs-native differences currently observed on some
  systems are explained by fpocket build drift, not by a source-level
  native/source mismatch".

## What upstream study has already established

### Embedded Qhull path

The current upstream study has already established that:

- the first replica goes directly from the embedded Qhull output to
  `testVvertice()`;
- there is no hidden extra cleanup stage before `testVvertice()` in that first
  path;
- the duplicate-removal logic by `barycenter + ray` only matters for extra
  replicas, not for the default `M_N_REPLICAS = 1` route.

### Embedded-Qhull semantics

The embedded upstream path does more than pass visible `qvoronoi` flags. It
also forces additional internal Qhull semantics such as:

- `_bbound-last`
- `_coplanar-keep`
- `DELAUNAY`
- `VORONOI`
- `SCALElast`
- `MERGEexact` in higher dimensions

This is one of the main reasons the residual mismatch is currently treated as a
backend-geometry issue, not as a parser or filter issue.

## Important anomaly systems

### `2HGR.pdb`

This should now be treated as a large-system deep-validation case, not as part
of the routine parity battery.

Current reading:

- final parity is now measured and confirmed;
- both the audited local fpocket build and the current native path are very
  slow on this input;
- the system is much larger than the rest of the audited set, with
  `55,628` heavy atoms retained by the native receptor-preparation path;
- the audited upstream build and the current native path both end at `612`
  final pockets;
- the recorded native deep-validation runtime is `871.35 s` (`14.52 min`);
- this makes it useful as an occasional deep validation and performance case,
  but not as a routine regression test.

### `1GG0.pdb`

This remains a key diagnostic system, but its interpretation has changed.

Current reading:

- the raw tetrahedrization diagnosis is still useful here;
- but the current native path now matches the audited local fpocket source
  build exactly at the final pocket level;
- the older `16` vs `17` discrepancy is now interpreted as a difference between
  fpocket builds, not as a native/source mismatch.

### `3LKF.pdb`

This remains the second key diagnostic system.

Current reading:

- the current native path matches the audited local fpocket source build
  exactly at the final pocket level;
- the earlier single-atom residual (`ILE 32 C`, atom index `230`) is now
  interpreted as a build-drift diagnostic because:
  - the system fpocket binary omits it;
  - the audited local source build keeps it;
  - the native path matches the audited local source build.
- the raw tetrahedron comparison still shows a deterministic native extra set,
  so this remains a useful system for studying raw geometry-policy differences.
- when compared against `implementation='topomt'`, the current difference is
  minimal: one matched pocket differs by one atom in the current audit. This
  is consistent with the corrected B-factor semantics acting as a local
  decision change rather than a global pocket-layout change.

### `E15ALA.pdb`

This remains useful, but it should no longer be treated as a native-only
geometry anomaly.

Current reading:

- `HEO` is not noise in this case; upstream keeps it;
- the current native path and the locally instrumented build compiled from the
  upstream source agree on the accepted alpha-sphere set, on the large
  pre-drop clusters, and on the final pocket set;
- the current discrepancy is between fpocket builds:
  - the system binary used by wrapper mode gives `9` final pockets;
  - the locally instrumented build gives `8`;
  - the native path also gives `8`.
- `implementation='topomt'` currently matches `native` exactly at the final
  pocket level on this system, which is consistent with the corrected
  B-factor semantics not introducing any additional pocket-level drift here.

So `E15ALA` is now best interpreted as a build-level fpocket discrepancy,
likely related to the temporary-output truncation issue, not as evidence of a
remaining native/source geometry mismatch.

### `1N57.pdb`

This is now the clean control system.

Current reading:

- the current native path matches the audited local fpocket source build
  exactly;
- no residual pocket-level discrepancy remains here;
- this system should be kept as a control when diagnosing future build drift
  or raw geometry regressions.

## Important non-conclusions

The following claims should **not** be treated as established:

- that the mismatch is purely caused by near-coplanarity;
- that the mismatch can be eliminated by adding the "right" visible
  `qhull_options` to SciPy;
- that the default `AlphaSpheres` implementation should be changed globally;
- that wrapper-vs-native disagreement automatically implies a native/source
  mismatch;
- that the residual raw mismatch is acceptable and can just be ignored.

## Architectural rule for future changes

If later work requires fpocket-specific geometric handling, that behavior
should remain isolated to the `fpocket4` method path or to an explicitly
fpocket-oriented strategy.

It should **not** silently replace the clean default behavior of
`topomt.alpha_spheres.AlphaSpheres`.

## Pending cleanup: replace local atom-purge logic with better MolSysMT use

One important cleanup item remains explicitly pending for the `fpocket4`
family (`native`, `topomt`, and later `topomt-scalable`).

Current status:

- the input atom-selection semantics are now validated against the audited
  upstream source behavior;
- but part of that logic is still expressed locally in `topomt.methods.fpocket4`
  through explicit masking and local filtering helpers;
- this was acceptable during the audit phase because it made upstream-fidelity
  debugging easier.

What still needs to happen later:

- replace as much of that local purge/filter logic as possible with more
  idiomatic `molsysmt` selection and filtering routes;
- keep the already validated semantics exactly the same while improving the
  implementation style;
- and avoid letting TopoMT keep a permanently parallel atom-selection layer for
  things that should ultimately be delegated to MolSysMT.

Important constraint:

- this is a cleanup/refactor task, not a semantics-change task;
- the validated final pocket results for `native` and `topomt` must remain the
  same after that refactor.

## Recommended next diagnostic steps

When work resumes, the preferred order is:

1. Document clearly that audited source-build parity is now exact on the main
   audited systems, including `2HGR.pdb`, while wrapper parity depends on the
   fpocket binary build.
2. Verify the effect of the temporary-output synchronization fix on clean
   unpatched local rebuilds, to close the loop with the build-drift diagnosis.
3. Continue toy-system experiments using the embedded Qhull harness and a
   correctly interpreted output format.
4. Use those toy systems to compare:
   - simple generic configurations;
   - nearly coplanar configurations;
   - nearly cospherical configurations.
5. Check whether the embedded-Qhull and SciPy-backed routes diverge already in
   those toy systems.
6. Only after that, return to the protein cases to see which toy behavior best
   explains the residual real-system mismatch.
7. Keep documenting anomaly systems and diagnostic evidence in
   [pocket_algorithm_issues.md](pocket_algorithm_issues.md).

## Related documents

- [native_methods_plan.md](native_methods_plan.md)
- [pocket_algorithm_issues.md](pocket_algorithm_issues.md)
- [status.md](status.md)
