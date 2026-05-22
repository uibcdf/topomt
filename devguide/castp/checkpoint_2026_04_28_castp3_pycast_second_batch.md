# CASTp3 PyCAST Second-Batch Audit

Date: 2026-04-28

## Context

This checkpoint extends the CASTp3-native audit pool with six additional
CASTpFold oracle ZIPs selected from the PyCAST benchmark list:

- `3phv`
- `1rob`
- `2ifb`
- `5dfr`
- `1cge`
- `1a6u`

Native settings were kept identical to the previous small-batch audit:

- package path: `topomt.third_party.castp3`
- input: processed PDB contained in each CASTpFold ZIP
- selection: `group_type=="amino acid"`
- radii model: `protor`
- probe radius: `1.4 A`

## Summary Matrix

Counts are `native / oracle / exact atom-set matches`.

| Case | Entity | Native | Oracle | Exact |
|---|---:|---:|---:|---:|
| `3phv` | pocket | 8 | 8 | 8 |
| `3phv` | void | 2 | 2 | 2 |
| `3phv` | channel | 2 | 2 | 2 |
| `3phv` | branched_channel | 1 | 1 | 1 |
| `3phv` | mouth | 15 | 11 | 8 |
| `1rob` | pocket | 8 | 8 | 4 |
| `1rob` | void | 2 | 2 | 2 |
| `1rob` | channel | 2 | 2 | 2 |
| `1rob` | branched_channel | 0 | 0 | 0 |
| `1rob` | mouth | 12 | 10 | 5 |
| `2ifb` | pocket | 11 | 10 | 9 |
| `2ifb` | void | 6 | 6 | 5 |
| `2ifb` | channel | 1 | 1 | 1 |
| `2ifb` | branched_channel | 0 | 0 | 0 |
| `2ifb` | mouth | 13 | 11 | 9 |
| `5dfr` | pocket | 11 | 10 | 8 |
| `5dfr` | void | 2 | 3 | 2 |
| `5dfr` | channel | 2 | 2 | 1 |
| `5dfr` | branched_channel | 1 | 1 | 0 |
| `5dfr` | mouth | 19 | 13 | 9 |
| `1cge` | pocket | 10 | 11 | 1 |
| `1cge` | void | 4 | 7 | 4 |
| `1cge` | channel | 0 | 3 | 0 |
| `1cge` | branched_channel | 0 | 0 | 0 |
| `1cge` | mouth | 10 | 14 | 1 |
| `1a6u` | pocket | 22 | 21 | 21 |
| `1a6u` | void | 19 | 19 | 19 |
| `1a6u` | channel | 2 | 2 | 2 |
| `1a6u` | branched_channel | 1 | 1 | 1 |
| `1a6u` | mouth | 29 | 24 | 19 |

## Case Notes

### `3phv`

This is a strong feature-level green control:

- pockets exact;
- voids exact;
- channels exact;
- branched channel exact.

The only mismatch is the mouth layer:

- native mouths: 15;
- oracle mouths: 11;
- exact mouth atom sets: 8.

This reinforces the conclusion from `1rbp`: mouth grouping/materialization can
be wrong even when feature components are exact.

### `1a6u`

This is another near-green control at feature level:

- pockets: `22 / 21 / 21`;
- voids: `19 / 19 / 19`;
- channels: `2 / 2 / 2`;
- branched channels: `1 / 1 / 1`.

The residual is again mostly mouth-layer:

- native mouths: 29;
- oracle mouths: 24;
- exact mouth atom sets: 19.

`1a6u` is useful because it is richer than `3phv` and still largely agrees at
the feature level.

### `1rob`

Feature topology is mostly correct:

- voids exact;
- channels exact;
- pockets have correct count but only 4 of 8 exact atom sets.

The pocket residuals are small:

- `POC-1`: native misses `{7}`;
- `POC-3`: native misses `{321}`;
- `POC-7`: native misses `{509}`;
- `POC-2`: native misses `{64}` and has extras `{66, 72}`.

This is a useful lining/rim atom reporting case because the component counts
are stable and the residuals are small.

### `2ifb`

This is a mild red case:

- pockets: native has one extra pocket;
- `POC-5` is represented by native subsets missing either `{254, 438}` or
  `{275, 448}`;
- voids: one oracle void is native subset missing `{278}`;
- channel is exact.

This case may indicate a small split/duplication around a local pocket and a
single-atom void reporting mismatch.

### `5dfr`

This is a useful mixed red case:

- native has one extra pocket and one fewer void;
- `POC-9` is a one-atom residual, native missing `{1059}`;
- `CHA-1` is a one-atom residual, native missing `{93}`;
- `BCH-1` is a near subset: native overlaps 101 of 110 oracle atoms and misses
  `{90, 92, 96, 119, 125, 128, 169, 885, 887}`;
- oracle `VOI-2` is absent from native voids.

It should be kept as a channel/branched-channel red case, but it is less clean
than the mouth-only controls.

### `1cge`

This is a strong red stress case:

- native pockets: 10 vs oracle pockets: 11;
- native voids: 4 vs oracle voids: 7;
- native channels: 0 vs oracle channels: 3;
- exact pockets: 1 of 11;
- exact mouths: 1 of 14.

Many oracle pockets overlap poorly with the nearest native pocket. This suggests
that `1cge` is not only a mouth-materialization problem; it likely exposes a
larger classification or preprocessing difference.

`1cge` should not be the first correction target. It is better retained as a
stress test after cleaner mouth and taxonomy issues are understood.

## Updated Working Pool

Recommended controls and red cases:

- green/small feature control: `1hew`;
- mouth-only or mouth-dominant controls: `1rbp`, `3phv`, `1a6u`;
- lining/rim small residuals: `1brq`, `1rob`;
- mild split/taxonomy residual: `2ifb`;
- channel/branched red: `5dfr`;
- pocket-vs-void taxonomy red: `1bmq`;
- broad stress red: `1cge`.

## Interpretation

The expanded pool strengthens the current diagnosis:

1. The CASTp3-native feature construction can be exact on multiple independent
   systems.
2. Mouth grouping/materialization is repeatedly divergent even when pockets,
   voids, and channels are exact.
3. Small lining/rim atom residuals appear across several systems.
4. Separate taxonomy failures still exist (`1bmq`, `5dfr`, `1cge`), but they
   should be attacked after the cleaner mouth/reporting layer is understood.

## Addendum: Server Mouth Export Semantics

The mouth rows above were generated before correcting one important comparison
semantics issue.

CASTpFold stores two different mouth notions:

- `N_mth` in `.pocInfo` is the number of topological mouths of the parent
  pocket/channel feature.
- `.mouth` records are grouped by parent feature ID, not by individual
  topological mouth ID.

Therefore, a native feature with several topological mouths must expose one
server-comparable exported mouth whose atom set is the union of those
topological mouths. The individual topological mouths remain useful internally
for classification and diagnostics, but they are not one-to-one with the mouth
features loaded from the server zip.

The native `castp3` record exporter now preserves both views:

- `topological_mouths`: the individual mouth components used by the native
  algorithm.
- `mouths`: the CASTpFold-server-compatible aggregated mouth feature exported
  per parent pocket/channel/branched-channel feature.

Regression coverage was added in
`tests/test_castp3_probe_limited_depth.py::test_castp3_native_record_exports_server_aggregated_mouth`.

### Immediate Recheck

Using stable PDB atom IDs for comparison and `radii_model='protor'`, the
semantic correction turns `3phv` into a full exact control:

| pdb | type | oracle | native | exact |
|---|---:|---:|---:|---:|
| 3phv | pocket | 8 | 8 | 8 |
| 3phv | void | 2 | 2 | 2 |
| 3phv | channel | 2 | 2 | 2 |
| 3phv | branched_channel | 1 | 1 | 1 |
| 3phv | mouth | 11 | 11 | 11 |

This is important because `3phv` previously looked mouth-red despite having
exact parent features. The red mouth signal there was not an algorithmic mouth
failure; it was an export/comparison mismatch.

### Remaining Caution

The same quick recheck exposed that `1hew` and `1rbp` are sensitive to the exact
input/preparation route used in the comparison script. They should not be used
as evidence for or against the mouth aggregation correction until the parity
harness fixes the molecular-system frame explicitly:

- compare by stable PDB atom IDs or labels, not by raw feature-local indices;
- record the selected input PDB from each zip;
- record `radii_model`;
- record whether the native run is CASTp1-style or CASTp3-style;
- keep server mouth features aggregated by parent feature.

The next parity harness should encode these rules before expanding the pyCAST
benchmark pool.
