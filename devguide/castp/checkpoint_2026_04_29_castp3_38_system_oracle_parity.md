# CASTp3 Native vs CASTpFold Oracle: 38-System Parity Sweep

Date: 2026-04-29

This checkpoint compares the current native `topomt.third_party.castp3` path
against the downloaded CASTpFold server ZIPs for the 38 small or near-small
systems available in `topomt/data/CASTpFold_server`.

The comparison uses the current working CASTp3 assumptions:

- Oracle: CASTpFold downloaded ZIP files.
- Native selection: `molecule_type in ["protein", "peptide"]`.
- Native radii: CASTpFold/ProtOr table.
- Probe radius: 1.4 A.
- Depth mode: full-depth, not probe-limited.
- Experimental peripheral atom expansion: disabled.
- Atom identity frame: PDB serial numbers from the PDB bundled inside each ZIP.

Each table cell below is `oracle/native/exact`, where `exact` is the number of
features whose atom set matches exactly between native TopoMT and the server.

## Execution

The 38 systems were run in four controlled parallel batches:

1. `1crn 1rop 2pk4 3phv 8rat 1stp 1rob 2lyz 1ifb 2ifb`
2. `1hew 1stn 1hel 1snc 5dfr 1hfc 1brq 1rbp 1hsi 1hiv`
3. `1ida 3ptb 3ptn 4phv 2tga 1cge 1a6u 1srf 1mtw 2ctv`
4. `1esa 1a6w 1inc 1bmq 1ahc 4ca2 3tms 1djb`

All 38 comparisons completed without stderr errors.

## Summary

Strict all-feature green systems: 6/38.

Green systems:

- `1crn`
- `1rop`
- `2pk4`
- `3phv`
- `1ifb`
- `1hew`

Feature-level totals across the 38 systems:

| feature | oracle total | native total | exact total | systems with equal counts | systems fully exact |
|---|---:|---:|---:|---:|---:|
| pockets | 443 | 453 | 363 | 24/38 | 8/38 |
| voids | 306 | 303 | 295 | 33/38 | 27/38 |
| channels | 46 | 43 | 33 | 35/38 | 27/38 |
| branched channels | 10 | 11 | 6 | 37/38 | 33/38 |
| mouths | 499 | 507 | 407 | 25/38 | 7/38 |

Interpretation:

- Voids are the most stable class in this sweep.
- Voids are not solved: they are better than pockets/mouths, but still fail in
  11/38 systems.
- Pockets and mouths remain the dominant divergence classes by total number of
  mismatched features, but they are not the only remaining issue.
- Channels are usually count-stable but often not atom-set exact when the parent
  pocket/channel boundary differs.
- Branched channels are rare; the global count is almost stable, but exact atom
  matching still reveals boundary differences.
- Mouth exactness is the strictest and most fragile signal because it depends on
  both pocket assignment and boundary-face/mouth export semantics.
- Void failures cannot be explained by mouth-definition errors. They point to a
  separate issue in closed empty-region construction, atom aggregation, or
  alpha/dual-complex classification.

## System Table

| pdb | atoms in ZIP PDB | status | pockets | voids | channels | branched | mouths |
|---|---:|---|---:|---:|---:|---:|---:|
| 1crn | 327 | green | 0/0/0 | 1/1/1 | 0/0/0 | 0/0/0 | 0/0/0 |
| 1rop | 495 | green | 3/3/3 | 0/0/0 | 0/0/0 | 0/0/0 | 3/3/3 |
| 2pk4 | 745 | green | 3/3/3 | 4/4/4 | 0/0/0 | 0/0/0 | 3/3/3 |
| 3phv | 758 | green | 8/8/8 | 2/2/2 | 2/2/2 | 1/1/1 | 11/11/11 |
| 8rat | 951 | atoms:pocket,mouth | 11/11/8 | 0/0/0 | 1/1/1 | 0/0/0 | 12/12/9 |
| 1stp | 1001 | atoms:pocket | 5/5/4 | 3/3/3 | 1/1/1 | 0/0/0 | 6/6/6 |
| 1rob | 1077 | atoms:pocket,mouth | 8/8/4 | 2/2/2 | 2/2/2 | 0/0/0 | 10/10/7 |
| 2lyz | 1102 | atoms:pocket,mouth | 6/6/5 | 6/6/6 | 0/0/0 | 0/0/0 | 6/6/5 |
| 1ifb | 1109 | green | 6/6/6 | 4/4/4 | 0/0/0 | 0/0/0 | 6/6/6 |
| 2ifb | 1136 | count:pocket,mouth; atoms:void | 10/11/9 | 6/6/5 | 1/1/1 | 0/0/0 | 11/12/10 |
| 1hew | 1147 | green | 4/4/4 | 3/3/3 | 0/0/0 | 0/0/0 | 4/4/4 |
| 1stn | 1174 | count:pocket,mouth; atoms:void | 11/10/6 | 7/7/6 | 0/0/0 | 0/0/0 | 11/10/6 |
| 1hel | 1186 | atoms:pocket,mouth | 8/8/7 | 4/4/4 | 0/0/0 | 0/0/0 | 8/8/6 |
| 1snc | 1190 | atoms:void,branched_channel,mouth | 5/5/5 | 8/8/7 | 0/0/0 | 1/1/0 | 6/6/5 |
| 5dfr | 1343 | count:pocket,void,mouth; atoms:channel,branched_channel | 10/11/8 | 3/2/2 | 2/2/1 | 1/1/0 | 13/14/11 |
| 1hfc | 1360 | atoms:pocket,mouth | 14/14/12 | 5/5/5 | 1/1/1 | 0/0/0 | 15/15/12 |
| 1brq | 1463 | atoms:pocket,channel,mouth | 10/10/7 | 7/7/7 | 2/2/1 | 1/1/1 | 13/13/9 |
| 1rbp | 1582 | atoms:mouth | 14/14/14 | 7/7/7 | 3/3/3 | 0/0/0 | 17/17/16 |
| 1hsi | 1602 | count:pocket,channel,mouth; atoms:branched_channel | 11/15/9 | 3/3/3 | 1/2/0 | 1/1/0 | 13/18/10 |
| 1hiv | 1665 | atoms:pocket,channel,mouth | 13/13/11 | 3/3/3 | 1/1/0 | 0/0/0 | 14/14/10 |
| 1ida | 1675 | count:pocket,mouth; atoms:channel | 12/11/8 | 5/5/5 | 2/2/1 | 0/0/0 | 14/13/10 |
| 3ptb | 1701 | count:pocket,void,mouth | 12/11/10 | 14/15/14 | 1/1/1 | 0/0/0 | 13/12/11 |
| 3ptn | 1712 | atoms:pocket,mouth | 17/17/16 | 14/14/14 | 0/0/0 | 0/0/0 | 17/17/16 |
| 4phv | 1716 | atoms:pocket,mouth | 17/17/15 | 5/5/5 | 1/1/1 | 1/1/1 | 19/19/17 |
| 2tga | 1723 | count:pocket,mouth; atoms:void | 14/16/11 | 16/16/15 | 1/1/1 | 0/0/0 | 15/17/13 |
| 1cge | 1853 | count:pocket,void,channel,mouth | 11/10/1 | 7/4/4 | 3/0/0 | 0/0/0 | 14/10/1 |
| 1a6u | 1892 | count:pocket,mouth | 21/22/21 | 19/19/19 | 2/2/2 | 1/1/1 | 24/25/22 |
| 1srf | 1943 | count:pocket,mouth; atoms:void,branched_channel | 18/19/18 | 12/12/11 | 1/1/1 | 2/2/1 | 21/22/20 |
| 1mtw | 1952 | atoms:pocket,channel,mouth | 10/10/7 | 14/14/14 | 1/1/0 | 0/0/0 | 11/11/9 |
| 2ctv | 1957 | atoms:pocket,void,channel,mouth | 13/13/9 | 14/14/13 | 3/3/2 | 0/0/0 | 16/16/15 |
| 1esa | 1967 | atoms:pocket,mouth | 15/15/13 | 16/16/16 | 0/0/0 | 1/1/1 | 16/16/12 |
| 1a6w | 1973 | count:pocket,void,branched_channel,mouth | 19/20/15 | 12/11/11 | 1/1/1 | 0/1/0 | 20/22/16 |
| 1inc | 1992 | atoms:pocket,mouth | 19/19/18 | 13/13/13 | 0/0/0 | 0/0/0 | 19/19/17 |
| 1bmq | 2070 | count:pocket,void,mouth; atoms:channel | 20/23/13 | 15/16/15 | 2/2/1 | 0/0/0 | 22/25/16 |
| 1ahc | 2096 | atoms:pocket,channel,mouth | 19/19/17 | 13/13/13 | 1/1/0 | 0/0/0 | 20/20/16 |
| 4ca2 | 2133 | count:pocket,channel; atoms:mouth | 12/13/9 | 15/15/15 | 6/5/5 | 0/0/0 | 18/18/15 |
| 3tms | 2166 | count:pocket,mouth | 12/11/10 | 17/17/17 | 2/2/2 | 0/0/0 | 14/13/11 |
| 1djb | 2189 | atoms:pocket,mouth | 22/22/19 | 7/7/7 | 2/2/2 | 0/0/0 | 24/24/21 |

## Failure Patterns

The dominant failure pattern is not complete loss of feature topology. Many
systems have the same number of server and native features, but differ in atom
sets. This is especially visible for pockets and mouths.

Void failures must be tracked independently:

- Count-level void mismatches: `5dfr`, `3ptb`, `1cge`, `1a6w`, `1bmq`.
- Atom-set-only void mismatches: `2ifb`, `1stn`, `1snc`, `2tga`, `1srf`,
  `2ctv`.
- Void-green systems: `1crn`, `1rop`, `2pk4`, `3phv`, `8rat`, `1stp`, `1rob`,
  `2lyz`, `1ifb`, `1hew`, `1hel`, `1hfc`, `1brq`, `1rbp`, `1hsi`, `1hiv`,
  `1ida`, `3ptn`, `4phv`, `1a6u`, `1mtw`, `1esa`, `1inc`, `1ahc`, `4ca2`,
  `3tms`, `1djb`.

The most useful classes for the next diagnostic pass are:

- Strict green controls: `1crn`, `1rop`, `2pk4`, `3phv`, `1ifb`, `1hew`.
- Pocket/mouth atom-set-only mismatches with stable counts: `8rat`, `1stp`,
  `1rob`, `2lyz`, `1hel`, `1hfc`, `3ptn`, `4phv`, `1inc`, `1djb`.
- Mouth-only mismatch with exact parent features: `1rbp`.
- Count-level pocket/mouth mismatches: `2ifb`, `1stn`, `5dfr`, `1hsi`,
  `1ida`, `3ptb`, `2tga`, `1cge`, `1a6u`, `1srf`, `1a6w`, `1bmq`, `4ca2`,
  `3tms`.

This supports the current working hypothesis that at least two distinct issues
remain:

1. A boundary/export issue: server atom sets can include atoms adjacent to the
   pocket boundary or mouth rim that are not currently included by our native
   feature atom aggregation.
2. A topology issue: some systems still differ in the number of pockets, voids,
   channels, or mouths, which cannot be solved by atom-reporting changes alone.
3. A void-specific issue: closed regions have no mouths, so their mismatches
   must come from alpha/dual-complex survival, closed-component construction,
   or atom reporting around closed empty tetrahedron components.

The temporary peripheral-atom expansion switch is not a correction. The broad
BFS version made the four-system focus batch worse by adding too many atoms.
Any future correction must be tied to a canonical CASTp3 or CASTpFold rule, not
to an oracle-fitted local expansion.

## Recommended Next Cases

For efficient diagnosis, use this order:

1. `1rbp`: parent pockets/voids/channels are exact; only one mouth differs.
2. `2ifb` or `1stn`: void count is correct but one void atom set is not exact.
3. `3ptb` or `5dfr`: void count differs, so the closed-component topology must
   be audited.
4. `1stp`: one pocket atom-set miss, mouths exact.
5. `8rat` and `1hel`: repeated pocket/mouth atom-set subset pattern.
6. `1a6u`: small count-level pocket/mouth divergence with voids already green.
7. `1cge`: broad red case, useful only after simpler boundary/topology issues
   are understood.

The next audit should separate:

- feature topology parity,
- mouth boundary-face parity,
- atom reporting parity,
- closed void component parity,
- physical metrics parity.

The current report only measures feature atom-set parity and feature counts.

## Void-First Audit Notes

The first void audit separates two failure modes:

- Atom-reporting mismatches with correct void count.
- Small closed-component birth/death mismatches where the number of voids
  differs.

Initial cases:

| pdb | void result | observation |
|---|---:|---|
| 2ifb | 6/6/5 | One oracle void has 93 atoms; the closest native void has 92 atoms. The missing atom is serial 279, `CB ASP A 34`. |
| 1stn | 7/7/6 | One oracle void has 7 atoms; the closest native void has 6 atoms. The missing atom is serial 120, `CG ASP A 21`. |
| 3ptb | 14/15/14 | Native has one extra one-tetrahedron void with atoms 42, 50, 392, 393. |
| 5dfr | 3/2/2 | Oracle has one missing one-tetrahedron void with atoms 122, 160, 163, 859. |

For `2ifb` and `1stn`, the missing oracle atom is not far from the native
closed component. It appears in tetrahedra adjacent to the native void at graph
distance 1. In `1stn`, the native non-exact void is formed by tetrahedra with
atom sets:

- 5623: 108, 115, 121, 284
- 5624: 108, 121, 284, 298
- 5639: 108, 284, 294, 298

The oracle adds atom 120. Atom 120 is the opposite vertex of occupied-side
tetrahedra across base-complex boundary faces adjacent to the void:

- 5624 -> 6322 across face 121, 284, 298 adds opposite atom 120.
- 5623 -> 6325 across face 115, 121, 284 adds opposite atom 120.

This suggests that CASTpFold may report some atoms from the solid wall adjacent
to the closed empty component, not only vertices of the empty tetrahedra in the
void component.

However, a naive rule that adds every atom from every occupied-side neighbor
across base-complex void boundary faces is too broad. In the four checked cases
(`2ifb`, `1stn`, `3ptb`, `5dfr`) it reduced exact void matches to zero. For
example, in `1stn` it would add atoms 107, 110, 111, 120, and 289, while the
oracle only adds 120.

Therefore this is not ready to become code. The immediate question is the
canonical filter: which solid-side adjacent atoms are considered part of the
void wall by CASTp3/CASTpFold, and which are not?

Current void hypotheses:

1. Native void topology is often correct, but atom reporting for voids is too
   narrow because it uses only vertices of empty tetrahedra.
2. Some server void atoms may come from occupied-side tetrahedra adjacent to
   base-complex boundary faces of a closed empty component.
3. A simple neighbor expansion is wrong; the missing filter is likely tied to
   alpha-shape contribution terms, Voronoi/dual incidence, or the CASTp3 export
   rule for atoms contributing to void area/volume.
4. Count-level failures (`3ptb`, `5dfr`, `1cge`, `1a6w`, `1bmq`) are separate
   from atom-reporting failures and must be audited as closed-component
   construction/rank-classification issues.

## Void Rank Sensitivity

The first count-level checks do not support the idea that CASTpFold ignores the
probe for voids. They instead point to near-threshold tetrahedra where tiny
effective-radius or tolerance changes flip the classification.

### `5dfr`: oracle void missing natively

CASTpFold reports a one-tetrahedron void with atoms 122, 160, 163, 859. The same
tetrahedron exists in the native triangulation:

- Tetrahedron index: 894.
- Native `rho_rank`: 15195.
- Native `base_rank`: 15204.
- Native classification: not empty, because `rho_rank < base_rank`.
- Euclidean tetrahedron volume: 7.4772639267.

The assigned ProtOr types and radii are:

| atom | residue atom | ProtOr type | base radius | inflated radius | center distance | margin |
|---:|---|---|---:|---:|---:|---:|
| 122 | NE1 TRP A 22 | N3H1 | 1.64 | 3.04 | 3.0364 | -0.0036 |
| 160 | CB ASP A 27 | C4H2 | 1.88 | 3.28 | 3.2766 | -0.0034 |
| 163 | OD2 ASP A 27 | O1H0 | 1.42 | 2.82 | 2.8161 | -0.0039 |
| 859 | CD1 ILE A 115 | C4H3 | 1.88 | 3.28 | 3.2766 | -0.0034 |

The negative margins are only about 0.003-0.004 A. Reducing the effective probe
or every effective radius by about 0.004 A flips this tetrahedron to empty:

| effective probe | classification |
|---:|---|
| 1.400 | not empty |
| 1.397 | not empty |
| 1.396 | empty |

Changing the exact fixed-point rank precision alone did not flip it:

| fixed decimals | classification |
|---:|---|
| 2 | not empty |
| 3 | not empty |
| 4 | not empty |
| 5 | not empty |
| 6 | not empty |

This makes a wrong ProtOr assignment, effective-radius convention, or numerical
tolerance more plausible than a large conceptual difference in probe handling.

### `3ptb`: native extra void

The unmatched native void is also one tetrahedron:

- Atoms: 42, 50, 392, 393.
- Tetrahedron index: 2713.
- Native `rho_rank`: 21343.
- Native `base_rank`: 21311.
- Native classification: empty, because `rho_rank > base_rank`.
- Euclidean tetrahedron volume: 7.9219129092.
- Margins against inflated atoms: about +0.0094 to +0.0109 A.

This is on the opposite side of the threshold from `5dfr`: native sees a tiny
probe-accessible closed void, but CASTpFold does not report it. A plausible
explanation is a server tolerance or minimum-reporting filter for near-zero
closed cavities. This must be verified against more count-level failures before
we implement anything.

### All count-level void mismatches

The five systems with void count mismatches were audited with the correct
geometry-local to PDB-serial mapping (`geometry.atom_indices_map`). The result
splits the failures into near-threshold one-tetrahedron cases and one broader
case.

| pdb | oracle/native/exact | pattern | detail |
|---|---:|---|---|
| 5dfr | 3/2/2 | missing oracle one-tetrahedron void | Exact native tetrahedron exists but is just below the empty cutoff. Margins: -0.0034 to -0.0039 A. |
| 3ptb | 14/15/14 | extra native one-tetrahedron void | Exact native tetrahedron exists and is just above the empty cutoff. Margins: +0.0094 to +0.0109 A. |
| 1a6w | 12/11/11 | missing oracle one-tetrahedron void | Exact native tetrahedron exists but is just below the empty cutoff. Margins: -0.0033 to -0.0039 A. |
| 1bmq | 15/16/15 | extra native one-tetrahedron void | Exact native tetrahedron exists and is barely above the empty cutoff. Margins: +0.0009 to +0.0011 A. |
| 1cge | 7/4/4 | broader missing-component mismatch | Missing oracle atom sets do not map to exact native tetrahedra or subset tetrahedra. Partial candidates are substantially inside the complex, with margins commonly around -0.1 A or deeper. |

Additional details:

- `1a6w` missing oracle void atoms: 1045, 1238, 1251, 1632. Native tetrahedron
  7031 has exactly these atoms, but `rho_rank=23068 < base_rank=23077`.
- `1bmq` extra native void atoms: 1034, 1048, 1376, 1922. Native tetrahedron
  3860 has exactly these atoms, with `rho_rank=25732 > base_rank=25730`.
- `1cge` is not a simple near-threshold one-tetrahedron case. It should not be
  used to tune a small tolerance until the simpler four systems are understood.

Updated interpretation:

1. Four of five void count mismatches are explained by exact tetrahedra sitting
   within about 0.001-0.011 A of the inflated-radius boundary.
2. A small effective tolerance or radius convention difference could explain
   those four, but the sign is mixed: it would need to include `5dfr`/`1a6w`
   without also keeping `3ptb`/`1bmq`, or CASTpFold may apply an additional
   minimum-reporting filter for tiny cavities.
3. `1cge` remains a separate, broad failure case and likely involves a larger
   topology/input/radius difference, not just a near-zero cutoff.

## Experimental Global Epsilon-Length Switch

An experimental `alpha_boundary_epsilon_length` switch was added to the CASTp3
native path and the oracle comparison harness. It is disabled by default.

Semantics:

- `0.0`: canonical current geometry.
- Positive epsilon: subtract epsilon from the effective inflated atom radii
  before constructing the weighted triangulation.
- This makes the empty-space classification more permissive globally.

This is intentionally a diagnostic switch, not a canonical rule.

### Focus sweep on void count cases

The five systems with void-count mismatches were tested with epsilons 0.001,
0.002, 0.004, and 0.008 A.

At `epsilon=0.004`:

| pdb | pockets | voids | channels | branched | mouths |
|---|---:|---:|---:|---:|---:|
| 5dfr | 10/10/7 | 3/3/3 | 2/3/2 | 1/1/0 | 13/14/10 |
| 1a6w | 19/20/15 | 12/12/11 | 1/1/1 | 0/1/0 | 20/22/15 |
| 3ptb | 12/12/10 | 14/15/14 | 1/1/1 | 0/0/0 | 13/13/11 |
| 1bmq | 20/24/13 | 15/16/15 | 2/2/1 | 0/0/0 | 22/26/17 |
| 1cge | 11/10/1 | 7/4/4 | 3/0/0 | 0/0/0 | 14/10/1 |

Interpretation:

- `5dfr` voids become fully exact.
- `1a6w` void count is fixed, but exact void composition remains 11/12.
- `3ptb` and `1bmq` still keep the extra native void.
- Pockets/channels/mouths move, confirming that a global alpha-boundary
  tolerance affects the full CASTp topology, not only voids.

### 38-system sweep at epsilon 0.004 A

The full 38-system benchmark was also run with `epsilon=0.004`.

Strict green systems:

- Baseline: 6/38 (`1crn`, `1rop`, `2pk4`, `3phv`, `1ifb`, `1hew`).
- Epsilon 0.004: 3/38 (`1crn`, `1rop`, `1hew`).

Feature totals:

| feature | baseline oracle/native/exact | epsilon 0.004 oracle/native/exact |
|---|---:|---:|
| pockets | 443/453/363 | 443/452/348 |
| voids | 306/303/295 | 306/310/271 |
| channels | 46/43/33 | 46/48/32 |
| branched channels | 10/11/6 | 10/11/5 |
| mouths | 499/507/407 | 499/511/399 |

Conclusion:

- A global epsilon of 0.004 A is useful diagnostically but is not a viable
  correction.
- It fixes some near-threshold void-count cases but degrades global parity,
  including previously green controls (`2pk4`, `3phv`, `1ifb`).
- The near-threshold issue likely needs a more specific canonical explanation:
  exact CASTp3 radius convention, server-side input preprocessing, or a
  post-reporting filter for tiny closed components.

## Near-Threshold Void Metrics and Reclassification

The server files show that the near-threshold count cases are not all missing
or suppressed features. In two cases, the same atom set exists on both sides
but the server classifies it as a pocket rather than a void.

| pdb | atom set | server id/type | server metrics | native classification |
|---|---|---|---|---|
| 5dfr | 122, 160, 163, 859 | ID 16, void | SA area 0.001, SA volume 0.000, MS area 25.628, MS volume 11.844, length 0.182, corners 4 | not emitted; exact tetrahedron just inside cutoff |
| 1a6w | 1045, 1238, 1251, 1632 | ID 31, void | SA area -0.000, SA volume 0.000, MS area 24.635, MS volume 11.497, length 0.002, corners 4 | not emitted; exact tetrahedron just inside cutoff |
| 3ptb | 42, 50, 392, 393 | ID 27, pocket | SA area 0.047, SA volume 0.000, MS area 17.120, MS volume 8.443, length 1.361, corners 3, mouth Ntri 1 | emitted as void |
| 1bmq | 1034, 1048, 1376, 1922 | ID 34, pocket | SA area 0.014, SA volume 0.000, MS area 14.450, MS volume 6.739, length 0.506, corners 3, mouth Ntri 1 | emitted as void |

This changes the interpretation:

- `3ptb` and `1bmq` are not server-suppressed tiny voids. They are server
  pockets with one tiny mouth triangle.
- Native TopoMT currently sees the same tetrahedron but all its faces are
  closed by the base complex, so the feature is classified as a void.
- Therefore, at least part of the void mismatch is actually a mouth/boundary
  classification issue at the alpha boundary.

Face-level evidence:

| pdb | native tetrahedron | base rank | tetra rho | near-boundary face |
|---|---:|---:|---:|---|
| 3ptb | 2713 | 21311 | 21343 | face 42, 50, 393 has `face_rho=21305`, only 6 ranks below base |
| 1bmq | 3860 | 25730 | 25732 | face 1034, 1048, 1376 has `face_rho=25729`, only 1 rank below base |

Hypothesis update:

1. For `5dfr` and `1a6w`, the tetrahedron itself is barely on the occupied
   side natively, while CASTpFold reports it as a void with essentially zero
   solvent-accessible volume.
2. For `3ptb` and `1bmq`, the tetrahedron is barely empty natively, but a
   near-threshold face remains closed in our base complex. CASTpFold appears to
   expose one mouth triangle and therefore classifies the feature as a pocket.
3. A single global radius epsilon is too blunt because it changes tetrahedra,
   faces, pockets, channels, and mouths together.
4. The next canonical audit should focus on triangle/face alpha membership and
   mouth seeding near `face_rho ~= base_rank`, not only tetrahedron occupancy.

## Experimental Face-Only Epsilon-Rank Switch

An experimental `alpha_boundary_face_epsilon_rank` switch was added to the
CASTp3 native path and oracle comparison harness. It is disabled by default.

Semantics:

- `0`: canonical current face membership.
- Positive integer: a face whose `face_rho_rank` is inside the complex but
  within this many ranks below `base_rank` is treated as open for
  boundary/mouth reporting.
- This does not move tetrahedron occupancy/radii; it only tests whether
  near-boundary face membership can explain `void -> pocket` differences.

This is diagnostic only.

### Focus results

`alpha_boundary_face_epsilon_rank=6` was tested on the near-threshold focus
cases.

| pdb | pockets | voids | channels | branched | mouths |
|---|---:|---:|---:|---:|---:|
| 5dfr | 10/11/8 | 3/2/2 | 2/2/1 | 1/1/0 | 13/14/11 |
| 1a6w | 19/20/15 | 12/11/11 | 1/1/1 | 0/1/0 | 20/22/16 |
| 3ptb | 12/12/11 | 14/14/14 | 1/1/1 | 0/0/0 | 13/13/12 |
| 1bmq | 20/24/14 | 15/15/15 | 2/2/1 | 0/0/0 | 22/26/17 |

Interpretation:

- `3ptb` is strongly explained by near-boundary face membership: voids become
  exact, pockets/mouths gain one exact feature, and counts align.
- `1bmq` fixes the void count but still has too many native pockets/mouths.
- `5dfr` and `1a6w` do not improve because their problem is tetrahedron
  occupancy, not face/mouth membership.

### 38-system sweep at face epsilon rank 6

Strict green systems:

- Baseline: 6/38 (`1crn`, `1rop`, `2pk4`, `3phv`, `1ifb`, `1hew`).
- Face epsilon 6: 3/38 (`1crn`, `2pk4`, `1ifb`).

Feature totals:

| feature | baseline oracle/native/exact | face epsilon 6 oracle/native/exact |
|---|---:|---:|
| pockets | 443/453/363 | 443/451/355 |
| voids | 306/303/295 | 306/294/289 |
| channels | 46/43/33 | 46/54/34 |
| branched channels | 10/11/6 | 10/11/6 |
| mouths | 499/507/407 | 499/516/401 |

Conclusion:

- A global face-rank tolerance is also too broad for default behavior.
- It is diagnostically valuable because it explains `3ptb` and partly `1bmq`,
  but it degrades previously green controls (`1rop`, `3phv`, `1hew`) and
  increases channel/mouth over-splitting.
- The next step should not be a global tolerance. We need the canonical CASTp3
  rule that decides when a near-boundary face becomes a mouth seed. The rule is
  likely tied to exact face classification, mouth construction, or server
  postprocessing for tiny one-triangle mouths.

## Sequential Five-Point Audit Checkpoint

This checkpoint records the current state of the agreed five-point route before
making additional CASTp3 behavior changes. The purpose is to keep the work
anchored to CASTp/CASTpFold evidence instead of adding local rules that only fix
one case.

### 1. `3ptb` minimal void-to-pocket case

`3ptb` remains the cleanest minimal case for the `void -> pocket` discrepancy:

- Native TopoMT emits one extra one-tetrahedron void with atoms 42, 50, 392,
  393.
- CASTpFold emits the same atom set as a pocket, not as a void.
- CASTpFold reports one mouth triangle for that feature.
- The reported mouth atoms are exactly 42, 50, 393.
- Native TopoMT sees that same face as closed by the base complex because its
  `face_rho_rank` is six ranks below `base_rank`.

The important point is that this is not a missing-feature problem. It is a
classification problem at the boundary between closed void and one-mouth pocket.

### 2. Pocket-over-void priority is insufficient

A simple priority rule such as "if the same tetrahedron appears as both pocket
and void, report the pocket" is not canonical enough and does not solve the
root problem.

The 1998 formal description constructs pockets from tetrahedra in the latter
part of the filtration, then derives mouths as components of the pocket
boundary after removing the alpha complex (`Bd P - Cpx_beta`). In other words,
a feature becomes a pocket/channel by having mouth components in that boundary;
it is not made into a pocket by a post-hoc preference over a void label.

For `3ptb` and `1bmq`, the diagnostic face-epsilon switch can create the
one-triangle mouth seed, but the global switch degrades the 38-system benchmark.
That makes it evidence for a near-boundary face-classification issue, not a
valid default rule.

### 3. Void atom reporting differs from void topology

`1stn` and `2ifb` show a separate issue: the void count can be correct while
the reported atom set differs by one atom.

Evidence from server `.contrib.csv` files:

| pdb | missing server atom | server contribution evidence |
|---|---|---|
| `1stn` | atom 120, `CG ASP A 21` | `SA_Area=0.0`, `MS_Area=1.64`, `SA_Volume=13.731`, `MS_Volume=12.959` |
| `2ifb` | atom 279, `CB ASP A 34` | `SA_Area=0.0`, `MS_Area=1.64`, `SA_Volume=34.6`, `MS_Volume=33.817` |

This supports the idea that CASTpFold may report atoms contributing to the
solid wall or molecular-surface contribution of a void, not only vertices of
the empty tetrahedra that define the closed component. A naive adjacent-solid
tetrahedron expansion was already tested and is too broad, so this should be
treated as an export/contribution attribution problem, not as a topology
problem.

### 4. Paper/code audit so far

The 1998 papers support the following canonical constraints:

- Empty tetrahedra and their filtration order are the substrate for pockets.
- Sinks are important because they predict void disappearance during ball
  growth.
- Pockets are constructed through the filtration using depth and union-find
  evolution.
- Mouths are components of `Bd P - Cpx_beta`.
- The mouth dual set is then obtained one dimension lower from those boundary
  components.

This agrees with our current CASTp1-derived implementation structure: build
rank-driven pocket components, build closed complement void components, then
derive mouth clusters from boundary faces. It does not justify a blanket
near-threshold epsilon or a blanket pocket-over-void priority.

The unresolved CASTp3/CASTpFold-specific question is narrower: what exact
server-side rule or numerical convention makes a near-boundary face in `3ptb`
and `1bmq` become a mouth triangle while not degrading controls such as `1rop`,
`3phv`, and `1hew`?

The original CASTp1 source narrows this further:

- `alf_pocket_sequence(rank1, rank2, ...)` adds tetrahedra only through the
  rank-driven pocket sequence.
- `handle_tetra_seq()` marks a mouth event only when the separating triangle is
  not in the alpha complex at `rank1` and the opposite tetrahedron is not
  already in the pocket union-find set.
- `alf_scan_pocket_f1()` later scans those same boundary triangles by checking
  `not alf_is_in_complex(ALF_TRIANGLE, p_rank1, triangle)` and adjacency to the
  exterior/non-pocket side.
- The alpha-shape scan uses the standard rank intervals: tetrahedra are present
  when `rho <= rank`; regular triangles satisfy `mu1 <= rank < mu2`; interior
  triangles satisfy `mu2 <= rank`; attached faces have `rho == 0`.

This means CASTp1 does not contain a hidden "if a void is tiny, prefer pocket"
rule. A mouth needs a boundary triangle outside `Cpx_rank1`.

Focused rank probe for the server-reported one-triangle mouths:

| pdb | tetrahedron atoms | server mouth atoms | base rank | tetra rho | mouth face rho/mu1/mu2 | native status |
|---|---|---|---:|---:|---:|---|
| `3ptb` | 42, 50, 392, 393 | 42, 50, 393 | 21311 | 21343 | 21305 / 21343 / 22731 | face is in native `Cpx_base` and `Cpx_beta` |
| `1bmq` | 1034, 1048, 1376, 1922 | 1034, 1048, 1376 | 25730 | 25732 | 25729 / 25732 / 26218 | face is in native `Cpx_base` and `Cpx_beta` |

Therefore, with the current native ranks, CASTp1-style mouth construction
cannot emit these faces as mouths. If CASTpFold reports them as mouths, then at
least one of the following must differ from our native CASTp3 path:

1. the face rank itself (`rho`, `mu1`, or tie handling),
2. the alpha/base rank selected by the server,
3. the effective input geometry/radii after server preprocessing,
4. the CASTp3/CASTpFold mouth export policy, which may no longer be identical
   to CASTp1 even though the public text still quotes the 1998 algorithm.

### 5. Current decision before the next code change

Do not promote either diagnostic epsilon switch to default behavior.

Recommended next work items, in order:

1. Audit the original CASTp1 source and our CASTp1 translation around face
   membership and mouth initialization, looking specifically for strict versus
   non-strict alpha comparisons, rank tie handling, and triangle membership
   decisions.
2. Audit CASTp3/CASTpFold server files for any per-feature mouth triangle data
   that can distinguish "face barely in complex" from "reported as mouth".
3. Implement only a rule that can be tied to the canonical alpha/filtration
   construction or to direct server evidence.
4. Keep `3ptb`, `1bmq`, `5dfr`, `1a6w`, `1stn`, and `2ifb` as focused guards:
   the first two test void-to-pocket boundary classification, the next two test
   near-threshold empty tetrahedron birth/death, and the last two test atom
   reporting without topology failure.

The first item is now partly resolved: CASTp1 source supports the current
native logic, not a pocket-over-void postprocessing rule. The next highest-value
audit is to compare the face-rank inputs and server ZIP mouth exports, because
the observed server behavior is not reachable from the current native ranks
through the CASTp1 mouth algorithm.
