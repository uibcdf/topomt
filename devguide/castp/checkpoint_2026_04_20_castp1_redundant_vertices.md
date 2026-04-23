# CASTp 1.0 Parity Checkpoint: Redundant Vertices

Date: 2026-04-20

## Current oracle policy

For the current implementation phase, the primary algorithmic oracle is the
local historical CASTp 1.0 stack:

- `DELCX`
- `MKALF`
- weighted alpha-shape output files generated from the same materialized input

The CASTP 3.0 and CASTPfold server ZIPs remain useful references, but they are
not the pass/fail oracle for the native CASTp 1.0 path. Known server-side
differences already include at least radii policy, and water handling is a
candidate difference for the later CASTP 3.0 phase.

## Correct reading of CASTp 1.0 output

The MKALF `*.poc` file should not be interpreted as "open pockets only".

For CASTp 1.0 parity, the current comparison contract is:

- native all feature components vs CASTp 1.0 `*.poc`
- native void components vs CASTp 1.0 `*.voids`

This matters because a component can appear in the MKALF pocket-structure
printout and also be classified as a void by the zero-mouth logic. The `2pk4`
case exposed this ambiguity.

## Confirmed green systems before redundant-vertex work

Using the corrected oracle reading, the native implementation had exact atom-set
parity with CASTp 1.0 for:

- `1rop`
- `2pk4`
- `1crn`
- `1ubq`
- `1pht`
- `1stp`

The comparison was made at the component atom-set level:

- exact multiset equality for native all components vs `*.poc`
- exact multiset equality for native voids vs `*.voids`

## First red systems

The next medium systems exposed real CASTp 1.0 divergences:

- `1lyz`
- `2lyz`
- `1mbn`

Initial failures:

- `1lyz`: same number of `*.poc` components, but one native size-7 component
  and one size-8 component did not match CASTp 1.0; voids also differed by a
  size-7 vs size-8 component.
- `2lyz`: native had one additional all-component size-13 feature relative to
  CASTp 1.0, while voids matched.
- `1mbn`: broad divergence in both all components and void components.

## Redundant vertices

DELCX reports "redundant vertices" during regular-triangulation construction.
These are not duplicate coordinates. They are weighted-redundant/hidden
vertices: atoms whose power cell is empty and therefore do not participate in
the effective regular triangulation.

Observed DELCX redundant vertices:

| System | Redundant vertices | Notes |
|---|---:|---|
| `1rop` | 4 | all `ARG CZ` |
| `2pk4` | 3 | all `ARG CZ` |
| `1lyz` | 10 | all `ARG CZ` |
| `2lyz` | 11 | mostly `ARG CZ` |
| `1mbn` | 5 | `ARG CZ` plus `HEM FE` |

The important point is conceptual, not atom-name-specific:

- do not filter `ARG CZ`;
- do not filter metals by name;
- filter weighted-redundant vertices using the regular-triangulation geometry.

## Implemented native correction

The native geometry build now discards weighted-redundant vertices after
duplicate-coordinate handling and before building the final CASTp geometry
substrate.

Operationally, a vertex is discarded if it does not appear in any lower-hull
simplex of the lifted weighted point set, i.e. if it has no cell in the regular
triangulation.

This criterion matched DELCX's reported redundant vertices exactly for:

| System | Native discarded vertices | DELCX redundant vertices |
|---|---:|---:|
| `1rop` | 4 | 4 |
| `2pk4` | 3 | 3 |
| `1lyz` | 10 | 10 |
| `2lyz` | 11 | 11 |
| `1mbn` | 5 | 5 |

The exact discarded local atom indices also matched DELCX in those systems.

## Result after correction

The redundant-vertex correction is canonical and should remain in the CASTp 1.0
path, but it does **not** by itself close the first red systems.

After regenerating CASTp 1.0 for `1lyz` from the same filtered input used by
the native path:

- native all components vs CASTp 1.0 `*.poc`: still `DIFF`
- native voids vs CASTp 1.0 `*.voids`: still `DIFF`

Therefore the redundant-vertex gap was real but not sufficient.

## Triangulation-count check

After redundant-vertex filtering, native triangulation counts match DELCX for
the red systems:

| System | Native vertices | Native tetrahedra | DELCX tetrahedra |
|---|---:|---:|---:|
| `1lyz` | 1092 | 7120 | 7120 |
| `2lyz` | 1091 | 7114 | 7114 |
| `1mbn` | 1255 | 8187 | 8187 |

This narrows the residual problem:

- it is not simply a different number of active vertices;
- it is not simply a different number of tetrahedra;
- the remaining gap is likely in simplex identity/order, exact rank/mu
  assignment, SoS tie resolution, or the component/mouth scan over otherwise
  count-compatible triangulations.

## Current interpretation of DELX/SoS importance

DELX/SoS is not a blocker for the smaller green systems, but it cannot be
dismissed.

The updated view is:

- redundant vertex dumping is a required CASTp 1.0 behavior and is now
  implemented;
- full DELX/SoS behavior remains a residual risk for degenerate or near-tied
  systems;
- the first medium red systems now point toward deeper triangulation identity,
  rank-order, or scan-order differences rather than only missing redundant
  filtering.

## Next recommended step

Use `1lyz` as the next focused red case.

Recommended audit order:

1. Compare native simplex atom sets against CASTp 1.0 printed tetrahedra if a
   reliable MKALF/DT dump can be extracted.
2. If simplex sets match, compare rho-rank and mu-rank assignments.
3. If ranks match, compare the pocket sequence / union-find state for the
   specific native-only size-7 component and CASTp-only size-8 component.
4. Only after locating the layer, implement the next correction.

Do not introduce local heuristics around lysozyme, arginine, waters, or feature
sizes.

## Follow-up correction: CASTp 1.0 fixed-point materialization

The next `1lyz` audit showed that the triangulation simplex identity already
matched CASTp 1.0 after redundant-vertex filtering, but the exact rho/master
layer still differed by one edge event:

- CASTp 1.0 master: 16595 ranks including Rank[0], 64395 entries.
- Native before this correction: 16589 ranks including Rank[0], 64394 entries.
- Missing native rho edge: local `(556, 557)`, CASTp 1.0 one-based `557 558`.

Direct probing of the original CASTp 1.0 code showed that `alf_w_hidden1(557,
558,555)` returns `0`, while native previously returned attached for the same
geometric edge/probe case. The formula and the Fnext/opposite-vertex orbit were
not the cause.

The actual difference was input materialization:

- CASTp 1.0 `PDB2ALF` writes `# fix: 7.5`.
- `dt.c` reads that path as doubles and calls `ffp_param_push2`.
- `lia_ffpload` stores `floor(value * 10**5)`.
- The values are first the fixed-decimal text values written by PDB2ALF, not
  post-processed Python/MolSysMT floats.

Native exact predicates now use explicit CASTp 1.0 fixed-point materialization:

1. rematerialize coordinate/radius values at the PDB2ALF text precision
   currently modeled as 3 decimals;
2. apply `floor(value * 1e5)`;
3. square the fixed-point radius integer for the lifted weight term.

This is canonical for CASTp 1.0 and replaces the previous cleaner-but-wrong
`round`/`rint` decimal grid in the hidden/rho exact layer.

Verification after the correction on `1lyz`:

| Quantity | CASTp 1.0 | Native after correction |
|---|---:|---:|
| active vertices | 1092 | 1092 |
| tetrahedra | 7120 | 7120 |
| ranks including Rank[0] | 16595 | 16595 |
| master entries | 64395 | 64395 |
| non-attached rho edges | 3039 | 3039 |
| edge `(556,557)` rho rank | non-zero | 987 |

The server ZIP parity tests for CASTP 3.0 remain intentionally outside the
current pass/fail criterion. They are a later phase because CASTP 3.0 differs
from CASTp 1.0 in at least radii and water policy, and likely in other server
pipeline choices.

## Follow-up correction: explicit CASTp ranks and zero-mouth pockets

After the fixed-point correction, the `1lyz` triangulation and master-list were
audited at the next layer.

Native master-list rendered as CASTp-style entries matched
`1lyz.master.ml` exactly as a multiset:

- same 64395 entries;
- same rank, feature type, rho/mu event type, and atom set for every entry;
- no native-only or CASTp-only master entries.

The remaining component discrepancy was not in the master-list. It came from
two reporting/assembly assumptions:

1. The CASTp 1.0 `.poc` file was generated by an explicit command:
   `print pockets rank 14676 rank2 15044`.
2. Native was instead deriving `rank1/rank2` from `base_rank` and
   `probe_radius`, yielding `14682/15050` for the corrected `1lyz` geometry.

Using the explicit CASTp 1.0 ranks closed the tetrahedron composition of the
raw pocket/void components:

| Comparison | Native with explicit ranks | CASTp 1.0 | Difference |
|---|---:|---:|---:|
| non-void `.poc` components by `iT` | 13 | 13 | 0 |
| void `.voids` components by `iT` | 6 | 6 | 0 |

A second canonical reporting difference was also corrected: CASTp 1.0 prints
components in `.poc` even when they have zero mouth triangles. Native previously
dropped `n_mouths == 0` components. Native now reports them as `pocket`
components, while preserving the existing channel classification for two mouths
and branched-channel classification for more than two mouths.

The code now supports explicit `alpha_rank` and `beta_rank` overrides. This is
needed for strict CASTp 1.0 reproduction of a specific `print pockets rank R
rank2 R2` execution. The default `probe_radius`-derived path remains available,
but should not be used as the pass/fail criterion when the CASTp 1.0 oracle was
generated with explicit ranks.

## Follow-up correction: independent `f0/f1` face scans

A residual `2pk4` pocket difference exposed another wrong native assumption.
Native had treated interior faces (`iF`) and regular/mouth faces (`rF`) as
mutually exclusive partitions.

CASTp 1.0 does not do that in the printed pocket structure. In `voids.c`,
`alf_scan_pocket_f0` and `alf_scan_pocket_f1` are independent scans:

- `f0` emits faces from pocket tetrahedra that are not in the alpha complex at
  `rank1`;
- `f1` emits boundary/regular faces from the same component scan;
- the same triangle can therefore appear in both `iF` and `rF`.

The native face reporting now follows this behavior. This closed the `2pk4`
case where CASTp 1.0 printed triangle `(305, 645, 673)` in both `iF` and `rF`.

## Follow-up correction: `print_voids` only emits interior entities

The remaining `2lyz` and `1mbn` void differences were not component differences.
The native code was reporting regular edges for void records, while CASTp 1.0
`print_voids` never emits `rF`, `rE`, or `rV`.

The original `print_pocket.c` behavior is:

- `print_pockets` counts and prints `t0`, `f0`, `f1`, `e0`, `e1`, `v0`, and
  `v1`;
- `print_voids` counts and prints only `t0`, `f0`, `e0`, and `v0`.

Native void records now preserve only:

- `iT`
- `iF`
- `iE`
- `iV`

and leave `rF`, `rE`, and `rV` empty for the CASTp 1.0 reporting path.

## Current CASTp 1.0 parity matrix

After the fixed-point, explicit-rank, zero-mouth, independent-face-scan, and
void-reporting corrections, the native implementation matches CASTp 1.0 exactly
for the current regression matrix at the structural reporting level.

Comparison contract:

- oracle: local CASTp 1.0 `*.poc` and `*.voids`;
- native input: same PDB files from `sandbox/castp_oracle_runs`;
- ranks: explicit `alpha_rank`/`beta_rank` parsed from CASTp 1.0 output names;
- numbering: original one-based atom IDs for comparison;
- fields compared: `iT`, `iF`, `rF`, `iE`, `rE`, `iV`, and `rV`;
- excluded from this matrix: CASTP 3.0 and CASTPfold server ZIPs.

| System | `.poc` components | `.poc` status | `.voids` components | `.voids` status |
|---|---:|---|---:|---|
| `1crn` | 1 | OK | 0 | OK |
| `1rop` | 3 | OK | 0 | OK |
| `2pk4` | 10 | OK | 1 | OK |
| `1pht` | 6 | OK | 0 | OK |
| `1ubq` | 9 | OK | 3 | OK |
| `1stp` | 4 | OK | 1 | OK |
| `1lyz` | 13 | OK | 6 | OK |
| `2lyz` | 16 | OK | 7 | OK |
| `1mbn` | 26 | OK | 22 | OK |

No missing components, extra components, or field-level differences remain in
this matrix.

This matrix is now guarded by the parametrized regression test
`test_native_castp1_matches_local_mkalf_structural_outputs`. The test compares
the native structural records against the local MKALF `*.poc` and `*.voids`
files when `sandbox/castp_oracle_runs` is available, and skips otherwise so
normal package test runs are not coupled to local oracle artifacts.

## Current implementation status

The native CASTp path is now much closer to a faithful CASTp 1.0 reproduction
than at the start of this checkpoint:

- weighted-redundant vertices are removed like DELCX;
- CASTp 1.0 fixed-point input materialization is used in the exact rho/hidden
  layer;
- explicit `print pockets rank R rank2 R2` ranks are supported;
- zero-mouth components are retained in `.poc` reporting;
- `iF` and `rF` are allowed to overlap where CASTp 1.0's independent scans do;
- `voids` reporting is restricted to the entities actually printed by
  CASTp 1.0.

The main remaining caveat is DELX/SoS itself. The current matrix does not force
a full DELX/SoS reimplementation because the tested systems are already
structurally matched after the corrections above. It remains a residual risk
for degenerate or near-tied inputs and should be audited separately before
claiming universal CASTp 1.0 identity.

CASTP 3.0 parity remains a separate later phase. Known and suspected
differences include radii policy, water handling, and server-pipeline choices.
The current green matrix should therefore be interpreted as CASTp 1.0 parity,
not CASTP 3.0 parity.

## Verification

Focused tests:

```bash
pytest -q tests/test_castp_core.py -k "component_face_partitions or component_edge_partitions or explicit_castp_ranks or canonical_base_rank or probe_rank_as_beta"
```

Result: passed.

CASTp 1.0 oracle matrix:

```bash
pytest -q tests/test_castp_core.py -k "native_castp1_matches_local_mkalf_structural_outputs"
```

Result: passed, 9 parametrized cases.

Full CASTp test module:

```bash
pytest -q tests/test_castp_core.py
```

Result: passed with the expected `xfail` cases for CASTP 3.0 server parity.
