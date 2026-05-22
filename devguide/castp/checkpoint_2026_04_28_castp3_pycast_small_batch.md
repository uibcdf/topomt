# CASTp3 PyCAST Small-Batch Audit

Date: 2026-04-28

## Context

The PyCAST benchmark PDB list in
`topomt/data/CASTpFold_server/list_pycast_pdbs.md` was normalized to 240 unique
PDB IDs. CASTpFold oracle ZIP downloads are being used as the practical CASTp3
server oracle because CASTp3 and CASTpFold exports have matched on the cases
checked so far.

For this audit round, four small or moderate systems were selected from the new
CASTpFold ZIPs:

- `1hew`
- `1brq`
- `1rbp`
- `1bmq`

Native settings:

- package path: `topomt.third_party.castp3`
- input: processed PDB contained in each CASTpFold ZIP
- selection: `group_type=="amino acid"`
- radii model: `protor`
- probe radius: `1.4 A`

## Summary Matrix

Counts are `native / oracle / exact atom-set matches`.

| Case | Entity | Native | Oracle | Exact |
|---|---:|---:|---:|---:|
| `1hew` | pocket | 4 | 4 | 4 |
| `1hew` | void | 3 | 3 | 3 |
| `1hew` | channel | 0 | 0 | 0 |
| `1hew` | branched_channel | 0 | 0 | 0 |
| `1hew` | mouth | 4 | 4 | 4 |
| `1brq` | pocket | 10 | 10 | 7 |
| `1brq` | void | 7 | 7 | 7 |
| `1brq` | channel | 2 | 2 | 1 |
| `1brq` | branched_channel | 1 | 1 | 1 |
| `1brq` | mouth | 18 | 13 | 7 |
| `1rbp` | pocket | 14 | 14 | 14 |
| `1rbp` | void | 7 | 7 | 7 |
| `1rbp` | channel | 3 | 3 | 3 |
| `1rbp` | branched_channel | 0 | 0 | 0 |
| `1rbp` | mouth | 20 | 17 | 14 |
| `1bmq` | pocket | 23 | 20 | 13 |
| `1bmq` | void | 16 | 15 | 15 |
| `1bmq` | channel | 2 | 2 | 1 |
| `1bmq` | branched_channel | 0 | 0 | 0 |
| `1bmq` | mouth | 27 | 22 | 14 |

## Case Notes

### `1hew`

This is a clean green control:

- all pockets exact;
- all voids exact;
- all mouths exact;
- no channels or branched channels in either native or oracle.

This is useful as a small regression control for the current CASTp3-native
state.

### `1rbp`

Feature atom sets are green:

- pockets: `14 / 14 / 14`;
- voids: `7 / 7 / 7`;
- channels: `3 / 3 / 3`.

However, mouths are not green:

- native mouths: 20;
- oracle mouths: 17;
- exact mouth atom sets: 14.

This is important because it separates two layers:

- pocket/channel/void component atom reporting can be correct;
- mouth grouping/reporting can still diverge.

Therefore, CASTp3 parity cannot be judged only by pocket/void/channel atom sets.
Mouth topology and mouth atom materialization remain independent acceptance
criteria.

### `1brq`

Main residuals are small and mostly look like lining/mouth atom reporting:

- `POC-2`: native has the full oracle atom set plus extra atom `995`;
- `POC-1`: native misses `{1033, 1036, 1042}`;
- `POC-5`: native misses `{497, 534, 766}`;
- `CHA-1`: native misses `{1186, 1220, 1253}`.

Voids and branched channels are exact.

The mouth layer is less aligned:

- native mouths: 18;
- oracle mouths: 13;
- exact mouth atom sets: 7.

Interpretation: this case reinforces the hypothesis that the remaining CASTp3
gap is strongly tied to mouth grouping/materialization and nearby
mouth/lining-atom reporting, not to a global failure of the alpha-shape
substrate.

### `1bmq`

This is the most informative red case in the small batch.

Observed divergences:

- native pockets: 23 vs oracle pockets: 20;
- native voids: 16 vs oracle voids: 15;
- exact pocket atom sets: 13;
- exact void atom sets: 15;
- exact channels: 1 of 2;
- mouths: native 27 vs oracle 22, exact 14.

Important taxonomic mismatch:

- oracle `POC-11` has atom set `{1033, 1047, 1374, 1920}`;
- native has an extra void with exactly `{1033, 1047, 1374, 1920}`.

This suggests that at least one CASTp3 server pocket is being classified by the
native CASTp3 path as a void. That is a distinct problem from simple atom-set
lining differences.

Other large residuals in `1bmq` are mostly native subsets of oracle pockets,
for example:

- `POC-16`: native best overlaps 11 of 21 atoms;
- `POC-20`: native best overlaps 14 of 20 atoms;
- `POC-19`: native best overlaps 13 of 18 atoms;
- `POC-7`: native best overlaps 17 of 23 atoms.

This case should be kept as a priority red system because it combines:

- pocket/void taxonomy drift;
- missing lining/mouth atoms;
- mouth count divergence;
- a channel atom-set residual.

## Current Interpretation

The four-case batch supports a more precise CASTp3 work split:

1. Component construction is already strong on some systems (`1hew`, `1rbp`).
2. Mouth grouping/reporting is not closed, even when feature atom sets are
   green (`1rbp`).
3. Some residuals are likely mouth/lining materialization issues (`1brq`).
4. At least one residual is a true pocket-vs-void taxonomy issue (`1bmq`
   `POC-11`).

This means the next code work should not be a broad local atom-inclusion rule.
The next focused audits should separate:

- mouth seed generation;
- mouth Fnext clustering;
- CASTp3 server mouth atom export;
- pocket vs void accessibility classification for small isolated components.

## Recommended Next Cases

For the next CASTp3-native audit step:

- keep `1hew` as a small green control;
- keep `1rbp` as a mouth-only red control;
- keep `1brq` as a lining/mouth reporting red case;
- prioritize `1bmq` as the taxonomy red case.

