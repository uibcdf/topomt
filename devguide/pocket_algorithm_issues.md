# Pocket Algorithm Issues

## Purpose

This document collects known problems, anomalies, ambiguities, and residual
non-parity cases observed while auditing and reimplementing pocket-detection
engines in TopoMT.

It is not limited to confirmed bugs. It should also record:

- deterministic but unexplained discrepancies against upstream tools;
- local geometric ambiguities that may lead to multiple valid tetrahedrizations;
- upstream limitations that affect parity or interpretation;
- cases where parity is not exact yet but should be pursued;
- cases where the remaining mismatch appears to be tied to backend geometry.

Whenever a new issue is detected, it should be added here together with:

- affected engine;
- affected systems;
- current evidence;
- current hypothesis;
- whether the issue blocks parity;
- and the next diagnostic or implementation step.

## Active issues

### `fpocket4`: residual raw tetrahedrization mismatch in locally ambiguous regions

#### Status

Open at the raw geometry level. Not accepted as resolved. The current policy is:

- do not silently accept residual non-parity;
- detect systems and regions where the discrepancy may appear;
- keep studying the upstream geometry path until the origin is as clear as
  possible.

#### Affected systems

- `1GG0.pdb`
- `3LKF.pdb`

#### Observed behavior

For the current native `fpocket4` reimplementation:

- final pocket-output parity is exact against the current audited local
  fpocket source build on `1GG0.pdb`, `1N57.pdb`, `3LKF.pdb`, and `E15ALA.pdb`;
- however, the raw geometry layer still shows deterministic local
  tetrahedrization mismatches, especially in `1GG0.pdb` and `3LKF.pdb`.

#### Main evidence collected so far

In `1GG0`:

- the extra native pocket is associated with the region around
  `VAL27 / GLU29 / TYR69 / GLY71`;
- six native tetrahedra/alpha-spheres from that region do not appear in the
  accepted vertex set of the upstream `fpocket` run;
- those same tetrahedra do appear in the raw `qvoronoi` CLI output;
- they do not appear in the raw embedded-Qhull output instrumented from the
  upstream `fpocket` source.

This means the residual discrepancy is not explained by:

- the TopoMT parser;
- atom purging at the start of the workflow;
- the final pocket dropping stage;
- or a simple mismatch in `testVvertice()` alone.

The discrepancy already exists in the raw tetrahedrization/vertex generation
layer.

Direct SciPy-side probes were also run with several explicit Qhull option sets,
including variants around `Qbb`, `Qc`, `Qz`, and `Qt`. For the current `1GG0`
problem region, these probes still generated the same six local tetrahedra that
the upstream embedded-Qhull path does not keep. This means that simply passing
more explicit `qhull_options` to SciPy is not, by itself, enough to recover the
upstream behavior in this anomaly case.

An additional diagnosis also showed that a naive local reconstruction of the
Qhull input may differ from the actual upstream input. In `1GG0`, a local
rebuild initially included two `PO4` groups that upstream `fpocket` did not
pass to the detection geometry path. However, even after rebuilding the
external `qvoronoi` input from the exact heavy-atom list emitted by the
instrumented upstream run, the six problematic tetrahedra were still present in
the external result and still absent from the embedded-Qhull result.

This separates two different issues:

- input reconstruction must match the upstream heavy-atom list exactly when
  auditing geometry;
- even with matched input, the embedded and external geometry paths may still
  resolve locally ambiguous regions differently.

#### Systemic input-population mismatch

Broader diagnostics on the bundled fpocket sample systems show that input
reconstruction mismatch is not exceptional. Several systems differ
substantially between:

- a naive local rule such as "all non-hydrogen PDB atoms";
- and the heavy-atom population that upstream `fpocket` actually passes to its
  Voronoi/Qhull stage.

Representative examples:

- `1ATP.pdb`
  local reconstruction includes `MN` and `ATP` atoms that upstream does not use
  in the geometric stage;
- `1CEN.pdb`
  local reconstruction includes many `BGC` atoms that upstream does not use;
- `1N57.pdb`, `2GI9.pdb`, `2H05.pdb`, `3LKF.pdb`
  local reconstruction includes many waters and small-molecule atoms that
  upstream does not use;
- `1GG0.pdb`
  local reconstruction includes two `PO4` groups that upstream does not use;
- `E15ALA.pdb`
  upstream includes additional `HEO` atoms that a naive local rule may miss.

This means that geometry audits should be interpreted in two stages:

1. reproduce the exact atom population seen by upstream;
2. only then compare tetrahedrization and accepted alpha-spheres.

If stage 1 is not matched, stage-2 conclusions about Qhull behavior may be
misleading.

In `3LKF`:

- the two residual atom mismatches involve heavy protein atoms
  `ILE 32 C` and `GLU 191 N`;
- they are not missing because of hydrogen, water, ion, or ligand purging;
- local raw tetrahedra also differ between the external `qvoronoi` route and
  the embedded upstream geometry path.

#### Current interpretation

The most plausible explanation is a combination of:

- locally ambiguous or near-degenerate geometry;
- and a deterministic but different tetrahedrization policy between:
  - the embedded Qhull path used by upstream `fpocket`;
  - and the external or SciPy-backed geometry route used during TopoMT-native
    reconstruction and diagnostics.

This is not treated as an acceptable final explanation by itself. It is only
the current best diagnosis.

#### Why this matters

If this interpretation is correct, then a residual mismatch can appear even
when:

- atom filtering is correct;
- alpha-sphere acceptance logic is close to upstream;
- and the same local region is being analyzed.

In that case, exact raw parity depends on reproducing not only the filtering
semantics but also the effective tetrahedrization policy of the upstream
backend.

#### Required TopoMT response

TopoMT should:

- detect alpha-spheres that are likely to belong to locally ambiguous regions;
- report where these regions occur in a system;
- and use that information as a validation signal rather than as a reason to
  stop pursuing parity.

Residual raw non-parity in such regions should be explicitly marked, not
silently ignored.

#### Next work

- keep improving the diagnosis of embedded-Qhull vs external-Qhull behavior;
- test whether SciPy can be configured or post-processed to reproduce the same
  local tetrahedrization policy more closely;
- keep using `1GG0.pdb` and `3LKF.pdb` as reference anomaly systems;
- extend the issue log with any new deterministic local mismatch found in other
  systems;
- maintain the larger running checkpoint in
  [fpocket4/native_checkpoint.md](fpocket4/native_checkpoint.md).

### `fpocket4`: final-pocket discrepancies between fpocket builds/binaries

#### Status

Open, and now clearly separated from native/source parity.

#### Affected systems

- `1GG0.pdb`
- `3LKF.pdb`
- `E15ALA.pdb`

#### Observed behavior

Different fpocket binaries/builds can produce different final pocket sets on
the same input.

Current audited examples:

- `1GG0.pdb`
  - system fpocket binary used by wrapper mode: `16` pockets
  - audited local fpocket source build: `17` pockets
  - TopoMT native: `17` pockets
- `3LKF.pdb`
  - system fpocket binary omits atom index `230` from the relevant pocket
  - audited local fpocket source build keeps atom index `230`
  - TopoMT native matches the audited local source build
- `E15ALA.pdb`
  - system fpocket binary used by wrapper mode: `9` pockets
  - audited local fpocket source build: `8` pockets
  - TopoMT native: `8` pockets

#### Current interpretation

These are not currently treated as native/source mismatches.

They are treated as fpocket build-drift cases, likely connected to the
temporary-output synchronization problem documented in:

- [fpocket4/corrections/report_truncation.md](fpocket4/corrections/report_truncation.md)

#### Why this matters

When wrapper mode is used as a parity oracle, parity claims must identify which
fpocket binary is being treated as the reference. Otherwise:

- a native/source match may look wrong against the wrapper;
- and a wrapper/native mismatch may be misdiagnosed as a native failure.

#### Next work

- verify the impact of the `fflush(ftmp)` synchronization fix in clean
  unpatched local rebuilds;
- record binary identity for future wrapper-based parity runs;
- keep source-build parity and wrapper-binary parity explicitly separated in
  tests and in `devguide`.
- if wrapper mode later moves to a UIBCDF-packaged `fpocket` binary, validate
  that package explicitly before adoption using at least:
  - pocket-count parity on `1GG0.pdb`, `1N57.pdb`, `3LKF.pdb`, and
    `E15ALA.pdb`;
  - pocket atom-membership parity on the same systems;
  - explicit negative checks that the packaged binary does not reproduce the
    current conda-forge/system-binary drift on `1GG0.pdb`, `3LKF.pdb`, and
    `E15ALA.pdb`.

### `fpocket4`: `E15ALA` discrepancy between fpocket builds, not a native-only residual

#### Status

Open, but reclassified.

This is no longer treated as evidence that the native `fpocket4`
reimplementation disagrees with the upstream source algorithm.

#### Affected system

- `E15ALA.pdb`

#### Observed behavior

Different `fpocket` builds produce different final pocket counts on the same
input:

- the system `fpocket` binary used by the TopoMT wrapper currently produces
  `9` pockets;
- the locally instrumented build compiled from
  `../../repos@others/fpocket` currently produces `8` pockets after
  `dropSmallNpolarPockets()` and sorting;
- the current native `fpocket4` path also produces `8` pockets.

#### Main evidence collected so far

- For `E15ALA`, the accepted alpha-sphere set and the large pre-drop clusters
  match between the native path and the locally instrumented upstream build.
- The six alpha-spheres that were initially suspected to form a native-only
  bridge are also accepted upstream and share the same transferred `resid`.
- The locally instrumented upstream build reports:
  - `after_assign nvert=553 pockets=553`
  - `after_apply pockets=122`
  - `after_drop pockets=8`
  - `after_sort pockets=8`
- The wrapper-backed TopoMT route uses the system binary at:
  `/home/diego/Myopt/miniconda3/envs/molsyssuite@uibcdf_3.13/bin/fpocket`
- Running that system binary on a clean temporary copy of `E15ALA.pdb`
  currently produces `9` pockets.

#### Current interpretation

The current `E15ALA` mismatch should be interpreted as a discrepancy between
different `fpocket` builds or binaries, not as a discrepancy between:

- TopoMT native `fpocket4`;
- and the upstream source algorithm represented by the audited local build.

This build-level discrepancy is likely related to the upstream temporary-output
truncation problem already documented in:

- [fpocket4/corrections/report_truncation.md](fpocket4/corrections/report_truncation.md)
  

but that causal link is not yet fully locked down in a clean unpatched local
rebuild.

#### Why this matters

If wrapper mode is used as the parity oracle, parity claims need to specify
which `fpocket` binary is being treated as the reference. Otherwise:

- a native/source comparison may look wrong;
- while a native/source comparison is actually correct and the divergence comes
  from wrapper-binary drift.

#### Next work

- verify the effect of the `fflush(ftmp)` truncation fix on `E15ALA` using a
  clean unpatched local rebuild;
- record binary identity when using wrapper mode as a parity oracle;
- keep `E15ALA` out of the list of native-only residual geometry anomalies
  unless new evidence shows a real source-level native mismatch.
